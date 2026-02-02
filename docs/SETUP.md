# 🚀 Repository Setup Guide

Complete setup instructions for the Zerodha Multi-Account Login Automation repository.

## ✅ Pre-Setup Checklist

- [x] Repository cloned successfully
- [x] Logs directory created
- [x] Configuration files structure ready
- [ ] Python dependencies installed
- [ ] ChromeDriver installed
- [ ] Credentials configured

---

## 📦 Step 1: Install Python Dependencies

### Option A: Using pip3 (Recommended)

```bash
# Install pip3 if not already installed
sudo apt update
sudo apt install python3-pip -y

# Install dependencies
pip3 install -r requirements.txt
```

### Option B: Using virtual environment (Best Practice)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Required Packages:
- `selenium` - Web automation and browser control
- `pyotp` - Time-based One-Time Password (TOTP) generation
- `rich` - Beautiful terminal UI with colors, tables, and progress bars
- `tqdm` - Progress bars for long-running operations

---

## 🔐 Step 2: Configure Credentials

### 2.1 Zerodha Credentials (CSV Format)

1. **Copy the example file:**
   ```bash
   cp config/zerodha_credentials.csv.example config/zerodha_credentials.csv
   ```

2. **Edit `config/zerodha_credentials.csv` with your credentials:**
   ```csv
   Username,Password,PIN/TOTP Secret,Status
   YOUR_USERNAME,your_password,YourTOTPSecretOrPIN,1
   ```

3. **Set proper permissions (Security):**
   ```bash
   chmod 600 config/zerodha_credentials.csv
   ```

**CSV Format Explanation:**
- `Username`: Your Zerodha user ID (required)
- `Password`: Your account password (required)
- `PIN/TOTP Secret`: Either:
  - Static PIN: 6-digit numeric PIN (e.g., "123456")
  - TOTP Secret: Base32 encoded secret for authenticator apps (e.g., "JBSWY3DPEHPK3PXP")
  - Leave empty if 2FA is not required
- `Status`: "1" for active (will be logged in), "0" for inactive (will be skipped)

### 2.2 AlgoTest Credentials (JSON Format - Optional)

If using AlgoTest automation:

1. **Copy the example file:**
   ```bash
   cp "CronJob Algotest Login/algotest_credentials.json.example" "CronJob Algotest Login/algotest_credentials.json"
   ```

2. **Edit `CronJob Algotest Login/algotest_credentials.json`:**
   ```json
   {
     "algotest": {
       "username": "your_phone_number",
       "password": "your_password"
     }
   }
   ```

3. **Set proper permissions:**
   ```bash
   chmod 600 "CronJob Algotest Login/algotest_credentials.json"
   ```

---

## 🌐 Step 3: Install ChromeDriver

ChromeDriver is required for Selenium automation. See detailed instructions in `DRIVERS/README_DRIVERS.md`.

### Quick Setup:

```bash
# Check Chrome version
google-chrome --version
# OR
chromium --version

# Download matching ChromeDriver from:
# https://chromedriver.chromium.org/downloads

# Extract and install
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Verify installation
chromedriver --version
```

**Note:** ChromeDriver version must match your Chrome/Chromium browser version.

---

## ✅ Step 4: Verify Setup

### 4.1 Check Directory Structure

```bash
# Verify repository structure
tree -L 2 . || find . -maxdepth 2 -type d
```

Expected structure:
```
zerodha_automation/
├── config/
│   ├── zerodha_credentials.csv (create from example)
│   └── account_groups.json
├── logs/ (created automatically)
├── src/
│   └── auto_login.py
├── CronJob Algotest Login/
│   └── algotest_credentials.json (optional)
└── requirements.txt
```

### 4.2 Test Installation

```bash
# Test Python imports
python3 -c "import selenium; import pyotp; import rich; import tqdm; print('All dependencies installed!')"

# Test ChromeDriver
chromedriver --version

# Test script (dry run - will show help)
python3 src/auto_login.py --help
```

