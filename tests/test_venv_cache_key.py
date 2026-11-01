"""Tests for the venv cache key: it must name the exact Python version.

A venv symlinks the exact interpreter (``/opt/hostedtoolcache/Python/3.14.9``).
Runner images roll out gradually, so jobs of the same run can get different
patch versions. Keyed by the matrix minor version (``3.14``), a venv built on
3.14.9 is restored on 3.14.8, ``poetry install`` is skipped on the cache hit
and the job runs with a broken venv (#84). The snok/install-poetry docs key
by ``steps.setup-python.outputs.python-version`` for this reason.
"""

from pathlib import Path

import pytest
import yaml

WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"


def _venv_cache_steps():
    """Yield (workflow, job, step, setup-python step id) for each venv cache."""
    for workflow in sorted(WORKFLOWS.glob("*.yml")):
        jobs = yaml.safe_load(workflow.read_text(encoding="utf-8"))["jobs"]
        for job_name, job in jobs.items():
            steps = job.get("steps", [])
            setup_ids = [
                step.get("id")
                for step in steps
                if step.get("uses", "").startswith("actions/setup-python@")
            ]
            for step in steps:
                key = step.get("with", {}).get("key", "")
                if step.get("uses", "").startswith("actions/cache@") and (
                    key.startswith("venv-")
                ):
                    yield workflow.name, job_name, key, setup_ids


CACHES = list(_venv_cache_steps())


def test_workflows_cache_a_venv():
    """Guard against a vacuous pass: the parametrized test needs cases."""
    assert CACHES, "no venv cache found; the key test below checks nothing"


@pytest.mark.parametrize(
    ("workflow", "job", "key", "setup_ids"),
    CACHES,
    ids=[f"{workflow}:{job}" for workflow, job, _, _ in CACHES],
)
def test_venv_cache_key_uses_exact_python_version(workflow, job, key, setup_ids):
    """The key names the interpreter setup-python installed in this job."""
    assert (
        len(setup_ids) == 1 and setup_ids[0]
    ), f"{workflow}:{job} needs one setup-python step with an id"
    expected = f"steps.{setup_ids[0]}.outputs.python-version"
    assert expected in key, f"{workflow}:{job} cache key lacks {expected}: {key}"
    assert (
        "matrix.python-version" not in key
    ), f"{workflow}:{job} cache key uses the minor version: {key}"
