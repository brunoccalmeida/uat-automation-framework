"""Screenshot, page source, timing and page errors of a failed test (#129, #180).

A flaky integration failure left only a one-line message in the CI log. The
browser state at the failure (screenshot, page source, URL) tells what really
happened. Files go to reports/, which CI already uploads as an artifact.

The pytest hook in tests/integration/conftest.py stores each phase's report
under PHASE_REPORT_KEY, as in the pytest docs ("Making test result
information available in fixtures"); the driver fixture reads it on teardown.
"""

import json
import re
import warnings
from dataclasses import asdict
from pathlib import Path

import pytest
from selenium.common.exceptions import WebDriverException

ARTIFACTS_DIR = Path("reports/integration-failures")

PHASE_REPORT_KEY = pytest.StashKey[dict[str, pytest.TestReport]]()
# The page's console messages and JavaScript errors, recorded by the driver
# fixture from the session's start (#180)
PAGE_ERRORS_KEY = pytest.StashKey[list[dict]]()


def watch_page_errors(driver) -> list[dict]:
    """Record the page's console messages and JavaScript errors from now on.

    Needs a session with WebDriver BiDi (DriverManager enables it). Call it
    before the first navigation: an app bundle that throws does so while
    driver.get loads the page.

    Args:
        driver: WebDriver whose pages to listen to.

    Returns:
        The list the BiDi handlers fill, one dict per log entry (text, level,
        timestamp and, for JavaScript errors, the stack trace).
    """
    entries: list[dict] = []
    driver.script.add_console_message_handler(lambda e: entries.append(asdict(e)))
    driver.script.add_javascript_error_handler(lambda e: entries.append(asdict(e)))
    return entries


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


def save_failure_artifacts(
    driver,
    nodeid: str,
    out_dir: Path = ARTIFACTS_DIR,
    page_errors: list[dict] | None = None,
):
    """Save the screenshot, page source (with its URL), page errors and timing.

    Args:
        driver: WebDriver of the failed test, still open.
        nodeid: pytest node id, used to name the files.
        out_dir: Folder for the files, created if missing.
        page_errors: Entries from watch_page_errors, if it ran. An empty list
            is saved too: "no JavaScript error" rules out a cause.

    Returns:
        The saved paths. If the browser cannot answer, only the page errors
        (or nothing): that case only warns, since raising would bury the
        test's own failure.
    """
    stem = re.sub(r"[^\w.-]+", "_", nodeid)
    png, html = out_dir / f"{stem}.png", out_dir / f"{stem}.html"
    timing = out_dir / f"{stem}.timing.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    # The page errors are already in hand: save them before asking the
    # browser anything, so a crashed tab cannot cost them too.
    console = []
    if page_errors is not None:
        console = [out_dir / f"{stem}.console.json"]
        console[0].write_text(json.dumps(page_errors, indent=2), encoding="utf-8")
    try:
        driver.save_screenshot(str(png))
        source = f"<!-- URL: {driver.current_url} -->\n{driver.page_source}"
    except WebDriverException as exc:
        warnings.warn(f"No failure artifacts for {nodeid}: {exc}", stacklevel=2)
        return console
    html.write_text(source, encoding="utf-8")
    saved = [png, html, *console]
    # The timeline is extra evidence: if the page cannot run the script,
    # keep the screenshot and source rather than lose them too.
    try:
        timeline = driver.execute_script(TIMING_SCRIPT)
    except WebDriverException as exc:
        warnings.warn(f"No timing artifact for {nodeid}: {exc}", stacklevel=2)
        return saved
    timing.write_text(timeline, encoding="utf-8")
    return [*saved, timing]
