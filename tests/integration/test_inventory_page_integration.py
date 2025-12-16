"""Integration tests for InventoryPage with real browser.

Tests InventoryPage interactions with actual DOM elements.
"""

import pytest

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


@pytest.fixture(scope="function")
def authenticated_driver(driver, base_url):
    """Provide authenticated driver on inventory page.

    Args:
        driver: WebDriver instance.
        base_url: Application base URL.

    Yields:
        Authenticated WebDriver on inventory page.
    """
    driver.get(base_url)
    login_page = LoginPage(driver)
    login_page.login("standard_user", "secret_sauce")

    yield driver


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
        initial_count = page.get_cart_item_count()
        assert initial_count == 0

        # Add product
        page.add_product_to_cart("Sauce Labs Backpack")

        # Badge should show 1
        updated_count = page.get_cart_item_count()
        assert updated_count == 1

    def test_add_multiple_products_increments_badge(self, authenticated_driver):
        """Adding multiple products should increment cart badge."""
        page = InventoryPage(authenticated_driver)

        page.add_product_to_cart("Sauce Labs Backpack")
        page.add_product_to_cart("Sauce Labs Bike Light")

        count = page.get_cart_item_count()
        assert count == 2

    def test_click_shopping_cart_navigates_to_cart(self, authenticated_driver):
        """Clicking shopping cart should navigate to cart page."""
        page = InventoryPage(authenticated_driver)

        page.click_shopping_cart()

        assert "/cart.html" in authenticated_driver.current_url

    def test_logout_returns_to_login_page(self, authenticated_driver):
        """Logout should return user to login page."""
        page = InventoryPage(authenticated_driver)

        page.logout()

        # Should be on login page
        assert authenticated_driver.current_url.endswith(("/", "/index.html"))

        # Login elements should be present
        login_page = LoginPage(authenticated_driver)
        assert login_page.is_element_present(login_page.USERNAME_INPUT, timeout=3)


class TestInventoryPageNavigation:
    """Test navigation from inventory page."""

    def test_shopping_cart_link_is_clickable(self, authenticated_driver):
        """Shopping cart link should be clickable."""
        page = InventoryPage(authenticated_driver)

        # Should not raise exception
        assert page.is_element_present(page.SHOPPING_CART_LINK, timeout=3)

    def test_menu_button_is_accessible(self, authenticated_driver):
        """Menu button should be accessible for navigation."""
        page = InventoryPage(authenticated_driver)

        assert page.is_element_present(page.MENU_BUTTON, timeout=3)
