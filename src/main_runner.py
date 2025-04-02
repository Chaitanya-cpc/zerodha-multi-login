# src/main_runner.py
"""
Main entry point for the Zerodha Multi-Account Login Script.

Reads configuration, launches concurrent login threads, and orchestrates
the login process by calling functions from other modules.
"""

import threading
import time
import sys
import traceback
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import modules from the src package using relative imports
from . import constants
from . import config_reader
from . import driver_setup
from . import login_flow

def run_single_login_session(credentials):
    """
    Orchestrates the login process for a single Zerodha account in its own thread.

    Args:
        credentials (dict): A dictionary containing account credentials.
    """
    username = credentials.get(constants.CSV_USERNAME_HEADER, 'UNKNOWN_USER')
    driver = None # Initialize driver to None for robust error handling

    try:
        # Step 1: Setup WebDriver
        driver = driver_setup.setup_driver(username)
        if not driver:
            print(f"[{username}] Aborting thread due to driver setup failure.")
            return # Exit this thread

        # Step 2: Navigate to Login Page and get WebDriverWait
        wait = login_flow.navigate_and_wait(driver, username)

        # Step 3: Enter Credentials
        login_flow.enter_credentials(wait,
                                     credentials[constants.CSV_USERNAME_HEADER],
                                     credentials[constants.CSV_PASSWORD_HEADER],
                                     username)

        # Step 4: Submit Initial Login
        login_flow.submit_initial_login(wait, username)

        # Step 5: Handle 2FA (PIN/TOTP)
        pin_or_totp = credentials.get(constants.CSV_2FA_HEADER, '') # Get secret once
        login_flow.handle_two_factor_auth(wait, pin_or_totp, username)

        # Step 6: Final message (browser remains open)
        print(f"[{username}] Browser window should be open. Check for login success/failure.")
        print(f"[{username}] Close the browser window manually when finished.")

    except (TimeoutException, NoSuchElementException) as e:
        # Handle common Selenium errors during the flow
        error_type = type(e).__name__
        print(f"[{username}] ERROR ({error_type}): Issue during login flow. Website structure may have changed or element not found in time.")
        print(f"[{username}] Error details: {e}")
        if driver:
            try:
                driver.save_screenshot(f"{username}_{error_type.lower()}_error.png")
                print(f"[{username}] Screenshot saved: {username}_{error_type.lower()}_error.png")
            except Exception as screen_err:
                print(f"[{username}] Failed to save screenshot: {screen_err}")
    except KeyError as e:
        print(f"[{username}] ERROR: Missing expected key in credentials dictionary: {e}. Check CSV headers ('{constants.CSV_USERNAME_HEADER}', '{constants.CSV_PASSWORD_HEADER}').")
    except Exception as e:
        # Catch any other unexpected errors during the orchestration
        print(f"[{username}] UNEXPECTED ERROR during login orchestration for {username}: {e}")
        traceback.print_exc()
        if driver:
            try:
                driver.save_screenshot(f"{username}_unexpected_error.png")
                print(f"[{username}] Screenshot saved: {username}_unexpected_error.png")
            except Exception as screen_err:
                print(f"[{username}] Failed to save screenshot: {screen_err}")

    # Note: No 'finally' block with driver.quit() because the 'detach' option keeps the browser open.
    print(f"[{username}] Login attempt thread finished.")


def main():
    """
    Main function: Reads credentials and launches login threads.
    """
    print("--- Zerodha Multi-Account Login Script ---")

    # --- Read Credentials ---
    accounts_data = config_reader.read_credentials()
    if accounts_data is None:
        print("Exiting due to credential reading errors.")
        sys.exit(1) # Exit script

    # --- Launch Threads ---
    threads = []
    launch_delay = constants.BROWSER_LAUNCH_DELAY
    print(f"Launching login threads (with a {launch_delay}s delay between each)...")

    for credentials in accounts_data:
        # Target the orchestrator function for a single session
        thread = threading.Thread(target=run_single_login_session, args=(credentials,), daemon=True)
        threads.append(thread)
        thread.start()
        # Stagger browser launches
        time.sleep(launch_delay)

    print(f"\nLaunched {len(threads)} login threads.")
    print("Main thread is running. Browser windows launched via threads.")
    print("Browsers will remain open after this script potentially exits due to the 'detach' option.")
    print("Close browser windows manually when finished.")
    print("Monitor individual browser windows and terminal output for login status/errors.")

    # Optional: Keep main thread alive briefly or wait for non-daemon threads using join()
    # Since threads are daemon, main can exit while browsers stay open.

if __name__ == "__main__":
    main()