# src/constants.py
"""Stores constant values used across the application."""

import os
from selenium.webdriver.common.by import By # Added import

# --- File Paths ---
# Determine the base directory (ZERODHA_AUTOMATION)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Goes up one level from src/
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, 'zerodha_credentials.csv')

# --- URLs ---
ZERODHA_LOGIN_URL = "https://kite.zerodha.com/"

# --- Timeouts and Delays (in seconds) ---
WEBDRIVER_WAIT_TIMEOUT = 30 # Max time to wait for elements
SHORT_DELAY = 0.75 # Minor pause after certain actions
INTER_KEY_DELAY = SHORT_DELAY / 2 # Pause between entering username/password
POST_LOGIN_CLICK_DELAY = SHORT_DELAY # Pause after clicking initial login
POST_2FA_KEY_DELAY = 1.0 # Pause after entering PIN/TOTP, before submit
POST_FINAL_SUBMIT_DELAY = SHORT_DELAY # Pause after final submit
BROWSER_LAUNCH_DELAY = 2.0 # Delay between starting each browser instance

# --- Selenium Locators ---
# NOTE: IDs are generally preferred and more stable if available.
# Use XPATH carefully as it can be more brittle to website changes.

# Login Page 1
USER_ID_INPUT_LOCATOR = (By.ID, "userid")
PASSWORD_INPUT_LOCATOR = (By.ID, "password")
LOGIN_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "//button[@type='submit']")

# Login Page 2 (2FA)
# --- CRITICAL: Replace 'pin' with the ACTUAL ID of the PIN input field ---
# Inspect the element on Zerodha's 2FA page to find the correct ID.
PIN_INPUT_ID_NAME = "pin" # <-- Placeholder - MUST BE VERIFIED AND CORRECTED
PIN_INPUT_LOCATOR = (By.ID, PIN_INPUT_ID_NAME)
PIN_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "//button[@type='submit']") # Often the same submit button type

# --- CSV Headers ---
CSV_USERNAME_HEADER = "Username"
CSV_PASSWORD_HEADER = "Password"
CSV_2FA_HEADER = "PIN/TOTP Secret"
REQUIRED_CSV_HEADERS = [CSV_USERNAME_HEADER, CSV_PASSWORD_HEADER]