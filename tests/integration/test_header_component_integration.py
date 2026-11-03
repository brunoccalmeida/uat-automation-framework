"""Integration tests for HeaderComponent with real browser.

Tests the header shared by every page after login against the actual DOM.
"""

import pytest

from pages.cart_page import CartPage
from pages.checkout_step_one_page import CheckoutStepOnePage
from pages.checkout_step_two_page import CheckoutStepTwoPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from tests.helpers.navigation import go_to_cart, go_to_step_one, go_to_step_two

BACKPACK = "Sauce Labs Backpack"


def open_inventory(driver, base_url):
    """Inventory page with the backpack in the cart."""
    go_to_cart(driver, base_url)
    return CartPage(driver).click_continue_shopping()


def open_product_details(driver, base_url):
    """Backpack details page with the backpack in the cart."""
    return open_inventory(driver, base_url).open_product_details(BACKPACK)


def open_cart(driver, base_url):
    """Cart page with the backpack."""
    go_to_cart(driver, base_url)
    return CartPage(driver)


def open_step_one(driver, base_url):
    """Checkout step one with the backpack in the cart."""
    go_to_step_one(driver, base_url)
    return CheckoutStepOnePage(driver)


def open_step_two(driver, base_url):
    """Checkout step two with the backpack in the cart."""
    go_to_step_two(driver, base_url)
    return CheckoutStepTwoPage(driver)


class TestHeaderOnEveryPage:
    """Test the header is read through each page shown after login."""

    @pytest.mark.parametrize(
        "open_page",
        [open_inventory, open_product_details, open_cart, open_step_one, open_step_two],
    )
    def test_page_header_shows_the_cart_badge(self, driver, base_url, open_page):
        """The page's header renders and its badge counts the cart."""
        page = open_page(driver, base_url)

        page.header.wait_until_loaded()
        assert page.header.get_cart_item_count() == 1

    def test_confirmation_page_header_shows_empty_cart(self, driver, base_url):
        """After the order, the confirmation page's header has no badge."""
        page = open_step_two(driver, base_url).click_finish()

        page.header.wait_until_loaded()
        assert page.header.get_cart_item_count() == 0


class TestHeaderElements:
    """Test the header elements are shown."""

    def test_shopping_cart_link_is_visible(self, authenticated_driver):
        """Shopping cart link should be visible."""
        header = InventoryPage(authenticated_driver).header

        assert header.is_element_visible(header.SHOPPING_CART_LINK, timeout=3)

    def test_menu_button_is_visible(self, authenticated_driver):
        """Menu button should be visible."""
        header = InventoryPage(authenticated_driver).header

        assert header.is_element_visible(header.MENU_BUTTON, timeout=3)


class TestHeaderNavigation:
    """Test navigation from the header."""

    def test_click_shopping_cart_navigates_to_cart(self, authenticated_driver):
        """Clicking shopping cart should navigate to cart page."""
        InventoryPage(authenticated_driver).header.click_shopping_cart()

        assert "/cart.html" in authenticated_driver.current_url

    def test_click_shopping_cart_returns_after_cart_page_renders(
        self, authenticated_driver
    ):
        """click_shopping_cart should return only after cart page is rendered.

        Sauce Demo is a SPA: the URL changes before the new page renders.
        Reading the DOM right after the click (no wait) must see the cart items.
        """
        page = InventoryPage(authenticated_driver)
        page.add_product_to_cart("Sauce Labs Backpack")
        page.add_product_to_cart("Sauce Labs Bike Light")

        next_page = page.header.click_shopping_cart()

        cart_items = authenticated_driver.find_elements(*CartPage.CART_ITEMS)
        assert len(cart_items) == 2
        assert isinstance(next_page, CartPage)

    def test_click_shopping_cart_works_from_another_page(self, cart_with_products):
        """The cart link opens the cart from a page other than the inventory."""
        inventory = CartPage(cart_with_products).click_continue_shopping()
        details = inventory.open_product_details(BACKPACK)

        cart = details.header.click_shopping_cart()

        assert cart.get_cart_item_count() == 2

    def test_open_menu_returns_once_the_menu_has_slid_in(self, authenticated_driver):
        """open_menu returns with the Logout link fully on screen, not sliding."""
        header = InventoryPage(authenticated_driver).header

        header.open_menu()

        link = authenticated_driver.find_element(*header.LOGOUT_LINK)
        assert link.rect["x"] >= 0

    def test_open_menu_then_click_logout_returns_to_login(self, authenticated_driver):
        """Opening the menu, then clicking Logout, returns the login page."""
        header = InventoryPage(authenticated_driver).header

        header.open_menu()
        next_page = header.click_logout()

        assert isinstance(next_page, LoginPage)
        assert next_page.is_element_visible(LoginPage.USERNAME_INPUT, timeout=3)

    def test_logout_returns_to_login_page(self, authenticated_driver):
        """Logout should return user to login page."""
        InventoryPage(authenticated_driver).header.logout()

        assert authenticated_driver.current_url.endswith(("/", "/index.html"))
        login_page = LoginPage(authenticated_driver)
        assert login_page.is_element_visible(login_page.USERNAME_INPUT, timeout=3)
