# ChromeDriver Information

This project requires the Selenium WebDriver for Chrome (ChromeDriver) to interact with the Google Chrome browser.

**ChromeDriver is NOT included in this repository due to:**

1.  **Versioning:** ChromeDriver is tied to specific Chrome browser versions. You need the version that matches _your_ installed Chrome.
2.  **Licensing:** Redistributing ChromeDriver might have licensing implications.
3.  **Platform Specificity:** Different operating systems (Windows, macOS, Linux) require different ChromeDriver binaries.

## How to Get ChromeDriver

1.  **Check your Chrome Version:** Open Chrome, go to `Help` > `About Google Chrome`, and note the version number (e.g., `115.0.5790.171`).
2.  **Download ChromeDriver:** Go to the official ChromeDriver download page: [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)
    - Find the version that corresponds to your Chrome browser version.
    - Download the appropriate zip file for your operating system (e.g., `chromedriver_mac64.zip`, `chromedriver_win32.zip`, `chromedriver_linux64.zip`).
3.  **Extract the Executable:** Unzip the downloaded file. You will find an executable file named `chromedriver` (or `chromedriver.exe` on Windows).

## How to Use ChromeDriver with the Script

You have two main options:

1.  **Add to System PATH (Recommended):**

    - Move the extracted `chromedriver` executable to a directory that is already listed in your system's PATH environment variable. Common locations include `/usr/local/bin` on macOS/Linux.
    - Alternatively, add the directory where you placed `chromedriver` to your system's PATH. (Search online for "add directory to PATH" for your specific OS).
    - If ChromeDriver is in your PATH, the script should find it automatically.

2.  **Specify Path in Script (Alternative):**
    - If you prefer not to modify your PATH, you can edit the `src/auto_login.py` script.
    - Locate the line `driver = webdriver.Chrome(service=service, options=options)`.
    - Modify the `service` line just above it to include the full path to your executable:
      ```python
      # Example for macOS/Linux:
      service = Service('/path/to/your/downloaded/chromedriver')
      # Example for Windows:
      # service = Service('C:\\path\\to\\your\\downloaded\\chromedriver.exe')
      ```
    - **Note:** If you modify the script, remember your changes might be overwritten if you update the script from the source repository later.

Verify the setup by opening a terminal and running `chromedriver --version`. If it's in the PATH, it should display the version number.
