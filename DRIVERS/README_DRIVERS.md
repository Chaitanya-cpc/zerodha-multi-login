# 🚗 ChromeDriver Setup Guide

<div align="center">

**Complete Guide for Setting Up ChromeDriver**

*Required for Selenium WebDriver Automation*

[![ChromeDriver](https://img.shields.io/badge/ChromeDriver-Latest-blue.svg)](https://chromedriver.chromium.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.0+-green.svg)](https://selenium-python.readthedocs.io/)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Why ChromeDriver is Not Included](#-why-chromedriver-is-not-included)
- [Installation Methods](#-installation-methods)
- [Platform-Specific Instructions](#-platform-specific-instructions)
- [Verification](#-verification)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

This project requires the Selenium WebDriver for Chrome (ChromeDriver) to interact with the Google Chrome browser. ChromeDriver acts as a bridge between Selenium and the Chrome browser, enabling automated browser control.

### Key Points

- ✅ **Version Matching Required** - ChromeDriver must match your Chrome browser version
- ✅ **Platform Specific** - Different binaries for Windows, macOS, and Linux
- ✅ **Auto-Detection** - Scripts will auto-detect ChromeDriver if in PATH
- ✅ **Manual Setup Available** - Can specify path directly if needed

---

## ❓ Why ChromeDriver is Not Included

**ChromeDriver is NOT included in this repository due to:**

1. **Versioning Compatibility**
   - ChromeDriver is tied to specific Chrome browser versions
   - You need the version that matches *your* installed Chrome
   - Including a specific version would break for users with different Chrome versions

2. **Licensing Considerations**
   - Redistributing ChromeDriver may have licensing implications
   - Better to download directly from official sources

3. **Platform Specificity**
   - Different operating systems require different ChromeDriver binaries:
     - `chromedriver_mac64.zip` for macOS
     - `chromedriver_win32.zip` for Windows
     - `chromedriver_linux64.zip` for Linux
   - Including all platforms would bloat the repository

4. **Size and Maintenance**
   - ChromeDriver binaries are large
   - Regular updates would require frequent commits
   - Better to manage separately

---

## 📦 Installation Methods

### Method 1: System PATH (Recommended) ⭐

This is the **recommended approach** as it allows the scripts to automatically find ChromeDriver.

#### Steps:

1. **Check Your Chrome Version**
   - Open Google Chrome
   - Go to `Help` → `About Google Chrome`
   - Note the version number (e.g., `120.0.6099.109`)

2. **Download ChromeDriver**
   - Visit: [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)
   - Find the version matching your Chrome browser
   - Download the appropriate zip file for your OS:
     - **macOS**: `chromedriver_mac64.zip`
     - **Windows**: `chromedriver_win32.zip` or `chromedriver_win64.zip`
     - **Linux**: `chromedriver_linux64.zip`

3. **Extract the Executable**
   - Unzip the downloaded file
   - You'll find:
     - `chromedriver` (macOS/Linux)
     - `chromedriver.exe` (Windows)

4. **Add to System PATH**

   **macOS/Linux:**
   ```bash
   # Option A: Move to existing PATH directory
   sudo mv chromedriver /usr/local/bin/
   
   # Option B: Add directory to PATH
   # Add this line to ~/.bashrc or ~/.zshrc:
   export PATH="$PATH:/path/to/chromedriver/directory"
   ```

   **Windows:**
   - Right-click "This PC" → Properties → Advanced System Settings
   - Click "Environment Variables"
   - Under "System Variables", find "Path" and click "Edit"
   - Click "New" and add the directory containing `chromedriver.exe`
   - Click "OK" on all dialogs

5. **Verify Installation**
   ```bash
   chromedriver --version
   ```
   Should display: `ChromeDriver 120.0.6099.109` (or your version)

### Method 2: Specify Path in Script (Alternative)

If you prefer not to modify your PATH, you can specify the ChromeDriver path directly in the script.

⚠️ **Note:** This method is less recommended as script updates may overwrite your changes.

#### Steps:

1. **Download ChromeDriver** (same as Method 1, steps 1-3)

2. **Note the Full Path**
   - **macOS/Linux**: `/Users/yourname/Downloads/chromedriver`
   - **Windows**: `C:\Users\yourname\Downloads\chromedriver.exe`

3. **Modify the Script**
   
   In `src/auto_login.py`, find the browser setup section:
   
   ```python
   # Find this section:
   service = Service()
   driver = webdriver.Chrome(service=service, options=options)
   ```
   
   Modify to:
   ```python
   # macOS/Linux example:
   service = Service('/Users/yourname/Downloads/chromedriver')
   
   # Windows example:
   # service = Service('C:\\Users\\yourname\\Downloads\\chromedriver.exe')
   
   driver = webdriver.Chrome(service=service, options=options)
   ```

4. **Test the Script**
   - Run the script to verify ChromeDriver is found
   - Check for any path-related errors

---

## 🖥️ Platform-Specific Instructions

### macOS

**Recommended Location:**
```bash
/usr/local/bin/chromedriver
```

**Installation Steps:**
```bash
# 1. Download and extract ChromeDriver
# 2. Move to /usr/local/bin
sudo mv ~/Downloads/chromedriver /usr/local/bin/

# 3. Make executable (if needed)
sudo chmod +x /usr/local/bin/chromedriver

# 4. Verify
chromedriver --version
```

**Homebrew Alternative:**
```bash
brew install chromedriver
```

### Linux

**Recommended Location:**
```bash
/usr/local/bin/chromedriver
```

**Installation Steps:**
```bash
# 1. Download and extract ChromeDriver
# 2. Move to /usr/local/bin
sudo mv ~/Downloads/chromedriver /usr/local/bin/

# 3. Make executable
sudo chmod +x /usr/local/bin/chromedriver

# 4. Verify
chromedriver --version
```

**Package Manager Alternative:**
```bash
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# Fedora/RHEL
sudo dnf install chromium-driver
```

### Windows

**Recommended Approach:**
- Add ChromeDriver directory to System PATH (see Method 1 above)

**Manual Installation:**
1. Download `chromedriver_win64.zip`
2. Extract to a permanent location (e.g., `C:\Tools\chromedriver`)
3. Add that directory to System PATH
4. Verify in Command Prompt:
   ```cmd
   chromedriver --version
   ```

**Chocolatey Alternative:**
```powershell
choco install chromedriver
```

---

## ✅ Verification

### Quick Test

```bash
# Check ChromeDriver version
chromedriver --version

# Expected output:
# ChromeDriver 120.0.6099.109 (or your version)
```

### Test with Python Script

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Test auto-detection
try:
    service = Service()
    driver = webdriver.Chrome(service=service)
    print("✅ ChromeDriver found and working!")
    driver.quit()
except Exception as e:
    print(f"❌ Error: {e}")
```

### Test with Project Script

```bash
# Run the main script (it will test ChromeDriver)
python src/auto_login.py --accounts TEST_ACCOUNT
```

---

## 🐛 Troubleshooting

### Issue: ChromeDriver Not Found

**Error Message:**
```
selenium.common.exceptions.WebDriverException: 
Message: 'chromedriver' executable needs to be in PATH
```

**Solutions:**
1. Verify ChromeDriver is in PATH:
   ```bash
   which chromedriver  # macOS/Linux
   where chromedriver  # Windows
   ```
2. Check if executable:
   ```bash
   ls -l $(which chromedriver)  # macOS/Linux
   ```
3. Try specifying path directly (Method 2)

### Issue: Version Mismatch

**Error Message:**
```
SessionNotCreatedException: session not created: 
This version of ChromeDriver only supports Chrome version XX
```

**Solutions:**
1. Check your Chrome version:
   - Chrome → Help → About Google Chrome
2. Download matching ChromeDriver version
3. Replace old ChromeDriver with new one
4. Restart terminal/IDE

### Issue: Permission Denied (macOS/Linux)

**Error Message:**
```
PermissionError: [Errno 13] Permission denied: 'chromedriver'
```

**Solutions:**
```bash
# Make executable
chmod +x /path/to/chromedriver

# If in system directory, use sudo
sudo chmod +x /usr/local/bin/chromedriver
```

### Issue: ChromeDriver Quarantined (macOS)

**Error Message:**
```
"chromedriver" cannot be opened because the developer cannot be verified
```

**Solutions:**
```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine /path/to/chromedriver

# Or allow in System Preferences:
# System Preferences → Security & Privacy → Allow
```

### Issue: Chrome Not Found

**Error Message:**
```
selenium.common.exceptions.WebDriverException: 
Message: unknown error: cannot find Chrome binary
```

**Solutions:**
1. Verify Chrome is installed
2. Check Chrome installation path:
   - **macOS**: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
   - **Windows**: `C:\Program Files\Google\Chrome\Application\chrome.exe`
   - **Linux**: `/usr/bin/google-chrome` or `/usr/bin/chromium-browser`
3. Specify Chrome binary path if needed:
   ```python
   options = Options()
   options.binary_location = "/path/to/chrome/binary"
   ```

### Issue: Outdated ChromeDriver

**Symptoms:**
- Scripts work inconsistently
- Unexpected errors
- Browser doesn't open

**Solutions:**
1. Update Chrome to latest version
2. Download matching ChromeDriver
3. Replace old ChromeDriver
4. Restart terminal

---

## 📚 Additional Resources

- **Official ChromeDriver Downloads**: [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)
- **Selenium Documentation**: [https://selenium-python.readthedocs.io/](https://selenium-python.readthedocs.io/)
- **ChromeDriver Issues**: [https://github.com/SeleniumHQ/selenium/issues](https://github.com/SeleniumHQ/selenium/issues)

---

## 🔄 Keeping ChromeDriver Updated

ChromeDriver should match your Chrome browser version. When Chrome updates:

1. **Check Chrome Version**
   - Chrome → Help → About Google Chrome

2. **Download Matching ChromeDriver**
   - Visit ChromeDriver downloads page
   - Download version matching your Chrome

3. **Replace Old ChromeDriver**
   - Remove old version
   - Install new version (same method as before)

4. **Verify**
   ```bash
   chromedriver --version
   ```

---

<div align="center">

**Need Help?** Check the [Main README](../README.md) or [open an issue](https://github.com/Chaitanya-cpc/zerodha-multi-login/issues)

</div>
