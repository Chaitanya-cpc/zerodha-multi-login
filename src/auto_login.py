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
# Determine the base directory (ZERODHA_AUTOMATION) assuming src is one level down
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, 'zerodha_credentials.csv') # Use the correct filename

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

# --- CSV Headers ---
CSV_USERNAME_HEADER = "Username"
CSV_PASSWORD_HEADER = "Password"
CSV_2FA_HEADER = "PIN/TOTP Secret" # Adjust if your header name is different
REQUIRED_CSV_HEADERS = [CSV_USERNAME_HEADER, CSV_PASSWORD_HEADER] # 2FA is optional but read if present

# --- Selenium Locators ---
# NOTE: IDs are generally preferred. Update these if Zerodha changes its site.

# Login Page 1
USER_ID_INPUT_LOCATOR = (By.ID, "userid")
PASSWORD_INPUT_LOCATOR = (By.ID, "password")
LOGIN_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "//button[@type='submit']")

# Login Page 2 (2FA)
# --- CRITICAL: Replace 'pin' with the ACTUAL ID of the PIN/TOTP input field ---
# Inspect the element on Zerodha's 2FA page using F12 Dev Tools.
PIN_INPUT_ID_NAME = "pin" # <-- Placeholder - MUST BE VERIFIED AND CORRECTED
PIN_INPUT_LOCATOR = (By.ID, PIN_INPUT_ID_NAME)
PIN_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "//button[@type='submit']") # Often the same submit button type

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

            # Check headers
            if not reader.fieldnames or not all(header in reader.fieldnames for header in REQUIRED_CSV_HEADERS):
                 print(f"ERROR: Credentials file '{filepath}' is missing required headers ({REQUIRED_CSV_HEADERS}) or is empty.")
                 print(f"Found headers: {reader.fieldnames}")
                 return None

            print("-" * 30) # Separator for reading loop
            for i, row in enumerate(reader):
                print(f"\nDEBUG: Processing CSV row {i+1}")
                print(f"DEBUG: Raw row data: {row}") # Print raw row

                username = row.get(CSV_USERNAME_HEADER, "").strip()
                password = row.get(CSV_PASSWORD_HEADER, "").strip()
                pin_or_totp = row.get(CSV_2FA_HEADER, "").strip() # Read 2FA if present

                print(f"DEBUG: Extracted - User: '{username}', Pass: '******', 2FA provided: {'Yes' if pin_or_totp else 'No'}")

                if username and password:
                    # Ensure 2FA header key exists even if column was missing/empty
                    if CSV_2FA_HEADER not in row:
                        row[CSV_2FA_HEADER] = ''
                    accounts_data.append(row)
                    print(f"DEBUG: Row {i+1} deemed valid and added.")
                else:
                    print(f"DEBUG: Row {i+1} SKIPPED due to missing Username or Password.")

            print("-" * 30) # Separator after reading loop

            if not accounts_data:
                 print("ERROR: No valid account credentials found in the CSV file.")
                 return None

            print(f"\nDEBUG: Finished reading CSV. Total valid accounts found: {len(accounts_data)}")
            print("DEBUG: Final accounts_data list structure:")
            pprint.pprint(accounts_data) # Pretty print the list of dicts
            print("-" * 30)
            return accounts_data

    except FileNotFoundError:
        print(f"ERROR: Credentials file not found at '{filepath}'.")
        print(f"Expected location: {os.path.abspath(filepath)}")
        return None
    except Exception as e:
        print(f"ERROR: Failed to read or parse credentials file: {e}")
        traceback.print_exc()
        return None

# --- Driver Setup ---
def setup_driver(log_prefix):
    """Sets up and returns a Selenium Chrome WebDriver instance."""
    print(f"[{log_prefix}] Setting up Chrome options...")
    driver = None
    try:
        options = Options()
        options.add_experimental_option("detach", True) # Keep browser open
        options.headless = False # Run in non-headless mode

        # Assumes chromedriver is in PATH by default.
        # If needed, specify path via Service object:
        # service = Service('/path/to/your/chromedriver')
        # driver = webdriver.Chrome(service=service, options=options)

        print(f"[{log_prefix}] Launching Chrome browser...")
        driver = webdriver.Chrome(options=options)
        print(f"[{log_prefix}] Chrome launched successfully.")
        return driver

    except Exception as e:
        print(f"[{log_prefix}] CRITICAL ERROR: Failed to launch Chrome. Ensure ChromeDriver is installed and in PATH.")
        print(f"[{log_prefix}] Error details: {e}")
        if driver:
            try:
                driver.quit()
            except Exception: pass
        return None

# --- Login Flow Steps ---
def navigate_and_wait(driver, username_log_prefix):
    """Navigates to the login URL and returns a WebDriverWait object."""
    url = ZERODHA_LOGIN_URL
    timeout = WEBDRIVER_WAIT_TIMEOUT
    print(f"[{username_log_prefix}] Navigating to {url}...")
    driver.get(url)
    print(f"[{username_log_prefix}] Pausing {SHORT_DELAY}s after page navigation...")
    time.sleep(SHORT_DELAY)
    return WebDriverWait(driver, timeout)

