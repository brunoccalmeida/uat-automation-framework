"""Tests that every workflow job is bounded in time and in credentials.

``timeout-minutes``: without it a hung job (e.g. a Selenium Grid that never
becomes ready) runs until GitHub's default of 360 minutes, burning runner
minutes and blocking the one-PR-at-a-time merge queue. Values are about 3x
the slowest of 20 recent green runs, rounded up to a multiple of 5 (minimum
5); each job states its measured slowest run next to the value (#135).
The ``test`` job is sized for an estimated mass failure instead (~21 min).

``persist-credentials: false``: by default ``actions/checkout`` keeps the job
token on disk so later steps can run authenticated git commands. Any later
step can then read it. No job here pushes with git (``deploy-report`` passes
its own ``github_token`` to the deploy action and has no checkout), so every
checkout opts out.
"""

from pathlib import Path

import pytest
import yaml

WORKFLOWS_DIR = Path(__file__).resolve().parent.parent / ".github" / "workflows"
CHECKOUT_ACTION = "actions/checkout@"


def _load_jobs():
    """Return (id, job) for every job of every workflow."""
    jobs = []
    for workflow in sorted(WORKFLOWS_DIR.glob("*.y*ml")):
        content = yaml.safe_load(workflow.read_text(encoding="utf-8"))
        for job_id, job in content["jobs"].items():
            jobs.append((f"{workflow.name}::{job_id}", job))
    return jobs


def _load_checkouts(jobs):
    """Return (id, step) for every actions/checkout step."""
    return [
        (f"{job_id}::step{index}", step)
        for job_id, job in jobs
        for index, step in enumerate(job.get("steps", []), start=1)
        if str(step.get("uses", "")).startswith(CHECKOUT_ACTION)
    ]


JOBS = _load_jobs()
CHECKOUTS = _load_checkouts(JOBS)


def test_workflows_have_jobs_and_checkouts():
    """Guard against a vacuous pass (wrong path or parsing finds nothing)."""
    assert JOBS, f"no jobs found under {WORKFLOWS_DIR}"
    assert CHECKOUTS, f"no '{CHECKOUT_ACTION}' step found under {WORKFLOWS_DIR}"


def timeout_problem(job):
    """Return why ``job`` breaks the timeout rule, or None if it complies."""
    # A job that calls a reusable workflow cannot take timeout-minutes
    # (GitHub docs, "Supported keywords for jobs that call a reusable
    # workflow"): the limit belongs to the called workflow's own jobs. No
    # such job exists yet; when one appears, decide its rule here on purpose
    # instead of exempting it silently.
    if "uses" in job:
        return (
            "job calls a reusable workflow, which cannot take timeout-minutes: "
            "set the timeout in the called workflow's jobs and teach this test "
            "that case explicitly"
        )
    timeout = job.get("timeout-minutes")
    # bool is an int subclass: "timeout-minutes: true" must not pass
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
        return (
            f"job has no positive 'timeout-minutes' (got {timeout!r}); "
            "GitHub's default is 360 minutes"
        )
    return None


@pytest.mark.parametrize(
    "job,expected",
    [
        ({"runs-on": "ubuntu-latest", "timeout-minutes": 5}, None),
        ({"runs-on": "ubuntu-latest"}, "no positive 'timeout-minutes'"),
        ({"runs-on": "ubuntu-latest", "timeout-minutes": 0}, "no positive"),
        ({"runs-on": "ubuntu-latest", "timeout-minutes": True}, "no positive"),
        ({"uses": "./.github/workflows/reusable.yml"}, "reusable workflow"),
    ],
    ids=["valid", "missing", "zero", "bool", "reusable-call"],
)
def test_timeout_problem(job, expected):
    """The rule itself, on synthetic jobs (including cases absent today)."""
    problem = timeout_problem(job)
    if expected is None:
        assert problem is None
    else:
        assert problem is not None and expected in problem


@pytest.mark.parametrize("job", [job for _, job in JOBS], ids=[i for i, _ in JOBS])
def test_job_has_timeout(job):
    """Each job must cap its run time with a positive ``timeout-minutes``."""
    problem = timeout_problem(job)
    assert problem is None, problem


@pytest.mark.parametrize(
    "step", [step for _, step in CHECKOUTS], ids=[i for i, _ in CHECKOUTS]
)
def test_checkout_does_not_persist_credentials(step):
    """Each checkout must opt out of keeping the token for later steps."""
    persist = step.get("with", {}).get("persist-credentials")
    assert persist is False, (
        f"checkout '{step.get('name', step['uses'])}' persists the job token "
        f"(persist-credentials: {persist!r}); set it to false"
    )
