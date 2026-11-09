"""Tests for the wait behind /ship-pr: report the outcome of a native auto-merge.

GitHub decides the merge (ruleset plus auto-merge); the script only waits for
the outcome, stops on a state that will never merge by itself, and names any
check outside the ruleset that did not pass, because neither GitHub nor
``gh pr merge --auto`` holds the merge for those.
"""

import json
import subprocess
from datetime import UTC, datetime

import pytest

from scripts.wait_for_merge import failed_checks, main, run_gh

SHA = "abc123"
REQUIRED = ["ci-passed", "pip-audit"]
NOW = datetime(2026, 11, 9, 12, 0, tzinfo=UTC)


def _run(
    name,
    status="completed",
    conclusion: str | None = "success",
    run_id=1,
    started_at: str | None = "2026-11-09T11:40:00Z",
):
    return {
        "id": run_id,
        "name": name,
        "status": status,
        "conclusion": conclusion,
        "started_at": started_at,
    }


GREEN = [_run("ci-passed"), _run("pip-audit"), _run("lint")]
PENDING = [_run("pip-audit"), _run("lint")]
STUCK = [*GREEN, _run("codecov/patch", status="in_progress", conclusion=None)]


def _pr(state="OPEN", merge_state="BLOCKED", auto_merge=True, head=SHA):
    return {
        "state": state,
        "headRefOid": head,
        "baseRefName": "master",
        "mergeStateStatus": merge_state,
        "autoMergeRequest": {"mergeMethod": "SQUASH"} if auto_merge else None,
    }


MERGED = _pr(state="MERGED", merge_state="UNKNOWN", auto_merge=False)


class Clock:
    """A clock that only moves when the script sleeps."""

    def __init__(self):
        self.time = 0.0
        self.sleeps = 0

    def __call__(self):
        return self.time

    def sleep(self, seconds):
        """Advance the clock instead of waiting."""
        self.sleeps += 1
        self.time += seconds


class FakeGh:
    """Answer gh commands from queues; the last answer repeats."""

    def __init__(self, prs=(MERGED,), check_runs=(GREEN,), required=None):
        self.prs = list(prs)
        self.check_runs = list(check_runs)
        self.required = REQUIRED if required is None else required

    @staticmethod
    def _next(queue):
        answer = queue.pop(0) if len(queue) > 1 else queue[0]
        if isinstance(answer, Exception):
            raise answer
        return answer

    def __call__(self, *args):
        if args[:2] == ("pr", "view"):
            return json.dumps(self._next(self.prs))
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
        raise AssertionError(f"unexpected gh call: {args}")


def _gh_error(stderr):
    return subprocess.CalledProcessError(1, ["gh", "pr", "view"], stderr=stderr)


def _main(gh, *extra, clock=None):
    clock = clock or Clock()
    return main(
        ["157", SHA, "--timeout", "90", "--interval", "30", *extra],
        gh=gh,
        sleep=clock.sleep,
        clock=clock,
        now=lambda: NOW,
    )


class TestFailedChecks:
    """Only what GitHub would refuse counts as a failure."""

    def test_passing_conclusions_follow_what_github_accepts(self):
        runs = [
            _run("a", conclusion="success"),
            _run("b", conclusion="skipped"),
            _run("c", conclusion="neutral"),
        ]
        assert not failed_checks(["a", "b", "c"], runs)

    @pytest.mark.parametrize(
        "conclusion", ["failure", "cancelled", "timed_out", "action_required"]
    )
    def test_any_other_conclusion_is_a_failure(self, conclusion):
        runs = [_run("ci-passed", conclusion=conclusion)]
        assert failed_checks(["ci-passed"], runs) == [f"ci-passed: {conclusion}"]

    def test_unfinished_or_absent_check_is_not_a_failure(self):
        runs = [_run("ci-passed", status="in_progress", conclusion=None)]
        assert not failed_checks(["ci-passed", "pip-audit"], runs)

    def test_a_rerun_replaces_the_previous_result(self):
        runs = [
            _run("ci-passed", conclusion="failure", run_id=1),
            _run("ci-passed", conclusion="success", run_id=2),
        ]
        assert not failed_checks(["ci-passed"], runs)


