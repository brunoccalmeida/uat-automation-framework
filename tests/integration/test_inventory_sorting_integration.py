import pytest
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


@pytest.fixture(scope="function")
def authenticated_driver(driver, base_url):
    driver.get(base_url)
    login_page = LoginPage(driver)
    login_page.login("standard_user", "secret_sauce")
    yield driver


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
