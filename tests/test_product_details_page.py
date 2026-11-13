"""Unit tests for ProductDetailsPage class.

Only the wait contracts a real browser cannot check deterministically:
add and remove wait for the opposite button, and going back waits for the
inventory. Locators and reads are covered against the DOM by
tests/integration/test_product_details_integration.py (#143).
"""

from unittest.mock import Mock, patch

import pytest

from pages.product_details_page import ProductDetailsPage
from tests.helpers.navigation_contract import assert_clicks_then_returns_loaded


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
