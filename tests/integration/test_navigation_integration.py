"""Integration tests for page navigation synchronization.

Sauce Demo is a SPA: the URL changes before the new page renders. Every
navigation method must return only after the destination is rendered, so
these tests read the DOM right after the call, without any wait.
"""

from pages.cart_page import CartPage
from pages.checkout_complete_page import CheckoutCompletePage
from pages.checkout_step_one_page import CheckoutStepOnePage
from pages.checkout_step_two_page import CheckoutStepTwoPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


def _go_to_cart(driver, base_url):
    """Log in, add a product and open the cart."""
    driver.get(base_url)
    LoginPage(driver).login("standard_user", "secret_sauce")
    inventory_page = InventoryPage(driver)
    inventory_page.add_product_to_cart("Sauce Labs Backpack")
    inventory_page.click_shopping_cart()


def _go_to_step_one(driver, base_url):
    """Open checkout step one with a product in the cart."""
    _go_to_cart(driver, base_url)
    CartPage(driver).click_checkout()


def _go_to_step_two(driver, base_url):
    """Open checkout step two (overview) with valid customer info."""
    _go_to_step_one(driver, base_url)
    step_one_page = CheckoutStepOnePage(driver)
    step_one_page.enter_first_name("John")
    step_one_page.enter_last_name("Doe")
    step_one_page.enter_zip_code("12345")
    step_one_page.click_continue()


class TestLoginNavigation:
    """Test login waits for its outcome."""

    def test_valid_login_returns_after_inventory_renders(self, driver, base_url):
        """Valid login should return only after inventory page renders."""
        driver.get(base_url)

        LoginPage(driver).login("standard_user", "secret_sauce")

        assert driver.find_elements(*InventoryPage.INVENTORY_CONTAINER)

    def test_invalid_login_returns_after_error_renders(self, driver, base_url):
        """Invalid login should return only after error message renders."""
        driver.get(base_url)

        LoginPage(driver).login("invalid_user", "wrong_password")

        assert driver.find_elements(*LoginPage.ERROR_MESSAGE)


class TestInventoryNavigation:
    """Test navigation methods on inventory page."""

    def test_logout_returns_loaded_login_page(self, driver, base_url):
        """logout should return LoginPage after it renders."""
        driver.get(base_url)
        LoginPage(driver).login("standard_user", "secret_sauce")

        next_page = InventoryPage(driver).logout()

        assert driver.find_elements(*LoginPage.LOGIN_BUTTON)
        assert isinstance(next_page, LoginPage)


class TestCartNavigation:
    """Test navigation methods on cart page."""

    def test_continue_shopping_returns_loaded_inventory_page(self, driver, base_url):
        """click_continue_shopping should return InventoryPage after it renders."""
        _go_to_cart(driver, base_url)

        next_page = CartPage(driver).click_continue_shopping()

        assert driver.find_elements(*InventoryPage.INVENTORY_CONTAINER)
        assert isinstance(next_page, InventoryPage)

    def test_checkout_returns_loaded_step_one_page(self, driver, base_url):
        """click_checkout should return CheckoutStepOnePage after it renders."""
        _go_to_cart(driver, base_url)

        next_page = CartPage(driver).click_checkout()

        assert driver.find_elements(*CheckoutStepOnePage.CHECKOUT_INFO_CONTAINER)
        assert isinstance(next_page, CheckoutStepOnePage)


class TestCheckoutStepOneNavigation:
    """Test navigation methods on checkout step one."""

    def test_continue_with_valid_info_returns_after_step_two_renders(
        self, driver, base_url
    ):
        """click_continue with valid info should return after step two renders."""
        _go_to_step_one(driver, base_url)
        step_one_page = CheckoutStepOnePage(driver)
        step_one_page.enter_first_name("John")
        step_one_page.enter_last_name("Doe")
        step_one_page.enter_zip_code("12345")

        step_one_page.click_continue()

        assert driver.find_elements(*CheckoutStepTwoPage.CHECKOUT_SUMMARY_CONTAINER)

    def test_continue_without_info_returns_after_error_renders(self, driver, base_url):
        """click_continue without info should return after error renders."""
        _go_to_step_one(driver, base_url)

        CheckoutStepOnePage(driver).click_continue()

        assert driver.find_elements(*CheckoutStepOnePage.ERROR_MESSAGE)

    def test_cancel_returns_loaded_cart_page(self, driver, base_url):
        """click_cancel should return CartPage after it renders."""
        _go_to_step_one(driver, base_url)

        next_page = CheckoutStepOnePage(driver).click_cancel()

        assert driver.find_elements(*CartPage.CART_CONTAINER)
        assert isinstance(next_page, CartPage)


class TestCheckoutStepTwoNavigation:
    """Test navigation methods on checkout step two."""

    def test_finish_returns_loaded_complete_page(self, driver, base_url):
        """click_finish should return CheckoutCompletePage after it renders."""
        _go_to_step_two(driver, base_url)

        next_page = CheckoutStepTwoPage(driver).click_finish()

        assert driver.find_elements(*CheckoutCompletePage.CHECKOUT_COMPLETE_CONTAINER)
        assert isinstance(next_page, CheckoutCompletePage)

    def test_cancel_returns_loaded_inventory_page(self, driver, base_url):
        """click_cancel should return InventoryPage after it renders."""
        _go_to_step_two(driver, base_url)

        next_page = CheckoutStepTwoPage(driver).click_cancel()

        assert driver.find_elements(*InventoryPage.INVENTORY_CONTAINER)
        assert isinstance(next_page, InventoryPage)


class TestCheckoutCompleteNavigation:
    """Test navigation methods on checkout complete page."""

    def test_back_home_returns_loaded_inventory_page(self, driver, base_url):
        """click_back_home should return InventoryPage after it renders."""
        _go_to_step_two(driver, base_url)
        CheckoutStepTwoPage(driver).click_finish()

        next_page = CheckoutCompletePage(driver).click_back_home()

        assert driver.find_elements(*InventoryPage.INVENTORY_CONTAINER)
        assert isinstance(next_page, InventoryPage)
