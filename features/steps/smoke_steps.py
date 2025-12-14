"""Smoke test step definitions for Sauce Demo.

Basic validation steps to ensure application is operational.
"""

from behave import given, when, then
from selenium.webdriver.common.by import By

from core.config import get_base_url
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


@when('I navigate to the Sauce Demo homepage')
@given('I am on the Sauce Demo homepage')
def step_navigate_to_homepage(context):
    """Navigate to Sauce Demo homepage."""
    base_url = get_base_url(context.config_data)
    context.driver.get(base_url)
    context.login_page = LoginPage(context.driver)


@then('the login page should be displayed')
def step_verify_login_page(context):
    """Verify login page is displayed."""
    assert context.login_page.is_element_present(context.login_page.USERNAME_INPUT), \
        "Login page should be displayed (username field present)"


@then('the page title should contain "{expected_text}"')
def step_verify_page_title(context, expected_text):
    """Verify page title contains expected text."""
    assert expected_text.lower() in context.driver.title.lower(), \
        f"Page title should contain '{expected_text}'"


@then('the username field should be visible')
def step_verify_username_field(context):
    """Verify username field is visible."""
    assert context.login_page.is_element_present(context.login_page.USERNAME_INPUT), \
        "Username field should be visible"


@then('the password field should be visible')
def step_verify_password_field(context):
    """Verify password field is visible."""
    assert context.login_page.is_element_present(context.login_page.PASSWORD_INPUT), \
        "Password field should be visible"


@then('the login button should be visible')
def step_verify_login_button(context):
    """Verify login button is visible."""
    assert context.login_page.is_element_present(context.login_page.LOGIN_BUTTON), \
        "Login button should be visible"


@when('I enter valid credentials')
def step_enter_valid_credentials(context):
    """Enter valid test credentials (standard_user)."""
    context.login_page.login("standard_user", "secret_sauce")


@when('I enter invalid credentials')
def step_enter_invalid_credentials(context):
    """Enter invalid credentials."""
    context.login_page.login("invalid_user", "wrong_password")


@then('I should be redirected to the inventory page')
def step_verify_redirected_to_inventory(context):
    """Verify user is on inventory page."""
    context.inventory_page = InventoryPage(context.driver)
    assert context.inventory_page.is_on_inventory_page(), \
        "Should be redirected to inventory page after login"


@then('I should see an error message')
def step_verify_error_message(context):
    """Verify error message is displayed."""
    error_message = context.login_page.get_error_message()
    assert error_message is not None, "Error message should be displayed"
    assert len(error_message) > 0, "Error message should not be empty"
