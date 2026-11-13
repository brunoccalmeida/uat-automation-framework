"""Unit tests for CheckoutCompletePage class.

Tests the CheckoutCompletePage Page Object in isolation using mocks.
"""

from unittest.mock import Mock, patch

from selenium.webdriver.common.by import By

from pages.checkout_complete_page import CheckoutCompletePage
from tests.helpers.navigation_contract import assert_clicks_then_returns_loaded


class TestCheckoutCompletePageLocators:
    """Test CheckoutCompletePage locator definitions."""

    def test_checkout_complete_container_locator(self):
        """CHECKOUT_COMPLETE_CONTAINER locator should use correct ID."""
        assert CheckoutCompletePage.CHECKOUT_COMPLETE_CONTAINER == (
            By.ID,
            "checkout_complete_container",
        )

    def test_complete_header_locator(self):
        """COMPLETE_HEADER locator should use correct class name."""
        assert CheckoutCompletePage.COMPLETE_HEADER == (
            By.CLASS_NAME,
            "complete-header",
        )

    def test_back_home_button_locator(self):
        """BACK_HOME_BUTTON locator should use correct ID."""
        assert CheckoutCompletePage.BACK_HOME_BUTTON == (By.ID, "back-to-products")


class TestIsOnConfirmationPage:
    """Test is_on_confirmation_page method."""

    def test_is_on_confirmation_page_returns_true_when_container_present(self):
        """is_on_confirmation_page should return True when complete container exists."""
        mock_driver = Mock()
        page = CheckoutCompletePage(mock_driver)

        with patch.object(
            page, "is_element_visible", return_value=True
        ) as mock_is_present:
            result = page.is_on_confirmation_page()

            mock_is_present.assert_called_once_with(
                CheckoutCompletePage.CHECKOUT_COMPLETE_CONTAINER, timeout=3
            )
            assert result is True

    def test_is_on_confirmation_page_returns_false_when_container_not_present(self):
        """is_on_confirmation_page is False without the complete container."""
        mock_driver = Mock()
        page = CheckoutCompletePage(mock_driver)

        with patch.object(page, "is_element_visible", return_value=False):
            result = page.is_on_confirmation_page()

            assert result is False


class TestGetConfirmationMessage:
    """Test get_confirmation_message method."""

    def test_get_confirmation_message_returns_header_text(self):
        """get_confirmation_message should return confirmation header text."""
        mock_driver = Mock()
        page = CheckoutCompletePage(mock_driver)

        with patch.object(
            page, "get_text", return_value="Thank you for your order!"
        ) as mock_get_text:
            result = page.get_confirmation_message()

            mock_get_text.assert_called_once_with(CheckoutCompletePage.COMPLETE_HEADER)
            assert result == "Thank you for your order!"


class TestClickBackHome:
    """Test click_back_home method."""

    def test_click_back_home_clicks_and_returns_loaded_inventory_page(self):
        """click_back_home clicks the button, returns a loaded InventoryPage."""
        page = CheckoutCompletePage(Mock())

        assert_clicks_then_returns_loaded(
            page,
            page.click_back_home,
            CheckoutCompletePage.BACK_HOME_BUTTON,
            "pages.inventory_page.InventoryPage",
        )