def enter_credentials(wait, username_val, password_val, username_log_prefix):
    """Enters username and password into the respective fields."""
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
    print(f"[{username_log_prefix}] Pausing {POST_LOGIN_CLICK_DELAY}s after login click (waiting for 2FA page)...")
    time.sleep(POST_LOGIN_CLICK_DELAY)

def handle_two_factor_auth(wait, pin_or_totp_secret, username_log_prefix):
    """Handles the 2FA screen (PIN or TOTP). Uses latest suggested logic."""
    try:
        # Wait for the element to be clickable, not just present
        # --- IMPORTANT: Verify PIN_INPUT_LOCATOR uses the correct ID/selector ---
        print(f"[{username_log_prefix}] Waiting for PIN input field to be clickable (locator: {PIN_INPUT_LOCATOR})...")
        pin_input = wait.until(EC.element_to_be_clickable(PIN_INPUT_LOCATOR))
        print(f"[{username_log_prefix}] 2FA screen detected and input field is clickable.")

        pin_or_totp_secret = pin_or_totp_secret.strip()
        print(f"[{username_log_prefix}] DEBUG: Value read for PIN/TOTP Secret: '{pin_or_totp_secret}'")

        if not pin_or_totp_secret:
            print(f"[{username_log_prefix}] WARNING: 2FA screen detected, but no PIN/TOTP found in credentials file.")
            return # Stop processing 2FA

        print(f"[{username_log_prefix}] Attempting to enter PIN/TOTP...")
        current_value_to_send = ""

        # Heuristic check for TOTP secret
        if len(pin_or_totp_secret) > 8 and pin_or_totp_secret.isalnum() and not pin_or_totp_secret.isdigit():
            print(f"[{username_log_prefix}] DEBUG: Treating as TOTP Secret.")
            try:
                totp = pyotp.TOTP(pin_or_totp_secret)
                current_otp = totp.now()
                print(f"[{username_log_prefix}] DEBUG: Generated TOTP: {current_otp}")
                current_value_to_send = current_otp
            except Exception as totp_gen_error:
                print(f"[{username_log_prefix}] ERROR generating TOTP: {totp_gen_error}")
                return # Cannot proceed
        else:
            print(f"[{username_log_prefix}] DEBUG: Treating as static PIN/Other value.")
            current_value_to_send = pin_or_totp_secret

        # --- Send Keys ---
        print(f"[{username_log_prefix}] DEBUG: Sending keys: '{current_value_to_send}'")
        # Clear the field before sending keys
        print(f"[{username_log_prefix}] DEBUG: Clearing PIN input field before sending keys.")
        pin_input.clear()
        time.sleep(0.1) # Tiny pause after clear
        pin_input.send_keys(current_value_to_send)

        # Pause after sending keys, before waiting for submit
        print(f"[{username_log_prefix}] DEBUG: Pausing {POST_2FA_KEY_DELAY}s after sending keys...")
        time.sleep(POST_2FA_KEY_DELAY)

        print(f"[{username_log_prefix}] Waiting for PIN/TOTP submit button...")
        # Ensure the submit button locator is also correct
        pin_submit_button = wait.until(EC.element_to_be_clickable(PIN_SUBMIT_BUTTON_LOCATOR))
        print(f"[{username_log_prefix}] Submitting PIN/TOTP...")
        pin_submit_button.click()

        print(f"[{username_log_prefix}] Pausing {POST_FINAL_SUBMIT_DELAY}s after final submit...")
        time.sleep(POST_FINAL_SUBMIT_DELAY)
        print(f"[{username_log_prefix}] Login submitted successfully after 2FA.")
        return True # Indicate 2FA step was attempted successfully

    except TimeoutException:
        print(f"[{username_log_prefix}] ERROR: Timed out waiting for PIN input field to be clickable (Locator: '{PIN_INPUT_LOCATOR}').")
        print(f"[{username_log_prefix}] Possible reasons: Incorrect locator, element not interactable, page didn't load correctly, or element is inside an iframe.")
        if not pin_or_totp_secret.strip():
             print(f"[{username_log_prefix}] Proceeding assuming no 2FA was needed or flow changed.")
             return True # Assume success if no 2FA was expected and screen didn't appear
        else:
             print(f"[{username_log_prefix}] WARNING: PIN/TOTP was provided, but 2FA input field was not found or not clickable.")
             return False # Indicate failure as 2FA was expected but couldn't be handled

    except Exception as e:
        print(f"[{username_log_prefix}] ERROR during 2FA handling (after potentially finding element): {e}")
        traceback.print_exc()
        return False # Indicate failure

