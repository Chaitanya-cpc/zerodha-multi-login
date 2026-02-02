#!/usr/bin/env python3
"""
AlgoTest Login Automation Script

Logs into configured Zerodha accounts, then opens algotest.in/live in a new tab and logs in.
Account IDs are loaded from config/accounts_config.json for security.
"""

# Standard Library Imports
import csv
import json
import time
import sys
import os
import traceback
import subprocess
from typing import Dict, Optional

# Third-party Imports
import pyotp
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# WebDriver Manager (automatic ChromeDriver management)
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

# Add parent directory to path to import shared modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# ==========================================================================
# --- Configuration ---
# ==========================================================================

def load_accounts_config():
    """Load account configuration from JSON file."""
    config_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'accounts_config.json'),
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
    
    raise FileNotFoundError(
        "accounts_config.json not found. Please copy config/accounts_config.json.example "
        "to config/accounts_config.json and configure your account IDs."
    )

class Config:
    """Configuration settings."""
    
    # File Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONFIG_DIR = os.path.join(BASE_DIR, 'config')
    CREDENTIALS_FILE = os.path.join(CONFIG_DIR, 'zerodha_credentials.csv')
    ALGOTEST_CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'algotest_credentials.json')
    
    # Load account config
    _accounts_config = load_accounts_config()
    
    # Account Configuration - loaded from config file
    # Set to 1 to enable, 0 to disable in accounts_config.json
    ACCOUNTS_CONFIG = _accounts_config.get('algotest', {}).get('zerodha_accounts', {})
    
    # Target Accounts list (for iteration)
    TARGET_ACCOUNTS = list(ACCOUNTS_CONFIG.keys())
    
    # Default account (first enabled one)
    ZERODHA_ACCOUNT = next((acc for acc, enabled in ACCOUNTS_CONFIG.items() if enabled), None)
    
    # URLs
    ZERODHA_LOGIN_URL = "https://kite.zerodha.com/"
    ALGOTEST_LOGIN_URL = "https://algotest.in/live"
    
    # Timeouts and Delays (seconds)
    WEBDRIVER_WAIT_TIMEOUT = 30
    SHORT_DELAY = 0.75
    INTER_KEY_DELAY = 0.375
    POST_LOGIN_CLICK_DELAY = 4.0
    POST_2FA_KEY_DELAY = 1.0
    
    # CSV Headers
    CSV_USERNAME_HEADER = "Username"
    CSV_PASSWORD_HEADER = "Password"
    CSV_2FA_HEADER = "PIN/TOTP Secret"
    CSV_STATUS_HEADER = "Status"
    
    # Zerodha Selenium Locators
    USER_ID_INPUT_LOCATOR = (By.ID, "userid")
    PASSWORD_INPUT_LOCATOR = (By.ID, "password")
    LOGIN_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "//button[@type='submit']")
    PIN_INPUT_ID_NAME = "userid"
    PIN_INPUT_LOCATOR = (By.ID, PIN_INPUT_ID_NAME)
    PIN_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "//button[@type='submit']")
    
    # AlgoTest Selenium Locators
    ALGOTEST_LOGIN_BUTTON_LOCATOR = (By.XPATH, "/html/body/div[1]/div/div/div[1]/div[2]/div[1]/button[1]")  # Button to open login form
    ALGOTEST_PHONE_INPUT_LOCATOR = (By.XPATH, "/html/body/div[1]/div/div/div[3]/form/div[1]/input")  # Phone number input
    ALGOTEST_PASSWORD_LOCATOR = (By.XPATH, "/html/body/div[1]/div/div/div[3]/form/div[2]/div/input")  # Password input
    ALGOTEST_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "/html/body/div[1]/div/div/div[3]/form/button")  # Submit button after entering credentials
    
    # AlgoTest Post-Login Locators
    ALGOTEST_BROKER_SETUP_BUTTON_LOCATOR = (By.XPATH, "/html/body/div[1]/div/div/nav/div[2]/div[1]/a[2]")  # Broker setup button
    ALGOTEST_BROKER_SETUP_BUTTON_FALLBACK_LOCATOR = (By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[2]/div[3]/div/a/button")  # Fallback broker setup button
    ALGOTEST_UNLISTED_BROKER_LOCATOR = (By.XPATH, "//p[contains(text(), 'Unlisted Broker')]")  # Unlisted broker text (by text content)
    ALGOTEST_UNLISTED_BROKER_FALLBACK_LOCATOR = (By.XPATH, "/html/body/div[1]/div/div/div/div/div/div[3]/div/div/div/div[1]/div[1]/div[1]/p")  # Fallback locator for unlisted broker
    
    # Account-specific login button locators (after unlisted broker)
    # These are dynamically generated based on account position in config
    ACCOUNT_POSITIONS = _accounts_config.get('algotest', {}).get('account_positions', {})
    
    @classmethod
    def get_algotest_login_button_locator(cls, account_id):
        """Get the XPath locator for an account's login button based on its position."""
        position = cls.ACCOUNT_POSITIONS.get(account_id, 1)
        return (By.XPATH, f"/html/body/div[1]/div/div/div/div/div/div[3]/div/div/div/div[3]/div[2]/div[{position}]/div/div/div[3]/button")
    
    @classmethod
    def get_algotest_login_button_fallback_locator(cls, account_id):
        """Get the fallback XPath locator for an account's login button."""
        position = cls.ACCOUNT_POSITIONS.get(account_id, 1)
        return (By.XPATH, f"/html/body/div[1]/div/div/div/div/div/div[3]/div/div/div/div[1]/div[2]/div[{position}]/div/div/div[3]/button")

# ==========================================================================
# --- Terminal UI ---
# ==========================================================================

class AlgoTestUI:
    """Simple UI for the AlgoTest login."""
    
    CUSTOM_THEME = Theme({
        "info": "cyan",
        "success": "green bold",
        "warning": "yellow bold",
        "error": "bold red",
        "highlight": "bold magenta",
        "title": "bold cyan",
        "subtitle": "italic cyan",
    })
    
    def __init__(self):
        """Initialize the terminal UI."""
        self.console = Console(theme=self.CUSTOM_THEME)
        self.start_time = time.time()
    
    def print_banner(self):
        """Display the application banner."""
        banner_text = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║    ╔═══════════════════════════════════════════════════════╗ ║
    ║    ║   🤖 AlgoTest Login Automation System                 ║ ║
    ║    ║   🔄 Zerodha → AlgoTest Seamless Integration          ║ ║
    ║    ╚═══════════════════════════════════════════════════════╝ ║
    ║                                                               ║
    ║    [highlight]Automated Multi-Platform Login Solution[/highlight]  ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
        """
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        # Enhanced spacing and presentation
        self.console.print()
        self.console.print(Panel(banner_text, style="highlight", expand=False, border_style="bold #9c27b0", padding=(1, 2)))
        self.console.print()
        self.console.print(Panel.fit(
            f"[bold bright_cyan]📊 Zerodha Account: [bold white]{Config.ZERODHA_ACCOUNT}[/bold white][/bold bright_cyan]\n\n"
            f"[dim]Started at:[/dim] [bold white]{current_time}[/bold white]",
            style="cyan",
            border_style="bright_cyan",
            padding=(0, 2)
        ))
        self.console.print()
        self.console.print("[bold cyan]" + "═" * 72 + "[/bold cyan]")
        self.console.print()
    
    def log(self, message: str, level: str = "info"):
        """Log a message with appropriate styling."""
        if level not in ["info", "success", "warning", "error", "highlight"]:
            level = "info"
            
        # Add timestamp
        elapsed = time.time() - self.start_time
        elapsed_str = f"{elapsed:.1f}s"
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        
        # Create prefixes
        time_prefix = f"[dim]{timestamp}[/dim]"
        elapsed_prefix = f"[dim](+{elapsed_str})[/dim]"
        
        # Format the log message with appropriate icons
        icon = {
            "info": "🔵",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "highlight": "✨"
        }.get(level, "•")
        
        # Enhanced styling based on level
        level_styles = {
            "info": "[bold cyan]",
            "success": "[bold green]",
            "warning": "[bold yellow]",
            "error": "[bold red]",
            "highlight": "[bold bright_magenta]"
        }
        level_style = level_styles.get(level, "[bold white]")
        
        # Combine all parts with enhanced formatting
        log_msg = f"{time_prefix} {elapsed_prefix} {level_style}{icon}[/] {message}"
        self.console.print(log_msg)

# ==========================================================================
# --- Credential Manager ---
# ==========================================================================

class CredentialManager:
    """Handles reading credentials."""
    
    def __init__(self, ui: AlgoTestUI):
        """Initialize with UI reference."""
        self.ui = ui
        self.credentials_file = Config.CREDENTIALS_FILE
    
    def get_algotest_credentials(self) -> Optional[Dict[str, str]]:
        """Get AlgoTest credentials from JSON file."""
        try:
            if os.path.exists(Config.ALGOTEST_CREDENTIALS_FILE):
                with open(Config.ALGOTEST_CREDENTIALS_FILE, 'r') as f:
                    data = json.load(f)
                    algotest_creds = data.get('algotest', {})
                    username = algotest_creds.get('username', '').strip()
                    password = algotest_creds.get('password', '').strip()
                    
                    if username and password:
                        return {"username": username, "password": password}
                    else:
                        self.ui.log("AlgoTest credentials not configured in JSON file", "warning")
                        return None
            else:
                self.ui.log("AlgoTest credentials file not found", "warning")
                return None
        except Exception as e:
            self.ui.log(f"Error reading AlgoTest credentials: {e}", "error")
            return None
    
    def get_zerodha_credentials(self, account_id: str) -> Optional[Dict[str, str]]:
        """Get credentials for a specific Zerodha account."""
        self.ui.log(f"Reading Zerodha credentials for {account_id}")
        
        try:
            with open(self.credentials_file, mode='r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    username = row.get(Config.CSV_USERNAME_HEADER, "").strip()
                    if username == account_id:
                        password = row.get(Config.CSV_PASSWORD_HEADER, "").strip()
                        pin_or_totp = row.get(Config.CSV_2FA_HEADER, "").strip()
                        
                        if not password:
                            self.ui.log(f"No password found for {account_id}", "error")
                            return None
                        
                        self.ui.log(f"Found Zerodha credentials for {account_id}", "success")
                        return {
                            "user_id": username,
                            "password": password,
                            "pin": pin_or_totp,
                            "totp_secret": pin_or_totp
                        }
                
                self.ui.log(f"Account {account_id} not found in credentials file", "error")
                return None
                
        except FileNotFoundError:
            self.ui.log(f"Credentials file not found: '{self.credentials_file}'", "error")
            return None
        except Exception as e:
            self.ui.log(f"Failed to read credentials: {e}", "error")
            return None

# ==========================================================================
# --- Browser Manager ---
# ==========================================================================

class AlgoTestBrowserManager:
    """Manages browser instance for Zerodha and AlgoTest login."""
    
    def __init__(self, ui: AlgoTestUI):
        """Initialize with UI reference."""
        self.ui = ui
    
    def setup_driver(self) -> Optional[webdriver.Chrome]:
        """Set up and return a Chrome WebDriver instance."""
        self.ui.log("Setting up Chrome browser")
        driver = None
        
        try:
            options = Options()
            options.add_experimental_option("detach", True)
            
            # Use Google Chrome
            chrome_paths = [
                '/usr/bin/google-chrome',
                '/usr/bin/google-chrome-stable',
                '/usr/bin/chromium-browser',
                '/usr/bin/chromium',
            ]
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    options.binary_location = chrome_path
                    break
            
            # Use webdriver-manager if available for automatic ChromeDriver management
            if WEBDRIVER_MANAGER_AVAILABLE:
                try:
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                except Exception as wdm_error:
                    # Fallback to PATH-based ChromeDriver
                    driver = webdriver.Chrome(options=options)
            else:
                # Fallback to PATH-based ChromeDriver
                driver = webdriver.Chrome(options=options)
            self.ui.log("Chrome launched successfully", "success")
            return driver
            
        except Exception as e:
            self.ui.log(f"Failed to launch Chrome: {e}", "error")
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            return None
    
    def login_zerodha(self, driver: webdriver.Chrome, credentials: Dict[str, str]) -> bool:
        """Login to Zerodha account."""
        self.ui.log("Starting Zerodha login process")
        
        try:
            # Navigate to Zerodha login
            wait = WebDriverWait(driver, Config.WEBDRIVER_WAIT_TIMEOUT)
            self.ui.log("Navigating to Zerodha login page")
            driver.get(Config.ZERODHA_LOGIN_URL)
            time.sleep(Config.SHORT_DELAY)
            
            # Enter credentials
            self.ui.log("Entering Zerodha credentials")
            username_input = wait.until(EC.presence_of_element_located(Config.USER_ID_INPUT_LOCATOR))
            username_input.send_keys(credentials["user_id"])
            time.sleep(Config.INTER_KEY_DELAY)
            
            password_input = wait.until(EC.presence_of_element_located(Config.PASSWORD_INPUT_LOCATOR))
            password_input.send_keys(credentials["password"])
            time.sleep(Config.INTER_KEY_DELAY)
            
            # Submit login
            self.ui.log("Submitting Zerodha login form")
            login_button = wait.until(EC.element_to_be_clickable(Config.LOGIN_SUBMIT_BUTTON_LOCATOR))
            login_button.click()
            time.sleep(Config.POST_LOGIN_CLICK_DELAY)
            
            # Handle 2FA
            pin_or_totp = credentials.get("pin", "")
            if pin_or_totp:
                self.ui.log("Handling 2FA authentication")
                try:
                    pin_input = wait.until(EC.element_to_be_clickable(Config.PIN_INPUT_LOCATOR))
                    
                    # Determine if TOTP or PIN
                    if len(pin_or_totp) > 8 and pin_or_totp.isalnum() and not pin_or_totp.isdigit():
                        # TOTP
                        totp = pyotp.TOTP(pin_or_totp)
                        current_otp = totp.now()
                        self.ui.log(f"Generated TOTP: {current_otp}")
                        pin_input.send_keys(current_otp)
                    else:
                        # Static PIN
                        pin_input.send_keys(pin_or_totp)
                    
                    time.sleep(Config.POST_2FA_KEY_DELAY)
                    
                    # Submit 2FA
                    pin_submit_button = wait.until(EC.element_to_be_clickable(Config.PIN_SUBMIT_BUTTON_LOCATOR))
                    pin_submit_button.click()
                    time.sleep(Config.SHORT_DELAY)
                    
                    self.ui.log("Zerodha 2FA submitted successfully", "success")
                except TimeoutException:
                    self.ui.log("2FA field not found, assuming login successful", "warning")
            
            # Wait a bit for login to complete
            time.sleep(2.0)
            self.ui.log("Zerodha login completed successfully", "success")
            return True
            
        except Exception as e:
            self.ui.log(f"Zerodha login failed: {e}", "error")
            return False
    
    def open_algotest_tab(self, driver: webdriver.Chrome) -> bool:
        """Open algotest.in/live in a new tab."""
        try:
            self.ui.log("Opening AlgoTest in new tab")
            driver.execute_script("window.open('{}', '_blank');".format(Config.ALGOTEST_LOGIN_URL))
            
            # Switch to the new tab
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(Config.SHORT_DELAY)
            
            self.ui.log("AlgoTest tab opened successfully", "success")
            return True
            
        except Exception as e:
            self.ui.log(f"Failed to open AlgoTest tab: {e}", "error")
            return False
    
    def login_algotest(self, driver: webdriver.Chrome, username: str, password: str) -> bool:
        """Login to AlgoTest website."""
        self.ui.log("Starting AlgoTest login process")
        
        try:
            wait = WebDriverWait(driver, Config.WEBDRIVER_WAIT_TIMEOUT)
            
            # Wait for page to load
            self.ui.log("Waiting for AlgoTest page to load...")
            time.sleep(2.0)
            
            # Step 1: Click the login button first to open/show the login form
            self.ui.log("Clicking login button to open login form...")
            login_button = wait.until(EC.element_to_be_clickable(Config.ALGOTEST_LOGIN_BUTTON_LOCATOR))
            self.ui.log("Found login button", "success")
            login_button.click()
            self.ui.log("Clicked login button", "success")
            time.sleep(1.5)  # Wait for form to appear
            
            # Step 2: Find and fill phone number field
            self.ui.log("Looking for phone number input field...")
            phone_input = wait.until(EC.presence_of_element_located(Config.ALGOTEST_PHONE_INPUT_LOCATOR))
            self.ui.log("Found phone number field", "success")
            
            phone_input.clear()
            phone_input.send_keys(username)
            time.sleep(Config.INTER_KEY_DELAY)
            
            # Step 3: Find and fill password field
            self.ui.log("Looking for password input field...")
            password_input = wait.until(EC.presence_of_element_located(Config.ALGOTEST_PASSWORD_LOCATOR))
            self.ui.log("Found password field", "success")
            
            password_input.clear()
            password_input.send_keys(password)
            time.sleep(Config.INTER_KEY_DELAY)
            
            # Step 4: Find and click the submit button
            self.ui.log("Looking for submit button...")
            submit_button = wait.until(EC.element_to_be_clickable(Config.ALGOTEST_SUBMIT_BUTTON_LOCATOR))
            self.ui.log("Found submit button", "success")
            
            self.ui.log("Clicking submit button...")
            submit_button.click()
            time.sleep(2.0)
            
            self.ui.log("AlgoTest login submitted successfully", "success")
            return True
            
        except TimeoutException as e:
            self.ui.log(f"Timeout waiting for AlgoTest login elements: {e}", "error")
            # Save page source for debugging
            try:
                with open("algotest_page_source.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                self.ui.log("Page source saved to algotest_page_source.html for debugging", "info")
            except:
                pass
            return False
        except Exception as e:
            self.ui.log(f"AlgoTest login failed: {e}", "error")
            traceback.print_exc()
            return False
    
    def post_login_steps(self, driver: webdriver.Chrome, account_id: str) -> bool:
        """Perform post-login steps: remove ads, navigate to broker setup, select unlisted broker, and click account-specific login button."""
        self.ui.log("Starting post-login steps")
        
        try:
            wait = WebDriverWait(driver, Config.WEBDRIVER_WAIT_TIMEOUT)
            
            # Step 1: Press Escape key to remove ads
            self.ui.log("Pressing Escape key to remove ads...")
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ESCAPE)
            time.sleep(Config.SHORT_DELAY)
            self.ui.log("Escape key pressed", "success")
            
            # Step 2: Click broker setup button
            self.ui.log("Looking for broker setup button...")
            broker_setup_button = None
            
            # Try primary locator first
            try:
                broker_setup_button = wait.until(EC.element_to_be_clickable(Config.ALGOTEST_BROKER_SETUP_BUTTON_LOCATOR))
                self.ui.log("Found broker setup button using primary XPath", "success")
            except TimeoutException:
                # If primary fails, try fallback
                self.ui.log("Primary XPath failed for broker setup button. Trying fallback XPath...", "warning")
                try:
                    broker_setup_button = wait.until(EC.element_to_be_clickable(Config.ALGOTEST_BROKER_SETUP_BUTTON_FALLBACK_LOCATOR))
                    self.ui.log("Found broker setup button using fallback XPath", "success")
                except TimeoutException:
                    self.ui.log("Failed to find broker setup button using both primary and fallback XPaths", "error")
                    raise
            
            broker_setup_button.click()
            self.ui.log("Clicked broker setup button", "success")
            time.sleep(Config.SHORT_DELAY)
            
            # Step 3: Click unlisted broker text (try by text first, then fallback to XPath)
            self.ui.log("Looking for unlisted broker text...")
            unlisted_broker = None
            
            try:
                # First, try to find by text content
                unlisted_broker = wait.until(EC.element_to_be_clickable(Config.ALGOTEST_UNLISTED_BROKER_LOCATOR))
                element_text = unlisted_broker.text.strip()
                if "Unlisted Broker" in element_text:
                    self.ui.log(f"Found unlisted broker text by content: '{element_text}'", "success")
                else:
                    self.ui.log(f"Found element but text doesn't match: '{element_text}'. Trying fallback...", "warning")
                    unlisted_broker = None
            except TimeoutException:
                self.ui.log("Could not find unlisted broker by text content. Trying fallback XPath...", "warning")
                unlisted_broker = None
            
            # If not found by text, try fallback XPath
            if unlisted_broker is None:
                try:
                    self.ui.log("Trying fallback XPath for unlisted broker...")
                    unlisted_broker = wait.until(EC.element_to_be_clickable(Config.ALGOTEST_UNLISTED_BROKER_FALLBACK_LOCATOR))
                    self.ui.log("Found unlisted broker text using fallback XPath", "success")
                except TimeoutException:
                    self.ui.log("Failed to find unlisted broker text using both methods", "error")
                    raise
            
            # Click the found element
            unlisted_broker.click()
            self.ui.log("Clicked unlisted broker text", "success")
            time.sleep(Config.SHORT_DELAY)
            
            # Step 4: Click account-specific login button (dynamic based on config)
            if account_id not in Config.ACCOUNT_POSITIONS:
                self.ui.log(f"Account {account_id} not found in account_positions config. Skipping account-specific login button.", "warning")
                return True
            
            login_button_locator = Config.get_algotest_login_button_locator(account_id)
            fallback_locator = Config.get_algotest_login_button_fallback_locator(account_id)
            
            self.ui.log(f"Looking for login button for {account_id}...")
            account_login_button = None
            
            # Try primary locator first
            try:
                account_login_button = wait.until(EC.element_to_be_clickable(login_button_locator))
                self.ui.log(f"Found login button for {account_id} using primary XPath", "success")
            except TimeoutException:
                # If primary fails and we have a fallback, try it
                if fallback_locator:
                    self.ui.log(f"Primary XPath failed for {account_id}. Trying fallback XPath...", "warning")
                    try:
                        account_login_button = wait.until(EC.element_to_be_clickable(fallback_locator))
                        self.ui.log(f"Found login button for {account_id} using fallback XPath", "success")
                    except TimeoutException:
                        self.ui.log(f"Failed to find login button for {account_id} using both primary and fallback XPaths", "error")
                        raise
                else:
                    self.ui.log(f"Failed to find login button for {account_id}", "error")
                    raise
            
            account_login_button.click()
            self.ui.log(f"Clicked login button for {account_id}", "success")
            
            # Wait 5 seconds for auto-login verification
            self.ui.log("Waiting 5 seconds for auto-login verification...")
            time.sleep(5.0)
            self.ui.log("Auto-login verification wait completed", "success")
            
            self.ui.log("Post-login steps completed successfully", "success")
            return True
            
        except TimeoutException as e:
            self.ui.log(f"Timeout waiting for post-login elements: {e}", "error")
            return False
        except Exception as e:
            self.ui.log(f"Post-login steps failed: {e}", "error")
            traceback.print_exc()
            return False

# ==========================================================================
# --- Main Application ---
# ==========================================================================

def process_account(account_id: str, ui: AlgoTestUI, credential_manager: CredentialManager, browser_manager: AlgoTestBrowserManager) -> bool:
    """Process a single account through the complete workflow."""
    ui.console.print()
    ui.console.print(Panel.fit(
        f"[bold bright_magenta]🔄 Processing Account: [bold white]{account_id}[/bold white][/bold bright_magenta]",
        border_style="bright_magenta",
        padding=(1, 2)
    ))
    ui.console.print()
    
    driver = None
    try:
        # Get Zerodha credentials for this account
        zerodha_credentials = credential_manager.get_zerodha_credentials(account_id)
        if not zerodha_credentials:
            ui.log(f"Failed to get Zerodha credentials for {account_id}. Skipping.", "error")
            return False
        
        # Setup browser
        driver = browser_manager.setup_driver()
        if not driver:
            ui.log(f"Failed to setup browser for {account_id}. Skipping.", "error")
            return False
        
        # Step 1: Login to Zerodha
        ui.console.print()
        ui.console.print(Panel.fit(
            f"[bold bright_cyan]📋 STEP 1: Logging into Zerodha ({account_id})[/bold bright_cyan]",
            border_style="bright_cyan",
            padding=(0, 2)
        ))
        ui.console.print()
        
        zerodha_success = browser_manager.login_zerodha(driver, zerodha_credentials)
        if not zerodha_success:
            ui.console.print()
            ui.console.print(Panel.fit(
                f"[bold bright_red]❌ Zerodha Login Failed for {account_id}[/bold bright_red]\n\n"
                "[dim]Please check the logs above for error details[/dim]",
                border_style="bright_red",
                padding=(1, 2)
            ))
            ui.console.print()
            if driver:
                driver.quit()
            return False
        
        # Step 2: Open AlgoTest tab
        ui.console.print()
        ui.console.print(Panel.fit(
            "[bold bright_cyan]📋 STEP 2: Opening AlgoTest Tab[/bold bright_cyan]",
            border_style="bright_cyan",
            padding=(0, 2)
        ))
        ui.console.print()
        
        algotest_tab_success = browser_manager.open_algotest_tab(driver)
        if not algotest_tab_success:
            ui.console.print()
            ui.console.print(Panel.fit(
                "[bold bright_red]❌ Failed to Open AlgoTest Tab[/bold bright_red]\n\n"
                "[dim]Please check the logs above for error details[/dim]",
                border_style="bright_red",
                padding=(1, 2)
            ))
            ui.console.print()
            if driver:
                driver.quit()
            return False
        
        # Step 3: Login to AlgoTest
        ui.console.print()
        ui.console.print(Panel.fit(
            "[bold bright_cyan]📋 STEP 3: Logging into AlgoTest[/bold bright_cyan]",
            border_style="bright_cyan",
            padding=(0, 2)
        ))
        ui.console.print()
        
        # Get AlgoTest credentials
        algotest_credentials = credential_manager.get_algotest_credentials()
        
        if algotest_credentials:
            algotest_success = browser_manager.login_algotest(
                driver, 
                algotest_credentials["username"], 
                algotest_credentials["password"]
            )
            ui.console.print()
            if algotest_success:
                ui.console.print(Panel.fit(
                    "[bold bright_green]✅ AlgoTest Login Completed Successfully![/bold bright_green]",
                    border_style="bright_green",
                    padding=(1, 2)
                ))
                ui.console.print()
                ui.log("AlgoTest login completed successfully", "success")
                
                # Step 4: Post-login steps
                ui.console.print()
                ui.console.print(Panel.fit(
                    "[bold bright_cyan]📋 STEP 4: Post-Login Steps[/bold bright_cyan]",
                    border_style="bright_cyan",
                    padding=(0, 2)
                ))
                ui.console.print()
                
                post_login_success = browser_manager.post_login_steps(driver, account_id)
                if post_login_success:
                    ui.log("Post-login steps completed successfully", "success")
                else:
                    ui.log("Post-login steps failed - continuing anyway", "warning")
            else:
                ui.console.print(Panel.fit(
                    "[bold yellow]⚠️ AlgoTest Login Failed[/bold yellow]\n\n"
                    "[dim]You may need to login manually[/dim]\n"
                    "[dim]Check algotest_page_source.html for page structure[/dim]",
                    border_style="yellow",
                    padding=(1, 2)
                ))
                ui.console.print()
                ui.log("AlgoTest login failed - you may need to login manually", "warning")
                ui.log("Check algotest_page_source.html for page structure", "info")
                if driver:
                    driver.quit()
                return False
        else:
            ui.console.print()
            ui.console.print(Panel.fit(
                "[bold yellow]⚠️ AlgoTest Credentials Not Configured[/bold yellow]\n\n"
                f"[dim]Add credentials to: [bold white]{Config.ALGOTEST_CREDENTIALS_FILE}[/bold white][/dim]\n"
                "[dim]Browser window will remain open for manual login[/dim]",
                border_style="yellow",
                padding=(1, 2)
            ))
            ui.console.print()
            ui.log("AlgoTest credentials not configured - please login manually", "warning")
            ui.log(f"Add credentials to: {Config.ALGOTEST_CREDENTIALS_FILE}", "info")
            ui.log("Browser window will remain open for manual login", "info")
            if driver:
                driver.quit()
            return False
        
        # Close browser after completing all steps for this account
        ui.log(f"Closing browser for {account_id} after completing all steps", "info")
        if driver:
            driver.quit()
        
        ui.console.print()
        ui.console.print(Panel.fit(
            f"[bold bright_green]✅ Account {account_id} Process Completed Successfully![/bold bright_green]",
            border_style="bright_green",
            padding=(1, 2)
        ))
        ui.console.print()
        
        return True
        
    except Exception as e:
        ui.log(f"Error processing account {account_id}: {str(e)}", "error")
        traceback.print_exc()
        if driver:
            try:
                driver.quit()
            except:
                pass
        return False

def main():
    """Main entry point."""
    ui = AlgoTestUI()
    
    try:
        ui.print_banner()
        
        # Get list of enabled accounts
        enabled_accounts = [account_id for account_id, enabled in Config.ACCOUNTS_CONFIG.items() if enabled == 1]
        
        if not enabled_accounts:
            ui.console.print()
            ui.console.print(Panel.fit(
                "[bold yellow]⚠️ No Accounts Enabled[/bold yellow]\n\n"
                "[dim]Set at least one account to 1 in Config.ACCOUNTS_CONFIG[/dim]",
                border_style="yellow",
                padding=(1, 2)
            ))
            ui.console.print()
            ui.log("No accounts enabled in configuration. Exiting.", "warning")
            input("\nPress Enter to exit...")
            sys.exit(0)
        
        ui.console.print()
        ui.console.print(Panel.fit(
            f"[bold bright_cyan]📋 Processing [bold white]{len(enabled_accounts)}[/bold white] Account(s)[/bold bright_cyan]\n\n"
            f"[dim]Accounts: [bold white]{', '.join(enabled_accounts)}[/bold white][/dim]",
            border_style="bright_cyan",
            padding=(1, 2)
        ))
        ui.console.print()
        
        # Initialize managers
        credential_manager = CredentialManager(ui)
        browser_manager = AlgoTestBrowserManager(ui)
        
        # Process each enabled account sequentially
        results = {}
        for account_id in enabled_accounts:
            success = process_account(account_id, ui, credential_manager, browser_manager)
            results[account_id] = success
            
            # Add a small delay between accounts
            if account_id != enabled_accounts[-1]:  # Not the last account
                ui.log("Waiting before processing next account...", "info")
                time.sleep(2.0)
        
        # Final summary
        ui.console.print()
        ui.console.print(Panel.fit(
            "[bold bright_green]✅ All Accounts Processed![/bold bright_green]\n\n"
            f"[dim]Results:[/dim]\n" + 
            "\n".join([f"  [{'green' if results[acc] else 'red'}]●[/] {acc}: {'Success' if results[acc] else 'Failed'}" for acc in enabled_accounts]),
            border_style="bright_green",
            padding=(1, 2)
        ))
        ui.console.print()
        
        # Only wait for user input if running interactively (not via launchd/cron)
        if sys.stdin.isatty() or len(sys.argv) == 1:  # Also check if double-clicked
            try:
                ui.console.print()
                ui.console.print(Panel.fit(
                    "[bold yellow]⚠️  Close All Chrome Windows?[/bold yellow]\n\n"
                    "[dim]Press [bold white]Enter[/bold white] to close all Chrome windows and exit[/dim]\n"
                    "[dim]Press [bold white]Ctrl+C[/bold white] to keep Chrome windows open and exit[/dim]",
                    border_style="yellow",
                    padding=(1, 2)
                ))
                ui.console.print()
                input("Press Enter to close all Chrome windows...")
                ui.log("Closing all Chrome windows...", "info")
                # Very aggressive Chrome window closing
                chrome_pids = set()
                for pattern in ['google-chrome', 'chromedriver', 'chrome']:
                    try:
                        result = subprocess.run(['pgrep', '-f', pattern], capture_output=True, timeout=2)
                        if result.returncode == 0:
                            pids = result.stdout.decode().strip().split('\n')
                            for pid in pids:
                                if pid.strip() and pid.strip().isdigit():
                                    chrome_pids.add(pid.strip())
                    except:
                        pass
                
                commands = [
                    ['pkill', '-9', 'google-chrome'],
                    ['pkill', '-9', '-f', 'google-chrome'],
                    ['pkill', '-9', '-f', 'chromedriver'],
                    ['pkill', '-9', '-f', 'chrome'],
                    ['killall', '-9', 'google-chrome'],
                    ['killall', '-9', 'chromedriver'],
                    ['killall', '-9', 'chrome'],
                    ['pkill', '-15', 'google-chrome'],
                    ['killall', '-15', 'google-chrome'],
                ]
                for cmd in commands:
                    try:
                        subprocess.run(cmd, check=False, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, timeout=2)
                        time.sleep(0.1)
                    except:
                        pass
                time.sleep(0.8)
                for pid in chrome_pids:
                    try:
                        subprocess.run(['kill', '-9', pid], check=False, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, timeout=1)
                    except:
                        pass
                for pattern in ['google-chrome', 'chromedriver', 'chrome']:
                    try:
                        result = subprocess.run(['pgrep', '-f', pattern], capture_output=True, timeout=1)
                        if result.returncode == 0:
                            remaining_pids = result.stdout.decode().strip().split('\n')
                            for pid in remaining_pids:
                                if pid.strip() and pid.strip().isdigit():
                                    try:
                                        subprocess.run(['kill', '-9', pid.strip()], check=False, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, timeout=1)
                                    except:
                                        pass
                    except:
                        pass
                time.sleep(0.3)
                ui.log("All Chrome windows closed", "success")
            except KeyboardInterrupt:
                ui.log("Keeping Chrome windows open", "info")
            except (EOFError, KeyboardInterrupt):
                pass  # Ignore EOF errors when running non-interactively
        
    except KeyboardInterrupt:
        ui.log("\nOperation cancelled by user", "warning")
        sys.exit(1)
    except Exception as e:
        ui.log(f"An error occurred: {str(e)}", "error")
        traceback.print_exc()
        # Only wait for user input if running interactively
        if sys.stdin.isatty():
            try:
                input("\nPress Enter to exit...")
            except (EOFError, KeyboardInterrupt):
                pass  # Ignore EOF errors when running non-interactively
        sys.exit(1)

if __name__ == '__main__':
    main()

