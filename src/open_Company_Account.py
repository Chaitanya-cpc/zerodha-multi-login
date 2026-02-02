#!/usr/bin/env python3
"""
Zerodha Company Account Login Script

A specialized script for logging into the HDN374 company account only.
"""

# Standard Library Imports
import csv
import time
import sys
import os
import platform
import traceback
from typing import Dict, Optional

# Third-party Imports
import pyotp
import requests
import zipfile
import tempfile
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
from rich import box

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# WebDriver Manager (automatic ChromeDriver management)
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ==========================================================================
# --- Configuration ---
# ==========================================================================

class Config:
    """Configuration settings for the company account login."""
    
    # File Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_DIR = os.path.join(BASE_DIR, 'config')
    CREDENTIALS_FILE = os.path.join(CONFIG_DIR, 'zerodha_credentials.csv')
    
    # Target Account
    TARGET_ACCOUNT = "HDN374"
    
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
    
    # Selenium Locators
    USER_ID_INPUT_LOCATOR = (By.ID, "userid")
    PASSWORD_INPUT_LOCATOR = (By.ID, "password")
    LOGIN_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "//button[@type='submit']")
    PIN_INPUT_ID_NAME = "userid"
    PIN_INPUT_LOCATOR = (By.ID, PIN_INPUT_ID_NAME)
    PIN_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "//button[@type='submit']")

# ==========================================================================
# --- Terminal UI ---
# ==========================================================================

