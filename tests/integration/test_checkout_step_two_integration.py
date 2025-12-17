"""Integration tests for CheckoutStepTwoPage with real browser.

Tests CheckoutStepTwoPage interactions with actual DOM elements.
"""

import pytest

from pages.cart_page import CartPage
from pages.checkout_step_one_page import CheckoutStepOnePage
from pages.checkout_step_two_page import CheckoutStepTwoPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


@pytest.fixture(scope="function")
def checkout_step_two(driver, base_url):
    """Provide driver on checkout step two page.

    Args:
        driver: WebDriver instance.
        base_url: Application base URL.

    Yields:
        WebDriver on checkout step two (overview) page.
    """
    driver.get(base_url)
    login_page = LoginPage(driver)
    login_page.login("standard_user", "secret_sauce")

    # Add product and complete step one
    inventory_page = InventoryPage(driver)
    inventory_page.add_product_to_cart("Sauce Labs Backpack")
    inventory_page.click_shopping_cart()

    cart_page = CartPage(driver)
    cart_page.click_checkout()

    step_one_page = CheckoutStepOnePage(driver)
    step_one_page.enter_first_name("John")
    step_one_page.enter_last_name("Doe")
    step_one_page.enter_zip_code("12345")
    step_one_page.click_continue()

    yield driver


class TestCheckoutStepTwoElements:
    """Test CheckoutStepTwoPage elements are present."""

    def test_checkout_summary_container_is_present(self, checkout_step_two):
        """Checkout summary container should be present."""
        page = CheckoutStepTwoPage(checkout_step_two)

        assert page.is_on_checkout_overview_page()

    def test_payment_info_is_displayed(self, checkout_step_two):
        """Payment information should be displayed."""
        page = CheckoutStepTwoPage(checkout_step_two)

        assert page.is_payment_info_displayed()

    def test_shipping_info_is_displayed(self, checkout_step_two):
        """Shipping information should be displayed."""
        page = CheckoutStepTwoPage(checkout_step_two)

        assert page.is_shipping_info_displayed()

    def test_finish_button_exists(self, checkout_step_two):
        """Finish button should exist."""
        page = CheckoutStepTwoPage(checkout_step_two)

        assert page.is_element_present(page.FINISH_BUTTON, timeout=3)

    def test_cancel_button_exists(self, checkout_step_two):
        """Cancel button should exist."""
        page = CheckoutStepTwoPage(checkout_step_two)

        assert page.is_element_present(page.CANCEL_BUTTON, timeout=3)


class TestCheckoutStepTwoOrderSummary:
    """Test order summary information."""

    def test_product_appears_in_summary(self, checkout_step_two):
        """Added product should appear in order summary."""
        page = CheckoutStepTwoPage(checkout_step_two)

        assert page.is_product_in_summary("Sauce Labs Backpack")

    def test_item_total_is_displayed(self, checkout_step_two):
        """Item subtotal should be displayed and numeric."""
        page = CheckoutStepTwoPage(checkout_step_two)

        item_total = page.get_item_total()
        assert isinstance(item_total, float)
        assert item_total > 0

    def test_tax_is_displayed(self, checkout_step_two):
        """Tax should be displayed and numeric."""
        page = CheckoutStepTwoPage(checkout_step_two)

        tax = page.get_tax()
        assert isinstance(tax, float)
        assert tax > 0

    def test_total_is_displayed(self, checkout_step_two):
        """Total should be displayed and numeric."""
        page = CheckoutStepTwoPage(checkout_step_two)

        total = page.get_total()
        assert isinstance(total, float)
        assert total > 0

    def test_total_equals_subtotal_plus_tax(self, checkout_step_two):
        """Total should equal subtotal plus tax."""
        page = CheckoutStepTwoPage(checkout_step_two)

        item_total = page.get_item_total()
        tax = page.get_tax()
        total = page.get_total()

        expected_total = round(item_total + tax, 2)
        assert total == expected_total


class TestCheckoutStepTwoInteractions:
    """Test CheckoutStepTwoPage interactions."""

    def test_finish_completes_order(self, checkout_step_two):
        """Finish button should complete order and navigate to completion page."""
        page = CheckoutStepTwoPage(checkout_step_two)

        page.click_finish()

        assert "/checkout-complete.html" in checkout_step_two.current_url

    def test_cancel_returns_to_inventory(self, checkout_step_two):
        """Cancel button should return to inventory page."""
        page = CheckoutStepTwoPage(checkout_step_two)

        page.click_cancel()

        assert "/inventory.html" in checkout_step_two.current_url


class TestCheckoutStepTwoMultipleProducts:
    """Test checkout with multiple products."""

    def test_multiple_products_in_summary(self, driver, base_url):
        """Multiple products should appear in order summary."""
        driver.get(base_url)
        login_page = LoginPage(driver)
        login_page.login("standard_user", "secret_sauce")

        # Add multiple products
        inventory_page = InventoryPage(driver)
        inventory_page.add_product_to_cart("Sauce Labs Backpack")
        inventory_page.add_product_to_cart("Sauce Labs Bike Light")
        inventory_page.click_shopping_cart()

        cart_page = CartPage(driver)
        cart_page.click_checkout()

        step_one_page = CheckoutStepOnePage(driver)
        step_one_page.enter_first_name("John")
        step_one_page.enter_last_name("Doe")
        step_one_page.enter_zip_code("12345")
        step_one_page.click_continue()

        page = CheckoutStepTwoPage(driver)
        assert page.is_product_in_summary("Sauce Labs Backpack")
        assert page.is_product_in_summary("Sauce Labs Bike Light")
