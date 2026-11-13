"""Unit tests for CheckoutStepOnePage class.

Only what a real browser cannot check deterministically: the wait contracts
of submitting the form and of navigating, and the fail-fast read of the Last
Name input. Locators and plain delegation to BasePage are covered against
the DOM by tests/integration/test_checkout_step_one_integration.py (#143).
"""

from unittest.mock import Mock, patch

import pytest

from pages.checkout_step_one_page import CheckoutStepOnePage
from pages.checkout_step_two_page import CheckoutStepTwoPage
from tests.helpers.navigation_contract import assert_clicks_then_returns_loaded


class TestClickContinue:
    """Test click_continue method."""

    def test_click_continue_submits_and_waits_for_outcome(self):
        """click_continue submits and waits for CheckoutStepTwoPage or an error."""
        page = CheckoutStepOnePage(Mock())

        with patch.object(page, "submit_and_wait_for_outcome") as mock_submit:
            page.click_continue()

            mock_submit.assert_called_once_with(
                CheckoutStepOnePage.CONTINUE_BUTTON, CheckoutStepTwoPage
            )


class TestClickCancel:
    """Test click_cancel method."""

    def test_click_cancel_clicks_and_returns_loaded_cart_page(self):
        """click_cancel should click CANCEL_BUTTON and return loaded CartPage."""
        page = CheckoutStepOnePage(Mock())

        assert_clicks_then_returns_loaded(
            page,
            page.click_cancel,
            CheckoutStepOnePage.CANCEL_BUTTON,
            "pages.cart_page.CartPage",
        )


class TestGetLastName:
    """Test get_last_name method."""

    def test_get_last_name_raises_when_the_input_has_no_value(self):
        """get_last_name should fail loudly, not return None, without a value."""
        page = CheckoutStepOnePage(Mock())

        with patch.object(page, "find_element") as mock_find:
            mock_find.return_value.get_attribute.return_value = None
            with pytest.raises(ValueError, match="no value attribute"):
                page.get_last_name()