class TestOutcome:
    """The wait ends on a final state, never an intermediate one."""

    def test_merged_right_away_exits_zero(self, capsys):
        assert _main(FakeGh()) == 0
        out = capsys.readouterr().out
        assert "merged" in out
        assert "WARNING" not in out

    def test_waits_for_the_merge_while_auto_merge_is_on(self):
        clock = Clock()
        gh = FakeGh(prs=[_pr(), _pr(), MERGED])
        assert _main(gh, clock=clock) == 0
        assert clock.sleeps == 2

    def test_unknown_merge_state_means_wait(self):
        gh = FakeGh(prs=[_pr(merge_state="UNKNOWN"), MERGED])
        assert _main(gh) == 0

    def test_required_check_failure_stops_and_names_it(self, capsys):
        runs = [_run("ci-passed", conclusion="failure"), _run("pip-audit")]
        clock = Clock()
        assert _main(FakeGh(prs=[_pr()], check_runs=[runs]), clock=clock) == 1
        assert "ci-passed: failure" in capsys.readouterr().err
        assert clock.sleeps == 0

    def test_closed_pr_stops(self, capsys):
        assert _main(FakeGh(prs=[_pr(state="CLOSED")])) == 1
        assert "CLOSED" in capsys.readouterr().err

    def test_auto_merge_turned_off_stops(self, capsys):
        assert _main(FakeGh(prs=[_pr(auto_merge=False)], check_runs=[PENDING])) == 1
        assert "auto-merge" in capsys.readouterr().err

    def test_new_head_stops_before_reading_old_checks(self, capsys):
        failed_on_old_head = [_run("ci-passed", conclusion="failure")]
        gh = FakeGh(prs=[_pr(head="def456")], check_runs=[failed_on_old_head])
        assert _main(gh) == 1
        err = capsys.readouterr().err
        assert "def456" in err
        assert "ci-passed" not in err

    def test_auto_merge_off_is_confirmed_by_a_second_read(self):
        gh = FakeGh(prs=[_pr(auto_merge=False), MERGED], check_runs=[PENDING])
        assert _main(gh) == 0

    def test_merged_pr_is_not_reported_as_not_merged_over_the_ruleset(self, capsys):
        assert _main(FakeGh(required=[])) == 0
        captured = capsys.readouterr()
        assert "merged" in captured.out
        assert "no required checks" in captured.out

    @pytest.mark.parametrize("state", ["BEHIND", "DIRTY"])
    def test_state_that_never_merges_by_itself_stops_once_confirmed(
        self, state, capsys
    ):
        clock = Clock()
        gh = FakeGh(prs=[_pr(merge_state=state)], check_runs=[PENDING])
        assert _main(gh, clock=clock) == 1
        assert f"not merged: merge state is {state}" in capsys.readouterr().err
        assert clock.sleeps == 1

    @pytest.mark.parametrize("state", ["BEHIND", "DIRTY"])
    def test_single_read_of_a_stopping_state_does_not_end_the_wait(self, state):
        gh = FakeGh(prs=[_pr(merge_state=state), MERGED], check_runs=[PENDING])
        assert _main(gh) == 0

    def test_merge_seen_after_behind_still_reports_extra_checks(self, capsys):
        failed = [*GREEN, _run("codecov/patch", conclusion="failure")]
        gh = FakeGh(prs=[_pr(merge_state="BEHIND"), MERGED], check_runs=[failed])
        assert _main(gh) == 0
        assert "WARNING: codecov/patch: failure" in capsys.readouterr().out

    def test_confirmation_needs_two_reads_in_a_row(self):
        behind = _pr(merge_state="BEHIND")
        gh = FakeGh(prs=[behind, _pr(), behind, MERGED], check_runs=[PENDING])
        assert _main(gh) == 0

    def test_a_different_stopping_state_does_not_confirm_the_first(self):
        prs = [_pr(merge_state="BEHIND"), _pr(merge_state="DIRTY"), MERGED]
        assert _main(FakeGh(prs=prs, check_runs=[PENDING])) == 0

    def test_deadline_reports_the_last_state(self, capsys):
        clock = Clock()
        assert _main(FakeGh(prs=[_pr()], check_runs=[PENDING]), clock=clock) == 1
        err = capsys.readouterr().err
        assert "timed out" in err
        assert "ci-passed: missing" in err
        assert clock.time == 90

    def test_no_required_checks_stops(self, capsys):
        assert _main(FakeGh(required=[], prs=[_pr()])) == 1
        assert "no required checks" in capsys.readouterr().err

    def test_unread_check_runs_stop_instead_of_deciding_on_a_part(self, capsys):
        gh = FakeGh(prs=[_pr()])
        real = gh.__call__

        def truncated(*args):
            answer = real(*args)
            return (
                json.dumps({"total_count": 500, "check_runs": []})
                if "check-runs" in args[-1]
                else answer
            )

        assert _main(truncated) == 1
        assert "500" in capsys.readouterr().err


