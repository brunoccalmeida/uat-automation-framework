"""Unit tests for LoginPage class.

Only what a real browser cannot check deterministically: branch logic and
the wait contract of submitting the form. Locators and plain delegation to
BasePage are covered against the DOM by
tests/integration/test_login_page_integration.py (#143).
"""

from unittest.mock import Mock, patch

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


class TestClickLogin:
    """Test click_login method."""

    def test_click_login_submits_and_waits_for_outcome(self):
        """click_login submits and waits for InventoryPage or an error."""
        page = LoginPage(Mock())

        with patch.object(page, "submit_and_wait_for_outcome") as mock_submit:
            page.click_login()

            mock_submit.assert_called_once_with(LoginPage.LOGIN_BUTTON, InventoryPage)


class TestGetErrorMessage:
    """Test get_error_message method."""

    def test_get_error_message_returns_text_when_error_present(self):
        """get_error_message should return error text when error element exists."""
        mock_driver = Mock()
        page = LoginPage(mock_driver)

        expected_error = "Epic sadface: Username and password do not match"

        with patch.object(page, "is_element_visible", return_value=True):
            with patch.object(
                page, "get_text", return_value=expected_error
            ) as mock_get_text:
                result = page.get_error_message()

                mock_get_text.assert_called_once_with(LoginPage.ERROR_MESSAGE)
                assert result == expected_error

    def test_get_error_message_returns_none_when_error_not_present(self):
        """get_error_message should return None when error element doesn't exist."""
        mock_driver = Mock()
        page = LoginPage(mock_driver)

        with patch.object(page, "is_element_visible", return_value=False):
            with patch.object(page, "get_text") as mock_get_text:
                result = page.get_error_message()

                # Should not try to get text if element not present
                mock_get_text.assert_not_called()
                assert result is None
