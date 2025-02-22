from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def login_to_internal_platform():
    # Setup Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = "/usr/bin/google-chrome"
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Initialize the driver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    try:
        # Navigate to the login page
        driver.get("http://16.171.65.143/")
        print(f"Navigated to: {driver.current_url}")
        
        # Add a small delay to ensure page is loaded
        time.sleep(2)
        
        # Wait for username field to be present and fill it
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_username"))
        )
        username_field.send_keys("admin")
        print("Entered username: admin")
        
        # Fill password field
        password_field = driver.find_element(By.ID, "id_password")
        password_field.send_keys("admin")
        print("Entered password")
        
        # Take screenshot for debugging (optional)
        driver.save_screenshot("/tmp/login_page.png")
        
        # Click login button with explicit wait
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        login_button.click()
        print("Clicked login button")
        
        # Wait for page to load after login
        time.sleep(5)
        
        # Take another screenshot after login attempt
        driver.save_screenshot("/tmp/after_login.png")
        
        if "Nxt-Gen Networks Automation Platform" in driver.title:
            print("Page title suggests we're on the main application page")
        
        xpath = "//a[contains(@href, '/logout/')]"  # Logout URL

        element = driver.find_element(By.XPATH, xpath)
        print(f"Found login indicator: {xpath}")
        print("Login successful")

        return driver
    except Exception as e:
        print(f"An error occurred during login: {e}")
        # Take error screenshot
        driver.save_screenshot("/tmp/login_error.png")
        driver.quit()
        raise

if __name__ == "__main__":
    # Run the login automation
    browser_session = login_to_internal_platform()
    
    if browser_session:
        print("Login successful! Browser session is active.")
        # Keep browser open to see the result
        input("Press Enter to close the browser...")
        browser_session.quit()
    else:
        print("Login failed.")