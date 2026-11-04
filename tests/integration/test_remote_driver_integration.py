"""Integration: browser sessions run in the configured Selenium Grid (#116).

Local and CI share one browser build only if the session really runs in the
container. The Grid's /status endpoint lists the session held by each slot,
so the check is observable from outside the framework.
"""

import json
import os
import urllib.request

import pytest

from tests.helpers.driver_setup import make_driver_manager

REMOTE_URL = os.getenv("SELENIUM_REMOTE_URL")


def _grid_session_ids(remote_url: str) -> set[str]:
    """Return the ids of the sessions the Grid is serving right now."""
    with urllib.request.urlopen(f"{remote_url}/status", timeout=10) as response:
        status = json.load(response)
    return {
        slot["session"]["sessionId"]
        for node in status["value"]["nodes"]
        for slot in node["slots"]
        if slot["session"]
    }


def test_session_is_served_by_configured_grid():
    """A driver built from the configuration opens its session in the Grid.

    Without a Grid the test is skipped locally, where a local browser is the
    default. In CI (GitHub sets CI=true) it fails instead: a skipped check
    counts as passed and would hide a job that lost its Grid.
    """
    if not REMOTE_URL:
        if os.getenv("CI"):
            pytest.fail(
                "CI must run the browser tests in the Grid: set SELENIUM_REMOTE_URL"
            )
        pytest.skip("no Selenium Grid configured (SELENIUM_REMOTE_URL)")
    manager = make_driver_manager()
    try:
        driver = manager.get_driver()

        assert driver.session_id in _grid_session_ids(REMOTE_URL)
    finally:
        manager.quit()
