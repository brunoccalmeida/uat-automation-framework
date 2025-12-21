"""Unit tests for DriverManager class.

Tests WebDriver creation and configuration in isolation using mocks.
"""

from unittest.mock import Mock, patch

import pytest

from core.driver_manager import DriverManager


class TestDriverManagerInit:
    """Test DriverManager initialization."""

    def test_init_stores_browser_config(self):
        """DriverManager should store browser config on initialization."""
        browser_config = {"name": "chrome", "headless": True}
        manager = DriverManager(browser_config)

        assert manager.browser_config == browser_config
        assert manager._driver is None


class TestGetDriver:
    """Test get_driver method (lazy initialization)."""

    def test_get_driver_creates_driver_on_first_call(self):
        """get_driver should create driver on first call."""
        browser_config = {"name": "chrome", "headless": False}
        manager = DriverManager(browser_config)

        with patch.object(manager, "_create_driver") as mock_create:
            mock_driver = Mock()
            mock_create.return_value = mock_driver

            result = manager.get_driver()

            mock_create.assert_called_once()
            assert result == mock_driver

    def test_get_driver_reuses_existing_driver(self):
        """get_driver should reuse existing driver on subsequent calls."""
        browser_config = {"name": "chrome", "headless": False}
        manager = DriverManager(browser_config)

        with patch.object(manager, "_create_driver") as mock_create:
            mock_driver = Mock()
            mock_create.return_value = mock_driver

            # First call creates driver
            first_result = manager.get_driver()
            # Second call should reuse
            second_result = manager.get_driver()

            mock_create.assert_called_once()  # Only one creation
            assert first_result == second_result


class TestCreateDriver:
    """Test _create_driver method (browser routing)."""

    def test_create_driver_calls_chrome_for_chrome_browser(self):
        """_create_driver should route to Chrome for 'chrome' config."""
        browser_config = {"name": "chrome"}
        manager = DriverManager(browser_config)

        with patch.object(manager, "_create_chrome_driver") as mock_chrome:
            mock_driver = Mock()
            mock_chrome.return_value = mock_driver

            result = manager._create_driver()

            mock_chrome.assert_called_once()
            assert result == mock_driver

    def test_create_driver_calls_firefox_for_firefox_browser(self):
        """_create_driver should route to Firefox for 'firefox' config."""
        browser_config = {"name": "firefox"}
        manager = DriverManager(browser_config)

        with patch.object(manager, "_create_firefox_driver") as mock_firefox:
            mock_driver = Mock()
            mock_firefox.return_value = mock_driver

            result = manager._create_driver()

            mock_firefox.assert_called_once()
            assert result == mock_driver

    def test_create_driver_defaults_to_chrome_when_name_missing(self):
        """_create_driver should default to Chrome when 'name' not in config."""
        browser_config = {}  # No 'name' key
        manager = DriverManager(browser_config)

        with patch.object(manager, "_create_chrome_driver") as mock_chrome:
            mock_driver = Mock()
            mock_chrome.return_value = mock_driver

            result = manager._create_driver()

            mock_chrome.assert_called_once()
            assert result == mock_driver

    def test_create_driver_raises_for_unsupported_browser(self):
        """_create_driver should raise ValueError for unsupported browsers."""
        browser_config = {"name": "safari"}
        manager = DriverManager(browser_config)

        with pytest.raises(ValueError, match="Unsupported browser: safari"):
            manager._create_driver()


