"""Step definitions for user journey scenarios."""

from behave import when, then

from pages.cart_page import CartPage
from pages.checkout_complete_page import CheckoutCompletePage
from pages.checkout_step_one_page import CheckoutStepOnePage
from pages.checkout_step_two_page import CheckoutStepTwoPage
from pages.inventory_page import InventoryPage


@when("I sort products by price low to high")
def step_sort_by_price_low_to_high(context):
    """Sort products by price from low to high.

    Args:
        context: Behave context.
    """
    page = InventoryPage(context.driver)
    page.select_sort_option("lohi")


@when("I sort products by price high to low")
def step_sort_by_price_high_to_low(context):
    """Sort products by price from high to low.

    Args:
        context: Behave context.
    """
    page = InventoryPage(context.driver)
    page.select_sort_option("hilo")


@when("I add the first product to cart")
def step_add_first_product_to_cart(context):
    """Add the first displayed product to cart.

    Args:
        context: Behave context.
    """
    page = InventoryPage(context.driver)
    product_names = page.get_product_names()
    if product_names:
        context.first_product = product_names[0]
        page.add_product_to_cart(context.first_product)


@when("I click the shopping cart")
def step_click_shopping_cart(context):
    """Click the shopping cart icon.

    Args:
        context: Behave context.
    """
    page = InventoryPage(context.driver)
    page.click_shopping_cart()


@when("I proceed to checkout")
def step_proceed_to_checkout(context):
    """Click checkout button to proceed.

    Args:
        context: Behave context.
    """
    page = CartPage(context.driver)
    page.click_checkout()


@then("I should be on the checkout information page")
def step_verify_on_checkout_info_page(context):
    """Verify user is on checkout information page.

    Args:
        context: Behave context.
    """
    page = CheckoutStepOnePage(context.driver)
    assert page.is_on_checkout_form(), "Should be on checkout information page"


@when("I enter checkout information:")
def step_enter_checkout_information(context):
    """Enter checkout information from table.

    Args:
        context: Behave context with table data.
    """
    page = CheckoutStepOnePage(context.driver)
    for row in context.table:
        field = row["field"]
        value = row["value"]
        if field == "first_name":
            page.enter_first_name(value)
        elif field == "last_name":
            page.enter_last_name(value)
        elif field == "zip_code":
            page.enter_zip_code(value)


@when("I click continue to review order")
def step_click_continue_to_review(context):
    """Click continue button to review order.

    Args:
        context: Behave context.
    """
    page = CheckoutStepOnePage(context.driver)
    page.click_continue()


@when("I click finish to complete order")
def step_click_finish_to_complete_order(context):
    """Click finish button to complete order.

    Args:
        context: Behave context.
    """
    page = CheckoutStepTwoPage(context.driver)
    page.click_finish()


@then('the confirmation message should be "{expected_message}"')
def step_verify_confirmation_message(context, expected_message):
    """Verify confirmation message text.

    Args:
        context: Behave context.
        expected_message: Expected confirmation message.
    """
    page = CheckoutCompletePage(context.driver)
    actual_message = page.get_confirmation_message()
    assert (
        expected_message.lower() in actual_message.lower()
    ), f"Expected message '{expected_message}' not found in '{actual_message}'"


@when("I click back to products")
def step_click_back_to_products(context):
    """Click back to products button.

    Args:
        context: Behave context.
    """
    page = CheckoutCompletePage(context.driver)
    page.click_back_home()
