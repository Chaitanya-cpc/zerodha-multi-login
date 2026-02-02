# ⏰ Cron Job Setup Guide for Linux

Complete guide for setting up scheduled AlgoTest login automation on Linux using cron.

## 📋 Overview

This guide shows how to schedule the AlgoTest login automation script (`algotest_login.py`) to run automatically at specific times using Linux cron.

**Default Schedule:** 8:45 AM daily (can be customized)

---

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
bash "CronJob Algotest Login/setup_cron.sh"

# Or manually add to crontab
(crontab -l 2>/dev/null; echo "45 8 * * * $(pwd)/CronJob\ Algotest\ Login/algotest_cron.sh") | crontab -
```

### Option 2: Manual Setup

```bash
# 1. Make the wrapper script executable (if not already)
chmod +x "CronJob Algotest Login/algotest_cron.sh"

# 2. Edit your crontab
crontab -e

# 3. Add this line (adjust time as needed):
45 8 * * * /media/chaitanya/NVME_512/zerodha_automation/CronJob\ Algotest\ Login/algotest_cron.sh

# 4. Save and exit (Ctrl+X, then Y, then Enter for nano)
```

---

## 📝 Cron Syntax Explained

Cron uses 5 fields to specify schedule:

```
* * * * * command
│ │ │ │ │
│ │ │ │ └─── Day of week (0-7, 0 or 7 = Sunday)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

### Common Examples

```bash
# Run at 8:45 AM daily
45 8 * * * /path/to/algotest_cron.sh

# Run at 9:00 AM on weekdays (Monday-Friday)
0 9 * * 1-5 /path/to/algotest_cron.sh

# Run at 8:30 AM and 3:30 PM daily
30 8,15 * * * /path/to/algotest_cron.sh

# Run every hour during market hours (9 AM to 3:30 PM)
0 9-15 * * 1-5 /path/to/algotest_cron.sh

# Run at 8:45 AM only on weekdays
45 8 * * 1-5 /path/to/algotest_cron.sh
```

---

## 🔧 Step-by-Step Setup

### Step 1: Get Full Path to Wrapper Script

```bash
cd /media/chaitanya/NVME_512/zerodha_automation
FULL_PATH="$(pwd)/CronJob Algotest Login/algotest_cron.sh"
echo "Full path: $FULL_PATH"
```

### Step 2: Make Script Executable

```bash
chmod +x "CronJob Algotest Login/algotest_cron.sh"
```

### Step 3: Verify Script Works

```bash
# Test the wrapper script manually
"CronJob Algotest Login/algotest_cron.sh"

# Check logs
tail -f logs/cron/algotest_cron.log
tail -f logs/cron/algotest_cron.error.log
```

### Step 4: Add to Crontab

```bash
# Open crontab editor
crontab -e

# Add the cron job (replace with your actual path)
45 8 * * * /media/chaitanya/NVME_512/zerodha_automation/CronJob\ Algotest\ Login/algotest_cron.sh
```

**Important:** Use escaped spaces or quotes in the path, or use absolute path without spaces.

### Step 5: Verify Crontab Entry

```bash
# List current crontab entries
crontab -l

# You should see your entry
```

---

## 📊 Viewing Logs

### Real-time Log Monitoring

```bash
# View output log
tail -f logs/cron/algotest_cron.log

# View error log
tail -f logs/cron/algotest_cron.error.log

# View both logs simultaneously
tail -f logs/cron/algotest_cron*.log
```

### Check Recent Runs

```bash
# Last 50 lines of output log
tail -n 50 logs/cron/algotest_cron.log

# Last 50 lines of error log
tail -n 50 logs/cron/algotest_cron.error.log

# Search for errors
grep -i error logs/cron/algotest_cron.error.log
```

---

## 🔍 Troubleshooting

### Issue: Cron Job Not Running

**Check cron service:**
```bash
# Check if cron service is running
systemctl status cron  # Ubuntu/Debian
systemctl status crond  # CentOS/RHEL

# Start cron if not running
sudo systemctl start cron
sudo systemctl enable cron
```

**Check crontab:**
```bash
# Verify cron job exists
crontab -l

# Check cron logs
grep CRON /var/log/syslog | tail -20  # Ubuntu/Debian
grep CRON /var/log/cron | tail -20    # CentOS/RHEL
```

### Issue: Script Not Found