class CompanyAccountUI:
    """Simple UI for the company account login."""
    
    CUSTOM_THEME = Theme({
        "info": "cyan",
        "success": "green bold",
        "warning": "yellow bold",
        "error": "bold red",
        "highlight": "bold magenta",
        "zerodha": "bold #ff5722",
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
    ║    ███████╗███████╗██████╗  ██████╗ ██████╗ ██╗  ██╗         ║
    ║    ╚══███╔╝██╔════╝██╔══██╗██╔═══██╗██╔══██╗██║  ██║         ║
    ║      ███╔╝ █████╗  ██████╔╝██║   ██║██║  ██║███████║         ║
    ║     ███╔╝  ██╔══╝  ██╔══██╗██║   ██║██║  ██║██╔══██║         ║
    ║    ███████╗███████╗██║  ██║╚██████╔╝██████╔╝██║  ██║         ║
    ║    ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝         ║
    ║                                                               ║
    ║    ╔═══════════════════════════════════════════════════════╗ ║
    ║    ║   🏢 Company Account Login Portal                     ║ ║
    ║    ║   ⭐ Exclusive HDN374 Account Access                  ║ ║
    ║    ╚═══════════════════════════════════════════════════════╝ ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
        """
        version = "v1.0.0"
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        # Enhanced spacing and presentation
        self.console.print()
        self.console.print(Panel(banner_text, style="zerodha", expand=False, border_style="bold #ff5722", padding=(1, 2)))
        self.console.print()
        self.console.print(Panel.fit(
            f"[bold bright_magenta]🏢 Company Account: [bold white]{Config.TARGET_ACCOUNT}[/bold white][/bold bright_magenta]\n\n"
            f"[dim]Version:[/dim] [bold white]{version}[/bold white]  [dim]|[/dim]  "
            f"[dim]Started:[/dim] [bold white]{current_time}[/bold white]",
            style="bright_magenta",
            border_style="bright_magenta",
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

class CompanyCredentialManager:
    """Handles reading credentials for the company account."""
    
    def __init__(self, ui: CompanyAccountUI):
        """Initialize with UI reference."""
        self.ui = ui
        self.credentials_file = Config.CREDENTIALS_FILE
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure the config directory exists."""
        os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
    
    def get_company_credentials(self) -> Optional[Dict[str, str]]:
        """Get credentials for the company account (HDN374)."""
        self.ui.log(f"Reading credentials for {Config.TARGET_ACCOUNT}")
        
        try:
            with open(self.credentials_file, mode='r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    username = row.get(Config.CSV_USERNAME_HEADER, "").strip()
                    if username == Config.TARGET_ACCOUNT:
                        password = row.get(Config.CSV_PASSWORD_HEADER, "").strip()
                        pin_or_totp = row.get(Config.CSV_2FA_HEADER, "").strip()
                        status = row.get(Config.CSV_STATUS_HEADER, "").strip()
                        
                        if not password:
                            self.ui.log(f"No password found for {Config.TARGET_ACCOUNT}", "error")
                            return None
                        
                        # Note: Company account login bypasses status check
                        if status != "1":
                            self.ui.log(f"Account {Config.TARGET_ACCOUNT} has status '{status}' but proceeding anyway (company account)", "warning")
                        
                        self.ui.log(f"Found credentials for {Config.TARGET_ACCOUNT}", "success")
                        return {
                            "user_id": username,
                            "password": password,
                            "pin": pin_or_totp,
                            "totp_secret": pin_or_totp,
                            "status": status
                        }
                
                self.ui.log(f"Account {Config.TARGET_ACCOUNT} not found in credentials file", "error")
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

class CompanyBrowserManager:
    """Manages browser instance for company account login."""
    
    def __init__(self, ui: CompanyAccountUI, headless: bool = False):
        """Initialize with UI reference and browser settings."""
        self.ui = ui
        self.headless = headless
    
    def _setup_chrome_profile(self):
        """Setup Chrome to use existing profile with all extensions."""
        # Get Chrome user data directory based on OS
        system = platform.system()
        home = os.path.expanduser("~")
        
        if system == "Windows":
            # Windows: AppData\Local\Google\Chrome\User Data
            user_data_dir = os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data")
        elif system == "Darwin":  # macOS
            # macOS: ~/Library/Application Support/Google/Chrome
            user_data_dir = os.path.join(home, "Library", "Application Support", "Google", "Chrome")
        else:  # Linux (and other Unix-like systems)
            # Linux: Try google-chrome first, then chromium
            user_data_dir = os.path.join(home, ".config", "google-chrome")
            # Check if google-chrome exists, if not try chromium
            if not os.path.exists(user_data_dir):
                chromium_dir = os.path.join(home, ".config", "chromium")
                if os.path.exists(chromium_dir):
                    user_data_dir = chromium_dir
        
        return user_data_dir
    
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
            
            # Use existing Chrome profile to get all installed extensions
            user_data_dir = self._setup_chrome_profile()
            if os.path.exists(user_data_dir):
                # Create a temporary profile directory to avoid conflicts
                import tempfile
                temp_profile_dir = os.path.join(tempfile.gettempdir(), f"chrome_profile_{int(time.time())}")
                os.makedirs(temp_profile_dir, exist_ok=True)
                
                options.add_argument(f"--user-data-dir={temp_profile_dir}")
                options.add_argument("--profile-directory=Default")
                
                # Copy extensions from main profile to temp profile
                source_extensions = os.path.join(user_data_dir, "Default", "Extensions")
                target_extensions = os.path.join(temp_profile_dir, "Default", "Extensions")
                
                if os.path.exists(source_extensions):
                    import shutil
                    try:
                        shutil.copytree(source_extensions, target_extensions, dirs_exist_ok=True)
                        self.ui.log("Copied existing extensions to new profile", "success")
                    except Exception as copy_error:
                        self.ui.log(f"Could not copy extensions: {copy_error}", "warning")
                
                self.ui.log("Using Chrome profile with existing extensions", "info")
            else:
                self.ui.log("Chrome profile not found, using default settings", "warning")
            
            # Additional options for better compatibility
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            if self.headless:
                options.add_argument('--headless')
            
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
            
            # Execute script to remove automation indicators
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.ui.log("Chrome launched successfully with profile extensions", "success")
            return driver
            
        except Exception as e:
            self.ui.log(f"Failed to launch Chrome: {e}", "error")
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            return None
    
    def navigate_to_login(self, driver: webdriver.Chrome) -> WebDriverWait:
        """Navigate to the login URL and return a WebDriverWait object."""
        self.ui.log("Navigating to login page")
        driver.get(Config.ZERODHA_LOGIN_URL)
        time.sleep(Config.SHORT_DELAY)
        return WebDriverWait(driver, Config.WEBDRIVER_WAIT_TIMEOUT)
    
    def enter_credentials(self, wait: WebDriverWait, username: str, password: str):
        """Enter username and password in the login form."""
        self.ui.log("Entering credentials")
        
        username_input = wait.until(EC.presence_of_element_located(Config.USER_ID_INPUT_LOCATOR))
        username_input.send_keys(username)
        time.sleep(Config.INTER_KEY_DELAY)
        
        password_input = wait.until(EC.presence_of_element_located(Config.PASSWORD_INPUT_LOCATOR))
        password_input.send_keys(password)
        time.sleep(Config.INTER_KEY_DELAY)
    
    def submit_initial_login(self, wait: WebDriverWait):
        """Submit the initial login form."""
        self.ui.log("Submitting login form")
        
        login_button = wait.until(EC.element_to_be_clickable(Config.LOGIN_SUBMIT_BUTTON_LOCATOR))
        login_button.click()
        self.ui.log("Waiting for 2FA screen")
        time.sleep(Config.POST_LOGIN_CLICK_DELAY)
    
    def handle_two_factor_auth(self, wait: WebDriverWait, pin_or_totp_secret: str) -> bool:
        """Handle two-factor authentication (PIN or TOTP)."""
        try:
            self.ui.log(f"Waiting for 2FA input field (id='{Config.PIN_INPUT_ID_NAME}') to be clickable...")
            pin_input = wait.until(EC.element_to_be_clickable(Config.PIN_INPUT_LOCATOR))
            self.ui.log("2FA screen detected and input field clickable.", "success")
            
            pin_or_totp_secret = pin_or_totp_secret.strip()
            
            if not pin_or_totp_secret:
                self.ui.log("WARNING: 2FA required but no PIN/TOTP found.", "error")
                return False
            
            self.ui.log("Attempting to enter PIN/TOTP...")
            
            # Determine if we're using TOTP or static PIN
            current_value_to_send = ""
            if len(pin_or_totp_secret) > 8 and pin_or_totp_secret.isalnum() and not pin_or_totp_secret.isdigit():
                self.ui.log("Treating as TOTP Secret.")
                try:
                    totp = pyotp.TOTP(pin_or_totp_secret)
                    current_otp = totp.now()
                    self.ui.log(f"Generated TOTP: {current_otp}")
                    current_value_to_send = current_otp
                except Exception as totp_gen_error:
                    self.ui.log(f"ERROR generating TOTP: {totp_gen_error}", "error")
                    return False
            else:
                self.ui.log("Treating as static PIN/Other value.")
                current_value_to_send = pin_or_totp_secret
            
            # Enter the 2FA code
            self.ui.log(f"Sending keys: '{current_value_to_send}'")
            pin_input.clear()
            time.sleep(0.1)
            pin_input.send_keys(current_value_to_send)
            self.ui.log(f"Pausing {Config.POST_2FA_KEY_DELAY}s...")
            time.sleep(Config.POST_2FA_KEY_DELAY)
            
            # Submit the 2FA form
            self.ui.log("Waiting for 2FA submit button...")
            pin_submit_button = wait.until(EC.element_to_be_clickable(Config.PIN_SUBMIT_BUTTON_LOCATOR))
            self.ui.log("Submitting PIN/TOTP...")
            pin_submit_button.click()
            
            self.ui.log("2FA submitted successfully.", "success")
            return True
            
        except TimeoutException:
            self.ui.log(f"INFO: 2FA input field (id='{Config.PIN_INPUT_ID_NAME}') not detected or clickable within timeout.")
            if not pin_or_totp_secret.strip():
                self.ui.log("Assuming no 2FA was needed.", "info")
                return True
            else:
                # Attempt to check if we're already on the dashboard despite the timeout
                try:
                    if "dashboard" in wait._driver.current_url.lower() or "kite.zerodha.com/dashboard" in wait._driver.current_url:
                        self.ui.log("Login appears successful despite 2FA detection issues.", "success")
                        return True
                except:
                    pass
                
                self.ui.log("WARNING: PIN/TOTP provided but 2FA field not interactable.", "warning")
                return False
        except Exception as e:
            self.ui.log(f"ERROR during 2FA handling: {e}", "error")
            
            # Check if we're already on the dashboard despite the error
            try:
                if "dashboard" in wait._driver.current_url.lower() or "kite.zerodha.com/dashboard" in wait._driver.current_url:
                    self.ui.log("Login appears successful despite 2FA handling errors.", "success")
                    return True
            except:
                pass
                
            return False

# ==========================================================================
# --- Main Login Process ---
# ==========================================================================

class CompanyAccountLogin:
    """Handles the complete login process for the company account."""
    
    def __init__(self, credentials: Dict[str, str], ui: CompanyAccountUI, browser_manager: CompanyBrowserManager):
        """Initialize with account credentials and managers."""
        self.credentials = credentials
        self.username = credentials.get("user_id", Config.TARGET_ACCOUNT)
        self.ui = ui
        self.browser_manager = browser_manager
    
    def execute(self) -> bool:
        """Execute the complete login process."""
        self.ui.log(f"Starting login process for {Config.TARGET_ACCOUNT}")
        driver = None
        login_successful = False
        
        try:
            # Initialize browser
            driver = self.browser_manager.setup_driver()
            if not driver:
                return False
            
            # Execute login steps
            wait = self.browser_manager.navigate_to_login(driver)
            self.browser_manager.enter_credentials(
                wait, 
                self.credentials["user_id"], 
                self.credentials["password"]
            )
            self.browser_manager.submit_initial_login(wait)
            
            # Handle 2FA if needed
            pin_or_totp = self.credentials.get("pin", "")
            two_fa_success = self.browser_manager.handle_two_factor_auth(wait, pin_or_totp)

            if two_fa_success:
                self.ui.log(f"Login completed successfully for {Config.TARGET_ACCOUNT}", "success")
                login_successful = True
                return login_successful
            else:
                self.ui.log(f"Login failed during 2FA for {Config.TARGET_ACCOUNT}", "error")
                login_successful = False
                
        except (TimeoutException, NoSuchElementException) as e:
            error_type = type(e).__name__
            self.ui.log(f"Element not found: {e}", "error")
            if driver:
                try:
                    driver.save_screenshot(f"{Config.TARGET_ACCOUNT}_{error_type.lower()}_error.png")
                except:
                    pass
        except KeyError as e:
            self.ui.log(f"Missing key in credentials: {e}", "error")
        except Exception as e:
            self.ui.log(f"Unexpected error: {e}", "error")
            if driver:
                try:
                    driver.save_screenshot(f"{Config.TARGET_ACCOUNT}_unexpected_error.png")
                except:
                    pass
        finally:
            if not login_successful:
                self.ui.log(f"Login process failed for {Config.TARGET_ACCOUNT}", "error")
            return login_successful

# ==========================================================================
# --- Main Application ---
# ==========================================================================

def main():
    """Main entry point for the company account login script."""
    
    # Check if running from double-click (no command line arguments)
    is_double_clicked = len(sys.argv) == 1
    
    # Clear screen for better presentation when double-clicked
    if is_double_clicked:
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
        except:
            pass
    
    # Initialize UI
    ui = CompanyAccountUI()
    
    try:
        # Display banner
        ui.print_banner()
        
        # Special welcome message for double-clicked execution
        if is_double_clicked:
            ui.log("🎯 Welcome! This script will login to your company account.", "highlight")
            ui.log("📋 Please ensure you have the correct credentials in the CSV file.", "info")
            ui.log("")
        
        # Initialize managers
        credential_manager = CompanyCredentialManager(ui)
        browser_manager = CompanyBrowserManager(ui, headless=False)
        
        # Get credentials for company account
        credentials = credential_manager.get_company_credentials()
        if not credentials:
            ui.log("Failed to get credentials. Exiting.", "error")
            if is_double_clicked:
                input("\nPress Enter to exit...")
            sys.exit(1)
        
        # Display account info
        two_fa_method = 'TOTP' if len(credentials.get('pin', '')) > 8 else 'PIN' if credentials.get('pin') else 'None'
        two_fa_icon = "🔐" if two_fa_method == "TOTP" else "🔑" if two_fa_method == "PIN" else "❌"
        
        ui.console.print()
        ui.console.print(Panel.fit(
            f"[bold bright_cyan]📋 Account Information[/bold bright_cyan]\n\n"
            f"[dim]Account ID:[/dim] [bold white]{Config.TARGET_ACCOUNT}[/bold white]\n"
            f"[dim]User ID:[/dim] [bold white]{credentials['user_id']}[/bold white]\n"
            f"[dim]2FA Method:[/dim] [bold yellow]{two_fa_icon} {two_fa_method}[/bold yellow]",
            border_style="bright_cyan",
            padding=(1, 2)
        ))
        ui.console.print()
        
        # Confirm before proceeding
        ui.console.print(Panel.fit(
            "[bold yellow]⏸️  Ready to Login[/bold yellow]\n\n"
            "[dim]Press [bold white]Enter[/bold white] to continue or [bold white]Ctrl+C[/bold white] to cancel[/dim]",
            border_style="yellow",
            padding=(1, 2)
        ))
        ui.console.print()
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            if isinstance(sys.stdin, type(None)) or not sys.stdin.isatty():
                # Non-interactive mode (desktop launch), skip input and proceed
                pass
            else:
                ui.log("Operation cancelled by user.", "warning")
                if is_double_clicked:
                    try:
                        input("\nPress Enter to exit...")
                    except (EOFError, KeyboardInterrupt):
                        pass
                sys.exit(0)
        
        # Execute login
        login_session = CompanyAccountLogin(credentials, ui, browser_manager)
        result = login_session.execute()
        
        ui.console.print()
        if result:
            ui.console.print(Panel.fit(
                f"[bold bright_green]✅ Successfully Logged Into {Config.TARGET_ACCOUNT}![/bold bright_green]\n\n"
                "[dim]Browser window will remain open for your use[/dim]",
                border_style="bright_green",
                padding=(1, 2)
            ))
            ui.console.print()
            ui.log(f"✅ Successfully logged into {Config.TARGET_ACCOUNT}", "success")
            ui.log("Browser window will remain open for your use.", "info")
        else:
            ui.console.print(Panel.fit(
                f"[bold bright_red]❌ Failed to Login to {Config.TARGET_ACCOUNT}[/bold bright_red]\n\n"
                "[dim]Please check the logs above for error details[/dim]",
                border_style="bright_red",
                padding=(1, 2)
            ))
            ui.console.print()
            ui.log(f"❌ Failed to login to {Config.TARGET_ACCOUNT}", "error")
            if is_double_clicked:
                input("\nPress Enter to exit...")
            sys.exit(1)
        
        # Keep terminal open when double-clicked
        if is_double_clicked:
            ui.console.print(Panel.fit(
                "[bold bright_magenta]✨ Login Process Completed[/bold bright_magenta]\n\n"
                "[dim]Browser window remains open for your use[/dim]",
                border_style="bright_magenta",
                padding=(1, 2)
            ))
            ui.console.print()
            input("\nPress Enter to exit...")
        
    except KeyboardInterrupt:
        ui.log("\nOperation cancelled by user", "warning")
        if is_double_clicked:
            input("\nPress Enter to exit...")
        sys.exit(1)
    except Exception as e:
        ui.log(f"An error occurred: {str(e)}", "error")
        import traceback
        ui.console.print_exception()
        
        # Keep terminal open when double-clicked and there's an error
        if is_double_clicked:
            input("\nPress Enter to exit...")
        
        sys.exit(1)

if __name__ == '__main__':
    main()
