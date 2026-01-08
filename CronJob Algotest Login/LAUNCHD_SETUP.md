# 🚀 LaunchD Setup Guide for AlgoTest Login Automation

## Overview
`launchd` is the recommended task scheduler for macOS. It's more reliable than cron and integrates better with the macOS system, including wake-from-sleep functionality.

## 📋 Setup Instructions

### Step 1: Copy the plist file to LaunchAgents directory

```bash
# Copy the plist file to your user LaunchAgents directory
cp "/Applications/Codebase/zerodha_automation/CronJob Algotest Login/com.algotest.login.plist" ~/Library/LaunchAgents/
```

### Step 2: Load the launch agent

```bash
# Load the launch agent (starts the scheduled job)
launchctl load ~/Library/LaunchAgents/com.algotest.login.plist
```

### Step 3: Verify it's loaded

```bash
# Check if the job is loaded
launchctl list | grep algotest
```

You should see `com.algotest.login` in the list.

### Step 4: Test run (optional)

To test if it works immediately:

```bash
# Unload first (if already loaded)
launchctl unload ~/Library/LaunchAgents/com.algotest.login.plist

# Edit the plist to enable RunAtLoad temporarily
# Then reload
launchctl load ~/Library/LaunchAgents/com.algotest.login.plist
```

## 📝 Common Commands

### Check Job Status
```bash
launchctl list | grep algotest
```

### View Logs
```bash
# View output log
tail -f /Applications/Codebase/zerodha_automation/logs/cron/algotest_launchd.log

# View error log
tail -f /Applications/Codebase/zerodha_automation/logs/cron/algotest_launchd.error.log
```

### Unload (Stop) the Job
```bash
launchctl unload ~/Library/LaunchAgents/com.algotest.login.plist
```

### Reload After Changes
```bash
# Unload first
launchctl unload ~/Library/LaunchAgents/com.algotest.login.plist

# Make your changes to the plist file

# Load again
launchctl load ~/Library/LaunchAgents/com.algotest.login.plist
```

### Remove Completely
```bash
# Unload
launchctl unload ~/Library/LaunchAgents/com.algotest.login.plist

# Delete the plist file
rm ~/Library/LaunchAgents/com.algotest.login.plist
```

## ⚙️ Configuration

### Change Schedule Time
Edit the plist file:
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>8</integer>    <!-- Change hour (0-23) -->
    <key>Minute</key>
    <integer>45</integer>   <!-- Change minute (0-59) -->
</dict>
```

After editing, reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.algotest.login.plist
launchctl load ~/Library/LaunchAgents/com.algotest.login.plist
```

### Run Multiple Times Per Day
Remove `StartCalendarInterval` and use multiple entries or `StartInterval` for periodic execution.

### Run Only on Weekdays
Add day-specific keys:
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>8</integer>
    <key>Minute</key>
    <integer>45</integer>
    <key>Weekday</key>
    <integer>1</integer>  <!-- 0=Sunday, 1=Monday, etc. -->
</dict>
```

## 🔍 Troubleshooting

### Job Not Running
1. Check if it's loaded: `launchctl list | grep algotest`
2. Check logs for errors: `tail -f logs/cron/algotest_launchd.error.log`
3. Verify paths in plist are correct
4. Check file permissions: `ls -l ~/Library/LaunchAgents/com.algotest.login.plist`

### Permission Issues
```bash
# Ensure plist has correct permissions
chmod 644 ~/Library/LaunchAgents/com.algotest.login.plist
```

### Mac Waking from Sleep
LaunchD jobs will run when the Mac wakes up if the scheduled time has passed. However, for more control, you may want to prevent sleep during scheduled times.

## 📊 Advantages Over Cron

1. **Better macOS Integration**: Native macOS service
2. **Wake from Sleep**: Can wake Mac for scheduled tasks (with proper configuration)
3. **Automatic Restart**: Can automatically restart failed jobs
4. **Better Logging**: Built-in log file management
5. **Environment Variables**: Better environment variable handling

## 🔐 Security Note

The launch agent runs with your user privileges. Make sure your credential files have proper permissions:
```bash
chmod 600 config/zerodha_credentials.csv
chmod 600 "CronJob Algotest Login/algotest_credentials.json"
```

