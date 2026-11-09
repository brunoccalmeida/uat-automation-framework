"""DriverManager setup shared by the tests that open a real browser."""

from core.config import load_settings
from core.driver_manager import DriverManager


def make_driver_manager():
    """Build a DriverManager from the settings, as Behave does."""
    return DriverManager(load_settings().browser_config)
