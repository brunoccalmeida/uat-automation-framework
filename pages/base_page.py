"""Base Page Object providing common functionality.

All page objects should inherit from this base class.
"""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class BasePage:
    """Base class for all page objects.
    
    Provides common methods for interacting with web pages.
    """
    
    def __init__(self, driver: WebDriver, timeout: int = 10):
        """Initialize base page.
        
        Args:
            driver: Selenium WebDriver instance.
            timeout: Default timeout for waiting operations.
        """
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)
    
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
        """Type text into element.
        
        Args:
            locator: Tuple of (By strategy, locator value).
            text: Text to type.
        """
        element = self.find_element(locator)
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
