#!/bin/bash
# Install pip3 without sudo using get-pip.py
# This installs pip to user directory

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📦 Installing pip3 (User Space - No sudo)${NC}"
echo ""

# Check if pip already exists
if command -v pip3 &> /dev/null || python3 -m pip --version &> /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} pip3 is already installed"
    pip3 --version 2>/dev/null || python3 -m pip --version
    exit 0
fi

echo -e "${BLUE}Downloading get-pip.py...${NC}"
cd /tmp

# Download get-pip.py
if command -v curl &> /dev/null; then
    curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
elif command -v wget &> /dev/null; then
    wget -q https://bootstrap.pypa.io/get-pip.py -O get-pip.py
else
    echo -e "${RED}✗${NC} Neither curl nor wget found. Cannot download get-pip.py"
    exit 1
fi

if [ ! -f get-pip.py ]; then
    echo -e "${RED}✗${NC} Failed to download get-pip.py"
    exit 1
fi

echo -e "${GREEN}✓${NC} Downloaded get-pip.py"
echo ""

echo -e "${BLUE}Installing pip3 to user directory...${NC}"
python3 get-pip.py --user

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓${NC} pip3 installed successfully!"
    echo ""
    
    # Add to PATH if needed
    if [ -d "$HOME/.local/bin" ] && [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo -e "${YELLOW}⚠${NC} Adding ~/.local/bin to PATH..."
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        export PATH="$HOME/.local/bin:$PATH"
        echo -e "${GREEN}✓${NC} PATH updated. Run 'source ~/.bashrc' or restart terminal."
        echo ""
    fi
    
    # Verify installation
    echo -e "${BLUE}Verifying pip3 installation...${NC}"
    if command -v pip3 &> /dev/null; then
        pip3 --version
    elif python3 -m pip --version &> /dev/null; then
        python3 -m pip --version
        echo -e "${YELLOW}Note:${NC} Use 'python3 -m pip' instead of 'pip3'"
    fi
    
    echo ""
    echo -e "${GREEN}✅ pip3 installation complete!${NC}"
    echo ""
    echo "Next step: Install dependencies"
    echo "  bash install_dependencies_user.sh"
else
    echo ""
    echo -e "${RED}✗${NC} pip3 installation failed"
    exit 1
fi

# Cleanup
rm -f /tmp/get-pip.py