class TestCreateChromeDriver:
    """Test _create_chrome_driver method."""

    def test_create_chrome_driver_applies_headless_mode(self):
        """_create_chrome_driver should add headless argument when configured."""
        browser_config = {"name": "chrome", "headless": True}
        manager = DriverManager(browser_config)

        with patch("core.driver_manager.webdriver.Chrome") as mock_chrome:
            with patch("core.driver_manager.ChromeOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options
                mock_driver = Mock()
                mock_chrome.return_value = mock_driver

                manager._create_chrome_driver()

                # Verify headless argument was added
                mock_options.add_argument.assert_any_call("--headless=new")

    def test_create_chrome_driver_skips_headless_when_false(self):
        """_create_chrome_driver should not add headless when headless=False."""
        browser_config = {"name": "chrome", "headless": False}
        manager = DriverManager(browser_config)

        with patch("core.driver_manager.webdriver.Chrome") as mock_chrome:
            with patch("core.driver_manager.ChromeOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options
                mock_driver = Mock()
                mock_chrome.return_value = mock_driver

                manager._create_chrome_driver()

                # Verify headless was NOT added
                headless_calls = [
                    call
                    for call in mock_options.add_argument.call_args_list
                    if "headless" in str(call)
                ]
                assert len(headless_calls) == 0

    def test_create_chrome_driver_sets_custom_window_size(self):
        """_create_chrome_driver should use custom window size when configured."""
        browser_config = {"name": "chrome", "window_size": "1280,720"}
        manager = DriverManager(browser_config)

        with patch("core.driver_manager.webdriver.Chrome") as mock_chrome:
            with patch("core.driver_manager.ChromeOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options
                mock_driver = Mock()
                mock_chrome.return_value = mock_driver

                manager._create_chrome_driver()

                mock_options.add_argument.assert_any_call("--window-size=1280,720")

    def test_create_chrome_driver_uses_default_window_size(self):
        """_create_chrome_driver should use default 1920x1080 when not configured."""
        browser_config = {"name": "chrome"}
        manager = DriverManager(browser_config)

        with patch("core.driver_manager.webdriver.Chrome") as mock_chrome:
            with patch("core.driver_manager.ChromeOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options
                mock_driver = Mock()
                mock_chrome.return_value = mock_driver

                manager._create_chrome_driver()

                mock_options.add_argument.assert_any_call("--window-size=1920,1080")


class TestCreateFirefoxDriver:
    """Test _create_firefox_driver method."""

    def test_create_firefox_driver_applies_headless_mode(self):
        """_create_firefox_driver should add headless argument when configured."""
        browser_config = {"name": "firefox", "headless": True}
        manager = DriverManager(browser_config)

        with patch("core.driver_manager.webdriver.Firefox") as mock_firefox:
            with patch("core.driver_manager.FirefoxOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options
                mock_driver = Mock()
                mock_firefox.return_value = mock_driver

                manager._create_firefox_driver()

                mock_options.add_argument.assert_any_call("--headless")

    def test_create_firefox_driver_skips_headless_when_false(self):
        """_create_firefox_driver should not add headless when headless=False."""
        browser_config = {"name": "firefox", "headless": False}
        manager = DriverManager(browser_config)

        with patch("core.driver_manager.webdriver.Firefox") as mock_firefox:
            with patch("core.driver_manager.FirefoxOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options
                mock_driver = Mock()
                mock_firefox.return_value = mock_driver

                manager._create_firefox_driver()

                # Verify headless was NOT added
                headless_calls = [
                    call
                    for call in mock_options.add_argument.call_args_list
                    if "headless" in str(call)
                ]
                assert len(headless_calls) == 0

    def test_create_firefox_driver_sets_custom_window_size(self):
        """_create_firefox_driver should use custom window size when configured."""
        browser_config = {"name": "firefox", "window_size": "1280,720"}
        manager = DriverManager(browser_config)

        with patch("core.driver_manager.webdriver.Firefox") as mock_firefox:
            with patch("core.driver_manager.FirefoxOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options
                mock_driver = Mock()
                mock_firefox.return_value = mock_driver

                manager._create_firefox_driver()

                mock_options.add_argument.assert_any_call("--width=1280")
                mock_options.add_argument.assert_any_call("--height=720")

    def test_create_firefox_driver_uses_default_window_size(self):
        """_create_firefox_driver should use default 1920x1080 when not configured."""
        browser_config = {"name": "firefox"}
        manager = DriverManager(browser_config)

        with patch("core.driver_manager.webdriver.Firefox") as mock_firefox:
            with patch("core.driver_manager.FirefoxOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options
                mock_driver = Mock()
                mock_firefox.return_value = mock_driver

                manager._create_firefox_driver()

                mock_options.add_argument.assert_any_call("--width=1920")
                mock_options.add_argument.assert_any_call("--height=1080")

    def test_create_firefox_driver_disables_notifications(self):
        """_create_firefox_driver should disable web notifications."""
        browser_config = {"name": "firefox"}
        manager = DriverManager(browser_config)

        with patch("core.driver_manager.webdriver.Firefox") as mock_firefox:
            with patch("core.driver_manager.FirefoxOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options
                mock_driver = Mock()
                mock_firefox.return_value = mock_driver

                manager._create_firefox_driver()

                mock_options.set_preference.assert_any_call(
                    "dom.webnotifications.enabled", False
                )

    def test_create_firefox_driver_disables_password_autofill(self):
        """_create_firefox_driver should disable password autofill."""
        browser_config = {"name": "firefox"}
        manager = DriverManager(browser_config)

        with patch("core.driver_manager.webdriver.Firefox") as mock_firefox:
            with patch("core.driver_manager.FirefoxOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options
                mock_driver = Mock()
                mock_firefox.return_value = mock_driver

                manager._create_firefox_driver()

                mock_options.set_preference.assert_any_call(
                    "signon.rememberSignons", False
                )
                mock_options.set_preference.assert_any_call(
                    "signon.autofillForms", False
                )


class TestQuit:
    """Test quit method."""

    def test_quit_calls_driver_quit_when_driver_exists(self):
        """quit should call driver.quit() when driver exists."""
        browser_config = {"name": "chrome"}
        manager = DriverManager(browser_config)

        mock_driver = Mock()
        manager._driver = mock_driver

        manager.quit()

        mock_driver.quit.assert_called_once()
        assert manager._driver is None

    def test_quit_does_nothing_when_driver_is_none(self):
        """quit should safely do nothing when driver is None."""
        browser_config = {"name": "chrome"}
        manager = DriverManager(browser_config)

        # Should not raise exception
        manager.quit()

        assert manager._driver is None
