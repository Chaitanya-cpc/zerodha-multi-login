#!/bin/bash
# Cron wrapper script for AlgoTest Login Automation
# This script ensures proper environment and runs the Python script

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Set up environment
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
export PYTHONUNBUFFERED=1

# Find Python3
PYTHON3=$(which python3)
if [ -z "$PYTHON3" ]; then
    echo "Error: python3 not found in PATH" >&2
    exit 1
fi

# Log file paths
LOG_DIR="$PROJECT_DIR/logs/cron"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/algotest_cron.log"
ERROR_LOG="$LOG_DIR/algotest_cron.error.log"

# Timestamp
echo "===========================================" >> "$LOG_FILE"
echo "Cron job started at: $(date)" >> "$LOG_FILE"
echo "===========================================" >> "$LOG_FILE"

# Run the Python script
"$PYTHON3" "$SCRIPT_DIR/algotest_login.py" >> "$LOG_FILE" 2>> "$ERROR_LOG"

# Capture exit code
EXIT_CODE=$?

# Log completion
if [ $EXIT_CODE -eq 0 ]; then
    echo "Cron job completed successfully at: $(date)" >> "$LOG_FILE"
else
    echo "Cron job failed with exit code $EXIT_CODE at: $(date)" >> "$ERROR_LOG"
fi

echo "===========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

exit $EXIT_CODE
