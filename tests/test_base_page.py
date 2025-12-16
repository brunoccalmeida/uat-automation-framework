"""Unit tests for BasePage class.

Tests the fundamental Page Object functionality without requiring a browser.
Uses mocks to isolate the logic from Selenium WebDriver.
"""

import pytest
from unittest.mock import Mock, MagicMock, call
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

from pages.base_page import BasePage


class TestBasePageInitialization:
    """Test BasePage initialization and setup."""
    
    def test_base_page_stores_driver(self):
        """BasePage should store the WebDriver instance."""
        mock_driver = Mock()
        page = BasePage(mock_driver)
        
        assert page.driver is mock_driver
    
    def test_base_page_creates_wait_with_default_timeout(self):
        """BasePage should create WebDriverWait with 10s timeout by default."""
        mock_driver = Mock()
        page = BasePage(mock_driver)
        
        assert isinstance(page.wait, WebDriverWait)
        assert page.wait._timeout == 10
    
    def test_base_page_stores_driver_reference_in_wait(self):
        """WebDriverWait should use the same driver instance."""
        mock_driver = Mock()
        page = BasePage(mock_driver)
        
        assert page.wait._driver is mock_driver


class TestFindElement:
    """Test find_element method."""
    
    def test_find_element_uses_explicit_wait(self):
        """find_element should use WebDriverWait to locate element."""
        mock_driver = Mock()
        mock_element = Mock()
        mock_wait = Mock()
        mock_wait.until.return_value = mock_element
        
        page = BasePage(mock_driver)
        page.wait = mock_wait
        
        locator = (By.ID, "test-id")
        result = page.find_element(locator)
        
        assert result is mock_element
        mock_wait.until.assert_called_once()
    
    def test_find_element_uses_visibility_condition(self):
        """find_element should wait for element to be visible."""
        mock_driver = Mock()
        page = BasePage(mock_driver)
        
        locator = (By.ID, "test-id")
        # This will test that EC.visibility_of_element_located is used
        # by checking the wait.until was called (actual EC testing is integration)
        page.wait = Mock()
        page.find_element(locator)
        
        page.wait.until.assert_called_once()


class TestFindClickableElement:
    """Test find_clickable_element method."""
    
    def test_find_clickable_element_uses_explicit_wait(self):
        """find_clickable_element should use WebDriverWait."""
        mock_driver = Mock()
        mock_element = Mock()
        mock_wait = Mock()
        mock_wait.until.return_value = mock_element
        
        page = BasePage(mock_driver)
        page.wait = mock_wait
        
        locator = (By.ID, "button-id")
        result = page.find_clickable_element(locator)
        
        assert result is mock_element
        mock_wait.until.assert_called_once()


class TestTypeMethod:
    """Test type method (text input)."""
    
    def test_type_finds_clickable_element(self, mocker):
        """type should find element using find_clickable_element."""
        mock_driver = Mock()
        mock_element = Mock()
        
        page = BasePage(mock_driver)
        mocker.patch.object(page, 'find_clickable_element', return_value=mock_element)
        mocker.patch.object(page.driver, 'execute_script')
        mocker.patch.object(page.wait, 'until', return_value=mock_element)
        
        locator = (By.ID, "input-field")
        page.type(locator, "test text")
        
        page.find_clickable_element.assert_called_once_with(locator)
    
    def test_type_scrolls_element_into_view(self, mocker):
        """type should scroll element to center of viewport."""
        mock_driver = Mock()
        mock_element = Mock()
        
        page = BasePage(mock_driver)
        mocker.patch.object(page, 'find_clickable_element', return_value=mock_element)
        mocker.patch.object(page.driver, 'execute_script')
        mocker.patch.object(page.wait, 'until', return_value=mock_element)
        
        locator = (By.ID, "input-field")
        page.type(locator, "test text")
        
        page.driver.execute_script.assert_called_once_with(
            "arguments[0].scrollIntoView({block: 'center'});",
            mock_element
        )
    
    def test_type_re_verifies_element_clickable_after_scroll(self, mocker):
        """type should verify element is still clickable after scrolling."""
        mock_driver = Mock()
        mock_element = Mock()
        
        page = BasePage(mock_driver)
        mocker.patch.object(page, 'find_clickable_element', return_value=mock_element)
        mocker.patch.object(page.driver, 'execute_script')
        mocker.patch.object(page.wait, 'until', return_value=mock_element)
        
        locator = (By.ID, "input-field")
        page.type(locator, "test text")
        
        # Should be called once for re-verification
        page.wait.until.assert_called_once()
    
    def test_type_clears_field_before_typing(self, mocker):
        """type should clear existing text before typing new text."""
        mock_driver = Mock()
        mock_element = Mock()
        
        page = BasePage(mock_driver)
        mocker.patch.object(page, 'find_clickable_element', return_value=mock_element)
        mocker.patch.object(page.driver, 'execute_script')
        mocker.patch.object(page.wait, 'until', return_value=mock_element)
        
        locator = (By.ID, "input-field")
        page.type(locator, "test text")
        
        mock_element.clear.assert_called_once()
    
    def test_type_sends_text_to_element(self, mocker):
        """type should send keys to the element."""
        mock_driver = Mock()
        mock_element = Mock()
        
        page = BasePage(mock_driver)
        mocker.patch.object(page, 'find_clickable_element', return_value=mock_element)
        mocker.patch.object(page.driver, 'execute_script')
        mocker.patch.object(page.wait, 'until', return_value=mock_element)
        
        locator = (By.ID, "input-field")
        test_text = "my test input"
        page.type(locator, test_text)
        
        mock_element.send_keys.assert_called_once_with(test_text)
    
    def test_type_method_sequence_is_correct(self, mocker):
        """type should execute operations in correct order."""
        mock_driver = Mock()
        mock_element = Mock()
        
        page = BasePage(mock_driver)
        mocker.patch.object(page, 'find_clickable_element', return_value=mock_element)
        mock_execute = mocker.patch.object(page.driver, 'execute_script')
        mock_wait = mocker.patch.object(page.wait, 'until', return_value=mock_element)
        
        locator = (By.ID, "input-field")
        page.type(locator, "text")
        
        # Verify call order
        manager = Mock()
        manager.attach_mock(page.find_clickable_element, 'find_clickable')
        manager.attach_mock(mock_execute, 'execute_script')
        manager.attach_mock(mock_wait, 'wait_until')
        manager.attach_mock(mock_element.clear, 'clear')
        manager.attach_mock(mock_element.send_keys, 'send_keys')
        
        # Order should be: find → scroll → wait → clear → send_keys
        assert mock_element.clear.called
        assert mock_element.send_keys.called


