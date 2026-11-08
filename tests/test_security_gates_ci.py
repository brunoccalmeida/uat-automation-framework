"""Tests that the CI security gates cannot pass without checking anything.

A security gate fails open: a green check looks the same whether the scanner
judged the code or quietly looked at nothing. These tests pin only the settings
whose regression would turn a gate green in silence. Whether the tools really
catch a problem is proven by probes (a fake secret, an unpinned action; #147).
That both jobs gate the merge is covered by ``tests/test_ci_gate.py``.
"""

import re
from pathlib import Path

import pytest
import yaml

WORKFLOW = (
    Path(__file__).resolve().parent.parent / ".github" / "workflows" / "tests.yml"
)
SECRET_SCAN = "secret-scan"
WORKFLOW_AUDIT = "workflow-audit"
EXACT_VERSION = re.compile(r"^\d+\.\d+\.\d+$")

JOBS = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]


def _job(job_id):
    assert job_id in JOBS, f"{WORKFLOW.name} has no '{job_id}' job"
    return JOBS[job_id]


def _step_using(job_id, action):
    """Return the only step of the job that uses ``action``."""
    steps = [
        step
        for step in _job(job_id)["steps"]
        if str(step.get("uses", "")).startswith(f"{action}@")
    ]
    assert len(steps) == 1, f"{job_id} must use {action} exactly once"
    return steps[0]


def _step_running(job_id, command):
    """Return the only step of the job whose script contains ``command``."""
    steps = [
        step for step in _job(job_id)["steps"] if command in str(step.get("run", ""))
    ]
    assert len(steps) == 1, f"{job_id} must run '{command}' exactly once"
    return steps[0]


class TestSecretScan:
    """gitleaks reads every commit and only ever runs the verified release."""

    def test_checkout_fetches_the_whole_history(self):
        """A shallow clone holds one commit: a key added and deleted is unseen."""
        checkout = _step_using(SECRET_SCAN, "actions/checkout")
        assert checkout["with"]["fetch-depth"] == 0

    def test_scan_reads_the_git_history_of_the_tested_commit(self):
        """``git`` mode reads commits; bare ``HEAD`` keeps other branches out."""
        run = _step_running(SECRET_SCAN, "--log-opts=HEAD")["run"]
        assert '/gitleaks" git ' in run
        # A range such as HEAD~1..HEAD still contains the text above
        assert re.search(r"--log-opts=HEAD(\s|$)", run), "scan must not take a range"

    def test_scan_keeps_found_secrets_out_of_the_public_log(self):
        assert "--redact" in _step_running(SECRET_SCAN, "--log-opts=HEAD")["run"]

    def test_release_is_verified_before_it_is_unpacked(self):
        """An archive that fails its checksum must never reach ``tar``."""
        run = _step_running(SECRET_SCAN, "sha256sum --check --strict")["run"]
        assert run.index("sha256sum --check --strict") < run.index("tar ")

    def test_release_is_pinned_by_version_and_digest(self):
        env = _step_running(SECRET_SCAN, "sha256sum --check --strict")["env"]
        assert EXACT_VERSION.match(env["GITLEAKS_VERSION"])
        assert re.fullmatch(r"[0-9a-f]{64}", env["GITLEAKS_SHA256"])


class TestWorkflowAudit:
    """zizmor reports through the job's exit code, at a fixed version."""

    @staticmethod
    def _inputs():
        return _step_using(WORKFLOW_AUDIT, "zizmorcore/zizmor-action")["with"]

    def test_findings_fail_the_job(self):
        """With Advanced Security the action uploads SARIF and always exits 0."""
        assert self._inputs()["advanced-security"] is False

    def test_version_is_exact(self):
        """The default is ``latest``: a release could fail an unrelated PR."""
        assert EXACT_VERSION.match(self._inputs()["version"])

    def test_online_audits_are_not_turned_off(self):
        """Impostor commits and known-vulnerable actions need the GitHub API."""
        assert self._inputs().get("online-audits", True) is True


@pytest.mark.parametrize("job_id", [SECRET_SCAN, WORKFLOW_AUDIT])
def test_gate_failures_are_not_ignored(job_id):
    """``continue-on-error`` reports success to ``ci-passed`` on a finding."""
    job = _job(job_id)
    softened = [
        step.get("name", step.get("uses"))
        for step in job["steps"]
        if "continue-on-error" in step
    ]
    assert "continue-on-error" not in job
    assert not softened, f"{job_id} ignores failures of: {softened}"
