"""Integration tests for InventoryPage with real browser.

Tests InventoryPage interactions with actual DOM elements.
"""

from pages.inventory_page import InventoryPage
from tests.helpers.navigation import go_to_inventory


class TestInventoryPageElements:
    """Test InventoryPage elements are present."""

    def test_inventory_container_is_present(self, authenticated_driver):
        """Inventory container should be present after login."""
        page = InventoryPage(authenticated_driver)

        assert page.is_on_inventory_page()

    def test_page_title_displays_products(self, authenticated_driver):
        """Page title should display 'Products'."""
        page = InventoryPage(authenticated_driver)

        title = page.get_page_title()
        assert title == "Products"

    def test_product_count_is_correct(self, authenticated_driver):
        """Should display 6 products on inventory page."""
        page = InventoryPage(authenticated_driver)

        count = page.get_product_count()
        assert count == 6


class TestInventoryPageInteractions:
    """Test InventoryPage method interactions with browser."""

    def test_add_product_to_cart_updates_badge(self, authenticated_driver):
        """Adding product to cart should update cart badge."""
        page = InventoryPage(authenticated_driver)

        # Initially no badge
        initial_count = page.header.get_cart_item_count()
        assert initial_count == 0

        # Add product
        page.add_product_to_cart("Sauce Labs Backpack")

        # Badge should show 1
        updated_count = page.header.get_cart_item_count()
        assert updated_count == 1

    def test_add_multiple_products_increments_badge(self, authenticated_driver):
        """Adding multiple products should increment cart badge."""
        page = InventoryPage(authenticated_driver)

        page.add_product_to_cart("Sauce Labs Backpack")
        page.add_product_to_cart("Sauce Labs Bike Light")

        count = page.header.get_cart_item_count()
        assert count == 2


class TestInventoryPageRemoveProduct:
    """Test removing a product from the inventory page."""

    def test_remove_product_clears_the_badge(self, authenticated_driver):
        """Removing the only product in the cart should clear the badge."""
        page = InventoryPage(authenticated_driver)
        page.add_product_to_cart("Sauce Labs Backpack")
        assert page.header.get_cart_item_count() == 1

        page.remove_product("Sauce Labs Backpack")

        assert page.header.get_cart_item_count() == 0


class TestInventoryPageAlert:
    """Test JavaScript alerts raised on the inventory page."""

    def test_accept_alert_returns_the_error_user_sort_alert(self, driver, base_url):
        """error_user sorting opens an alert; accept_alert returns its text."""
        go_to_inventory(driver, base_url, "error_user")
        page = InventoryPage(driver)

        page.select_sort_option("za")

        assert page.accept_alert() == (
            "Sorting is broken! This error has been reported to Backtrace."
        )
        assert page.get_product_names()
