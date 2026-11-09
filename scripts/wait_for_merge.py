#!/usr/bin/env python3
"""Wait for the outcome of a native auto-merge and report it.

Run by the /ship-pr skill, after ``gh pr merge --auto``:
``python scripts/wait_for_merge.py <pr-number> <head-sha>``.

GitHub decides the merge from the ruleset; this script never merges. It exists
for what GitHub does not tell anyone:

1. The merge is asynchronous, so the script waits for ``MERGED`` and stops at
   once on a state that will never merge by itself (a failed required check,
   auto-merge off, a new head, ``BEHIND``, ``DIRTY``). Everything else, a gh
   error included, means "not known yet" and only the deadline ends the wait.
2. Check runs outside the ruleset, such as ``codecov/patch``, can make a PR
   ``UNSTABLE`` but never hold it: GitHub requires only the ruleset's checks,
   and ``gh pr merge --auto`` merges an ``UNSTABLE`` PR directly. After the
   merge the script waits for them for a bounded time and names any that did
   not pass, so a stuck or failed one is seen instead of passing in silence.
   A check that was never created cannot be detected.

Exit code 0 = merged (warnings about extra checks, if any, are printed)
Exit code 1 = not merged; the reason is printed to stderr
"""

import argparse
import json
import subprocess
import sys
import time
from collections.abc import Callable, Iterable, Sequence
from datetime import UTC, datetime

# What GitHub accepts for a required check ("About protected branches")
PASSING_CONCLUSIONS = {"success", "skipped", "neutral"}
# Auto-merge stays on in these states, but they never merge without a human
STOPPING_MERGE_STATES = {"BEHIND", "DIRTY"}
# GitHub's maximum page size; more runs than this fail loudly, not silently
PER_PAGE = 100
STUCK_CHECK_REMEDY = (
    "Remedy: re-run the `test` job of the head commit "
    "(gh run rerun <run-id> --job <job-id>); it uploads the coverage again "
    "and Codecov publishes its checks."
)


class NotMerged(Exception):
    """The PR did not merge and will not by itself; the message says why."""


class WaitTimedOut(Exception):
    """The deadline passed; the message holds the last state read."""


def run_gh(*args: str) -> str:
    """Run a gh command and return its standard output."""
    result = subprocess.run(
        ["gh", *args], check=True, capture_output=True, text=True, encoding="utf-8"
    )
    return result.stdout


def _latest(check_runs: list[dict]) -> dict[str, dict]:
    """Return the newest run of each check: a re-run replaces the previous one."""
    latest: dict[str, dict] = {}
    for run in check_runs:
        if run["name"] not in latest or run["id"] > latest[run["name"]]["id"]:
            latest[run["name"]] = run
    return latest


def _has_failed(run: dict) -> bool:
    return run["status"] == "completed" and (
        run["conclusion"] not in PASSING_CONCLUSIONS
    )


def failed_checks(required: Iterable[str], check_runs: list[dict]) -> list[str]:
    """Return "name: conclusion" for each required check that finished badly."""
    latest = _latest(check_runs)
    return [
        f"{name}: {latest[name]['conclusion']}"
        for name in required
        if name in latest and _has_failed(latest[name])
    ]


def _unfinished_required(required: Iterable[str], check_runs: list[dict]) -> list[str]:
    latest = _latest(check_runs)
    states = []
    for name in required:
        if name not in latest:
            states.append(f"{name}: missing")
        elif latest[name]["status"] != "completed":
            states.append(f"{name}: {latest[name]['status']}")
    return states


