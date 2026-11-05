"""Unit tests for the integration-test failure artifacts (#129).

A flaky integration failure left only a one-line message in the CI log; the
screenshot and page source show the state the browser was really in.
"""

from pathlib import Path, PurePosixPath
from unittest.mock import Mock

import pytest
import yaml
from selenium.common.exceptions import WebDriverException

from tests.helpers.failure_artifacts import (
    ARTIFACTS_DIR,
    PHASE_REPORT_KEY,
    call_failed,
    save_failure_artifacts,
)

NODEID = "tests/integration/test_header.py::TestMenu::test_logout[firefox]"
WORKFLOW = Path(__file__).resolve().parent.parent / ".github/workflows/tests.yml"
JOBS = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]
INTEGRATION_JOBS = [
    name
    for name, job in JOBS.items()
    if any("pytest tests/integration/" in step.get("run", "") for step in job["steps"])
]


def _node_with_reports(**outcomes):
    """Test item mock whose stash holds a report per phase (when=outcome)."""
    node = Mock()
    node.stash = {
        PHASE_REPORT_KEY: {
            when: Mock(failed=outcome == "failed") for when, outcome in outcomes.items()
        }
    }
    return node


class TestCallFailed:
    """call_failed: only a failure in the test body has a page to capture."""

    def test_is_true_when_the_test_body_failed(self):
        """A failed call phase is the failure worth a screenshot."""
        assert call_failed(_node_with_reports(setup="passed", call="failed"))

    def test_is_false_when_the_test_body_passed(self):
        """A passing test saves nothing."""
        assert not call_failed(_node_with_reports(setup="passed", call="passed"))

    def test_is_false_when_only_setup_ran(self):
        """A setup failure never reached the page; there is no call report."""
        assert not call_failed(_node_with_reports(setup="failed"))

    def test_is_false_without_any_report(self):
        """A node the hook never saw has nothing in its stash."""
        node = Mock()
        node.stash = {}

        assert not call_failed(node)


class TestSaveFailureArtifacts:
    """save_failure_artifacts: screenshot and page source of a failed test."""

    @staticmethod
    def _driver():
        driver = Mock()
        driver.current_url = "https://www.saucedemo.com/inventory.html"
        driver.page_source = "<html><body>inventory</body></html>"
        return driver

    def test_saves_screenshot_and_page_source_named_after_the_test(self, tmp_path):
        """Both files go to out_dir, named after the test id in a safe form."""
        driver = self._driver()

        saved = save_failure_artifacts(driver, NODEID, tmp_path)

        stem = "tests_integration_test_header.py_TestMenu_test_logout_firefox_"
        png, html = tmp_path / f"{stem}.png", tmp_path / f"{stem}.html"
        assert saved == [png, html]
        driver.save_screenshot.assert_called_once_with(str(png))
        assert html.read_text(encoding="utf-8") == (
            "<!-- URL: https://www.saucedemo.com/inventory.html -->\n"
            "<html><body>inventory</body></html>"
        )

    def test_creates_the_output_folder(self, tmp_path):
        """The folder may not exist yet on a fresh CI checkout."""
        out_dir = tmp_path / "reports" / "integration-failures"

        save_failure_artifacts(self._driver(), NODEID, out_dir)

        assert out_dir.is_dir()

    def test_a_dead_browser_warns_instead_of_hiding_the_test_failure(self, tmp_path):
        """If the session is gone, warn; an exception would bury the real one."""
        driver = self._driver()
        driver.save_screenshot.side_effect = WebDriverException("session deleted")

        with pytest.warns(UserWarning, match="session deleted"):
            saved = save_failure_artifacts(driver, NODEID, tmp_path)

        assert not saved


def _uploaded_paths_on_failure(job):
    """Paths that the job's upload-artifact steps send when the job fails."""
    return [
        PurePosixPath(line.strip())
        for step in job["steps"]
        if step.get("uses", "").startswith("actions/upload-artifact@")
        and step.get("if") in ("failure()", "always()")
        for line in step["with"]["path"].splitlines()
        if line.strip()
    ]


def test_the_workflow_runs_integration_tests_somewhere():
    """Guard: the check below must have jobs to look at."""
    assert INTEGRATION_JOBS


@pytest.mark.parametrize("job_name", INTEGRATION_JOBS)
def test_every_integration_job_uploads_the_failure_artifacts(job_name):
    """A failure's screenshot is useless if it stays on the runner."""
    target = PurePosixPath(ARTIFACTS_DIR.as_posix())

    paths = _uploaded_paths_on_failure(JOBS[job_name])

    assert any(target.is_relative_to(path) for path in paths), (
        f"job '{job_name}' runs integration tests but uploads no {target} "
        f"on failure (uploads: {paths})"
    )