**Solution:**
- Use absolute paths in crontab
- Ensure the script is executable: `chmod +x algotest_cron.sh`
- Check PATH in the wrapper script

### Issue: Python Not Found

**Solution:**
- Ensure Python3 is in PATH (wrapper script sets PATH)
- Or specify full Python path in wrapper script
- Test manually: `which python3`

### Issue: Permission Denied

**Solution:**
```bash
# Make script executable
chmod +x "CronJob Algotest Login/algotest_cron.sh"

# Check file permissions
ls -l "CronJob Algotest Login/algotest_cron.sh"
```

### Issue: Credentials Not Found

**Solution:**
- Ensure credentials file exists: `config/zerodha_credentials.csv`
- Ensure AlgoTest credentials exist: `CronJob Algotest Login/algotest_credentials.json`
- Check file permissions: `chmod 600 config/zerodha_credentials.csv`

### Issue: ChromeDriver Not Found

**Solution:**
- Install ChromeDriver and ensure it's in PATH
- Or specify full path to chromedriver in the script
- See `DRIVERS/README_DRIVERS.md` for ChromeDriver setup

---

## ⚙️ Configuration Options

### Change Schedule Time

Edit crontab:
```bash
crontab -e
```

Change the time fields:
```bash
# Original: 8:45 AM daily
45 8 * * * /path/to/algotest_cron.sh

# Example: 9:30 AM daily
30 9 * * * /path/to/algotest_cron.sh

# Example: 8:00 AM and 2:00 PM daily
0 8,14 * * * /path/to/algotest_cron.sh
```

### Run Only on Weekdays

```bash
# Monday-Friday at 8:45 AM
45 8 * * 1-5 /path/to/algotest_cron.sh
```

### Run Multiple Times Per Day

```bash
# Market hours: 9:15 AM, 11:00 AM, 2:30 PM on weekdays
15 9 * * 1-5 /path/to/algotest_cron.sh
0 11 * * 1-5 /path/to/algotest_cron.sh
30 14 * * 1-5 /path/to/algotest_cron.sh
```

### Add Email Notifications

```bash
# Add MAILTO to crontab (at the top)
MAILTO=your-email@example.com

# Then add your cron job
45 8 * * * /path/to/algotest_cron.sh
```

---

## 📋 Management Commands

### View Current Cron Jobs

```bash
# List all cron jobs for current user
crontab -l

# List cron jobs for specific user (requires sudo)
sudo crontab -u username -l
```

### Edit Cron Jobs

```bash
# Edit current user's crontab
crontab -e

# This opens your default editor (usually nano or vim)
```

### Remove Cron Job

```bash
# Edit crontab
crontab -e

# Remove the line with algotest_cron.sh
# Save and exit

# Or remove all cron jobs (CAUTION!)
crontab -r
```

### Test Cron Job Manually

```bash
# Run the wrapper script directly
bash "CronJob Algotest Login/algotest_cron.sh"

# Check if it works
echo $?  # Should be 0 if successful
```

---

## 🔐 Security Considerations

1. **File Permissions:**
   ```bash
   chmod 600 config/zerodha_credentials.csv
   chmod 600 "CronJob Algotest Login/algotest_credentials.json"
   chmod 755 "CronJob Algotest Login/algotest_cron.sh"
   ```

2. **Crontab Permissions:**
   - Only edit your own crontab (`crontab -e`)
   - Don't use `sudo crontab -e` unless necessary

3. **Credential Storage:**
   - Credentials are stored locally (gitignored)
   - Ensure cron runs with correct user permissions

---

## 📚 Additional Resources

- **Main README:** `../../README.md`
- **AlgoTest Automation:** `README.md`
- **Linux Setup:** `../../LINUX_SETUP.md`
- **ChromeDriver Guide:** `../../DRIVERS/README_DRIVERS.md`

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Cron job added: `crontab -l | grep algotest`
- [ ] Script is executable: `ls -l algotest_cron.sh`
- [ ] Manual test works: `bash algotest_cron.sh`
- [ ] Logs directory exists: `ls -d logs/cron`
- [ ] Credentials files exist and have correct permissions
- [ ] ChromeDriver is installed and in PATH
- [ ] Cron service is running: `systemctl status cron`

---

**Setup complete!** Your AlgoTest login automation will now run on schedule. Check logs in `logs/cron/` for execution history.
