#!/bin/bash
# ChromeDriver Download and Setup Script
# Downloads ChromeDriver matching your Chrome version

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🌐 ChromeDriver Setup Script${NC}"
echo ""

# Detect Chrome version
if command -v google-chrome &> /dev/null; then
    CHROME_VERSION=$(google-chrome --version 2>&1 | awk '{print $3}' | cut -d'.' -f1)
    CHROME_TYPE="google-chrome"
elif command -v chromium &> /dev/null; then
    CHROME_VERSION=$(chromium --version 2>&1 | awk '{print $2}' | cut -d'.' -f1)
    CHROME_TYPE="chromium"
else
    echo -e "${RED}✗ Chrome/Chromium not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Detected ${CHROME_TYPE} version: ${CHROME_VERSION}.x"

# Check if ChromeDriver already installed
if command -v chromedriver &> /dev/null; then
    CHROMEDRIVER_VERSION=$(chromedriver --version 2>&1 | awk '{print $2}' | cut -d'.' -f1)
    if [ "$CHROMEDRIVER_VERSION" = "$CHROME_VERSION" ]; then
        echo -e "${GREEN}✓${NC} ChromeDriver ${CHROMEDRIVER_VERSION}.x is already installed and matches Chrome version"
        exit 0
    else
        echo -e "${YELLOW}⚠${NC} ChromeDriver ${CHROMEDRIVER_VERSION}.x installed but doesn't match Chrome ${CHROME_VERSION}.x"
        echo "Please update ChromeDriver to match Chrome version"
    fi
fi

echo ""
echo -e "${BLUE}Note:${NC} ChromeDriver cannot be automatically downloaded due to Chrome's version-specific requirements."
echo "Please follow these steps manually:"
echo ""
echo "1. Visit: https://googlechromelabs.github.io/chrome-for-testing/"
echo "2. Or use: https://chromedriver.chromium.org/downloads"
echo "3. Download ChromeDriver for Chrome version ${CHROME_VERSION}.x (Linux x64)"
echo "4. Extract and install:"
echo ""
echo "   unzip chromedriver_linux64.zip"
echo "   sudo mv chromedriver /usr/local/bin/"
echo "   sudo chmod +x /usr/local/bin/chromedriver"
echo "   chromedriver --version  # Verify installation"
echo ""
echo "For automated installation using webdriver-manager (alternative):"
echo "   pip3 install webdriver-manager"
echo "   # Then update the script to use webdriver-manager"
echo ""
echo "See DRIVERS/README_DRIVERS.md for detailed instructions"
