"""Debug script to isolate and understand login error message.

Replicates the exact scenario: register → logout → login
Captures page state after login to identify error message.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from core.config import get_base_url, load_config
from pages.login_page import LoginPage
from pages.register_page import RegisterPage

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
    # Step 1: Register
    print("\n=== STEP 1: REGISTER ===")
    driver.get(base_url)
    login_page = LoginPage(driver)
    login_page.click_register_link()
    register_page = RegisterPage(driver)
    
    username = f"debugtest{int(time.time())}"
    password = "TestPass123"
    
    user_data = {
        "first_name": "Debug",
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
    
    register_page.fill_registration_form(user_data)
    register_page.submit_registration()
    time.sleep(2)
    
    print(f"✓ Registered with username: {username}")
    print(f"  Current URL: {driver.current_url}")
    
    # Step 2: Logout
    print("\n=== STEP 2: LOGOUT ===")
    logout_link = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Log Out"))
    )
    logout_link.click()
    time.sleep(2)
    
    print(f"✓ Logged out")
    print(f"  Current URL: {driver.current_url}")
    
    # Step 3: Login again
    print("\n=== STEP 3: LOGIN AGAIN ===")
    login_page = LoginPage(driver)
    login_page.enter_username(username)
    login_page.enter_password(password)
    print(f"  Entered credentials for: {username}")
    
    login_page.click_login()
    time.sleep(2)
    
    print(f"✓ Clicked login button")
    print(f"  Current URL: {driver.current_url}")
    
    # Step 4: Inspect page state
    print("\n=== STEP 4: PAGE INSPECTION ===")
    
    # Check for error messages
    print("\n--- Looking for error messages ---")
    error_selectors = [
        ("CSS: .error", (By.CSS_SELECTOR, ".error")),
        ("CSS: .alert-danger", (By.CSS_SELECTOR, ".alert-danger")),
        ("XPATH: //span[@class='error']", (By.XPATH, "//span[@class='error']")),
        ("XPATH: //p[@class='error']", (By.XPATH, "//p[@class='error']")),
        ("XPATH: //*[contains(@class, 'error')]", (By.XPATH, "//*[contains(@class, 'error')]")),
        ("XPATH: //*[contains(text(), 'error')]", (By.XPATH, "//*[contains(text(), 'error')]")),
    ]
    
    for desc, locator in error_selectors:
        try:
            elements = driver.find_elements(*locator)
            if elements:
                print(f"\n✓ Found via {desc}:")
                for i, elem in enumerate(elements):
                    if elem.is_displayed():
                        print(f"  [{i}] Text: '{elem.text}'")
                        print(f"      Tag: {elem.tag_name}")
                        print(f"      Class: {elem.get_attribute('class')}")
                        print(f"      HTML: {elem.get_attribute('outerHTML')[:200]}")
        except:
            pass
    
    # Check for login form (still present = login failed)
    print("\n--- Checking login form presence ---")
    try:
        login_form = driver.find_element(By.NAME, "username")
        print("⚠ Login form is STILL present - login may have failed")
    except:
        print("✓ Login form NOT present - likely logged in")
    
    # Check for Log Out link
    print("\n--- Checking Log Out link ---")
    try:
        logout = driver.find_element(By.LINK_TEXT, "Log Out")
        print("✓ Log Out link FOUND - user is logged in")
    except:
        print("⚠ Log Out link NOT found - user may not be logged in")
    
    # Check for Account Services menu
    print("\n--- Checking Account Services menu ---")
    try:
        menu = driver.find_element(By.XPATH, "//h2[text()='Account Services']")
        print("✓ Account Services menu FOUND")
    except:
        print("⚠ Account Services menu NOT found")
    
    # Capture page title and headings
    print("\n--- Page content ---")
    print(f"  Title: {driver.title}")
    
    h1_elements = driver.find_elements(By.TAG_NAME, "h1")
    for h1 in h1_elements:
        print(f"  H1: '{h1.text}'")
    
    h2_elements = driver.find_elements(By.TAG_NAME, "h2")
    for h2 in h2_elements:
        print(f"  H2: '{h2.text}'")
    
    p_elements = driver.find_elements(By.TAG_NAME, "p")
    print(f"\n  Paragraphs found: {len(p_elements)}")
    for i, p in enumerate(p_elements[:5]):  # First 5
        if p.text.strip():
            print(f"    [{i}] '{p.text[:100]}'")
    
    # Full page source snippet
    print("\n--- Page source (first 2000 chars) ---")
    print(driver.page_source[:2000])
    
finally:
    driver.quit()
    print("\n=== DONE ===")
