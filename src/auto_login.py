"""
Zerodha Multi-Account Login Script using Selenium and Threading

This script automates the login process for multiple Zerodha accounts simultaneously
using Selenium and Python's threading module. It reads credentials from a CSV file
and handles TOTP generation if a secret key is provided.

Please refer to the main README.md for setup and usage instructions.
"""

import csv
import threading
import time # Imported time module
import sys
import os
import pyotp # For TOTP generation

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
# --- Added: Small delay configuration ---
SHORT_DELAY = 0.75 # Seconds for minor pauses after actions

def login_zerodha(credentials):
    """
    Handles the login process for a single Zerodha account in a separate Chrome window.

    Args:
        credentials (dict): A dictionary containing 'Username', 'Password',
                            and optionally 'PIN/TOTP Secret' for the account.
    """
    username = credentials.get('Username', 'UNKNOWN')
    driver = None # Initialize driver to None for cleanup in case of early failure

    try:
        print(f"[{username}] Setting up Chrome options...")
        options = Options()
        options.add_experimental_option("detach", True)
        options.headless = False

        # --- WebDriver Service Setup ---
        # By default, Selenium tries to find chromedriver in PATH.
        # If you need to specify the path, uncomment and modify the line below.
        # See drivers/README_DRIVERS.md for more details.
        # service = Service('/path/to/your/chromedriver')
        # driver = webdriver.Chrome(service=service, options=options)
        try:
            print(f"[{username}] Launching Chrome browser...")
            # Assumes chromedriver is in PATH if service is not specified
            driver = webdriver.Chrome(options=options)
        except Exception as e:
            print(f"[{username}] CRITICAL ERROR: Failed to launch Chrome. Ensure ChromeDriver is installed and in PATH.")
            print(f"[{username}] Error details: {e}")
            return # Exit this thread if browser fails to launch

        print(f"[{username}] Navigating to {ZERODHA_LOGIN_URL}...")
        driver.get(ZERODHA_LOGIN_URL)
        # --- Added Delay ---
        print(f"[{username}] Pausing {SHORT_DELAY}s after page navigation...")
        time.sleep(SHORT_DELAY)
        # -----------------
        wait = WebDriverWait(driver, WEBDRIVER_WAIT_TIMEOUT)

        # --- Step 1: Enter Username and Password ---
        print(f"[{username}] Entering username...")
        username_input = wait.until(EC.presence_of_element_located((By.ID, "userid")))
        username_input.send_keys(credentials['Username'])
        # --- Added Delay ---
        time.sleep(SHORT_DELAY / 2) # Shorter pause after typing
        # -----------------

        print(f"[{username}] Entering password...")
        password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_input.send_keys(credentials['Password'])
        # --- Added Delay ---
        time.sleep(SHORT_DELAY / 2) # Shorter pause after typing
        # -----------------

        print(f"[{username}] Clicking login button...")
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        login_button.click()
        # --- Added Delay ---
        print(f"[{username}] Pausing {SHORT_DELAY}s after login click (waiting for 2FA page)...")
        time.sleep(SHORT_DELAY)
        # -----------------

        # --- Step 2: Handle PIN or TOTP ---
        # Check if the 2FA screen has appeared by looking for the PIN input field
        try:
            pin_input = wait.until(EC.presence_of_element_located((By.ID, "userid"))) # Changed ID to "userid"
            print(f"[{username}] 2FA screen detected.")

            # --- Start of Corrected Debugging Code Block ---
            # --- Trim whitespace from the secret ---
            pin_or_totp_secret = credentials.get('PIN/TOTP Secret', '').strip()

            # --- DEBUG PRINT 1: Show the value read from CSV ---
            print(f"[{username}] DEBUG: Value read for PIN/TOTP Secret: '{pin_or_totp_secret}'")
            # ----------------------------------------------------

            if pin_or_totp_secret:
                print(f"[{username}] Attempting to enter PIN/TOTP...")
                current_value_to_send = "" # Initialize variable
                try:
                    # Check if it looks like a TOTP secret (adjust logic if needed)
                    if len(pin_or_totp_secret) > 8 and pin_or_totp_secret.isalnum() and not pin_or_totp_secret.isdigit():
                        # --- DEBUG PRINT 2: Indicate TOTP attempt ---
                        print(f"[{username}] DEBUG: Treating as TOTP Secret.")
                        # --------------------------------------------
                        totp = pyotp.TOTP(pin_or_totp_secret)
                        current_otp = totp.now()
                        # --- DEBUG PRINT 3: Show generated TOTP ---
                        print(f"[{username}] DEBUG: Generated TOTP: {current_otp}")
                        # ------------------------------------------
                        current_value_to_send = current_otp
                    else:
                        # Assume it's a static PIN or other value
                        # --- DEBUG PRINT 4: Indicate Static PIN attempt ---
                        print(f"[{username}] DEBUG: Treating as static PIN/Other value.")
                        # -------------------------------------------------
                        current_value_to_send = pin_or_totp_secret

                    # --- Send Keys ---
                    print(f"[{username}] DEBUG: Sending keys: '{current_value_to_send}'")
                    pin_input.send_keys(current_value_to_send)
                    # -----------------

                    # --- Added Delay: Small pause *after* sending keys, *before* waiting for submit ---
                    print(f"[{username}] DEBUG: Pausing 1s after sending keys...")
                    time.sleep(1) # Adjust if needed (0.5 to 1.5 seconds is usually enough)
                    # -----------------------------------------------------------------------------

                    print(f"[{username}] Waiting for PIN/TOTP submit button...")
                    pin_submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
                    print(f"[{username}] Submitting PIN/TOTP...")
                    pin_submit_button.click()
                    # --- Kept existing delay after final submit ---
                    print(f"[{username}] Pausing {SHORT_DELAY}s after final submit...")
                    time.sleep(SHORT_DELAY)
                    # --------------------------------------------
                    print(f"[{username}] Login submitted successfully after 2FA.")

                except Exception as totp_error:
                    print(f"[{username}] ERROR handling PIN/TOTP input/submit: {totp_error}")
                    # Consider adding screenshot here
                    # if driver: driver.save_screenshot(f"{username}_totp_error.png")

            else:
                print(f"[{username}] WARNING: 2FA screen detected, but no PIN/TOTP found in credentials file.")
                # Script will likely be stuck here if 2FA is required but not provided
            # --- End of Corrected Debugging Code Block ---

        except TimeoutException:
            # --- This part handles when the PIN input is *not* found ---
            pin_or_totp_secret = credentials.get('PIN/TOTP Secret', '').strip() # Get secret again just to check if one was provided for the warning
            print(f"[{username}] 2FA screen (PIN input) not detected after login.")
            if not pin_or_totp_secret:
                 print(f"[{username}] Login submitted successfully (assuming no 2FA needed).")
            else:
                 print(f"[{username}] WARNING: PIN/TOTP was provided in CSV, but 2FA screen did not appear.")
            # --- End of TimeoutException handling ---


        print(f"[{username}] Browser window open. Press Enter in the main terminal window when finished with ALL browsers to allow script exit.")

    except TimeoutException as e:
        print(f"[{username}] ERROR: A timeout occurred waiting for an element. Page might not have loaded correctly or element ID/XPATH changed.")
        print(f"[{username}] Error details: {e}")
    except NoSuchElementException as e:
        print(f"[{username}] ERROR: An element was not found. Zerodha's website structure might have changed.")
        print(f"[{username}] Error details: {e}")
    except Exception as e:
        # Catch any other unexpected errors during the login process
        import traceback
        print(f"[{username}] UNEXPECTED ERROR during login process: {e}")
        traceback.print_exc() # Print full traceback for debugging
        # if driver: driver.save_screenshot(f"{username}_unexpected_error.png")
    # Note: The 'finally' block is not used here because the 'detach' option
    # is intended to keep the browser open. Closing the driver here would defeat that.
    # If 'detach' is removed, driver.quit() should be called in a 'finally' block.
    print(f"[{username}] Login attempt finished (browser may remain open due to 'detach' option).")


