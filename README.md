# ✨ Zerodha Multi-Account Login Automation ✨

Welcome! This project provides a Python script designed to automatically log you into **multiple Zerodha Kite accounts** at the same time using your web browser. It reads the login details you provide in a simple file and opens a separate browser window for each account.

Think of it as a helper that quickly gets you past the login screen for all your accounts, leaving the browser windows open for you to use manually afterwards.

---

## ⚠️🚨 **EXTREMELY IMPORTANT WARNINGS & DISCLAIMERS** 🚨⚠️

Please read these carefully **before** using this script. Your understanding and acceptance of these points are crucial.

1.  **📜 Violation of Terms of Service (HIGH RISK):**

    - Automating logins using scripts like this **is almost certainly against Zerodha's official Terms of Service**.
    - **CONSEQUENCE:** Using this script could lead to Zerodha **suspending or permanently banning** your trading account(s) without warning.
    - **RESPONSIBILITY:** You use this script **entirely at your own risk**. The creator of this script takes **NO responsibility** for any negative consequences, including account loss or financial implications.

2.  **🔒 Security Risk - Handle Credentials With EXTREME Care:**

    - The script reads your **Username, Password, and potentially your 2FA PIN or TOTP Secret Key** from a plain text file (`config/zerodha_credentials.csv`).
    - **DANGER:** Storing sensitive information like this in plain text is **highly insecure**. Anyone who gets access to this file gets access to your Zerodha accounts!
    - **ACTIONS:**
      - Store the `zerodha_credentials.csv` file in a **very secure location** on your computer.
      - Set restrictive file permissions if possible.
      - **NEVER, EVER commit the _real_ `zerodha_credentials.csv` file containing your actual details to Git, GitHub, or any other version control system or public place.** Use the provided `.gitignore` file, which helps prevent this by default.
      - Consider more secure alternatives (like environment variables or system keyrings) if you need higher security, although that would require modifying the script.

3.  **⚙️ Fragile & Requires Maintenance:**

    - This script works by telling the browser exactly where to click and type based on the _current_ design of the Zerodha Kite login pages.
    - **PROBLEM:** Zerodha can (and does) change its website design **at any time without warning**. When they do, this script **WILL BREAK**.
    - **YOUR JOB:** If the script stops working (e.g., can't find a button, doesn't enter details correctly), **you will need to manually update the script**. This involves:
      1.  Using your browser's "Developer Tools" (usually F12) to inspect the elements on the broken login page.
      2.  Finding the new `id` or `XPath` for the elements that changed.
      3.  Editing the `src/auto_login.py` script and updating the `*_LOCATOR` constants defined near the top of the file.
    - This script comes with **no guarantee** of future functionality.

4.  **🔑 Login Assistance Only:**

    - This script **only handles the login process**. It does **NOT** place trades, check your portfolio, manage funds, or perform any other trading actions. It just gets you logged in.

5.  **💻 Resource Usage:**
    - Opening many web browser windows at once uses a significant amount of your computer's **CPU and RAM (memory)**. Performance may degrade if you try to log into a very large number of accounts simultaneously.

---

## ✅ Features

- **Concurrent Logins:** Attempts to log into multiple Zerodha Kite accounts at the same time using Python's threading.
- **CSV Credentials:** Reads account details (Username, Password, 2FA info) from a simple CSV file.
- **2FA Support:** Designed to handle Zerodha's Two-Factor Authentication, supporting both:
  - **TOTP Secrets:** Time-based codes from apps like Google Authenticator or Authy (if you provide the secret key).
  - **Static PINs:** If you use a fixed PIN for 2FA.
- **Persistent Browsers:** Keeps the Chrome browser windows open after the script finishes logging in, allowing you to take over manually.

---

## 🛠️ Prerequisites (What You Need Before Starting)

You'll need a few things installed on your computer:

