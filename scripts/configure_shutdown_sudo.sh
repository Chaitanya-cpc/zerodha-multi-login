#!/bin/bash
# Helper script to configure passwordless sudo for shutdown command
# This script will guide you through the safe configuration process

echo "==========================================="
echo "Shutdown Sudo Configuration Helper"
echo "==========================================="
echo ""
echo "This script will help you configure passwordless sudo for the shutdown command."
echo "You will need to enter your password when prompted."
echo ""
read -p "Press Enter to continue..."

USERNAME=$(whoami)
SUDOERS_LINE="$USERNAME ALL=(ALL) NOPASSWD: /sbin/shutdown"

echo ""
echo "The following line will be added to sudoers:"
echo "$SUDOERS_LINE"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Configuration cancelled."
    exit 1
fi

echo ""
echo "Opening sudoers file in safe mode (visudo)..."
echo "You will need to enter your password."
echo ""
echo "Instructions:"
echo "1. Add this line at the END of the file:"
echo "   $SUDOERS_LINE"
echo "2. Save and exit (Ctrl+X, then Y, then Enter for nano)"
echo "3. Or use ':wq' for vim"
echo ""
read -p "Press Enter to open visudo..."

# Use visudo to safely edit sudoers
sudo visudo

echo ""
echo "Verifying configuration..."
if sudo -n shutdown -h +1 2>&1 | grep -q "scheduled"; then
    echo "✅ Passwordless sudo for shutdown is configured correctly!"
    sudo shutdown -c 2>/dev/null  # Cancel the test shutdown
else
    echo "⚠️  Configuration may not be working. Please check manually:"
    echo "   sudo -n shutdown -h +1"
fi

echo ""
echo "Configuration complete!"
