"""Unit tests for LoginPage class.

Tests the LoginPage Page Object in isolation using mocks to verify
that methods call the correct BasePage functionality with proper parameters.
Follows Testing Pyramid best practices.
"""

from unittest.mock import Mock, patch

from selenium.webdriver.common.by import By

from pages.login_page import LoginPage


class TestLoginPageLocators:
    """Test LoginPage locator definitions."""
    
    def test_username_input_locator(self):
        """USERNAME_INPUT locator should use correct ID."""
        assert LoginPage.USERNAME_INPUT == (By.ID, "user-name")
    
    def test_password_input_locator(self):
        """PASSWORD_INPUT locator should use correct ID."""
        assert LoginPage.PASSWORD_INPUT == (By.ID, "password")
    
    def test_login_button_locator(self):
        """LOGIN_BUTTON locator should use correct ID."""
        assert LoginPage.LOGIN_BUTTON == (By.ID, "login-button")
    
    def test_error_message_locator(self):
        """ERROR_MESSAGE locator should use correct CSS selector."""
        assert LoginPage.ERROR_MESSAGE == (By.CSS_SELECTOR, "[data-test='error']")


class TestEnterUsername:
    """Test enter_username method."""
    
    def test_enter_username_calls_type_with_username_locator(self):
        """enter_username should call type() with USERNAME_INPUT locator."""
        mock_driver = Mock()
        page = LoginPage(mock_driver)
        
        with patch.object(page, 'type') as mock_type:
            username = "test_user"
            page.enter_username(username)
            
            mock_type.assert_called_once_with(LoginPage.USERNAME_INPUT, username)


class TestEnterPassword:
    """Test enter_password method."""
    
    def test_enter_password_calls_type_with_password_locator(self):
        """enter_password should call type() with PASSWORD_INPUT locator."""
        mock_driver = Mock()
        page = LoginPage(mock_driver)
        
        with patch.object(page, 'type') as mock_type:
            password = "secret123"
            page.enter_password(password)
            
            mock_type.assert_called_once_with(LoginPage.PASSWORD_INPUT, password)


class TestClickLogin:
    """Test click_login method."""
    
    def test_click_login_calls_click_with_login_button_locator(self):
        """click_login should call click() with LOGIN_BUTTON locator."""
        mock_driver = Mock()
        page = LoginPage(mock_driver)
        
        with patch.object(page, 'click') as mock_click:
            page.click_login()
            
            mock_click.assert_called_once_with(LoginPage.LOGIN_BUTTON)


class TestLoginMethod:
    """Test login method (composite action)."""
    
    def test_login_calls_enter_username(self):
        """login should call enter_username with provided username."""
        mock_driver = Mock()
        page = LoginPage(mock_driver)
        
        with patch.object(page, 'enter_username') as mock_enter_user:
            with patch.object(page, 'enter_password'):
                with patch.object(page, 'click_login'):
                    username = "standard_user"
                    password = "secret_sauce"
                    page.login(username, password)
                    
                    mock_enter_user.assert_called_once_with(username)
    
    def test_login_calls_enter_password(self):
        """login should call enter_password with provided password."""
        mock_driver = Mock()
        page = LoginPage(mock_driver)
        
        with patch.object(page, 'enter_username'):
            with patch.object(page, 'enter_password') as mock_enter_pass:
                with patch.object(page, 'click_login'):
                    username = "standard_user"
                    password = "secret_sauce"
                    page.login(username, password)
                    
                    mock_enter_pass.assert_called_once_with(password)
    
    def test_login_calls_click_login(self):
        """login should call click_login to submit the form."""
        mock_driver = Mock()
        page = LoginPage(mock_driver)
        
        with patch.object(page, 'enter_username'):
            with patch.object(page, 'enter_password'):
                with patch.object(page, 'click_login') as mock_click:
                    username = "standard_user"
                    password = "secret_sauce"
                    page.login(username, password)
                    
                    mock_click.assert_called_once()
    
    def test_login_executes_steps_in_correct_order(self):
        """login should execute enter_username → enter_password → click_login."""
        mock_driver = Mock()
        page = LoginPage(mock_driver)
        
        call_order = []
        
        def track_enter_username(username):
            call_order.append(('enter_username', username))
        
        def track_enter_password(password):
            call_order.append(('enter_password', password))
        
        def track_click_login():
            call_order.append('click_login')
        
        with patch.object(page, 'enter_username', side_effect=track_enter_username):
            with patch.object(page, 'enter_password', side_effect=track_enter_password):
                with patch.object(page, 'click_login', side_effect=track_click_login):
                    page.login("user", "pass")
                    
                    assert call_order == [
                        ('enter_username', 'user'),
                        ('enter_password', 'pass'),
                        'click_login'
                    ]


class TestGetErrorMessage:
    """Test get_error_message method."""
    
    def test_get_error_message_returns_text_when_error_present(self):
        """get_error_message should return error text when error element exists."""
        mock_driver = Mock()
        page = LoginPage(mock_driver)
        
        expected_error = "Epic sadface: Username and password do not match"
        
        with patch.object(page, 'is_element_present', return_value=True):
            with patch.object(page, 'get_text', return_value=expected_error) as mock_get_text:
                result = page.get_error_message()
                
                mock_get_text.assert_called_once_with(LoginPage.ERROR_MESSAGE)
                assert result == expected_error
    
    def test_get_error_message_returns_none_when_error_not_present(self):
        """get_error_message should return None when error element doesn't exist."""
        mock_driver = Mock()
        page = LoginPage(mock_driver)
        
        with patch.object(page, 'is_element_present', return_value=False):
            with patch.object(page, 'get_text') as mock_get_text:
                result = page.get_error_message()
                
                # Should not try to get text if element not present
                mock_get_text.assert_not_called()
                assert result is None
    
    def test_get_error_message_checks_element_presence_first(self):
        """get_error_message should check is_element_present before getting text."""
        mock_driver = Mock()
        page = LoginPage(mock_driver)
        
        with patch.object(page, 'is_element_present', return_value=True) as mock_is_present:
            with patch.object(page, 'get_text', return_value="Error"):
                page.get_error_message()
                
                mock_is_present.assert_called_once_with(LoginPage.ERROR_MESSAGE)
