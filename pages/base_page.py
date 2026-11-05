"""Base Page Object providing common functionality.

All page objects should inherit from this base class.
"""

from typing import Self

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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

    def wait_until_stable(self, locator: tuple[str, str]):
        """Wait until an element is visible and has stopped moving.

        An element that slides in (e.g. a menu) counts as visible and
        clickable while it still moves, so a click then may miss it. It is
        stable once its bounding box is the same on two consecutive polls,
        as in Playwright's "Stable" actionability check.

        Args:
            locator: Tuple of (By strategy, locator value).

        Returns:
            WebElement once visible and stable.

        Raises:
            TimeoutException: If element is not stable within timeout. The
                message says whether it was hidden at the end ("did not
                become visible") or still moving ("did not stop moving").
        """
        last_rect = None

        def has_stopped_moving(driver):
            nonlocal last_rect
            element = EC.visibility_of_element_located(locator)(driver)
            rect = element.rect if element else None
            stopped = rect is not None and rect == last_rect
            last_rect = rect
            return element if stopped else False

        try:
            return self.wait.until(
                has_stopped_moving, message=f"{locator} did not stop moving"
            )
        except TimeoutException as exc:
            # until() fixes its message before waiting; only the last poll
            # knows which of the two failures happened.
            if last_rect is None:
                raise TimeoutException(f"{locator} did not become visible") from exc
            raise

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
            self.wait.until(
                EC.invisibility_of_element_located(self.ERROR_MESSAGE),
                message=f"{self.ERROR_MESSAGE} did not disappear",
            )
        self.click(submit_button)
        self.wait.until(
            EC.any_of(
                EC.visibility_of_element_located(success_page.PAGE_LOADED),
                EC.visibility_of_element_located(self.ERROR_MESSAGE),
            ),
            message=f"Neither {success_page.__name__} nor error message rendered",
        )

    def accept_alert(self) -> str:
        """Wait for a JavaScript alert, accept it and return its text.

        The text is read before accepting: the alert closes on accept.

        Returns:
            Alert message text.

        Raises:
            TimeoutException: If no alert opens within timeout.
        """
        alert = self.wait.until(EC.alert_is_present(), message="No alert opened")
        text = alert.text
        alert.accept()
        return text

    def find_element(self, locator: tuple[str, str]):
        """Find visible element with explicit wait.

        Waits for visibility, not presence: an element can be in the DOM
        before it renders, and reading it then returns an intermediate state.

        Args:
            locator: Tuple of (By strategy, locator value).

        Returns:
            WebElement if found and visible.

        Raises:
            TimeoutException: If element not visible within timeout.
        """
        return self.wait.until(
            EC.visibility_of_element_located(locator),
            message=f"{locator} did not become visible",
        )

    def find_clickable_element(self, locator: tuple[str, str]):
        """Find clickable element with explicit wait.

        Args:
            locator: Tuple of (By strategy, locator value).

        Returns:
            WebElement if found and clickable.

        Raises:
            TimeoutException: If element not clickable within timeout.
        """
        return self.wait.until(
            EC.element_to_be_clickable(locator),
            message=f"{locator} did not become clickable",
        )

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
        self.wait.until(
            EC.element_to_be_clickable(locator),
            message=f"{locator} did not stay clickable after scrolling",
        )

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

    def is_element_visible(self, locator: tuple[str, str], timeout: int = 3) -> bool:
        """Check if element is visible on page.

        Args:
            locator: Tuple of (By strategy, locator value).
            timeout: Custom timeout for this check.

        Returns:
            True if element becomes visible within timeout, False otherwise.
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(
                EC.visibility_of_element_located(locator),
                message=f"{locator} did not become visible",
            )
            return True
        except TimeoutException:
            return False