def main():
    """
    Main function to read credentials and launch login threads.
    """
    print("--- Zerodha Multi-Account Login Script ---")
    accounts_data = []

    # --- Read Credentials ---
    print(f"Reading credentials from: {CREDENTIALS_FILE}")
    try:
        # Explicitly use utf-8-sig to handle potential BOM (Byte Order Mark)
        with open(CREDENTIALS_FILE, mode='r', newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            required_headers = ['Username', 'Password', 'PIN/TOTP Secret']
            # Check if essential headers exist
            if not reader.fieldnames or not all(header in reader.fieldnames for header in required_headers[:2]):
                 print(f"ERROR: Credentials file is missing required headers ('Username', 'Password') or is empty.")
                 print(f"Found headers: {reader.fieldnames}")
                 sys.exit(1) # Exit script if headers are wrong or missing

            for i, row in enumerate(reader):
                # Basic validation: Ensure Username and Password are not empty
                username = row.get("Username", "").strip()
                password = row.get("Password", "").strip()
                if username and password:
                    accounts_data.append(row)
                else:
                    print(f"WARNING: Skipping row {i+1} in CSV due to missing Username or Password.")

        if not accounts_data:
             print("ERROR: No valid account credentials found in the CSV file.")
             sys.exit(1)

        print(f"Found {len(accounts_data)} account(s) with valid Username/Password.")

    except FileNotFoundError:
        print(f"ERROR: Credentials file not found at '{CREDENTIALS_FILE}'.")
        print("Please ensure the file exists and the path is correct.")
        print(f"Expected location: {os.path.abspath(CREDENTIALS_FILE)}")
        sys.exit(1) # Exit script if file not found
    except Exception as e:
        print(f"ERROR: Failed to read or parse credentials file: {e}")
        sys.exit(1)

    # --- Launch Threads ---
    threads = []
    # --- Added: Delay between starting browsers ---
    BROWSER_LAUNCH_DELAY = 2 # Seconds between launching each browser instance
    print(f"Launching login threads (with a {BROWSER_LAUNCH_DELAY}s delay between each)...")
    # ---------------------------------------------
    for credentials in accounts_data:
        thread = threading.Thread(target=login_zerodha, args=(credentials,), daemon=True)
        # Using daemon=True allows the main script to exit even if these threads get stuck
        threads.append(thread)
        thread.start()
        # --- Added Delay ---
        time.sleep(BROWSER_LAUNCH_DELAY) # Stagger browser launches
        # -----------------

    print("Main thread is running. Browser windows launched via threads.")
    print("Browsers will remain open after this script potentially exits due to the 'detach' option.")
    print("Close browser windows manually when finished.")

    # If you want the main script to wait until all threads *finish their execution*
    # (i.e., after you press Enter in each thread's console context if using input()),
    # you would remove daemon=True and use join():
    # for thread in threads:
    #     thread.join()
    # print("All login threads have completed their execution.")

if __name__ == "__main__":
    main()