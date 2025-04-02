"""
Zerodha Multi-Account Login Script using Selenium and Threading (Refactored)

This script automates the login process for multiple Zerodha accounts simultaneously
using Selenium and Python's threading module. It reads credentials from a CSV file
and handles TOTP generation if a secret key is provided.

This version refactors the main login logic into smaller helper functions
for better readability and maintainability within the same file.

Please refer to the main README.md for setup and usage instructions.
"""

import csv
import threading
import time
import sys
import os
import pyotp # For TOTP generation
import traceback # For detailed error logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- Configuration ---
# Determine the base directory of the script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Goes up one level from src/
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, 'zerodha_credentials.csv')
ZERODHA_LOGIN_URL = "https://kite.zerodha.com/"
WEBDRIVER_WAIT_TIMEOUT = 30 # Increased timeout
SHORT_DELAY = 0.75 # Seconds for minor pauses after actions
BROWSER_LAUNCH_DELAY = 2 # Seconds between launching each browser instance

# --- Helper Functions for Login Steps ---

def setup_driver(username):
    """Sets up and returns a Selenium Chrome WebDriver instance."""
    print(f"[{username}] Setting up Chrome options...")
    driver = None
    try:
        options = Options()
        options.add_experimental_option("detach", True) # Keep browser open
        options.headless = False # Run in non-headless mode

        # --- WebDriver Service Setup ---
        # By default, Selenium tries to find chromedriver in PATH.
        # If you need to specify the path, uncomment and modify the line below.
        # See drivers/README_DRIVERS.md for more details.
        # service = Service('/path/to/your/chromedriver')
        # driver = webdriver.Chrome(service=service, options=options)

        print(f"[{username}] Launching Chrome browser...")
        # Assumes chromedriver is in PATH if service is not specified
        driver = webdriver.Chrome(options=options)
        print(f"[{username}] Chrome launched successfully.")
        return driver
    except Exception as e:
        print(f"[{username}] CRITICAL ERROR: Failed to launch Chrome. Ensure ChromeDriver is installed and in PATH.")
        print(f"[{username}] Error details: {e}")
        if driver: # Attempt cleanup if partially initialized
            driver.quit()
        return None # Indicate failure


def navigate_and_wait(driver, url, timeout, username):
    """Navigates to the URL and returns a WebDriverWait object."""
    print(f"[{username}] Navigating to {url}...")
    driver.get(url)
    print(f"[{username}] Pausing {SHORT_DELAY}s after page navigation...")
    time.sleep(SHORT_DELAY)
    return WebDriverWait(driver, timeout)


def enter_credentials(wait, username_val, password_val, username_log_prefix):
    """Enters username and password into the respective fields."""
    print(f"[{username_log_prefix}] Entering username...")
    username_input = wait.until(EC.presence_of_element_located((By.ID, "userid")))
    username_input.send_keys(username_val)
    time.sleep(SHORT_DELAY / 2) # Shorter pause after typing

    print(f"[{username_log_prefix}] Entering password...")
    password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
    password_input.send_keys(password_val)
    time.sleep(SHORT_DELAY / 2) # Shorter pause after typing


def submit_initial_login(wait, username_log_prefix):
    """Clicks the initial login submit button."""
    print(f"[{username_log_prefix}] Clicking login button...")
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
    login_button.click()
    print(f"[{username_log_prefix}] Pausing {SHORT_DELAY}s after login click (waiting for 2FA page)...")
    time.sleep(SHORT_DELAY)


