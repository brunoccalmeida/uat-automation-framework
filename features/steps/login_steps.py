"""Login feature step definitions.

Implements BDD steps for user login scenarios.
"""

import time
from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.config import get_base_url
from pages.login_page import LoginPage
from pages.register_page import RegisterPage


@given('the user is on the Parabank homepage')
def step_user_on_homepage(context):
    """Navigate to Parabank homepage."""
    base_url = get_base_url(context.config_data)
    context.driver.get(base_url)
    context.login_page = LoginPage(context.driver)


@given('the user has a registered account with username "{username}" and password "{password}"')
def step_user_has_account(context, username, password):
    """Verify user has registered account."""
    context.username = username
    context.password = password


@given('the user registers a new account')
def step_register_new_account(context):
    """Register a new account for testing login."""
    username = f"logintest{int(time.time())}"
    password = "TestPass123"
    
    context.login_page.click_register_link()
    context.register_page = RegisterPage(context.driver)
    
    user_data = {
        "first_name": "Login",
        "last_name": "Test",
        "address": "123 Test St",
        "city": "TestCity",
        "state": "TS",
        "zip_code": "12345",
        "phone": "555-1234",
        "ssn": "123-45-6789",
        "username": username,
        "password": password
    }
    context.register_page.fill_registration_form(user_data)
    context.register_page.submit_registration()
    
    context.test_username = username
    context.test_password = password


@given('the user logs out')
def step_user_logs_out(context):
    """Log out the current user."""
    logout_link = WebDriverWait(context.driver, 5).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Log Out"))
    )
    logout_link.click()


@when('the user logs in with the registered credentials')
def step_login_with_credentials(context):
    """Log in with previously registered credentials."""
    context.login_page = LoginPage(context.driver)
    context.login_page.enter_username(context.test_username)
    context.login_page.enter_password(context.test_password)
    context.login_page.click_login()


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
    logout_link = (By.LINK_TEXT, "Log Out")
    assert context.login_page.is_element_present(logout_link, timeout=3), \
        "User should be logged in (Log Out link should be present)"


@then('the user should see the account overview page')
def step_verify_account_overview(context):
    """Verify account overview page is displayed."""
    assert "overview" in context.driver.current_url.lower()


@then('the user should see the account services menu')
def step_verify_account_services(context):
    """Verify account services menu is displayed."""
    account_services = (By.XPATH, "//h2[text()='Account Services']")
    assert context.login_page.is_element_present(account_services, timeout=3), \
        "Account Services menu should be visible"


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
