"""Integration tests for CartPage with real browser.

Tests CartPage interactions with actual DOM elements.
"""

import pytest

from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


@pytest.fixture(scope="function")
def cart_with_products(driver, base_url):
    """Provide authenticated driver with products in cart.

    Args:
        driver: WebDriver instance.
        base_url: Application base URL.

    Yields:
        WebDriver on cart page with 2 products.
    """
    driver.get(base_url)
    login_page = LoginPage(driver)
    login_page.login("standard_user", "secret_sauce")

    # Add products to cart
    inventory_page = InventoryPage(driver)
    inventory_page.add_product_to_cart("Sauce Labs Backpack")
    inventory_page.add_product_to_cart("Sauce Labs Bike Light")

    # Navigate to cart
    inventory_page.click_shopping_cart()

    yield driver


class TestCartPageElements:
    """Test CartPage elements are present."""

    def test_cart_container_is_present(self, cart_with_products):
        """Cart container should be present on cart page."""
        page = CartPage(cart_with_products)

        assert page.is_on_cart_page()

    def test_cart_items_are_displayed(self, cart_with_products):
        """Cart items should be displayed."""
        page = CartPage(cart_with_products)

        item_count = page.get_cart_item_count()
        assert item_count == 2

    def test_continue_shopping_button_exists(self, cart_with_products):
        """Continue Shopping button should exist."""
        page = CartPage(cart_with_products)

        assert page.is_element_present(page.CONTINUE_SHOPPING_BUTTON, timeout=3)

    def test_checkout_button_exists(self, cart_with_products):
        """Checkout button should exist."""
        page = CartPage(cart_with_products)

        assert page.is_element_present(page.CHECKOUT_BUTTON, timeout=3)


class TestCartPageInteractions:
    """Test CartPage method interactions with browser."""

    def test_product_is_in_cart(self, cart_with_products):
        """Added products should be found in cart."""
        page = CartPage(cart_with_products)

        assert page.is_product_in_cart("Sauce Labs Backpack")
        assert page.is_product_in_cart("Sauce Labs Bike Light")

    def test_remove_product_from_cart(self, cart_with_products):
        """Removing product should decrease cart item count."""
        page = CartPage(cart_with_products)

        initial_count = page.get_cart_item_count()
        assert initial_count == 2

        page.remove_product("Sauce Labs Backpack")

        updated_count = page.get_cart_item_count()
        assert updated_count == 1

    def test_continue_shopping_navigates_to_inventory(self, cart_with_products):
        """Continue Shopping should navigate back to inventory."""
        page = CartPage(cart_with_products)

        page.click_continue_shopping()

        assert "/inventory.html" in cart_with_products.current_url

    def test_checkout_navigates_to_checkout_page(self, cart_with_products):
        """Checkout button should navigate to checkout page."""
        page = CartPage(cart_with_products)

        page.click_checkout()

        assert "/checkout-step-one.html" in cart_with_products.current_url


class TestCartPageProductValidation:
    """Test cart product validation."""

    def test_empty_cart_has_zero_items(self, driver, base_url):
        """Empty cart should have zero items."""
        driver.get(base_url)
        login_page = LoginPage(driver)
        login_page.login("standard_user", "secret_sauce")

        inventory_page = InventoryPage(driver)
        inventory_page.click_shopping_cart()

        page = CartPage(driver)
        assert page.get_cart_item_count() == 0

    def test_product_not_in_cart_returns_false(self, cart_with_products):
        """Product not added should not be found in cart."""
        page = CartPage(cart_with_products)

        assert not page.is_product_in_cart("Nonexistent Product")
