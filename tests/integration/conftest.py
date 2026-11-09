"""Pytest fixtures for integration tests.

Provides shared fixtures for integration testing with real browsers.
"""

import pytest

from core.config import ConfigurationError, load_settings
from tests.helpers.driver_setup import make_driver_manager
from tests.helpers.failure_artifacts import (
    PHASE_REPORT_KEY,
    call_failed,
    save_failure_artifacts,
)
from tests.helpers.navigation import (
    go_to_cart,
    go_to_inventory,
    go_to_step_one,
    go_to_step_two,
)


def pytest_configure(config):
    """Stop before any test runs if a setting is wrong (fail fast).

    Only listing the tests (--collect-only) opens no browser and needs none.
    """
    if config.getoption("collectonly"):
        return
    try:
        load_settings()
    except ConfigurationError as error:
        raise pytest.UsageError(str(error)) from error


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):  # pylint: disable=unused-argument
    """Store each phase's report on the item, for the driver fixture.

    pytest docs, "Making test result information available in fixtures";
    ``call`` is part of the hook's signature.
    """
    report = yield
    item.stash.setdefault(PHASE_REPORT_KEY, {})[report.when] = report
    return report


@pytest.fixture(name="driver", scope="function")
def fixture_driver(request):
    """Create WebDriver instance for integration tests.

    On a failed test, saves its screenshot and page source before quitting
    (#129): the CI log alone cannot show the browser state.

    Yields:
        WebDriver instance configured for integration testing.
    """
    dm = make_driver_manager()
    driver = dm.get_driver()
    yield driver

    # Teardown
    if call_failed(request.node):
        save_failure_artifacts(driver, request.node.nodeid)
    dm.quit()


@pytest.fixture(name="base_url", scope="function")
def fixture_base_url():
    """Get base URL from configuration.

    Returns:
        Base URL for application under test.
    """
    return load_settings().base_url


@pytest.fixture(name="password")
def fixture_password():
    """Get the test users' password from configuration."""
    return load_settings().test_user_password.get_secret_value()


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