1.  **🐍 Python:** (Version 3.7 or newer recommended)
    - _Why?_ This is the programming language the script is written in.
    - _Get it:_ [Download Python](https://www.python.org/downloads/)
2.  **🌐 Google Chrome:**
    - _Why?_ The script specifically controls the Chrome web browser.
    - _Get it:_ [Download Google Chrome](https://www.google.com/chrome/)
3.  **✨ Git:**
    - _Why?_ To easily copy (clone) the project files from GitHub to your computer.
    - _Get it:_ [Download Git](https://git-scm.com/downloads)

---

## 🚀 Setup Instructions (Getting Ready to Run)

Follow these steps carefully:

1.  **➡️ Get the Code (Clone):**

    - Open your terminal or command prompt.
    - Navigate to the directory where you want to store the project.
    - Run the `git clone` command (replace the URL with your actual repository URL):
      ```bash
      git clone https://github.com/Chaitanya-cpc/zerodha-multi-login.git
      ```
    - Enter the newly created project directory:
      ```bash
      cd zerodha_automation # Or your project's folder name
      ```

2.  ** izolált Virtual Environment (Highly Recommended):**

    - _Why?_ This creates an isolated space for this project's Python packages, preventing conflicts with other Python projects on your system.
    - Create the environment:
      ```bash
      python3 -m venv venv
      ```
    - Activate the environment:
      - **On macOS / Linux:** `source venv/bin/activate`
      - **On Windows (Command Prompt):** `venv\Scripts\activate`
      - **On Windows (PowerShell):** `venv\Scripts\Activate.ps1` (You might need to adjust execution policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`)
    - You should see `(venv)` appear at the beginning of your terminal prompt.

3.  **📦 Install Required Packages:**

    - While the virtual environment is active, run:
      ```bash
      pip install -r requirements.txt
      ```
    - This reads the `requirements.txt` file and installs the necessary Python libraries (like Selenium and pyotp).

4.  **🚗 Download the Correct ChromeDriver:**

    - This is a separate small program that acts as a bridge between the Selenium script and the Chrome browser. **It MUST match your installed Chrome version.**
    - **Carefully follow the instructions** in the `DRIVERS/README_DRIVERS.md` file within this project. It explains how to find your Chrome version and download the matching ChromeDriver.
    - **Most importantly:** Ensure the downloaded `chromedriver` (or `chromedriver.exe` on Windows) is placed somewhere your system can find it. Adding it to your system's **PATH environment variable** is the recommended way (see the driver README).

5.  **🔑 Configure Your Credentials (The Sensitive Part!):**
    - First, **copy** the example credentials file to create your actual file:
      ```bash
      cp config/zerodha_credentials.csv.example config/zerodha_credentials.csv
      ```
    - Now, **open `config/zerodha_credentials.csv`** with a simple text editor (like Notepad, TextEdit, VS Code, etc. - _not_ Excel, as it can sometimes mess up formatting).
    - You'll see columns: `Username`, `Password`, `PIN/TOTP Secret`.
    - **Replace the placeholder data** with your **actual** Zerodha account details. Add one row for each account you want to log into.
      - `Username`: Your Zerodha Client ID.
      - `Password`: Your Zerodha login password.
      - `PIN/TOTP Secret`:
        - If you use a **static PIN** for 2FA, enter the PIN here.
        - If you use an **authenticator app (TOTP)**, enter the **Secret Key** provided by Zerodha when you set up 2FA (it's usually a long string of letters and numbers). **Do NOT enter the 6-digit code that changes every 30 seconds here.**
    - **➡️ SAVE THE FILE SECURELY! REMEMBER THE SECURITY WARNINGS! DO NOT COMMIT THIS FILE TO GIT!** ⬅️

---

## ▶️ Running the Script

Once setup is complete:

1.  Make sure your **virtual environment is active** (you should see `(venv)` in your prompt).
2.  Make sure you are in the **main project directory** (`zerodha_automation` or similar) in your terminal.
3.  Execute the script using this command:
    ```bash
    python src/auto_login.py
    ```
4.  **Watch the Terminal:** The script will print messages showing its progress: reading credentials, starting threads for each account, navigating, entering details, etc. Look out for any `ERROR` or `WARNING` messages.
5.  **Watch Your Screen:** You should see Chrome browser windows opening, one for each account. The script will attempt to log them in automatically.
6.  **After Completion:** The script will eventually finish in the terminal (it waits for all login attempts). The browser windows **will remain open** because of the "detach" setting. You can now use these logged-in sessions manually.
7.  **Cleanup:** Close the browser windows manually when you are finished.

---

## 🤔 How It Works (A Simple Overview)

1.  **Start:** You run `python src/auto_login.py`.
2.  **Read Credentials:** The script opens `config/zerodha_credentials.csv` and reads the account details for each row you provided.
3.  **Launch Browsers (Threading):** For each account found, the script starts a separate "thread" (like a mini-program running alongside others). Each thread's job is to log in one account.
4.  **Control Chrome (Selenium):** Inside each thread:
    - A new Chrome window is opened, controlled by Selenium.
    - The script tells Chrome to go to the Zerodha login page.
    - It waits for elements (like input boxes and buttons) to appear.
    - It finds the specific elements using "locators" (like `id="userid"`) defined near the top of the script.
    - It types your username and password into the correct boxes.
    - It clicks the login button.
5.  **Handle 2FA:**
    - After the first submit, it waits for the 2FA (PIN/TOTP) input box to appear (again, using a specific locator).
    - If a **TOTP Secret** was found in your CSV, it uses the `pyotp` library to calculate the current 6-digit code.
    - It enters the calculated TOTP code or the static PIN from your CSV into the 2FA input box.
    - It clicks the final submit button.
6.  **Wait & Detach:** The script includes pauses (`time.sleep`) to allow the webpage to load. The main script waits for all login threads to finish (`thread.join()`). The browser windows are launched with a "detach" option, meaning they don't automatically close when the script technically finishes its work.

---

## ❓ Troubleshooting (When Things Go Wrong)

Automation can be tricky. Here are common issues and how to approach them:

- **❓ Script doesn't start / `ModuleNotFoundError`:**

  - Did you activate the virtual environment (`source venv/bin/activate` or similar)?
  - Did you install the requirements (`pip install -r requirements.txt`)?
  - Are you running the command (`python src/auto_login.py`) from the main project directory (`zerodha_automation`)?

- **❓ No Browser Windows Open / ChromeDriver Errors:**

  - This is almost always a **ChromeDriver problem**. Re-read `DRIVERS/README_DRIVERS.md`.
  - **Version Mismatch:** Is your ChromeDriver version _exactly_ matching your installed Google Chrome version?
  - **PATH Issue:** Is the `chromedriver` executable placed in a directory listed in your system's PATH environment variable? This is the most reliable way.
  - **Permissions:** Is the `chromedriver` file executable (on Mac/Linux: `chmod +x path/to/chromedriver`)?

- **❓ `FileNotFoundError` for `zerodha_credentials.csv`:**

  - Did you copy the `.example` file to `config/zerodha_credentials.csv`?
  - Is the file named _exactly_ `zerodha_credentials.csv` inside the `config` folder?
  - Are you running the script from the main project directory?

- **❓ Errors Reading CSV / No Accounts Found:**

  - Check the **exact headers** in `config/zerodha_credentials.csv`: `Username,Password,PIN/TOTP Secret`. Case matters!
  - Make sure there are no weird characters or formatting issues (best edited with a plain text editor).
  - Check the DEBUG logs printed in the terminal when the script starts – it shows how it processes each row.

- **❓ Login Fails - Stops After Username/Password or During 2FA:**

  - **➡️ MOST LIKELY CAUSE: Zerodha Changed Their Website!** ⬅️
  - **ACTION:** You need to update the **Locators**.
    1.  Run the script, let it fail, keep the Selenium browser window open at the point of failure.
    2.  Open **Developer Tools (F12)** in that browser window.
    3.  Use the **Element Inspector** tool to click on the input field or button where the script got stuck (e.g., the username field, password field, PIN/TOTP field, a submit button).
    4.  Find the **HTML `id` attribute** for that element (most reliable). If no ID, find a unique `name` or construct a stable `XPath`.
    5.  Open `src/auto_login.py` in your editor.
    6.  Find the corresponding `*_LOCATOR` constant definition near the **top of the file**.
    7.  **Update the ID, Name, or XPath value** in the constant definition with the correct one you just found.
    8.  Save the file and try running the script again. Repeat if it fails on a different element.
  - **Check Terminal Errors:** Look for specific errors like `TimeoutException` (element not found in time) or `NoSuchElementException` (locator is definitely wrong).

- **❓ TOTP/PIN Entered Incorrectly or Not At All:**
  - **Verify the Locator:** Double, triple-check the `PIN_INPUT_LOCATOR` constant in `src/auto_login.py` using the Developer Tools method described above. Make sure it points to the _actual_ 2FA input field.
  - **Check CSV Value:** Is the `PIN/TOTP Secret` in your CSV file _exactly_ correct, with no extra spaces?
  - **Check Terminal Logs:** Look for the DEBUG messages during the 2FA step: Is the correct secret read? Is the correct 6-digit TOTP generated (if using TOTP)? Is it attempting to send the keys?
  - **Timing:** The script waits 4 seconds after the initial login click. If your connection is very slow, maybe (rarely) this isn't enough. You could try increasing `POST_LOGIN_CLICK_DELAY` slightly more in the constants section.

---

_Disclaimer: This script is provided for educational purposes and convenience. Use responsibly and be fully aware of the associated risks._
