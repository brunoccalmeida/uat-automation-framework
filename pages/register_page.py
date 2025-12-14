"""Register Page Object for Parabank.

Represents the user registration functionality.
"""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class RegisterPage(BasePage):
    """Page Object for Parabank registration form."""
    
    # Locators
    FIRST_NAME_INPUT = (By.NAME, "customer.firstName")
    LAST_NAME_INPUT = (By.NAME, "customer.lastName")
    ADDRESS_INPUT = (By.NAME, "customer.address.street")
    CITY_INPUT = (By.NAME, "customer.address.city")
    STATE_INPUT = (By.NAME, "customer.address.state")
    ZIP_CODE_INPUT = (By.NAME, "customer.address.zipCode")
    PHONE_INPUT = (By.NAME, "customer.phoneNumber")
    SSN_INPUT = (By.NAME, "customer.ssn")
    USERNAME_INPUT = (By.NAME, "customer.username")
    PASSWORD_INPUT = (By.NAME, "customer.password")
    CONFIRM_PASSWORD_INPUT = (By.NAME, "repeatedPassword")
    REGISTER_BUTTON = (By.XPATH, "//input[@value='Register']")
    SUCCESS_MESSAGE = (By.XPATH, "//div[@id='rightPanel']//p[contains(text(), 'Your account was created successfully')]")
    LOGOUT_LINK = (By.LINK_TEXT, "Log Out")
    
    def fill_registration_form(self, user_data: dict[str, str]) -> None:
        """Fill registration form with user data.
        
        Args:
            user_data: Dictionary with registration fields and values
        """
        self.type(self.FIRST_NAME_INPUT, user_data.get("first_name", ""))
        self.type(self.LAST_NAME_INPUT, user_data.get("last_name", ""))
        self.type(self.ADDRESS_INPUT, user_data.get("address", ""))
        self.type(self.CITY_INPUT, user_data.get("city", ""))
        self.type(self.STATE_INPUT, user_data.get("state", ""))
        self.type(self.ZIP_CODE_INPUT, user_data.get("zip_code", ""))
        self.type(self.PHONE_INPUT, user_data.get("phone", ""))
        self.type(self.SSN_INPUT, user_data.get("ssn", ""))
        self.type(self.USERNAME_INPUT, user_data.get("username", ""))
        
        password = user_data.get("password", "")
        self.type(self.PASSWORD_INPUT, password)
        self.type(self.CONFIRM_PASSWORD_INPUT, password)
    
    def submit_registration(self) -> None:
        """Submit registration form."""
        self.click(self.REGISTER_BUTTON)
    
    def get_success_message(self) -> str | None:
        """Get registration success message if present.
        
        Returns:
            Success message text if present, None otherwise.
        """
        if self.is_element_present(self.SUCCESS_MESSAGE, timeout=5):
            return self.get_text(self.SUCCESS_MESSAGE)
        return None
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in.
        
        Returns:
            True if Log Out link is present, False otherwise.
        """
        return self.is_element_present(self.LOGOUT_LINK, timeout=3)
