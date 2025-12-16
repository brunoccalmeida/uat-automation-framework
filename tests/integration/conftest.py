"""Pytest fixtures for integration tests.

Provides shared fixtures for integration testing with real browsers.
"""

import os

import pytest

from core.config import get_base_url, get_browser_config, load_config
from core.config_resolver import apply_config_hierarchy
from core.driver_manager import DriverManager


@pytest.fixture(scope="function")
def driver():
    """Create WebDriver instance for integration tests.

    Yields:
        WebDriver instance configured for integration testing.
    """
    # Load configuration
    config = load_config()
    browser_config = get_browser_config(config)

    # Apply headless mode hierarchy (respects HEADLESS env var for CI)
    apply_config_hierarchy(
        config=browser_config,
        key="headless",
        cli_value=None,
        env_value=os.getenv("HEADLESS"),
    )

    # Create driver
    dm = DriverManager(browser_config)
    driver = dm.get_driver()

    yield driver

    # Teardown
    dm.quit()


@pytest.fixture(scope="function")
def base_url():
    """Get base URL from configuration.

    Returns:
        Base URL for application under test.
    """
    config = load_config()
    return get_base_url(config)
