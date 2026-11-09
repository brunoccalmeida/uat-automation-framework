"""Smoke tests to validate basic framework setup.

These tests verify that the core infrastructure (config loading,
WebDriver initialization, basic navigation) works correctly.
"""

import pytest

from core.config import load_settings
from tests.helpers.driver_setup import make_driver_manager


@pytest.fixture(name="driver_manager")
def fixture_driver_manager():
    """Create driver manager instance with CI-friendly configuration."""
    manager = make_driver_manager()
    yield manager
    manager.quit()


def test_driver_manager_creates_driver(driver_manager):
    """Verify driver manager can create a WebDriver instance."""
    driver = driver_manager.get_driver()
    assert driver is not None


def test_can_access_sauce_demo(driver_manager):
    """Smoke test: Verify we can access Sauce Demo homepage.

    This is the most basic end-to-end test that validates:
    - Configuration loading works
    - WebDriver initialization works
    - Network connectivity works
    - Target application is accessible
    """
    driver = driver_manager.get_driver()
    base_url = load_settings().base_url

    # Navigate to Sauce Demo
    driver.get(base_url)

    # Verify page loaded by checking title
    assert "Swag Labs" in driver.title

    # Verify we're on the right page
    assert "saucedemo" in driver.current_url.lower()