# --- Thread Target Function ---
def run_single_login_session(credentials):
    """
    Orchestrates the login process for a single Zerodha account in its own thread.

    Args:
        credentials (dict): Dictionary containing account credentials.
    """
    # --- Added: Print credentials received by thread ---
    print("\n" + "="*10 + " THREAD ENTRY " + "="*10)
    print("DEBUG: Thread received credentials:")
    pprint.pprint(credentials)
    print("="*34)
    # --- End Added Print ---

    username = credentials.get(CSV_USERNAME_HEADER, 'UNKNOWN_USER')
    log_prefix = username # Use username for logging prefix
    driver = None
    login_successful = False # Track overall success

    try:
        # Step 1: Setup WebDriver
        driver = setup_driver(log_prefix)
        if not driver:
            print(f"[{log_prefix}] Aborting thread: WebDriver setup failed.")
            return # Exit this thread

        # Step 2: Navigate and get WebDriverWait
        wait = navigate_and_wait(driver, log_prefix)

        # Step 3: Enter Credentials
        enter_credentials(wait,
                          credentials[CSV_USERNAME_HEADER],
                          credentials[CSV_PASSWORD_HEADER],
                          log_prefix)

        # Step 4: Submit Initial Login
        submit_initial_login(wait, log_prefix)

        # Step 5: Handle 2FA (PIN/TOTP)
        pin_or_totp = credentials.get(CSV_2FA_HEADER, '') # Get secret/pin once
        two_fa_success = handle_two_factor_auth(wait, pin_or_totp, log_prefix)

        # Step 6: Final message based on outcome
        if two_fa_success: # Check if 2FA step completed ok (or wasn't needed)
            print(f"[{log_prefix}] Login flow steps completed (Verify visually in browser).")
            login_successful = True
        else:
            print(f"[{log_prefix}] Login flow failed during or before 2FA step.")
            login_successful = False


    except (TimeoutException, NoSuchElementException) as e:
        error_type = type(e).__name__
        print(f"[{log_prefix}] ERROR ({error_type}): Issue during login flow before 2FA handling.")
        print(f"[{log_prefix}] Details: {e}")
        if driver:
            try: driver.save_screenshot(f"{log_prefix}_{error_type.lower()}_error.png")
            except Exception: pass
    except KeyError as e:
        print(f"[{log_prefix}] ERROR: Missing expected key in credentials dictionary: {e}. Check CSV headers.")
    except Exception as e:
        print(f"[{log_prefix}] UNEXPECTED ERROR during login orchestration for {log_prefix}: {e}")
        traceback.print_exc()
        if driver:
            try: driver.save_screenshot(f"{log_prefix}_unexpected_error.png")
            except Exception: pass

    finally:
        # Adhering to 'detach' logic - driver is not quit automatically.
        # Optional: Could add logic to quit if login_successful is False
        if login_successful:
             print(f"[{log_prefix}] Browser window will remain open (Login likely successful).")
        else:
             print(f"[{log_prefix}] Browser window will remain open (Login likely FAILED).")
        print(f"[{log_prefix}] Login thread execution complete.")
        print("="*34) # Separator at end of thread execution

# ==============================================================================
# --- Main Execution Logic ---
# ==============================================================================

def main():
    """
    Main function: Reads credentials and launches login threads.
    """
    print("--- Zerodha Multi-Account Login Script (Single File) ---")

    # --- Read Credentials ---
    accounts_data = read_credentials(CREDENTIALS_FILE)
    if accounts_data is None:
        print("Exiting due to credential reading errors.")
        sys.exit(1)

    # --- Launch Threads ---
    threads = []
    launch_delay = BROWSER_LAUNCH_DELAY
    print(f"\nLaunching login threads for {len(accounts_data)} account(s)...")
    print(f"(Delay between launches: {launch_delay}s)")

    for i, credentials_for_thread in enumerate(accounts_data):
        print("-" * 30)
        print(f"DEBUG: Preparing Thread #{i+1} for account: {credentials_for_thread.get(CSV_USERNAME_HEADER, 'N/A')}")
        # Print credentials being passed to this specific thread
        # pprint.pprint(credentials_for_thread) # Already printed inside the thread now

        thread = threading.Thread(target=run_single_login_session, args=(credentials_for_thread,), daemon=True)
        threads.append(thread)
        print(f"DEBUG: Starting Thread #{i+1}...")
        thread.start()

        # Stagger browser launches only if there are more threads to launch
        if i < len(accounts_data) - 1:
             time.sleep(launch_delay)
             print(f"DEBUG: Paused for {launch_delay}s after starting Thread #{i+1}.")
        else:
             print(f"DEBUG: Last thread started.")

    print(f"\nLaunched {len(threads)} login threads.")
    print("Main thread will exit shortly (threads are daemons).")
    print("Monitor browser windows and terminal output for progress/errors.")
    print("Close browser windows manually when finished.")

# --- Script Entry Point ---
if __name__ == "__main__":
    main()