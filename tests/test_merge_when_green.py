"""Tests for the script behind /ship-pr: merge only when every check is green.

The ruleset only takes a PR whose required checks passed on its head commit,
but asking GitHub too early returns intermediate states that look final:
``ci-passed`` does not exist until the jobs it needs finish, the checks right
after a push may be those of the previous commit, and ``mergeStateStatus`` is
``UNKNOWN`` right after a merge to master. The script waits on each condition
and merges on an allowlist: only an explicit success passes.
"""

import json

import pytest

from scripts.merge_when_green import blocking_checks, main

SHA = "abc123"
REQUIRED = ["ci-passed", "pip-audit"]


def _run(name, status="completed", conclusion: str | None = "success", run_id=1):
    return {"id": run_id, "name": name, "status": status, "conclusion": conclusion}


GREEN = [_run("ci-passed"), _run("pip-audit"), _run("lint")]


class FakeGh:
    """Answer gh commands from queues; the last answer repeats."""

    def __init__(self, check_runs=None, merge_states=("CLEAN",), required=None):
        self.check_runs = list(check_runs or [GREEN])
        self.merge_states = list(merge_states)
        self.required = REQUIRED if required is None else required
        self.calls = []

    @staticmethod
    def _next(queue):
        return queue.pop(0) if len(queue) > 1 else queue[0]

    def __call__(self, *args):
        self.calls.append(args)
        if args[:2] == ("pr", "view"):
            return json.dumps(
                {
                    "headRefOid": SHA,
                    "baseRefName": "master",
                    "mergeStateStatus": self._next(self.merge_states),
                }
            )
        if args[0] == "api" and "/rules/branches/master" in args[1]:
            checks = [{"context": name} for name in self.required]
            return json.dumps(
                [
                    {"type": "pull_request"},
                    {
                        "type": "required_status_checks",
                        "parameters": {"required_status_checks": checks},
                    },
                ]
            )
        if args[0] == "api" and f"/commits/{SHA}/check-runs" in args[1]:
            runs = self._next(self.check_runs)
            return json.dumps({"total_count": len(runs), "check_runs": runs})
        if args[:2] == ("pr", "merge"):
            return ""
        raise AssertionError(f"unexpected gh call: {args}")

    @property
    def merged(self):
        """The merge commands the script ran."""
        return [call for call in self.calls if call[:2] == ("pr", "merge")]


class FakeClock:
    """A clock that only moves when the script sleeps."""

    def __init__(self):
        self.now = 0.0
        self.sleeps = 0

    def sleep(self, seconds):
        """Stand-in for time.sleep: advance the clock instead of waiting."""
        self.now += seconds
        self.sleeps += 1

    def monotonic(self):
        """Stand-in for time.monotonic."""
        return self.now


def _main(gh, clock=None, timeout=600):
    clock = clock or FakeClock()
    return main(
        ["7", "--timeout", str(timeout), "--interval", "30"],
        gh=gh,
        sleep=clock.sleep,
        clock=clock.monotonic,
    )


