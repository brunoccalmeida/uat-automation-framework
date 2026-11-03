"""Header Page Component for Sauce Demo.

Represents the header shared by every page after login: cart badge, cart
link and burger menu.
"""

from selenium.webdriver.common.by import By

from pages import cart_page, login_page
from pages.base_page import BasePage


class HeaderComponent(BasePage):
    """Page Component Object for the header shown on every page after login.

    A component, not a page: each page shown after login includes it as
    ``self.header``.
    It reuses BasePage's explicit waits; PAGE_LOADED is the header itself.
    """

    # Locators
    PAGE_LOADED = (By.CLASS_NAME, "primary_header")
    SHOPPING_CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    SHOPPING_CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")

    def get_cart_item_count(self) -> int:
        """Get number of items in shopping cart.

        Returns:
            Number shown in cart badge, 0 if no badge present.
        """
        if self.is_element_visible(self.SHOPPING_CART_BADGE, timeout=1):
            badge_text = self.get_text(self.SHOPPING_CART_BADGE)
            return int(badge_text)
        return 0

    def click_shopping_cart(self) -> "cart_page.CartPage":
        """Click shopping cart icon to view cart.

        Returns:
            CartPage, once rendered.
        """
        self.click(self.SHOPPING_CART_LINK)
        return cart_page.CartPage(self.driver).wait_until_loaded()

    def open_menu(self) -> None:
        """Open the burger menu.

        Returns once the menu has finished sliding in: its links count as
        clickable while still off screen.
        """
        self.click(self.MENU_BUTTON)
        self.wait_until_stable(self.LOGOUT_LINK)

    def click_logout(self) -> "login_page.LoginPage":
        """Click Logout in the menu (the menu must already be open).

        Returns:
            LoginPage, once rendered.
        """
        self.click(self.LOGOUT_LINK)
        return login_page.LoginPage(self.driver).wait_until_loaded()

    def logout(self) -> "login_page.LoginPage":
        """Log out from application.

        Returns:
            LoginPage, once rendered.
        """
        self.open_menu()
        return self.click_logout()
