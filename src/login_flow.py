# src/login_flow.py
"""Contains functions for executing the Zerodha login steps using Selenium."""

import time
import pyotp
import traceback
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException # Import specific exceptions
from . import constants # Relative import

def navigate_and_wait(driver, username_log_prefix):
    """Navigates to the login URL and returns a WebDriverWait object."""
    url = constants.ZERODHA_LOGIN_URL
    timeout = constants.WEBDRIVER_WAIT_TIMEOUT
    print(f"[{username_log_prefix}] Navigating to {url}...")
    driver.get(url)
    print(f"[{username_log_prefix}] Pausing {constants.SHORT_DELAY}s after page navigation...")
    time.sleep(constants.SHORT_DELAY)
    return WebDriverWait(driver, timeout)

def enter_credentials(wait, username_val, password_val, username_log_prefix):
    """Enters username and password into the respective fields."""
    print(f"[{username_log_prefix}] Entering username...")
    username_input = wait.until(EC.presence_of_element_located(constants.USER_ID_INPUT_LOCATOR))
    username_input.send_keys(username_val)
    time.sleep(constants.INTER_KEY_DELAY)

    print(f"[{username_log_prefix}] Entering password...")
    password_input = wait.until(EC.presence_of_element_located(constants.PASSWORD_INPUT_LOCATOR))
    password_input.send_keys(password_val)
    time.sleep(constants.INTER_KEY_DELAY)

def submit_initial_login(wait, username_log_prefix):
    """Clicks the initial login submit button."""
    print(f"[{username_log_prefix}] Clicking login button...")
    login_button = wait.until(EC.element_to_be_clickable(constants.LOGIN_SUBMIT_BUTTON_LOCATOR))
    login_button.click()
    print(f"[{username_log_prefix}] Pausing {constants.POST_LOGIN_CLICK_DELAY}s after login click (waiting for 2FA page)...")
    time.sleep(constants.POST_LOGIN_CLICK_DELAY)

def handle_two_factor_auth(wait, pin_or_totp_secret, username_log_prefix):
    """Handles the 2FA screen (PIN or TOTP)."""
    try:
        # --- IMPORTANT: Verify constants.PIN_INPUT_LOCATOR uses the correct ID ---
        pin_input = wait.until(EC.presence_of_element_located(constants.PIN_INPUT_LOCATOR))
        # If the above line works, 2FA screen is detected.
        print(f"[{username_log_prefix}] 2FA screen detected (using locator: {constants.PIN_INPUT_LOCATOR}).")

        pin_or_totp_secret = pin_or_totp_secret.strip() # Trim whitespace
        print(f"[{username_log_prefix}] DEBUG: Value read for PIN/TOTP Secret: '{pin_or_totp_secret}'")

        if not pin_or_totp_secret:
            print(f"[{username_log_prefix}] WARNING: 2FA screen detected, but no PIN/TOTP found in credentials file.")
            return # Stop processing 2FA for this user

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
        pin_input.send_keys(current_value_to_send)

        # Pause *after* sending keys, *before* waiting for submit
        print(f"[{username_log_prefix}] DEBUG: Pausing {constants.POST_2FA_KEY_DELAY}s after sending keys...")
        time.sleep(constants.POST_2FA_KEY_DELAY)

        print(f"[{username_log_prefix}] Waiting for PIN/TOTP submit button...")
        pin_submit_button = wait.until(EC.element_to_be_clickable(constants.PIN_SUBMIT_BUTTON_LOCATOR))
        print(f"[{username_log_prefix}] Submitting PIN/TOTP...")
        pin_submit_button.click()

        print(f"[{username_log_prefix}] Pausing {constants.POST_FINAL_SUBMIT_DELAY}s after final submit...")
        time.sleep(constants.POST_FINAL_SUBMIT_DELAY)
        print(f"[{username_log_prefix}] Login submitted successfully after 2FA.")

    except TimeoutException:
        # This block executes if the PIN input element is *not* found within the timeout.
        print(f"[{username_log_prefix}] 2FA screen (PIN input with locator '{constants.PIN_INPUT_LOCATOR}') not detected after initial login.")
        if not pin_or_totp_secret.strip():
             print(f"[{username_log_prefix}] Login proceeded (assuming no 2FA needed or page loaded differently).")
        else:
             print(f"[{username_log_prefix}] WARNING: PIN/TOTP was provided, but 2FA screen with expected input did not appear.")

    except Exception as e:
        # Catch errors specifically during 2FA handling
        print(f"[{username_log_prefix}] ERROR during 2FA handling: {e}")
        traceback.print_exc()