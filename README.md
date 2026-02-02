# 🚀 Zerodha Multi-Account Login Automation

<div align="center">

![Zerodha Logo](https://zerodha.com/static/images/logo.svg)

**A powerful, automated solution for managing multiple Zerodha trading accounts with beautiful terminal interface and comprehensive features.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.0+-green.svg)](https://selenium-python.readthedocs.io/)
[![Rich](https://img.shields.io/badge/Rich-Terminal%20UI-brightgreen.svg)](https://github.com/Textualize/rich)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Scripts](#-scripts)
- [Documentation](#-documentation)
- [Security](#-security)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## 🎯 Overview

This project provides a comprehensive automation solution for logging into multiple Zerodha trading accounts simultaneously. It features a beautiful terminal interface built with the Rich library, parallel processing for efficiency, account grouping for organization, and an interactive dashboard for managing your trading accounts efficiently.

### Key Highlights

- ✨ **Beautiful Terminal UI** - Rich, colorful interface with progress tracking and elegant formatting
- 🔐 **Secure Credential Management** - Status-based filtering and credential caching
- 🚀 **Parallel Processing** - All accounts login simultaneously for maximum speed
- 📊 **Interactive Dashboard** - Full-featured TUI for account management
- 🎯 **Account Groups** - Organize accounts into logical groups
- 📝 **Comprehensive Logging** - Detailed logs with timestamps and file output
- 🎨 **Visual Progress Indicators** - Real-time status updates with beautiful formatting

---

## ✨ Features

### Core Features

| Feature                    | Description                                               |
| -------------------------- | --------------------------------------------------------- |
| **Multi-Account Support**  | Login to multiple Zerodha accounts simultaneously         |
| **TOTP & PIN Support**     | Automatic 2FA handling with TOTP generation or static PIN |
| **Status-Based Filtering** | Only process accounts with status="1"                     |
| **Parallel Processing**    | All browser windows open simultaneously                   |
| **Interactive Selection**  | Choose accounts via command line or interactive menu      |
| **Account Groups**         | Create and manage groups of accounts                      |
| **Rich Terminal UI**       | Beautiful, colorful interface with progress bars          |
| **Comprehensive Logging**  | Timestamped logs saved to files                           |
| **Error Handling**         | Screenshot capture on failures                            |
| **Headless Mode**          | Run without GUI for automation                            |

### Advanced Features

- **Interactive Dashboard Mode** - Full TUI for managing accounts and groups
- **Credential Management** - Add, update, delete accounts via dashboard
- **Group Management** - Create, edit, delete account groups
- **Real-time Progress** - Live status updates during login process
- **Verbose Mode** - Detailed debugging output
- **Custom Logging** - Configurable log directories
- **Chrome Extension Support** - Pre-load extensions for company account

---

## 🏗️ Architecture

### Project Structure

```
zerodha_automation/
├── src/
│   ├── auto_login.py          # Main multi-account login script (2000+ lines)
│   └── __init__.py
├── config/
│   ├── zerodha_credentials.csv    # Account credentials (gitignored)
│   ├── account_groups.json         # Account group definitions
│   └── test.csv
├── CronJob Algotest Login/
│   ├── algotest_login.py          # Zerodha → AlgoTest automation (500+ lines)
│   ├── algotest_credentials.json  # AlgoTest credentials (gitignored)
│   ├── algotest_credentials.json.example
│   └── README.md
├── src/
│   ├── auto_login.py          # Main multi-account login script (2000+ lines)
│   ├── open_my_accounts.py    # Personal accounts login (configurable)
│   ├── open_Company_Account.py  # Legacy company account script
│   └── __init__.py
├── extensions/
│   └── Trading Algo/         # Chrome extension files
│       ├── manifest.json
│       └── content.js
├── DRIVERS/
│   └── README_DRIVERS.md
├── logs/                     # Log files directory
├── requirements.txt
├── .gitignore
└── README.md
```

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Terminal UI  │  │  Dashboard   │  │  Rich Output │     │
│  │  (Rich)      │  │   (TUI)      │  │  Formatting  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                 Application Logic Layer                      │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ ZerodhaLoginBot  │  │ AccountGroupMgr  │               │
│  │  (Orchestrator)  │  │  (Group Handler) │               │
│  └──────────────────┘  └──────────────────┘               │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ CredentialManager│  │  LoginSession    │               │
│  │  (Data Handler)  │  │  (Single Login)  │               │
│  └──────────────────┘  └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                   Browser Automation Layer                   │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ BrowserManager   │  │  Selenium        │               │
│  │  (Driver Setup)  │  │  WebDriver       │               │
│  └──────────────────┘  └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                      Data Persistence                        │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ CSV Files        │  │  JSON Files      │               │
│  │ (Credentials)    │  │  (Groups)        │               │
│  └──────────────────┘  └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
CSV File (Credentials)
    ↓
CredentialManager.read_credentials()
    ↓
Status Filter (status == "1")
    ↓
Account Selection (all/interactive/specific)
    ↓
ZerodhaLoginBot.run()
    ↓
ZerodhaLoginBot._run_parallel()
    ↓
ThreadPoolExecutor (Concurrent Processing)
    ↓
LoginSession.execute() [per account]
    ↓
BrowserManager.setup_driver()
    ↓
BrowserManager.enter_credentials()
    ↓
BrowserManager.handle_two_factor_auth()
    ├─→ TOTP (pyotp) OR PIN (static)
    └─→ Submit & Verify
    ↓
Success/Failure Status
    ↓
Browser Windows Remain Open
```

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Google Chrome browser (latest version recommended) or Chromium (Linux)
- ChromeDriver (usually auto-detected, see [DRIVERS/README_DRIVERS.md](DRIVERS/README_DRIVERS.md))

### Platform Support

This project supports **Windows**, **macOS**, and **Linux** operating systems. All scripts are cross-platform and will automatically detect and use the appropriate paths and configurations for your operating system.

**Linux-specific notes:**
- Supports both Google Chrome and Chromium browsers
- Automatically detects Chrome profile location (`~/.config/google-chrome` or `~/.config/chromium`)
- Chrome options optimized for Linux (including `--no-sandbox` and `--disable-dev-shm-usage`)
- All file paths use cross-platform methods (`os.path.join`)

📖 **For detailed Linux setup instructions, see [LINUX_SETUP.md](LINUX_SETUP.md)**

### Step 1: Clone Repository

```bash
git clone https://github.com/Chaitanya-cpc/zerodha-multi-login.git
cd zerodha-multi-login
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required Packages:**

- `selenium` - Web automation and browser control
- `pyotp` - Time-based One-Time Password (TOTP) generation
- `rich` - Beautiful terminal UI with colors, tables, and progress bars
- `tqdm` - Progress bars for long-running operations

### Step 3: Configure Credentials

Create `config/zerodha_credentials.csv`:

```csv
Username,Password,PIN/TOTP Secret,Status
AB1234,your_password,123456,1
CD5678,another_password,JBSWY3DPEHPK3PXP,1
EF9012,password123,,0
```

**CSV Headers:**

- `Username` - Zerodha user ID (required)
- `Password` - Account password (required)
- `PIN/TOTP Secret` - Static PIN (e.g., "123456") or TOTP secret key (e.g., "JBSWY3DPEHPK3PXP") (optional)
- `Status` - "1" for active, "0" for inactive (optional, defaults to "1")

---

## ⚙️ Configuration

### Credentials File Structure

The credentials CSV supports the following:

- **Username**: Your Zerodha user ID (required)
- **Password**: Your account password (required)
- **PIN/TOTP Secret**:
  - Static PIN (e.g., "123456") - 6-digit numeric PIN
  - TOTP Secret (e.g., "JBSWY3DPEHPK3PXP") - Base32 encoded secret for authenticator apps
  - Leave empty if 2FA is not required
- **Status**:
  - `1` = Active (will be logged in)
  - `0` = Inactive (will be skipped)

### Account Groups

Create groups in `config/account_groups.json`:

```json
{
  "groups": [
    {
      "name": "Trading Team",
      "accounts": ["AB1234", "CD5678"],
      "description": "Main trading accounts"
    },
    {
      "name": "Personal",
      "accounts": ["EF9012"],
      "description": "Personal trading accounts"
    }
  ]
}
```

**Group Structure:**

- `name` - Unique group identifier (required)
- `accounts` - Array of account usernames (required)
- `description` - Optional description of the group

---

## 🚀 Usage

### Basic Usage

**Login to all active accounts:**

```bash
python src/auto_login.py
```

**Login to specific accounts:**

```bash
python src/auto_login.py --accounts AB1234,CD5678
```

**Interactive account selection:**

```bash
python src/auto_login.py -i
```

**Interactive dashboard:**

```bash
python src/auto_login.py --dashboard
```

**Login to account group:**

```bash
python src/auto_login.py --group "Trading Team"
```

### Command-Line Options

#### Input/Output

| Option                   | Description                  |
| ------------------------ | ---------------------------- |
| `-c, --credentials PATH` | Path to credentials CSV file |
| `--no-log-file`          | Disable logging to file      |
| `--log-dir DIR`          | Directory to store log files |

#### Display

| Option          | Description                              |
| --------------- | ---------------------------------------- |
| `-v, --verbose` | Enable verbose output for debugging      |
| `-q, --quiet`   | Disable console output (not recommended) |

#### Execution

| Option       | Description                             |
| ------------ | --------------------------------------- |
| `-y, --yes`  | Skip confirmation prompt (auto-proceed) |
| `--headless` | Run browsers in headless mode (no GUI)  |

#### Account Selection

| Option              | Description                        |
| ------------------- | ---------------------------------- |
| `--accounts LIST`   | Comma-separated account usernames  |
| `-i, --interactive` | Interactive account selection menu |
| `--group NAME`      | Login to account group by name     |

### Examples

**Verbose mode with custom credentials:**

```bash
python src/auto_login.py -v -c /path/to/credentials.csv
```

**Headless mode (no GUI):**

```bash
python src/auto_login.py --headless -y
```

**Login to account group:**

```bash
python src/auto_login.py --group "Trading Team"
```

**Multiple accounts with verbose logging:**

```bash
python src/auto_login.py --accounts AB1234,CD5678,EF9012 -v
```

---

## 📚 Complete Code Structure

### Main Script: `src/auto_login.py`

This is the core script containing all the main classes and logic for multi-account login automation.

#### Class Hierarchy

```
Config (Configuration)
    ↓
TerminalUI (User Interface)
    ↓
CredentialManager (Data Management)
    ↓
BrowserManager (Browser Control)
    ↓
LoginSession (Single Account Login)
    ↓
ZerodhaLoginBot (Main Orchestrator)
    ↓
AccountGroupManager (Group Management)
    ↓
ZerodhaDashboard (Interactive TUI)
```

#### 1. Config Class

**Purpose:** Centralized configuration management for all application settings.

**Location:** `src/auto_login.py` (lines 54-94)

**Key Attributes:**

```python
class Config:
    # File Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONFIG_DIR = os.path.join(BASE_DIR, 'config')
    CREDENTIALS_FILE = os.path.join(CONFIG_DIR, 'zerodha_credentials.csv')
    GROUPS_CONFIG_FILE = os.path.join(CONFIG_DIR, 'account_groups.json')
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')

    # URLs
    ZERODHA_LOGIN_URL = "https://kite.zerodha.com/"

    # Timeouts and Delays (seconds)
    WEBDRIVER_WAIT_TIMEOUT = 30
    SHORT_DELAY = 0.75
    INTER_KEY_DELAY = 0.375
    POST_LOGIN_CLICK_DELAY = 4.0
    POST_2FA_KEY_DELAY = 1.0
    POST_FINAL_SUBMIT_DELAY = 0.75
    BROWSER_LAUNCH_DELAY = 2.0

    # CSV Headers
    CSV_USERNAME_HEADER = "Username"
    CSV_PASSWORD_HEADER = "Password"
    CSV_2FA_HEADER = "PIN/TOTP Secret"
    CSV_STATUS_HEADER = "Status"
    REQUIRED_CSV_HEADERS = [CSV_USERNAME_HEADER, CSV_PASSWORD_HEADER]

    # Selenium Locators
    USER_ID_INPUT_LOCATOR = (By.ID, "userid")
    PASSWORD_INPUT_LOCATOR = (By.ID, "password")
    LOGIN_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "//button[@type='submit']")
    PIN_INPUT_LOCATOR = (By.ID, "userid")
    PIN_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "//button[@type='submit']")
```

**Responsibilities:**

- Define all file paths and directories
- Configure timeouts and delays for Selenium operations
- Define CSV file structure and headers
- Specify Selenium element locators for Zerodha login page

#### 2. TerminalUI Class

**Purpose:** Manages all terminal output, formatting, and user interface elements using the Rich library.

**Location:** `src/auto_login.py` (lines 99-363)

**Key Methods:**

```python
class TerminalUI:
    def __init__(self, verbose: bool = False, log_to_file: bool = True)
    def print_banner(self) -> None
    def print_summary(self, accounts_data: List[Dict[str, str]]) -> None
    def log(self, message: str, level: str = "info", username: str = None) -> None
    def verbose_log(self, message: str, level: str = "info", username: str = None) -> None
    def print_warning(self, message: str) -> None
    def print_error(self, message: str) -> None
    def print_success(self, message: str) -> None
    def clear_screen(self) -> None
```

**Features:**

- Beautiful ASCII art banners with Rich panels
- Color-coded log messages with timestamps
- Formatted tables for account summaries
- Progress indicators and status updates
- File logging with timestamps
- Theme customization with Rich themes

**Log Levels:**

- `info` - General information (blue)
- `success` - Successful operations (green)
- `warning` - Warning messages (yellow)
- `error` - Error messages (red)
- `highlight` - Important highlights (magenta)

#### 3. CredentialManager Class

**Purpose:** Handles all credential-related operations including reading, writing, caching, and filtering.

**Location:** `src/auto_login.py` (lines 365-576)

**Key Methods:**

```python
class CredentialManager:
    def __init__(self, ui: TerminalUI, credentials_file: str = None)
    def read_credentials(self, credentials_file: str = None) -> List[Dict[str, str]]
    def get_credentials(self, username: str) -> Optional[Dict[str, str]]
    def save_credentials(self, account_data: Dict[str, str]) -> bool
    def delete_credentials(self, account_id: str) -> bool
    def set_credentials_file(self, file_path: str) -> None
```

**Key Features:**

- Status-based filtering (only processes accounts with status="1")
- Credential caching for performance
- CSV file parsing with error handling
- CRUD operations for credential management
- Automatic file path resolution

**Data Flow:**

```
CSV File → CSV Reader → Status Filter → Cache → Return List
```

#### 4. BrowserManager Class

**Purpose:** Manages Chrome WebDriver instances and handles all browser automation tasks.

**Location:** `src/auto_login.py` (lines 578-737)

**Key Methods:**

```python
class BrowserManager:
    def __init__(self, ui: TerminalUI, headless: bool = False)
    def setup_driver(self, username: str) -> Optional[webdriver.Chrome]
    def enter_credentials(self, wait: WebDriverWait, username: str, password: str) -> bool
    def handle_two_factor_auth(self, wait: WebDriverWait, pin_or_totp_secret: str, username: str) -> bool
    def save_screenshot(self, driver: webdriver.Chrome, filename: str, username: str) -> None
```

**Key Features:**

- Chrome WebDriver initialization with custom options
- Headless mode support
- Automatic credential form filling
- TOTP and PIN-based 2FA handling
- Screenshot capture on errors
- Wait strategies for element loading
- Detach option to keep browsers open

**2FA Handling Logic:**

```
PIN/TOTP Secret Input
    ↓
Check if TOTP (length > 8, alphanumeric, not all digits)
    ├─→ YES: Generate TOTP using pyotp
    └─→ NO: Use as static PIN
    ↓
Enter PIN/TOTP into input field
    ↓
Submit form
    ↓
Verify success (check URL or dashboard elements)
```

#### 5. LoginSession Class

**Purpose:** Orchestrates the complete login process for a single account.

**Location:** `src/auto_login.py` (lines 743-835)

**Key Methods:**

```python
class LoginSession:
    def __init__(self, account_data: Dict[str, str], ui: TerminalUI, browser_manager: BrowserManager)
    def execute(self) -> bool
    def update_status(self, status: str, final: bool = False) -> None
```

**Login Workflow:**

```
1. Initialize BrowserManager
2. Setup Chrome Driver
3. Navigate to Zerodha login page
4. Enter username and password
5. Handle 2FA (TOTP or PIN)
6. Verify login success
7. Handle errors with screenshots
8. Update status tracking
9. Return success/failure
```

**Status Tracking:**

- `pending` - Initial state
- `in_progress` - Login process started
- `success` - Login completed successfully
- `failed` - Login failed

#### 6. ZerodhaLoginBot Class

**Purpose:** Main orchestrator class that manages the entire multi-account login process.

**Location:** `src/auto_login.py` (lines 841-1103)

**Key Methods:**

```python
class ZerodhaLoginBot:
    def __init__(self, args: argparse.Namespace)
    def run(self) -> None
    def _filter_accounts_by_username(self, accounts_data: List[Dict], username_str: str) -> List[Dict]
    def _select_accounts_interactively(self, accounts_data: List[Dict]) -> List[Dict]
    def _confirm_proceed(self, account_count: int) -> bool
    def _run_parallel(self, accounts_data: List[Dict]) -> None
```

**Execution Flow:**

```
1. Initialize UI and managers
2. Display banner
3. Read credentials from CSV
4. Filter accounts (status, username, group, or interactive)
5. Display account summary
6. Confirm with user (unless -y flag)
7. Execute parallel login sessions
8. Track progress and status
9. Display completion summary
```

**Parallel Processing:**

- Uses `ThreadPoolExecutor` for concurrent execution
- Each account runs in its own thread
- All browser windows open simultaneously
- Independent error handling per account

#### 7. AccountGroup Class

**Purpose:** Data class representing an account group.

**Location:** `src/auto_login.py` (lines 1105-1135)

**Structure:**

```python
class AccountGroup:
    def __init__(self, name: str, accounts: List[str], description: str = "")
    def to_dict(self) -> Dict[str, Any]
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccountGroup'
    def validate(self) -> Tuple[bool, Optional[str]]
```

**Validation:**

- Checks for empty name
- Validates account list is not empty
- Ensures account names are valid

#### 8. AccountGroupManager Class

**Purpose:** Manages account group operations including creation, updating, deletion, and persistence.

**Location:** `src/auto_login.py` (lines 1137-1253)

**Key Methods:**

```python
class AccountGroupManager:
    def __init__(self, ui: TerminalUI, credential_manager: CredentialManager)
    def load_groups(self) -> List[AccountGroup]
    def save_groups(self, groups: List[AccountGroup]) -> bool
    def get_group(self, name: str) -> Optional[AccountGroup]
    def create_group(self, name: str, accounts: List[str], description: str = "") -> bool
    def update_group(self, name: str, accounts: List[str] = None, description: str = None) -> bool
    def delete_group(self, name: str) -> bool
    def list_groups(self) -> List[AccountGroup]
```

**Persistence:**

- JSON file storage (`config/account_groups.json`)
- Atomic file operations
- Error handling and validation
- Automatic file creation if missing

#### 9. ZerodhaDashboard Class

**Purpose:** Interactive terminal user interface (TUI) for managing accounts and groups.

**Location:** `src/auto_login.py` (lines 1255-1911)

**Key Methods:**

```python
class ZerodhaDashboard:
    def __init__(self, ui: TerminalUI, credential_manager: CredentialManager,
                 group_manager: AccountGroupManager, headless: bool = False)
    def run(self) -> None
    def _show_main_menu(self) -> None
    def _manage_accounts(self) -> None
    def _manage_groups(self) -> None
    def _add_account(self) -> None
    def _update_account(self) -> None
    def _delete_account(self) -> None
    def _create_group(self) -> None
    def _edit_group(self) -> None
    def _delete_group(self) -> None
    def _view_accounts(self) -> None
    def _view_groups(self) -> None
```

**Dashboard Features:**

- Main menu navigation
- Account CRUD operations
- Group CRUD operations
- View accounts and groups
- Interactive prompts using Rich
- Real-time updates

**Menu Structure:**

```
Main Menu
├── Manage Accounts
│   ├── Add Account
│   ├── Update Account
│   ├── Delete Account
│   └── View Accounts
├── Manage Groups
│   ├── Create Group
│   ├── Edit Group
│   ├── Delete Group
│   └── View Groups
└── Exit
```

#### Main Function

**Location:** `src/auto_login.py` (lines 1929-1998)

**Purpose:** Entry point for the application, handles command-line arguments and initialization.

**Key Logic:**

```python
def main():
    1. Parse command-line arguments
    2. Initialize TerminalUI
    3. Initialize CredentialManager
    4. Check for dashboard mode
       ├─→ YES: Launch ZerodhaDashboard
       └─→ NO: Launch ZerodhaLoginBot
    5. Handle exceptions and errors
    6. Keep terminal open if double-clicked
```

---

## 📜 Scripts

### 1. Main Script: `src/auto_login.py`

**Purpose:** Multi-account Zerodha login automation with full feature set.

**Features:**

- Parallel account login processing
- Status-based filtering
- Interactive dashboard mode
- Account group support
- Beautiful terminal UI
- Comprehensive logging
- Error handling with screenshots

**Usage:**

```bash
python src/auto_login.py [options]
```

**Key Classes:**

- `Config` - Configuration management
- `TerminalUI` - Terminal interface
- `CredentialManager` - Credential handling
- `BrowserManager` - Browser automation
- `LoginSession` - Single account login
- `ZerodhaLoginBot` - Main orchestrator
- `AccountGroupManager` - Group management
- `ZerodhaDashboard` - Interactive TUI

### 2. My Accounts: `src/open_my_accounts.py`

**Purpose:** Login to configured personal accounts in parallel.

**Features:**

- Parallel processing for multiple accounts
- Beautiful terminal UI
- Chrome window closing feature
- Status-independent processing

**Usage:**

```bash
python3 src/open_my_accounts.py
```

### 3. Legacy Company Account: `src/open_Company_Account.py`

**Purpose:** Script for company account with special features.

**Features:**

- Bypasses status filtering (always processes configured company account)
- Chrome extension support (Trading Algo extension)
- Beautiful terminal UI with enhanced banners
- Double-click support with welcome messages
- Profile-based extension loading

**Usage:**

```bash
python3 src/open_Company_Account.py
```

**Key Differences:**

- Targets single account (configured in accounts_config.json)
- Loads Chrome extensions from user profile
- Enhanced UI for double-click execution
- Status-independent processing

**Special Features:**

- Chrome profile copying for extension loading
- Anti-detection measures for automated browsers
- Enhanced error messages and status displays

### 4. AlgoTest Login: `CronJob Algotest Login/algotest_login.py`

**Purpose:** Automated multi-platform login flow (Zerodha → AlgoTest).

**Features:**

- Zerodha account login (configured accounts)
- AlgoTest tab opening in same browser
- AlgoTest login automation
- Multi-step process tracking
- XPath-based element location
- Error debugging with page source capture

**Usage:**

```bash
python "CronJob Algotest Login/algotest_login.py"
```

**Key Classes:**

- `Config` - Configuration (Zerodha and AlgoTest URLs, XPaths)
- `AlgoTestUI` - Terminal interface
- `CredentialManager` - Dual credential management (Zerodha + AlgoTest)
- `AlgoTestBrowserManager` - Browser automation with multi-platform support

**Process Flow:**

```
1. Read Zerodha credentials (configured accounts)
2. Setup Chrome browser
3. Login to Zerodha
   ├── Enter credentials
   ├── Handle 2FA
   └── Verify success
4. Open AlgoTest tab
   ├── Execute JavaScript (window.open)
   ├── Switch to new tab
   └── Navigate to algotest.in/live
5. Login to AlgoTest
   ├── Click login button (show form)
   ├── Fill phone number
   ├── Fill password
   └── Submit form
6. Complete
```

---

## 🔒 Security

### Credential Storage

- **CSV Files**: Stored in `config/` directory (gitignored)
- **JSON Files**: Credentials stored locally (gitignored)
- **Logs**: May contain sensitive info (stored locally, not committed)

### Best Practices

1. ✅ **Never commit credentials** - All credential files are gitignored
2. ✅ **Use status filtering** - Disable accounts by setting status="0"
3. ✅ **Secure file permissions** - Restrict access to credential files
4. ✅ **Regular password updates** - Change passwords periodically
5. ✅ **Private repositories** - Keep repo private if possible
6. ✅ **Local-only storage** - No credential transmission to external services

### Security Features

- Status-based account filtering
- Credential file gitignore (automatic)
- Local-only credential storage
- No credential transmission
- Secure file handling with error checking
- Optional credential caching (memory-only)

### Files Gitignored

```
config/zerodha_credentials.csv
CronJob Algotest Login/algotest_credentials.json
logs/*
*.png (screenshots)
algotest_page_source.html
```

---

## 🐛 Troubleshooting

### Common Issues

#### Chrome Driver Issues

**Problem:** ChromeDriver not found or version mismatch

**Solution:**

```bash
# Check Chrome version
chrome --version

# Download matching ChromeDriver from:
# https://chromedriver.chromium.org/downloads

# Add to PATH or specify in script
```

See [DRIVERS/README_DRIVERS.md](DRIVERS/README_DRIVERS.md) for detailed instructions.

#### 2FA Failures

**Problem:** Login fails during 2FA step

**Solutions:**

- Verify TOTP secret is correct (Base32 format)
- Check if using PIN vs TOTP (PIN should be 6 digits)
- Ensure system time is synchronized (critical for TOTP)
- Try using static PIN instead of TOTP
- Check CSV format and encoding

#### Login Timeouts

**Problem:** Script times out waiting for elements

**Solutions:**

- Increase `WEBDRIVER_WAIT_TIMEOUT` in Config class
- Check internet connection stability
- Verify Zerodha website is accessible
- Check if Zerodha website structure has changed
- Enable verbose mode for detailed logs

#### Account Not Found

**Problem:** Account not processed or not found

**Solutions:**

- Check CSV file format (headers must match exactly)
- Verify account status is "1" (if using status filtering)
- Ensure credentials are correct
- Check for encoding issues (use UTF-8)
- Verify account username matches exactly

#### Browser Not Opening

**Problem:** Chrome browser doesn't launch

**Solutions:**

- Check Chrome installation
- Verify ChromeDriver is in PATH
- Check for Chrome updates
- Try running with verbose mode (`-v`)
- Check system permissions

### Debug Mode

**Enable verbose logging:**

```bash
python src/auto_login.py -v
```

**Check log files:**

```bash
ls -la logs/
cat logs/zerodha_login_YYYYMMDD_HHMMSS.log
```

**Common Debug Steps:**

1. Run with `-v` flag for detailed output
2. Check log files in `logs/` directory
3. Review screenshots if login fails
4. Verify credentials in CSV file
5. Test with single account first: `--accounts ACCOUNT_ID`

---

## 🤝 Contributing

We welcome contributions! Here are some ways you can help:

1. **Report Bugs** - Open an issue with detailed information
2. **Suggest Features** - Share your ideas for improvements
3. **Submit Pull Requests** - Contribute code improvements
4. **Improve Documentation** - Help make docs better
5. **Test and Provide Feedback** - Help us find issues

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Chaitanya-cpc/zerodha-multi-login.git
cd zerodha-multi-login

# Install development dependencies
pip install -r requirements.txt

# Make changes and test
python src/auto_login.py -v

# Run tests (if available)
# pytest tests/
```

### Code Style

- Follow PEP 8 Python style guide
- Use type hints where appropriate
- Add docstrings to classes and methods
- Keep functions focused and small
- Use meaningful variable names

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is provided for educational and convenience purposes only. Use at your own risk and in compliance with Zerodha's terms of service. The authors and contributors are not responsible for any misuse or damages resulting from the use of this software.

---

<div align="center">

**Made with ❤️ for efficient trading account management**

[Report Bug](https://github.com/Chaitanya-cpc/zerodha-multi-login/issues) · [Request Feature](https://github.com/Chaitanya-cpc/zerodha-multi-login/issues) · [View Documentation](README.md)

</div>
