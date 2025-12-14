"""Login feature step definitions.

Implements BDD steps for user login scenarios.
"""

from behave import given, when, then

from core.config import get_base_url
from pages.login_page import LoginPage


@given('the user is on the Parabank homepage')
def step_user_on_homepage(context):
    """Navigate to Parabank homepage."""
    base_url = get_base_url(context.config_data)
    context.driver.get(base_url)
    context.login_page = LoginPage(context.driver)


@given('the user has a registered account with username "{username}" and password "{password}"')
def step_user_has_account(context, username, password):
    """Verify user has registered account.
    
    Note: For now, we assume the account exists. In future iterations,
    we'll implement auto-registration as specified in config.yaml.
    """
    context.username = username
    context.password = password


@when('the user enters username "{username}"')
def step_enter_username(context, username):
    """Enter username into login form."""
    context.login_page.enter_username(username)


@when('the user enters password "{password}"')
def step_enter_password(context, password):
    """Enter password into login form."""
    context.login_page.enter_password(password)


@when('the user clicks the login button')
def step_click_login(context):
    """Click login button."""
    context.login_page.click_login()


@then('the user should be logged in successfully')
def step_verify_logged_in(context):
    """Verify user is logged in."""
    # This will be implemented when we verify the resulting page
    # For now, we just check that we navigated away from login
    assert "login" not in context.driver.current_url.lower()


@then('the user should see the account overview page')
def step_verify_account_overview(context):
    """Verify account overview page is displayed."""
    assert "overview" in context.driver.current_url.lower()


@then('the user should see an error message')
def step_verify_error_message(context):
    """Verify error message is displayed."""
    error_message = context.login_page.get_error_message()
    assert error_message is not None
    assert len(error_message) > 0


@then('the user should remain on the login page')
def step_verify_on_login_page(context):
    """Verify user is still on login page."""
    base_url = get_base_url(context.config_data)
    current_url = context.driver.current_url
    # Parabank stays on index page or redirects to index.htm after failed login
    assert base_url in current_url
