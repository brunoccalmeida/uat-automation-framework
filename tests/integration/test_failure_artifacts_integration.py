"""Integration tests of the failure artifacts' evidence in a real browser.

The unit tests mock the driver, so only a browser can show that the evidence
an investigation needs (#180) really arrives: the document's ready state and
the Resource Timing entries, the app's JavaScript among them, and the errors
the page threw, heard over WebDriver BiDi from the first navigation on.
"""

import json

from selenium.webdriver.support.wait import WebDriverWait

from pages.login_page import LoginPage
from tests.helpers.failure_artifacts import PAGE_ERRORS_KEY, save_failure_artifacts

# Throws while loading, as an app bundle that breaks before rendering would
THROWING_PAGE = (
    "data:text/html,<div id=root></div>"
    "<script>throw new Error('bundle broke before render')</script>"
)


def test_timing_lists_the_ready_state_and_the_scripts_that_loaded(
    driver, base_url, tmp_path
):
    """A rendered page reports 'complete' and the app bundle it ran."""
    LoginPage(driver).open(base_url)

    timing_file = save_failure_artifacts(driver, "timing-probe", tmp_path)[-1]

    timing = json.loads(timing_file.read_text(encoding="utf-8"))
    assert timing["readyState"] == "complete"
    scripts = [e for e in timing["entries"] if e.get("initiatorType") == "script"]
    assert scripts, f"no script in the timeline: {timing['entries']}"
    assert all("duration" in e and "responseStatus" in e for e in scripts), scripts


def test_the_driver_records_errors_thrown_during_the_first_page_load(driver, request):
    """The listener is on before the test navigates, not added after."""
    driver.get(THROWING_PAGE)

    errors = request.node.stash[PAGE_ERRORS_KEY]
    # BiDi events arrive over a WebSocket, after driver.get returns
    WebDriverWait(driver, 5).until(
        lambda _: errors, message="no page error arrived over BiDi"
    )
    assert "bundle broke before render" in errors[0]["text"], errors
