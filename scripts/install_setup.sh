#!/bin/bash
# Automated Setup Script for Zerodha Multi-Account Login Automation
# This script installs all dependencies and sets up the environment

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Zerodha Automation Setup Script${NC}"
echo ""

# Check if running with sudo for system-wide installation
NEEDS_SUDO=false
if [ "$EUID" -ne 0 ]; then
    NEEDS_SUDO=true
fi

# Function to check command
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is not installed"
        return 1
    fi
}

echo "=== Step 1: Checking Prerequisites ==="
check_command python3
check_command pip3
check_command chromedriver
check_command google-chrome || check_command chromium

echo ""
echo "=== Step 2: Installing pip3 (if needed) ==="
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}Installing pip3...${NC}"
    if [ "$NEEDS_SUDO" = true ]; then
        echo -e "${YELLOW}Requires sudo. Please run:${NC}"
        echo "sudo apt update && sudo apt install python3-pip -y"
        exit 1
    else
        apt update && apt install python3-pip -y
    fi
else
    echo -e "${GREEN}✓${NC} pip3 is already installed"
fi

echo ""
echo "=== Step 3: Installing Python Dependencies ==="
if command -v pip3 &> /dev/null; then
    echo -e "${BLUE}Installing Python packages...${NC}"
    pip3 install -r requirements.txt
    echo -e "${GREEN}✓${NC} Python dependencies installed"
else
    echo -e "${RED}✗${NC} pip3 not available. Cannot install dependencies."
    exit 1
fi

echo ""
echo "=== Step 4: Setting up ChromeDriver ==="
if command -v chromedriver &> /dev/null; then
    CHROMEDRIVER_VERSION=$(chromedriver --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓${NC} ChromeDriver is installed (version: $CHROMEDRIVER_VERSION)"
else
    echo -e "${YELLOW}ChromeDriver not found. Checking Chrome version...${NC}"
    
    if command -v google-chrome &> /dev/null; then
        CHROME_VERSION=$(google-chrome --version 2>&1 | awk '{print $3}' | cut -d'.' -f1)
    elif command -v chromium &> /dev/null; then
        CHROME_VERSION=$(chromium --version 2>&1 | awk '{print $2}' | cut -d'.' -f1)
    else
        echo -e "${RED}✗${NC} Chrome/Chromium not found"
        CHROME_VERSION="unknown"
    fi
    
    if [ "$CHROME_VERSION" != "unknown" ]; then
        echo -e "${BLUE}Detected Chrome version: ${CHROME_VERSION}.x${NC}"
        echo -e "${YELLOW}Please install ChromeDriver manually:${NC}"
        echo "1. Visit: https://chromedriver.chromium.org/downloads"
        echo "2. Download matching version (${CHROME_VERSION}.x)"
        echo "3. Extract and install:"
        echo "   unzip chromedriver_linux64.zip"
        echo "   sudo mv chromedriver /usr/local/bin/"
        echo "   sudo chmod +x /usr/local/bin/chromedriver"
        echo ""
        echo "Or see: DRIVERS/README_DRIVERS.md for detailed instructions"
    fi
fi

echo ""
echo "=== Step 5: Setting up Configuration Files ==="
if [ ! -f "config/zerodha_credentials.csv" ]; then
    if [ -f "config/zerodha_credentials.csv.example" ]; then
        echo -e "${BLUE}Creating credentials file from example...${NC}"
        cp config/zerodha_credentials.csv.example config/zerodha_credentials.csv
        chmod 600 config/zerodha_credentials.csv
        echo -e "${GREEN}✓${NC} Credentials file created"
        echo -e "${YELLOW}⚠${NC} Please edit config/zerodha_credentials.csv with your actual credentials"
    else
        echo -e "${RED}✗${NC} Example credentials file not found"
    fi
else
    echo -e "${GREEN}✓${NC} Credentials file already exists"
    # Ensure permissions are secure
    chmod 600 config/zerodha_credentials.csv 2>/dev/null || true
fi

echo ""
echo "=== Step 6: Verifying Installation ==="
cd "$(dirname "$0")"
if [ -f "./verify_setup.sh" ]; then
    bash ./verify_setup.sh
    VERIFY_EXIT=$?
else
    echo -e "${YELLOW}⚠${NC} Verification script not found"
    VERIFY_EXIT=0
fi

echo ""
echo "=== Setup Complete! ==="
if [ $VERIFY_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ Setup completed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Edit config/zerodha_credentials.csv with your credentials"
    echo "2. Run: python3 src/auto_login.py --help"
    echo "3. Start using: python3 src/auto_login.py"
else
    echo -e "${YELLOW}⚠️  Setup completed with some issues.${NC}"
    echo "Please review the verification output above."
fi
