"""Debug script to test login with pre-existing demo user.

Tests if login works with standard Parabank demo credentials
to isolate if issue is with newly created users or general Parabank issue.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from core.config import get_base_url, load_config
from pages.login_page import LoginPage

# Setup
config = load_config("config.yaml")
base_url = get_base_url(config)

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("prefs", {
    "autofill.profile_enabled": False,
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False
})

driver = webdriver.Chrome(options=options)
driver.maximize_window()

try:
    # Test with known demo user
    print("\n=== TESTING LOGIN WITH DEMO USER ===")
    
    # Parabank has demo users: john (no password), testuser (password: testpass), etc
    test_users = [
        ("john", "demo"),
        ("testuser", "testpass"),
        ("demo", "demo"),
    ]
    
    for username, password in test_users:
        print(f"\n--- Testing: {username} / {password} ---")
        
        driver.get(base_url)
        time.sleep(1)
        
        login_page = LoginPage(driver)
        login_page.enter_username(username)
        login_page.enter_password(password)
        login_page.click_login()
        
        time.sleep(2)
        
        print(f"  Current URL: {driver.current_url}")
        print(f"  Page title: {driver.title}")
        
        # Check for error
        try:
            error = driver.find_element(By.CSS_SELECTOR, ".error")
            error_text = error.text
            print(f"  ❌ ERROR: {error_text}")
        except:
            print(f"  ✓ No error message")
        
        # Check for logout link (success indicator)
        try:
            logout = driver.find_element(By.LINK_TEXT, "Log Out")
            print(f"  ✓ LOGGED IN - Log Out link present")
        except:
            print(f"  ⚠ NOT logged in - No Log Out link")
        
        # Check for Account Services
        try:
            menu = driver.find_element(By.XPATH, "//h2[text()='Account Services']")
            print(f"  ✓ Account Services menu visible")
        except:
            print(f"  ⚠ Account Services menu not found")
        
finally:
    driver.quit()
    print("\n=== DONE ===")
