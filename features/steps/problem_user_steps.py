"""Step definitions for Problem User Journey feature."""

# behave replaces these decorator placeholders at import time; pylint only
# sees the placeholders, which are not callable.
# pylint: disable=not-callable

from behave import then

from pages.inventory_page import InventoryPage


@then("the product images should be broken")
def step_then_product_images_broken(context):
    """Verify product images are broken (src = /static/media/sl-404.168b1cce.jpg)."""
    page = InventoryPage(context.driver)
    broken = page.are_product_images_broken()
    assert broken, "Expected broken product images for problem_user"


@then("the product names should be visible")
def step_then_product_names_visible(context):
    """Valida que os nomes dos produtos estão visíveis."""
    page = InventoryPage(context.driver)
    names = page.get_product_names()
    assert names, "Os nomes dos produtos devem estar visíveis"
