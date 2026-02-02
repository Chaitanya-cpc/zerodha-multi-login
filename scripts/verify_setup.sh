#!/bin/bash
# Setup Verification Script for Zerodha Multi-Account Login Automation

echo "🔍 Verifying Zerodha Automation Setup..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Function to check and report
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

echo "=== Python Environment ==="
python3 --version > /dev/null 2>&1
check "Python 3 installed"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
info "Python version: $PYTHON_VERSION"

echo ""
echo "=== Python Dependencies ==="
python3 -c "import selenium" 2>/dev/null
check "selenium package installed" || warn "Install: pip3 install selenium"

python3 -c "import pyotp" 2>/dev/null
check "pyotp package installed" || warn "Install: pip3 install pyotp"

python3 -c "import rich" 2>/dev/null
check "rich package installed" || warn "Install: pip3 install rich"

python3 -c "import tqdm" 2>/dev/null
check "tqdm package installed" || warn "Install: pip3 install tqdm"

echo ""
echo "=== ChromeDriver ==="
if command -v chromedriver &> /dev/null; then
    CHROMEDRIVER_VERSION=$(chromedriver --version 2>&1 | awk '{print $2}')
    check "ChromeDriver installed (version: $CHROMEDRIVER_VERSION)"
else
    warn "ChromeDriver not found in PATH"
    info "Install ChromeDriver from: https://chromedriver.chromium.org/downloads"
fi

if command -v google-chrome &> /dev/null; then
    CHROME_VERSION=$(google-chrome --version 2>&1 | awk '{print $3}')
    info "Chrome version: $CHROME_VERSION"
elif command -v chromium &> /dev/null; then
    CHROMIUM_VERSION=$(chromium --version 2>&1 | awk '{print $2}')
    info "Chromium version: $CHROMIUM_VERSION"
else
    warn "Chrome/Chromium not found"
fi

echo ""
echo "=== Repository Structure ==="
[ -d "config" ] && check "config/ directory exists" || warn "config/ directory missing"
[ -d "src" ] && check "src/ directory exists" || warn "src/ directory missing"
[ -d "logs" ] && check "logs/ directory exists" || warn "logs/ directory missing"
[ -f "src/auto_login.py" ] && check "src/auto_login.py exists" || warn "src/auto_login.py missing"
[ -f "requirements.txt" ] && check "requirements.txt exists" || warn "requirements.txt missing"
[ -f "README.md" ] && check "README.md exists" || warn "README.md missing"

echo ""
echo "=== Configuration Files ==="
if [ -f "config/zerodha_credentials.csv" ]; then
    check "config/zerodha_credentials.csv exists"
    PERMS=$(stat -c %a "config/zerodha_credentials.csv" 2>/dev/null || stat -f %OLp "config/zerodha_credentials.csv" 2>/dev/null || echo "unknown")
    if [ "$PERMS" = "600" ]; then
        check "Credentials file permissions are secure (600)"
    else
        warn "Credentials file permissions should be 600 (current: $PERMS)"
        info "Fix with: chmod 600 config/zerodha_credentials.csv"
    fi
else
    warn "config/zerodha_credentials.csv not found"
    info "Create from: cp config/zerodha_credentials.csv.example config/zerodha_credentials.csv"
fi

if [ -f "config/zerodha_credentials.csv.example" ]; then
    check "config/zerodha_credentials.csv.example exists"
else
    warn "config/zerodha_credentials.csv.example missing"
fi

[ -f "config/account_groups.json" ] && check "config/account_groups.json exists" || warn "config/account_groups.json missing"

if [ -f "CronJob Algotest Login/algotest_credentials.json" ]; then
    check "AlgoTest credentials file exists"
    PERMS=$(stat -c %a "CronJob Algotest Login/algotest_credentials.json" 2>/dev/null || stat -f %OLp "CronJob Algotest Login/algotest_credentials.json" 2>/dev/null || echo "unknown")
    if [ "$PERMS" = "600" ]; then
        check "AlgoTest credentials file permissions are secure (600)"
    else
        warn "AlgoTest credentials file permissions should be 600 (current: $PERMS)"
        info "Fix with: chmod 600 'CronJob Algotest Login/algotest_credentials.json'"
    fi
else
    info "AlgoTest credentials file not found (optional)"
fi

echo ""
echo "=== Script Functionality ==="
python3 src/auto_login.py --help > /dev/null 2>&1
check "Main script (auto_login.py) is executable"

python3 open_Company_Account.py --help > /dev/null 2>&1
if [ $? -eq 0 ] || [ $? -eq 1 ]; then  # Exit code 0 or 1 is OK (help or missing args)
    check "Company account script is executable"
else
    warn "Company account script has issues"
fi

echo ""
echo "=== Security ==="
[ -f ".gitignore" ] && check ".gitignore exists" || warn ".gitignore missing"

if grep -q "zerodha_credentials.csv" .gitignore 2>/dev/null; then
    check "Credentials file is in .gitignore"
else
    warn "Credentials file not in .gitignore"
fi

echo ""
echo "=== Summary ==="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Setup is complete.${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Setup mostly complete with $WARNINGS warning(s).${NC}"
    echo -e "${YELLOW}   Review warnings above and fix as needed.${NC}"
    exit 0
else
    echo -e "${RED}❌ Setup incomplete with $ERRORS error(s) and $WARNINGS warning(s).${NC}"
    echo -e "${RED}   Please fix errors before using the automation.${NC}"
    exit 1
fi
