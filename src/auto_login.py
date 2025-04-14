#!/usr/bin/env python3
"""
Zerodha Multi-Account Login Script - Optimized Version

A tool for automating login to multiple Zerodha accounts using Selenium.
Features colorful terminal output, progress tracking, and improved error handling.
"""

# Standard Library Imports
import csv
import threading
import time
import sys
import os
import argparse
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Any, Tuple

# Third-party Imports
import pyotp
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.theme import Theme
from tqdm import tqdm

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================================================
# --- Configuration ---
# ==========================================================================

class Config:
    """Central configuration settings for the application."""
    
    # File Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONFIG_DIR = os.path.join(BASE_DIR, 'config')
    CREDENTIALS_FILE = os.path.join(CONFIG_DIR, 'zerodha_credentials.csv')
    
    # URLs
    ZERODHA_LOGIN_URL = "https://kite.zerodha.com/"
    
    # Timeouts and Delays (seconds)
    WEBDRIVER_WAIT_TIMEOUT = 30
    SHORT_DELAY = 0.5
    INTER_KEY_DELAY = 0.25
    POST_LOGIN_CLICK_DELAY = 3.0
    POST_2FA_KEY_DELAY = 0.5
    POST_FINAL_SUBMIT_DELAY = 0.5
    BROWSER_LAUNCH_DELAY = 1.5
    
    # CSV Headers
    CSV_USERNAME_HEADER = "Username"
    CSV_PASSWORD_HEADER = "Password"
    CSV_2FA_HEADER = "PIN/TOTP Secret"
    REQUIRED_CSV_HEADERS = [CSV_USERNAME_HEADER, CSV_PASSWORD_HEADER]
    
    # Selenium Locators
    USER_ID_INPUT_LOCATOR = (By.ID, "userid")
    PASSWORD_INPUT_LOCATOR = (By.ID, "password")
    LOGIN_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "//button[@type='submit']")
    PIN_INPUT_ID_NAME = "totp"  # Updated based on actual Zerodha login page
    PIN_INPUT_LOCATOR = (By.ID, PIN_INPUT_ID_NAME)
    PIN_SUBMIT_BUTTON_LOCATOR = (By.XPATH, "//button[@type='submit']")

# ==========================================================================
# --- Terminal UI Components ---
# ==========================================================================

