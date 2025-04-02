# Zerodha Multi-Account Login Framework

This script provides a basic framework for logging into multiple Zerodha Kite accounts simultaneously using Selenium and Python. It reads credentials from a CSV file and opens each account in a separate Chrome browser window.

**⚠️ IMPORTANT WARNINGS & DISCLAIMERS ⚠️**

- **Terms of Service:** Automating logins may violate Zerodha's Terms of Service. Use this script responsibly and **at your own risk**. The author assumes no liability for any consequences of using this script, including account suspension.
- **Security:** Storing credentials in a plain text CSV file is inherently insecure. Ensure this file is stored securely and **never commit your actual credentials file (`zerodha_credentials.csv`)** to version control (e.g., Git, GitHub). Use the included `.gitignore` file.
- **Maintenance:** Zerodha's website structure can change at any time without notice, which **will break this script**. You will need to update the Selenium locators (IDs, XPaths) in `src/auto_login.py` if this happens. This script is provided as-is without guarantees of future functionality.
- **Not for Trading:** This script only handles the login process. It does **not** perform any trading actions.
- **Resource Intensive:** Running multiple Chrome instances simultaneously can consume significant CPU and RAM.

## Features

- Logs into multiple Zerodha accounts concurrently using threading.
- Reads credentials from a `config/zerodha_credentials.csv` file.
- Supports 2FA using TOTP (Time-based One-Time Password) secrets (e.g., from Google Authenticator) or static PINs.
- Keeps browser windows open after login for manual inspection (using Selenium's 'detach' option).

## Prerequisites

- **Python 3.7+:** Download from [python.org](https://www.python.org/downloads/).
- **Google Chrome:** The script uses Chrome. Download from [google.com/chrome](https://www.google.com/chrome/).
- **Git:** For cloning the repository. Download from [git-scm.com](https://git-scm.com/downloads).

## Setup Instructions

1.  **Clone the Repository:**

    ```bash
    git clone <repository-url> # Replace <repository-url> with the actual URL
    cd zerodha-multi-login
    ```

2.  **Create a Virtual Environment (Recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Download ChromeDriver:**

    - Follow the instructions in the `drivers/README_DRIVERS.md` file carefully to download the correct version of ChromeDriver for your Chrome browser and operating system.
    - Ensure the `chromedriver` executable is either placed in your system's PATH or you modify the path directly in `src/auto_login.py` (see `drivers/README_DRIVERS.md` for details).

5.  **Configure Credentials:**
    - Copy the example credentials file:
      ```bash
      cp config/zerodha_credentials.csv.example config/zerodha_credentials.csv
      ```
    - **Edit `config/zerodha_credentials.csv`** with a text editor.
    - Replace the placeholder data with your actual Zerodha usernames, passwords, and PINs or TOTP secrets.
    - See the comments in the `.csv` file for guidance on format.
    - **SAVE THE FILE SECURELY AND DO NOT COMMIT IT.**

## Running the Script

1.  Ensure your virtual environment is active (if you created one).
2.  Navigate to the `zerodha-multi-login` directory in your terminal.
3.  Run the script:

    ```bash
    python3 src/auto_login.py
    ```

4.  The script will read the CSV file and attempt to log in to each account in a separate Chrome window.
5.  Observe the terminal output for progress and potential errors for each account.
6.  The browser windows should remain open after the script finishes, allowing you to interact with the logged-in sessions. Close them manually when done.

## How it Works

- The `main` function reads account details from the CSV.
- For each account, it starts a new Python `Thread`.
- The `login_zerodha` function runs within each thread, controlling a dedicated Selenium WebDriver instance (Chrome).
- It navigates to the Kite login page, enters credentials, and handles the 2FA step (if applicable).
- The `pyotp` library generates TOTP codes if a secret key is provided in the CSV.
- Selenium's `detach` option prevents the browser from closing automatically when the script/WebDriver session technically ends.

## Troubleshooting

- **No Chrome Windows Open / ChromeDriver Errors:**
  - Verify ChromeDriver version matches your Chrome version.
  - Ensure `chromedriver` is executable (`chmod +x path/to/chromedriver` on Mac/Linux).
  - Ensure `chromedriver` is in your system PATH or the path is correctly specified in `src/auto_login.py`.
  - Check `drivers/README_DRIVERS.md`.
- **Script Exits Immediately / `FileNotFoundError`:**
  - Make sure you are running the script from the `zerodha-multi-login` directory.
  - Verify `config/zerodha_credentials.csv` exists and is named correctly.
- **Errors Reading CSV / No Accounts Found:**
  - Check that `config/zerodha_credentials.csv` has the exact headers: `Username,Password,PIN/TOTP Secret`.
  - Ensure the file is saved as UTF-8.
  - Make sure there are valid entries for `Username` and `Password` in the rows you want to use.
- **Login Fails / Errors During Login:**
  - Zerodha's website might have changed. You may need to update element IDs or XPaths in `src/auto_login.py`. Inspect the elements on the Kite login page using your browser's developer tools.
  - Check the terminal output for specific error messages (e.g., TimeoutException, NoSuchElementException).
  - Ensure your credentials in the CSV are correct.
  - If using TOTP, verify the secret key is correct and your system clock is synchronized.
