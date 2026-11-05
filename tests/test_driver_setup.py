"""Unit tests for the DriverManager helper shared by browser tests (#118).

The helper must apply the same configuration hierarchy as Behave
(features/environment.py): an environment variable documented in
CONFIGURATION.md and silently ignored here would make the two entry points
open different browsers.
"""

import pytest

from core.config import get_browser_config, load_config
from tests.helpers.driver_setup import make_driver_manager


@pytest.mark.parametrize("browser", ["firefox", "chrome"])
def test_browser_env_var_selects_the_browser(monkeypatch, browser):
    """BROWSER overrides browser.name from config.yaml."""
    monkeypatch.setenv("BROWSER", browser)

    manager = make_driver_manager()

    assert manager.browser_config["name"] == browser


def test_config_file_browser_is_kept_without_env_var(monkeypatch):
    """Without BROWSER, the name from config.yaml is used unchanged."""
    monkeypatch.delenv("BROWSER", raising=False)

    manager = make_driver_manager()

    assert manager.browser_config["name"] == get_browser_config(load_config())["name"]
