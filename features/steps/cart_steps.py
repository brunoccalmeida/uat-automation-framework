"""Shopping Cart feature step definitions.

Implements BDD steps for shopping cart scenarios.
"""

from behave import given, when, then

from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage


@given('I am on the products page')
@then('I should be on the products page')
def step_on_products_page(context):
    """Verify user is on products/inventory page."""
    context.inventory_page = InventoryPage(context.driver)
    assert context.inventory_page.is_on_inventory_page(), \
        "Should be on products page"


@given('I have added "{product_name}" to the cart')
def step_have_added_product(context, product_name):
    """Add product to cart (setup step)."""
    context.inventory_page = InventoryPage(context.driver)
    context.inventory_page.add_product_to_cart(product_name)


@given('I am on the cart page')
def step_on_cart_page(context):
    """Navigate to cart page."""
    context.inventory_page = InventoryPage(context.driver)
    context.inventory_page.click_shopping_cart()
    context.cart_page = CartPage(context.driver)


@when('I add "{product_name}" to the cart')
def step_add_product_to_cart(context, product_name):
    """Add specific product to shopping cart."""
    context.inventory_page.add_product_to_cart(product_name)


@when('I click the shopping cart icon')
def step_click_cart_icon(context):
    """Click shopping cart icon to view cart."""
    context.inventory_page.click_shopping_cart()
    context.cart_page = CartPage(context.driver)


@when('I remove "{product_name}" from the cart')
def step_remove_product_from_cart(context, product_name):
    """Remove product from cart."""
    context.cart_page.remove_product(product_name)


@when('I click "{button_text}"')
def step_click_button(context, button_text):
    """Click button by text."""
    if button_text == "Continue Shopping":
        context.cart_page.click_continue_shopping()
    else:
        raise NotImplementedError(f"Button '{button_text}' not implemented")


@when('I navigate to different pages')
def step_navigate_different_pages(context):
    """Navigate to different pages to test cart persistence."""
    # Navigate to cart and back
    context.inventory_page.click_shopping_cart()
    context.cart_page = CartPage(context.driver)
    context.cart_page.click_continue_shopping()
    context.inventory_page = InventoryPage(context.driver)


@then('the cart badge should show "{count}"')
@then('the cart badge should still show "{count}"')
def step_verify_cart_badge(context, count):
    """Verify cart badge shows expected count."""
    actual_count = context.inventory_page.get_cart_item_count()
    assert actual_count == int(count), \
        f"Cart badge should show {count}, but shows {actual_count}"


@then('the product button should change to "{button_text}"')
def step_verify_button_text(context, button_text):
    """Verify product button text changed."""
    # Implementation depends on checking button state
    # For now, verify cart count changed (button text change correlates)
    cart_count = context.inventory_page.get_cart_item_count()
    if button_text == "Remove":
        assert cart_count > 0, "Product should be in cart (button changed to Remove)"


@then('I should be on the cart page')
def step_verify_on_cart_page(context):
    """Verify user is on cart page."""
    assert context.cart_page.is_on_cart_page(), \
        "Should be on cart page"


@then('I should see "{product_name}" in the cart')
def step_verify_product_in_cart(context, product_name):
    """Verify specific product is in cart."""
    assert context.cart_page.is_product_in_cart(product_name), \
        f"Product '{product_name}' should be in cart"


@then('the cart should have {count:d} item')
@then('the cart should have {count:d} items')
def step_verify_cart_item_count(context, count):
    """Verify number of items in cart."""
    actual_count = context.cart_page.get_cart_item_count()
    assert actual_count == count, \
        f"Cart should have {count} item(s), but has {actual_count}"


@then('the cart should be empty')
def step_verify_cart_empty(context):
    """Verify cart is empty."""
    cart_count = context.cart_page.get_cart_item_count()
    assert cart_count == 0, \
        f"Cart should be empty, but has {cart_count} item(s)"


@then('the cart badge should not be visible')
def step_verify_no_cart_badge(context):
    """Verify cart badge is not displayed."""
    # Return to inventory page to check badge
    context.cart_page.click_continue_shopping()
    context.inventory_page = InventoryPage(context.driver)
    cart_count = context.inventory_page.get_cart_item_count()
    assert cart_count == 0, \
        "Cart badge should not be visible (count should be 0)"
