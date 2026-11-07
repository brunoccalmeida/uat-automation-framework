"""Unit tests for HeaderComponent.

Tests the header shared by every page after login, in isolation using mocks.
"""

from unittest.mock import Mock, call, patch

import pytest
from selenium.webdriver.common.by import By

from pages.cart_page import CartPage
from pages.checkout_complete_page import CheckoutCompletePage
from pages.checkout_step_one_page import CheckoutStepOnePage
from pages.checkout_step_two_page import CheckoutStepTwoPage
from pages.header_component import HeaderComponent
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from pages.product_details_page import ProductDetailsPage
from tests.helpers.navigation_contract import assert_clicks_then_returns_loaded

# Pages shown after login, all of which show the header
LOGGED_IN_PAGES = [
    InventoryPage,
    ProductDetailsPage,
    CartPage,
    CheckoutStepOnePage,
    CheckoutStepTwoPage,
    CheckoutCompletePage,
]


class TestHeaderComponentLocators:
    """Test HeaderComponent locator definitions."""

    def test_header_loaded_locator(self):
        """PAGE_LOADED should be the primary header container."""
        assert HeaderComponent.PAGE_LOADED == (By.CLASS_NAME, "primary_header")

    def test_shopping_cart_badge_locator(self):
        """SHOPPING_CART_BADGE locator should use correct class name."""
        assert HeaderComponent.SHOPPING_CART_BADGE == (
            By.CLASS_NAME,
            "shopping_cart_badge",
        )

    def test_shopping_cart_link_locator(self):
        """SHOPPING_CART_LINK locator should use correct class name."""
        assert HeaderComponent.SHOPPING_CART_LINK == (
            By.CLASS_NAME,
            "shopping_cart_link",
        )

    def test_menu_button_locator(self):
        """MENU_BUTTON locator should use correct ID."""
        assert HeaderComponent.MENU_BUTTON == (By.ID, "react-burger-menu-btn")

    def test_logout_link_locator(self):
        """LOGOUT_LINK locator should use correct ID."""
        assert HeaderComponent.LOGOUT_LINK == (By.ID, "logout_sidebar_link")

    def test_menu_panel_locator(self):
        """MENU_PANEL locator should use the burger menu's wrapper class."""
        assert HeaderComponent.MENU_PANEL == (By.CLASS_NAME, "bm-menu-wrap")


class TestGetCartItemCount:
    """Test get_cart_item_count method."""

    def test_get_cart_item_count_returns_badge_value_when_present(self):
        """get_cart_item_count should return badge number when badge exists."""
        header = HeaderComponent(Mock())

        with (
            patch.object(header, "is_element_visible", return_value=True),
            patch.object(header, "get_text", return_value="3") as mock_get_text,
        ):
            result = header.get_cart_item_count()

        assert result == 3
        mock_get_text.assert_called_once_with(HeaderComponent.SHOPPING_CART_BADGE)

    def test_get_cart_item_count_returns_zero_when_no_badge(self):
        """get_cart_item_count should return 0 when badge not present."""
        header = HeaderComponent(Mock())

        with patch.object(
            header, "is_element_visible", return_value=False
        ) as mock_visible:
            result = header.get_cart_item_count()

        assert result == 0
        mock_visible.assert_called_once_with(
            HeaderComponent.SHOPPING_CART_BADGE, timeout=1
        )


class TestClickShoppingCart:
    """Test click_shopping_cart method."""

    def test_click_shopping_cart_clicks_and_returns_loaded_cart_page(self):
        """click_shopping_cart clicks the cart link, returns a loaded CartPage."""
        header = HeaderComponent(Mock())

        assert_clicks_then_returns_loaded(
            header,
            header.click_shopping_cart,
            HeaderComponent.SHOPPING_CART_LINK,
            "pages.cart_page.CartPage",
        )


class TestOpenMenu:
    """Test open_menu method."""

    def test_open_menu_waits_until_closed_clicks_then_waits_until_stable(self):
        """open_menu clicks only once the menu has settled closed (#129).

        The menu hides itself (``hidden``) 500 ms after it mounts; a click just
        before that timer fires opens the menu, which the timer then hides, so
        the click must wait for that state. The Logout link counts as clickable
        while it still slides in from off screen, so the click must be followed
        by a wait for it to stop moving.
        """
        header = HeaderComponent(Mock())

        with (
            patch.object(header, "wait_until_menu_is_closed") as mock_closed,
            patch.object(header, "click") as mock_click,
            patch.object(header, "wait_until_stable") as mock_stable,
        ):
            calls = Mock()
            calls.attach_mock(mock_closed, "wait_until_menu_is_closed")
            calls.attach_mock(mock_click, "click")
            calls.attach_mock(mock_stable, "wait_until_stable")
            header.open_menu()

        assert calls.mock_calls == [
            call.wait_until_menu_is_closed(),
            call.click(HeaderComponent.MENU_BUTTON),
            call.wait_until_stable(HeaderComponent.LOGOUT_LINK),
        ]


class TestWaitUntilMenuIsClosed:
    """Test wait_until_menu_is_closed method."""

    def test_waits_for_the_menu_panel_to_carry_the_hidden_attribute(self):
        """Closed means settled: the panel carries ``hidden``, not just off screen."""
        header = HeaderComponent(Mock())
        header.wait = Mock()

        with patch("pages.header_component.EC") as mock_ec:
            header.wait_until_menu_is_closed()

            mock_ec.element_attribute_to_include.assert_called_once_with(
                HeaderComponent.MENU_PANEL, "hidden"
            )
            header.wait.until.assert_called_once_with(
                mock_ec.element_attribute_to_include.return_value,
                message="the burger menu did not settle closed",
            )


class TestClickLogout:
    """Test click_logout method."""

    def test_click_logout_clicks_and_returns_loaded_login_page(self):
        """click_logout clicks the logout link, returns a loaded LoginPage."""
        header = HeaderComponent(Mock())

        assert_clicks_then_returns_loaded(
            header,
            header.click_logout,
            HeaderComponent.LOGOUT_LINK,
            "pages.login_page.LoginPage",
        )


class TestLogout:
    """Test logout method."""

    def test_logout_opens_the_menu_then_clicks_logout(self):
        """logout should open the menu, then click Logout and return its page."""
        header = HeaderComponent(Mock())

        with (
            patch.object(header, "open_menu") as mock_open,
            patch.object(header, "click_logout") as mock_logout,
        ):
            calls = Mock()
            calls.attach_mock(mock_open, "open_menu")
            calls.attach_mock(mock_logout, "click_logout")
            result = header.logout()

        assert calls.mock_calls == [call.open_menu(), call.click_logout()]
        assert result is mock_logout.return_value


class TestPagesIncludeHeader:
    """Test that pages shown after login include the header component."""

    @pytest.mark.parametrize("page_class", LOGGED_IN_PAGES)
    def test_page_includes_the_header(self, page_class):
        """Every page after login has the shared header, on the same driver."""
        driver = Mock()

        page = page_class(driver, timeout=5)

        assert isinstance(page.header, HeaderComponent)
        assert page.header.driver is driver
        assert page.header.timeout == 5

    def test_login_page_has_no_header(self):
        """The login page is shown before login, so it has no header."""
        assert not hasattr(LoginPage(Mock()), "header")
