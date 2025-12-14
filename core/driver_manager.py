"""WebDriver management module.

Manages Selenium WebDriver lifecycle using OOP approach.
Handles browser initialization, configuration, and cleanup.
"""

from typing import Any

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.remote.webdriver import WebDriver


class DriverManager:
    """Manages WebDriver instances with proper lifecycle handling.
    
    Uses OOP pattern as WebDriver inherently maintains state and requires
    lifecycle management (initialization, usage, cleanup).
    """
    
    def __init__(self, browser_config: dict[str, Any]) -> None:
        """Initialize driver manager with browser configuration.
        
        Args:
            browser_config: Browser configuration from config.yaml.
        """
        self.browser_config = browser_config
        self._driver: WebDriver | None = None
    
    def get_driver(self) -> WebDriver:
        """Get or create WebDriver instance.
        
        Implements lazy initialization - driver is created only when needed.
        
        Returns:
            Configured WebDriver instance.
        """
        if self._driver is None:
            self._driver = self._create_driver()
        
        return self._driver
    
    def _create_driver(self) -> WebDriver:
        """Create and configure WebDriver instance.
        
        Returns:
            Configured WebDriver instance.
            
        Raises:
            ValueError: If unsupported browser is specified.
        """
        browser_name = self.browser_config.get("name", "chrome").lower()
        
        if browser_name == "chrome":
            return self._create_chrome_driver()
        else:
            raise ValueError(f"Unsupported browser: {browser_name}")
    
    def _create_chrome_driver(self) -> WebDriver:
        """Create Chrome WebDriver with configuration.
        
        Returns:
            Configured Chrome WebDriver.
        """
        options = ChromeOptions()
        
        # Apply headless mode if configured
        if self.browser_config.get("headless", False):
            options.add_argument("--headless=new")
        
        # Set window size
        window_size = self.browser_config.get("window_size", "1920,1080")
        options.add_argument(f"--window-size={window_size}")
        
        # Additional options for stability
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Evitar detecção de automação
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Disable autofill to prevent browser prompts
        options.add_experimental_option("prefs", {
            "autofill.profile_enabled": False,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        })
        
        # Create driver (Selenium Manager will handle driver binary)
        driver = webdriver.Chrome(options=options)
        
        # Maximize window for better visibility
        driver.maximize_window()
        
        return driver
    
    def quit(self) -> None:
        """Quit the WebDriver and clean up resources.
        
        Safe to call multiple times - only quits if driver exists.
        """
        if self._driver is not None:
            self._driver.quit()
            self._driver = None
