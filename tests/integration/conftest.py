"""Pytest fixtures for integration tests.

Provides shared fixtures for integration testing with real browsers.
"""

import pytest

from core.config import get_base_url, get_default_password, load_config
from tests.helpers.driver_setup import make_driver_manager
from tests.helpers.navigation import (
    go_to_cart,
    go_to_inventory,
    go_to_step_one,
    go_to_step_two,
)


@pytest.fixture(name="driver", scope="function")
def fixture_driver():
    """Create WebDriver instance for integration tests.

    Yields:
        WebDriver instance configured for integration testing.
    """
    dm = make_driver_manager()
    yield dm.get_driver()

    # Teardown
    dm.quit()


@pytest.fixture(name="base_url", scope="function")
def fixture_base_url():
    """Get base URL from configuration.

    Returns:
        Base URL for application under test.
    """
    config = load_config()
    return get_base_url(config)


@pytest.fixture(name="password")
def fixture_password():
    """Get the test users' password from configuration."""
    return get_default_password(load_config())


@pytest.fixture(name="authenticated_driver")
def fixture_authenticated_driver(driver, base_url):
    """Driver logged in as standard_user, on the inventory page."""
    go_to_inventory(driver, base_url)
    return driver


@pytest.fixture(name="cart_with_products")
def fixture_cart_with_products(driver, base_url):
    """Driver on the cart page with 2 products."""
    go_to_cart(driver, base_url, ("Sauce Labs Backpack", "Sauce Labs Bike Light"))
    return driver


@pytest.fixture(name="checkout_step_one")
def fixture_checkout_step_one(driver, base_url):
    """Driver on checkout step one with a product in the cart."""
    go_to_step_one(driver, base_url)
    return driver


@pytest.fixture(name="checkout_step_two")
def fixture_checkout_step_two(driver, base_url):
    """Driver on checkout step two (overview) with valid customer info."""
    go_to_step_two(driver, base_url)
    return driver
