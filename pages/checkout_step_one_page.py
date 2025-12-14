"""Checkout Step One Page Object for Sauce Demo.

Represents the first step of checkout where customer information is entered.
"""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CheckoutStepOnePage(BasePage):
    """Page Object for Sauce Demo checkout step one (customer information)."""
    
    # Locators
    CHECKOUT_INFO_CONTAINER = (By.CLASS_NAME, "checkout_info")
    FIRST_NAME_INPUT = (By.ID, "first-name")
    LAST_NAME_INPUT = (By.ID, "last-name")
    ZIP_CODE_INPUT = (By.ID, "postal-code")
    CONTINUE_BUTTON = (By.ID, "continue")
    CANCEL_BUTTON = (By.ID, "cancel")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")
    
    def is_on_checkout_form(self) -> bool:
        """Check if user is on checkout form page.
        
        Returns:
            True if checkout info container is present, False otherwise.
        """
        return self.is_element_present(self.CHECKOUT_INFO_CONTAINER, timeout=5)
    
    def enter_first_name(self, first_name: str) -> None:
        """Enter first name in checkout form.
        
        Args:
            first_name: Customer's first name.
        """
        self.type(self.FIRST_NAME_INPUT, first_name)
    
    def enter_last_name(self, last_name: str) -> None:
        """Enter last name in checkout form.
        
        Args:
            last_name: Customer's last name.
        """
        self.type(self.LAST_NAME_INPUT, last_name)
    
    def enter_zip_code(self, zip_code: str) -> None:
        """Enter zip/postal code in checkout form.
        
        Args:
            zip_code: Customer's zip/postal code.
        """
        self.type(self.ZIP_CODE_INPUT, zip_code)
    
    def click_continue(self) -> None:
        """Click Continue button to proceed to checkout step two."""
        self.click(self.CONTINUE_BUTTON)
    
    def click_cancel(self) -> None:
        """Click Cancel button to return to cart."""
        self.click(self.CANCEL_BUTTON)
    
    def is_error_displayed(self) -> bool:
        """Check if error message is displayed.
        
        Returns:
            True if error message is present, False otherwise.
        """
        return self.is_element_present(self.ERROR_MESSAGE, timeout=2)
    
    def get_error_message(self) -> str:
        """Get error message text.
        
        Returns:
            Error message text.
        """
        return self.get_text(self.ERROR_MESSAGE)
