# Zerodha Login Bot

An automated tool for logging into multiple Zerodha accounts simultaneously. This tool streamlines the process of accessing multiple trading accounts with a clean interface and efficient login handling.

![Zerodha Login Bot Banner](https://zerodha.com/static/images/logo.svg)

## Features

- **Multi-Account Support**: Log into multiple Zerodha accounts simultaneously
- **TOTP Support**: Automatically generates time-based one-time passwords for 2FA
- **Rich Terminal UI**: Colorful, informative terminal interface with progress tracking
- **Parallel Processing**: Option to run login sessions in parallel for faster execution
- **Error Handling**: Comprehensive error detection with automatic screenshots
- **Headless Mode**: Option to run in headless mode for automated scenarios

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/zerodha-login-bot.git
   cd zerodha-login-bot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a CSV file with your Zerodha credentials in the `config` directory. The default file is `config/zerodha_credentials.csv`.

The CSV should have the following headers:
- `Username`: Your Zerodha user ID
- `Password`: Your Zerodha password
- `PIN/TOTP Secret`: Either your static PIN or your TOTP secret key

Example CSV:
```csv
Username,Password,PIN/TOTP Secret
AB1234,your_password,123456
CD5678,another_password,JBSWY3DPEHPK3PXP
```

## Usage

Run the script with:

```bash
python src/auto_login.py
```

### Command-line Options

- `-c, --credentials`: Path to credentials CSV file (default: config/zerodha_credentials.csv)
- `-v, --verbose`: Enable verbose output for detailed logging
- `-y, --yes`: Skip confirmation prompt and proceed automatically
- `-p, --parallel`: Run login sessions in parallel instead of sequentially
- `--headless`: Run browsers in headless mode (no GUI)

### Examples

Login with custom credentials file:
```bash
python src/auto_login.py -c /path/to/your/credentials.csv
```

Login with verbose output and parallel processing:
```bash
python src/auto_login.py -v -p
```

Automate the process without confirmation:
```bash
python src/auto_login.py -y
```

## Security Considerations

- This tool stores credentials in plaintext. Ensure the CSV file has appropriate file permissions.
- Consider using environment variables or a secure credential manager for production use.
- The script keeps browser windows open for your interaction, so ensure your system is secure.

## Troubleshooting

- If you encounter issues with the Chrome driver, try updating Chrome to the latest version.
- If 2FA fails, verify that your TOTP secret key is correct or try using a PIN instead.
- For detailed debugging, use the `-v` flag to enable verbose logging.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is provided for educational and convenience purposes only. Use at your own risk and in compliance with Zerodha's terms of service.
