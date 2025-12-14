"""Registration feature step definitions.

Implements BDD steps for user registration scenarios.
"""

import time
from behave import when, then

from pages.register_page import RegisterPage


@when('the user navigates to the registration page')
def step_navigate_to_register(context):
    """Navigate to registration page."""
    context.login_page.click_register_link()
    context.register_page = RegisterPage(context.driver)


@when('the user fills in the registration form with unique username')
def step_fill_registration_form(context):
    """Fill registration form with data from table."""
    # Parse table data
    user_data = {}
    for row in context.table:
        user_data[row['field']] = row['value']
    
    # Generate unique username
    username = f"testuser{int(time.time())}"
    user_data['username'] = username
    user_data['password'] = 'Password123'
    
    # Store for later verification
    context.test_username = username
    
    # Fill form
    context.register_page.fill_registration_form(user_data)


@when('the user submits the registration form')
def step_submit_registration(context):
    """Submit registration form."""
    context.register_page.submit_registration()


@then('the user should see a success message')
def step_verify_success_message(context):
    """Verify registration success message is displayed."""
    success_message = context.register_page.get_success_message()
    assert success_message is not None, "No success message found"
    assert "successfully" in success_message.lower(), \
        f"Expected success message, got: {success_message}"


@then('the user should be logged in automatically')
def step_verify_auto_login(context):
    """Verify user is logged in after registration."""
    assert context.register_page.is_logged_in(), \
        "Expected to be logged in (Log Out link should be present)"
