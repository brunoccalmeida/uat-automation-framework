"""Navigation helpers that open a page for an integration test.

Each helper starts at the login page and returns once the destination page
has rendered (the page objects' navigation methods wait for it). Fixtures in
conftest.py use them; tests that need another product mix call them directly.
"""

from pages.cart_page import CartPage
from pages.checkout_step_one_page import CheckoutStepOnePage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

DEFAULT_PRODUCTS = ("Sauce Labs Backpack",)


def go_to_inventory(driver, base_url):
    """Log in as standard_user and land on the inventory page."""
    driver.get(base_url)
    LoginPage(driver).login("standard_user", "secret_sauce")


def go_to_cart(driver, base_url, products=DEFAULT_PRODUCTS):
    """Log in, add the products and open the cart."""
    go_to_inventory(driver, base_url)
    inventory_page = InventoryPage(driver)
    for product in products:
        inventory_page.add_product_to_cart(product)
    inventory_page.click_shopping_cart()


def go_to_step_one(driver, base_url, products=DEFAULT_PRODUCTS):
    """Open checkout step one with the products in the cart."""
    go_to_cart(driver, base_url, products)
    CartPage(driver).click_checkout()


def fill_customer_info(driver):
    """Fill checkout step one with valid customer info, without submitting."""
    step_one_page = CheckoutStepOnePage(driver)
    step_one_page.enter_first_name("John")
    step_one_page.enter_last_name("Doe")
    step_one_page.enter_zip_code("12345")


def go_to_step_two(driver, base_url, products=DEFAULT_PRODUCTS):
    """Open checkout step two (overview) with valid customer info."""
    go_to_step_one(driver, base_url, products)
    fill_customer_info(driver)
    CheckoutStepOnePage(driver).click_continue()
