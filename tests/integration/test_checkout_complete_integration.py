"""Integration tests for CheckoutCompletePage reads with a real browser.

Cover the confirmation reads against the DOM (#170); the Back Home
navigation is covered by test_navigation_integration.py.
"""

from pages.checkout_complete_page import CheckoutCompletePage
from pages.checkout_step_two_page import CheckoutStepTwoPage


def test_confirmation_page_shows_the_thank_you_message(checkout_step_two):
    """After Finish, the page is the confirmation and reads its header."""
    CheckoutStepTwoPage(checkout_step_two).click_finish()
    page = CheckoutCompletePage(checkout_step_two)

    assert page.is_on_confirmation_page()
    assert page.get_confirmation_message() == "Thank you for your order!"


def test_is_on_confirmation_page_is_false_before_finishing(checkout_step_two):
    """On the overview, before Finish, the confirmation container is absent."""
    page = CheckoutCompletePage(checkout_step_two)

    assert page.is_on_confirmation_page() is False
