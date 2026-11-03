"""Integration tests for ProductDetailsPage with real browser.

Tests ProductDetailsPage interactions with actual DOM elements.
"""

import pytest

from pages.inventory_page import InventoryPage
from pages.product_details_page import ProductDetailsPage, ProductInfo
from tests.helpers.navigation import go_to_inventory

BACKPACK = "Sauce Labs Backpack"


@pytest.fixture(name="backpack_details")
def fixture_backpack_details(authenticated_driver):
    """Backpack details page, opened from its card as standard_user."""
    return InventoryPage(authenticated_driver).open_product_details(BACKPACK)


class TestOpenProductDetails:
    """Test opening details from the inventory page."""

    def test_get_product_card_reads_the_named_card(self, authenticated_driver):
        """get_product_card reads the card of the given product, not the first."""
        card = InventoryPage(authenticated_driver).get_product_card(
            "Sauce Labs Bike Light"
        )

        assert card.name == "Sauce Labs Bike Light"
        assert card.price == "$9.99"
        assert card.description.startswith("A red light")

    def test_details_match_the_card_that_was_opened(self, authenticated_driver):
        """Details show the same name, description and price as the card."""
        inventory = InventoryPage(authenticated_driver)
        card = inventory.get_product_card(BACKPACK)

        details = inventory.open_product_details(BACKPACK)

        assert isinstance(details, ProductDetailsPage)
        assert details.get_product_info() == card

    def test_name_locator_does_not_match_a_longer_name(self, authenticated_driver):
        """A name that is a prefix of another product's name matches nothing."""
        page = InventoryPage(authenticated_driver)

        assert not page.is_element_visible(page.product_name_locator("Sauce Labs"))


class TestProductDetailsReads:
    """Test reading the displayed product."""

    def test_get_product_info_returns_displayed_product(self, backpack_details):
        """get_product_info returns the displayed product."""
        info = backpack_details.get_product_info()

        assert isinstance(info, ProductInfo)
        assert (info.name, info.price) == (BACKPACK, "$29.99")

    def test_has_description_is_true_for_standard_user(self, backpack_details):
        """standard_user sees the description."""
        assert backpack_details.has_description()

    def test_has_description_is_false_for_error_user(self, driver, base_url):
        """error_user's details page has no description (known defect)."""
        go_to_inventory(driver, base_url, "error_user")

        details = InventoryPage(driver).open_product_details(BACKPACK)

        assert details.get_name() == BACKPACK
        assert not details.has_description()


class TestProductDetailsCart:
    """Test the cart button and navigation back."""

    def test_add_to_cart_shows_remove_and_updates_badge(self, backpack_details):
        """Adding switches the button to Remove; the badge counts it."""
        backpack_details.add_to_cart()

        assert backpack_details.get_cart_button_text() == "Remove"
        assert backpack_details.header.get_cart_item_count() == 1

    def test_remove_from_cart_shows_add_to_cart(self, backpack_details):
        """Removing switches the button back to Add to cart."""
        backpack_details.add_to_cart()

        backpack_details.remove_from_cart()

        assert backpack_details.get_cart_button_text() == "Add to cart"

    def test_back_to_products_returns_loaded_inventory(self, backpack_details):
        """Back to products returns the inventory page, cart kept."""
        backpack_details.add_to_cart()

        inventory = backpack_details.back_to_products()

        assert isinstance(inventory, InventoryPage)
        assert inventory.is_on_inventory_page()
        assert inventory.header.get_cart_item_count() == 1
