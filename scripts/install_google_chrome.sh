#!/bin/bash
# Install Google Chrome on Ubuntu

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Installing Google Chrome on Ubuntu                           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check if already installed
if command -v google-chrome >/dev/null 2>&1; then
    echo "✅ Google Chrome is already installed!"
    google-chrome --version
    exit 0
fi

# Download and add Google signing key
echo "📥 Downloading Google Chrome signing key..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -

# Add Google Chrome repository
echo "📦 Adding Google Chrome repository..."
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list >/dev/null

# Update package list
echo "🔄 Updating package list..."
sudo apt update

# Install Google Chrome
echo "📥 Installing Google Chrome..."
sudo apt install -y google-chrome-stable

# Verify installation
if command -v google-chrome >/dev/null 2>&1; then
    echo ""
    echo "✅ Google Chrome installed successfully!"
    google-chrome --version
    echo ""
    echo "🎉 Installation complete!"
else
    echo ""
    echo "⚠️  Installation may have failed. Please check the output above."
    exit 1
fi
