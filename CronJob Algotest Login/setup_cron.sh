#!/bin/bash
# Automated Cron Job Setup Script for AlgoTest Login
# This script helps set up the cron job easily

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}⏰ AlgoTest Cron Job Setup${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

echo -e "${BLUE}Step 1: Verifying setup...${NC}"

# Check if wrapper script exists
if [ ! -f "$SCRIPT_DIR/algotest_cron.sh" ]; then
    echo -e "${RED}✗${NC} algotest_cron.sh not found"
    exit 1
fi

# Make wrapper script executable
chmod +x "$SCRIPT_DIR/algotest_cron.sh"
echo -e "${GREEN}✓${NC} Wrapper script is executable"

# Create logs directory
mkdir -p logs/cron
echo -e "${GREEN}✓${NC} Logs directory created"

# Get full path to wrapper script
FULL_PATH="$SCRIPT_DIR/algotest_cron.sh"
echo -e "${GREEN}✓${NC} Script path: $FULL_PATH"

echo ""
echo -e "${BLUE}Step 2: Testing script manually...${NC}"
echo -e "${YELLOW}This will run the script once to verify it works.${NC}"
read -p "Continue? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Running test...${NC}"
    if bash "$FULL_PATH"; then
        echo -e "${GREEN}✓${NC} Script test successful"
    else
        echo -e "${RED}✗${NC} Script test failed. Please check logs/cron/algotest_cron.error.log"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠${NC} Skipping test. Please test manually before setting up cron."
fi

echo ""
echo -e "${BLUE}Step 3: Setting up cron job...${NC}"

# Default schedule: 8:45 AM daily
DEFAULT_SCHEDULE="45 8 * * *"

echo "Default schedule: 8:45 AM daily"
read -p "Use default schedule? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Enter custom cron schedule (format: minute hour day month weekday)"
    echo "Example: 45 8 * * * (8:45 AM daily)"
    echo "Example: 0 9 * * 1-5 (9:00 AM weekdays)"
    read -p "Schedule: " CUSTOM_SCHEDULE
    CRON_SCHEDULE="${CUSTOM_SCHEDULE:-$DEFAULT_SCHEDULE}"
else
    CRON_SCHEDULE="$DEFAULT_SCHEDULE"
fi

# Escape spaces in path for crontab
CRON_COMMAND="$CRON_SCHEDULE \"$FULL_PATH\""

echo ""
echo -e "${BLUE}Step 4: Adding to crontab...${NC}"
echo -e "${YELLOW}Cron entry to be added:${NC}"
echo "$CRON_SCHEDULE $FULL_PATH"
echo ""

read -p "Add this cron job? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Backup existing crontab
    crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null || true
    
    # Remove existing algotest cron entry if exists
    crontab -l 2>/dev/null | grep -v "algotest_cron.sh" | crontab - || true
    
    # Add new cron entry
    (crontab -l 2>/dev/null; echo "$CRON_SCHEDULE $FULL_PATH") | crontab -
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Cron job added successfully"
    else
        echo -e "${RED}✗${NC} Failed to add cron job"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}✅ Cron job setup complete!${NC}"
    echo ""
    echo "Current crontab entries:"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    crontab -l
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Monitor logs: tail -f logs/cron/algotest_cron.log"
    echo "2. Check errors: tail -f logs/cron/algotest_cron.error.log"
    echo "3. View crontab: crontab -l"
    echo "4. Edit schedule: crontab -e"
    echo ""
else
    echo -e "${YELLOW}⚠${NC} Cron job not added. You can add it manually:"
    echo ""
    echo "  crontab -e"
    echo ""
    echo "Then add this line:"
    echo "  $CRON_SCHEDULE $FULL_PATH"
    echo ""
fi