---

## 🚀 Step 5: First Run

### Basic Usage:

```bash
# Login to all active accounts
python3 src/auto_login.py

# Login to specific accounts
python3 src/auto_login.py --accounts USERNAME1,USERNAME2

# Interactive account selection
python3 src/auto_login.py -i

# Verbose mode (for debugging)
python3 src/auto_login.py -v

# Interactive dashboard
python3 src/auto_login.py --dashboard
```

### Company Account Script:

```bash
# Login to company account
python3 open_Company_Account.py
```

### AlgoTest Automation:

```bash
# Run Zerodha → AlgoTest workflow
python3 "CronJob Algotest Login/algotest_login.py"
```

---

## 🔒 Security Best Practices

1. **File Permissions:**
   ```bash
   # Restrict credential file access
   chmod 600 config/zerodha_credentials.csv
   chmod 600 "CronJob Algotest Login/algotest_credentials.json"
   ```

2. **Never Commit Credentials:**
   - Credential files are already in `.gitignore`
   - Never push credentials to GitHub
   - Use example files for documentation

3. **Use Virtual Environment:**
   - Isolates dependencies from system Python
   - Prevents conflicts with other projects

4. **Regular Updates:**
   - Update passwords periodically
   - Keep ChromeDriver updated with Chrome version
   - Update Python packages regularly

---

## 🐛 Troubleshooting

### Issue: Dependencies Not Installing

**Solution:**
```bash
# Update pip first
pip3 install --upgrade pip

# Install dependencies one by one
pip3 install selenium
pip3 install pyotp
pip3 install rich
pip3 install tqdm
```

### Issue: ChromeDriver Not Found

**Solution:**
- Check if ChromeDriver is in PATH: `which chromedriver`
- Verify ChromeDriver version matches Chrome: `chromedriver --version` vs `google-chrome --version`
- See `DRIVERS/README_DRIVERS.md` for detailed instructions

### Issue: Permission Denied on Credential Files

**Solution:**
```bash
# Set proper permissions
chmod 600 config/zerodha_credentials.csv
chmod 600 "CronJob Algotest Login/algotest_credentials.json"
```

### Issue: Import Errors

**Solution:**
- Verify virtual environment is activated (if using venv)
- Reinstall dependencies: `pip3 install -r requirements.txt --force-reinstall`
- Check Python version: `python3 --version` (requires Python 3.8+)

---

## 📚 Additional Documentation

- **Main README:** `README.md`
- **Linux Setup:** `LINUX_SETUP.md`
- **ChromeDriver Setup:** `DRIVERS/README_DRIVERS.md`
- **AlgoTest Automation:** `CronJob Algotest Login/README.md`
- **Launchd Setup (macOS):** `CronJob Algotest Login/LAUNCHD_SETUP.md`

---

## ✅ Setup Verification Checklist

Run these commands to verify your setup:

```bash
# 1. Check Python version (should be 3.8+)
python3 --version

# 2. Check dependencies
python3 -c "import selenium; import pyotp; import rich; import tqdm; print('✓ Dependencies OK')"

# 3. Check ChromeDriver
chromedriver --version && echo "✓ ChromeDriver OK"

# 4. Check credential files exist
[ -f config/zerodha_credentials.csv ] && echo "✓ Credentials file exists" || echo "✗ Create credentials file"

# 5. Check file permissions
[ $(stat -c %a config/zerodha_credentials.csv 2>/dev/null || echo 0) = "600" ] && echo "✓ Permissions OK" || echo "✗ Set permissions to 600"

# 6. Test script help
python3 src/auto_login.py --help > /dev/null && echo "✓ Script works" || echo "✗ Script error"
```

---

## 🎉 You're All Set!

Once all checks pass, you're ready to use the Zerodha Multi-Account Login Automation!

For usage instructions, see `README.md`.
