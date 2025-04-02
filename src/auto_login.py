# src/auto_login.py
"""
Zerodha Multi-Account Login Script (Single File Version)

This script automates the login process for multiple Zerodha accounts simultaneously
using Selenium and Python's threading module. It reads credentials from a CSV file
and handles TOTP generation if a secret key is provided.

All logic is contained within this single file.
"""

# --- Standard Library Imports ---
import csv
import threading
import time
import sys
import os
import pyotp # For TOTP generation
import traceback # For detailed error logging
import pprint # For cleaner debug printing

# --- Selenium Imports ---
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ==============================================================================
# --- Configuration Constants ---
# ==============================================================================

# --- File Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, 'zerodha_credentials.csv')

# --- URLs ---
ZERODHA_LOGIN_URL = "https://kite.zerodha.com/"

# --- Timeouts and Delays (in seconds) ---
WEBDRIVER_WAIT_TIMEOUT = 30
SHORT_DELAY = 0.75
INTER_KEY_DELAY = SHORT_DELAY / 2
POST_LOGIN_CLICK_DELAY = 4.0
POST_2FA_KEY_DELAY = 1.0
POST_FINAL_SUBMIT_DELAY = SHORT_DELAY
BROWSER_LAUNCH_DELAY = 2.0

# --- CSV Headers ---
CSV_USERNAME_HEADER = "Username"
CSV_PASSWORD_HEADER = "Password"
CSV_2FA_HEADER = "PIN/TOTP Secret"
REQUIRED_CSV_HEADERS = [CSV_USERNAME_HEADER, CSV_PASSWORD_HEADER]

# --- Selenium Locators ---
USER_ID_INPUT_LOCATOR = (By.ID, "userid")
PASSWORD_INPUT_LOCATOR = (By.ID, "password")
LOGIN_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "//button[@type='submit']")
# Corrected 2FA input locator based on previous feedback
PIN_INPUT_ID_NAME = "userid"
PIN_INPUT_LOCATOR = (By.ID, PIN_INPUT_ID_NAME)
PIN_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "//button[@type='submit']")

# ==============================================================================
# --- Helper Functions ---
# ==============================================================================

