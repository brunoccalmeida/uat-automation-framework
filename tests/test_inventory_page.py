"""Unit tests for InventoryPage class.

Only what a real browser cannot check deterministically: logic (building
button IDs, parsing prices, detecting broken images, failing fast) and the
navigation wait contract. Locators and plain delegation to BasePage are
covered against the DOM by tests/integration/test_inventory_page_integration.py,
test_inventory_sorting_integration.py and test_product_details_integration.py
(#143). The sort dropdown reads (get_current_sort_option,
get_sort_dropdown_options) run against a real browser only in the E2E suite,
so their unit tests stay until an integration test covers them.
"""

from unittest.mock import Mock, patch

import pytest
from selenium.webdriver.common.by import By

from pages.inventory_page import InventoryPage
from tests.helpers.navigation_contract import assert_clicks_then_returns_loaded


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

    def test_get_current_sort_option_fails_clearly_without_a_value(self):
        """A selected option without value breaks the str contract: fail fast."""
        page = InventoryPage(Mock())
        mock_select = Mock()
        mock_select.first_selected_option.get_attribute.return_value = None

        with patch.object(page, "find_element"):
            with patch("pages.inventory_page.Select", return_value=mock_select):
                with pytest.raises(ValueError, match="no value"):
                    page.get_current_sort_option()


class TestAreProductImagesBroken:
    """Test are_product_images_broken method."""

    def test_are_product_images_broken_returns_true_when_all_broken(self):
        """are_product_images_broken is True when every image has the sl-404 src."""
        mock_driver = Mock()
        mock_img1 = Mock()
        mock_img1.get_attribute.return_value = "/static/media/sl-404.png"
        mock_img2 = Mock()
        mock_img2.get_attribute.return_value = "/static/media/sl-404.png"
        mock_driver.find_elements.return_value = [mock_img1, mock_img2]

        page = InventoryPage(mock_driver)
        result = page.are_product_images_broken()

        assert result is True

    def test_are_product_images_broken_returns_false_when_some_valid(self):
        """are_product_images_broken is False when at least one image is valid."""
        mock_driver = Mock()
        mock_img1 = Mock()
        mock_img1.get_attribute.return_value = "/static/media/sl-404.png"
        mock_img2 = Mock()
        mock_img2.get_attribute.return_value = "/static/media/backpack.jpg"
        mock_driver.find_elements.return_value = [mock_img1, mock_img2]

        page = InventoryPage(mock_driver)
        result = page.are_product_images_broken()

        assert result is False

    def test_are_product_images_broken_returns_false_when_an_image_has_no_src(self):
        """An image without src is not the sl-404 placeholder."""
        mock_driver = Mock()
        mock_img1 = Mock()
        mock_img1.get_attribute.return_value = "/static/media/sl-404.png"
        mock_img2 = Mock()
        mock_img2.get_attribute.return_value = None
        mock_driver.find_elements.return_value = [mock_img1, mock_img2]

        page = InventoryPage(mock_driver)
        result = page.are_product_images_broken()

        assert result is False

    def test_are_product_images_broken_returns_false_when_no_images(self):
        """are_product_images_broken should return False when no images found."""
        mock_driver = Mock()
        mock_driver.find_elements.return_value = []

        page = InventoryPage(mock_driver)
        result = page.are_product_images_broken()

        assert result is False


class TestGetSortDropdownOptions:
    """Test get_sort_dropdown_options method."""

    def test_get_sort_dropdown_options_returns_option_texts(self):
        """get_sort_dropdown_options should return list of visible option texts."""
        mock_driver = Mock()
        page = InventoryPage(mock_driver)

        mock_dropdown_element = Mock()
        mock_select = Mock()
        mock_opt1 = Mock(text="Name (A to Z)")
        mock_opt2 = Mock(text="Name (Z to A)")
        mock_select.options = [mock_opt1, mock_opt2]

        with patch.object(page, "find_element", return_value=mock_dropdown_element):
            with patch("pages.inventory_page.Select", return_value=mock_select):
                result = page.get_sort_dropdown_options()

                assert result == ["Name (A to Z)", "Name (Z to A)"]


class TestSortDropdownContainsOption:
    """Test sort_dropdown_contains_option method."""

    def test_sort_dropdown_contains_option_returns_true_when_present(self):
        """sort_dropdown_contains_option should return True when option exists."""
        mock_driver = Mock()
        page = InventoryPage(mock_driver)

        with patch.object(
            page,
            "get_sort_dropdown_options",
            return_value=["Name (A to Z)", "Price (low to high)"],
        ):
            result = page.sort_dropdown_contains_option("Name (A to Z)")

            assert result is True

    def test_sort_dropdown_contains_option_returns_false_when_absent(self):
        """sort_dropdown_contains_option is False for a missing option."""
        mock_driver = Mock()
        page = InventoryPage(mock_driver)

        with patch.object(
            page,
            "get_sort_dropdown_options",
            return_value=["Name (A to Z)", "Price (low to high)"],
        ):
            result = page.sort_dropdown_contains_option("Invalid Option")

            assert result is False


class TestRemoveProduct:
    """Test remove_product method."""

    def test_remove_product_clicks_the_product_remove_button(self):
        """remove_product should click the product's Remove button on this page."""
        page = InventoryPage(Mock())

        with patch.object(page, "click") as mock_click:
            page.remove_product("Sauce Labs Backpack")

        mock_click.assert_called_once_with((By.ID, "remove-sauce-labs-backpack"))


class TestOpenProductDetails:
    """Test open_product_details method."""

    def test_open_product_details_clicks_name_and_returns_loaded_details(self):
        """open_product_details clicks the title, returns loaded details."""
        page = InventoryPage(Mock())

        assert_clicks_then_returns_loaded(
            page,
            lambda: page.open_product_details("Backpack"),
            InventoryPage.product_name_locator("Backpack"),
            "pages.product_details_page.ProductDetailsPage",
        )
