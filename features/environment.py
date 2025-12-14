"""Behave environment configuration.

Manages test lifecycle hooks for Behave scenarios.
Handles WebDriver initialization and cleanup.
"""

from core.config import get_browser_config, load_config
from core.driver_manager import DriverManager


def before_all(context):
    """Initialize configuration before all tests.
    
    Args:
        context: Behave context object.
    """
    context.config_data = load_config("config.yaml")


def before_scenario(context, scenario):
    """Initialize WebDriver before each scenario.
    
    Args:
        context: Behave context object.
        scenario: Current scenario being executed.
    """
    browser_config = get_browser_config(context.config_data)
    context.driver_manager = DriverManager(browser_config)
    context.driver = context.driver_manager.get_driver()


def after_scenario(context, scenario):
    """Clean up WebDriver after each scenario.
    
    Args:
        context: Behave context object.
        scenario: Scenario that was executed.
    """
    if hasattr(context, 'driver_manager'):
        context.driver_manager.quit()
