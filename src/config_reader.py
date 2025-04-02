# src/config_reader.py
"""Handles reading and validating credentials from the CSV file."""

import csv
import os
import sys
import traceback
from . import constants # Use relative import for constants

def read_credentials():
    """Reads credentials from the CSV file defined in constants."""
    filepath = constants.CREDENTIALS_FILE
    accounts_data = []
    print(f"Reading credentials from: {filepath}")
    try:
        # Explicitly use utf-8-sig to handle potential BOM
        with open(filepath, mode='r', newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)

            # Check if essential headers exist
            if not reader.fieldnames or not all(header in reader.fieldnames for header in constants.REQUIRED_CSV_HEADERS):
                 print(f"ERROR: Credentials file '{filepath}' is missing required headers ({constants.REQUIRED_CSV_HEADERS}) or is empty.")
                 print(f"Found headers: {reader.fieldnames}")
                 return None # Indicate failure

            for i, row in enumerate(reader):
                # Basic validation: Ensure Username and Password are not empty
                username = row.get(constants.CSV_USERNAME_HEADER, "").strip()
                password = row.get(constants.CSV_PASSWORD_HEADER, "").strip()

                if username and password:
                    # Ensure PIN/TOTP Secret key exists even if empty, for consistency
                    if constants.CSV_2FA_HEADER not in row:
                         row[constants.CSV_2FA_HEADER] = '' # Add empty string if column missing
                    accounts_data.append(row)
                else:
                    print(f"WARNING: Skipping row {i+1} in CSV due to missing Username or Password.")

        if not accounts_data:
             print("ERROR: No valid account credentials found in the CSV file.")
             return None

        print(f"Found {len(accounts_data)} account(s) with valid Username/Password.")
        return accounts_data

    except FileNotFoundError:
        print(f"ERROR: Credentials file not found at '{filepath}'.")
        print("Please ensure the file exists and the path is correct.")
        print(f"Expected location: {os.path.abspath(filepath)}")
        return None # Indicate failure
    except Exception as e:
        print(f"ERROR: Failed to read or parse credentials file: {e}")
        traceback.print_exc()
        return None