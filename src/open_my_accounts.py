#!/usr/bin/env python3
"""
Zerodha My Accounts Login Script

A specialized script for logging into HDN374 and BU0542 accounts.
"""

# Standard Library Imports
import csv
import time
import sys
import os
import platform
import traceback
import subprocess
import threading
from typing import Dict, Optional, List

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
    """Configuration settings for the my accounts login."""
    
    # File Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONFIG_DIR = os.path.join(BASE_DIR, 'config')
    CREDENTIALS_FILE = os.path.join(CONFIG_DIR, 'zerodha_credentials.csv')
    
    # Target Accounts (HDN374 and BU0542)
    TARGET_ACCOUNTS = ["HDN374", "BU0542"]
    
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

class MyAccountsUI:
    """Simple UI for the my accounts login."""
    
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
    ║    ║   🔐 My Accounts Login Portal                         ║ ║
    ║    ║   ⭐ HDN374 & BU0542 Account Access                   ║ ║
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
            f"[bold bright_magenta]🔐 My Accounts: HDN374 & BU0542[/bold bright_magenta]\n\n"
            f"[dim]Version:[/dim] [bold white]{version}[/bold white]  [dim]|[/dim]  "
            f"[dim]Started:[/dim] [bold white]{current_time}[/bold white]",
            style="cyan",
            border_style="bright_cyan",
            padding=(0, 2)
        ))
        self.console.print()
        self.console.print("[bold cyan]" + "═" * 72 + "[/bold cyan]")
        self.console.print()
    
    def log(self, message: str, level: str = "info"):
        """Log a message with timestamp and level."""
        elapsed = time.time() - self.start_time
        elapsed_str = f"{elapsed:6.1f}s"
        
        level_styles = {
            "info": "[bold cyan]🔵[/]",
            "success": "[bold green]✅[/]",
            "warning": "[bold yellow]⚠️[/]",
            "error": "[bold red]❌[/]",
            "highlight": "[bold magenta]✨[/]",
        }
        icon = level_styles.get(level, "[bold white]ℹ️[/]")
        
        time_str = time.strftime("%H:%M:%S", time.localtime())
        log_msg = f"{time_str} (+{elapsed_str}) {icon} {message}"
        self.console.print(log_msg)

# ==========================================================================
# --- Helper Functions ---
# ==========================================================================

def close_all_chrome_windows():
    """Close all Google Chrome windows - very aggressive version to ensure all processes are killed."""
    try:
        # Get all Chrome-related PIDs first
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
        
        # Try multiple kill methods
        commands = [
            # Kill by name patterns with SIGKILL (-9)
            ['pkill', '-9', 'google-chrome'],
            ['pkill', '-9', '-f', 'google-chrome'],
            ['pkill', '-9', '-f', 'chromedriver'],
            ['pkill', '-9', '-f', 'chrome'],
            ['killall', '-9', 'google-chrome'],
            ['killall', '-9', 'chromedriver'],
            ['killall', '-9', 'chrome'],
            # Try SIGTERM (-15) first, then SIGKILL
            ['pkill', '-15', 'google-chrome'],
            ['killall', '-15', 'google-chrome'],
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, check=False, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, timeout=2)
                time.sleep(0.1)
            except:
                pass
        
        # Wait a bit for processes to terminate
        time.sleep(0.8)
        
        # Force kill any PIDs we found earlier
        for pid in chrome_pids:
            try:
                subprocess.run(['kill', '-9', pid], check=False, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, timeout=1)
            except:
                pass
        
        # Final verification and cleanup - check for any remaining Chrome processes
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
        
        # Final wait
        time.sleep(0.3)
    except Exception:
        pass

