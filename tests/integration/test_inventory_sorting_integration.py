"""Integration tests for InventoryPage sorting with a real browser."""

from pages.inventory_page import InventoryPage


def test_sorting_orders_products_correctly(authenticated_driver):
    page = InventoryPage(authenticated_driver)

    # A-Z (default)
    names_az = page.get_product_names()
    assert names_az == sorted(names_az), f"A-Z sorting failed: {names_az}"

    # Z-A
    page.select_sort_option("za")
    names_za = page.get_product_names()
    assert names_za == sorted(names_za, reverse=True), f"Z-A sorting failed: {names_za}"

    # Price low-high
    page.select_sort_option("lohi")
    prices_lohi = page.get_product_prices()
    assert prices_lohi == sorted(prices_lohi), f"Low-High sorting failed: {prices_lohi}"

    # Price high-low
    page.select_sort_option("hilo")
    prices_hilo = page.get_product_prices()
    assert prices_hilo == sorted(
        prices_hilo, reverse=True
    ), f"High-Low sorting failed: {prices_hilo}"


def test_sort_dropdown_lists_the_four_options(authenticated_driver):
    page = InventoryPage(authenticated_driver)

    assert page.get_sort_dropdown_options() == [
        "Name (A to Z)",
        "Name (Z to A)",
        "Price (low to high)",
        "Price (high to low)",
    ]


def test_current_sort_option_reads_the_selected_value(authenticated_driver):
    page = InventoryPage(authenticated_driver)
    assert page.get_current_sort_option() == "az"

    page.select_sort_option("hilo")

    assert page.get_current_sort_option() == "hilo"
