"""Base Page Object providing common functionality.

All page objects should inherit from this base class.
"""

from typing import Self

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class BasePage:
    """Base class for all page objects.

    Provides common methods for interacting with web pages.

    Subclasses define PAGE_LOADED: a locator unique to the page, visible once
    the page has rendered. Sauce Demo is a SPA, so the URL changes before the
    new page renders; navigation methods must wait for the destination's
    PAGE_LOADED before returning.

    Form pages whose submit may fail validation also define ERROR_MESSAGE and
    ERROR_CLOSE_BUTTON, and submit through submit_and_wait_for_outcome.
    """

    PAGE_LOADED: tuple[str, str]
    ERROR_MESSAGE: tuple[str, str]
    ERROR_CLOSE_BUTTON: tuple[str, str]

    def __init__(self, driver: WebDriver, timeout: int = 10):
        """Initialize base page.

        Args:
            driver: Selenium WebDriver instance.
            timeout: Default timeout for waiting operations.
        """
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def wait_until_loaded(self) -> Self:
        """Wait until this page has rendered.

        Returns:
            This page object, for chaining from navigation methods.

        Raises:
            TimeoutException: If page does not render within timeout.
        """
        self.wait.until(
            EC.visibility_of_element_located(self.PAGE_LOADED),
            message=f"{type(self).__name__} did not render",
        )
        return self

    def submit_and_wait_for_outcome(
        self, submit_button: tuple[str, str], success_page: type["BasePage"]
    ) -> None:
        """Submit a form and wait for its outcome: success page or error.

        Sauce Demo keeps the same error banner on screen when a resubmit fails
        again, so a leftover banner would look like the new outcome. It is
        dismissed first, making any error after the click belong to this submit.

        Args:
            submit_button: Locator of the button that submits the form.
            success_page: Page object class shown when the submit succeeds.

        Raises:
            TimeoutException: If neither outcome renders within timeout.
        """
        if self.driver.find_elements(*self.ERROR_MESSAGE):
            self.click(self.ERROR_CLOSE_BUTTON)
            self.wait.until(EC.invisibility_of_element_located(self.ERROR_MESSAGE))
        self.click(submit_button)
        self.wait.until(
            EC.any_of(
                EC.visibility_of_element_located(success_page.PAGE_LOADED),
                EC.visibility_of_element_located(self.ERROR_MESSAGE),
            ),
            message=f"Neither {success_page.__name__} nor error message rendered",
        )

    def find_element(self, locator: tuple[str, str]):
        """Find element with explicit wait.

        Args:
            locator: Tuple of (By strategy, locator value).

        Returns:
            WebElement if found.

        Raises:
            TimeoutException: If element not found within timeout.
        """
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_clickable_element(self, locator: tuple[str, str]):
        """Find clickable element with explicit wait.

        Args:
            locator: Tuple of (By strategy, locator value).

        Returns:
            WebElement if found and clickable.

        Raises:
            TimeoutException: If element not clickable within timeout.
        """
        return self.wait.until(EC.element_to_be_clickable(locator))

    def click(self, locator: tuple[str, str]) -> None:
        """Click element after ensuring it's clickable.

        Args:
            locator: Tuple of (By strategy, locator value).
        """
        element = self.find_clickable_element(locator)
        element.click()

    def type(self, locator: tuple[str, str], text: str) -> None:
        """Type text into element using explicit waits.

        Args:
            locator: Tuple of (By strategy, locator value).
            text: Text to type.
        """
        # First wait for element to be clickable
        element = self.find_clickable_element(locator)

        # Verify element is not obscured using JavaScript
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )

        # Double-check element is still interactable after scroll
        self.wait.until(EC.element_to_be_clickable(locator))

        # Now safe to interact
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple[str, str]) -> str:
        """Get text from element.

        Args:
            locator: Tuple of (By strategy, locator value).

        Returns:
            Text content of element.
        """
        element = self.find_element(locator)
        return element.text

    def is_element_present(self, locator: tuple[str, str], timeout: int = 3) -> bool:
        """Check if element is present on page.

        Args:
            locator: Tuple of (By strategy, locator value).
            timeout: Custom timeout for this check.

        Returns:
            True if element is present, False otherwise.
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False
