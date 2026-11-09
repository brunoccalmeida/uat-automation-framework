"""Behave environment configuration.

Manages test lifecycle hooks for Behave scenarios.
Handles WebDriver initialization and cleanup.
"""

import allure

from core.config import load_settings
from core.driver_manager import DriverManager


def before_all(context):
    """Read and validate the settings, stopping the run if one is wrong.

    The -D parameters (-Dbrowser, -Dheadless, -Dremote_url) override the
    environment; see core/config.py for the whole precedence.

    Args:
        context: Behave context object.
    """
    userdata = context.config.userdata
    context.settings = load_settings(
        browser=userdata.get("browser"),
        headless=userdata.get("headless"),
        selenium_remote_url=userdata.get("remote_url"),
    )


def before_scenario(context, _scenario):
    """Initialize WebDriver before each scenario.

    Args:
        context: Behave context object.
        _scenario: Current scenario being executed (unused).
    """
    context.driver_manager = DriverManager(context.settings.browser_config)
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
