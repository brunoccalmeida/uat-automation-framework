"""Behave environment configuration.

Manages test lifecycle hooks for Behave scenarios.
Handles WebDriver initialization and cleanup.
"""

import os

import allure

from core.config import get_browser_config, load_config
from core.config_resolver import apply_config_hierarchy
from core.driver_manager import DriverManager


def before_all(context):
    """Initialize configuration before all tests.

    Args:
        context: Behave context object.
    """
    context.config_data = load_config("config.yaml")


def before_scenario(context, _scenario):
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
        _scenario: Current scenario being executed (unused).
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
    """Attach failure evidence to the Allure result, then quit WebDriver.

    A failed or broken scenario keeps a screenshot and the current URL, taken
    before quit: afterwards there is no page left to capture.

    Args:
        context: Behave context object.
        scenario: Scenario that was executed.
    """
    try:
        if scenario.status.has_failed() and hasattr(context, "driver"):
            allure.attach(
                context.driver.get_screenshot_as_png(),
                name="screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
            allure.attach(
                context.driver.current_url,
                name="url",
                attachment_type=allure.attachment_type.URI_LIST,
            )
    finally:
        if hasattr(context, "driver_manager"):
            context.driver_manager.quit()
