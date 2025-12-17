"""Integration tests for CheckoutStepOnePage with real browser.

Tests CheckoutStepOnePage interactions with actual DOM elements.
"""

import pytest

from pages.cart_page import CartPage
from pages.checkout_step_one_page import CheckoutStepOnePage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


@pytest.fixture(scope="function")
def checkout_step_one(driver, base_url):
    """Provide driver on checkout step one page.

    Args:
        driver: WebDriver instance.
        base_url: Application base URL.

    Yields:
        WebDriver on checkout step one page.
    """
    driver.get(base_url)
    login_page = LoginPage(driver)
    login_page.login("standard_user", "secret_sauce")

    # Add product and go to checkout
    inventory_page = InventoryPage(driver)
    inventory_page.add_product_to_cart("Sauce Labs Backpack")
    inventory_page.click_shopping_cart()

    cart_page = CartPage(driver)
    cart_page.click_checkout()

    yield driver


class TestCheckoutStepOneElements:
    """Test CheckoutStepOnePage elements are present."""

    def test_checkout_info_container_is_present(self, checkout_step_one):
        """Checkout info container should be present."""
        page = CheckoutStepOnePage(checkout_step_one)

        assert page.is_on_checkout_form()

    def test_first_name_input_exists(self, checkout_step_one):
        """First name input field should exist."""
        page = CheckoutStepOnePage(checkout_step_one)

        assert page.is_element_present(page.FIRST_NAME_INPUT, timeout=3)

    def test_last_name_input_exists(self, checkout_step_one):
        """Last name input field should exist."""
        page = CheckoutStepOnePage(checkout_step_one)

        assert page.is_element_present(page.LAST_NAME_INPUT, timeout=3)

    def test_zip_code_input_exists(self, checkout_step_one):
        """Zip code input field should exist."""
        page = CheckoutStepOnePage(checkout_step_one)

        assert page.is_element_present(page.ZIP_CODE_INPUT, timeout=3)

    def test_continue_button_exists(self, checkout_step_one):
        """Continue button should exist."""
        page = CheckoutStepOnePage(checkout_step_one)

        assert page.is_element_present(page.CONTINUE_BUTTON, timeout=3)

    def test_cancel_button_exists(self, checkout_step_one):
        """Cancel button should exist."""
        page = CheckoutStepOnePage(checkout_step_one)

        assert page.is_element_present(page.CANCEL_BUTTON, timeout=3)


class TestCheckoutStepOneInteractions:
    """Test CheckoutStepOnePage method interactions with browser."""

    def test_enter_first_name_types_text(self, checkout_step_one):
        """Entering first name should type text into field."""
        page = CheckoutStepOnePage(checkout_step_one)

        page.enter_first_name("John")

        first_name_field = checkout_step_one.find_element(*page.FIRST_NAME_INPUT)
        assert first_name_field.get_attribute("value") == "John"

    def test_enter_last_name_types_text(self, checkout_step_one):
        """Entering last name should type text into field."""
        page = CheckoutStepOnePage(checkout_step_one)

        page.enter_last_name("Doe")

        last_name_field = checkout_step_one.find_element(*page.LAST_NAME_INPUT)
        assert last_name_field.get_attribute("value") == "Doe"

    def test_enter_zip_code_types_text(self, checkout_step_one):
        """Entering zip code should type text into field."""
        page = CheckoutStepOnePage(checkout_step_one)

        page.enter_zip_code("12345")

        zip_field = checkout_step_one.find_element(*page.ZIP_CODE_INPUT)
        assert zip_field.get_attribute("value") == "12345"

    def test_continue_with_valid_info_navigates_to_step_two(self, checkout_step_one):
        """Continue with valid info should navigate to step two."""
        page = CheckoutStepOnePage(checkout_step_one)

        page.enter_first_name("John")
        page.enter_last_name("Doe")
        page.enter_zip_code("12345")
        page.click_continue()

        assert "/checkout-step-two.html" in checkout_step_one.current_url

    def test_cancel_returns_to_cart(self, checkout_step_one):
        """Cancel button should return to cart page."""
        page = CheckoutStepOnePage(checkout_step_one)

        page.click_cancel()

        assert "/cart.html" in checkout_step_one.current_url


class TestCheckoutStepOneValidation:
    """Test checkout form validation."""

    def test_continue_without_first_name_shows_error(self, checkout_step_one):
        """Continue without first name should show error."""
        page = CheckoutStepOnePage(checkout_step_one)

        page.enter_last_name("Doe")
        page.enter_zip_code("12345")
        page.click_continue()

        assert page.is_error_displayed()
        assert "First Name is required" in page.get_error_message()

    def test_continue_without_last_name_shows_error(self, checkout_step_one):
        """Continue without last name should show error."""
        page = CheckoutStepOnePage(checkout_step_one)

        page.enter_first_name("John")
        page.enter_zip_code("12345")
        page.click_continue()

        assert page.is_error_displayed()
        assert "Last Name is required" in page.get_error_message()

    def test_continue_without_zip_code_shows_error(self, checkout_step_one):
        """Continue without zip code should show error."""
        page = CheckoutStepOnePage(checkout_step_one)

        page.enter_first_name("John")
        page.enter_last_name("Doe")
        page.click_continue()

        assert page.is_error_displayed()
        assert "Postal Code is required" in page.get_error_message()

    def test_no_error_initially(self, checkout_step_one):
        """Error should not be displayed initially."""
        page = CheckoutStepOnePage(checkout_step_one)

        assert not page.is_error_displayed()
