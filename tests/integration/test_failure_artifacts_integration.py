"""Integration test of the failure artifacts' timing script in a real browser.

The unit tests mock execute_script, so only a browser can show that the
script runs and returns what an investigation needs (#180): the document's
ready state and the Resource Timing entries, the app's JavaScript among them.
"""

import json

from pages.login_page import LoginPage
from tests.helpers.failure_artifacts import save_failure_artifacts


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
