"""Unit tests for InventoryPage class.

Tests the InventoryPage Page Object in isolation using mocks.
"""

from unittest.mock import Mock, patch

from selenium.webdriver.common.by import By

from pages.inventory_page import InventoryPage


class TestInventoryPageLocators:
    """Test InventoryPage locator definitions."""

    def test_inventory_container_locator(self):
        """INVENTORY_CONTAINER locator should use correct ID."""
        assert InventoryPage.INVENTORY_CONTAINER == (By.ID, "inventory_container")

    def test_page_title_locator(self):
        """PAGE_TITLE locator should use correct class name."""
        assert InventoryPage.PAGE_TITLE == (By.CLASS_NAME, "title")

    def test_shopping_cart_badge_locator(self):
        """SHOPPING_CART_BADGE locator should use correct class name."""
        assert InventoryPage.SHOPPING_CART_BADGE == (
            By.CLASS_NAME,
            "shopping_cart_badge",
        )

    def test_shopping_cart_link_locator(self):
        """SHOPPING_CART_LINK locator should use correct class name."""
        assert InventoryPage.SHOPPING_CART_LINK == (By.CLASS_NAME, "shopping_cart_link")

    def test_sort_dropdown_locator(self):
        """SORT_DROPDOWN locator should use correct class name."""
        assert InventoryPage.SORT_DROPDOWN == (By.CLASS_NAME, "product_sort_container")


class TestIsOnInventoryPage:
    """Test is_on_inventory_page method."""

    def test_is_on_inventory_page_returns_true_when_container_present(self):
        """is_on_inventory_page should return True when inventory container exists."""
        mock_driver = Mock()
        page = InventoryPage(mock_driver)

        with patch.object(
            page, "is_element_present", return_value=True
        ) as mock_is_present:
            result = page.is_on_inventory_page()

            mock_is_present.assert_called_once_with(
                InventoryPage.INVENTORY_CONTAINER, timeout=3
            )
            assert result is True


class TestGetPageTitle:
    """Test get_page_title method."""

    def test_get_page_title_returns_text(self):
        """get_page_title should return page title text."""
        mock_driver = Mock()
        page = InventoryPage(mock_driver)

        with patch.object(page, "get_text", return_value="Products") as mock_get_text:
            result = page.get_page_title()

            mock_get_text.assert_called_once_with(InventoryPage.PAGE_TITLE)
            assert result == "Products"


class TestGetProductCount:
    """Test get_product_count method."""

    def test_get_product_count_returns_correct_count(self):
        """get_product_count should return number of product items."""
        mock_driver = Mock()
        mock_items = [Mock() for _ in range(6)]
        mock_driver.find_elements.return_value = mock_items

        page = InventoryPage(mock_driver)
        result = page.get_product_count()

        mock_driver.find_elements.assert_called_once_with(
            *InventoryPage.INVENTORY_ITEMS
        )
        assert result == 6


class TestAddProductToCart:
    """Test add_product_to_cart method."""

    def test_add_product_to_cart_converts_name_to_button_id(self):
        """add_product_to_cart should convert product name to button ID format."""
        mock_driver = Mock()
        page = InventoryPage(mock_driver)

        with patch.object(page, "click") as mock_click:
            page.add_product_to_cart("Sauce Labs Backpack")

            expected_locator = (By.ID, "add-to-cart-sauce-labs-backpack")
            mock_click.assert_called_once_with(expected_locator)


class TestGetCartItemCount:
    """Test get_cart_item_count method."""

    def test_get_cart_item_count_returns_badge_value_when_present(self):
        """get_cart_item_count should return badge number when badge exists."""
        mock_driver = Mock()
        page = InventoryPage(mock_driver)

        with patch.object(page, "is_element_present", return_value=True):
            with patch.object(page, "get_text", return_value="3"):
                result = page.get_cart_item_count()

                assert result == 3

    def test_get_cart_item_count_returns_zero_when_no_badge(self):
        """get_cart_item_count should return 0 when badge not present."""
        mock_driver = Mock()
        page = InventoryPage(mock_driver)

        with patch.object(page, "is_element_present", return_value=False):
            result = page.get_cart_item_count()

            assert result == 0


class TestClickShoppingCart:
    """Test click_shopping_cart method."""

    def test_click_shopping_cart_calls_click(self):
        """click_shopping_cart should call click with correct locator."""
        mock_driver = Mock()
        page = InventoryPage(mock_driver)

        with patch.object(page, "click") as mock_click:
            page.click_shopping_cart()

            mock_click.assert_called_once_with(InventoryPage.SHOPPING_CART_LINK)


class TestLogout:
    """Test logout method."""

    def test_logout_clicks_menu_then_logout_link(self):
        """logout should click menu button then logout link."""
        mock_driver = Mock()
        page = InventoryPage(mock_driver)

        with patch.object(page, "click") as mock_click:
            page.logout()

            assert mock_click.call_count == 2


class TestSelectSortOption:
    """Test select_sort_option method."""

    def test_select_sort_option_selects_by_value(self):
        """select_sort_option should select dropdown option by value."""
        mock_driver = Mock()
        page = InventoryPage(mock_driver)

        mock_dropdown_element = Mock()
        mock_select = Mock()

        with patch.object(
            page, "find_clickable_element", return_value=mock_dropdown_element
        ):
            with patch("pages.inventory_page.Select", return_value=mock_select):
                page.select_sort_option("za")

                mock_select.select_by_value.assert_called_once_with("za")


class TestGetProductNames:
    """Test get_product_names method."""

    def test_get_product_names_returns_list_of_names(self):
        """get_product_names should return list of product names in order."""
        mock_driver = Mock()
        mock_elements = [Mock(text="Product A"), Mock(text="Product B")]
        mock_driver.find_elements.return_value = mock_elements

        page = InventoryPage(mock_driver)
        result = page.get_product_names()

        mock_driver.find_elements.assert_called_once_with(
            *InventoryPage.INVENTORY_ITEM_NAME
        )
        assert result == ["Product A", "Product B"]


class TestGetProductPrices:
    """Test get_product_prices method."""

    def test_get_product_prices_returns_list_of_floats(self):
        """get_product_prices should return list of prices as floats."""
        mock_driver = Mock()
        mock_elements = [Mock(text="$29.99"), Mock(text="$15.99")]
        mock_driver.find_elements.return_value = mock_elements

        page = InventoryPage(mock_driver)
        result = page.get_product_prices()

        mock_driver.find_elements.assert_called_once_with(
            *InventoryPage.INVENTORY_ITEM_PRICE
        )
        assert result == [29.99, 15.99]


class TestGetCurrentSortOption:
    """Test get_current_sort_option method."""

    def test_get_current_sort_option_returns_selected_value(self):
        """get_current_sort_option should return value of selected option."""
        mock_driver = Mock()
        page = InventoryPage(mock_driver)

        mock_dropdown_element = Mock()
        mock_select = Mock()
        mock_option = Mock()
        mock_option.get_attribute.return_value = "lohi"
        mock_select.first_selected_option = mock_option

        with patch.object(page, "find_element", return_value=mock_dropdown_element):
            with patch("pages.inventory_page.Select", return_value=mock_select):
                result = page.get_current_sort_option()

                mock_option.get_attribute.assert_called_once_with("value")
                assert result == "lohi"
