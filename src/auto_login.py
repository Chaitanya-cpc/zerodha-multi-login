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
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

# Suppress Python's verbose import messages
sys.modules['torch'] = None  # Prevent any potential pytorch import messages
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)  # Suppress large int representation warnings
os.environ['PYTHONVERBOSE'] = '0'  # Turn off verbose imports

# Third-party Imports
import pyotp
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.table import Table
from rich.theme import Theme
from rich import box
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.layout import Layout
from rich.live import Live
from tqdm import tqdm

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
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

# ==========================================================================
# --- Configuration ---
# ==========================================================================

class Config:
    """Central configuration settings for the application."""
    
    # File Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONFIG_DIR = os.path.join(BASE_DIR, 'config')
    CREDENTIALS_FILE = os.path.join(CONFIG_DIR, 'zerodha_credentials.csv')
    
    # Account Groups configuration
    GROUPS_CONFIG_FILE = os.path.join(CONFIG_DIR, 'account_groups.json')
    
    # Logs directory
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    
    # URLs
    ZERODHA_LOGIN_URL = "https://kite.zerodha.com/"
    
    # Timeouts and Delays (seconds)
    WEBDRIVER_WAIT_TIMEOUT = 30
    SHORT_DELAY = 0.75
    INTER_KEY_DELAY = 0.375  # SHORT_DELAY / 2
    POST_LOGIN_CLICK_DELAY = 4.0
    POST_2FA_KEY_DELAY = 1.0
    POST_FINAL_SUBMIT_DELAY = 0.75  # SHORT_DELAY
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
    PIN_INPUT_ID_NAME = "userid"  # Restored to the original value
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
        "success": "green bold",
        "warning": "yellow bold",
        "error": "bold red",
        "highlight": "bold magenta",
        "zerodha": "bold #ff5722",  # Zerodha's orange
        "title": "bold cyan",
        "subtitle": "italic cyan",
        "header": "bold blue",
        "value": "bold white",
        "status.pending": "yellow",
        "status.running": "cyan",
        "status.success": "green",
        "status.failed": "red",
    })
    
    def __init__(self, verbose: bool = False, log_to_file: bool = True):
        """Initialize the terminal UI components."""
        self.console = Console(theme=self.CUSTOM_THEME)
        self.verbose = verbose
        self.start_time = time.time()
        self.log_to_file = log_to_file
        self.log_file = None
        
        # Initialize log file if needed
        if self.log_to_file:
            self._setup_log_file()
    
    def clear_screen(self):
        """Clear the terminal screen."""
        # Cross-platform clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _setup_log_file(self):
        """Set up the log file."""
        # Create logs directory if it doesn't exist
        if not os.path.exists(Config.LOGS_DIR):
            os.makedirs(Config.LOGS_DIR)
        
        # Create a timestamped log file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_filepath = os.path.join(Config.LOGS_DIR, f"zerodha_login_{timestamp}.log")
        
        try:
            self.log_file = open(log_filepath, 'w', encoding='utf-8')
            self.log_file.write(f"=== Zerodha Login Bot Log - {timestamp} ===\n\n")
            self.console.print(f"[info]Logging to file: {log_filepath}[/info]")
        except Exception as e:
            self.console.print(f"[error]Failed to create log file: {e}[/error]")
            self.log_to_file = False
    
    def print_info(self, message: str, username: str = None):
        """Print an info message."""
        self.log(message, "info", username)
    
    def print_success(self, message: str, username: str = None):
        """Print a success message."""
        self.log(message, "success", username)
    
    def print_warning(self, message: str, username: str = None):
        """Print a warning message."""
        self.log(message, "warning", username)
    
    def print_error(self, message: str, username: str = None):
        """Print an error message."""
        self.log(message, "error", username)
    
    def print_verbose(self, message: str, username: str = None):
        """Print a verbose message if verbose mode is enabled."""
        self.verbose_log(message, "info", username)
    
    def __del__(self):
        """Clean up resources on deletion."""
        if self.log_file:
            try:
                self.log_file.close()
            except:
                pass
    
    def print_banner(self):
        """Display the application banner."""
        # Beautiful, enhanced banner with ASCII art
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
    ║    ║   🚀 Multi-Account Login Automation System            ║ ║
    ║    ║   ✨ Professional Trading Platform Management         ║ ║
    ║    ╚═══════════════════════════════════════════════════════╝ ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
        """
        version = "v1.1.0"
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        # Enhanced spacing and presentation
        self.console.print()
        self.console.print(Panel(banner_text, style="zerodha", expand=False, border_style="bold #ff5722", padding=(1, 2)))
        self.console.print()
        self.console.print(Panel.fit(
            f"[bold cyan]🚀 Zerodha Trading Platform Automation[/bold cyan]\n\n"
            f"[dim]Version:[/dim] [bold white]{version}[/bold white]  [dim]|[/dim]  "
            f"[dim]Started:[/dim] [bold white]{current_time}[/bold white]",
            style="cyan",
            border_style="bright_cyan",
            padding=(0, 2)
        ))
        self.console.print()
        self.console.print("[bold cyan]" + "═" * 72 + "[/bold cyan]")
        self.console.print()
        
        # Log to file
        if self.log_to_file and self.log_file:
            self.log_file.write(f"Zerodha Trading Platform Automation {version}\n")
            self.log_file.write(f"Started at: {current_time}\n")
            self.log_file.write("=" * 60 + "\n")
    
    def print_summary(self, accounts_data: List[Dict[str, str]]):
        """Display a summary of accounts to be processed."""
        self.console.print()
        self.console.print(Panel.fit(
            "[bold bright_magenta]📊 Account Processing Summary[/bold bright_magenta]",
            style="highlight",
            border_style="bright_magenta",
            padding=(0, 2)
        ))
        self.console.print()
        
        table = Table(
            title="[bold bright_cyan]┌─ Accounts to Process ─┐[/bold bright_cyan]",
            show_header=True,
            header_style="bold bright_blue on dark_blue",
            box=box.ROUNDED,
            border_style="bright_cyan",
            title_style="bold bright_cyan",
            show_lines=True,
            padding=(0, 1)
        )
        table.add_column("[bold]№[/bold]", style="bold cyan", justify="center", width=5, no_wrap=True)
        table.add_column("[bold]Username[/bold]", style="bold white", width=15, no_wrap=True)
        table.add_column("[bold]2FA Method[/bold]", style="bold yellow", justify="center", width=12)
        table.add_column("[bold]Status[/bold]", style="dim white", justify="center", width=12)
        table.add_column("[bold]Active[/bold]", style="bold green", justify="center", width=10)
        
        for i, account in enumerate(accounts_data, start=1):
            username = account.get(Config.CSV_USERNAME_HEADER, "N/A")
            pin_or_totp = account.get(Config.CSV_2FA_HEADER, "")
            status = account.get(Config.CSV_STATUS_HEADER, "1")
            two_fa_type = "[bold green]🔐 TOTP[/bold green]" if len(pin_or_totp) > 8 and pin_or_totp.isalnum() and not pin_or_totp.isdigit() else "[bold yellow]🔑 PIN[/bold yellow]" if pin_or_totp else "[dim]❌ None[/dim]"
            active_status = "[bold green]✅ Active[/bold green]" if status == "1" else "[dim]⏸️  Inactive[/dim]"
            table.add_row(
                f"[cyan]{i}[/cyan]", 
                f"[bold white]{username}[/bold white]", 
                two_fa_type, 
                "[yellow]⏳ Pending[/yellow]", 
                active_status
            )
        
        self.console.print(table)
        self.console.print()
        self.console.print(Panel.fit(
            f"[bold bright_green]✅ Total Accounts to Process: [bold white]{len(accounts_data)}[/bold white][/bold bright_green]",
            border_style="bright_green",
            padding=(0, 2)
        ))
        self.console.print()
    
    def log(self, message: str, level: str = "info", username: str = None):
        """Log a message with the appropriate styling and timestamp."""
        if level not in ["info", "success", "warning", "error", "highlight"]:
            level = "info"
            
        # Add timestamp
        elapsed = time.time() - self.start_time
        elapsed_str = f"{elapsed:.1f}s"
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        
        # Create prefixes
        time_prefix = f"[dim]{timestamp}[/dim]"
        elapsed_prefix = f"[dim](+{elapsed_str})[/dim]"
        user_prefix = f"[bold]{username}[/bold]" if username else ""
        
        # Format the log message with appropriate icons based on level
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
        if username:
            log_msg = f"{time_prefix} {elapsed_prefix} {level_style}{icon}[/] [bold]{username}[/bold] {message}"
        else:
            log_msg = f"{time_prefix} {elapsed_prefix} {level_style}{icon}[/] {message}"
            
        self.console.print(log_msg)
        
        # Write to log file if enabled
        if self.log_to_file and self.log_file:
            # Plain text version for the log file (without formatting)
            plain_icon = {
                "info": "[i]",
                "success": "[+]",
                "warning": "[!]",
                "error": "[X]",
                "highlight": "[*]"
            }.get(level, "[-]")
            
            plain_prefix = f"[{username}]" if username else ""
            log_file_msg = f"{timestamp} (+{elapsed_str}) {plain_icon} {plain_prefix} {message}\n"
            
            try:
                self.log_file.write(log_file_msg)
                self.log_file.flush()  # Ensure it's written immediately
            except Exception as e:
                # If we can't write to the log file, disable file logging and show an error
                self.console.print(f"[error]Error writing to log file: {e}[/error]")
                self.log_to_file = False
    
    def verbose_log(self, message: str, level: str = "info", username: str = None):
        """Log a message only if verbose mode is enabled."""
        if self.verbose:
            self.log(message, level, username)
    
    def create_progress(self):
        """Create and return a progress bar for tracking operations."""
        return Progress(
            TextColumn("[progress.description]{task.description}"),
            SpinnerColumn("dots"),
            BarColumn(bar_width=30),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
            console=self.console,
            expand=True
        )

# ==========================================================================
# --- Helper Functions ---
# ==========================================================================

class CredentialManager:
    """Handles reading and validating account credentials."""
    
    def __init__(self, ui: TerminalUI):
        """Initialize with UI reference for logging."""
        self.ui = ui
        self.credentials_file = Config.CREDENTIALS_FILE
        self.credentials_cache = {}
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure the config directory exists."""
        os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
    
    def set_credentials_file(self, filepath):
        """Set the credentials file path."""
        self.credentials_file = filepath
    
    def read_credentials(self, filepath: str = None) -> Optional[List[Dict[str, str]]]:
        """Read and validate credentials from the specified CSV file."""
        if filepath:
            self.credentials_file = filepath
            
        accounts_data = []
        self.ui.log(f"Reading credentials from: {self.credentials_file}")
        
        try:
            with open(self.credentials_file, mode='r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                # Validate CSV structure
                if not reader.fieldnames or not all(header in reader.fieldnames for header in Config.REQUIRED_CSV_HEADERS):
                    self.ui.log(f"Credentials file missing required headers {Config.REQUIRED_CSV_HEADERS}", "error")
                    return None
                
                for row in reader:
                    username = row.get(Config.CSV_USERNAME_HEADER, "").strip()
                    password = row.get(Config.CSV_PASSWORD_HEADER, "").strip()
                    pin_or_totp = row.get(Config.CSV_2FA_HEADER, "").strip()
                    status = row.get(Config.CSV_STATUS_HEADER, "").strip()
                    
                    if username and password:
                        # Check if status column exists and filter by status "1"
                        if Config.CSV_STATUS_HEADER in row:
                            if status != "1":
                                self.ui.verbose_log(f"Skipped account {username} - status is '{status}' (not '1')", "warning")
                                continue
                        
                        if Config.CSV_2FA_HEADER not in row: 
                            row[Config.CSV_2FA_HEADER] = ''
                        if Config.CSV_STATUS_HEADER not in row:
                            row[Config.CSV_STATUS_HEADER] = ''
                        accounts_data.append(row)
                        self.ui.verbose_log(f"Added account: {username}", "success")
                    else:
                        self.ui.verbose_log(f"Skipped row due to missing Username or Password", "warning")
            
            if not accounts_data:
                self.ui.log("No valid account credentials found.", "error")
                return None
                
            self.ui.log(f"Successfully loaded {len(accounts_data)} account(s)", "success")
            
            # Cache the credentials for faster access
            self.credentials_cache = {row[Config.CSV_USERNAME_HEADER]: row for row in accounts_data}
            
            return accounts_data
            
        except FileNotFoundError:
            self.ui.log(f"Credentials file not found: '{self.credentials_file}'", "error")
            
            # Create an empty CSV file
            try:
                with open(self.credentials_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(Config.REQUIRED_CSV_HEADERS + [Config.CSV_2FA_HEADER, Config.CSV_STATUS_HEADER])
                self.ui.log(f"Created new credentials file: {self.credentials_file}", "success")
            except Exception as e:
                self.ui.log(f"Failed to create credentials file: {e}", "error")
            
            return []
            
        except Exception as e:
            self.ui.log(f"Failed to read/parse credentials: {e}", "error")
            if self.ui.verbose:
                traceback.print_exc()
            return None
    
    def list_accounts(self) -> List[str]:
        """Return a list of all account usernames."""
        # Try to use cached credentials first
        if self.credentials_cache:
            return list(self.credentials_cache.keys())
        
        # Otherwise, read from file
        accounts_data = self.read_credentials()
        if not accounts_data:
            return []
        
        return [account[Config.CSV_USERNAME_HEADER] for account in accounts_data]
    
    def get_credentials(self, account_id: str) -> Optional[Dict[str, str]]:
        """Get credentials for a specific account."""
        # Try to use cached credentials first
        if account_id in self.credentials_cache:
            return self.credentials_cache[account_id]
        
        # Otherwise, read from file
        accounts_data = self.read_credentials()
        if not accounts_data:
            return None
        
        for account in accounts_data:
            if account[Config.CSV_USERNAME_HEADER] == account_id:
                return {
                    "user_id": account[Config.CSV_USERNAME_HEADER],
                    "password": account[Config.CSV_PASSWORD_HEADER],
                    "pin": account.get(Config.CSV_2FA_HEADER, ""),
                    "totp_secret": account.get(Config.CSV_2FA_HEADER, ""),
                    "status": account.get(Config.CSV_STATUS_HEADER, "1")
                }
        
        return None
    
    def save_credentials(self, account_id: str, credentials: Dict[str, str]) -> bool:
        """Save or update credentials for a specific account."""
        accounts = self.list_accounts()
        
        # Read existing data
        all_accounts = []
        headers = Config.REQUIRED_CSV_HEADERS + [Config.CSV_2FA_HEADER, Config.CSV_STATUS_HEADER]
        
        try:
            # Try to read existing data
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'r', newline='', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    if reader.fieldnames:
                        headers = reader.fieldnames
                    all_accounts = [row for row in reader]
        except Exception as e:
            self.ui.log(f"Error reading credentials file: {e}", "error")
            return False
        
        # Update or add the account
        account_updated = False
        for account in all_accounts:
            if account.get(Config.CSV_USERNAME_HEADER) == account_id:
                account[Config.CSV_USERNAME_HEADER] = credentials.get("user_id", account_id)
                account[Config.CSV_PASSWORD_HEADER] = credentials.get("password", "")
                account[Config.CSV_2FA_HEADER] = credentials.get("pin", credentials.get("totp_secret", ""))
                account[Config.CSV_STATUS_HEADER] = credentials.get("status", "1")  # Default to "1" if not specified
                account_updated = True
                break
        
        if not account_updated:
            # Add new account
            new_account = {
                Config.CSV_USERNAME_HEADER: credentials.get("user_id", account_id),
                Config.CSV_PASSWORD_HEADER: credentials.get("password", ""),
                Config.CSV_2FA_HEADER: credentials.get("pin", credentials.get("totp_secret", "")),
                Config.CSV_STATUS_HEADER: credentials.get("status", "1")  # Default to "1" if not specified
            }
            all_accounts.append(new_account)
        
        # Write back to file
        try:
            with open(self.credentials_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(all_accounts)
            
            # Update cache
            self.read_credentials()
            return True
        except Exception as e:
            self.ui.log(f"Error saving credentials: {e}", "error")
            return False
    
    def delete_credentials(self, account_id: str) -> bool:
        """Delete credentials for a specific account."""
        # Read existing data
        all_accounts = []
        headers = Config.REQUIRED_CSV_HEADERS + [Config.CSV_2FA_HEADER, Config.CSV_STATUS_HEADER]
        
        try:
            # Try to read existing data
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'r', newline='', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    if reader.fieldnames:
                        headers = reader.fieldnames
                    all_accounts = [row for row in reader if row.get(Config.CSV_USERNAME_HEADER) != account_id]
        except Exception as e:
            self.ui.log(f"Error reading credentials file: {e}", "error")
            return False
        
        # Write back to file
        try:
            with open(self.credentials_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(all_accounts)
            
            # Update cache
            if account_id in self.credentials_cache:
                del self.credentials_cache[account_id]
            
            return True
        except Exception as e:
            self.ui.log(f"Error deleting credentials: {e}", "error")
            return False

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
            
            # Additional options for better compatibility
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Fix headless mode deprecation warning
            if self.headless:
                options.add_argument('--headless')
            
            # Use webdriver-manager if available for automatic ChromeDriver management
            if WEBDRIVER_MANAGER_AVAILABLE:
                try:
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                    self.ui.verbose_log(f"Chrome launched successfully (using webdriver-manager)", "success", username)
                except Exception as wdm_error:
                    self.ui.verbose_log(f"webdriver-manager failed, trying PATH: {wdm_error}", "warning", username)
                    # Fallback to PATH-based ChromeDriver
                    driver = webdriver.Chrome(options=options)
                    self.ui.verbose_log(f"Chrome launched successfully (using PATH)", "success", username)
            else:
                # Fallback to PATH-based ChromeDriver
                driver = webdriver.Chrome(options=options)
                self.ui.verbose_log(f"Chrome launched successfully", "success", username)
            
            # Execute script to remove automation indicators
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
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
            self.ui.verbose_log(f"Waiting for 2FA input field (id='{Config.PIN_INPUT_ID_NAME}') to be clickable...", username=username)
            pin_input = wait.until(EC.element_to_be_clickable(Config.PIN_INPUT_LOCATOR))
            self.ui.verbose_log(f"2FA screen detected and input field clickable.", "success", username)
            
            pin_or_totp_secret = pin_or_totp_secret.strip()
            self.ui.verbose_log(f"DEBUG: 2FA Value from CSV: '{pin_or_totp_secret}'", username=username)
            
            if not pin_or_totp_secret:
                self.ui.log(f"WARNING: 2FA required but no PIN/TOTP found.", "error", username)
                return False
            
            self.ui.verbose_log(f"Attempting to enter PIN/TOTP...", username=username)
            
            # Determine if we're using TOTP or static PIN
            current_value_to_send = ""
            if len(pin_or_totp_secret) > 8 and pin_or_totp_secret.isalnum() and not pin_or_totp_secret.isdigit():
                self.ui.verbose_log(f"DEBUG: Treating as TOTP Secret.", username=username)
                try:
                    totp = pyotp.TOTP(pin_or_totp_secret)
                    current_otp = totp.now()
                    self.ui.verbose_log(f"DEBUG: Generated TOTP: {current_otp}", username=username)
                    current_value_to_send = current_otp
                except Exception as totp_gen_error:
                    self.ui.log(f"ERROR generating TOTP: {totp_gen_error}", "error", username)
                    return False
            else:
                self.ui.verbose_log(f"DEBUG: Treating as static PIN/Other value.", username=username)
                current_value_to_send = pin_or_totp_secret
            
            # Enter the 2FA code
            self.ui.verbose_log(f"DEBUG: Sending keys: '{current_value_to_send}'", username=username)
            self.ui.verbose_log(f"DEBUG: Clearing 2FA input field...", username=username)
            pin_input.clear()
            time.sleep(0.1)
            pin_input.send_keys(current_value_to_send)
            self.ui.verbose_log(f"DEBUG: Pausing {Config.POST_2FA_KEY_DELAY}s...", username=username)
            time.sleep(Config.POST_2FA_KEY_DELAY)
            
            # Submit the 2FA form
            self.ui.verbose_log(f"Waiting for 2FA submit button...", username=username)
            pin_submit_button = wait.until(EC.element_to_be_clickable(Config.PIN_SUBMIT_BUTTON_LOCATOR))
            self.ui.verbose_log(f"Submitting PIN/TOTP...", username=username)
            pin_submit_button.click()
            
            # Report immediate success after TOTP submission without waiting
            self.ui.log(f"2FA submitted successfully.", "success", username)
            
            # Skip the delay for terminal reporting purposes - browser will continue in background
            # time.sleep(Config.POST_FINAL_SUBMIT_DELAY)
            
            return True
            
        except TimeoutException:
            self.ui.verbose_log(f"INFO: 2FA input field (id='{Config.PIN_INPUT_ID_NAME}') not detected or clickable within timeout.", username=username)
            if not pin_or_totp_secret.strip():
                self.ui.verbose_log(f"Assuming no 2FA was needed.", "info", username)
                return True
            else:
                # Attempt to check if we're already on the dashboard despite the timeout
                try:
                    # Check for common elements on the logged-in dashboard
                    if "dashboard" in wait._driver.current_url.lower() or "kite.zerodha.com/dashboard" in wait._driver.current_url:
                        self.ui.log(f"Login appears successful despite 2FA detection issues.", "success", username)
                        return True
                except:
                    pass
                
                self.ui.log(f"WARNING: PIN/TOTP provided but 2FA field not interactable.", "warning", username)
                return False
        except Exception as e:
            self.ui.log(f"ERROR during 2FA handling: {e}", "error", username)
            if self.ui.verbose:
                traceback.print_exc()
            
            # Check if we're already on the dashboard despite the error
            try:
                # Check for common elements on the logged-in dashboard
                if "dashboard" in wait._driver.current_url.lower() or "kite.zerodha.com/dashboard" in wait._driver.current_url:
                    self.ui.log(f"Login appears successful despite 2FA handling errors.", "success", username)
                    return True
            except:
                pass
                
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
    
    def __init__(self, credentials: Dict[str, str], ui: TerminalUI, browser_manager: BrowserManager, 
                 status_tracker=None, status_lock=None):
        """Initialize with account credentials and managers."""
        self.credentials = credentials
        self.username = credentials.get(Config.CSV_USERNAME_HEADER, 'UNKNOWN_USER')
        self.ui = ui
        self.browser_manager = browser_manager
        self.status_tracker = status_tracker
        self.status_lock = status_lock
    
    def update_status(self, status: str, completed: bool = False):
        """Update the login status in the shared tracker."""
        if self.status_tracker is not None and self.status_lock is not None:
            with self.status_lock:
                self.status_tracker[self.username]["status"] = status
                if completed:
                    self.status_tracker[self.username]["completed"] = True
    
    def execute(self) -> bool:
        """Execute the complete login process."""
        self.ui.log(f"Starting login process", username=self.username)
        driver = None
        login_successful = False
        
        try:
            # Initialize browser
            driver = self.browser_manager.setup_driver(self.username)
            if not driver:
                self.update_status("failed", True)
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
                # Since 2FA is successful, we can immediately report login success
                self.ui.log(f"Login completed successfully", "success", self.username)
                login_successful = True
                
                # Update status immediately for real-time tracking
                self.update_status("success", True)
                
                # Return success but let thread continue running in background
                return login_successful
            else:
                self.ui.log(f"Login failed during 2FA", "error", self.username)
                login_successful = False
                self.update_status("failed", True)
                
        except (TimeoutException, NoSuchElementException) as e:
            error_type = type(e).__name__
            self.ui.log(f"Element not found: {e}", "error", self.username)
            if driver:
                self.browser_manager.save_screenshot(
                    driver, 
                    f"{self.username}_{error_type.lower()}_error.png", 
                    self.username
                )
            self.update_status("failed", True)
        except KeyError as e:
            self.ui.log(f"Missing key in credentials: {e}", "error", self.username)
            self.update_status("failed", True)
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
            self.update_status("failed", True)
        finally:
            if not login_successful:
                self.ui.log(f"Login process failed", "error", self.username)
                # Ensure status is updated in case it wasn't done earlier
                self.update_status("failed", True)
            return login_successful

# ==========================================================================
# --- Main Application Class ---
# ==========================================================================

class ZerodhaLoginBot:
    """Main application class that orchestrates the entire login process."""
    
    def __init__(self, args: argparse.Namespace):
        """Initialize with command-line arguments."""
        self.args = args
        
        # Set up logging
        log_to_file = not args.no_log_file
        
        # If log_dir is specified, update the Config
        if args.log_dir:
            Config.LOGS_DIR = args.log_dir
            
        # Initialize UI and managers
        self.ui = TerminalUI(verbose=args.verbose, log_to_file=log_to_file)
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
            
        # Filter accounts if specified
        if self.args.accounts:
            accounts_data = self._filter_accounts_by_username(accounts_data, self.args.accounts)
            if not accounts_data:
                self.ui.log("No matching accounts found. Please check the account names provided.", "error")
                sys.exit(1)
                
        # Interactive mode if requested
        if self.args.interactive:
            accounts_data = self._select_accounts_interactively(accounts_data)
            if not accounts_data:
                self.ui.log("No accounts selected. Exiting.", "warning")
                sys.exit(0)
        
        # Display account summary
        self.ui.print_summary(accounts_data)
        
        # Enable verbose mode for better debugging if needed
        if not self.args.verbose:
            self.ui.console.print(Panel.fit(
                "[bold yellow]💡 TIP:[/bold yellow] Run with [bold white]-v[/bold white] flag for detailed debug output",
                border_style="yellow",
                padding=(0, 1)
            ))
            self.ui.console.print()
        
        # Confirm before proceeding
        if not self.args.yes and not self._confirm_proceed(len(accounts_data)):
            self.ui.log("Operation cancelled by user.", "warning")
            sys.exit(0)
        
        # Execute login sessions
        self.ui.console.print()
        self.ui.console.print(Panel.fit(
            f"[bold bright_cyan]🚀 Starting Login Sessions[/bold bright_cyan]\n"
            f"[dim]Processing {len(accounts_data)} account(s) in parallel mode[/dim]",
            border_style="bright_cyan",
            padding=(0, 2)
        ))
        self.ui.console.print()
        self.ui.log(f"Starting login sessions for {len(accounts_data)} account(s)...", "highlight")
        self.ui.log(f"Configuration Parameters:")
        self.ui.console.print(f"  [dim]├─[/dim] [bold white]WEBDRIVER_WAIT_TIMEOUT:[/bold white] [cyan]{Config.WEBDRIVER_WAIT_TIMEOUT}s[/cyan]")
        self.ui.console.print(f"  [dim]├─[/dim] [bold white]SHORT_DELAY:[/bold white] [cyan]{Config.SHORT_DELAY}s[/cyan]")
        self.ui.console.print(f"  [dim]├─[/dim] [bold white]POST_LOGIN_CLICK_DELAY:[/bold white] [cyan]{Config.POST_LOGIN_CLICK_DELAY}s[/cyan]")
        self.ui.console.print(f"  [dim]└─[/dim] [bold white]POST_2FA_KEY_DELAY:[/bold white] [cyan]{Config.POST_2FA_KEY_DELAY}s[/cyan]")
        self.ui.console.print()
        
        # Always use parallel processing for faster login
        self._run_parallel(accounts_data)
        
        self.ui.console.print()
        self.ui.console.print(Panel.fit(
            "[bold bright_green]✅ All Login Sessions Completed Successfully![/bold bright_green]\n\n"
            "[dim]All browser windows remain open for your interaction[/dim]",
            border_style="bright_green",
            padding=(1, 2)
        ))
        self.ui.console.print()
        self.ui.log("All login sessions completed.", "highlight")
        self.ui.log("Browser windows remain open for your interaction.", "info")
    
    def _filter_accounts_by_username(self, accounts_data: List[Dict[str, str]], username_str: str) -> List[Dict[str, str]]:
        """Filter accounts based on comma-separated username list."""
        usernames = [u.strip() for u in username_str.split(',') if u.strip()]
        self.ui.log(f"Filtering accounts by username: {', '.join(usernames)}", "info")
        
        filtered_accounts = []
        for account in accounts_data:
            username = account.get(Config.CSV_USERNAME_HEADER)
            if username in usernames:
                filtered_accounts.append(account)
                self.ui.verbose_log(f"Selected account: {username}", "success")
        
        self.ui.log(f"Found {len(filtered_accounts)} matching accounts", "info")
        return filtered_accounts
    
    def _select_accounts_interactively(self, accounts_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Allow interactive selection of accounts."""
        self.ui.clear_screen()
        self.ui.console.print(Panel(
            "[title]Interactive Account Selection[/title]\n\n"
            "Select which accounts you want to log in to.",
            title="Account Selection Mode", 
            style="highlight"
        ))
        
        # Show available accounts
        account_table = Table(title="Available Accounts", show_header=True, box=box.ROUNDED)
        account_table.add_column("#", style="cyan", justify="center")
        account_table.add_column("Username", style="value")
        account_table.add_column("2FA Method", style="status.running")
        account_table.add_column("Active", style="status.success")
        
        for i, account in enumerate(accounts_data, start=1):
            username = account.get(Config.CSV_USERNAME_HEADER, "N/A")
            pin_or_totp = account.get(Config.CSV_2FA_HEADER, "")
            status = account.get(Config.CSV_STATUS_HEADER, "1")
            two_fa_type = "TOTP" if len(pin_or_totp) > 8 and pin_or_totp.isalnum() and not pin_or_totp.isdigit() else "PIN" if pin_or_totp else "None"
            active_status = "✓" if status == "1" else "✗"
            account_table.add_row(str(i), username, two_fa_type, active_status)
        
        self.ui.console.print(account_table)
        
        # Ask selection method
        selection_mode = Prompt.ask(
            "Selection mode", 
            choices=["all", "specific", "none"], 
            default="all"
        )
        
        selected_accounts = []
        
        if selection_mode == "all":
            self.ui.log("Selected all accounts", "success")
            return accounts_data
            
        elif selection_mode == "none":
            self.ui.log("No accounts selected", "warning")
            return []
            
        elif selection_mode == "specific":
            indices_input = Prompt.ask(
                "Enter account numbers separated by commas (e.g., 1,3,5)", 
                default="1"
            )
            
            try:
                indices = [int(idx.strip()) for idx in indices_input.split(',') if idx.strip()]
                for idx in indices:
                    if 1 <= idx <= len(accounts_data):
                        selected_accounts.append(accounts_data[idx-1])
                        self.ui.log(f"Selected account #{idx}: {accounts_data[idx-1].get(Config.CSV_USERNAME_HEADER)}", "success")
                    else:
                        self.ui.log(f"Invalid account number: {idx}", "warning")
            except ValueError:
                self.ui.log("Invalid input. Using all accounts as default.", "warning")
                return accounts_data
        
        if not selected_accounts and selection_mode == "specific":
            self.ui.log("No valid accounts selected. Using all accounts as default.", "warning")
            return accounts_data
            
        self.ui.log(f"Selected {len(selected_accounts)} accounts", "info")
        return selected_accounts
    
    def _confirm_proceed(self, account_count: int) -> bool:
        """Ask for user confirmation before proceeding."""
        self.ui.console.print()
        response = input(f"Proceed with login for {account_count} account(s)? [y/N]: ").strip().lower()
        return response == 'y' or response == 'yes'
    
    def _run_parallel(self, accounts_data: List[Dict[str, str]]):
        """Run login sessions in parallel using ThreadPoolExecutor."""
        self.ui.log("Launching all login sessions simultaneously", "highlight")
        
        # Create a shared status tracker for real-time updates
        login_status = {}
        status_lock = threading.Lock()
        
        # Create all threads but don't start them yet
        threads = []
        for credentials in accounts_data:
            username = credentials.get(Config.CSV_USERNAME_HEADER, "UNKNOWN")
            # Initialize status as pending
            login_status[username] = {"status": "pending", "completed": False}
            thread = threading.Thread(
                target=self._process_account_thread,
                args=(credentials, login_status, status_lock),
                name=f"Login-{username}"
            )
            threads.append(thread)
            
        # Start all threads at once for simultaneous processing
        self.ui.console.print(f"[bold bright_cyan]🌐 Opening [bold white]{len(threads)}[/bold white] browser windows simultaneously...[/bold bright_cyan]")
        self.ui.console.print()
        self.ui.log(f"Opening {len(threads)} browser windows simultaneously...", "highlight")
        for thread in threads:
            thread.start()
            
        # Wait for all threads to complete with real-time status updates
        with self.ui.create_progress() as progress:
            task = progress.add_task("[cyan]Waiting for all logins to complete...", total=len(threads))
            
            all_completed = False
            progress_check_interval = 0.1  # Check more frequently (was 0.5)
            
            while not all_completed:
                # Check each account's status for real-time updates
                completed_count = 0
                for username, status in login_status.items():
                    if status["completed"] and not status.get("reported", False):
                        # Mark as reported to avoid duplicate messages
                        with status_lock:
                            login_status[username]["reported"] = True
                        
                    if status["completed"]:
                        completed_count += 1
                
                # Update the progress bar based on completed logins, not thread completion
                progress.update(task, completed=completed_count)
                
                # Check if all accounts are done
                all_completed = completed_count == len(threads)
                
                # Small wait to avoid CPU spinning
                time.sleep(progress_check_interval)
            
            # Ensure progress reaches 100%
            progress.update(task, completed=len(threads))
        
        # Wait for all threads to actually terminate
        for thread in threads:
            thread.join()
    
    def _process_account_thread(self, credentials: Dict[str, str], status_tracker=None, status_lock=None):
        """Process a single account login in a separate thread."""
        username = credentials.get(Config.CSV_USERNAME_HEADER, "UNKNOWN")
        session = LoginSession(credentials, self.ui, self.browser_manager, status_tracker, status_lock)
        result = session.execute()
        
        # Mark this login as completed in the status tracker
        if status_tracker is not None and status_lock is not None:
            with status_lock:
                status_tracker[username]["completed"] = True
                status_tracker[username]["status"] = "success" if result else "failed"
        
        return result

# ==========================================================================
# --- Account Group Management ---
# ==========================================================================

class AccountGroup:
    """Represents a group of trading accounts."""
    
    def __init__(self, name: str, accounts: List[str], description: str = ""):
        """Initialize an account group.
        
        Args:
            name: Name of the account group
            accounts: List of account identifiers in this group
            description: Optional description of this group
        """
        self.name = name
        self.accounts = accounts
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the account group to a dictionary."""
        return {
            "name": self.name,
            "accounts": self.accounts,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccountGroup':
        """Create an account group from a dictionary."""
        return cls(
            name=data["name"],
            accounts=data["accounts"],
            description=data.get("description", "")
        )

class AccountGroupManager:
    """Manages account groups for the Zerodha Login Bot."""
    
    def __init__(self, ui: TerminalUI, credential_manager: CredentialManager):
        """Initialize the account group manager.
        
        Args:
            ui: The terminal UI instance
            credential_manager: The credential manager instance
        """
        self.ui = ui
        self.credential_manager = credential_manager
        self.groups: Dict[str, AccountGroup] = {}
        self.groups_file = Path(Config.CONFIG_DIR) / "account_groups.json"
        self._load_groups()
    
    def _load_groups(self) -> None:
        """Load account groups from the config file."""
        if not self.groups_file.exists():
            self.ui.print_info(f"Account groups file not found. Creating new at {self.groups_file}")
            self._save_groups()
            return
        
        try:
            with open(self.groups_file, 'r') as f:
                data = json.load(f)
            
            for group_data in data.get("groups", []):
                group = AccountGroup.from_dict(group_data)
                self.groups[group.name] = group
            
            self.ui.print_verbose(f"Loaded {len(self.groups)} account groups")
        except Exception as e:
            self.ui.print_error(f"Error loading account groups: {e}")
    
    def _save_groups(self) -> None:
        """Save account groups to the config file."""
        try:
            data = {
                "groups": [group.to_dict() for group in self.groups.values()]
            }
            
            # Create directory if it doesn't exist
            self.groups_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.groups_file, 'w') as f:
                json.dump(data, f, indent=4)
            
            self.ui.print_verbose(f"Saved {len(self.groups)} account groups")
        except Exception as e:
            self.ui.print_error(f"Error saving account groups: {e}")
    
    def get_group(self, name: str) -> Optional[AccountGroup]:
        """Get an account group by name."""
        return self.groups.get(name)
    
    def get_all_groups(self) -> List[AccountGroup]:
        """Get all account groups."""
        return list(self.groups.values())
    
    def create_group(self, name: str, accounts: List[str], description: str = "") -> AccountGroup:
        """Create a new account group."""
        # Validate group name
        if name in self.groups:
            raise ValueError(f"Group '{name}' already exists")
        
        # Validate accounts
        available_accounts = self.credential_manager.list_accounts()
        invalid_accounts = [acc for acc in accounts if acc not in available_accounts]
        if invalid_accounts:
            raise ValueError(f"Invalid accounts: {', '.join(invalid_accounts)}")
        
        # Create and save the group
        group = AccountGroup(name, accounts, description)
        self.groups[name] = group
        self._save_groups()
        return group
    
    def update_group(self, name: str, accounts: Optional[List[str]] = None, description: Optional[str] = None) -> AccountGroup:
        """Update an existing account group."""
        if name not in self.groups:
            raise ValueError(f"Group '{name}' does not exist")
        
        group = self.groups[name]
        
        if accounts is not None:
            # Validate accounts
            available_accounts = self.credential_manager.list_accounts()
            invalid_accounts = [acc for acc in accounts if acc not in available_accounts]
            if invalid_accounts:
                raise ValueError(f"Invalid accounts: {', '.join(invalid_accounts)}")
            group.accounts = accounts
        
        if description is not None:
            group.description = description
        
        self._save_groups()
        return group
    
    def delete_group(self, name: str) -> None:
        """Delete an account group."""
        if name not in self.groups:
            raise ValueError(f"Group '{name}' does not exist")
        
        del self.groups[name]
        self._save_groups()
    
    def get_accounts_for_group(self, group_name: str) -> List[str]:
        """Get the list of accounts for a specific group."""
        group = self.get_group(group_name)
        if not group:
            return []
        return group.accounts

# ==========================================================================
# --- Dashboard TUI ---
# ==========================================================================

class ZerodhaDashboard:
    """Interactive dashboard for managing Zerodha account logins."""
    
    def __init__(self, ui: TerminalUI, credential_manager: CredentialManager, 
                 account_group_manager: AccountGroupManager, browser_headless: bool = False):
        """Initialize the Zerodha dashboard.
        
        Args:
            ui: The terminal UI instance
            credential_manager: The credential manager instance
            account_group_manager: The account group manager instance
            browser_headless: Whether to run browsers in headless mode
        """
        self.ui = ui
        self.credential_manager = credential_manager
        self.account_group_manager = account_group_manager
        self.browser_headless = browser_headless
        self.running = False
    
    def _display_main_menu(self) -> str:
        """Display the main menu and get user choice."""
        self.ui.clear_screen()
        menu_items = [
            "1. Login to individual accounts",
            "2. Login to account group",
            "3. Manage account groups",
            "4. Update credentials",
            "5. Exit"
        ]
        
        self.ui.console.print(Panel.fit("\n".join(menu_items), 
                                       title="[title]Zerodha Login Dashboard[/title]",
                                       subtitle="[subtitle]Choose an option[/subtitle]"))
        
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5"])
        return choice
    
    def _handle_individual_login(self) -> None:
        """Handle login to individual accounts."""
        self.ui.clear_screen()
        
        # Get available accounts
        accounts = self.credential_manager.list_accounts()
        if not accounts:
            self.ui.print_error("No accounts found. Please add credentials first.")
            input("Press Enter to continue...")
            return
        
        # Display account selection UI
        account_table = Table(title="Available Accounts")
        account_table.add_column("#", style="dim")
        account_table.add_column("Account ID", style="cyan")
        
        for i, account in enumerate(accounts, 1):
            account_table.add_row(str(i), account)
        
        self.ui.console.print(account_table)
        
        # Get user selection
        selection = Prompt.ask("Enter account numbers to login (comma-separated) or 'all'")
        
        selected_accounts = []
        if selection.lower() == 'all':
            selected_accounts = accounts
        else:
            try:
                indices = [int(idx.strip()) - 1 for idx in selection.split(',')]
                selected_accounts = [accounts[idx] for idx in indices if 0 <= idx < len(accounts)]
            except (ValueError, IndexError):
                self.ui.print_error("Invalid selection")
                input("Press Enter to continue...")
                return
        
        if not selected_accounts:
            self.ui.print_error("No accounts selected")
            input("Press Enter to continue...")
            return
        
        # Perform login
        self._login_to_accounts(selected_accounts)
    
    def _handle_group_login(self) -> None:
        """Handle login to account groups."""
        self.ui.clear_screen()
        
        # Get available groups
        groups = self.account_group_manager.get_all_groups()
        if not groups:
            self.ui.print_error("No account groups found. Please create groups first.")
            input("Press Enter to continue...")
            return
        
        # Display group selection UI
        group_table = Table(title="Available Account Groups")
        group_table.add_column("#", style="dim")
        group_table.add_column("Group Name", style="cyan")
        group_table.add_column("Accounts", style="green")
        group_table.add_column("Description", style="yellow")
        
        for i, group in enumerate(groups, 1):
            group_table.add_row(
                str(i), 
                group.name, 
                ", ".join(group.accounts), 
                group.description
            )
        
        self.ui.console.print(group_table)
        
        # Get user selection
        selection = Prompt.ask("Enter group number to login")
        
        try:
            idx = int(selection.strip()) - 1
            if 0 <= idx < len(groups):
                selected_group = groups[idx]
                self._login_to_accounts(selected_group.accounts)
            else:
                self.ui.print_error("Invalid selection")
        except ValueError:
            self.ui.print_error("Invalid selection")
        
        input("Press Enter to continue...")
    
    def _login_to_accounts(self, accounts: List[str]) -> None:
        """Login to multiple accounts."""
        self.ui.clear_screen()
        
        total_accounts = len(accounts)
        self.ui.print_info(f"Logging in to {total_accounts} accounts...")
        
        # Create browser manager
        browser_manager = BrowserManager(self.ui, headless=self.browser_headless)
        
        # Create a progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.ui.console
        ) as progress:
            overall_task = progress.add_task(f"[cyan]Overall progress", total=total_accounts)
            
            successful = 0
            failed = 0
            
            for account in accounts:
                account_task = progress.add_task(f"[yellow]Login {account}", total=1)
                
                try:
                    # Get account credentials
                    credentials = self.credential_manager.get_credentials(account)
                    
                    if not credentials:
                        progress.update(account_task, description=f"[red]✗ {account} - No credentials found", completed=1)
                        failed += 1
                        progress.update(overall_task, advance=1)
                        continue
                    
                    # Create CSV-like credentials dict that LoginSession expects
                    login_credentials = {
                        Config.CSV_USERNAME_HEADER: credentials.get("user_id", ""),
                        Config.CSV_PASSWORD_HEADER: credentials.get("password", ""),
                        Config.CSV_2FA_HEADER: credentials.get("pin", credentials.get("totp_secret", ""))
                    }
                    
                    # Create the login session
                    session = LoginSession(
                        login_credentials, 
                        self.ui, 
                        browser_manager
                    )
                    
                    # Perform login
                    result = session.execute()
                    
                    if result:
                        progress.update(account_task, description=f"[green]✓ {account} - Success", completed=1)
                        successful += 1
                    else:
                        progress.update(account_task, description=f"[red]✗ {account} - Failed", completed=1)
                        failed += 1
                    
                except Exception as e:
                    self.ui.print_error(f"Error logging in to {account}: {str(e)}")
                    progress.update(account_task, description=f"[red]✗ {account} - Error: {str(e)[:30]}...", completed=1)
                    failed += 1
                
                progress.update(overall_task, advance=1)
        
        # Show summary
        self.ui.console.print()
        self.ui.console.print(Panel.fit(
            f"Login Summary\n\n"
            f"Total accounts: {total_accounts}\n"
            f"Successful: [green]{successful}[/]\n"
            f"Failed: [red]{failed}[/]",
            title="[title]Login Results[/title]"
        ))
        
        input("Press Enter to continue...")
    
    def _handle_manage_groups(self) -> None:
        """Handle account group management."""
        while True:
            self.ui.clear_screen()
            
            # Display available groups
            groups = self.account_group_manager.get_all_groups()
            
            if groups:
                group_table = Table(title="Account Groups")
                group_table.add_column("Name", style="cyan")
                group_table.add_column("Accounts", style="green")
                group_table.add_column("Description", style="yellow")
                
                for group in groups:
                    group_table.add_row(
                        group.name, 
                        ", ".join(group.accounts), 
                        group.description
                    )
                
                self.ui.console.print(group_table)
            else:
                self.ui.console.print("[yellow]No account groups defined yet[/]")
            
            # Display management menu
            self.ui.console.print()
            menu_items = [
                "1. Create new group",
                "2. Edit existing group",
                "3. Delete group",
                "4. Back to main menu"
            ]
            
            self.ui.console.print(Panel.fit("\n".join(menu_items), 
                                           title="[title]Group Management[/title]"))
            
            choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4"])
            
            if choice == "1":
                self._create_group()
            elif choice == "2":
                self._edit_group()
            elif choice == "3":
                self._delete_group()
            elif choice == "4":
                break
    
    def _create_group(self) -> None:
        """Create a new account group."""
        self.ui.clear_screen()
        
        # Get available accounts
        accounts = self.credential_manager.list_accounts()
        if not accounts:
            self.ui.print_error("No accounts found. Please add credentials first.")
            input("Press Enter to continue...")
            return
        
        # Display available accounts
        account_table = Table(title="Available Accounts")
        account_table.add_column("#", style="dim")
        account_table.add_column("Account ID", style="cyan")
        
        for i, account in enumerate(accounts, 1):
            account_table.add_row(str(i), account)
        
        self.ui.console.print(account_table)
        
        # Get group details
        name = Prompt.ask("Enter group name")
        if not name:
            self.ui.print_error("Group name cannot be empty")
            input("Press Enter to continue...")
            return
        
        # Check if group already exists
        if self.account_group_manager.get_group(name):
            self.ui.print_error(f"Group '{name}' already exists")
            input("Press Enter to continue...")
            return
        
        description = Prompt.ask("Enter group description (optional)", default="")
        
        # Get account selection
        selection = Prompt.ask("Enter account numbers to include (comma-separated) or 'all'")
        
        selected_accounts = []
        if selection.lower() == 'all':
            selected_accounts = accounts
        else:
            try:
                indices = [int(idx.strip()) - 1 for idx in selection.split(',')]
                selected_accounts = [accounts[idx] for idx in indices if 0 <= idx < len(accounts)]
            except (ValueError, IndexError):
                self.ui.print_error("Invalid selection")
                input("Press Enter to continue...")
                return
        
        if not selected_accounts:
            self.ui.print_error("No accounts selected")
            input("Press Enter to continue...")
            return
        
        # Create the group
        try:
            self.account_group_manager.create_group(name, selected_accounts, description)
            self.ui.print_success(f"Created group '{name}' with {len(selected_accounts)} accounts")
        except Exception as e:
            self.ui.print_error(f"Error creating group: {e}")
        
        input("Press Enter to continue...")
    
    def _edit_group(self) -> None:
        """Edit an existing account group."""
        self.ui.clear_screen()
        
        # Get available groups
        groups = self.account_group_manager.get_all_groups()
        if not groups:
            self.ui.print_error("No account groups found.")
            input("Press Enter to continue...")
            return
        
        # Display group selection UI
        group_table = Table(title="Available Account Groups")
        group_table.add_column("#", style="dim")
        group_table.add_column("Group Name", style="cyan")
        group_table.add_column("Accounts", style="green")
        group_table.add_column("Description", style="yellow")
        
        for i, group in enumerate(groups, 1):
            group_table.add_row(
                str(i), 
                group.name, 
                ", ".join(group.accounts), 
                group.description
            )
        
        self.ui.console.print(group_table)
        
        # Get user selection
        selection = Prompt.ask("Enter group number to edit")
        
        try:
            idx = int(selection.strip()) - 1
            if 0 <= idx < len(groups):
                selected_group = groups[idx]
                
                # Get available accounts
                accounts = self.credential_manager.list_accounts()
                
                # Display current accounts in the group
                account_table = Table(title=f"Accounts in '{selected_group.name}'")
                account_table.add_column("#", style="dim")
                account_table.add_column("Account ID", style="cyan")
                account_table.add_column("In Group", style="green")
                
                for i, account in enumerate(accounts, 1):
                    in_group = "✓" if account in selected_group.accounts else ""
                    account_table.add_row(str(i), account, in_group)
                
                self.ui.console.print(account_table)
                
                # Get updated details
                new_description = Prompt.ask(
                    "Enter new description (leave empty to keep current)", 
                    default=selected_group.description
                )
                
                # Get account selection
                selection = Prompt.ask(
                    "Enter account numbers to include (comma-separated), 'all', or leave empty to keep current"
                )
                
                if selection:
                    selected_accounts = []
                    if selection.lower() == 'all':
                        selected_accounts = accounts
                    else:
                        try:
                            indices = [int(idx.strip()) - 1 for idx in selection.split(',')]
                            selected_accounts = [accounts[idx] for idx in indices if 0 <= idx < len(accounts)]
                        except (ValueError, IndexError):
                            self.ui.print_error("Invalid selection")
                            input("Press Enter to continue...")
                            return
                    
                    if not selected_accounts:
                        self.ui.print_error("No accounts selected")
                        input("Press Enter to continue...")
                        return
                    
                    # Update the group
                    self.account_group_manager.update_group(
                        selected_group.name, 
                        accounts=selected_accounts, 
                        description=new_description
                    )
                else:
                    # Only update description
                    self.account_group_manager.update_group(
                        selected_group.name, 
                        description=new_description
                    )
                
                self.ui.print_success(f"Updated group '{selected_group.name}'")
            else:
                self.ui.print_error("Invalid selection")
        except ValueError:
            self.ui.print_error("Invalid selection")
        except Exception as e:
            self.ui.print_error(f"Error updating group: {e}")
        
        input("Press Enter to continue...")
    
    def _delete_group(self) -> None:
        """Delete an account group."""
        self.ui.clear_screen()
        
        # Get available groups
        groups = self.account_group_manager.get_all_groups()
        if not groups:
            self.ui.print_error("No account groups found.")
            input("Press Enter to continue...")
            return
        
        # Display group selection UI
        group_table = Table(title="Available Account Groups")
        group_table.add_column("#", style="dim")
        group_table.add_column("Group Name", style="cyan")
        group_table.add_column("Accounts", style="green")
        group_table.add_column("Description", style="yellow")
        
        for i, group in enumerate(groups, 1):
            group_table.add_row(
                str(i), 
                group.name, 
                ", ".join(group.accounts), 
                group.description
            )
        
        self.ui.console.print(group_table)
        
        # Get user selection
        selection = Prompt.ask("Enter group number to delete")
        
        try:
            idx = int(selection.strip()) - 1
            if 0 <= idx < len(groups):
                selected_group = groups[idx]
                
                # Confirm deletion
                confirm = Confirm.ask(f"Are you sure you want to delete group '{selected_group.name}'?")
                if confirm:
                    self.account_group_manager.delete_group(selected_group.name)
                    self.ui.print_success(f"Deleted group '{selected_group.name}'")
            else:
                self.ui.print_error("Invalid selection")
        except ValueError:
            self.ui.print_error("Invalid selection")
        except Exception as e:
            self.ui.print_error(f"Error deleting group: {e}")
        
        input("Press Enter to continue...")
    
    def _handle_update_credentials(self) -> None:
        """Handle credential updates."""
        self.ui.clear_screen()
        
        # Get available accounts
        accounts = self.credential_manager.list_accounts()
        if not accounts:
            self.ui.print_error("No accounts found.")
            input("Press Enter to continue...")
            return
        
        # Display account selection UI
        account_table = Table(title="Available Accounts")
        account_table.add_column("#", style="dim")
        account_table.add_column("Account ID", style="cyan")
        
        for i, account in enumerate(accounts, 1):
            account_table.add_row(str(i), account)
        
        self.ui.console.print(account_table)
        
        # Options menu
        self.ui.console.print()
        menu_items = [
            "1. Update existing account",
            "2. Add new account",
            "3. Delete account",
            "4. Back to main menu"
        ]
        
        self.ui.console.print(Panel.fit("\n".join(menu_items), 
                                       title="[title]Credential Management[/title]"))
        
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4"])
        
        if choice == "1":
            self._update_account(accounts)
        elif choice == "2":
            self._add_account()
        elif choice == "3":
            self._delete_account(accounts)
        elif choice == "4":
            return
        
        input("Press Enter to continue...")
    
    def _update_account(self, accounts: List[str]) -> None:
        """Update an existing account's credentials."""
        selection = Prompt.ask("Enter account number to update")
        
        try:
            idx = int(selection.strip()) - 1
            if 0 <= idx < len(accounts):
                account_id = accounts[idx]
                
                # Get current credentials
                try:
                    current_creds = self.credential_manager.get_credentials(account_id)
                    
                    # Get new credentials
                    self.ui.console.print(f"[cyan]Updating credentials for {account_id}[/]")
                    self.ui.console.print("[yellow]Leave fields empty to keep current values[/]")
                    
                    new_user_id = Prompt.ask("User ID", default=current_creds.get("user_id", ""))
                    new_password = Prompt.ask("Password", password=True, default="")
                    new_pin = Prompt.ask("PIN", password=True, default="")
                    new_totp_secret = Prompt.ask("TOTP Secret (leave empty if not changed)", default=current_creds.get("totp_secret", ""))
                    new_status = Prompt.ask("Status (1=active, 0=inactive)", default=current_creds.get("status", "1"))
                    
                    # Update credentials
                    updated_creds = {
                        "user_id": new_user_id,
                        "password": new_password if new_password else current_creds.get("password", ""),
                        "pin": new_pin if new_pin else current_creds.get("pin", ""),
                        "totp_secret": new_totp_secret if new_totp_secret else current_creds.get("totp_secret", ""),
                        "status": new_status
                    }
                    
                    self.credential_manager.save_credentials(account_id, updated_creds)
                    self.ui.print_success(f"Updated credentials for {account_id}")
                
                except Exception as e:
                    self.ui.print_error(f"Error updating credentials: {e}")
            else:
                self.ui.print_error("Invalid selection")
        except ValueError:
            self.ui.print_error("Invalid selection")
    
    def _add_account(self) -> None:
        """Add a new account."""
        self.ui.console.print("[cyan]Adding new account[/]")
        
        account_id = Prompt.ask("Account ID (unique identifier)")
        if not account_id:
            self.ui.print_error("Account ID cannot be empty")
            return
        
        # Check if account already exists
        if account_id in self.credential_manager.list_accounts():
            self.ui.print_error(f"Account '{account_id}' already exists")
            return
        
        user_id = Prompt.ask("User ID")
        password = Prompt.ask("Password", password=True)
        pin = Prompt.ask("PIN", password=True)
        totp_secret = Prompt.ask("TOTP Secret (optional)", default="")
        status = Prompt.ask("Status (1=active, 0=inactive)", default="1")
        
        # Save credentials
        creds = {
            "user_id": user_id,
            "password": password,
            "pin": pin,
            "totp_secret": totp_secret,
            "status": status
        }
        
        try:
            self.credential_manager.save_credentials(account_id, creds)
            self.ui.print_success(f"Added new account '{account_id}'")
        except Exception as e:
            self.ui.print_error(f"Error adding account: {e}")
    
    def _delete_account(self, accounts: List[str]) -> None:
        """Delete an account."""
        selection = Prompt.ask("Enter account number to delete")
        
        try:
            idx = int(selection.strip()) - 1
            if 0 <= idx < len(accounts):
                account_id = accounts[idx]
                
                # Confirm deletion
                confirm = Confirm.ask(f"Are you sure you want to delete account '{account_id}'?")
                if confirm:
                    # Check if account is used in any groups
                    used_in_groups = []
                    for group in self.account_group_manager.get_all_groups():
                        if account_id in group.accounts:
                            used_in_groups.append(group.name)
                    
                    if used_in_groups:
                        self.ui.print_warning(f"Account '{account_id}' is used in groups: {', '.join(used_in_groups)}")
                        confirm_again = Confirm.ask("Delete anyway? (This will remove it from all groups)")
                        if not confirm_again:
                            return
                        
                        # Remove account from all groups
                        for group_name in used_in_groups:
                            group = self.account_group_manager.get_group(group_name)
                            if group:
                                updated_accounts = [acc for acc in group.accounts if acc != account_id]
                                self.account_group_manager.update_group(group_name, accounts=updated_accounts)
                    
                    # Delete account
                    self.credential_manager.delete_credentials(account_id)
                    self.ui.print_success(f"Deleted account '{account_id}'")
            else:
                self.ui.print_error("Invalid selection")
        except ValueError:
            self.ui.print_error("Invalid selection")
        except Exception as e:
            self.ui.print_error(f"Error deleting account: {e}")
    
    def run(self) -> None:
        """Run the dashboard."""
        self.running = True
        
        while self.running:
            choice = self._display_main_menu()
            
            if choice == "1":
                self._handle_individual_login()
            elif choice == "2":
                self._handle_group_login()
            elif choice == "3":
                self._handle_manage_groups()
            elif choice == "4":
                self._handle_update_credentials()
            elif choice == "5":
                self.running = False
                self.ui.print_info("Exiting dashboard...")
                break

# ==========================================================================
# --- Command Line Interface ---
# ==========================================================================

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Zerodha Login Bot - Automate login for multiple Zerodha accounts"
    )

    # Create argument groups for better help text organization
    input_group = parser.add_argument_group('Input/Output')
    display_group = parser.add_argument_group('Display')
    exec_group = parser.add_argument_group('Execution')
    mode_group = parser.add_argument_group('Running Modes')
    account_group = parser.add_argument_group('Account Selection')

    # Running Modes
    mode_group.add_argument('--interactive', '-i', action='store_true',
                        help='Run in interactive mode (select accounts from a list)')
    mode_group.add_argument('--dashboard', action='store_true',
                        help='Start with interactive dashboard for account management and login')

    # Input/Output arguments
    input_group.add_argument('--credentials', '-c', type=str, default='credentials.csv',
                         help='Path to the credentials CSV file')
    input_group.add_argument('--output', '-o', type=str,
                         help='Save console output to the specified file')

    # Display arguments
    display_group.add_argument('--verbose', '-v', action='store_true',
                          help='Enable verbose output')
    display_group.add_argument('--quiet', '-q', action='store_true',
                          help='Disable all console output')
    display_group.add_argument('--no-color', action='store_true',
                          help='Disable colored output')

    # Execution arguments
    exec_group.add_argument('--headless', action='store_true',
                        help='Run the browser in headless mode')
    exec_group.add_argument('--no-close', action='store_true',
                        help='Keep browser windows open after login')
    exec_group.add_argument('--threads', '-t', type=int, default=5,
                        help='Number of concurrent login threads (default: 5)')
    exec_group.add_argument('--retry', '-r', type=int, default=2,
                        help='Number of retry attempts for failed logins (default: 2)')
    exec_group.add_argument('--delay', '-d', type=float, default=1.0,
                        help='Delay between actions in seconds (default: 1.0)')
    exec_group.add_argument('--timeout', type=float, default=30.0,
                        help='Timeout for web elements in seconds (default: 30.0)')

    # Account selection arguments
    account_group.add_argument('--accounts', '-a', type=str,
                          help='Comma-separated list of account usernames to login')
    account_group.add_argument('--exclude', '-e', type=str,
                          help='Comma-separated list of account usernames to exclude')
    account_group.add_argument('--all', action='store_true',
                          help='Login to all accounts in the credentials file')
    account_group.add_argument('--group', '-g', type=str,
                          help='Login to accounts in the specified group')

    return parser.parse_args()

# ==========================================================================
# --- Entry Point ---
# ==========================================================================

def main():
    """Main entry point for the Zerodha auto-login script."""
    parser = argparse.ArgumentParser(description='Automate Zerodha login process.')
    
    # Basic arguments
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive account selection')
    parser.add_argument('--accounts', type=str, help='Comma-separated list of accounts to log in')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-y', '--yes', action='store_true', help='Skip confirmation prompt')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--credentials', type=str, help='Path to credentials file')
    parser.add_argument('--log-dir', type=str, help='Directory to store log files')
    parser.add_argument('--no-log-file', action='store_true', help='Disable logging to file')
    
    # Dashboard mode
    parser.add_argument('--dashboard', action='store_true', help='Launch interactive dashboard')
    
    args = parser.parse_args()
    
    # Check if no specific arguments were provided (like when double-clicking)
    # If so, automatically login to all accounts with yes flag
    if len(sys.argv) == 1:  # Only the script name, no arguments
        args.yes = True  # Skip confirmation
    
    # Initialize UI
    ui = TerminalUI(verbose=args.verbose, log_to_file=not args.no_log_file)
    
    try:
        # Initialize credential manager
        credential_manager = CredentialManager(ui)
        
        # Set credentials path if specified
        if args.credentials:
            credential_manager.set_credentials_file(args.credentials)
        
        # Set log directory if specified
        if args.log_dir:
            Config.LOGS_DIR = args.log_dir
        
        if args.dashboard:
            # Initialize account group manager and dashboard
            account_group_manager = AccountGroupManager(ui, credential_manager)
            dashboard = ZerodhaDashboard(ui, credential_manager, account_group_manager, args.headless)
            dashboard.run()
        else:
            # Regular login bot mode
            login_bot = ZerodhaLoginBot(args)
            # Pass the credential manager to the login bot
            if args.credentials:
                login_bot.credential_manager.set_credentials_file(args.credentials)
            login_bot.run()
        
        # Keep terminal open when double-clicked and offer to close Chrome
        if len(sys.argv) == 1:
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
                ui.print_info("Closing all Chrome windows...")
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
                ui.print_success("All Chrome windows closed")
            except KeyboardInterrupt:
                ui.console.print("[bold cyan]Keeping Chrome windows open[/bold cyan]")
            except EOFError:
                pass
        
    except KeyboardInterrupt:
        ui.print_warning("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        ui.print_error(f"An error occurred: {str(e)}")
        if args.verbose:
            import traceback
            ui.console.print_exception()
        
        # Keep terminal open when double-clicked and there's an error
        if len(sys.argv) == 1:
            try:
                input("\nPress Enter to exit...")
            except (EOFError, KeyboardInterrupt):
                pass
        
        sys.exit(1)

if __name__ == '__main__':
    main()