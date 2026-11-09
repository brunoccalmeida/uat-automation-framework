"""Unit tests for the DriverManager helper shared by browser tests (#118).

The helper must read the same settings as Behave (features/environment.py): a
variable documented in CONFIGURATION.md and silently ignored here would make
the two entry points open different browsers.
"""

import pytest

from tests.helpers.driver_setup import make_driver_manager

pytestmark = pytest.mark.usefixtures("settings_env")


@pytest.mark.parametrize("browser", ["firefox", "chrome"])
def test_browser_env_var_selects_the_browser(monkeypatch, browser):
    """BROWSER selects the browser."""
    monkeypatch.setenv("BROWSER", browser)

    manager = make_driver_manager()

    assert manager.browser_config["name"] == browser


def test_default_browser_is_used_without_env_var():
    """Without BROWSER, the default browser is used."""
    assert make_driver_manager().browser_config["name"] == "chrome"
