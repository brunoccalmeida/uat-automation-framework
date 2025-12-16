"""Unit tests for CheckoutCompletePage class.

Tests the CheckoutCompletePage Page Object in isolation using mocks.
"""

from unittest.mock import Mock, patch

from selenium.webdriver.common.by import By

from pages.checkout_complete_page import CheckoutCompletePage


class TestCheckoutCompletePageLocators:
    """Test CheckoutCompletePage locator definitions."""
    
    def test_checkout_complete_container_locator(self):
        """CHECKOUT_COMPLETE_CONTAINER locator should use correct ID."""
        assert CheckoutCompletePage.CHECKOUT_COMPLETE_CONTAINER == (By.ID, "checkout_complete_container")
    
    def test_complete_header_locator(self):
        """COMPLETE_HEADER locator should use correct class name."""
        assert CheckoutCompletePage.COMPLETE_HEADER == (By.CLASS_NAME, "complete-header")
    
    def test_complete_text_locator(self):
        """COMPLETE_TEXT locator should use correct class name."""
        assert CheckoutCompletePage.COMPLETE_TEXT == (By.CLASS_NAME, "complete-text")
    
    def test_back_home_button_locator(self):
        """BACK_HOME_BUTTON locator should use correct ID."""
        assert CheckoutCompletePage.BACK_HOME_BUTTON == (By.ID, "back-to-products")
    
    def test_pony_express_image_locator(self):
        """PONY_EXPRESS_IMAGE locator should use correct class name."""
        assert CheckoutCompletePage.PONY_EXPRESS_IMAGE == (By.CLASS_NAME, "pony_express")


class TestIsOnConfirmationPage:
    """Test is_on_confirmation_page method."""
    
    def test_is_on_confirmation_page_returns_true_when_container_present(self):
        """is_on_confirmation_page should return True when complete container exists."""
        mock_driver = Mock()
        page = CheckoutCompletePage(mock_driver)
        
        with patch.object(page, 'is_element_present', return_value=True) as mock_is_present:
            result = page.is_on_confirmation_page()
            
            mock_is_present.assert_called_once_with(CheckoutCompletePage.CHECKOUT_COMPLETE_CONTAINER, timeout=3)
            assert result is True
    
    def test_is_on_confirmation_page_returns_false_when_container_not_present(self):
        """is_on_confirmation_page should return False when complete container doesn't exist."""
        mock_driver = Mock()
        page = CheckoutCompletePage(mock_driver)
        
        with patch.object(page, 'is_element_present', return_value=False):
            result = page.is_on_confirmation_page()
            
            assert result is False


class TestGetConfirmationMessage:
    """Test get_confirmation_message method."""
    
    def test_get_confirmation_message_returns_header_text(self):
        """get_confirmation_message should return confirmation header text."""
        mock_driver = Mock()
        page = CheckoutCompletePage(mock_driver)
        
        with patch.object(page, 'get_text', return_value="Thank you for your order!") as mock_get_text:
            result = page.get_confirmation_message()
            
            mock_get_text.assert_called_once_with(CheckoutCompletePage.COMPLETE_HEADER)
            assert result == "Thank you for your order!"


class TestGetConfirmationText:
    """Test get_confirmation_text method."""
    
    def test_get_confirmation_text_returns_description_text(self):
        """get_confirmation_text should return confirmation description text."""
        mock_driver = Mock()
        page = CheckoutCompletePage(mock_driver)
        
        expected_text = "Your order has been dispatched"
        with patch.object(page, 'get_text', return_value=expected_text) as mock_get_text:
            result = page.get_confirmation_text()
            
            mock_get_text.assert_called_once_with(CheckoutCompletePage.COMPLETE_TEXT)
            assert result == expected_text


class TestClickBackHome:
    """Test click_back_home method."""
    
    def test_click_back_home_calls_click(self):
        """click_back_home should call click with BACK_HOME_BUTTON locator."""
        mock_driver = Mock()
        page = CheckoutCompletePage(mock_driver)
        
        with patch.object(page, 'click') as mock_click:
            page.click_back_home()
            
            mock_click.assert_called_once_with(CheckoutCompletePage.BACK_HOME_BUTTON)


class TestIsPonyExpressDisplayed:
    """Test is_pony_express_displayed method."""
    
    def test_is_pony_express_displayed_returns_true_when_image_present(self):
        """is_pony_express_displayed should return True when image exists."""
        mock_driver = Mock()
        page = CheckoutCompletePage(mock_driver)
        
        with patch.object(page, 'is_element_present', return_value=True) as mock_is_present:
            result = page.is_pony_express_displayed()
            
            mock_is_present.assert_called_once_with(CheckoutCompletePage.PONY_EXPRESS_IMAGE, timeout=2)
            assert result is True
    
    def test_is_pony_express_displayed_returns_false_when_image_not_present(self):
        """is_pony_express_displayed should return False when image doesn't exist."""
        mock_driver = Mock()
        page = CheckoutCompletePage(mock_driver)
        
        with patch.object(page, 'is_element_present', return_value=False):
            result = page.is_pony_express_displayed()
            
            assert result is False
