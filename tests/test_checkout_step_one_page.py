"""Unit tests for CheckoutStepOnePage class.

Tests the CheckoutStepOnePage Page Object in isolation using mocks.
"""

from unittest.mock import Mock, patch

from selenium.webdriver.common.by import By

from pages.checkout_step_one_page import CheckoutStepOnePage


class TestCheckoutStepOnePageLocators:
    """Test CheckoutStepOnePage locator definitions."""

    def test_checkout_info_container_locator(self):
        """CHECKOUT_INFO_CONTAINER locator should use correct class name."""
        assert CheckoutStepOnePage.CHECKOUT_INFO_CONTAINER == (
            By.CLASS_NAME,
            "checkout_info",
        )

    def test_first_name_input_locator(self):
        """FIRST_NAME_INPUT locator should use correct ID."""
        assert CheckoutStepOnePage.FIRST_NAME_INPUT == (By.ID, "first-name")

    def test_last_name_input_locator(self):
        """LAST_NAME_INPUT locator should use correct ID."""
        assert CheckoutStepOnePage.LAST_NAME_INPUT == (By.ID, "last-name")

    def test_zip_code_input_locator(self):
        """ZIP_CODE_INPUT locator should use correct ID."""
        assert CheckoutStepOnePage.ZIP_CODE_INPUT == (By.ID, "postal-code")

    def test_continue_button_locator(self):
        """CONTINUE_BUTTON locator should use correct ID."""
        assert CheckoutStepOnePage.CONTINUE_BUTTON == (By.ID, "continue")


class TestIsOnCheckoutForm:
    """Test is_on_checkout_form method."""

    def test_is_on_checkout_form_returns_true_when_container_present(self):
        """is_on_checkout_form should return True when checkout info container exists."""
        mock_driver = Mock()
        page = CheckoutStepOnePage(mock_driver)

        with patch.object(
            page, "is_element_present", return_value=True
        ) as mock_is_present:
            result = page.is_on_checkout_form()

            mock_is_present.assert_called_once_with(
                CheckoutStepOnePage.CHECKOUT_INFO_CONTAINER, timeout=5
            )
            assert result is True


class TestEnterFirstName:
    """Test enter_first_name method."""

    def test_enter_first_name_calls_type_with_first_name_locator(self):
        """enter_first_name should call type with FIRST_NAME_INPUT locator."""
        mock_driver = Mock()
        page = CheckoutStepOnePage(mock_driver)

        with patch.object(page, "type") as mock_type:
            page.enter_first_name("John")

            mock_type.assert_called_once_with(
                CheckoutStepOnePage.FIRST_NAME_INPUT, "John"
            )


class TestEnterLastName:
    """Test enter_last_name method."""

    def test_enter_last_name_calls_type_with_last_name_locator(self):
        """enter_last_name should call type with LAST_NAME_INPUT locator."""
        mock_driver = Mock()
        page = CheckoutStepOnePage(mock_driver)

        with patch.object(page, "type") as mock_type:
            page.enter_last_name("Doe")

            mock_type.assert_called_once_with(
                CheckoutStepOnePage.LAST_NAME_INPUT, "Doe"
            )


class TestEnterZipCode:
    """Test enter_zip_code method."""

    def test_enter_zip_code_calls_type_with_zip_code_locator(self):
        """enter_zip_code should call type with ZIP_CODE_INPUT locator."""
        mock_driver = Mock()
        page = CheckoutStepOnePage(mock_driver)

        with patch.object(page, "type") as mock_type:
            page.enter_zip_code("12345")

            mock_type.assert_called_once_with(
                CheckoutStepOnePage.ZIP_CODE_INPUT, "12345"
            )


class TestClickContinue:
    """Test click_continue method."""

    def test_click_continue_calls_click(self):
        """click_continue should call click with CONTINUE_BUTTON locator."""
        mock_driver = Mock()
        page = CheckoutStepOnePage(mock_driver)

        with patch.object(page, "click") as mock_click:
            page.click_continue()

            mock_click.assert_called_once_with(CheckoutStepOnePage.CONTINUE_BUTTON)


class TestClickCancel:
    """Test click_cancel method."""

    def test_click_cancel_calls_click(self):
        """click_cancel should call click with CANCEL_BUTTON locator."""
        mock_driver = Mock()
        page = CheckoutStepOnePage(mock_driver)

        with patch.object(page, "click") as mock_click:
            page.click_cancel()

            mock_click.assert_called_once_with(CheckoutStepOnePage.CANCEL_BUTTON)


class TestIsErrorDisplayed:
    """Test is_error_displayed method."""

    def test_is_error_displayed_returns_true_when_error_present(self):
        """is_error_displayed should return True when error message exists."""
        mock_driver = Mock()
        page = CheckoutStepOnePage(mock_driver)

        with patch.object(page, "is_element_present", return_value=True):
            result = page.is_error_displayed()

            assert result is True


class TestGetErrorMessage:
    """Test get_error_message method."""

    def test_get_error_message_returns_text(self):
        """get_error_message should return error message text."""
        mock_driver = Mock()
        page = CheckoutStepOnePage(mock_driver)

        with patch.object(
            page, "get_text", return_value="Error: First Name is required"
        ) as mock_get_text:
            result = page.get_error_message()

            mock_get_text.assert_called_once_with(CheckoutStepOnePage.ERROR_MESSAGE)
            assert result == "Error: First Name is required"
