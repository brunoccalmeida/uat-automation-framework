"""Checkout Complete Page Object for Sauce Demo.

Represents the order confirmation page after successful checkout.
"""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CheckoutCompletePage(BasePage):
    """Page Object for Sauce Demo checkout complete (confirmation) page."""
    
    # Locators
    CHECKOUT_COMPLETE_CONTAINER = (By.ID, "checkout_complete_container")
    COMPLETE_HEADER = (By.CLASS_NAME, "complete-header")
    COMPLETE_TEXT = (By.CLASS_NAME, "complete-text")
    BACK_HOME_BUTTON = (By.ID, "back-to-products")
    PONY_EXPRESS_IMAGE = (By.CLASS_NAME, "pony_express")
    
    def is_on_confirmation_page(self) -> bool:
        """Check if user is on order confirmation page.
        
        Returns:
            True if checkout complete container is present, False otherwise.
        """
        return self.is_element_present(self.CHECKOUT_COMPLETE_CONTAINER, timeout=3)
    
    def get_confirmation_message(self) -> str:
        """Get order confirmation message.
        
        Returns:
            Confirmation header text.
        """
        return self.get_text(self.COMPLETE_HEADER)
    
    def get_confirmation_text(self) -> str:
        """Get detailed confirmation text.
        
        Returns:
            Confirmation description text.
        """
        return self.get_text(self.COMPLETE_TEXT)
    
    def click_back_home(self) -> None:
        """Click Back Home button to return to products page."""
        self.click(self.BACK_HOME_BUTTON)
    
    def is_pony_express_displayed(self) -> bool:
        """Check if Pony Express delivery image is displayed.
        
        Returns:
            True if image is present, False otherwise.
        """
        return self.is_element_present(self.PONY_EXPRESS_IMAGE, timeout=2)
