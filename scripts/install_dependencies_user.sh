#!/bin/bash
# Install Dependencies in User Space (No sudo required)
# This script installs Python packages to user directory

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📦 Installing Python Dependencies (User Space)${NC}"
echo ""

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo -e "${RED}✗${NC} pip3 not found"
    echo ""
    echo -e "${YELLOW}Installing pip3 requires sudo. Please run:${NC}"
    echo "  sudo apt update && sudo apt install python3-pip -y"
    echo ""
    echo "OR install pip using get-pip.py (no sudo):"
    echo "  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py"
    echo "  python3 get-pip.py --user"
    echo ""
    exit 1
fi

# Determine pip command
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif python3 -m pip --version &> /dev/null; then
    PIP_CMD="python3 -m pip"
else
    echo -e "${RED}✗${NC} pip not available"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found pip: $PIP_CMD"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${BLUE}Python version:${NC} $PYTHON_VERSION"
echo ""

# Install dependencies to user directory
echo -e "${BLUE}Installing dependencies to user directory...${NC}"
echo ""

if [ "$PIP_CMD" = "pip3" ]; then
    pip3 install --user -r requirements.txt
else
    python3 -m pip install --user -r requirements.txt
fi

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓${NC} Dependencies installed successfully!"
    echo ""
    echo -e "${BLUE}Note:${NC} Packages are installed to user directory (~/.local/lib/python3.x/site-packages)"
    echo "Make sure ~/.local/bin is in your PATH if binaries are installed there."
    echo ""
    
    # Add to PATH if needed
    if [ -d "$HOME/.local/bin" ] && [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo -e "${YELLOW}⚠${NC} Consider adding ~/.local/bin to your PATH:"
        echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
        echo "  source ~/.bashrc"
        echo ""
    fi
    
    # Verify installation
    echo -e "${BLUE}Verifying installation...${NC}"
    python3 -c "import selenium; print('✓ selenium installed')" 2>/dev/null || echo "✗ selenium failed"
    python3 -c "import pyotp; print('✓ pyotp installed')" 2>/dev/null || echo "✗ pyotp failed"
    python3 -c "import rich; print('✓ rich installed')" 2>/dev/null || echo "✗ rich failed"
    python3 -c "import tqdm; print('✓ tqdm installed')" 2>/dev/null || echo "✗ tqdm failed"
    
    echo ""
    echo -e "${GREEN}✅ Installation complete!${NC}"
    echo ""
    echo "Next step: Install ChromeDriver"
    echo "  bash download_chromedriver.sh"
else
    echo ""
    echo -e "${RED}✗${NC} Installation failed"
    exit 1
fi
