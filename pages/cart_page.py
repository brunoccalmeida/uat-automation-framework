"""Cart Page Object for Sauce Demo.

Represents the shopping cart page.
"""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CartPage(BasePage):
    """Page Object for Sauce Demo shopping cart page."""
    
    # Locators
    CART_CONTAINER = (By.ID, "cart_contents_container")
    CART_ITEMS = (By.CLASS_NAME, "cart_item")
    CART_ITEM_NAME = (By.CLASS_NAME, "inventory_item_name")
    REMOVE_BUTTON_PREFIX = "remove-"  # Will be combined with product name
    CONTINUE_SHOPPING_BUTTON = (By.ID, "continue-shopping")
    CHECKOUT_BUTTON = (By.ID, "checkout")
    
    def is_on_cart_page(self) -> bool:
        """Check if user is on cart page.
        
        Returns:
            True if cart container is present, False otherwise.
        """
        return self.is_element_present(self.CART_CONTAINER, timeout=3)
    
    def get_cart_item_count(self) -> int:
        """Get number of items in cart.
        
        Returns:
            Number of cart items.
        """
        items = self.driver.find_elements(*self.CART_ITEMS)
        return len(items)
    
    def is_product_in_cart(self, product_name: str) -> bool:
        """Check if specific product is in cart.
        
        Args:
            product_name: Name of product to check.
            
        Returns:
            True if product found in cart, False otherwise.
        """
        cart_items = self.driver.find_elements(*self.CART_ITEM_NAME)
        for item in cart_items:
            if product_name in item.text:
                return True
        return False
    
    def remove_product(self, product_name: str) -> None:
        """Remove product from cart by name.
        
        Args:
            product_name: Name of product to remove.
        """
        # Convert product name to button ID format
        # "Sauce Labs Backpack" -> "remove-sauce-labs-backpack"
        button_id = f"{self.REMOVE_BUTTON_PREFIX}{product_name.lower().replace(' ', '-')}"
        remove_button = (By.ID, button_id)
        self.click(remove_button)
    
    def click_continue_shopping(self) -> None:
        """Click Continue Shopping button."""
        self.click(self.CONTINUE_SHOPPING_BUTTON)
    
    def click_checkout(self) -> None:
        """Click Checkout button."""
        self.click(self.CHECKOUT_BUTTON)
