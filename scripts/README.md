# 🔧 Scripts Directory

This directory contains all shell scripts for setup, installation, and maintenance.

## 📋 Available Scripts

### Installation Scripts
- **install_setup.sh** - Main installation script (installs pip3 and dependencies, requires sudo)
- **install_pip.sh** - Install pip3 in user space
- **install_dependencies_user.sh** - Install Python dependencies in user space
- **install_google_chrome.sh** - Install Google Chrome on Ubuntu

### Setup & Verification
- **verify_setup.sh** - Verify the entire setup (Python, dependencies, ChromeDriver, etc.)
- **download_chromedriver.sh** - Download and setup ChromeDriver

### Utility Scripts
- **activate_and_run.sh** - Activate virtual environment and run scripts

## 🚀 Usage

All scripts are executable. Run them directly:

```bash
./scripts/install_setup.sh
./scripts/verify_setup.sh
```

## 📝 Notes

- Some scripts require `sudo` privileges (e.g., `install_setup.sh`, `install_google_chrome.sh`)
- User-space installation scripts don't require `sudo` (e.g., `install_dependencies_user.sh`)
- Check individual scripts for specific requirements

## 🔗 Related

- Main README: [../README.md](../README.md)
- Documentation: [../docs/](../docs/)
- Source Code: [../src/](../src/)
