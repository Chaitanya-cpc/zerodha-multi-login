# Zerodha Login Bot

An automated tool for logging into multiple Zerodha accounts simultaneously. This tool streamlines the process of accessing multiple trading accounts with a clean interface and efficient login handling.

![Zerodha Login Bot Banner](https://zerodha.com/static/images/logo.svg)

## Features

- **Multi-Account Support**: Log into multiple Zerodha accounts simultaneously
- **TOTP Support**: Automatically generates time-based one-time passwords for 2FA
- **Rich Terminal UI**: Colorful, informative terminal interface with progress tracking
- **Parallel Processing**: All browser windows open simultaneously for faster login
- **Selective Login**: Choose which accounts to log in to via command line or interactive selection
- **Comprehensive Logging**: Detailed logs with timestamps, saved to file for later reference
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

#### Input/Output Options:
- `-c, --credentials PATH`: Path to credentials CSV file
- `--no-log-file`: Disable logging to file
- `--log-dir DIR`: Directory to store log files

#### Display Options:
- `-v, --verbose`: Enable verbose output for detailed logging
- `--debug`: Show detailed error information when issues occur

#### Execution Options:
- `-y, --yes`: Skip confirmation prompt and proceed automatically
- `-p, --parallel`: Run login sessions in parallel (default behavior)
- `--headless`: Run browsers in headless mode (no GUI)

#### Account Selection:
- `--accounts LIST`: Comma-separated list of account usernames to login (e.g. 'AB1234,CD5678')
- `-i, --interactive`: Start in interactive mode to select accounts

### Examples

Login to all accounts:
```bash
python src/auto_login.py
```

Login to specific accounts only:
```bash
python src/auto_login.py --accounts AB1234,CD5678
```

Interactive account selection:
```bash
python src/auto_login.py -i
```

Login with verbose output and custom credentials file:
```bash
python src/auto_login.py -v -c /path/to/your/credentials.csv
```

Automate the process without confirmation:
```bash
python src/auto_login.py -y
```

## Interactive Mode

The interactive mode allows you to select specific accounts to log in to. When you run the script with the `-i` flag, you'll be presented with a menu of options:

1. **All**: Login to all accounts in the credentials file
2. **Specific**: Choose individual accounts by number
3. **Range**: Select a range of accounts by specifying start and end numbers
4. **None**: Exit without logging into any accounts

For example:
```
python src/auto_login.py -i
```

## Logs

Logs are saved to the `logs` directory with timestamped filenames. Each log contains:
- Timestamps for each event
- Account-specific information
- Success/failure status for login attempts

To disable file logging:
```
python src/auto_login.py --no-log-file
```

## Security Considerations

- This tool stores credentials in plaintext. Ensure the CSV file has appropriate file permissions.
- Consider using environment variables or a secure credential manager for production use.
- The script keeps browser windows open for your interaction, so ensure your system is secure.

## Troubleshooting

- If you encounter issues with the Chrome driver, try updating Chrome to the latest version.
- If 2FA fails, verify that your TOTP secret key is correct or try using a PIN instead.
- For detailed debugging, use the `-v` flag for verbose logging.
- Check the log files in the `logs` directory for more information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is provided for educational and convenience purposes only. Use at your own risk and in compliance with Zerodha's terms of service.
