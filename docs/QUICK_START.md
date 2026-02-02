# ⚡ Quick Start Guide

Get started with Zerodha Multi-Account Login Automation in 5 minutes!

## 🚀 Quick Setup (5 Steps)

### Step 1: Install Dependencies

```bash
# Install pip3 if needed
sudo apt update && sudo apt install python3-pip -y

# Install Python packages
pip3 install -r requirements.txt
```

**Or use virtual environment (recommended):**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Install ChromeDriver

```bash
# Check Chrome version
google-chrome --version

# Download matching ChromeDriver from:
# https://chromedriver.chromium.org/downloads

# Install ChromeDriver
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

**See `DRIVERS/README_DRIVERS.md` for detailed instructions.**

### Step 3: Create Credentials File

```bash
# Copy example file
cp config/zerodha_credentials.csv.example config/zerodha_credentials.csv

# Edit with your credentials
nano config/zerodha_credentials.csv

# Set secure permissions
chmod 600 config/zerodha_credentials.csv
```

**CSV Format:**
```csv
Username,Password,PIN/TOTP Secret,Status
YOUR_USERNAME,your_password,TOTP_SECRET_OR_PIN,1
```

### Step 4: Verify Setup

```bash
# Run verification script
./verify_setup.sh
```

### Step 5: First Run

```bash
# Login to all active accounts
python3 src/auto_login.py

# Or login to specific accounts
python3 src/auto_login.py --accounts USERNAME1,USERNAME2

# Or use interactive mode
python3 src/auto_login.py -i
```

---

## 📋 Common Commands

```bash
# Login to all accounts
python3 src/auto_login.py

# Login to specific accounts
python3 src/auto_login.py --accounts USER1,USER2

# Interactive account selection
python3 src/auto_login.py -i

# Interactive dashboard
python3 src/auto_login.py --dashboard

# Verbose mode (debugging)
python3 src/auto_login.py -v

# Company account
python3 open_Company_Account.py

# AlgoTest automation
python3 "CronJob Algotest Login/algotest_login.py"
```

---

## 🔧 Troubleshooting

### "Command 'pip3' not found"
```bash
sudo apt install python3-pip
```

### "ChromeDriver not found"
- Install ChromeDriver (see Step 2 above)
- Make sure it's in PATH: `which chromedriver`

### "Import errors"
```bash
# Reinstall dependencies
pip3 install -r requirements.txt --force-reinstall
```

### "Permission denied"
```bash
chmod 600 config/zerodha_credentials.csv
chmod +x verify_setup.sh
```

---

## 📚 Next Steps

- **Full Documentation:** See `README.md`
- **Detailed Setup:** See `SETUP.md`
- **Linux Setup:** See `LINUX_SETUP.md`
- **ChromeDriver Guide:** See `DRIVERS/README_DRIVERS.md`

---

## ✅ Verification Checklist

Run this to verify everything is set up:

```bash
./verify_setup.sh
```

All checks should pass before first use!

---

**Need Help?** Check the full documentation in `README.md` or `SETUP.md`.
