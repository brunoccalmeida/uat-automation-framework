"""Unit tests for CheckoutStepTwoPage class.

Only what a real browser cannot check deterministically: logic (name
matching, reading amounts out of their labels) and the wait contracts of
finishing and cancelling. Locators and plain delegation to BasePage are
covered against the DOM by tests/integration/test_checkout_step_two_integration.py
(#143).
"""

from unittest.mock import Mock, patch

from pages.checkout_step_two_page import CheckoutStepTwoPage
from tests.helpers.navigation_contract import assert_clicks_then_returns_loaded


class TestIsProductInSummary:
    """Test is_product_in_summary method."""

    def test_is_product_in_summary_returns_true_when_product_found(self):
        """is_product_in_summary should return True when product in summary."""
        mock_driver = Mock()
        mock_item = Mock()
        mock_item.text = "Sauce Labs Backpack"
        mock_driver.find_elements.return_value = [mock_item]

        page = CheckoutStepTwoPage(mock_driver)
        result = page.is_product_in_summary("Sauce Labs Backpack")

        assert result is True

    def test_is_product_in_summary_returns_false_when_product_not_found(self):
        """is_product_in_summary should return False when product not in summary."""
        mock_driver = Mock()
        mock_item = Mock()
        mock_item.text = "Other Product"
        mock_driver.find_elements.return_value = [mock_item]

        page = CheckoutStepTwoPage(mock_driver)
        result = page.is_product_in_summary("Sauce Labs Backpack")

        assert result is False


class TestGetItemTotal:
    """Test get_item_total method."""

    def test_get_item_total_extracts_value_from_text(self):
        """get_item_total should extract and return float value from subtotal text."""
        mock_driver = Mock()
        page = CheckoutStepTwoPage(mock_driver)

        with patch.object(page, "get_text", return_value="Item total: $29.99"):
            result = page.get_item_total()

            assert result == 29.99


class TestGetTax:
    """Test get_tax method."""

    def test_get_tax_extracts_value_from_text(self):
        """get_tax should extract and return float value from tax text."""
        mock_driver = Mock()
        page = CheckoutStepTwoPage(mock_driver)

        with patch.object(page, "get_text", return_value="Tax: $2.40"):
            result = page.get_tax()

            assert result == 2.40


class TestGetTotal:
    """Test get_total method."""

    def test_get_total_extracts_value_from_text(self):
        """get_total should extract and return float value from total text."""
        mock_driver = Mock()
        page = CheckoutStepTwoPage(mock_driver)

        with patch.object(page, "get_text", return_value="Total: $32.39"):
            result = page.get_total()

            assert result == 32.39


class TestClickFinish:
    """Test click_finish method."""

    def test_click_finish_clicks_and_returns_loaded_checkout_complete_page(self):
        """click_finish clicks the button, returns a loaded CheckoutCompletePage."""
        page = CheckoutStepTwoPage(Mock())

        assert_clicks_then_returns_loaded(
            page,
            page.click_finish,
            CheckoutStepTwoPage.FINISH_BUTTON,
            "pages.checkout_complete_page.CheckoutCompletePage",
        )


class TestClickCancel:
    """Test click_cancel method."""

    def test_click_cancel_clicks_and_returns_loaded_inventory_page(self):
        """click_cancel should click CANCEL_BUTTON and return loaded InventoryPage."""
        page = CheckoutStepTwoPage(Mock())

        assert_clicks_then_returns_loaded(
            page,
            page.click_cancel,
            CheckoutStepTwoPage.CANCEL_BUTTON,
            "pages.inventory_page.InventoryPage",
        )


class TestTryFinish:
    """Test try_finish method."""

    def test_try_finish_clicks_without_waiting_for_the_confirmation(self):
        """try_finish should click FINISH_BUTTON and not wait for the next page."""
        page = CheckoutStepTwoPage(Mock())

        with (
            patch.object(page, "click") as mock_click,
            patch("pages.checkout_complete_page.CheckoutCompletePage") as mock_complete,
        ):
            page.try_finish()

        mock_click.assert_called_once_with(CheckoutStepTwoPage.FINISH_BUTTON)
        mock_complete.assert_not_called()