def handle_two_factor_auth(wait, pin_or_totp_secret, username_log_prefix):
    """Handles the 2FA screen (PIN or TOTP)."""
    try:
        # --- IMPORTANT: Verify this ID is correct for the 2FA PIN input ---
        # It's likely NOT 'userid'. Inspect the element on the 2FA page.
        # Common IDs might be 'pin', 'mfapin', 'twofa', etc.
        # Using a placeholder ID for now - MUST BE CORRECTED.
        pin_input_id = "pin" # <-- Replace with the ACTUAL ID of the PIN input
        pin_input = wait.until(EC.presence_of_element_located((By.ID, pin_input_id)))
        # If the above line works, 2FA screen is detected.
        print(f"[{username_log_prefix}] 2FA screen detected (using ID: {pin_input_id}).") # Log which ID we are using

        pin_or_totp_secret = pin_or_totp_secret.strip() # Trim whitespace

        print(f"[{username_log_prefix}] DEBUG: Value read for PIN/TOTP Secret: '{pin_or_totp_secret}'")

        if not pin_or_totp_secret:
            print(f"[{username_log_prefix}] WARNING: 2FA screen detected, but no PIN/TOTP found in credentials file.")
            # Script will likely be stuck here if 2FA is required but not provided
            return # Stop processing 2FA for this user

        print(f"[{username_log_prefix}] Attempting to enter PIN/TOTP...")
        current_value_to_send = ""

        # Check if it looks like a TOTP secret
        # (basic heuristic: > 8 chars, alphanumeric, not purely digits)
        if len(pin_or_totp_secret) > 8 and pin_or_totp_secret.isalnum() and not pin_or_totp_secret.isdigit():
            print(f"[{username_log_prefix}] DEBUG: Treating as TOTP Secret.")
            try:
                totp = pyotp.TOTP(pin_or_totp_secret)
                current_otp = totp.now()
                print(f"[{username_log_prefix}] DEBUG: Generated TOTP: {current_otp}")
                current_value_to_send = current_otp
            except Exception as totp_gen_error:
                print(f"[{username_log_prefix}] ERROR generating TOTP: {totp_gen_error}")
                return # Cannot proceed without OTP
        else:
            # Assume it's a static PIN or other value
            print(f"[{username_log_prefix}] DEBUG: Treating as static PIN/Other value.")
            current_value_to_send = pin_or_totp_secret

        # --- Send Keys ---
        print(f"[{username_log_prefix}] DEBUG: Sending keys: '{current_value_to_send}'")
        pin_input.send_keys(current_value_to_send)

        # Pause *after* sending keys, *before* waiting for submit
        print(f"[{username_log_prefix}] DEBUG: Pausing 1s after sending keys...")
        time.sleep(1)

        print(f"[{username_log_prefix}] Waiting for PIN/TOTP submit button...")
        pin_submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        print(f"[{username_log_prefix}] Submitting PIN/TOTP...")
        pin_submit_button.click()

        print(f"[{username_log_prefix}] Pausing {SHORT_DELAY}s after final submit...")
        time.sleep(SHORT_DELAY)
        print(f"[{username_log_prefix}] Login submitted successfully after 2FA.")

    except TimeoutException:
        # This block executes if the PIN input element (ID: pin_input_id) is *not* found within the timeout.
        print(f"[{username_log_prefix}] 2FA screen (PIN input with ID '{pin_input_id}') not detected after initial login.")
        if not pin_or_totp_secret.strip():
             print(f"[{username_log_prefix}] Login submitted successfully (assuming no 2FA needed or page loaded differently).")
        else:
             # A PIN/TOTP was provided, but the expected input field didn't appear.
             print(f"[{username_log_prefix}] WARNING: PIN/TOTP was provided in CSV, but 2FA screen with input ID '{pin_input_id}' did not appear as expected.")
        # Indicate that 2FA screen wasn't handled or found
        # Depending on Zerodha's flow, this might be okay or an error state

    except Exception as e:
        # Catch errors specifically during 2FA handling (e.g., interacting with elements after finding pin_input)
        print(f"[{username_log_prefix}] ERROR during 2FA handling: {e}")
        traceback.print_exc()
        # Consider adding screenshot here
        # if driver: driver.save_screenshot(f"{username_log_prefix}_2fa_error.png")


# --- Main Orchestration Function ---

