#!/bin/bash
# Helper script to activate venv and run commands

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
    "$@"
else
    echo "✗ Virtual environment not found. Creating it..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo "✓ Virtual environment created and dependencies installed"
    "$@"
fi
