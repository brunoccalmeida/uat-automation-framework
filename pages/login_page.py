"""Login Page Object for Sauce Demo.

Represents the login functionality on Sauce Demo e-commerce application.
"""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    """Page Object for Sauce Demo login form."""
    
    # Locators
    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")
    
    def enter_username(self, username: str) -> None:
        """Enter username into login form.
        
        Args:
            username: Username to enter.
        """
        self.type(self.USERNAME_INPUT, username)
    
    def enter_password(self, password: str) -> None:
        """Enter password into login form.
        
        Args:
            password: Password to enter.
        """
        self.type(self.PASSWORD_INPUT, password)
    
    def click_login(self) -> None:
        """Click the login button."""
        self.click(self.LOGIN_BUTTON)
    
    def login(self, username: str, password: str) -> None:
        """Perform complete login action.
        
        Convenience method that combines all login steps.
        
        Args:
            username: Username to login with.
            password: Password to login with.
        """
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
    
    def get_error_message(self) -> str | None:
        """Get error message if present.
        
        Returns:
            Error message text if present, None otherwise.
        """
        if self.is_element_present(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return None
