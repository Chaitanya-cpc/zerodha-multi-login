# 🤖 AlgoTest Login Automation

<div align="center">

**Automated Multi-Platform Login Solution**

*Zerodha → AlgoTest Seamless Integration*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.0+-green.svg)](https://selenium-python.readthedocs.io/)
[![Rich](https://img.shields.io/badge/Rich-Terminal%20UI-brightgreen.svg)](https://github.com/Textualize/rich)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Complete Code Structure](#-complete-code-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Process Flow](#-process-flow)
- [Troubleshooting](#-troubleshooting)
- [Development](#-development)

---

## 🎯 Overview

This script automates the complete login flow for both Zerodha (BU0542 account) and AlgoTest.in/live platforms. It provides a seamless, automated solution for traders who need to access both platforms simultaneously in a single browser session.

### Key Highlights

- 🔄 **Multi-Platform Automation** - Zerodha and AlgoTest in one seamless flow
- 🎯 **Targeted Account** - Specifically designed for BU0542 account
- 🚀 **Single Browser Session** - Opens AlgoTest in new tab (no separate window)
- ✨ **Beautiful Terminal UI** - Rich, colorful progress tracking with step-by-step indicators
- 🔐 **Secure Credential Management** - JSON-based configuration with separate credential files
- 📊 **Multi-Step Process Tracking** - Clear visual feedback for each step

---

## ✨ Features

### Core Features

| Feature | Description |
|---------|-------------|
| **Zerodha Login** | Automatic login to BU0542 account with 2FA support |
| **Tab Management** | Opens AlgoTest in new browser tab (same session) |
| **AlgoTest Login** | Automated form filling and submission using XPaths |
| **Status Bypass** | Works regardless of CSV status value for BU0542 |
| **Error Handling** | Comprehensive error capture and logging |
| **Progress Tracking** | Real-time step-by-step progress display |
| **Page Source Debugging** | Saves page source on errors for troubleshooting |

### Technical Features

- **TOTP/PIN Support** - Automatic 2FA handling for Zerodha
- **XPath-Based Locators** - Precise element targeting for AlgoTest
- **Wait Strategies** - Robust element waiting with explicit waits
- **Screenshot Capture** - Error debugging support (if needed)
- **Credential Validation** - Pre-flight checks before execution
- **Beautiful UI** - Enhanced terminal output with Rich library

---

## 🏗️ Architecture

### Script Structure

```
algotest_login.py (500+ lines)
├── Config Class
│   ├── File paths and URLs
│   ├── Timeouts and delays
│   ├── Zerodha locators
│   └── AlgoTest XPath locators
├── AlgoTestUI Class
│   ├── Banner display
│   ├── Logging system
│   └── Progress tracking
├── CredentialManager Class
│   ├── Zerodha credential reading (from CSV)
│   └── AlgoTest credential reading (from JSON)
├── AlgoTestBrowserManager Class
│   ├── Browser setup
│   ├── Zerodha login workflow
│   ├── Tab management (JavaScript execution)
│   └── AlgoTest login workflow
└── Main Function
    └── Orchestration logic
```

### Class Relationships

```
main()
    ↓
AlgoTestUI (Terminal Interface)
    ↓
CredentialManager (Read Credentials)
    ├──→ Zerodha CSV File
    └──→ AlgoTest JSON File
    ↓
AlgoTestBrowserManager (Browser Automation)
    ├──→ setup_driver() → Chrome WebDriver
    ├──→ login_zerodha() → Zerodha Login
    ├──→ open_algotest_tab() → New Tab + Navigate
    └──→ login_algotest() → AlgoTest Login
    ↓
Complete (Browser stays open)
```

### Data Flow

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1: Initialize                                      │
│   ├── Create AlgoTestUI instance                        │
│   ├── Create CredentialManager instance                 │
│   └── Create AlgoTestBrowserManager instance            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 2: Read Credentials                                │
│   ├── Read BU0542 from config/zerodha_credentials.csv  │
│   └── Read AlgoTest from algotest_credentials.json     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 3: Setup Browser                                   │
│   └── Initialize Chrome WebDriver with options          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 4: Login to Zerodha                                │
│   ├── Navigate to kite.zerodha.com                      │
│   ├── Enter username (BU0542)                           │
│   ├── Enter password                                    │
│   ├── Submit login form                                 │
│   ├── Handle 2FA (TOTP or PIN)                          │
│   └── Verify login success                              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 5: Open AlgoTest Tab                               │
│   ├── Execute window.open() JavaScript                  │
│   ├── Switch to new tab                                 │
│   └── Navigate to algotest.in/live                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 6: Login to AlgoTest                               │
│   ├── Click login button (show form)                    │
│   ├── Wait for form to appear                           │
│   ├── Fill phone number field                           │
│   ├── Fill password field                               │
│   ├── Click submit button                               │
│   └── Wait for login completion                         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 7: Complete                                        │
│   └── Browser stays open for use                        │
└─────────────────────────────────────────────────────────┘
```

---

## 📚 Complete Code Structure

### 1. Config Class

**Purpose:** Centralized configuration for all settings including file paths, URLs, timeouts, and XPath locators.

**Key Attributes:**

```python
class Config:
    # File Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    CONFIG_DIR = os.path.join(BASE_DIR, 'config')
    ZERODHA_CREDENTIALS_FILE = os.path.join(CONFIG_DIR, 'zerodha_credentials.csv')
    ALGOTEST_CREDENTIALS_FILE = os.path.join(BASE_DIR, 'CronJob Algotest Login', 'algotest_credentials.json')
    
    # URLs
    ZERODHA_LOGIN_URL = "https://kite.zerodha.com/"
    ALGOTEST_LOGIN_URL = "https://algotest.in/live"
    
    # Zerodha Account
    ZERODHA_ACCOUNT = "BU0542"
    
    # Timeouts
    WEBDRIVER_WAIT_TIMEOUT = 30
    SHORT_DELAY = 0.75
    POST_LOGIN_CLICK_DELAY = 4.0
    POST_2FA_KEY_DELAY = 1.0
    
    # Zerodha Locators
    USER_ID_INPUT_LOCATOR = (By.ID, "userid")
    PASSWORD_INPUT_LOCATOR = (By.ID, "password")
    LOGIN_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "//button[@type='submit']")
    PIN_INPUT_LOCATOR = (By.ID, "userid")
    PIN_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "//button[@type='submit']")
    
    # AlgoTest XPath Locators
    ALGOTEST_LOGIN_BUTTON_LOCATOR = (By.XPATH, "/html/body/div[1]/div/div/div[1]/div[2]/div[1]/button[1]")
    ALGOTEST_PHONE_INPUT_LOCATOR = (By.XPATH, "/html/body/div[1]/div/div/div[3]/form/div[1]/input")
    ALGOTEST_PASSWORD_LOCATOR = (By.XPATH, "/html/body/div[1]/div/div/div[3]/form/div[2]/div/input")
    ALGOTEST_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "/html/body/div[1]/div/div/div[3]/form/button")
```

**Responsibilities:**
- Define file paths for credentials
- Configure Zerodha and AlgoTest URLs
- Set timeouts and delays for operations
- Define Selenium locators for both platforms
- Specify target Zerodha account (BU0542)

### 2. AlgoTestUI Class

**Purpose:** Terminal interface management with beautiful formatting using Rich library.

**Key Methods:**

```python
class AlgoTestUI:
    def __init__(self)
    def print_banner(self) -> None
    def log(self, message: str, level: str = "info") -> None
```

**Features:**
- Beautiful banner display with ASCII art
- Color-coded log messages with timestamps
- Enhanced visual formatting with Rich panels
- Progress indicators for multi-step process
- Consistent styling with main script

**Log Levels:**
- `info` - General information (cyan)
- `success` - Successful operations (green)
- `warning` - Warning messages (yellow)
- `error` - Error messages (red)
- `highlight` - Important highlights (magenta)

### 3. CredentialManager Class

**Purpose:** Handles credential reading from both Zerodha CSV and AlgoTest JSON files.

**Key Methods:**

```python
class CredentialManager:
    def __init__(self, ui: AlgoTestUI)
    def get_zerodha_credentials(self) -> Optional[Dict[str, str]]
    def get_algotest_credentials(self) -> Optional[Dict[str, str]]
```

**Zerodha Credential Reading:**
```
config/zerodha_credentials.csv
    ↓
Read CSV file
    ↓
Filter for BU0542 account
    ↓
Return credentials dict
    ├── user_id: "BU0542"
    ├── password: "***"
    └── pin: "TOTP_SECRET or PIN"
```

**AlgoTest Credential Reading:**
```
algotest_credentials.json
    ↓
Read JSON file
    ↓
Extract algotest section
    ↓
Return credentials dict
    ├── username: "phone_number"
    └── password: "***"
```

**Key Features:**
- Bypasses status check for BU0542 (always processes)
- JSON file parsing with error handling
- Validation of credential structure
- User-friendly error messages

### 4. AlgoTestBrowserManager Class

**Purpose:** Manages browser automation for both Zerodha and AlgoTest platforms.

**Key Methods:**

```python
class AlgoTestBrowserManager:
    def __init__(self, ui: AlgoTestUI)
    def setup_driver(self) -> Optional[webdriver.Chrome]
    def login_zerodha(self, driver: webdriver.Chrome, credentials: Dict[str, str]) -> bool
    def open_algotest_tab(self, driver: webdriver.Chrome) -> bool
    def login_algotest(self, driver: webdriver.Chrome, username: str, password: str) -> bool
```

#### setup_driver()

**Purpose:** Initialize Chrome WebDriver with appropriate options.

**Features:**
- Detach option to keep browser open
- Standard Chrome options
- Error handling and logging

#### login_zerodha()

**Purpose:** Complete Zerodha login workflow for BU0542 account.

**Workflow:**
```
1. Navigate to kite.zerodha.com
2. Wait for page load
3. Enter username (BU0542)
4. Enter password
5. Click submit button
6. Handle 2FA
   ├── Check if TOTP (length > 8, alphanumeric)
   ├── Generate TOTP using pyotp OR use static PIN
   ├── Enter PIN/TOTP
   └── Submit 2FA form
7. Verify login success (check URL)
8. Return success status
```

**Error Handling:**
- Timeout exceptions
- Element not found exceptions
- Screenshot capture on failure
- Detailed error logging

#### open_algotest_tab()

**Purpose:** Open AlgoTest in a new tab within the same browser session.

**Implementation:**
```python
# Execute JavaScript to open new tab
driver.execute_script("window.open('about:blank', '_blank');")

# Switch to new tab
driver.switch_to.window(driver.window_handles[-1])

# Navigate to AlgoTest URL
driver.get(Config.ALGOTEST_LOGIN_URL)

# Wait for page load
WebDriverWait(driver, Config.WEBDRIVER_WAIT_TIMEOUT).until(
    lambda d: d.ready_state == 'complete'
)
```

**Features:**
- JavaScript-based tab opening
- Window handle management
- Page load verification
- Error handling

#### login_algotest()

**Purpose:** Complete AlgoTest login workflow using XPath locators.

**Workflow (Correct Chronology):**
```
1. Click initial login button (show form)
   ├── Locate: /html/body/div[1]/div/div/div[1]/div[2]/div[1]/button[1]
   └── Click to reveal login form
2. Wait for form to appear
3. Fill phone number
   ├── Locate: /html/body/div[1]/div/div/div[3]/form/div[1]/input
   ├── Clear field
   └── Enter phone number
4. Fill password
   ├── Locate: /html/body/div[1]/div/div/div[3]/form/div[2]/div/input
   ├── Clear field
   └── Enter password
5. Click submit button
   ├── Locate: /html/body/div[1]/div/div/div[3]/form/button
   └── Click to submit
6. Wait for login completion
7. Return success status
```

**Error Handling:**
- Element not found exceptions
- Timeout exceptions
- Page source saving for debugging (`algotest_page_source.html`)
- Detailed error logging

**Debugging Support:**
- Saves page source HTML on errors
- Allows manual inspection of page structure
- Helps identify XPath changes

### 5. Main Function

**Purpose:** Main entry point that orchestrates the entire login flow.

**Execution Flow:**

```python
def main():
    # Initialize UI
    ui = AlgoTestUI()
    ui.print_banner()
    
    # Initialize managers
    credential_manager = CredentialManager(ui)
    browser_manager = AlgoTestBrowserManager(ui)
    
    # Step 1: Get Zerodha credentials
    zerodha_credentials = credential_manager.get_zerodha_credentials()
    
    # Step 2: Setup browser
    driver = browser_manager.setup_driver()
    
    # Step 3: Login to Zerodha
    ui.log("STEP 1: Logging into Zerodha", "highlight")
    zerodha_success = browser_manager.login_zerodha(driver, zerodha_credentials)
    
    # Step 4: Open AlgoTest tab
    ui.log("STEP 2: Opening AlgoTest tab", "highlight")
    algotest_tab_success = browser_manager.open_algotest_tab(driver)
    
    # Step 5: Login to AlgoTest
    ui.log("STEP 3: Logging into AlgoTest", "highlight")
    algotest_credentials = credential_manager.get_algotest_credentials()
    algotest_success = browser_manager.login_algotest(
        driver,
        algotest_credentials["username"],
        algotest_credentials["password"]
    )
    
    # Step 6: Complete
    ui.log("Process completed", "success")
    input("\nPress Enter to exit...")
```

**Error Handling:**
- Exits gracefully on credential errors
- Handles browser setup failures
- Continues even if AlgoTest login fails (allows manual login)
- Keyboard interrupt handling
- Exception logging with tracebacks

---

## 📦 Installation

### Prerequisites

- Python 3.8+
- Google Chrome (latest version recommended)
- ChromeDriver (see main project README or DRIVERS/README_DRIVERS.md)
- Main project dependencies installed

### Step 1: Ensure Main Project is Set Up

```bash
cd /path/to/zerodha_automation
pip install -r requirements.txt
```

**Required Packages:**
- `selenium` - Web automation
- `pyotp` - TOTP generation for 2FA
- `rich` - Terminal UI formatting

### Step 2: Configure Credentials

**Zerodha Credentials:**
- Already in `config/zerodha_credentials.csv`
- BU0542 account must be present
- Status value is ignored (script bypasses filtering)

**AlgoTest Credentials:**
Create `algotest_credentials.json` in the `CronJob Algotest Login` directory:

```json
{
  "algotest": {
    "username": "your_phone_number",
    "password": "your_password"
  },
  "note": "Username can be phone number or email"
}
```

**Note:** Copy from `algotest_credentials.json.example` if needed.

---

## ⚙️ Configuration

### Credential Files

#### Zerodha Credentials (`config/zerodha_credentials.csv`)

```csv
Username,Password,PIN/TOTP Secret,Status
BU0542,shashwat2000,NK43ALDINHX6BZH6YBB67LU5D255QMUK,0
```

**Important Notes:**
- Status is ignored - script always processes BU0542
- TOTP secret should be Base32 encoded
- PIN should be 6 digits if using static PIN

#### AlgoTest Credentials (`algotest_credentials.json`)

```json
{
  "algotest": {
    "username": "9599002805",
    "password": "your_password_here"
  }
}
```

**Structure:**
- `algotest` - Main section
  - `username` - Phone number or email (required)
  - `password` - Account password (required)

### XPath Configuration

Current XPaths are defined in the `Config` class. Update these if AlgoTest website structure changes:

```python
# Login button (shows the form)
ALGOTEST_LOGIN_BUTTON_LOCATOR = (By.XPATH, "/html/body/div[1]/div/div/div[1]/div[2]/div[1]/button[1]")

# Phone number input field
ALGOTEST_PHONE_INPUT_LOCATOR = (By.XPATH, "/html/body/div[1]/div/div/div[3]/form/div[1]/input")

# Password input field
ALGOTEST_PASSWORD_LOCATOR = (By.XPATH, "/html/body/div[1]/div/div/div[3]/form/div[2]/div/input")

# Submit button
ALGOTEST_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "/html/body/div[1]/div/div/div[3]/form/button")
```

**Updating XPaths:**
1. Inspect AlgoTest login page in browser
2. Get new XPath using browser DevTools
3. Update `Config` class in `algotest_login.py`
4. Test the updated script

---

## 🚀 Usage

### Basic Usage

```bash
python "CronJob Algotest Login/algotest_login.py"
```

### Execution Flow

The script will:

1. **Display Beautiful Banner** - Welcome screen with project info
2. **Read Credentials** - Load Zerodha and AlgoTest credentials
3. **Setup Chrome Browser** - Initialize WebDriver
4. **Login to Zerodha BU0542** - Complete Zerodha login with 2FA
5. **Open AlgoTest Tab** - Create new tab and navigate to algotest.in/live
6. **Login to AlgoTest** - Fill and submit AlgoTest login form
7. **Complete** - Keep browser open for use

### Expected Output

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║    ╔═══════════════════════════════════════════════════════╗ ║
║    ║   🤖 AlgoTest Login Automation System                 ║ ║
║    ║   🔄 Zerodha → AlgoTest Seamless Integration          ║ ║
║    ╚═══════════════════════════════════════════════════════╝ ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

📊 Zerodha Account: BU0542
Started at: 2024-01-15 10:30:00

════════════════════════════════════════════════════════════════

📋 STEP 1: Logging into Zerodha
✅ Successfully logged into Zerodha

📋 STEP 2: Opening AlgoTest Tab
✅ AlgoTest tab opened successfully

📋 STEP 3: Logging into AlgoTest
✅ AlgoTest login completed successfully

✅ Process Completed Successfully!
```

---

## 🔄 Process Flow

### Step 1: Zerodha Login

```
┌─────────────────────────────────────────────────┐
│ 1. Navigate to kite.zerodha.com                 │
│ 2. Wait for page to load                        │
│ 3. Enter username (BU0542)                      │
│ 4. Enter password                               │
│ 5. Submit login form                            │
│ 6. Handle 2FA                                   │
│    ├── Check if TOTP (secret length > 8)        │
│    ├── Generate TOTP using pyotp OR use PIN     │
│    ├── Enter PIN/TOTP into input field          │
│    └── Submit 2FA form                          │
│ 7. Verify login success (check URL)             │
│ 8. Log success/failure                          │
└─────────────────────────────────────────────────┘
```

### Step 2: Open AlgoTest Tab

```
┌─────────────────────────────────────────────────┐
│ 1. Execute JavaScript: window.open()            │
│    └── Opens new tab in same browser            │
│ 2. Switch to new tab                            │
│    └── driver.switch_to.window(handles[-1])     │
│ 3. Navigate to algotest.in/live                 │
│    └── driver.get(ALGOTEST_LOGIN_URL)           │
│ 4. Wait for page load                           │
│    └── Wait for ready_state == 'complete'       │
│ 5. Log success/failure                          │
└─────────────────────────────────────────────────┘
```

### Step 3: AlgoTest Login

```
┌─────────────────────────────────────────────────┐
│ 1. Click login button (show form)               │
│    └── Locator: /html/body/div[1]/.../button[1] │
│ 2. Wait for form to appear                      │
│    └── Wait for form elements to be visible     │
│ 3. Fill phone number                            │
│    ├── Locate phone input field                 │
│    ├── Clear existing content                   │
│    └── Enter phone number                       │
│ 4. Fill password                                │
│    ├── Locate password input field              │
│    ├── Clear existing content                   │
│    └── Enter password                           │
│ 5. Click submit button                          │
│    └── Locator: /html/body/div[1]/.../form/button │
│ 6. Wait for login completion                    │
│    └── Wait for page change or element          │
│ 7. Log success/failure                          │
└─────────────────────────────────────────────────┘
```

**Important:** The chronology is critical:
1. Click login button FIRST (reveals the form)
2. Then fill phone number
3. Then fill password
4. Finally click submit button

---

## 🐛 Troubleshooting

### AlgoTest Login Fails

**Symptoms:**
- Script can't find form elements
- Timeout errors
- Login button not clickable

**Solutions:**

1. **Check XPaths:**
   - Inspect AlgoTest page in browser (F12)
   - Verify XPaths are correct using browser DevTools
   - Update XPaths in `Config` class if changed
   - Test with browser console: `$x("/html/body/div[1]/...")`

2. **Check Credentials:**
   - Verify JSON file format is correct
   - Ensure username/password are correct
   - Check file permissions
   - Validate JSON syntax (no trailing commas)

3. **Page Source Debugging:**
   - Script saves `algotest_page_source.html` on errors
   - Inspect this file to see page structure
   - Compare with live page to identify changes
   - Update XPaths accordingly

4. **Manual Login:**
   - Browser stays open on failure
   - Login manually if needed
   - Check browser console for JavaScript errors
   - Verify network requests in Network tab

### Zerodha Login Issues

**Common Problems:**
- 2FA timeout
- Wrong credentials
- Network issues
- Website changes

**Solutions:**
- Verify BU0542 credentials in CSV
- Check TOTP secret is correct (Base32 format)
- Ensure system time is synchronized (critical for TOTP)
- Try using static PIN instead of TOTP
- Check internet connection stability
- Verify Zerodha website is accessible

### Browser Issues

**Chrome Driver:**
- Update Chrome to latest version
- ChromeDriver should match Chrome version
- Check ChromeDriver is in PATH
- Verify Chrome is installed correctly

**Tab Management:**
- Ensure JavaScript is enabled
- Check popup blockers aren't interfering
- Verify browser permissions
- Check if multiple tabs are being created

### Credential File Issues

**Zerodha CSV:**
- Verify BU0542 account exists in CSV
- Check CSV format (commas, quotes)
- Ensure proper encoding (UTF-8)
- Verify headers match exactly

**AlgoTest JSON:**
- Validate JSON syntax (use JSON validator)
- Check file path is correct
- Ensure `algotest` section exists
- Verify username and password fields are present

---

## 🛠️ Development

### Adding New Features

**Example: Adding notification on completion**

```python
def login_algotest(self, driver, username, password):
    # ... existing code ...
    if success:
        self.ui.log("AlgoTest login completed", "success")
        # Add notification here
        self.ui.console.print("[bold green]🔔 Notification: Login complete![/bold green]")
    return success
```

### Modifying XPaths

If AlgoTest website structure changes:

1. Open browser DevTools (F12)
2. Inspect the login elements
3. Right-click element → Copy → Copy XPath
4. Update `Config` class with new XPaths
5. Test thoroughly

### Testing

**Manual Testing Steps:**
1. Run script with valid credentials
2. Verify Zerodha login succeeds
3. Verify AlgoTest tab opens
4. Verify AlgoTest login succeeds
5. Test with invalid credentials (error handling)
6. Test with missing credential files

**Debug Mode:**
- Add `print()` statements for debugging
- Use browser DevTools to inspect elements
- Check saved page source HTML files
- Review log output carefully

---

## 📝 Notes

- This script is designed specifically for BU0542 account
- Status filtering is bypassed for BU0542
- Browser remains open after completion
- Page source is saved on AlgoTest login errors
- All credential files are gitignored

---

## 🔒 Security

- ✅ Credentials stored locally (gitignored)
- ✅ No credential transmission
- ✅ Secure file permissions recommended
- ✅ Regular password updates advised
- ✅ Private credential files not committed

---

## 📄 License

This script is part of the Zerodha Multi-Login project. See main README for license details.

---

<div align="center">

**Automated Trading Platform Access Made Easy**

[Main Project README](../README.md) · [Report Issue](https://github.com/Chaitanya-cpc/zerodha-multi-login/issues)

</div>
