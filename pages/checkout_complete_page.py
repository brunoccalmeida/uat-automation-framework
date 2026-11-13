"""Checkout Complete Page Object for Sauce Demo.

Represents the order confirmation page after successful checkout.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages import header_component, inventory_page
from pages.base_page import BasePage


class CheckoutCompletePage(BasePage):
    """Page Object for Sauce Demo checkout complete (confirmation) page."""

    # Locators
    CHECKOUT_COMPLETE_CONTAINER = (By.ID, "checkout_complete_container")
    PAGE_LOADED = CHECKOUT_COMPLETE_CONTAINER
    COMPLETE_HEADER = (By.CLASS_NAME, "complete-header")
    BACK_HOME_BUTTON = (By.ID, "back-to-products")

    def __init__(self, driver: WebDriver, timeout: int = 10):
        """Initialize the page and the header it includes.

        Args:
            driver: Selenium WebDriver instance.
            timeout: Default timeout for waiting operations.
        """
        super().__init__(driver, timeout)
        self.header = header_component.HeaderComponent(driver, timeout)

    def is_on_confirmation_page(self) -> bool:
        """Check if user is on order confirmation page.

        Returns:
            True if checkout complete container is present, False otherwise.
        """
        return self.is_element_visible(self.CHECKOUT_COMPLETE_CONTAINER, timeout=3)

    def get_confirmation_message(self) -> str:
        """Get order confirmation message.

        Returns:
            Confirmation header text.
        """
        return self.get_text(self.COMPLETE_HEADER)

    def click_back_home(self) -> "inventory_page.InventoryPage":
        """Click Back Home button to return to products page.

        Returns:
            InventoryPage, once rendered.
        """
        self.click(self.BACK_HOME_BUTTON)
        return inventory_page.InventoryPage(self.driver).wait_until_loaded()
