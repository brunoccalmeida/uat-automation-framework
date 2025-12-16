"""Unit tests for CartPage class.

Tests the CartPage Page Object in isolation using mocks.
"""

from unittest.mock import Mock, patch

from selenium.webdriver.common.by import By

from pages.cart_page import CartPage


class TestCartPageLocators:
    """Test CartPage locator definitions."""
    
    def test_cart_container_locator(self):
        """CART_CONTAINER locator should use correct ID."""
        assert CartPage.CART_CONTAINER == (By.ID, "cart_contents_container")
    
    def test_cart_items_locator(self):
        """CART_ITEMS locator should use correct class name."""
        assert CartPage.CART_ITEMS == (By.CLASS_NAME, "cart_item")
    
    def test_cart_item_name_locator(self):
        """CART_ITEM_NAME locator should use correct class name."""
        assert CartPage.CART_ITEM_NAME == (By.CLASS_NAME, "inventory_item_name")
    
    def test_continue_shopping_button_locator(self):
        """CONTINUE_SHOPPING_BUTTON locator should use correct ID."""
        assert CartPage.CONTINUE_SHOPPING_BUTTON == (By.ID, "continue-shopping")
    
    def test_checkout_button_locator(self):
        """CHECKOUT_BUTTON locator should use correct ID."""
        assert CartPage.CHECKOUT_BUTTON == (By.ID, "checkout")


class TestIsOnCartPage:
    """Test is_on_cart_page method."""
    
    def test_is_on_cart_page_returns_true_when_container_present(self):
        """is_on_cart_page should return True when cart container exists."""
        mock_driver = Mock()
        page = CartPage(mock_driver)
        
        with patch.object(page, 'is_element_present', return_value=True) as mock_is_present:
            result = page.is_on_cart_page()
            
            mock_is_present.assert_called_once_with(CartPage.CART_CONTAINER, timeout=3)
            assert result is True
    
    def test_is_on_cart_page_returns_false_when_container_not_present(self):
        """is_on_cart_page should return False when cart container doesn't exist."""
        mock_driver = Mock()
        page = CartPage(mock_driver)
        
        with patch.object(page, 'is_element_present', return_value=False):
            result = page.is_on_cart_page()
            
            assert result is False


class TestGetCartItemCount:
    """Test get_cart_item_count method."""
    
    def test_get_cart_item_count_returns_correct_count(self):
        """get_cart_item_count should return number of cart items."""
        mock_driver = Mock()
        mock_items = [Mock(), Mock(), Mock()]
        mock_driver.find_elements.return_value = mock_items
        
        page = CartPage(mock_driver)
        result = page.get_cart_item_count()
        
        mock_driver.find_elements.assert_called_once_with(*CartPage.CART_ITEMS)
        assert result == 3


class TestIsProductInCart:
    """Test is_product_in_cart method."""
    
    def test_is_product_in_cart_returns_true_when_product_found(self):
        """is_product_in_cart should return True when product name matches."""
        mock_driver = Mock()
        mock_item = Mock()
        mock_item.text = "Sauce Labs Backpack"
        mock_driver.find_elements.return_value = [mock_item]
        
        page = CartPage(mock_driver)
        result = page.is_product_in_cart("Sauce Labs Backpack")
        
        assert result is True
    
    def test_is_product_in_cart_returns_false_when_product_not_found(self):
        """is_product_in_cart should return False when product not in cart."""
        mock_driver = Mock()
        mock_item = Mock()
        mock_item.text = "Sauce Labs Backpack"
        mock_driver.find_elements.return_value = [mock_item]
        
        page = CartPage(mock_driver)
        result = page.is_product_in_cart("Different Product")
        
        assert result is False


class TestRemoveProduct:
    """Test remove_product method."""
    
    def test_remove_product_converts_name_to_button_id(self):
        """remove_product should convert product name to button ID format."""
        mock_driver = Mock()
        page = CartPage(mock_driver)
        
        with patch.object(page, 'click') as mock_click:
            page.remove_product("Sauce Labs Backpack")
            
            expected_locator = (By.ID, "remove-sauce-labs-backpack")
            mock_click.assert_called_once_with(expected_locator)


class TestClickContinueShopping:
    """Test click_continue_shopping method."""
    
    def test_click_continue_shopping_calls_click(self):
        """click_continue_shopping should call click with correct locator."""
        mock_driver = Mock()
        page = CartPage(mock_driver)
        
        with patch.object(page, 'click') as mock_click:
            page.click_continue_shopping()
            
            mock_click.assert_called_once_with(CartPage.CONTINUE_SHOPPING_BUTTON)


class TestClickCheckout:
    """Test click_checkout method."""
    
    def test_click_checkout_calls_click(self):
        """click_checkout should call click with correct locator."""
        mock_driver = Mock()
        page = CartPage(mock_driver)
        
        with patch.object(page, 'click') as mock_click:
            page.click_checkout()
            
            mock_click.assert_called_once_with(CartPage.CHECKOUT_BUTTON)
