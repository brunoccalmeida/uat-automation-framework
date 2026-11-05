"""CI fills the Allure Environment and Executor panels (#130).

Allure reads ``environment.properties`` and ``executor.json`` from the results
directory (allurereport.org/docs, How it works: "Environment file",
"Executor file"). Without them the Overview shows two empty panels.

Values come from the run itself (Grid ``/status``, the interpreter, the
installed bindings, GitHub's default variables), never from literals, so a
Dependabot bump of the Grid image shows up in the report on its own.
"""

import json
from pathlib import Path

import pytest
import yaml

from scripts.write_allure_metadata import (
    environment_properties,
    executor,
    main,
)

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"

# Shape of a real response, from the "Show Grid and browser versions" step
GRID_STATUS = {
    "value": {
        "ready": True,
        "nodes": [
            {
                "version": (
                    "4.51.0 (revision 35c5fab"
                    " 35c5fab4a58fa5878edb255eb7747b04ca51a015)"
                ),
                "slots": [
                    {
                        "stereotype": {
                            "browserName": "chrome",
                            "browserVersion": "155.0",
                        }
                    }
                ],
            }
        ],
    }
}

GITHUB_ENV = {
    "GITHUB_SERVER_URL": "https://github.com",
    "GITHUB_REPOSITORY": "owner/repo",
    "GITHUB_RUN_ID": "42091367989",
    "GITHUB_RUN_NUMBER": "612",
    "GITHUB_WORKFLOW": "Tests",
}


def _properties(text):
    """Parse the simple key=value lines Allure shows in the panel."""
    return dict(line.split("=", 1) for line in text.splitlines() if line)


class TestEnvironmentProperties:
    """The Environment panel: what ran the tests."""

    def test_lists_browser_grid_bindings_and_python(self):
        text = environment_properties(
            GRID_STATUS, python_version="3.14.10", selenium_version="4.52.0"
        )

        assert _properties(text) == {
            "Browser": "chrome 155.0",
            "Selenium.Grid": "4.51.0",
            "Selenium.Python": "4.52.0",
            "Python": "3.14.10",
        }

    def test_fails_when_the_grid_has_no_node(self):
        with pytest.raises(ValueError, match="no node"):
            environment_properties(
                {"value": {"nodes": []}},
                python_version="3.14.10",
                selenium_version="4.52.0",
            )


class TestExecutor:
    """The Executor panel: which CI run built the report."""

    def test_names_github_actions_and_links_the_run(self):
        assert executor(GITHUB_ENV) == {
            "name": "GitHub Actions",
            "type": "github",
            "buildName": "Tests #612",
            "buildOrder": 612,
            "buildUrl": "https://github.com/owner/repo/actions/runs/42091367989",
        }

    def test_fails_outside_github_actions(self):
        with pytest.raises(KeyError, match="GITHUB_RUN_ID"):
            executor({k: v for k, v in GITHUB_ENV.items() if k != "GITHUB_RUN_ID"})


class TestMain:
    """Both files land in the results directory Allure reads."""

    def test_writes_both_files_into_the_results_directory(self, tmp_path):
        environ = {**GITHUB_ENV, "SELENIUM_REMOTE_URL": "http://grid:4444"}
        fetched = []

        def fetch_status(url):
            fetched.append(url)
            return GRID_STATUS

        assert main([str(tmp_path)], environ, fetch_status) == 0

        assert fetched == ["http://grid:4444/status"]
        props = _properties((tmp_path / "environment.properties").read_text("utf-8"))
        assert props["Browser"] == "chrome 155.0"
        build = json.loads((tmp_path / "executor.json").read_text("utf-8"))
        assert build["buildOrder"] == 612


def _test_steps():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["test"]["steps"]


def _step_index(steps, needle):
    return next(i for i, step in enumerate(steps) if needle in step.get("run", ""))


class TestWorkflow:
    """The metadata lands in the results the report job downloads."""

    def test_written_after_e2e_and_before_the_upload(self):
        steps = _test_steps()
        e2e = _step_index(steps, "allure_behave.formatter:AllureFormatter")
        metadata = _step_index(steps, "scripts/write_allure_metadata.py")
        upload = next(
            i
            for i, step in enumerate(steps)
            if step.get("with", {}).get("name") == "allure-results"
        )

        assert e2e < metadata < upload

    def test_written_into_the_directory_that_is_uploaded(self):
        steps = _test_steps()
        metadata = steps[_step_index(steps, "scripts/write_allure_metadata.py")]
        upload = next(
            step
            for step in steps
            if step.get("with", {}).get("name") == "allure-results"
        )

        assert metadata["run"].split()[-1] == upload["with"]["path"]

    def test_written_even_when_tests_failed(self):
        steps = _test_steps()
        metadata = steps[_step_index(steps, "scripts/write_allure_metadata.py")]

        assert metadata["if"] == "${{ !cancelled() }}"
