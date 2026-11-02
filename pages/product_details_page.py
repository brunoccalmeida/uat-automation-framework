"""Product Details Page Object for Sauce Demo.

Represents the details page of a single product, opened from its card.
"""

from typing import NamedTuple

from selenium.webdriver.common.by import By

from pages import inventory_page
from pages.base_page import BasePage


class ProductInfo(NamedTuple):
    """Product data shown both on its card and on its details page."""

    name: str
    description: str
    price: str


class ProductDetailsPage(BasePage):
    """Page Object for Sauce Demo product details page."""

    # Locators
    DETAILS_CONTAINER = (By.CLASS_NAME, "inventory_details_container")
    PAGE_LOADED = DETAILS_CONTAINER
    PRODUCT_NAME = (By.CLASS_NAME, "inventory_details_name")
    PRODUCT_DESCRIPTION = (By.CLASS_NAME, "inventory_details_desc")
    PRODUCT_PRICE = (By.CLASS_NAME, "inventory_details_price")
    ADD_TO_CART_BUTTON = (By.ID, "add-to-cart")
    REMOVE_BUTTON = (By.ID, "remove")
    # Matches whichever of the two cart buttons is shown
    CART_BUTTON = (By.CSS_SELECTOR, ".inventory_details_desc_container button")
    BACK_BUTTON = (By.ID, "back-to-products")

    def get_name(self) -> str:
        """Get the displayed product name.

        Returns:
            Product name text.
        """
        return self.get_text(self.PRODUCT_NAME)

    def get_product_info(self) -> ProductInfo:
        """Get the displayed product name, description and price.

        Returns:
            ProductInfo, comparable with the card's (InventoryPage).
        """
        return ProductInfo(
            name=self.get_text(self.PRODUCT_NAME),
            description=self.get_text(self.PRODUCT_DESCRIPTION),
            price=self.get_text(self.PRODUCT_PRICE),
        )

    def has_description(self) -> bool:
        """Check if the product description is shown.

        Returns:
            True if the description becomes visible, False otherwise.
        """
        return self.is_element_visible(self.PRODUCT_DESCRIPTION)

    def get_cart_button_text(self) -> str:
        """Get the text of the cart button (Add to cart or Remove).

        Returns:
            Cart button text.
        """
        return self.get_text(self.CART_BUTTON)

    def add_to_cart(self) -> None:
        """Add the product to the cart.

        Returns once the Remove button is shown: the cart has changed only
        then, so a badge read right after sees the new count.
        """
        self.click(self.ADD_TO_CART_BUTTON)
        self.find_element(self.REMOVE_BUTTON)

    def remove_from_cart(self) -> None:
        """Remove the product from the cart.

        Returns once the Add to cart button is shown, as in add_to_cart.
        """
        self.click(self.REMOVE_BUTTON)
        self.find_element(self.ADD_TO_CART_BUTTON)

    def back_to_products(self) -> "inventory_page.InventoryPage":
        """Click Back to products.

        Returns:
            InventoryPage, once rendered.
        """
        self.click(self.BACK_BUTTON)
        return inventory_page.InventoryPage(self.driver).wait_until_loaded()
