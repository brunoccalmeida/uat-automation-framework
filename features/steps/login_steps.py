"""Login feature step definitions for Sauce Demo.

Implements BDD steps for user login scenarios.
"""

from behave import given, when, then
from selenium.webdriver.common.by import By

from core.config import get_base_url
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


@given("I am on the Sauce Demo login page")
def step_on_login_page(context):
    """Navigate to Sauce Demo login page."""
    base_url = get_base_url(context.config_data)
    context.driver.get(base_url)
    context.login_page = LoginPage(context.driver)


@given('I am logged in as "{username}"')
def step_logged_in_as_user(context, username):
    """Log in as specific user."""
    base_url = get_base_url(context.config_data)
    context.driver.get(base_url)
    context.login_page = LoginPage(context.driver)
    context.login_page.login(username, "secret_sauce")
    context.inventory_page = InventoryPage(context.driver)


@when('I enter username "{username}"')
def step_enter_username(context, username):
    """Enter username into login form."""
    context.login_page.enter_username(username)


@when('I login with username "{username}" and password "{password}"')
def step_login_with_credentials(context, username, password):
    """Log in with provided credentials."""
    context.login_page.login(username, password)


@when("I click the menu button")
def step_click_menu(context):
    """Click menu button."""
    context.inventory_page.click(context.inventory_page.MENU_BUTTON)


@when("I click the login button")
def step_click_login_button(context):
    """Click login button."""
    context.login_page.click_login()


# Remover steps duplicados/placeholders inválidos e garantir steps corretos




@then("I should be on the inventory page")
def step_verify_on_inventory_page(context):
    """Verify user is on inventory/products page."""
    context.inventory_page = InventoryPage(context.driver)
    assert (
        context.inventory_page.is_on_inventory_page()
    ), "User should be on inventory page"


@then('the page title should be "{expected_title}"')
def step_verify_page_title(context, expected_title):
    """Verify page title matches expected text."""
    inventory_page = InventoryPage(context.driver)
    actual_title = inventory_page.get_page_title()
    assert (
        actual_title == expected_title
    ), f"Page title should be '{expected_title}', but was '{actual_title}'"


@then("I should see login error message")
def step_verify_login_error(context):
    """Verify login error message is displayed."""
    error_message = context.login_page.get_error_message()
    assert error_message is not None, "Error message should be displayed"
    assert len(error_message) > 0, "Error message should not be empty"


@then('the error should mention "{text}"')
def step_verify_error_contains(context, text):
    """Verify error message contains specific text.
    
    Supports OR logic with ' or ' separator for alternative texts.
    Example: 'locked out" or "too many attempts'
    """
    error_message = context.login_page.get_error_message()
    
    # Check if text contains OR operator
    if '" or "' in text:
        # Extract alternative texts - split by '" or "' and clean up quotes
        alternatives = [alt.strip(' "') for alt in text.split('" or "')]
        # Check if any alternative is present
        found = any(alt.lower() in error_message.lower() for alt in alternatives)
        assert found, (
            f"Error message should mention one of {alternatives}, "
            f"but got: '{error_message}'"
        )
    else:
        # Simple text match
        assert (
            text.lower() in error_message.lower()
        ), f"Error message should mention '{text}', but got: '{error_message}'"


@then("I should remain on the login page")
def step_verify_on_login_page(context):
    """Verify user is still on login page."""
    base_url = get_base_url(context.config_data)
    current_url = context.driver.current_url
    assert base_url in current_url, "Should remain on login page after failed login"


@then("I should be logged in successfully")
def step_verify_logged_in_successfully(context):
    """Verify user successfully logged in (on inventory page)."""
    inventory_page = InventoryPage(context.driver)
    assert inventory_page.is_on_inventory_page(), "Should be on inventory page after successful login"


@then("I should see the products page")
def step_verify_see_products_page(context):
    """Verify user sees the products page (inventory page)."""
    inventory_page = InventoryPage(context.driver)
    assert inventory_page.is_on_inventory_page(), "Should see the products page"


@when("I click logout")
def step_click_logout(context):
    """Click logout from menu (menu should already be open)."""
    # Use existing inventory_page from context (menu already clicked)
    context.inventory_page.click(context.inventory_page.LOGOUT_LINK)


@then("I should be redirected to the login page")
def step_verify_redirected_to_login(context):
    """Verify user is redirected to login page."""
    base_url = get_base_url(context.config_data)
    current_url = context.driver.current_url
    assert base_url in current_url, "Should be redirected to login page after logout"
