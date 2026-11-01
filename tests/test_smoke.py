"""Smoke tests to validate basic framework setup.

These tests verify that the core infrastructure (config loading,
WebDriver initialization, basic navigation) works correctly.
"""

import pytest

from core.config import get_base_url, load_config
from tests.helpers.driver_setup import make_driver_manager


@pytest.fixture(name="config")
def fixture_config():
    """Load configuration for tests."""
    return load_config("config.yaml")


@pytest.fixture(name="driver_manager")
def fixture_driver_manager():
    """Create driver manager instance with CI-friendly configuration."""
    manager = make_driver_manager()
    yield manager
    manager.quit()


def test_config_loads_successfully(config):
    """Verify configuration loads without errors."""
    assert config is not None
    assert "environment" in config
    assert "browser" in config


def test_can_get_base_url(config):
    """Verify base URL can be extracted from config."""
    base_url = get_base_url(config)
    assert base_url is not None
    assert "saucedemo" in base_url.lower()


def test_driver_manager_creates_driver(driver_manager):
    """Verify driver manager can create a WebDriver instance."""
    driver = driver_manager.get_driver()
    assert driver is not None


def test_can_access_sauce_demo(driver_manager, config):
    """Smoke test: Verify we can access Sauce Demo homepage.

    This is the most basic end-to-end test that validates:
    - Configuration loading works
    - WebDriver initialization works
    - Network connectivity works
    - Target application is accessible
    """
    driver = driver_manager.get_driver()
    base_url = get_base_url(config)

    # Navigate to Sauce Demo
    driver.get(base_url)

    # Verify page loaded by checking title
    assert "Swag Labs" in driver.title

    # Verify we're on the right page
    assert "saucedemo" in driver.current_url.lower()
