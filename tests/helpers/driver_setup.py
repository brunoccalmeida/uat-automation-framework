"""DriverManager setup shared by the tests that open a real browser."""

import os

from core.config import get_browser_config, load_config
from core.config_resolver import apply_config_hierarchy
from core.driver_manager import DriverManager


def make_driver_manager():
    """Build a DriverManager from config.yaml.

    Environment variables override config.yaml, as in Behave
    (features/environment.py): HEADLESS runs without a display, BROWSER
    selects the browser and SELENIUM_REMOTE_URL opens the session in a
    Selenium Grid (e.g. the docker-selenium container).
    """
    browser_config = get_browser_config(load_config())
    apply_config_hierarchy(
        config=browser_config,
        key="headless",
        cli_value=None,
        env_value=os.getenv("HEADLESS"),
    )
    apply_config_hierarchy(
        config=browser_config,
        key="name",
        cli_value=None,
        env_value=os.getenv("BROWSER"),
    )
    apply_config_hierarchy(
        config=browser_config,
        key="remote_url",
        cli_value=None,
        env_value=os.getenv("SELENIUM_REMOTE_URL"),
    )
    return DriverManager(browser_config)
