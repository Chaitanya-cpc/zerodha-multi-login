# 📁 Source Code Directory

This directory contains all Python scripts for the Zerodha automation project.

## 📋 Scripts

### Main Scripts
- **auto_login.py** - Multi-account login automation (main script)
- **open_my_accounts.py** - Login to HDN374 and BU0542 accounts (parallel processing)
- **open_Company_Account.py** - Legacy company account login script

### Cron Jobs
- **[../CronJob Algotest Login/algotest_login.py](../CronJob%20Algotest%20Login/algotest_login.py)** - Zerodha to AlgoTest automation

## 🚀 Usage

Run scripts from the project root:

```bash
# Multi-account login
python3 src/auto_login.py

# My accounts (HDN374 & BU0542)
python3 src/open_my_accounts.py

# Legacy company account
python3 src/open_Company_Account.py
```

## 📝 Notes

- All scripts use parallel processing for multiple accounts
- Scripts automatically manage ChromeDriver via webdriver-manager
- All scripts support "close Chrome windows" feature on completion

## 🔗 Related

- Main README: [../README.md](../README.md)
- Documentation: [../docs/](../docs/)
- Scripts: [../scripts/](../scripts/)
- Configuration: [../config/](../config/)

