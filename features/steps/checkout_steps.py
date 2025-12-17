"""Checkout feature step definitions.

Implements BDD steps for checkout process scenarios.
"""

from behave import given, when, then

from pages.cart_page import CartPage
from pages.checkout_step_one_page import CheckoutStepOnePage
from pages.checkout_step_two_page import CheckoutStepTwoPage
from pages.checkout_complete_page import CheckoutCompletePage
from pages.inventory_page import InventoryPage


@when("I click the checkout button")
def step_click_checkout(context):
    """Click checkout button from cart page."""
    cart_page = CartPage(context.driver)
    cart_page.click_checkout()
    page = CheckoutStepOnePage(context.driver)
    # Ensure page is ready
    assert page.is_on_checkout_form(), "Should be on checkout form page"


@when("I fill in the checkout information:")
def step_fill_checkout_info(context):
    """Fill in checkout form with provided information."""
    page = CheckoutStepOnePage(context.driver)
    for row in context.table:
        field = row["field"]
        value = row["value"]

        if field == "First Name":
            page.enter_first_name(value)
        elif field == "Last Name":
            page.enter_last_name(value)
        elif field == "Zip Code":
            page.enter_zip_code(value)


@when("I click continue")
def step_click_continue(context):
    """Click continue button on checkout step one."""
    page = CheckoutStepOnePage(context.driver)
    page.click_continue()


@when("I click cancel")
def step_click_cancel(context):
    """Click cancel button."""
    page = CheckoutStepOnePage(context.driver)
    page.click_cancel()


@when("I click finish")
def step_click_finish(context):
    """Click finish button on checkout overview."""
    page = CheckoutStepTwoPage(context.driver)
    page.click_finish()


@when("I click back home")
def step_click_back_home(context):
    """Click back home button on confirmation page."""
    page = CheckoutCompletePage(context.driver)
    page.click_back_home()


@then("I should be on the checkout overview page")
def step_verify_on_overview_page(context):
    """Verify user is on checkout overview page."""
    page = CheckoutStepTwoPage(context.driver)
    assert page.is_on_checkout_overview_page(), "Should be on checkout overview page"


@then('I should see "{product_name}" in the order summary')
def step_verify_product_in_summary(context, product_name):
    """Verify product appears in order summary."""
    page = CheckoutStepTwoPage(context.driver)
    assert page.is_product_in_summary(
        product_name
    ), f"Product '{product_name}' should be in order summary"


@then("I should see the payment information")
def step_verify_payment_info(context):
    """Verify payment information is displayed."""
    page = CheckoutStepTwoPage(context.driver)
    assert page.is_payment_info_displayed(), "Payment information should be displayed"


@then("I should see the shipping information")
def step_verify_shipping_info(context):
    """Verify shipping information is displayed."""
    page = CheckoutStepTwoPage(context.driver)
    assert page.is_shipping_info_displayed(), "Shipping information should be displayed"


@then("I should see the order confirmation")
def step_verify_order_confirmation(context):
    """Verify order confirmation page is displayed."""
    page = CheckoutCompletePage(context.driver)
    assert page.is_on_confirmation_page(), "Should be on order confirmation page"


@then('the confirmation message should say "{expected_message}"')
def step_verify_confirmation_message(context, expected_message):
    """Verify confirmation message matches expected text."""
    page = CheckoutCompletePage(context.driver)
    actual_message = page.get_confirmation_message()
    assert (
        expected_message in actual_message
    ), f"Expected '{expected_message}' in confirmation, got '{actual_message}'"


@then("the item total should be displayed")
def step_verify_item_total(context):
    """Verify item total is displayed."""
    page = CheckoutStepTwoPage(context.driver)
    item_total = page.get_item_total()
    assert item_total is not None, "Item total should be displayed"
    assert item_total > 0, "Item total should be greater than 0"


@then("the tax should be displayed")
def step_verify_tax(context):
    """Verify tax is displayed."""
    page = CheckoutStepTwoPage(context.driver)
    tax = page.get_tax()
    assert tax is not None, "Tax should be displayed"
    assert tax >= 0, "Tax should be greater than or equal to 0"


@then("the total should be displayed")
def step_verify_total(context):
    """Verify total is displayed."""
    page = CheckoutStepTwoPage(context.driver)
    total = page.get_total()
    assert total is not None, "Total should be displayed"
    assert total > 0, "Total should be greater than 0"


@then('the checkout error should mention "{expected_text}"')
def step_verify_checkout_error_text(context, expected_text):
    """Verify checkout error message contains expected text."""
    page = CheckoutStepOnePage(context.driver)
    error_message = page.get_error_message()
    assert (
        expected_text in error_message
    ), f"Expected '{expected_text}' in error, got '{error_message}'"
