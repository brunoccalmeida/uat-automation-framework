from pages.inventory_page import InventoryPage


@when("I refresh the page")
def step_refresh_page(context):
    """Refresh the current browser page and espera inventory carregar."""
    context.driver.refresh()
    page = InventoryPage(context.driver)
    assert page.is_on_inventory_page(), "Inventory page did not load after refresh"


from behave import given, then, when


@then('the sort dropdown should NOT show "{option}" as selected')
def step_verify_sort_dropdown_not_selected(context, option):
    """Verify sort dropdown does NOT show the given option as selected (for bug scenarios).

    Args:
        context: Behave context.
        option: Option value that should NOT be selected.
    """
    page = InventoryPage(context.driver)
    current_option = page.get_current_sort_option()
    assert (
        current_option != option
    ), f"Sort dropdown unexpectedly shows '{option}' as selected (actual: '{current_option}')"


@then("products should NOT be sorted by name Z to A")
def step_verify_sort_name_za_not_sorted(context):
    """Verify products are NOT sorted by name Z to A (for problem_user bug scenario).

    Args:
        context: Behave context.
    """
    page = InventoryPage(context.driver)
    product_names = page.get_product_names()
    sorted_names = sorted(product_names, reverse=True)
    assert (
        product_names != sorted_names
    ), f"Products are (unexpectedly) sorted Z-A: {product_names}"


from pages.cart_page import CartPage


from behave import given, then, when

from pages.inventory_page import InventoryPage


@when('I select sort option "{option}"')
@then('I select sort option "{option}"')
def step_select_sort_option(context, option):
    """Select sort option from dropdown.

    Args:
        context: Behave context.
        option: Sort option value (az, za, lohi, hilo).
    """
    page = InventoryPage(context.driver)
    page.select_sort_option(option)


@then("products should be sorted by name A to Z")
def step_verify_sort_name_az(context):
    """Verify products are sorted by name A to Z.

    Args:
        context: Behave context.
    """
    page = InventoryPage(context.driver)
    product_names = page.get_product_names()

    # Verify names are in alphabetical order
    sorted_names = sorted(product_names)
    assert product_names == sorted_names, f"Products not sorted A-Z: {product_names}"


@then("products should be sorted by name Z to A")
def step_verify_sort_name_za(context):
    """Verify products are sorted by name Z to A.

    Args:
        context: Behave context.
    """
    page = InventoryPage(context.driver)
    product_names = page.get_product_names()

    # Verify names are in reverse alphabetical order
    sorted_names = sorted(product_names, reverse=True)
    assert product_names == sorted_names, f"Products not sorted Z-A: {product_names}"


@then("products should be sorted by price low to high")
def step_verify_sort_price_lohi(context):
    """Verify products are sorted by price low to high.

    Args:
        context: Behave context.
    """
    page = InventoryPage(context.driver)
    product_prices = page.get_product_prices()

    # Verify prices are in ascending order
    sorted_prices = sorted(product_prices)
    assert (
        product_prices == sorted_prices
    ), f"Products not sorted low-high: {product_prices}"


@then("products should be sorted by price high to low")
def step_verify_sort_price_hilo(context):
    """Verify products are sorted by price high to low.

    Args:
        context: Behave context.
    """
    page = InventoryPage(context.driver)
    product_prices = page.get_product_prices()

    # Verify prices are in descending order
    sorted_prices = sorted(product_prices, reverse=True)
    assert (
        product_prices == sorted_prices
    ), f"Products not sorted high-low: {product_prices}"


@then('the sort dropdown should show "{option}" as selected')
def step_verify_sort_dropdown_selected(context, option):
    """Verify sort dropdown shows expected option as selected.

    Args:
        context: Behave context.
        option: Expected selected option value.
    """
    page = InventoryPage(context.driver)
    current_option = page.get_current_sort_option()
    assert (
        current_option == option
    ), f"Sort dropdown shows '{current_option}' but expected '{option}'"


@then("I should see {count:d} products on the page")
def step_verify_product_count(context, count):
    """Verify number of products displayed.

    Args:
        context: Behave context.
        count: Expected number of products.
    """
    page = InventoryPage(context.driver)
    actual_count = page.get_product_count()
    assert actual_count == count, f"Expected {count} products but found {actual_count}"
