# 🐧 Linux Setup and Execution Guide

Complete guide for running Zerodha automation scripts on Linux.

---

## 📋 Prerequisites

### 1. Install Python 3.8+

```bash
# Check if Python 3 is installed
python3 --version

# If not installed, install it (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-pip

# Or on Fedora/RHEL
sudo dnf install python3 python3-pip
```

### 2. Install Google Chrome or Chromium

**Option A: Google Chrome**

```bash
# Ubuntu/Debian
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f  # Fix dependencies if needed

# Fedora/RHEL
sudo dnf install google-chrome-stable
```

**Option B: Chromium (Open Source Alternative)**

```bash
# Ubuntu/Debian
sudo apt install chromium-browser

# Fedora/RHEL
sudo dnf install chromium
```

### 3. Install ChromeDriver

**Method 1: Download and Install (Recommended)**

```bash
# 1. Check Chrome version
google-chrome --version
# OR if using Chromium:
chromium --version

# 2. Download matching ChromeDriver
# Visit: https://chromedriver.chromium.org/downloads
# Download chromedriver_linux64.zip for your Chrome version

# 3. Extract and install
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# 4. Verify installation
chromedriver --version
```

**Method 2: Package Manager (Alternative)**

```bash
# Ubuntu/Debian
sudo apt install chromium-chromedriver

# Fedora/RHEL
sudo dnf install chromium-driver
```

### 4. Install Python Dependencies

```bash
# Navigate to project directory
cd /path/to/zerodha_automation

# Install dependencies
pip3 install -r requirements.txt

# Or use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 Running the Scripts

### Script 1: Multi-Account Login (`src/auto_login.py`)

**Basic Usage:**

```bash
# Run with all active accounts
python3 src/auto_login.py

# Run with specific accounts
python3 src/auto_login.py --accounts ACCOUNT1,ACCOUNT2

# Run in interactive mode (select accounts)
python3 src/auto_login.py --interactive

# Run with verbose output
python3 src/auto_login.py -v

# Run dashboard mode
python3 src/auto_login.py --dashboard
```

**Make Executable (Optional):**

```bash
chmod +x src/auto_login.py
./src/auto_login.py
```

---

### Script 2: Company Account Login (`open_Company_Account.py`)

**Basic Usage:**

```bash
# Run the script
python3 open_Company_Account.py
```

**Make Executable (Optional):**

```bash
chmod +x open_Company_Account.py
./open_Company_Account.py
```

**Note:** This script logs into the configured company account and loads Chrome extensions.

---

### Script 3: AlgoTest Login (`CronJob Algotest Login/algotest_login.py`)

**Basic Usage:**

```bash
# Run with default configuration
python3 "CronJob Algotest Login/algotest_login.py"
```

**Make Executable (Optional):**

```bash
chmod +x "CronJob Algotest Login/algotest_login.py"
./"CronJob Algotest Login/algotest_login.py"
```

**Configuration:**

Edit the script to enable/disable accounts:

```python
ACCOUNTS_CONFIG = {
    "YOUR_ACCOUNT_1": 1,  # Set to 1 to enable, 0 to disable
    "YOUR_ACCOUNT_2": 1,  # Set to 1 to enable, 0 to disable
}
```

---

## 📁 File Structure Setup

### 1. Create Configuration Directory

```bash
mkdir -p config
```

### 2. Create Credentials File

Create `config/zerodha_credentials.csv`:

```bash
nano config/zerodha_credentials.csv
```

**Format:**

```csv
Username,Password,PIN/TOTP Secret,Status
YOUR_USERNAME,your_password,YOUR_TOTP_OR_PIN,1
ANOTHER_USERNAME,another_password,ANOTHER_TOTP_OR_PIN,1
```

### 3. Create AlgoTest Credentials (if using AlgoTest script)

Create `CronJob Algotest Login/algotest_credentials.json`:

```bash
nano "CronJob Algotest Login/algotest_credentials.json"
```

**Format:**

```json
{
  "algotest": {
    "username": "your_phone_number",
    "password": "your_password"
  }
}
```

### 4. Set Proper Permissions (Security)

```bash
# Restrict access to credential files
chmod 600 config/zerodha_credentials.csv
chmod 600 "CronJob Algotest Login/algotest_credentials.json"
```

---

## 🔧 Common Linux Issues and Solutions

### Issue 1: ChromeDriver Not Found

```bash
# Check if ChromeDriver is in PATH
which chromedriver

# If not found, verify installation
chromedriver --version

# Add to PATH if needed (add to ~/.bashrc or ~/.zshrc)
export PATH="$PATH:/usr/local/bin"
```

### Issue 2: Permission Denied

```bash
# Make scripts executable
chmod +x src/auto_login.py
chmod +x open_Company_Account.py
chmod +x "CronJob Algotest Login/algotest_login.py"

# Make ChromeDriver executable
sudo chmod +x /usr/local/bin/chromedriver
```

### Issue 3: Chrome/Chromium Not Found

```bash
# Check if Chrome is installed
google-chrome --version
# OR
chromium --version

# Verify Chrome profile directory exists
ls -la ~/.config/google-chrome
# OR
ls -la ~/.config/chromium
```

### Issue 4: Python Module Not Found

```bash
# Install dependencies
pip3 install -r requirements.txt

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue 5: Display/Headless Issues

If running on a headless server (no display):

```bash
# Install Xvfb (virtual display)
sudo apt install xvfb

# Run with virtual display
xvfb-run -a python3 src/auto_login.py --headless
```

### Issue 6: Shared Memory Issues

If you encounter shared memory errors:

The scripts already include `--disable-dev-shm-usage` flag, but if issues persist:

```bash
# Increase shared memory size (temporary)
sudo mount -o remount,size=2G /dev/shm
```

---

## 🎯 Quick Start Commands

**Complete setup (one-time):**

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Setup ChromeDriver (see Prerequisites section)

# 3. Create credentials file
nano config/zerodha_credentials.csv

# 4. Run script
python3 src/auto_login.py
```

**Daily usage:**

```bash
# Option 1: Multi-account login
python3 src/auto_login.py

# Option 2: Company account only
python3 open_Company_Account.py

# Option 3: AlgoTest workflow
python3 "CronJob Algotest Login/algotest_login.py"
```

---

## 🔒 Security Best Practices for Linux

1. **File Permissions:**

   ```bash
   chmod 600 config/zerodha_credentials.csv
   chmod 600 "CronJob Algotest Login/algotest_credentials.json"
   ```

2. **Use Virtual Environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Keep Scripts Private:**

   - Don't share credentials files
   - Keep repository private if possible
   - Use secure file transfer methods (SFTP, SCP)

4. **Regular Updates:**

   ```bash
   # Update Chrome/Chromium
   sudo apt update && sudo apt upgrade google-chrome-stable
   # OR
   sudo dnf update chromium

   # Update ChromeDriver to match Chrome version
   # (Download new version from chromedriver.chromium.org)
   ```

---

## 📝 Notes

- All scripts work with both Google Chrome and Chromium on Linux
- Scripts automatically detect Chrome profile location
- File paths are cross-platform (works on Windows, macOS, and Linux)
- Logs are saved in `logs/` directory
- Screenshots (on errors) are saved in project root

---

## 🆘 Getting Help

If you encounter issues:

1. Check the main [README.md](README.md) for detailed documentation
2. Review [DRIVERS/README_DRIVERS.md](DRIVERS/README_DRIVERS.md) for ChromeDriver setup
3. Run scripts with `-v` flag for verbose output:
   ```bash
   python3 src/auto_login.py -v
   ```
4. Check log files in `logs/` directory for error details
