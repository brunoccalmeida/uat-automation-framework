"""Tests for the Python version source: one file names it for every workflow.

The version lived in five places (two single-value matrices, the lint and
security jobs, and the Allure artifact name that ``build-report`` downloads).
A bump that missed one broke the report with "artifact not found" (#48).
setup-python reads ``.python-version`` (``python-version-file``), the file
pyenv and uv also use, so a bump edits one line. A single-value matrix tests
nothing extra (YAGNI); a multi-version matrix would also need a parameter in
the Allure results, or the report hides one version as a retry.
"""

import tomllib
from pathlib import Path

import pytest
import yaml
from packaging.specifiers import SpecifierSet

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
VERSION_FILE = ".python-version"


def _setup_python_steps():
    """Yield (workflow, job, step inputs) for each setup-python step."""
    for workflow in sorted(WORKFLOWS.glob("*.yml")):
        jobs = yaml.safe_load(workflow.read_text(encoding="utf-8"))["jobs"]
        for job_name, job in jobs.items():
            for step in job.get("steps", []):
                if step.get("uses", "").startswith("actions/setup-python@"):
                    yield workflow.name, job_name, step.get("with", {})


STEPS = list(_setup_python_steps())


def test_version_file_satisfies_requires_python():
    version = (ROOT / VERSION_FILE).read_text(encoding="utf-8").strip()
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    requires = SpecifierSet(pyproject["project"]["requires-python"])
    assert version in requires, f"{VERSION_FILE} {version} is outside {requires}"


def test_workflows_set_up_python():
    """Guard against a vacuous pass: the parametrized test needs cases."""
    assert STEPS, "no setup-python step found; the test below checks nothing"


@pytest.mark.parametrize(
    ("workflow", "job", "inputs"),
    STEPS,
    ids=[f"{workflow}:{job}" for workflow, job, _ in STEPS],
)
def test_setup_python_reads_version_file(workflow, job, inputs):
    """``python-version`` would win over the file and duplicate the version."""
    assert "python-version" not in inputs, f"{workflow}:{job} pins a version"
    assert (
        inputs.get("python-version-file") == VERSION_FILE
    ), f"{workflow}:{job} does not read {VERSION_FILE}"


@pytest.mark.parametrize("workflow", sorted(p.name for p in WORKFLOWS.glob("*.yml")))
def test_no_python_version_matrix(workflow):
    """A matrix version renames artifacts and checks on every bump."""
    text = (WORKFLOWS / workflow).read_text(encoding="utf-8")
    assert "matrix.python-version" not in text, f"{workflow} uses the matrix version"