class TerminalUI:
    """Handles all terminal UI components and output formatting."""
    
    # Define a custom theme for rich
    CUSTOM_THEME = Theme({
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "bold red",
        "highlight": "bold magenta",
        "zerodha": "bold #ff5722",  # Zerodha's orange
    })
    
    def __init__(self, verbose: bool = False):
        """Initialize the terminal UI components."""
        self.console = Console(theme=self.CUSTOM_THEME)
        self.verbose = verbose
    
    def print_banner(self):
        """Display the application banner."""
        banner = """
        ███████╗███████╗██████╗  ██████╗ ██████╗ ██╗  ██╗ █████╗     
        ╚══███╔╝██╔════╝██╔══██╗██╔═══██╗██╔══██╗██║  ██║██╔══██╗    
          ███╔╝ █████╗  ██████╔╝██║   ██║██║  ██║███████║███████║    
         ███╔╝  ██╔══╝  ██╔══██╗██║   ██║██║  ██║██╔══██║██╔══██║    
        ███████╗███████╗██║  ██║╚██████╔╝██████╔╝██║  ██║██║  ██║    
        ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝    
                                                                      
        ██╗      ██████╗  ██████╗ ██╗███╗   ██╗    ██████╗  ██████╗ ████████╗
        ██║     ██╔═══██╗██╔════╝ ██║████╗  ██║    ██╔══██╗██╔═══██╗╚══██╔══╝
        ██║     ██║   ██║██║  ███╗██║██╔██╗ ██║    ██████╔╝██║   ██║   ██║   
        ██║     ██║   ██║██║   ██║██║██║╚██╗██║    ██╔══██╗██║   ██║   ██║   
        ███████╗╚██████╔╝╚██████╔╝██║██║ ╚████║    ██████╔╝╚██████╔╝   ██║   
        ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝╚═╝  ╚═══╝    ╚═════╝  ╚═════╝    ╚═╝   
        """
        self.console.print(Panel(banner, style="zerodha", expand=False))
        self.console.print("Automated Zerodha Multi-Account Login Tool", style="highlight")
        self.console.print("------------------------------------------------", style="info")
    
    def print_summary(self, accounts_data: List[Dict[str, str]]):
        """Display a summary of accounts to be processed."""
        table = Table(title="Accounts to Process", show_header=True, header_style="zerodha")
        table.add_column("№", style="cyan")
        table.add_column("Username", style="green")
        table.add_column("2FA Method", style="yellow")
        
        for i, account in enumerate(accounts_data, start=1):
            username = account.get(Config.CSV_USERNAME_HEADER, "N/A")
            pin_or_totp = account.get(Config.CSV_2FA_HEADER, "")
            two_fa_type = "TOTP" if len(pin_or_totp) > 8 and pin_or_totp.isalnum() and not pin_or_totp.isdigit() else "PIN" if pin_or_totp else "None"
            table.add_row(str(i), username, two_fa_type)
        
        self.console.print(table)
    
    def log(self, message: str, level: str = "info", username: str = None):
        """Log a message with the appropriate styling."""
        if level not in ["info", "success", "warning", "error", "highlight"]:
            level = "info"
        
        prefix = f"[{username}] " if username else ""
        self.console.print(f"{prefix}{message}", style=level)
    
    def verbose_log(self, message: str, level: str = "info", username: str = None):
        """Log a message only if verbose mode is enabled."""
        if self.verbose:
            self.log(message, level, username)
    
    def create_progress(self):
        """Create and return a progress bar for tracking operations."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        )

# ==========================================================================
# --- Helper Functions ---
# ==========================================================================

class CredentialManager:
    """Handles reading and validating account credentials."""
    
    def __init__(self, ui: TerminalUI):
        """Initialize with UI reference for logging."""
        self.ui = ui
    
    def read_credentials(self, filepath: str) -> Optional[List[Dict[str, str]]]:
        """Read and validate credentials from the specified CSV file."""
        accounts_data = []
        self.ui.log(f"Reading credentials from: {filepath}")
        
        try:
            with open(filepath, mode='r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                # Validate CSV structure
                if not reader.fieldnames or not all(header in reader.fieldnames for header in Config.REQUIRED_CSV_HEADERS):
                    self.ui.log(f"Credentials file missing required headers {Config.REQUIRED_CSV_HEADERS}", "error")
                    return None
                
                for row in reader:
                    username = row.get(Config.CSV_USERNAME_HEADER, "").strip()
                    password = row.get(Config.CSV_PASSWORD_HEADER, "").strip()
                    pin_or_totp = row.get(Config.CSV_2FA_HEADER, "").strip()
                    
                    if username and password:
                        if Config.CSV_2FA_HEADER not in row: 
                            row[Config.CSV_2FA_HEADER] = ''
                        accounts_data.append(row)
                        self.ui.verbose_log(f"Added account: {username}", "success")
                    else:
                        self.ui.verbose_log(f"Skipped row due to missing Username or Password", "warning")
            
            if not accounts_data:
                self.ui.log("No valid account credentials found.", "error")
                return None
                
            self.ui.log(f"Successfully loaded {len(accounts_data)} account(s)", "success")
            return accounts_data
            
        except FileNotFoundError:
            self.ui.log(f"Credentials file not found: '{filepath}'", "error")
            return None
        except Exception as e:
            self.ui.log(f"Failed to read/parse credentials: {e}", "error")
            if self.ui.verbose:
                traceback.print_exc()
            return None

class BrowserManager:
    """Manages browser instances and Selenium interactions."""
    
    def __init__(self, ui: TerminalUI, headless: bool = False):
        """Initialize with UI reference and browser settings."""
        self.ui = ui
        self.headless = headless
    
    def setup_driver(self, username: str) -> Optional[webdriver.Chrome]:
        """Set up and return a Chrome WebDriver instance."""
        self.ui.verbose_log(f"Setting up Chrome browser", username=username)
        driver = None
        
        try:
            options = Options()
            options.add_experimental_option("detach", True)
            options.headless = self.headless
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            self.ui.verbose_log(f"Chrome launched successfully", "success", username)
            return driver
            
        except Exception as e:
            self.ui.log(f"Failed to launch Chrome: {e}", "error", username)
            if self.ui.verbose:
                traceback.print_exc()
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            return None
    
    def navigate_to_login(self, driver: webdriver.Chrome, username: str) -> WebDriverWait:
        """Navigate to the login URL and return a WebDriverWait object."""
        self.ui.verbose_log(f"Navigating to login page", username=username)
        driver.get(Config.ZERODHA_LOGIN_URL)
        time.sleep(Config.SHORT_DELAY)
        return WebDriverWait(driver, Config.WEBDRIVER_WAIT_TIMEOUT)
    
    def enter_credentials(self, wait: WebDriverWait, username: str, password: str, username_log: str):
        """Enter username and password in the login form."""
        self.ui.verbose_log(f"Entering credentials", username=username_log)
        
        username_input = wait.until(EC.presence_of_element_located(Config.USER_ID_INPUT_LOCATOR))
        username_input.send_keys(username)
        time.sleep(Config.INTER_KEY_DELAY)
        
        password_input = wait.until(EC.presence_of_element_located(Config.PASSWORD_INPUT_LOCATOR))
        password_input.send_keys(password)
        time.sleep(Config.INTER_KEY_DELAY)
    
    def submit_initial_login(self, wait: WebDriverWait, username: str):
        """Submit the initial login form."""
        self.ui.verbose_log(f"Submitting login form", username=username)
        
        login_button = wait.until(EC.element_to_be_clickable(Config.LOGIN_SUBMIT_BUTTON_LOCATOR))
        login_button.click()
        self.ui.verbose_log(f"Waiting for 2FA screen", username=username)
        time.sleep(Config.POST_LOGIN_CLICK_DELAY)
    
    def handle_two_factor_auth(self, wait: WebDriverWait, pin_or_totp_secret: str, username: str) -> bool:
        """Handle two-factor authentication (PIN or TOTP)."""
        try:
            self.ui.verbose_log(f"Looking for 2FA input field", username=username)
            pin_input = wait.until(EC.element_to_be_clickable(Config.PIN_INPUT_LOCATOR))
            self.ui.verbose_log(f"2FA screen detected", "success", username)
            
            pin_or_totp_secret = pin_or_totp_secret.strip()
            if not pin_or_totp_secret:
                self.ui.log(f"2FA required but no PIN/TOTP provided", "error", username)
                return False
            
            # Determine if we're using TOTP or static PIN
            current_value = ""
            if len(pin_or_totp_secret) > 8 and pin_or_totp_secret.isalnum() and not pin_or_totp_secret.isdigit():
                self.ui.verbose_log(f"Using TOTP authentication", username=username)
                try:
                    totp = pyotp.TOTP(pin_or_totp_secret)
                    current_value = totp.now()
                    self.ui.verbose_log(f"Generated TOTP: {current_value}", username=username)
                except Exception as totp_error:
                    self.ui.log(f"Failed to generate TOTP: {totp_error}", "error", username)
                    return False
            else:
                self.ui.verbose_log(f"Using static PIN authentication", username=username)
                current_value = pin_or_totp_secret
            
            # Enter the 2FA code
            pin_input.clear()
            time.sleep(0.1)
            pin_input.send_keys(current_value)
            time.sleep(Config.POST_2FA_KEY_DELAY)
            
            # Submit the 2FA form
            pin_submit_button = wait.until(EC.element_to_be_clickable(Config.PIN_SUBMIT_BUTTON_LOCATOR))
            self.ui.verbose_log(f"Submitting 2FA", username=username)
            pin_submit_button.click()
            time.sleep(Config.POST_FINAL_SUBMIT_DELAY)
            
            self.ui.log(f"2FA submitted successfully", "success", username)
            return True
            
        except TimeoutException:
            self.ui.verbose_log(f"2FA input field not detected within timeout", username=username)
            if not pin_or_totp_secret.strip():
                self.ui.verbose_log(f"Assuming no 2FA was needed", "info", username)
                return True
            else:
                self.ui.log(f"PIN/TOTP provided but 2FA field not found", "warning", username)
                return False
        except Exception as e:
            self.ui.log(f"Error during 2FA handling: {e}", "error", username)
            if self.ui.verbose:
                traceback.print_exc()
            return False
    
    def save_screenshot(self, driver: webdriver.Chrome, filename: str, username: str):
        """Save a screenshot of the current browser state."""
        try:
            driver.save_screenshot(filename)
            self.ui.verbose_log(f"Screenshot saved: {filename}", "info", username)
        except Exception as e:
            self.ui.verbose_log(f"Failed to save screenshot: {e}", "warning", username)

# ==========================================================================
# --- Login Process Orchestration ---
# ==========================================================================

class LoginSession:
    """Handles the complete login process for a single account."""
    
    def __init__(self, credentials: Dict[str, str], ui: TerminalUI, browser_manager: BrowserManager):
        """Initialize with account credentials and managers."""
        self.credentials = credentials
        self.username = credentials.get(Config.CSV_USERNAME_HEADER, 'UNKNOWN_USER')
        self.ui = ui
        self.browser_manager = browser_manager
    
    def execute(self) -> bool:
        """Execute the complete login process."""
        self.ui.log(f"Starting login process", username=self.username)
        driver = None
        login_successful = False
        
        try:
            # Initialize browser
            driver = self.browser_manager.setup_driver(self.username)
            if not driver:
                return False
            
            # Execute login steps
            wait = self.browser_manager.navigate_to_login(driver, self.username)
            self.browser_manager.enter_credentials(
                wait, 
                self.credentials[Config.CSV_USERNAME_HEADER], 
                self.credentials[Config.CSV_PASSWORD_HEADER], 
                self.username
            )
            self.browser_manager.submit_initial_login(wait, self.username)
            
            # Handle 2FA if needed
            pin_or_totp = self.credentials.get(Config.CSV_2FA_HEADER, '')
            two_fa_success = self.browser_manager.handle_two_factor_auth(wait, pin_or_totp, self.username)
            
            if two_fa_success:
                self.ui.log(f"Login completed successfully", "success", self.username)
                login_successful = True
            else:
                self.ui.log(f"Login failed during 2FA", "error", self.username)
                login_successful = False
                
        except (TimeoutException, NoSuchElementException) as e:
            error_type = type(e).__name__
            self.ui.log(f"Element not found: {e}", "error", self.username)
            if driver:
                self.browser_manager.save_screenshot(
                    driver, 
                    f"{self.username}_{error_type.lower()}_error.png", 
                    self.username
                )
        except KeyError as e:
            self.ui.log(f"Missing key in credentials: {e}", "error", self.username)
        except Exception as e:
            self.ui.log(f"Unexpected error: {e}", "error", self.username)
            if self.ui.verbose:
                traceback.print_exc()
            if driver:
                self.browser_manager.save_screenshot(
                    driver, 
                    f"{self.username}_unexpected_error.png", 
                    self.username
                )
        finally:
            status = "successful" if login_successful else "failed"
            self.ui.log(f"Login process {status}", "info" if login_successful else "error", self.username)
            return login_successful

# ==========================================================================
# --- Main Application Class ---
# ==========================================================================

class ZerodhaLoginBot:
    """Main application class that orchestrates the entire login process."""
    
    def __init__(self, args: argparse.Namespace):
        """Initialize with command-line arguments."""
        self.args = args
        self.ui = TerminalUI(verbose=args.verbose)
        self.credential_manager = CredentialManager(self.ui)
        self.browser_manager = BrowserManager(self.ui, headless=args.headless)
    
    def run(self):
        """Execute the main application workflow."""
        # Display application banner
        self.ui.print_banner()
        
        # Read account credentials
        credentials_file = self.args.credentials or Config.CREDENTIALS_FILE
        accounts_data = self.credential_manager.read_credentials(credentials_file)
        if not accounts_data:
            self.ui.log("Exiting due to credential reading errors.", "error")
            sys.exit(1)
        
        # Display account summary
        self.ui.print_summary(accounts_data)
        
        # Confirm before proceeding
        if not self.args.yes and not self._confirm_proceed(len(accounts_data)):
            self.ui.log("Operation cancelled by user.", "warning")
            sys.exit(0)
        
        # Execute login sessions
        self.ui.log(f"Starting login sessions for {len(accounts_data)} account(s)...")
        
        if self.args.parallel:
            self._run_parallel(accounts_data)
        else:
            self._run_sequential(accounts_data)
        
        self.ui.log("All login sessions completed.", "highlight")
        self.ui.log("Browser windows remain open for your interaction.", "info")
    
    def _confirm_proceed(self, account_count: int) -> bool:
        """Ask for user confirmation before proceeding."""
        self.ui.console.print()
        response = input(f"Proceed with login for {account_count} account(s)? [y/N]: ").strip().lower()
        return response == 'y' or response == 'yes'
    
    def _run_sequential(self, accounts_data: List[Dict[str, str]]):
        """Run login sessions sequentially with visual progress tracking."""
        with self.ui.create_progress() as progress:
            task = progress.add_task("[cyan]Processing accounts...", total=len(accounts_data))
            
            for i, credentials in enumerate(accounts_data):
                username = credentials.get(Config.CSV_USERNAME_HEADER, f"Account-{i+1}")
                progress.update(task, description=f"[cyan]Processing [green]{username}[/green]...")
                
                session = LoginSession(credentials, self.ui, self.browser_manager)
                success = session.execute()
                
                # Add delay between browser launches
                if i < len(accounts_data) - 1:
                    time.sleep(Config.BROWSER_LAUNCH_DELAY)
                
                progress.update(task, advance=1)
    
    def _run_parallel(self, accounts_data: List[Dict[str, str]]):
        """Run login sessions in parallel using ThreadPoolExecutor."""
        self.ui.log("Running sessions in parallel mode", "highlight")
        
        def process_account(credentials):
            session = LoginSession(credentials, self.ui, self.browser_manager)
            return session.execute()
        
        with ThreadPoolExecutor(max_workers=min(len(accounts_data), 5)) as executor:
            futures = [executor.submit(process_account, credentials) for credentials in accounts_data]
            
            with tqdm(total=len(accounts_data), desc="Processing accounts", unit="account") as pbar:
                for future in futures:
                    future.result()  # Wait for each future to complete
                    pbar.update(1)

# ==========================================================================
# --- Command Line Interface ---
# ==========================================================================

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Zerodha Multi-Account Login Bot",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "-c", "--credentials", 
        help=f"Path to credentials CSV file (default: {Config.CREDENTIALS_FILE})"
    )
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "-y", "--yes", 
        action="store_true", 
        help="Skip confirmation prompt and proceed automatically"
    )
    
    parser.add_argument(
        "-p", "--parallel", 
        action="store_true", 
        help="Run login sessions in parallel instead of sequentially"
    )
    
    parser.add_argument(
        "--headless", 
        action="store_true", 
        help="Run browsers in headless mode (no GUI)"
    )
    
    return parser.parse_args()

# ==========================================================================
# --- Entry Point ---
# ==========================================================================

def main():
    """Application entry point."""
    args = parse_arguments()
    bot = ZerodhaLoginBot(args)
    bot.run()

if __name__ == "__main__":
    main()