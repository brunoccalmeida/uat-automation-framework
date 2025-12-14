"""Checkout Step Two Page Object for Sauce Demo.

Represents the checkout overview page with order summary.
"""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CheckoutStepTwoPage(BasePage):
    """Page Object for Sauce Demo checkout step two (order overview)."""
    
    # Locators
    CHECKOUT_SUMMARY_CONTAINER = (By.ID, "checkout_summary_container")
    CART_ITEMS = (By.CLASS_NAME, "cart_item")
    ITEM_NAME = (By.CLASS_NAME, "inventory_item_name")
    SUBTOTAL_LABEL = (By.CLASS_NAME, "summary_subtotal_label")
    TAX_LABEL = (By.CLASS_NAME, "summary_tax_label")
    TOTAL_LABEL = (By.CLASS_NAME, "summary_total_label")
    PAYMENT_INFO = (By.CSS_SELECTOR, "[data-test='payment-info-value']")
    SHIPPING_INFO = (By.CSS_SELECTOR, "[data-test='shipping-info-value']")
    FINISH_BUTTON = (By.ID, "finish")
    CANCEL_BUTTON = (By.ID, "cancel")
    
    def is_on_checkout_overview_page(self) -> bool:
        """Check if user is on checkout overview page.
        
        Returns:
            True if checkout summary container is present, False otherwise.
        """
        return self.is_element_present(self.CHECKOUT_SUMMARY_CONTAINER, timeout=3)
    
    def is_product_in_summary(self, product_name: str) -> bool:
        """Check if specific product is in order summary.
        
        Args:
            product_name: Name of product to check.
            
        Returns:
            True if product found in summary, False otherwise.
        """
        item_names = self.driver.find_elements(*self.ITEM_NAME)
        for item in item_names:
            if product_name in item.text:
                return True
        return False
    
    def is_payment_info_displayed(self) -> bool:
        """Check if payment information is displayed.
        
        Returns:
            True if payment info is present, False otherwise.
        """
        return self.is_element_present(self.PAYMENT_INFO, timeout=2)
    
    def is_shipping_info_displayed(self) -> bool:
        """Check if shipping information is displayed.
        
        Returns:
            True if shipping info is present, False otherwise.
        """
        return self.is_element_present(self.SHIPPING_INFO, timeout=2)
    
    def get_item_total(self) -> float:
        """Get item subtotal from order summary.
        
        Returns:
            Subtotal as float value.
        """
        subtotal_text = self.get_text(self.SUBTOTAL_LABEL)
        # Extract number from "Item total: $29.99"
        return float(subtotal_text.split('$')[1])
    
    def get_tax(self) -> float:
        """Get tax amount from order summary.
        
        Returns:
            Tax as float value.
        """
        tax_text = self.get_text(self.TAX_LABEL)
        # Extract number from "Tax: $2.40"
        return float(tax_text.split('$')[1])
    
    def get_total(self) -> float:
        """Get total amount from order summary.
        
        Returns:
            Total as float value.
        """
        total_text = self.get_text(self.TOTAL_LABEL)
        # Extract number from "Total: $32.39"
        return float(total_text.split('$')[1])
    
    def click_finish(self) -> None:
        """Click Finish button to complete order."""
        self.click(self.FINISH_BUTTON)
    
    def click_cancel(self) -> None:
        """Click Cancel button to return to products page."""
        self.click(self.CANCEL_BUTTON)
