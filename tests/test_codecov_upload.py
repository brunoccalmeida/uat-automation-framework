"""Tests for the Codecov coverage upload in the Tests workflow.

The upload authenticates with OIDC: GitHub issues a short-lived credential per
run, so there is no long-lived secret to leak or rotate. A broken upload must
fail CI (``fail_ci_if_error``); hiding it left coverage unreported for months.

GitHub withholds ``id-token: write`` from runs started by Dependabot and from
fork pull requests. The upload is skipped exactly there, so those runs stay
green without silencing the upload everywhere else.
"""

from pathlib import Path

import yaml

WORKFLOW = (
    Path(__file__).resolve().parent.parent / ".github" / "workflows" / "tests.yml"
)
JOB = "test"
STEP = "Upload coverage to Codecov"
# Runs where GitHub grants the OIDC token: not Dependabot, not a fork PR
OIDC_AVAILABLE = (
    "${{ github.actor != 'dependabot[bot]' && "
    "(github.event_name != 'pull_request' || "
    "github.event.pull_request.head.repo.full_name == github.repository) }}"
)


def _job():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"][JOB]


def _step():
    steps = [s for s in _job()["steps"] if s.get("name") == STEP]
    assert steps, f"job '{JOB}' has no step '{STEP}'"
    return steps[0]


class TestJobPermissions:
    """Only the job that uploads may request an OIDC token."""

    def test_job_can_request_oidc_token(self):
        assert _job().get("permissions", {}).get("id-token") == "write"

    def test_job_keeps_read_only_contents(self):
        """Job permissions replace the workflow's, so restate contents: read."""
        assert _job().get("permissions", {}).get("contents") == "read"


class TestUploadStep:
    """The upload authenticates with OIDC and fails loudly."""

    def test_uses_oidc(self):
        assert _step()["with"].get("use_oidc") is True

    def test_does_not_use_a_stored_token(self):
        assert "token" not in _step()["with"]

    def test_failed_upload_fails_ci(self):
        assert _step()["with"].get("fail_ci_if_error") is True

    def test_runs_only_where_oidc_is_available(self):
        assert _step().get("if") == OIDC_AVAILABLE