def _describe_pending(run: dict, now: datetime) -> str:
    """Return "name: status, age" for a check that has not finished."""
    if run["started_at"] is None:
        return f"{run['name']}: {run['status']}, not started"
    started = datetime.fromisoformat(run["started_at"])
    minutes = int((now - started).total_seconds() // 60)
    return f"{run['name']}: {run['status']}, pending for {minutes} min"


class MergeWatcher:
    """Follow a PR until its auto-merge reaches a final state."""

    def __init__(self, gh, sleep, clock, now, interval):
        self.gh = gh
        self.sleep = sleep
        self.clock = clock
        self.now = now
        self.interval = interval
        self.required: list[str] | None = None

    def _poll(self, step: Callable[[], str | None], timeout: float) -> None:
        """Repeat step() until it returns None, meaning done, or fail at the deadline.

        step() returns a description of what is still pending. A failing gh
        call means the state is not known yet, so it is kept as that description.
        """
        deadline = self.clock() + timeout
        while True:
            try:
                pending = step()
            except subprocess.CalledProcessError as error:
                pending = f"gh failed: {(error.stderr or '').strip()}"
            if pending is None:
                return
            if self.clock() >= deadline:
                raise WaitTimedOut(pending)
            self.sleep(self.interval)

    def _pr(self, number: str) -> dict:
        fields = "state,headRefOid,baseRefName,mergeStateStatus,autoMergeRequest"
        return json.loads(self.gh("pr", "view", number, "--json", fields))

    def _required_checks(self, base: str) -> list[str]:
        rules = json.loads(
            self.gh("api", f"repos/{{owner}}/{{repo}}/rules/branches/{base}")
        )
        required = [
            check["context"]
            for rule in rules
            if rule["type"] == "required_status_checks"
            for check in rule["parameters"]["required_status_checks"]
        ]
        if not required:
            raise NotMerged(f"the ruleset of {base} has no required checks")
        return required

    def _check_runs(self, sha: str) -> list[dict]:
        path = f"repos/{{owner}}/{{repo}}/commits/{sha}/check-runs?per_page={PER_PAGE}"
        data = json.loads(self.gh("api", path))
        if data["total_count"] > len(data["check_runs"]):
            raise NotMerged(
                f"{data['total_count']} check runs, only "
                f"{len(data['check_runs'])} read: paginate before deciding"
            )
        return data["check_runs"]

    def _merge_step(self, number: str, sha: str) -> str | None:
        pr = self._pr(number)
        if self.required is None:
            self.required = self._required_checks(pr["baseRefName"])
        if pr["state"] == "MERGED":
            return None
        if pr["state"] != "OPEN":
            raise NotMerged(f"the PR is {pr['state']}")
        if pr["headRefOid"] != sha:
            raise NotMerged(f"the head moved from {sha} to {pr['headRefOid']}")

        check_runs = self._check_runs(sha)
        failed = failed_checks(self.required, check_runs)
        if failed:
            raise NotMerged("required checks failed: " + ", ".join(failed))
        if pr["autoMergeRequest"] is None:
            raise NotMerged("auto-merge is off")
        if pr["mergeStateStatus"] in STOPPING_MERGE_STATES:
            raise NotMerged(f"merge state is {pr['mergeStateStatus']}")

        unfinished = _unfinished_required(self.required, check_runs)
        return f"merge state {pr['mergeStateStatus']}; " + (
            ", ".join(unfinished) or "required checks passed"
        )

    def wait_for_merge(self, number: str, sha: str, timeout: float) -> None:
        """Return once the PR is merged, or raise saying why it will not be."""
        self._poll(lambda: self._merge_step(number, sha), timeout)

    def extra_check_warnings(self, sha: str, timeout: float) -> list[str]:
        """Wait a bounded time for checks outside the ruleset; report the bad ones."""
        required = self.required or []
        extras: list[dict] = []

        def step() -> str | None:
            latest = _latest(self._check_runs(sha))
            extras[:] = [run for name, run in latest.items() if name not in required]
            pending = [run["name"] for run in extras if run["status"] != "completed"]
            return ", ".join(pending) or None

        try:
            self._poll(step, timeout)
        except WaitTimedOut as error:
            if not extras:
                return [f"extra checks could not be read: {error}"]

        pending = [
            _describe_pending(run, self.now())
            for run in extras
            if run["status"] != "completed"
        ]
        failed = [
            f"{run['name']}: {run['conclusion']}" for run in extras if _has_failed(run)
        ]
        return failed + pending + ([STUCK_CHECK_REMEDY] if pending else [])


def main(
    argv: Sequence[str] | None = None,
    gh: Callable[..., str] = run_gh,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> int:
    """Wait for the PR given on the command line and report the outcome."""
    parser = argparse.ArgumentParser(
        description="Wait for a native auto-merge and report its outcome."
    )
    parser.add_argument("pr", help="pull request number")
    parser.add_argument("sha", help="head commit the auto-merge was enabled for")
    parser.add_argument("--timeout", type=float, default=1800, help="seconds")
    parser.add_argument("--interval", type=float, default=30, help="seconds")
    parser.add_argument(
        "--extra-timeout",
        type=float,
        default=300,
        help="seconds to wait after the merge for checks outside the ruleset",
    )
    args = parser.parse_args(argv)

    watcher = MergeWatcher(gh, sleep, clock, now, args.interval)
    try:
        watcher.wait_for_merge(args.pr, args.sha, args.timeout)
    except WaitTimedOut as error:
        print(f"ERROR: PR #{args.pr} not merged: timed out; {error}", file=sys.stderr)
        return 1
    except NotMerged as error:
        print(f"ERROR: PR #{args.pr} not merged: {error}", file=sys.stderr)
        return 1

    print(f"OK: PR #{args.pr} merged at {args.sha}")
    try:
        warnings = watcher.extra_check_warnings(args.sha, args.extra_timeout)
    except NotMerged as error:
        warnings = [str(error)]
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
