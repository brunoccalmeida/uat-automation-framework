"""Unit tests for ProductDetailsPage class.

Tests the ProductDetailsPage Page Object in isolation using mocks.
"""

from unittest.mock import Mock, patch

import pytest
from selenium.webdriver.common.by import By

from pages.product_details_page import ProductDetailsPage, ProductInfo
from tests.helpers.navigation_contract import assert_clicks_then_returns_loaded


class TestProductDetailsPageLocators:
    """Test ProductDetailsPage locator definitions."""

    def test_page_loaded_is_details_container(self):
        """PAGE_LOADED should be the details container."""
        assert ProductDetailsPage.PAGE_LOADED == (
            By.CLASS_NAME,
            "inventory_details_container",
        )

    def test_product_name_locator(self):
        """PRODUCT_NAME locator should use the details name class."""
        assert ProductDetailsPage.PRODUCT_NAME == (
            By.CLASS_NAME,
            "inventory_details_name",
        )

    def test_product_description_locator(self):
        """PRODUCT_DESCRIPTION locator should use the details description class."""
        assert ProductDetailsPage.PRODUCT_DESCRIPTION == (
            By.CLASS_NAME,
            "inventory_details_desc",
        )

    def test_product_price_locator(self):
        """PRODUCT_PRICE locator should use the details price class."""
        assert ProductDetailsPage.PRODUCT_PRICE == (
            By.CLASS_NAME,
            "inventory_details_price",
        )

    def test_cart_buttons_locators(self):
        """Add and remove buttons should use their IDs."""
        assert ProductDetailsPage.ADD_TO_CART_BUTTON == (By.ID, "add-to-cart")
        assert ProductDetailsPage.REMOVE_BUTTON == (By.ID, "remove")

    def test_cart_button_locator(self):
        """CART_BUTTON should match whichever cart button is shown."""
        assert ProductDetailsPage.CART_BUTTON == (
            By.CSS_SELECTOR,
            ".inventory_details_desc_container button",
        )

    def test_back_button_locator(self):
        """BACK_BUTTON locator should use correct ID."""
        assert ProductDetailsPage.BACK_BUTTON == (By.ID, "back-to-products")


class TestReadProduct:
    """Test methods that read the displayed product."""

    def test_get_name_reads_product_name(self):
        """get_name should return the product name text."""
        page = ProductDetailsPage(Mock())

        with patch.object(page, "get_text", return_value="Backpack") as mock_text:
            assert page.get_name() == "Backpack"

        mock_text.assert_called_once_with(ProductDetailsPage.PRODUCT_NAME)

    def test_get_product_info_reads_name_description_and_price(self):
        """get_product_info should return name, description and price."""
        page = ProductDetailsPage(Mock())
        texts = {
            ProductDetailsPage.PRODUCT_NAME: "Backpack",
            ProductDetailsPage.PRODUCT_DESCRIPTION: "Sleek pack",
            ProductDetailsPage.PRODUCT_PRICE: "$29.99",
        }

        with patch.object(page, "get_text", side_effect=texts.__getitem__):
            result = page.get_product_info()

        assert result == ProductInfo("Backpack", "Sleek pack", "$29.99")

    @pytest.mark.parametrize("visible", [True, False])
    def test_has_description_reflects_visibility(self, visible):
        """has_description should return whether the description is visible."""
        page = ProductDetailsPage(Mock())

        with patch.object(
            page, "is_element_visible", return_value=visible
        ) as mock_visible:
            assert page.has_description() is visible

        mock_visible.assert_called_once_with(ProductDetailsPage.PRODUCT_DESCRIPTION)

    def test_get_cart_button_text_reads_cart_button(self):
        """get_cart_button_text should return the cart button text."""
        page = ProductDetailsPage(Mock())

        with patch.object(page, "get_text", return_value="Remove") as mock_text:
            assert page.get_cart_button_text() == "Remove"

        mock_text.assert_called_once_with(ProductDetailsPage.CART_BUTTON)


class TestCartButtons:
    """Test add and remove: click, then wait for the opposite button."""

    @pytest.mark.parametrize(
        ("method", "clicked", "awaited"),
        [
            (
                "add_to_cart",
                ProductDetailsPage.ADD_TO_CART_BUTTON,
                ProductDetailsPage.REMOVE_BUTTON,
            ),
            (
                "remove_from_cart",
                ProductDetailsPage.REMOVE_BUTTON,
                ProductDetailsPage.ADD_TO_CART_BUTTON,
            ),
        ],
    )
    def test_clicks_then_waits_for_opposite_button(self, method, clicked, awaited):
        """The cart state changed only once the opposite button is shown."""
        page = ProductDetailsPage(Mock())

        with (
            patch.object(page, "click") as mock_click,
            patch.object(page, "find_element") as mock_find,
        ):
            calls = Mock()
            calls.attach_mock(mock_click, "click")
            calls.attach_mock(mock_find, "find_element")
            getattr(page, method)()

        assert calls.mock_calls == [
            ("click", (clicked,), {}),
            ("find_element", (awaited,), {}),
        ]


class TestBackToProducts:
    """Test back_to_products method."""

    def test_back_to_products_clicks_and_returns_loaded_inventory_page(self):
        """back_to_products clicks the button, returns a loaded InventoryPage."""
        page = ProductDetailsPage(Mock())

        assert_clicks_then_returns_loaded(
            page,
            page.back_to_products,
            ProductDetailsPage.BACK_BUTTON,
            "pages.inventory_page.InventoryPage",
        )