def login_zerodha(credentials):
    """
    Orchestrates the login process for a single Zerodha account by calling helper functions.

    Args:
        credentials (dict): A dictionary containing 'Username', 'Password',
                            and optionally 'PIN/TOTP Secret' for the account.
    """
    username = credentials.get('Username', 'UNKNOWN_USER') # Use a default if key missing
    driver = None # Initialize driver to None

    try:
        # Step 1: Setup WebDriver
        driver = setup_driver(username)
        if not driver:
            return # Exit this thread if driver setup failed

        # Step 2: Navigate to Login Page
        wait = navigate_and_wait(driver, ZERODHA_LOGIN_URL, WEBDRIVER_WAIT_TIMEOUT, username)

        # Step 3: Enter Credentials
        enter_credentials(wait, credentials['Username'], credentials['Password'], username)

        # Step 4: Submit Initial Login
        submit_initial_login(wait, username)

        # Step 5: Handle 2FA (PIN/TOTP)
        pin_or_totp = credentials.get('PIN/TOTP Secret', '') # Get secret once
        handle_two_factor_auth(wait, pin_or_totp, username)

        # Step 6: Final message (browser remains open)
        print(f"[{username}] Browser window should be open and potentially logged in.")
        print(f"[{username}] Close the browser window manually when finished.")

    except TimeoutException as e:
        print(f"[{username}] ERROR: A timeout occurred waiting for an element. Page might not have loaded correctly or element ID/XPATH changed.")
        print(f"[{username}] Error details: {e}")
        if driver: driver.save_screenshot(f"{username}_timeout_error.png")
    except NoSuchElementException as e:
        print(f"[{username}] ERROR: An element was not found. Zerodha's website structure might have changed.")
        print(f"[{username}] Error details: {e}")
        if driver: driver.save_screenshot(f"{username}_nosuch_error.png")
    except KeyError as e:
        print(f"[{username}] ERROR: Missing expected key in credentials dictionary: {e}. Check CSV headers ('Username', 'Password').")
    except Exception as e:
        # Catch any other unexpected errors during the overall login process
        print(f"[{username}] UNEXPECTED ERROR during login orchestration for {username}: {e}")
        traceback.print_exc() # Print full traceback for debugging
        if driver: driver.save_screenshot(f"{username}_unexpected_error.png")

    # Note: No 'finally' block with driver.quit() because the 'detach' option
    # is intended to keep the browser open.
    print(f"[{username}] Login attempt thread finished (browser may remain open due to 'detach' option).")


def read_credentials(filepath):
    """Reads credentials from the specified CSV file."""
    accounts_data = []
    print(f"Reading credentials from: {filepath}")
    try:
        # Explicitly use utf-8-sig to handle potential BOM (Byte Order Mark)
        with open(filepath, mode='r', newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            required_headers = ['Username', 'Password'] # PIN/TOTP is optional but needed if present
            # Check if essential headers exist
            if not reader.fieldnames or not all(header in reader.fieldnames for header in required_headers):
                 print(f"ERROR: Credentials file '{filepath}' is missing required headers ('Username', 'Password') or is empty.")
                 print(f"Found headers: {reader.fieldnames}")
                 return None # Indicate failure

            for i, row in enumerate(reader):
                # Basic validation: Ensure Username and Password are not empty
                username = row.get("Username", "").strip()
                password = row.get("Password", "").strip()
                if username and password:
                    # Ensure PIN/TOTP Secret key exists even if empty, for consistency
                    if 'PIN/TOTP Secret' not in row:
                         row['PIN/TOTP Secret'] = '' # Add empty string if column missing
                    accounts_data.append(row)
                else:
                    print(f"WARNING: Skipping row {i+1} in CSV due to missing Username or Password.")

        if not accounts_data:
             print("ERROR: No valid account credentials found in the CSV file.")
             return None

        print(f"Found {len(accounts_data)} account(s) with valid Username/Password.")
        return accounts_data

    except FileNotFoundError:
        print(f"ERROR: Credentials file not found at '{filepath}'.")
        print("Please ensure the file exists and the path is correct.")
        print(f"Expected location: {os.path.abspath(filepath)}")
        return None # Indicate failure
    except Exception as e:
        print(f"ERROR: Failed to read or parse credentials file: {e}")
        traceback.print_exc()
        return None


def main():
    """
    Main function to read credentials and launch login threads.
    """
    print("--- Zerodha Multi-Account Login Script ---")

    # --- Read Credentials ---
    accounts_data = read_credentials(CREDENTIALS_FILE)
    if accounts_data is None:
        sys.exit(1) # Exit script if reading credentials failed

    # --- Launch Threads ---
    threads = []
    print(f"Launching login threads (with a {BROWSER_LAUNCH_DELAY}s delay between each)...")
    for credentials in accounts_data:
        # Pass credentials dict directly to the orchestrator function
        thread = threading.Thread(target=login_zerodha, args=(credentials,), daemon=True)
        # Using daemon=True allows the main script to exit even if these threads get stuck
        threads.append(thread)
        thread.start()
        # Stagger browser launches to avoid resource spikes and potential rate limits
        time.sleep(BROWSER_LAUNCH_DELAY)

    print("\nMain thread is running. Browser windows launched via threads.")
    print("Browsers will remain open after this script potentially exits due to the 'detach' option.")
    print("Close browser windows manually when finished.")
    print("Monitor individual browser windows and terminal output for login status/errors.")

    # Keep the main thread alive briefly to ensure messages are seen,
    # but daemon threads mean it doesn't need to wait indefinitely.
    # If you needed to wait for all threads (e.g., for cleanup), remove daemon=True and use thread.join().
    # time.sleep(5) # Optional brief pause for main thread

if __name__ == "__main__":
    main()