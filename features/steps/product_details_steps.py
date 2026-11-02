"""Product Details feature step definitions.

Implements BDD steps for the product details page scenarios.
"""

# behave replaces these decorator placeholders at import time; pylint only
# sees the placeholders, which are not callable.
# pylint: disable=not-callable

from behave import given, then, when

from pages.inventory_page import InventoryPage
from pages.product_details_page import ProductDetailsPage


@given('I am on the details of "{product_name}"')
@when('I open the details of "{product_name}"')
def step_open_product_details(context, product_name):
    """Open product details from its card, keeping the card for comparison."""
    page = InventoryPage(context.driver)
    context.product_card = page.get_product_card(product_name)
    page.open_product_details(product_name)


@given("I have added the product to the cart from its details")
@when("I add the product to the cart from its details")
def step_add_from_details(context):
    """Add the displayed product to the cart."""
    ProductDetailsPage(context.driver).add_to_cart()


@when("I remove the product from the cart on its details")
def step_remove_on_details(context):
    """Remove the displayed product from the cart."""
    ProductDetailsPage(context.driver).remove_from_cart()


@when("I go back to the products page")
def step_back_to_products(context):
    """Return from product details to the products page."""
    ProductDetailsPage(context.driver).back_to_products()


@then("the details should match the product card")
def step_verify_details_match_card(context):
    """Verify name, description and price match the card that was opened."""
    details = ProductDetailsPage(context.driver).get_product_info()
    assert (
        details == context.product_card
    ), f"Details {details} should match card {context.product_card}"


@then('the details should show "{product_name}"')
def step_verify_details_name(context, product_name):
    """Verify the product shown on the details page."""
    actual = ProductDetailsPage(context.driver).get_name()
    assert actual == product_name, f"Details should show {product_name}, not {actual}"


@then("the details should have no description")
def step_verify_no_description(context):
    """Verify the details page shows no description."""
    page = ProductDetailsPage(context.driver)
    assert not page.has_description(), "Details should have no description"


@then('the details button should show "{button_text}"')
def step_verify_details_button(context, button_text):
    """Verify the cart button text on the details page."""
    actual = ProductDetailsPage(context.driver).get_cart_button_text()
    assert actual == button_text, f"Button should show {button_text}, not {actual}"
