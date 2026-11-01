"""Tests for the CI gate: the single required check of the Tests workflow.

The ruleset cannot require matrix jobs by name: GitHub names them after the
matrix values ("test (3.14)"), so a version bump renames the check and every
PR waits forever for a check that never runs. Instead the ruleset requires
one job with a fixed name that depends on every other job.

A skipped required check counts as passed. So the gate must run even when a
dependency fails (``if: always()``) and approve only when every dependency
explicitly succeeded (allowlist): failure, cancelled and skipped all fail it.
"""

from pathlib import Path

import pytest
import yaml

from scripts.check_needs import main, unsuccessful_jobs

WORKFLOW = (
    Path(__file__).resolve().parent.parent / ".github" / "workflows" / "tests.yml"
)
GATE = "ci-passed"
# Jobs that never run on pull requests cannot gate a pull request
PUSH_ONLY_JOBS = {"deploy-report"}


def _jobs():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]


JOBS = _jobs()


class TestGateJob:
    """The workflow exposes one stable, matrix-independent required check."""

    def test_gate_job_exists(self):
        assert GATE in JOBS, f"{WORKFLOW.name} has no '{GATE}' job"

    def test_gate_has_no_matrix(self):
        """A matrix would put its values back into the check name."""
        assert "strategy" not in JOBS[GATE]

    def test_gate_has_no_custom_name(self):
        """The check name must be the job id the ruleset requires."""
        assert "name" not in JOBS[GATE]

    def test_gate_runs_even_when_a_dependency_fails(self):
        """Without always() a failed dependency skips the gate (= passed)."""
        assert JOBS[GATE].get("if") == "${{ always() }}"

    def test_gate_needs_every_job_that_runs_on_pull_requests(self):
        expected = set(JOBS) - {GATE} - PUSH_ONLY_JOBS
        assert set(JOBS[GATE].get("needs", [])) == expected

    def test_gate_checks_the_result_of_every_dependency(self):
        steps = JOBS[GATE].get("steps", [])
        checker = [s for s in steps if s.get("run") == "python3 scripts/check_needs.py"]
        assert checker, "gate does not run scripts/check_needs.py"
        assert checker[0].get("env", {}).get("NEEDS") == "${{ toJSON(needs) }}"


def _needs(**results):
    """Build the shape of ``toJSON(needs)``: {job: {result, outputs}}."""
    return {job: {"result": result, "outputs": {}} for job, result in results.items()}


class TestUnsuccessfulJobs:
    """Only an explicit "success" counts; anything else blocks the merge."""

    def test_all_successful(self):
        assert unsuccessful_jobs(_needs(lint="success", test="success")) == []

    @pytest.mark.parametrize("result", ["failure", "cancelled", "skipped", ""])
    def test_any_other_result_is_unsuccessful(self, result):
        needs = _needs(lint="success", test=result)
        assert unsuccessful_jobs(needs) == [f"test: {result}"]

    def test_missing_result_is_unsuccessful(self):
        assert unsuccessful_jobs({"test": {}}) == ["test: None"]


class TestMain:
    """Exit code 0 only when every job succeeded."""

    def test_success(self):
        assert main({"NEEDS": '{"lint": {"result": "success"}}'}) == 0

    def test_failure(self, capsys):
        assert main({"NEEDS": '{"lint": {"result": "failure"}}'}) == 1
        assert "lint: failure" in capsys.readouterr().err

    def test_empty_needs_fails(self):
        """No dependencies means nothing was checked: not a pass."""
        assert main({"NEEDS": "{}"}) == 1

    def test_missing_needs_fails(self):
        assert main({}) == 1
