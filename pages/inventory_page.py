"""Inventory Page Object for Sauce Demo.

Represents the products/inventory page after successful login.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from pages.base_page import BasePage


class InventoryPage(BasePage):
    """Page Object for Sauce Demo inventory (products) page."""

    # Locators
    INVENTORY_CONTAINER = (By.ID, "inventory_container")
    INVENTORY_ITEMS = (By.CLASS_NAME, "inventory_item")
    INVENTORY_ITEM_NAME = (By.CLASS_NAME, "inventory_item_name")
    INVENTORY_ITEM_PRICE = (By.CLASS_NAME, "inventory_item_price")
    PAGE_TITLE = (By.CLASS_NAME, "title")
    SHOPPING_CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    SHOPPING_CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")
    SORT_DROPDOWN = (By.CLASS_NAME, "product_sort_container")

    def is_on_inventory_page(self) -> bool:
        """Check if user is on inventory page.

        Returns:
            True if inventory container is present, False otherwise.
        """
        return self.is_element_present(self.INVENTORY_CONTAINER, timeout=3)

    def get_page_title(self) -> str:
        """Get the page title text.

        Returns:
            Page title text (should be 'Products').
        """
        return self.get_text(self.PAGE_TITLE)

    def get_product_count(self) -> int:
        """Get total number of products displayed.

        Returns:
            Number of product items on page.
        """
        items = self.driver.find_elements(*self.INVENTORY_ITEMS)
        return len(items)

    def add_product_to_cart(self, product_name: str) -> None:
        """Add specific product to shopping cart by name.

        Args:
            product_name: Name of product (e.g., 'Sauce Labs Backpack').
        """
        # Convert product name to button ID format
        # "Sauce Labs Backpack" -> "add-to-cart-sauce-labs-backpack"
        button_id = f"add-to-cart-{product_name.lower().replace(' ', '-')}"
        add_button = (By.ID, button_id)
        self.click(add_button)

    def get_cart_item_count(self) -> int:
        """Get number of items in shopping cart.

        Returns:
            Number shown in cart badge, 0 if no badge present.
        """
        if self.is_element_present(self.SHOPPING_CART_BADGE, timeout=1):
            badge_text = self.get_text(self.SHOPPING_CART_BADGE)
            return int(badge_text)
        return 0

    def click_shopping_cart(self) -> None:
        """Click shopping cart icon to view cart."""
        self.click(self.SHOPPING_CART_LINK)

    def logout(self) -> None:
        """Log out from application."""
        self.click(self.MENU_BUTTON)
        self.click(self.LOGOUT_LINK)

    def select_sort_option(self, option: str) -> None:
        """Select sort option from dropdown.

        Args:
            option: Sort option value (az, za, lohi, hilo).
        """
        dropdown_element = self.find_clickable_element(self.SORT_DROPDOWN)
        select = Select(dropdown_element)
        select.select_by_value(option)

    def get_product_names(self) -> list[str]:
        """Get all product names from inventory page.

        Returns:
            List of product names in display order.
        """
        name_elements = self.driver.find_elements(*self.INVENTORY_ITEM_NAME)
        return [element.text for element in name_elements]

    def get_product_prices(self) -> list[float]:
        """Get all product prices from inventory page.

        Returns:
            List of product prices in display order as floats.
        """
        price_elements = self.driver.find_elements(*self.INVENTORY_ITEM_PRICE)
        return [float(element.text.replace("$", "")) for element in price_elements]

    def get_current_sort_option(self) -> str:
        """Get currently selected sort option from dropdown.

        Returns:
            Value of selected sort option (az, za, lohi, hilo).
        """
        dropdown_element = self.find_element(self.SORT_DROPDOWN)
        select = Select(dropdown_element)
        return select.first_selected_option.get_attribute("value")
