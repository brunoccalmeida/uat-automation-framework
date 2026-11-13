"""Unit tests for CartPage class.

Only what a real browser cannot check deterministically: logic (name
matching, building the button ID) and the navigation wait contract.
Locators and plain delegation to BasePage are covered against the DOM by
tests/integration/test_cart_page_integration.py (#143).
"""

from unittest.mock import Mock, patch

from selenium.webdriver.common.by import By

from pages.cart_page import CartPage
from tests.helpers.navigation_contract import assert_clicks_then_returns_loaded


class TestIsProductInCart:
    """Test is_product_in_cart method."""

    def test_is_product_in_cart_returns_true_when_product_found(self):
        """is_product_in_cart should return True when product name matches."""
        mock_driver = Mock()
        mock_item = Mock()
        mock_item.text = "Sauce Labs Backpack"
        mock_driver.find_elements.return_value = [mock_item]

        page = CartPage(mock_driver)
        result = page.is_product_in_cart("Sauce Labs Backpack")

        assert result is True

    def test_is_product_in_cart_returns_false_when_product_not_found(self):
        """is_product_in_cart should return False when product not in cart."""
        mock_driver = Mock()
        mock_item = Mock()
        mock_item.text = "Sauce Labs Backpack"
        mock_driver.find_elements.return_value = [mock_item]

        page = CartPage(mock_driver)
        result = page.is_product_in_cart("Different Product")

        assert result is False


class TestRemoveProduct:
    """Test remove_product method."""

    def test_remove_product_converts_name_to_button_id(self):
        """remove_product should convert product name to button ID format."""
        mock_driver = Mock()
        page = CartPage(mock_driver)

        with patch.object(page, "click") as mock_click:
            page.remove_product("Sauce Labs Backpack")

            expected_locator = (By.ID, "remove-sauce-labs-backpack")
            mock_click.assert_called_once_with(expected_locator)


class TestClickContinueShopping:
    """Test click_continue_shopping method."""

    def test_click_continue_shopping_clicks_and_returns_loaded_inventory_page(self):
        """click_continue_shopping clicks the button, returns a loaded InventoryPage."""
        page = CartPage(Mock())

        assert_clicks_then_returns_loaded(
            page,
            page.click_continue_shopping,
            CartPage.CONTINUE_SHOPPING_BUTTON,
            "pages.inventory_page.InventoryPage",
        )


class TestClickCheckout:
    """Test click_checkout method."""

    def test_click_checkout_clicks_and_returns_loaded_checkout_step_one_page(self):
        """click_checkout clicks the button, returns a loaded CheckoutStepOnePage."""
        page = CartPage(Mock())

        assert_clicks_then_returns_loaded(
            page,
            page.click_checkout,
            CartPage.CHECKOUT_BUTTON,
            "pages.checkout_step_one_page.CheckoutStepOnePage",
        )