def get_account_credentials(account_id: str, ui: MyAccountsUI) -> Optional[Dict[str, str]]:
    """Get credentials for a specific account."""
    ui.log(f"Reading credentials for {account_id}")
    
    try:
        credentials_file = Config.CREDENTIALS_FILE
        with open(credentials_file, mode='r', newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                username = row.get(Config.CSV_USERNAME_HEADER, "").strip()
                if username == account_id:
                    password = row.get(Config.CSV_PASSWORD_HEADER, "").strip()
                    pin_or_totp = row.get(Config.CSV_2FA_HEADER, "").strip()
                    status = row.get(Config.CSV_STATUS_HEADER, "").strip()
                    
                    if not password:
                        ui.log(f"No password found for {account_id}", "error")
                        return None
                    
                    ui.log(f"Found credentials for {account_id}", "success")
                    return {
                        "user_id": username,
                        "password": password,
                        "pin": pin_or_totp,
                        "totp_secret": pin_or_totp,
                        "status": status
                    }
            
            ui.log(f"Account {account_id} not found in credentials file", "error")
            return None
            
    except FileNotFoundError:
        ui.log(f"Credentials file not found: '{Config.CREDENTIALS_FILE}'", "error")
        return None
    except Exception as e:
        ui.log(f"Failed to read credentials: {e}", "error")
        return None

def login_to_account(account_id: str, credentials: Dict[str, str], ui: MyAccountsUI) -> bool:
    """Login to a specific account."""
    ui.log(f"Starting login process for {account_id}")
    
    driver = None
    login_successful = False
    
    try:
        # Setup browser
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
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Use webdriver-manager if available
        if WEBDRIVER_MANAGER_AVAILABLE:
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            except Exception:
                driver = webdriver.Chrome(options=options)
        else:
            driver = webdriver.Chrome(options=options)
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        ui.log("Chrome launched successfully", "success")
        
        # Navigate to login
        ui.log("Navigating to login page")
        wait = WebDriverWait(driver, Config.WEBDRIVER_WAIT_TIMEOUT)
        driver.get(Config.ZERODHA_LOGIN_URL)
        time.sleep(Config.SHORT_DELAY)
        
        # Enter credentials
        ui.log("Entering credentials")
        username_input = wait.until(EC.presence_of_element_located(Config.USER_ID_INPUT_LOCATOR))
        username_input.send_keys(credentials["user_id"])
        time.sleep(Config.INTER_KEY_DELAY)
        
        password_input = wait.until(EC.presence_of_element_located(Config.PASSWORD_INPUT_LOCATOR))
        password_input.send_keys(credentials["password"])
        time.sleep(Config.INTER_KEY_DELAY)
        
        # Submit login
        ui.log("Submitting login form")
        login_button = wait.until(EC.element_to_be_clickable(Config.LOGIN_SUBMIT_BUTTON_LOCATOR))
        login_button.click()
        time.sleep(Config.POST_LOGIN_CLICK_DELAY)
        
        # Handle 2FA
        pin_or_totp = credentials.get("pin", "")
        if pin_or_totp:
            ui.log("Handling 2FA authentication")
            try:
                pin_input = wait.until(EC.element_to_be_clickable(Config.PIN_INPUT_LOCATOR))
                
                if len(pin_or_totp) > 8 and pin_or_totp.isalnum() and not pin_or_totp.isdigit():
                    # TOTP
                    totp = pyotp.TOTP(pin_or_totp)
                    current_otp = totp.now()
                    ui.log(f"Generated TOTP: {current_otp}")
                    pin_input.send_keys(current_otp)
                else:
                    # Static PIN
                    pin_input.send_keys(pin_or_totp)
                
                time.sleep(Config.POST_2FA_KEY_DELAY)
                pin_submit_button = wait.until(EC.element_to_be_clickable(Config.PIN_SUBMIT_BUTTON_LOCATOR))
                pin_submit_button.click()
                time.sleep(Config.POST_FINAL_SUBMIT_DELAY)
                ui.log("2FA submitted successfully", "success")
                login_successful = True
            except Exception as e:
                ui.log(f"2FA handling error: {e}", "error")
                login_successful = False
        else:
            login_successful = True
        
        if login_successful:
            ui.log(f"Login completed successfully for {account_id}", "success")
        else:
            ui.log(f"Login failed for {account_id}", "error")
        
        # Don't close the browser - keep it open
        return login_successful
        
    except Exception as e:
        ui.log(f"Error during login: {e}", "error")
        if driver:
            try:
                driver.save_screenshot(f"{account_id}_error.png")
            except:
                pass
        return False

# ==========================================================================
# --- Main Application ---
# ==========================================================================

def main():
    """Main entry point for the my accounts login script."""
    
    # Check if running from double-click (no command line arguments)
    is_double_clicked = len(sys.argv) == 1
    
    # Clear screen for better presentation when double-clicked
    if is_double_clicked:
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
        except:
            pass
    
    # Initialize UI
    ui = MyAccountsUI()
    
    try:
        # Display banner
        ui.print_banner()
        
        # Special welcome message for double-clicked execution
        if is_double_clicked:
            ui.log("🎯 Welcome! This script will login to HDN374 and BU0542 accounts.", "highlight")
            ui.log("📋 Please ensure you have the correct credentials in the CSV file.", "info")
            ui.log("")
        
        # Get credentials for all accounts first
        all_credentials = {}
        for account_id in Config.TARGET_ACCOUNTS:
            credentials = get_account_credentials(account_id, ui)
            if not credentials:
                ui.log(f"Failed to get credentials for {account_id}. Skipping.", "error")
            else:
                all_credentials[account_id] = credentials
        
        if not all_credentials:
            ui.log("No valid credentials found. Exiting.", "error")
            if is_double_clicked:
                try:
                    input("\nPress Enter to exit...")
                except (EOFError, KeyboardInterrupt):
                    pass
            sys.exit(1)
        
        # Display account information
        ui.console.print()
        ui.console.print(Panel.fit(
            f"[bold bright_cyan]📋 Account Information[/bold bright_cyan]\n\n" +
            "\n".join([
                f"[dim]• {acc_id}:[/dim] [bold white]{creds['user_id']}[/bold white] "
                f"({'TOTP' if len(creds.get('pin', '')) > 8 else 'PIN' if creds.get('pin') else 'None'})"
                for acc_id, creds in all_credentials.items()
            ]),
            border_style="bright_cyan",
            padding=(1, 2)
        ))
        ui.console.print()
        
        # Process accounts in parallel using threads (like auto_login.py)
        ui.console.print(Panel.fit(
            f"[bold bright_cyan]🚀 Starting Login Sessions[/bold bright_cyan]\n"
            f"[dim]Processing {len(all_credentials)} account(s) in parallel mode[/dim]",
            border_style="bright_cyan",
            padding=(0, 2)
        ))
        ui.console.print()
        ui.log(f"Launching all login sessions simultaneously", "highlight")
        
        # Create shared results dictionary and lock
        results = {}
        results_lock = threading.Lock()
        login_status = {}
        status_lock = threading.Lock()
        
        # Initialize status for each account
        for account_id in all_credentials.keys():
            login_status[account_id] = {"status": "pending", "completed": False}
        
        def process_account_thread(account_id: str, credentials: Dict[str, str]):
            """Process a single account login in a separate thread (like auto_login.py)."""
            try:
                ui.log(f"Starting login process for {account_id}", "info")
                
                # Update status to running
                with status_lock:
                    login_status[account_id]["status"] = "running"
                
                # Login to account
                success = login_to_account(account_id, credentials, ui)
                
                # Update results and status
                with results_lock:
                    results[account_id] = success
                with status_lock:
                    login_status[account_id]["completed"] = True
                    login_status[account_id]["status"] = "success" if success else "failed"
                
                return success
            except Exception as e:
                ui.log(f"Error processing {account_id}: {e}", "error")
                with results_lock:
                    results[account_id] = False
                with status_lock:
                    login_status[account_id]["completed"] = True
                    login_status[account_id]["status"] = "failed"
                return False
        
        # Create all threads but don't start them yet (like auto_login.py)
        threads = []
        for account_id, credentials in all_credentials.items():
            thread = threading.Thread(
                target=process_account_thread,
                args=(account_id, credentials),
                name=f"Login-{account_id}"
            )
            threads.append(thread)
        
        # Start all threads at once for simultaneous processing (like auto_login.py)
        ui.console.print(f"[bold bright_cyan]🌐 Opening [bold white]{len(threads)}[/bold white] browser windows simultaneously...[/bold bright_cyan]")
        ui.console.print()
        ui.log(f"Opening {len(threads)} browser windows simultaneously...", "highlight")
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete (like auto_login.py)
        for thread in threads:
            thread.join()
        
        # Final summary
        ui.console.print()
        ui.console.print(Panel.fit(
            "[bold bright_green]✅ Login Process Completed![/bold bright_green]\n\n" +
            "\n".join([f"  [{'green' if results[acc] else 'red'}]●[/] {acc}: {'Success' if results[acc] else 'Failed'}" for acc in Config.TARGET_ACCOUNTS]) +
            "\n\n[dim]Browser windows will remain open for your use[/dim]",
            border_style="bright_green",
            padding=(1, 2)
        ))
        ui.console.print()
        
        # Keep terminal open when double-clicked and offer to close Chrome
        if is_double_clicked or sys.stdin.isatty():
            ui.console.print(Panel.fit(
                "[bold yellow]⚠️  Close All Chrome Windows?[/bold yellow]\n\n"
                "[dim]Press [bold white]Enter[/bold white] to close all Chrome windows and exit[/dim]\n"
                "[dim]Press [bold white]Ctrl+C[/bold white] to keep Chrome windows open and exit[/dim]",
                border_style="yellow",
                padding=(1, 2)
            ))
            ui.console.print()
            try:
                input("Press Enter to close all Chrome windows...")
                ui.log("Closing all Chrome windows...", "info")
                close_all_chrome_windows()
                ui.log("All Chrome windows closed", "success")
            except KeyboardInterrupt:
                ui.log("Keeping Chrome windows open", "info")
            except EOFError:
                pass
        
    except KeyboardInterrupt:
        ui.log("\nOperation cancelled by user", "warning")
        if is_double_clicked or sys.stdin.isatty():
            try:
                input("\nPress Enter to exit...")
            except (EOFError, KeyboardInterrupt):
                pass
        sys.exit(1)
    except Exception as e:
        ui.log(f"An error occurred: {str(e)}", "error")
        import traceback
        ui.console.print_exception()
        
        # Keep terminal open when double-clicked and there's an error
        if is_double_clicked or sys.stdin.isatty():
            try:
                input("\nPress Enter to exit...")
            except (EOFError, KeyboardInterrupt):
                pass
        
        sys.exit(1)

if __name__ == '__main__':
    main()
