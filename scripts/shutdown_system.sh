#!/bin/bash
# System Shutdown Script for Cron
# This script safely shuts down the system

# Log file path (relative to script location)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs/cron"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/shutdown_cron.log"
ERROR_LOG="$LOG_DIR/shutdown_cron.error.log"

# Timestamp
echo "===========================================" >> "$LOG_FILE"
echo "Shutdown scheduled at: $(date)" >> "$LOG_FILE"
echo "===========================================" >> "$LOG_FILE"

# Try different shutdown methods
# Method 1: systemctl poweroff (preferred, works if user has permissions)
if systemctl poweroff >> "$LOG_FILE" 2>> "$ERROR_LOG"; then
    echo "Shutdown initiated via systemctl poweroff at: $(date)" >> "$LOG_FILE"
    exit 0
fi

# Method 2: shutdown command without sudo (if user has permissions)
if shutdown -h now >> "$LOG_FILE" 2>> "$ERROR_LOG"; then
    echo "Shutdown initiated via shutdown command at: $(date)" >> "$LOG_FILE"
    exit 0
fi

# Method 3: sudo shutdown (requires passwordless sudo configuration)
if sudo -n shutdown -h now >> "$LOG_FILE" 2>> "$ERROR_LOG" 2>/dev/null; then
    echo "Shutdown initiated via sudo shutdown at: $(date)" >> "$LOG_FILE"
    exit 0
fi

# Method 4: dbus-send (alternative method)
if dbus-send --system --print-reply --dest=org.freedesktop.login1 /org/freedesktop/login1 "org.freedesktop.login1.Manager.PowerOff" boolean:true >> "$LOG_FILE" 2>> "$ERROR_LOG"; then
    echo "Shutdown initiated via dbus-send at: $(date)" >> "$LOG_FILE"
    exit 0
fi

# If all methods fail, log error
echo "ERROR: Failed to initiate shutdown at: $(date)" >> "$ERROR_LOG"
echo "All shutdown methods failed. Check permissions." >> "$ERROR_LOG"
echo "You may need to configure passwordless sudo for shutdown command." >> "$ERROR_LOG"
exit 1
