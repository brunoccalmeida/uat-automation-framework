#!/usr/bin/env python3
"""Squash-merge a PR only when every required check passed on its head commit.

Run by the /ship-pr skill: ``python scripts/merge_when_green.py <pr-number>``.

Each read waits for a final state, never an intermediate one:

1. The required checks come from the ruleset of the PR's base branch, so this
   script follows a ruleset change instead of keeping a second list.
2. The check runs are those of the PR's head commit. A required check that is
   missing or unfinished means *wait*: ``ci-passed`` only appears when the
   jobs it needs finish (``gh pr checks --watch --required`` returns before
   that, showing only ``pip-audit``).
3. ``mergeStateStatus`` is ``UNKNOWN`` for a while after a merge to the base
   branch; wait until GitHub computes it.

Allowlist: only an explicit "success" per required check and a ``CLEAN``
merge state merge; anything else (failure, skipped, behind, a timeout) stops.
``UNSTABLE`` ("mergeable with non-passing commit status", GraphQL
``MergeStateStatus``) is accepted by the ruleset but stops here too: every
check of a PR feeds ``ci-passed`` or is ``pip-audit`` and the repository has
no commit statuses, so a non-passing extra check is unexpected and a human
looks before merging.
``--match-head-commit`` makes GitHub refuse the merge if the head moved.

Exit code 0 = merged
Exit code 1 = not merged; the reason is printed to stderr
"""

import argparse
import json
import subprocess
import sys
import time
from collections.abc import Callable, Iterable, Sequence

PENDING_MERGE_STATE = "UNKNOWN"
MERGEABLE_STATE = "CLEAN"
# GitHub's maximum page size; more runs than this fail loudly, not silently
PER_PAGE = 100


class NotMergeable(Exception):
    """The PR must not be merged; the message says why."""


def run_gh(*args: str) -> str:
    """Run a gh command and return its standard output."""
    result = subprocess.run(
        ["gh", *args], check=True, capture_output=True, text=True, encoding="utf-8"
    )
    return result.stdout


def blocking_checks(required: Iterable[str], check_runs: list[dict]) -> list[str]:
    """Return "name: state" for each required check that did not succeed.

    The state is the conclusion of the latest run of the check (a re-run
    replaces the previous result), "pending" if it has not finished, or
    "missing" if it has no run yet.
    """
    latest: dict[str, dict] = {}
    for run in check_runs:
        if run["name"] not in latest or run["id"] > latest[run["name"]]["id"]:
            latest[run["name"]] = run

    blocking = []
    for name in required:
        run = latest.get(name)
        if run is None:
            state = "missing"
        elif run["status"] != "completed":
            state = "pending"
        else:
            state = run["conclusion"]
        if state != "success":
            blocking.append(f"{name}: {state}")
    return blocking


def _is_pending(blocking: list[str]) -> bool:
    return any(line.endswith((": pending", ": missing")) for line in blocking)


class Merger:
    """Wait for the final state of a PR and merge it only when green."""

    def __init__(self, gh, sleep, clock, timeout, interval):
        self.gh = gh
        self.sleep = sleep
        self.deadline = clock() + timeout
        self.clock = clock
        self.interval = interval

    def _wait(self, read: Callable, done: Callable, what: str):
        """Return the first reading for which done() holds, or fail at the deadline."""
        while True:
            reading = read()
            if done(reading):
                return reading
            if self.clock() >= self.deadline:
                raise NotMergeable(f"timed out waiting for {what}: {reading}")
            self.sleep(self.interval)

    def _pr(self, number: str) -> dict:
        fields = "headRefOid,baseRefName,mergeStateStatus"
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
            raise NotMergeable(f"the ruleset of {base} has no required checks")
        return required

    def _check_runs(self, sha: str) -> list[dict]:
        path = f"repos/{{owner}}/{{repo}}/commits/{sha}/check-runs?per_page={PER_PAGE}"
        data = json.loads(self.gh("api", path))
        if data["total_count"] > len(data["check_runs"]):
            raise NotMergeable(
                f"{data['total_count']} check runs, only "
                f"{len(data['check_runs'])} read: paginate before deciding"
            )
        return data["check_runs"]

    def merge(self, number: str) -> str:
        """Merge the PR and return its head SHA, or raise NotMergeable."""
        pr = self._pr(number)
        sha = pr["headRefOid"]
        required = self._required_checks(pr["baseRefName"])

        blocking = self._wait(
            lambda: blocking_checks(required, self._check_runs(sha)),
            lambda blocking: not _is_pending(blocking),
            f"the required checks of {sha}",
        )
        if blocking:
            raise NotMergeable(
                "required checks did not succeed: " + ", ".join(blocking)
            )

        state = self._wait(
            lambda: self._pr(number)["mergeStateStatus"],
            lambda state: state != PENDING_MERGE_STATE,
            "the merge state",
        )
        if state != MERGEABLE_STATE:
            raise NotMergeable(f"merge state is {state}, not {MERGEABLE_STATE}")

        self.gh("pr", "merge", number, "--squash", "--match-head-commit", sha)
        return sha


def main(
    argv: Sequence[str] | None = None,
    gh: Callable[..., str] = run_gh,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
) -> int:
    """Merge the PR given on the command line, or report why not."""
    parser = argparse.ArgumentParser(
        description="Squash-merge a PR only when every required check passed."
    )
    parser.add_argument("pr", help="pull request number")
    parser.add_argument("--timeout", type=float, default=1800, help="seconds")
    parser.add_argument("--interval", type=float, default=30, help="seconds")
    args = parser.parse_args(argv)

    merger = Merger(gh, sleep, clock, args.timeout, args.interval)
    try:
        sha = merger.merge(args.pr)
    except NotMergeable as error:
        print(f"ERROR: PR #{args.pr} not merged: {error}", file=sys.stderr)
        return 1
    print(f"OK: PR #{args.pr} squash-merged at {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
