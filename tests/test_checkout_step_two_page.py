"""Unit tests for CheckoutStepTwoPage class.

Tests the CheckoutStepTwoPage Page Object in isolation using mocks.
"""

from unittest.mock import Mock, patch

from selenium.webdriver.common.by import By

from pages.checkout_step_two_page import CheckoutStepTwoPage


class TestCheckoutStepTwoPageLocators:
    """Test CheckoutStepTwoPage locator definitions."""

    def test_checkout_summary_container_locator(self):
        """CHECKOUT_SUMMARY_CONTAINER locator should use correct ID."""
        assert CheckoutStepTwoPage.CHECKOUT_SUMMARY_CONTAINER == (
            By.ID,
            "checkout_summary_container",
        )

    def test_subtotal_label_locator(self):
        """SUBTOTAL_LABEL locator should use correct class name."""
        assert CheckoutStepTwoPage.SUBTOTAL_LABEL == (
            By.CLASS_NAME,
            "summary_subtotal_label",
        )

    def test_tax_label_locator(self):
        """TAX_LABEL locator should use correct class name."""
        assert CheckoutStepTwoPage.TAX_LABEL == (By.CLASS_NAME, "summary_tax_label")

    def test_total_label_locator(self):
        """TOTAL_LABEL locator should use correct class name."""
        assert CheckoutStepTwoPage.TOTAL_LABEL == (By.CLASS_NAME, "summary_total_label")

    def test_finish_button_locator(self):
        """FINISH_BUTTON locator should use correct ID."""
        assert CheckoutStepTwoPage.FINISH_BUTTON == (By.ID, "finish")


class TestIsOnCheckoutOverviewPage:
    """Test is_on_checkout_overview_page method."""

    def test_is_on_checkout_overview_page_returns_true_when_container_present(self):
        """is_on_checkout_overview_page should return True when summary container exists."""
        mock_driver = Mock()
        page = CheckoutStepTwoPage(mock_driver)

        with patch.object(
            page, "is_element_present", return_value=True
        ) as mock_is_present:
            result = page.is_on_checkout_overview_page()

            mock_is_present.assert_called_once_with(
                CheckoutStepTwoPage.CHECKOUT_SUMMARY_CONTAINER, timeout=3
            )
            assert result is True


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


class TestIsPaymentInfoDisplayed:
    """Test is_payment_info_displayed method."""

    def test_is_payment_info_displayed_returns_true_when_present(self):
        """is_payment_info_displayed should return True when payment info exists."""
        mock_driver = Mock()
        page = CheckoutStepTwoPage(mock_driver)

        with patch.object(page, "is_element_present", return_value=True):
            result = page.is_payment_info_displayed()

            assert result is True


class TestIsShippingInfoDisplayed:
    """Test is_shipping_info_displayed method."""

    def test_is_shipping_info_displayed_returns_true_when_present(self):
        """is_shipping_info_displayed should return True when shipping info exists."""
        mock_driver = Mock()
        page = CheckoutStepTwoPage(mock_driver)

        with patch.object(page, "is_element_present", return_value=True):
            result = page.is_shipping_info_displayed()

            assert result is True


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

    def test_click_finish_calls_click(self):
        """click_finish should call click with FINISH_BUTTON locator."""
        mock_driver = Mock()
        page = CheckoutStepTwoPage(mock_driver)

        with patch.object(page, "click") as mock_click:
            page.click_finish()

            mock_click.assert_called_once_with(CheckoutStepTwoPage.FINISH_BUTTON)


class TestClickCancel:
    """Test click_cancel method."""

    def test_click_cancel_calls_click(self):
        """click_cancel should call click with CANCEL_BUTTON locator."""
        mock_driver = Mock()
        page = CheckoutStepTwoPage(mock_driver)

        with patch.object(page, "click") as mock_click:
            page.click_cancel()

            mock_click.assert_called_once_with(CheckoutStepTwoPage.CANCEL_BUTTON)
