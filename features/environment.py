"""Behave environment configuration.

Manages test lifecycle hooks for Behave scenarios.
Handles WebDriver initialization and cleanup.
"""

import os

from core.config import get_browser_config, load_config
from core.config_resolver import apply_config_hierarchy
from core.driver_manager import DriverManager


def before_all(context):
    """Initialize configuration before all tests.

    Args:
        context: Behave context object.
    """
    context.config_data = load_config("config.yaml")


def before_scenario(context, scenario):
    """Initialize WebDriver before each scenario.

    Configuration hierarchy (highest to lowest priority):
    1. CLI parameter: -Dheadless=true
    2. Environment variable: HEADLESS=true
    3. Config file: config.yaml

    Browser selection hierarchy (highest to lowest priority):
    1. CLI parameter: -Dbrowser=firefox
    2. Environment variable: BROWSER=firefox
    3. Config file: config.yaml (browser.name)

    Args:
        context: Behave context object.
        scenario: Current scenario being executed.
    """
    browser_config = get_browser_config(context.config_data)

    # Apply configuration hierarchy for headless mode
    apply_config_hierarchy(
        config=browser_config,
        key="headless",
        cli_value=context.config.userdata.get("headless"),
        env_value=os.getenv("HEADLESS"),
    )

    # Apply configuration hierarchy for browser name
    apply_config_hierarchy(
        config=browser_config,
        key="name",
        cli_value=context.config.userdata.get("browser"),
        env_value=os.getenv("BROWSER"),
    )

    context.driver_manager = DriverManager(browser_config)
    context.driver = context.driver_manager.get_driver()


def after_scenario(context, scenario):
    """Clean up WebDriver after each scenario.

    Args:
        context: Behave context object.
        scenario: Scenario that was executed.
    """
    if hasattr(context, "driver_manager"):
        context.driver_manager.quit()