class TestBlockingChecks:
    """Allowlist: a required check passes only with an explicit success."""

    def test_all_required_checks_succeeded(self):
        assert not blocking_checks(REQUIRED, GREEN)

    @pytest.mark.parametrize(
        "conclusion", ["failure", "cancelled", "skipped", "neutral", "timed_out"]
    )
    def test_anything_but_success_blocks(self, conclusion):
        runs = [_run("ci-passed", conclusion=conclusion), _run("pip-audit")]
        assert blocking_checks(REQUIRED, runs) == [f"ci-passed: {conclusion}"]

    @pytest.mark.parametrize("status", ["queued", "in_progress"])
    def test_unfinished_check_is_pending(self, status):
        runs = [_run("ci-passed", status=status, conclusion=None), _run("pip-audit")]
        assert blocking_checks(REQUIRED, runs) == ["ci-passed: pending"]

    def test_check_that_does_not_exist_yet_is_missing(self):
        # ci-passed only appears when the jobs it needs finish
        assert blocking_checks(REQUIRED, [_run("pip-audit")]) == ["ci-passed: missing"]

    def test_failing_check_outside_the_ruleset_does_not_block(self):
        # Not a required check; the PR is then UNSTABLE, which stops the merge
        # on its own (test_does_not_merge_unless_the_merge_state_is_clean)
        runs = [*GREEN, _run("smoke", conclusion="failure")]
        assert not blocking_checks(REQUIRED, runs)

    @pytest.mark.parametrize(
        "old, new, expected",
        [
            ("failure", "success", []),
            ("success", "failure", ["ci-passed: failure"]),
        ],
    )
    def test_latest_run_of_a_rerun_check_decides(self, old, new, expected):
        runs = [
            _run("ci-passed", conclusion=new, run_id=2),
            _run("ci-passed", conclusion=old, run_id=1),
            _run("pip-audit"),
        ]
        assert blocking_checks(REQUIRED, runs) == expected


class TestMerge:
    """Merge only on green checks of the head commit and a clean merge state."""

    def test_merges_the_head_commit_with_squash(self):
        gh = FakeGh()
        assert _main(gh) == 0
        assert gh.merged == [
            ("pr", "merge", "7", "--squash", "--match-head-commit", SHA)
        ]

    def test_reads_the_checks_of_the_head_commit(self):
        gh = FakeGh()
        _main(gh)
        assert any(f"/commits/{SHA}/check-runs" in call[1] for call in gh.calls[1:])

    def test_waits_while_a_required_check_is_missing_or_pending(self):
        pending = [_run("ci-passed", status="in_progress", conclusion=None)]
        gh = FakeGh(check_runs=[[_run("pip-audit")], pending, GREEN])
        clock = FakeClock()
        assert _main(gh, clock) == 0
        assert clock.sleeps == 2
        assert gh.merged

    def test_does_not_merge_when_a_required_check_failed(self, capsys):
        gh = FakeGh(check_runs=[[_run("ci-passed", conclusion="failure")]])
        assert _main(gh) == 1
        assert not gh.merged
        assert "ci-passed: failure" in capsys.readouterr().err

    def test_gives_up_when_a_required_check_never_finishes(self, capsys):
        gh = FakeGh(check_runs=[[_run("pip-audit")]])
        clock = FakeClock()
        assert _main(gh, clock, timeout=120) == 1
        assert clock.now == 120  # gives up at the deadline, polling every 30 s
        assert not gh.merged
        assert "ci-passed: missing" in capsys.readouterr().err

    def test_waits_while_the_merge_state_is_unknown(self):
        # The first answer goes to the initial read of the head commit
        gh = FakeGh(merge_states=["UNKNOWN", "UNKNOWN", "UNKNOWN", "CLEAN"])
        clock = FakeClock()
        assert _main(gh, clock) == 0
        assert clock.sleeps == 2

    @pytest.mark.parametrize("state", ["BEHIND", "DIRTY", "BLOCKED", "UNSTABLE"])
    def test_does_not_merge_unless_the_merge_state_is_clean(self, state, capsys):
        gh = FakeGh(merge_states=[state])
        assert _main(gh) == 1
        assert not gh.merged
        assert state in capsys.readouterr().err

    def test_fails_when_the_ruleset_requires_no_check(self, capsys):
        # Nothing to check is not green: the ruleset lost its required checks
        gh = FakeGh(required=[])
        assert _main(gh) == 1
        assert not gh.merged
        assert "no required checks" in capsys.readouterr().err

    def test_fails_loudly_when_check_runs_are_truncated(self, capsys):
        gh = FakeGh()
        real = gh.__call__

        def truncated(*args):
            answer = real(*args)
            if "check-runs" in args[-1]:
                data = json.loads(answer)
                data["total_count"] = 101
                return json.dumps(data)
            return answer

        assert _main(truncated) == 1
        assert not gh.merged
        assert "101" in capsys.readouterr().err
