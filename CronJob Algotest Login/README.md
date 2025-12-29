# AlgoTest Login Automation

This script automates the login process for both Zerodha (BU0542 account) and AlgoTest.in/live platforms.

## Features

1. **Zerodha Login**: Automatically logs into BU0542 Zerodha account
2. **Tab Management**: Opens algotest.in/live in a new browser tab
3. **AlgoTest Login**: Attempts to automatically login to AlgoTest (requires credential configuration)

## Setup

### 1. Zerodha Credentials

The script uses credentials from `config/zerodha_credentials.csv`. The BU0542 account credentials should already be present in that file.

**Note**: This script bypasses status filtering, so BU0542 will work even if its status is "0" in the CSV.

### 2. AlgoTest Credentials

Add your AlgoTest login credentials to `algotest_credentials.json`:

```json
{
  "algotest": {
    "username": "your_email@example.com",
    "password": "your_password"
  }
}
```

## Usage

Run the script:

```bash
python "CronJob Algotest Login/algotest_login.py"
```

## Process Flow

1. **Step 1**: Logs into Zerodha BU0542 account
   - Opens Zerodha login page
   - Enters username and password
   - Handles 2FA (TOTP or PIN)
   - Completes login

2. **Step 2**: Opens AlgoTest tab
   - Opens a new tab in the same browser
   - Navigates to https://algotest.in/live

3. **Step 3**: Logs into AlgoTest
   - Attempts to find and fill login form
   - Submits credentials
   - If automatic login fails, browser remains open for manual login

## Troubleshooting

### AlgoTest Login Not Working

If automatic AlgoTest login fails:

1. Check that credentials are correctly set in `algotest_credentials.json`
2. The script will save page source to `algotest_page_source.html` for inspection
3. You may need to update the locators in the script based on the actual AlgoTest login page structure
4. The browser will remain open so you can login manually

### Updating AlgoTest Locators

If the AlgoTest login form structure changes, you'll need to update the locators in `algotest_login.py`:

```python
# Update these in the Config class:
ALGOTEST_USERNAME_LOCATOR = (By.NAME, "email")  # Update based on actual field
ALGOTEST_PASSWORD_LOCATOR = (By.NAME, "password")  # Update based on actual field
ALGOTEST_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "//button[@type='submit']")  # Update based on actual button
```

## Next Steps

Once the basic login flow is working, you can extend this script with additional automation features as needed.

