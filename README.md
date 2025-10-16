# python scraping data
# Altus Real Estate Listings Scraper

This Python application automates the login process to Altus Data Studio, allows you to specify search criteria, and generates an Excel report of real estate listings. Features include:


## For Users (Using the Executable)

### Requirements

* **Google Chrome Browser:** This program relies on Google Chrome being installed on your computer.

### How to Use

1.  **Download the Program:**
    * Obtain the `AltusReportGenerator.exe` file through the Google Drive link (https://drive.google.com/file/d/1UIO7QisOhVe3YBh9YExGfnaTJ3k24syT/view?usp=sharing). Save it to a convenient location on your computer.

2.  **Run the Program:**
    * Double-click `AltusReportGenerator.exe`. A command prompt window will open.

3.  **Enter Credentials:**
    * The program will prompt you to "Enter your Altus Data Studio username:" and "Enter your Altus Data Studio password:". Type your credentials and press `Enter` after each. **There will be output in the terminal confirming that steps in the background were successfully run, these can be ignored.**

4.  **Follow On-Screen Prompts:**
    * Choose your desired search method ( "General Search", "Search by Specific Building Name", Search by District/Node).
    * Enter any optional search parameters (available area, asking rate) as requested.

5.  **Access Your Report:**
    * Once the data fetching and report generation are complete, an Excel file named `real_estate_report.xlsx` will be created in the **same folder** where you ran `AltusReportGenerator.exe`.

### Troubleshooting for End-Users

* **"WebDriverException" or "Chrome failed to start" / Program closes immediately:**
    * This usually indicates an incompatibility between the `chromedriver.exe` bundled with the executable and your locally installed Google Chrome browser version.
    * **Solution:**
        1.  Check your Google Chrome browser version (Open Chrome -> Click the three dots menu -> `Help` -> `About Google Chrome`).
        2.  Go to the official [ChromeDriver Downloads page](https://googlechromelabs.github.io/chrome-for-testing/) (or an equivalent specific version download page if the main one is too new).
        3.  Download the `chromedriver.exe` file that exactly matches your Chrome browser's version.
        4.  Place this newly downloaded `chromedriver.exe` file **in the same directory as the `AltusReportGenerator.exe`**. When an external `chromedriver.exe` is present in the same directory, it will usually be used instead of the bundled one.
* **"Authentication failed" or "Failed to fetch data":**
    * Double-check that you are entering your Altus Data Studio username and password correctly.
    * The Altus Data Studio website's login process or API might have changed. If this is a persistent issue, the script may need an update.

---

## For Developers (Running from Source)

If you want to modify the script, contribute to the project, or run it directly from its Python source code, follow these steps.

### Requirements

* Python 3.9+ (recommended)
* Google Chrome Browser

### Setup

After Cloning the Repository:


1.  **Install Dependencies:**
    pip install -r requirements.txt
    

2.  **Download ChromeDriver:**
    * Download the `chromedriver.exe` (or `chromedriver` for macOS/Linux) that matches your installed Google Chrome browser version from the official [ChromeDriver Downloads page](https://googlechromelabs.github.io/chrome-for-testing/).
    * Place this `chromedriver.exe` file in the root directory of this project (next to `main.py`).

### Running the Script
1.  From the project root directory, run:
    python main.py
    
2.  The script will prompt you for your Altus Data Studio username and password, and then guide you through the search options.

### Building the Executable (for Developers)

If you make changes to `main.py` and want to build a new executable:

1.  Ensure you have PyInstaller installed (`pip install pyinstaller`).
2.  Make sure `chromedriver.exe` (matching your local Chrome version) is in the project root.
3.  Run the PyInstaller command from your project root:
    ```bash
    python -m PyInstaller --onefile --name AltusReportGenerator --add-data "chromedriver.exe;." .\main.py --clean
    ```
    The executable will be found in the `dist/` folder that is created after the above command is successfully run.

---