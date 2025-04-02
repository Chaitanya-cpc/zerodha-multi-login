# src/driver_setup.py
"""Handles the setup and creation of the Selenium WebDriver."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
# No constants needed directly here, but the caller might use them

def setup_driver(username_log_prefix):
    """Sets up and returns a Selenium Chrome WebDriver instance."""
    print(f"[{username_log_prefix}] Setting up Chrome options...")
    driver = None
    try:
        options = Options()
        # Keep browser open after script technically finishes
        options.add_experimental_option("detach", True)
        # Run browser in the foreground (visible)
        options.headless = False

        # --- WebDriver Service Setup ---
        # Assumes chromedriver is in PATH by default.
        # For specifying path explicitly:
        # service = Service('/path/to/your/chromedriver')
        # driver = webdriver.Chrome(service=service, options=options)
        # See drivers/README_DRIVERS.md for details.

        print(f"[{username_log_prefix}] Launching Chrome browser...")
        driver = webdriver.Chrome(options=options)
        print(f"[{username_log_prefix}] Chrome launched successfully.")
        return driver

    except Exception as e:
        print(f"[{username_log_prefix}] CRITICAL ERROR: Failed to launch Chrome. Ensure ChromeDriver is installed and in PATH.")
        print(f"[{username_log_prefix}] Error details: {e}")
        if driver: # Attempt cleanup if partially initialized
            try:
                driver.quit()
            except Exception:
                pass # Ignore errors during cleanup attempt
        return None # Indicate failure