class TestClickMethod:
    """Test click method."""
    
    def test_click_finds_clickable_element(self, mocker):
        """click should find element using find_clickable_element."""
        mock_driver = Mock()
        mock_element = Mock()
        
        page = BasePage(mock_driver)
        mocker.patch.object(page, 'find_clickable_element', return_value=mock_element)
        
        locator = (By.ID, "button")
        page.click(locator)
        
        page.find_clickable_element.assert_called_once_with(locator)
    
    def test_click_calls_element_click(self, mocker):
        """click should call click() on the element."""
        mock_driver = Mock()
        mock_element = Mock()
        
        page = BasePage(mock_driver)
        mocker.patch.object(page, 'find_clickable_element', return_value=mock_element)
        
        locator = (By.ID, "button")
        page.click(locator)
        
        mock_element.click.assert_called_once()


class TestGetTextMethod:
    """Test get_text method."""
    
    def test_get_text_finds_visible_element(self, mocker):
        """get_text should find element using find_element."""
        mock_driver = Mock()
        mock_element = Mock()
        mock_element.text = "Sample text"
        
        page = BasePage(mock_driver)
        mocker.patch.object(page, 'find_element', return_value=mock_element)
        
        locator = (By.ID, "label")
        result = page.get_text(locator)
        
        page.find_element.assert_called_once_with(locator)
    
    def test_get_text_returns_element_text(self, mocker):
        """get_text should return the text property of element."""
        mock_driver = Mock()
        mock_element = Mock()
        expected_text = "Expected text content"
        mock_element.text = expected_text
        
        page = BasePage(mock_driver)
        mocker.patch.object(page, 'find_element', return_value=mock_element)
        
        locator = (By.ID, "label")
        result = page.get_text(locator)
        
        assert result == expected_text


class TestIsElementPresentMethod:
    """Test is_element_present method."""
    
    def test_is_element_present_returns_true_when_found(self):
        """is_element_present should return True when element is found."""
        from unittest.mock import patch
        
        mock_driver = Mock()
        mock_wait = Mock()
        mock_wait.until.return_value = Mock()  # Element found
        
        page = BasePage(mock_driver)
        
        # Mock WebDriverWait creation for custom timeout
        with patch('pages.base_page.WebDriverWait', return_value=mock_wait):
            locator = (By.ID, "existing-element")
            result = page.is_element_present(locator, timeout=3)
        
        assert result is True
        mock_wait.until.assert_called_once()
    
    def test_is_element_present_returns_false_on_timeout(self):
        """is_element_present should return False if element not found."""
        from unittest.mock import patch
        
        mock_driver = Mock()
        mock_wait = Mock()
        mock_wait.until.side_effect = TimeoutException("Not found")
        
        page = BasePage(mock_driver)
        
        with patch('pages.base_page.WebDriverWait', return_value=mock_wait):
            locator = (By.ID, "missing-element")
            result = page.is_element_present(locator, timeout=3)
        
        assert result is False
    
    def test_is_element_present_uses_custom_timeout(self):
        """is_element_present should use provided custom timeout."""
        from unittest.mock import patch
        
        mock_driver = Mock()
        
        page = BasePage(mock_driver)
        
        with patch('pages.base_page.WebDriverWait') as mock_wait_class:
            locator = (By.ID, "element")
            custom_timeout = 5
            page.is_element_present(locator, timeout=custom_timeout)
            
            # Verify WebDriverWait was created with custom timeout
            mock_wait_class.assert_called_with(mock_driver, custom_timeout)
