"""Behave environment configuration.

Manages test lifecycle hooks for Behave scenarios.
Handles WebDriver initialization and cleanup.
"""

import json

import allure

from core.config import load_settings
from core.driver_manager import DriverManager
from core.page_errors import watch_page_errors


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
    """Initialize WebDriver before each scenario and listen to its page errors.

    The listener starts before the first step navigates: an app bundle that
    throws does so while the first page loads (#183).

    Args:
        context: Behave context object.
        _scenario: Current scenario being executed (unused).
    """
    context.driver_manager = DriverManager(context.settings.browser_config)
    context.driver = context.driver_manager.get_driver()
    context.page_errors = watch_page_errors(context.driver)


def after_scenario(context, scenario):
    """Attach failure evidence to the Allure result, then quit WebDriver.

    A failed or broken scenario keeps the page's console messages and
    JavaScript errors ("[]" means none), a screenshot and the current URL,
    taken before quit: afterwards there is no page left to capture. The page
    errors go first: they are already in hand, so a browser that cannot
    answer the screenshot does not cost them too.

    Args:
        context: Behave context object.
        scenario: Scenario that was executed.
    """
    try:
        if scenario.status.has_failed() and hasattr(context, "driver"):
            if hasattr(context, "page_errors"):
                allure.attach(
                    json.dumps(context.page_errors, indent=2),
                    name="page-errors",
                    attachment_type=allure.attachment_type.JSON,
                )
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