def read_credentials(filepath):
    """Reads credentials from the specified CSV file."""
    accounts_data = []
    print(f"Reading credentials from: {filepath}")
    try:
        with open(filepath, mode='r', newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            if not reader.fieldnames or not all(header in reader.fieldnames for header in REQUIRED_CSV_HEADERS):
                 print(f"ERROR: Credentials file '{filepath}' missing required headers ({REQUIRED_CSV_HEADERS}) or empty.")
                 return None
            print("-" * 30)
            for i, row in enumerate(reader):
                print(f"\nDEBUG: Processing CSV row {i+1}")
                print(f"DEBUG: Raw row data: {row}")
                username = row.get(CSV_USERNAME_HEADER, "").strip()
                password = row.get(CSV_PASSWORD_HEADER, "").strip()
                pin_or_totp = row.get(CSV_2FA_HEADER, "").strip()
                print(f"DEBUG: Extracted - User: '{username}', Pass: '******', 2FA provided: {'Yes' if pin_or_totp else 'No'}")
                if username and password:
                    if CSV_2FA_HEADER not in row: row[CSV_2FA_HEADER] = ''
                    accounts_data.append(row)
                    print(f"DEBUG: Row {i+1} deemed valid and added.")
                else:
                    print(f"DEBUG: Row {i+1} SKIPPED due to missing Username or Password.")
            print("-" * 30)
            if not accounts_data:
                 print("ERROR: No valid account credentials found.")
                 return None
            print(f"\nDEBUG: Finished reading CSV. Valid accounts: {len(accounts_data)}")
            print("DEBUG: Final accounts_data list:")
            pprint.pprint(accounts_data)
            print("-" * 30)
            return accounts_data
    except FileNotFoundError:
        print(f"ERROR: Credentials file not found: '{filepath}'.")
        return None
    except Exception as e:
        print(f"ERROR: Failed to read/parse credentials: {e}")
        traceback.print_exc()
        return None

def setup_driver(log_prefix):
    """Sets up and returns a Selenium Chrome WebDriver instance."""
    print(f"[{log_prefix}] Setting up Chrome...")
    driver = None
    try:
        options = Options()
        options.add_experimental_option("detach", True)
        options.headless = False
        print(f"[{log_prefix}] Launching Chrome browser...")
        driver = webdriver.Chrome(options=options)
        print(f"[{log_prefix}] Chrome launched.")
        return driver
    except Exception as e:
        print(f"[{log_prefix}] CRITICAL ERROR launching Chrome: {e}")
        if driver:
            try: driver.quit()
            except Exception: pass
        return None

def navigate_and_wait(driver, username_log_prefix):
    """Navigates to the login URL and returns a WebDriverWait object."""
    print(f"[{username_log_prefix}] Navigating to {ZERODHA_LOGIN_URL}...")
    driver.get(ZERODHA_LOGIN_URL)
    print(f"[{username_log_prefix}] Pausing {SHORT_DELAY}s...")
    time.sleep(SHORT_DELAY)
    return WebDriverWait(driver, WEBDRIVER_WAIT_TIMEOUT)

def enter_credentials(wait, username_val, password_val, username_log_prefix):
    """Enters username and password."""
    print(f"[{username_log_prefix}] Entering username...")
    username_input = wait.until(EC.presence_of_element_located(USER_ID_INPUT_LOCATOR))
    username_input.send_keys(username_val)
    time.sleep(INTER_KEY_DELAY)
    print(f"[{username_log_prefix}] Entering password...")
    password_input = wait.until(EC.presence_of_element_located(PASSWORD_INPUT_LOCATOR))
    password_input.send_keys(password_val)
    time.sleep(INTER_KEY_DELAY)

def submit_initial_login(wait, username_log_prefix):
    """Clicks the initial login submit button."""
    print(f"[{username_log_prefix}] Clicking login button...")
    login_button = wait.until(EC.element_to_be_clickable(LOGIN_SUBMIT_BUTTON_LOCATOR))
    login_button.click()
    print(f"[{username_log_prefix}] Pausing {POST_LOGIN_CLICK_DELAY}s for 2FA page...")
    time.sleep(POST_LOGIN_CLICK_DELAY)

def handle_two_factor_auth(wait, pin_or_totp_secret, username_log_prefix):
    """Handles the 2FA screen (PIN or TOTP)."""
    try:
        print(f"[{username_log_prefix}] Waiting for 2FA input field (id='{PIN_INPUT_ID_NAME}') to be clickable...")
        pin_input = wait.until(EC.element_to_be_clickable(PIN_INPUT_LOCATOR))
        print(f"[{username_log_prefix}] 2FA screen detected and input field clickable.")
        pin_or_totp_secret = pin_or_totp_secret.strip()
        print(f"[{username_log_prefix}] DEBUG: 2FA Value from CSV: '{pin_or_totp_secret}'")
        if not pin_or_totp_secret:
            print(f"[{username_log_prefix}] WARNING: 2FA required but no PIN/TOTP found.")
            return False
        print(f"[{username_log_prefix}] Attempting to enter PIN/TOTP...")
        current_value_to_send = ""
        if len(pin_or_totp_secret) > 8 and pin_or_totp_secret.isalnum() and not pin_or_totp_secret.isdigit():
            print(f"[{username_log_prefix}] DEBUG: Treating as TOTP Secret.")
            try:
                totp = pyotp.TOTP(pin_or_totp_secret)
                current_otp = totp.now()
                print(f"[{username_log_prefix}] DEBUG: Generated TOTP: {current_otp}")
                current_value_to_send = current_otp
            except Exception as totp_gen_error:
                print(f"[{username_log_prefix}] ERROR generating TOTP: {totp_gen_error}")
                return False
        else:
            print(f"[{username_log_prefix}] DEBUG: Treating as static PIN/Other value.")
            current_value_to_send = pin_or_totp_secret
        print(f"[{username_log_prefix}] DEBUG: Sending keys: '{current_value_to_send}'")
        print(f"[{username_log_prefix}] DEBUG: Clearing 2FA input field...")
        pin_input.clear()
        time.sleep(0.1)
        pin_input.send_keys(current_value_to_send)
        print(f"[{username_log_prefix}] DEBUG: Pausing {POST_2FA_KEY_DELAY}s...")
        time.sleep(POST_2FA_KEY_DELAY)
        print(f"[{username_log_prefix}] Waiting for 2FA submit button...")
        pin_submit_button = wait.until(EC.element_to_be_clickable(PIN_SUBMIT_BUTTON_LOCATOR))
        print(f"[{username_log_prefix}] Submitting PIN/TOTP...")
        pin_submit_button.click()
        print(f"[{username_log_prefix}] Pausing {POST_FINAL_SUBMIT_DELAY}s...")
        time.sleep(POST_FINAL_SUBMIT_DELAY)
        print(f"[{username_log_prefix}] 2FA submitted successfully.")
        return True
    except TimeoutException:
        print(f"[{username_log_prefix}] INFO: 2FA input field (id='{PIN_INPUT_ID_NAME}') not detected or clickable within timeout.")
        if not pin_or_totp_secret.strip():
             print(f"[{username_log_prefix}] Assuming no 2FA was needed.")
             return True # Okay if 2FA wasn't expected
        else:
             print(f"[{username_log_prefix}] WARNING: PIN/TOTP provided but 2FA field not interactable.")
             return False # Failed as 2FA expected but couldn't be handled
    except Exception as e:
        print(f"[{username_log_prefix}] ERROR during 2FA handling: {e}")
        traceback.print_exc()
        return False

# --- Thread Target Function ---
def run_single_login_session(credentials):
    """Orchestrates the login process for a single Zerodha account."""
    print("\n" + "="*10 + " THREAD ENTRY " + "="*10)
    print("DEBUG: Thread received credentials:")
    pprint.pprint(credentials)
    print("="*34)
    username = credentials.get(CSV_USERNAME_HEADER, 'UNKNOWN_USER')
    log_prefix = username
    driver = None
    login_successful = False
    try:
        driver = setup_driver(log_prefix)
        if not driver: return # Exit if driver setup failed

        wait = navigate_and_wait(driver, log_prefix)
        enter_credentials(wait, credentials[CSV_USERNAME_HEADER], credentials[CSV_PASSWORD_HEADER], log_prefix)
        submit_initial_login(wait, log_prefix) # Includes 4s wait
        pin_or_totp = credentials.get(CSV_2FA_HEADER, '')
        two_fa_success = handle_two_factor_auth(wait, pin_or_totp, log_prefix) # Uses corrected 2FA logic

        if two_fa_success:
            print(f"[{log_prefix}] Login flow steps completed.")
            login_successful = True
        else:
            print(f"[{log_prefix}] Login flow failed during/after 2FA.")
            login_successful = False

    except (TimeoutException, NoSuchElementException) as e:
        error_type = type(e).__name__
        print(f"[{log_prefix}] ERROR ({error_type}) before 2FA handling: {e}")
        # --- CORRECTED SCREENSHOT BLOCK 1 ---
        if driver:
            try:
                filename = f"{log_prefix}_{error_type.lower()}_error.png"
                driver.save_screenshot(filename)
                print(f"[{log_prefix}] Screenshot saved: {filename}")
            except Exception as screenshot_error:
                print(f"[{log_prefix}] WARNING: Failed to save screenshot: {screenshot_error}")
                pass # Ignore screenshot saving errors
        # --- END CORRECTION ---
    except KeyError as e:
        print(f"[{log_prefix}] ERROR: Missing key in credentials: {e}.")
    except Exception as e:
        print(f"[{log_prefix}] UNEXPECTED ERROR in orchestration: {e}")
        traceback.print_exc()
        # --- CORRECTED SCREENSHOT BLOCK 2 ---
        if driver:
            try:
                filename = f"{log_prefix}_unexpected_error.png"
                driver.save_screenshot(filename)
                print(f"[{log_prefix}] Screenshot saved: {filename}")
            except Exception as screenshot_error:
                print(f"[{log_prefix}] WARNING: Failed to save screenshot: {screenshot_error}")
                pass # Ignore screenshot saving errors
        # --- END CORRECTION ---
    finally:
        status = "likely SUCCESSFUL" if login_successful else "likely FAILED"
        print(f"[{log_prefix}] Browser window remains open (Login {status}).")
        print(f"[{log_prefix}] Thread execution complete.")
        print("="*34)


# ==============================================================================
# --- Main Execution Logic ---
# ==============================================================================

def main():
    """Main function: Reads credentials and launches login threads."""
    print("--- Zerodha Multi-Account Login Script (Single File) ---")
    accounts_data = read_credentials(CREDENTIALS_FILE)
    if accounts_data is None:
        print("Exiting due to credential reading errors.")
        sys.exit(1)

    threads = []
    launch_delay = BROWSER_LAUNCH_DELAY
    print(f"\nLaunching login threads for {len(accounts_data)} account(s)...")
    print(f"(Delay between launches: {launch_delay}s)")

    for i, credentials_for_thread in enumerate(accounts_data):
        print("-" * 30)
        print(f"DEBUG: Preparing Thread #{i+1} for account: {credentials_for_thread.get(CSV_USERNAME_HEADER, 'N/A')}")

        # Threads are NOT daemons, main will wait for them
        thread = threading.Thread(target=run_single_login_session, args=(credentials_for_thread,))
        threads.append(thread)
        print(f"DEBUG: Starting Thread #{i+1}...")
        thread.start()

        if i < len(accounts_data) - 1:
             time.sleep(launch_delay)
             print(f"DEBUG: Paused for {launch_delay}s after starting Thread #{i+1}.")
        else:
             print(f"DEBUG: Last thread started.")

    # Wait for all threads to complete before exiting main
    print("\n" + "="*10 + " WAITING FOR THREADS " + "="*10)
    print("Main thread is now waiting for all login attempts to finish...")
    for i, thread in enumerate(threads):
        thread.join() # Wait here until thread 'i' finishes its execution
        print(f"DEBUG: Thread #{i+1} has completed.")
    print("="*38)
    print("All login threads have finished.")
    print("You can now manually close the browser windows.")
    print("Script execution complete.")

if __name__ == "__main__":
    main()