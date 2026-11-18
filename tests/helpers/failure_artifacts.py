"""Screenshot, page source and timing of a failed integration test (#129, #180).

A flaky integration failure left only a one-line message in the CI log. The
browser state at the failure (screenshot, page source, URL) tells what really
happened. Files go to reports/, which CI already uploads as an artifact.

The pytest hook in tests/integration/conftest.py stores each phase's report
under PHASE_REPORT_KEY, as in the pytest docs ("Making test result
information available in fixtures"); the driver fixture reads it on teardown.
"""

import re
import warnings
from pathlib import Path

import pytest
from selenium.common.exceptions import WebDriverException

ARTIFACTS_DIR = Path("reports/integration-failures")

PHASE_REPORT_KEY = pytest.StashKey[dict[str, pytest.TestReport]]()

# W3C Performance Timeline: the page's navigation and every resource it
# fetched, with duration and HTTP status (#180). A blank SPA shell alone
# cannot tell a slow or failed bundle from a script error; this can.
TIMING_SCRIPT = """
return JSON.stringify({
  readyState: document.readyState,
  entries: performance.getEntries().map((entry) => entry.toJSON()),
}, null, 2);
"""


def call_failed(node) -> bool:
    """Tell whether the test body failed.

    A setup failure (e.g. no Grid) never reached a page, so it has no call
    report and nothing to capture.
    """
    report = node.stash.get(PHASE_REPORT_KEY, {}).get("call")
    return report is not None and report.failed


def save_failure_artifacts(driver, nodeid: str, out_dir: Path = ARTIFACTS_DIR):
    """Save the screenshot, page source (with its URL) and timing of a failure.

    Args:
        driver: WebDriver of the failed test, still open.
        nodeid: pytest node id, used to name the files.
        out_dir: Folder for the files, created if missing.

    Returns:
        The saved paths, or an empty list if the browser could not answer.
        That case only warns: raising would bury the test's own failure.
    """
    stem = re.sub(r"[^\w.-]+", "_", nodeid)
    png, html = out_dir / f"{stem}.png", out_dir / f"{stem}.html"
    timing = out_dir / f"{stem}.timing.json"
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(png))
        source = f"<!-- URL: {driver.current_url} -->\n{driver.page_source}"
        timeline = driver.execute_script(TIMING_SCRIPT)
    except WebDriverException as exc:
        warnings.warn(f"No failure artifacts for {nodeid}: {exc}", stacklevel=2)
        return []
    html.write_text(source, encoding="utf-8")
    timing.write_text(timeline, encoding="utf-8")
    return [png, html, timing]
