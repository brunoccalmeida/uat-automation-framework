"""Integration tests for LoginPage with real browser.

Tests LoginPage interactions with actual DOM elements,
validating that locators work and methods interact correctly with Selenium.
"""

import pytest

from pages.login_page import LoginPage


class TestLoginPageElements:
    """Test LoginPage elements are present and accessible."""
    
    def test_username_input_is_present(self, driver, base_url):
        """Username input should be present on login page."""
        driver.get(base_url)
        page = LoginPage(driver)
        
        assert page.is_element_present(page.USERNAME_INPUT, timeout=5)
    
    def test_password_input_is_present(self, driver, base_url):
        """Password input should be present on login page."""
        driver.get(base_url)
        page = LoginPage(driver)
        
        assert page.is_element_present(page.PASSWORD_INPUT, timeout=5)
    
    def test_login_button_is_present(self, driver, base_url):
        """Login button should be present on login page."""
        driver.get(base_url)
        page = LoginPage(driver)
        
        assert page.is_element_present(page.LOGIN_BUTTON, timeout=5)


class TestLoginPageInteractions:
    """Test LoginPage method interactions with browser."""
    
    def test_enter_username_types_text(self, driver, base_url):
        """enter_username should type text into username field."""
        driver.get(base_url)
        page = LoginPage(driver)
        
        test_username = "standard_user"
        page.enter_username(test_username)
        
        # Verify text was entered
        username_field = driver.find_element(*page.USERNAME_INPUT)
        assert username_field.get_attribute("value") == test_username
    
    def test_enter_password_types_text(self, driver, base_url):
        """enter_password should type text into password field."""
        driver.get(base_url)
        page = LoginPage(driver)
        
        test_password = "secret_sauce"
        page.enter_password(test_password)
        
        # Verify text was entered
        password_field = driver.find_element(*page.PASSWORD_INPUT)
        assert password_field.get_attribute("value") == test_password
    
    def test_login_with_valid_credentials_succeeds(self, driver, base_url):
        """login with valid credentials should navigate to inventory page."""
        driver.get(base_url)
        page = LoginPage(driver)
        
        page.login("standard_user", "secret_sauce")
        
        # Should navigate away from login page
        assert "/inventory.html" in driver.current_url
    
    def test_login_with_invalid_credentials_shows_error(self, driver, base_url):
        """login with invalid credentials should display error message."""
        driver.get(base_url)
        page = LoginPage(driver)
        
        page.login("invalid_user", "wrong_password")
        
        # Error message should be present
        assert page.is_element_present(page.ERROR_MESSAGE, timeout=3)
        error_text = page.get_error_message()
        assert error_text is not None
        assert "Username and password do not match" in error_text


class TestLoginPageErrorHandling:
    """Test LoginPage error scenarios with real browser."""
    
    def test_get_error_message_returns_none_when_no_error(self, driver, base_url):
        """get_error_message should return None when error not present."""
        driver.get(base_url)
        page = LoginPage(driver)
        
        error = page.get_error_message()
        assert error is None
    
    def test_locked_user_shows_error(self, driver, base_url):
        """Locked user should display appropriate error message."""
        driver.get(base_url)
        page = LoginPage(driver)
        
        page.login("locked_out_user", "secret_sauce")
        
        error = page.get_error_message()
        assert error is not None
        assert "locked out" in error.lower()