class TestGhErrors:
    """A failing gh call means "not known yet", until the deadline."""

    def test_transient_error_is_not_knowing_yet(self):
        gh = FakeGh(prs=[_gh_error("HTTP 502"), MERGED])
        assert _main(gh) == 0

    def test_persistent_error_reports_stderr_at_the_deadline(self, capsys):
        assert _main(FakeGh(prs=[_gh_error("HTTP 502: bad gateway")])) == 1
        err = capsys.readouterr().err
        assert "HTTP 502: bad gateway" in err
        assert "gh pr view" in err

    def test_hung_gh_is_not_knowing_yet(self):
        hung = subprocess.TimeoutExpired(["gh", "pr", "view"], 60)
        assert _main(FakeGh(prs=[hung, MERGED])) == 0

    def test_every_gh_call_has_its_own_deadline(self, monkeypatch):
        seen = {}

        def fake_run(*_args, **kwargs):
            seen.update(kwargs)
            return subprocess.CompletedProcess(["gh"], 0, stdout="{}")

        monkeypatch.setattr(subprocess, "run", fake_run)
        run_gh("pr", "view")
        assert seen["timeout"] > 0

    def test_empty_answer_is_not_knowing_yet(self):
        gh = FakeGh()
        first = [""]

        def empty_once(*args):
            return first.pop() if first else gh(*args)

        assert _main(empty_once) == 0


class TestExtraChecks:
    """Checks outside the ruleset never hold the merge, so they are reported."""

    def test_unfinished_extra_is_waited_for(self, capsys):
        clock = Clock()
        finished = [*GREEN, _run("codecov/patch")]
        gh = FakeGh(check_runs=[STUCK, finished])
        assert _main(gh, clock=clock) == 0
        assert clock.sleeps == 1
        assert "WARNING" not in capsys.readouterr().out

    def test_stuck_extra_is_named_with_age_state_and_remedy(self, capsys):
        clock = Clock()
        assert (
            _main(FakeGh(check_runs=[STUCK]), "--extra-timeout", "60", clock=clock) == 0
        )
        out = capsys.readouterr().out
        assert "codecov/patch: in_progress, pending for 20 min" in out
        assert "re-run the `test` job" in out
        assert clock.time == 60

    def test_queued_extra_has_no_age(self, capsys):
        queued = [
            *GREEN,
            _run("codecov/patch", "queued", conclusion=None, started_at=None),
        ]
        assert _main(FakeGh(check_runs=[queued]), "--extra-timeout", "0") == 0
        assert "codecov/patch: queued, not started" in capsys.readouterr().out

    def test_failed_extra_is_reported_without_turning_the_merge_into_an_error(
        self, capsys
    ):
        failed = [*GREEN, _run("codecov/patch", conclusion="failure")]
        assert _main(FakeGh(check_runs=[failed])) == 0
        out = capsys.readouterr().out
        assert "WARNING" in out
        assert "codecov/patch: failure" in out
        assert "re-run" not in out

    @pytest.mark.parametrize("conclusion", ["success", "skipped", "neutral"])
    def test_passing_extra_is_not_reported(self, conclusion, capsys):
        runs = [*GREEN, _run("deploy-report", conclusion=conclusion)]
        assert _main(FakeGh(check_runs=[runs])) == 0
        assert "WARNING" not in capsys.readouterr().out

    def test_extras_that_cannot_be_read_are_reported_not_hidden(self, capsys):
        gh = FakeGh(check_runs=[_gh_error("HTTP 502: bad gateway")])
        assert _main(gh, "--extra-timeout", "30") == 0
        out = capsys.readouterr().out
        assert "WARNING" in out
        assert "HTTP 502: bad gateway" in out
