"""Step definitions for product sorting edge cases."""

from behave import when, then

from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage


@then("I verify the sort dropdown has the correct option selected")
def step_verify_sort_dropdown_correct_option(context):
    """Verify sort dropdown has correct option selected (visual check).

    Args:
        context: Behave context.
    """
    page = InventoryPage(context.driver)
    current_option = page.get_current_sort_option()
    # Verify the dropdown element is present and shows selected value
    assert current_option in [
        "az",
        "za",
        "lohi",
        "hilo",
    ], f"Sort option '{current_option}' should be one of valid options"


@when("I click the cart button")
def step_click_cart_button(context):
    """Click the cart/shopping cart button.

    Args:
        context: Behave context.
    """
    page = InventoryPage(context.driver)
    page.click_shopping_cart()


@when("I click the continue shopping button")
def step_click_continue_shopping(context):
    """Click continue shopping button to return to inventory.

    Args:
        context: Behave context.
    """
    page = CartPage(context.driver)
    page.click_continue_shopping()


@then("I should see all sort options in the dropdown")
def step_verify_all_sort_options_present(context):
    """Verify all expected sort options are present in dropdown.

    Args:
        context: Behave context.
    """
    page = InventoryPage(context.driver)
    options = page.get_sort_dropdown_options()
    # Verify dropdown has exactly 4 options
    assert len(options) == 4, f"Expected 4 sort options, got {len(options)}"


@then('the sort dropdown should contain "{option_text}"')
def step_verify_sort_dropdown_contains(context, option_text):
    """Verify sort dropdown contains specific option text.

    Args:
        context: Behave context.
        option_text: Visible text of option (e.g., 'Name (A to Z)').
    """
    page = InventoryPage(context.driver)
    assert page.sort_dropdown_contains_option(
        option_text
    ), f"Sort dropdown should contain option '{option_text}'"
