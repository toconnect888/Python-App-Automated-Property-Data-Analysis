import requests
import json
import os
import sys
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time 
from urllib.parse import unquote 
from selenium.common.exceptions import TimeoutException, WebDriverException 
import xlsxwriter
import pandas as pd
# For PDF generation
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors


API_URL = "https://www.altusdatastudio.com/api/v1/search-result/comm_listings/data"

# Function to dynamically get authentication tokens
def get_dynamic_tokens():
    #print("Attempting to log in to Altus Data Studio to get fresh tokens...")

    # --- 1. Get Username and Password from User ---
    username = input("Enter your Altus Data Studio username: ")
    password = input("Enter your Altus Data Studio password: ")

    # --- 2. Initialize WebDriver ---
    # Determine the path to chromedriver.exe when running from PyInstaller executable
    if getattr(sys, 'frozen', False):
        chromedriver_path = os.path.join(sys._MEIPASS, 'chromedriver.exe')
    else:
        chromedriver_path = './chromedriver.exe' # Use './chromedriver' for macOS/Linux

    service = Service(executable_path=chromedriver_path) # Use the dynamically determined path
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') 
    options.add_argument('--disable-gpu') 
    options.add_argument('--no-sandbox') 

    driver = None 
    try:
        #print("running")
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)

        # --- 3. Navigate to Login Page ---
        login_url = "https://www.altusdatastudio.com" 
        driver.get(login_url)

        # --- 4. Locate Credentials & Click Checkbox ---
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[formcontrolname='username']"))).send_keys(username)
        driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='password']").send_keys(password)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.mdc-checkbox__native-control[type='checkbox']"))).click()

        # Locate the login button element
        login_button = None
        try:
            # Using normalize-space() for robust text matching 
            login_button = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space(text())='Log In']")))
            print("Login button located (present in DOM).")

            time.sleep(1)

            driver.execute_script("arguments[0].click();", login_button)
            print("Login button clicked via JavaScript.")

            # Check for alerts (like password save prompts) immediately after click
            try:
                WebDriverWait(driver, 2).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                print(f"ALERT FOUND: {alert.text}")
                alert.accept()
                print("Alert handled.")
            except TimeoutException:
                print("No browser alert present immediately after login click.")

            
            print("Waiting to observe browser behavior after login click (5 seconds)...")
            time.sleep(5)
            print(f"Current URL after login attempt: {driver.current_url}")
           

        except TimeoutException:
            print("ERROR: Login button was not found or not present within the given timeout (15 seconds).")
            raise
        except Exception as e:
            print(f"DEBUG: An unexpected exception occurred during login button click or immediate aftermath: {type(e).__name__}: {e}")
            raise

        print("before crash")
        # --- 5. Wait for Post-Login Page Load / Navigate to Commercial Listings ---
        # Locate and click the "Commercial listings" button
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "tile_comm_listings"))).click()
        print("Commercial listings button clicked.")
        # Wait for the search screen to load by looking for the 'Search' button
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//button[text()='Search']")))
        print("Search page loaded successfully.")
        # --- 6. Extract Tokens ---
        print("Waiting 3 seconds for cookies to settle...")
        time.sleep(3) # Give JavaScript time to set cookies
        auth_header_value = None # Value for the Authorization header, sid cookie as auth token
        cookie_header_parts = [] # Build the full Cookie header string

        # Get all cookies from the browser session
        cookies = driver.get_cookies()


        # Iterate through cookies to find 'sid' and build the full cookie string
        for c in cookies:
            cookie_name_clean = str(c['name']).strip() 
            cookie_header_parts.append(f"{c['name']}={c['value']}")
            
            if cookie_name_clean == 'sid':
                auth_header_value_decoded = unquote(c['value'])
                # break 
            else:
                pass

        cookie_header_string = "; ".join(cookie_header_parts)

        if not auth_header_value_decoded:
            print("WARNING: AUTH_TOKEN (sid cookie value) not found for Authorization header. Cannot proceed.")
            return None

        if not cookie_header_string: 
            print("WARNING: Cookie header is empty. Cannot proceed.")
            return None

        return {"AUTH_HEADER_VALUE": auth_header_value_decoded, "COOKIE_HEADER": cookie_header_string}

    except Exception as e: 
        print(f"An error occurred during automated login: {e}")
        return None
    finally: 
        if driver:
            driver.quit() 

# Prompts the user to input search parameters for the query, returns dictionary of paramters to request from API
def get_user_search_parameters():
    # Required search parameters in API response
    params = {}
    print("Select a search method:")
    print("1: Search by Specific Building Name")
    print("2: Search by Office Node and District ")
    print("3: General Search") # This will now use default Office, Ontario, GTA

    search_method_choice = input("Enter the number of your choice: ")

    if search_method_choice == '1':
        # Search by Building Name/Address
        building_name = input("Enter Building Name or Address: ")
        params['BUILDING_NAME'] = building_name
        # Automatically set Sector to Office for address search
        params['SECTOR'] = "Office"
        params['saveLayoutProductType'] = "Office"
        # Skip location/geolevel parameters for this search type

    elif search_method_choice == '2':
        # Search by Office Node/District (as implemented before)
        # Automatically set Sector and Province for this search method
        params['SECTOR'] = "Office"
        params['saveLayoutProductType'] = "Office"
        params['PROVINCE'] = ["Ontario"]  # Send province as a list
        params['MARKET'] = ["GTA"]
        params['GEOLEVEL1'] = ["Greater Toronto"]

        # Hardcoded lists of Nodes and Districts
        office_nodes = {
            "1": "Downtown Toronto",
            "2": "Midtown Toronto",
            "3": "Toronto East",
            "4": "Toronto North",
            "5": "Toronto West"
        }

        office_districts = {
            "Downtown Toronto": {
                "1": "Downtown East", "2": "Downtown North", "3": "Downtown South",
                "4": "Downtown West", "5": "Financial Core", "6": "King and Dufferin"
            },
            "Midtown Toronto": {
                "1": "Bloor", "2": "Eglinton", "3": "St. Clair"
            },
            "Toronto East": {
                "1": "Consumers Road", "2": "Don Mills and Eglinton", "3": "Highway 404 and 407",
                "4": "Highway 404 and Steeles", "5": "Pickering", "6": "Scarborough"
            },
            "Toronto North": {
                "1": "Downsview", "2": "Dufferin and Finch", "3": "North Yonge",
                "4": "Richmond Hill", "5": "Vaughan", "6": "Yorkdale"
            },
            "Toronto West": {
                "1": "Airport Corporate Centre", "2": "Airport East", "3": "Airport North",
                "4": "Airport West", "5": "Bloor and Islington", "6": "Brampton", "7": "Burlington"
            }
        }

        # Prompt user to select an Office Node - Goes straight to this
        print("\nSelect an Office Node:")
        for key, value in office_nodes.items():
            print(f"{key}: {value}")

        while True:
            node_choice = input("Enter the number of the Office Node: ")
            selected_node_name = office_nodes.get(node_choice)
            if selected_node_name:
                params['GEOLEVEL2O'] = [selected_node_name] # Save the selected office node
                break
            else:
                print("Invalid selection. Please enter a valid number.")

        # Prompt user to select an Office District based on the selected Node
        print(f"\nSelect an Office District within {selected_node_name}:")
        districts_in_node = office_districts.get(selected_node_name, {})
        for key, value in districts_in_node.items():
            print(f"{key}: {value}")

        while True:
            district_choice = input("Enter the number of the Office District: ")
            selected_district_name = districts_in_node.get(district_choice)
            if selected_district_name:
                params['GEOLEVEL3O'] = [selected_district_name] # Save the selected district
                break
            else:
                print("Invalid selection. Please enter a valid number.")

    elif search_method_choice == '3':
        # General Search - Automatically set default location/province/sector
        params['SECTOR'] = "Office"
        params['saveLayoutProductType'] = "Office"
        params['PROVINCE'] = ["Ontario"]  
        params['MARKET'] = ["GTA"]   
        # Skip GEOLEVEL parameters in this case

    else:
        print("Invalid search method choice. Exiting.")
        return None 

    # These parameters are common to all search types based on API payloads seen
    params['includeContiguousSpaces'] = True
    params['includeMinimumDivisibleArea'] = True
    params['size'] = 500 

    # Optional search parameters (available area and asking rate) - These apply to all search types
    print("\nOptional search parameters (leave blank to skip):")

    # Optional search parameter (available area) 
    available_area = input("Enter available area (sq. ft.) (e.g., 1000-5000): ")
    if available_area:
        if '-' in available_area:
            areas = available_area.split('-')
            if len(areas) == 2:
                try:
                    from_area = float(areas[0])
                    to_area = float(areas[1])
                    params['AvailableArea'] = {'from': from_area, 'to': to_area}
                except ValueError:
                    print("Invalid available area range format. Please use NUMBER-NUMBER or just a NUMBER.")
            else:
                print("Invalid available area range format. Please use NUMBER-NUMBER or just a NUMBER.")
        else:
            try:
                single_area = float(available_area)
                params['AvailableArea'] = {'from': single_area, 'to': single_area}
            except ValueError:
                print("Invalid available area format. Please use NUMBER-NUMBER or just a NUMBER.")

    # Optional search parameter (asking rate) 
    asking_rate = input("Enter asking rate ($/sq. ft.) (e.g., 20-30 or just 25): ")
    if asking_rate:
        if '-' in asking_rate:
            rates = asking_rate.split('-')
            if len(rates) == 2:
                try:
                    from_rate = float(rates[0])
                    to_rate = float(rates[1])
                    params['AskingRatePortion'] = {'from': from_rate, 'to': to_rate} 
                except ValueError:
                    print("Invalid asking rate range format. Please use NUMBER-NUMBER or just a NUMBER.")
            else:
                print("Invalid asking rate range format. Please use NUMBER-NUMBER or just a NUMBER.")
        else:
            try:
                single_rate = float(asking_rate)
                params['AskingRatePortion'] = {'from': single_rate, 'to': single_rate} 
            except ValueError:
                print("Invalid asking rate format. Please use NUMBER-NUMBER or just a NUMBER.")

    return params

    
# Sends a POST request to Altus API, returns JSON response data
def fetch_real_estate_data(search_parameters, fetched_tokens): 

    initial_timeout = 15
    max_retries = 3

    AUTH_HEADER_VALUE = fetched_tokens.get("AUTH_HEADER_VALUE")
    COOKIE_HEADER = fetched_tokens.get("COOKIE_HEADER")

    if not AUTH_HEADER_VALUE or not COOKIE_HEADER:
        print("Authentication tokens (AUTH_HEADER_VALUE or COOKIE_HEADER) are missing or invalid after dynamic login attempt. Cannot proceed with data fetch.")
        return None

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd", 
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": AUTH_HEADER_VALUE, # Use raw sid value
        # "Connection": "keep-alive",
        # "Content-Length": "319", 
        "Content-Type": "application/json",
        "Cookie": COOKIE_HEADER, # Use the full Cookie string
        "Host": "www.altusdatastudio.com",
        "Origin": "https://www.altusdatastudio.com",
        "Referer": "https://www.altusdatastudio.com/search", 
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua": "\"Google Chrome\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?1", 
        "sec-ch-ua-platform": "\"Android\"" 
    }

    timeout = initial_timeout 
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, json=search_parameters, timeout=timeout)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error during API request (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                timeout *= 2
                print(f"Retrying in {timeout} seconds...")
            else:
                print("Max retries reached. Could not fetch data.")
                return None

# Generates an Excel report named 'real_estate_report.xlsx' based on the fetched building data
def create_excel_report(buildings):
    workbook = xlsxwriter.Workbook('real_estate_report.xlsx')
    worksheet = workbook.add_worksheet()

    # Formatting for left alignment in a cell
    left_align_format = workbook.add_format({'align': 'left'})
    # Add bold format for titles
    bold_format = workbook.add_format({'bold': True, 'align': 'left'})
    # Format for percentage values
    percentage_format = workbook.add_format({'num_format': '0.00%', 'align': 'left'})
    
    # Column headers for each building table - Updated to 19 fields
    headers = [
        "Building Name",
        "Address", # Corrected typo
        "Leasing District",
        "Node/Municipality",
        "Total Building Area",
        "Office Area",
        "Number of Floors",
        "Typical Floor",
        "Number of Parking Stalls",
        "Building Type",
        "Year Built",
        "Parking Ratio (1 per)", # Building Profile ends here
        "Direct Available Area", # Leasing Profile begins here
        "Direct Available Rate", 
        "Total Available Area",
        "Total Available Rate", 
        "Direct Asking Rate", # Mapping to ASKING_RATE_RATE_MIN_PORTION
        "Total Additional Rent", # Mapping to TOTAL_ADDITIONAL_RENT_PORTION
        "Gross Rent" 
    ]

    building_profile_end_index = 11 

    start_row = 0 # Tracks the row position in Excel for the start of the current building's entry
    for building_index, building in enumerate(buildings.get('source_record', [])):
        # Define variables with default values N/A
        building_name_to_write = 'N/A'
        address_to_write = 'N/A'
        leasing_district_to_write = 'N/A'
        node_municipality_to_write = 'N/A'
        total_building_area_to_write = 'N/A'
        office_area_to_write = 'N/A'
        number_of_floors_to_write = 'N/A'
        typical_floor_to_write = 'N/A'
        number_of_parking_stalls_to_write = 'N/A'
        building_type_to_write = 'N/A'
        year_built_to_write = 'N/A'
        parking_ratio_to_write = 'N/A'
        direct_available_area_to_write = 'N/A'
        total_available_area_to_write = 'N/A'
        direct_asking_rate_to_write = 'N/A'
        total_additional_rent_to_write = 'N/A'
        gross_rent_to_write = 'N/A'

        # Variables to hold values for calculations
        total_building_area_value = None
        direct_available_area_value = None
        total_available_area_value = None


        try:
            # Set column widths 
            worksheet.set_column(0,0,25)
            worksheet.set_column(1,1,25)

            # Extract raw data for all fields
            building_name_raw = building.get('BUILDING_NAME')
            address_raw = building.get('ADDRESS')
            leasing_district_raw = building.get('GEOLEVEL2')
            node_municipality_raw = building.get('GEOLEVEL3')
            total_building_area_raw = building.get('TOTAL_BUILDING_AREA')
            office_area_raw = building.get('TOTAL_OFFICE_AREA')
            number_of_floors_raw = building.get('NUMBER_OF_FLOORS')
            typical_floor_raw = building.get('TYPICAL_FLOOR')
            number_of_parking_stalls_raw = building.get('NUMBER_OF_PARKING_STALLS')
            building_type_raw = building.get('BuildingType')
            year_built_raw = building.get('YEAR_BUILT')
            parking_ratio_raw = building.get('PARKING_RATIO')
            direct_available_area_raw = building.get('DIRECT_AVAILABLE_AREA')
            total_available_area_raw = building.get('TOTAL_AVAILABLE_AREA')

            # Extracts rent values from portions/building level
            portions = building.get('PORTIONS', [])
            first_portion = portions[0] if portions else {}
            total_additional_rent_portion_raw = building.get('TOTAL_ADDITIONAL_RENT_PORTION', first_portion.get('TOTAL_ADDITIONAL_RENT_PORTION'))
            asking_rate_min_portion_raw = first_portion.get('ASKING_RATE_MIN_PORTION') # Used for Direct Asking Rate


            # Assign values to the _to_write variables, using 'N/A' if source data is missing
            building_name_to_write = building_name_raw if building_name_raw is not None and building_name_raw != '' else 'N/A'
            address_to_write = address_raw if address_raw is not None and address_raw != '' else 'N/A'
            leasing_district_to_write = leasing_district_raw if leasing_district_raw is not None and leasing_district_raw != '' else 'N/A'
            node_municipality_to_write = node_municipality_raw if node_municipality_raw is not None and node_municipality_raw != '' else 'N/A'
            office_area_to_write = office_area_raw if office_area_raw is not None and office_area_raw != '' else 'N/A'
            number_of_floors_to_write = number_of_floors_raw if number_of_floors_raw is not None and number_of_floors_raw != '' else 'N/A'
            typical_floor_to_write = typical_floor_raw if typical_floor_raw is not None and typical_floor_raw != '' else 'N/A'
            number_of_parking_stalls_to_write = number_of_parking_stalls_raw if number_of_parking_stalls_raw is not None and number_of_parking_stalls_raw != '' else 'N/A'
            building_type_to_write = building_type_raw if building_type_raw is not None and building_type_raw != '' else 'N/A'
            year_built_to_write = year_built_raw if year_built_raw is not None and year_built_raw != '' else 'N/A'
            parking_ratio_to_write = parking_ratio_raw if parking_ratio_raw is not None and parking_ratio_raw != '' else 'N/A'


            # Convert area values to numbers for calculation
            if total_building_area_raw is not None and total_building_area_raw != '':
                try:
                    total_building_area_value = float(total_building_area_raw)
                    total_building_area_to_write = total_building_area_value
                except ValueError:
                    pass

            if direct_available_area_raw is not None and direct_available_area_raw != '':
                try:
                    direct_available_area_value = float(direct_available_area_raw)
                    direct_available_area_to_write = direct_available_area_value
                except ValueError:
                    pass 

            if total_available_area_raw is not None and total_available_area_raw != '':
                try:
                    total_available_area_value = float(total_available_area_raw)
                    total_available_area_to_write = total_available_area_value
                except ValueError:
                    pass 

            # Calculate Direct Available Rate
            direct_available_rate_to_write = 'N/A'
            if direct_available_area_value is not None and total_building_area_value is not None and total_building_area_value != 0:
                 direct_available_rate_to_write = (direct_available_area_value / total_building_area_value)

            # Calculate Total Available Rate
            total_available_rate_to_write = 'N/A'
            if total_available_area_value is not None and total_building_area_value is not None and total_building_area_value != 0:
                 total_available_rate_to_write = (total_available_area_value / total_building_area_value)


            # Asking rate and additional rent calculations
            direct_asking_rate_to_write = 'N/A'
            total_additional_rent_to_write = 'N/A'
            gross_rent_to_write = 'N/A'
            asking_rate_value = None
            additional_rent_value = None

            if asking_rate_min_portion_raw is not None and asking_rate_min_portion_raw != '':
                try:
                    asking_rate_value = float(asking_rate_min_portion_raw)
                    direct_asking_rate_to_write = asking_rate_value
                except ValueError:
                    pass 
            if total_additional_rent_portion_raw is not None and total_additional_rent_portion_raw != '':
                 try:
                    additional_rent_value = float(total_additional_rent_portion_raw)
                    total_additional_rent_to_write = additional_rent_value
                 except ValueError:
                    pass 

            # Calculate gross rent only if both components are valid numbers
            if asking_rate_value is not None and additional_rent_value is not None:
                gross_rent_value = asking_rate_value + additional_rent_value
                gross_rent_to_write = gross_rent_value
            elif direct_asking_rate_to_write == 'N/A' or total_additional_rent_to_write == 'N/A':
                 gross_rent_to_write = 'N/A'
            elif asking_rate_value is not None or additional_rent_value is not None:
                 gross_rent_to_write = 'N/A'
            else:
                 gross_rent_to_write = 'N/A'


            # List of values to write, in the order of headers
            values_to_write = [
                building_name_to_write,
                address_to_write,
                leasing_district_to_write,
                node_municipality_to_write,
                total_building_area_to_write,
                office_area_to_write,
                number_of_floors_to_write,
                typical_floor_to_write,
                number_of_parking_stalls_to_write,
                building_type_to_write,
                year_built_to_write,
                parking_ratio_to_write,
                direct_available_area_to_write,
                direct_available_rate_to_write, 
                total_available_area_to_write,
                total_available_rate_to_write, 
                direct_asking_rate_to_write,
                total_additional_rent_to_write,
                gross_rent_to_write
            ]

            # --- Writing Headers and Values with Titles and Gap ---
            current_row = start_row 

            # Write "Building Profile" title
            worksheet.write(current_row, 0, "Building Profile", bold_format if 'bold_format' in locals() else left_align_format)
            current_row += 1 
            # Write Building Profile fields (first 12)
            for i in range(building_profile_end_index + 1): # Write up to and including index 11
                 worksheet.write(current_row, 0, headers[i], left_align_format)
                 # Use percentage format for the calculated rate fields
                 # Check and apply percentage format for Direct Available Rate
                 if headers[i] == "Direct Available Rate":
                      if isinstance(values_to_write[i], (int, float)):
                         worksheet.write(current_row, 1, values_to_write[i], percentage_format if 'percentage_format' in locals() else left_align_format)
                      else: 
                         worksheet.write(current_row, 1, values_to_write[i], left_align_format)
                 elif headers[i] == "Total Available Rate":
                      if isinstance(values_to_write[i], (int, float)):
                         worksheet.write(current_row, 1, values_to_write[i], percentage_format if 'percentage_format' in locals() else left_align_format)
                      else: 
                         worksheet.write(current_row, 1, values_to_write[i], left_align_format)
                 else:
                    worksheet.write(current_row, 1, values_to_write[i], left_align_format)
                 current_row += 1 

            # Gap row
            current_row += 1

            worksheet.write(current_row, 0, "Leasing Profile", bold_format if 'bold_format' in locals() else left_align_format)
            current_row += 1 

            # Write Leasing Profile fields (last 7)
            for i in range(building_profile_end_index + 1, len(headers)): 
                 worksheet.write(current_row, 0, headers[i], left_align_format)
                 if headers[i] == "Direct Available Rate":
                      if isinstance(values_to_write[i], (int, float)):
                         worksheet.write(current_row, 1, values_to_write[i], percentage_format if 'percentage_format' in locals() else left_align_format)
                      else: 
                         worksheet.write(current_row, 1, values_to_write[i], left_align_format)
                 elif headers[i] == "Total Available Rate":
                      if isinstance(values_to_write[i], (int, float)):
                         worksheet.write(current_row, 1, values_to_write[i], percentage_format if 'percentage_format' in locals() else left_align_format)
                      else: 
                         worksheet.write(current_row, 1, values_to_write[i], left_align_format)
                 else:
                    worksheet.write(current_row, 1, values_to_write[i], left_align_format)
                 current_row += 1 

            start_row = current_row + 2
            worksheet.set_column(0,0,25)
            worksheet.set_column(1,1,25)


        except Exception as e:
            print(f"Error processing building: {building_name_to_write}. Error: {e}")
            # To prevent infinite loop if an error occurs but start_row is not updated
            start_row += len(headers) + 4 
        # if building_index >= 29: # Limit to 30 buildings
        #     break

    workbook.close()
    print("Real estate report generated successfully: real_estate_report.xlsx")





# Main program execution
if __name__ == "__main__":
    auth_tokens = get_dynamic_tokens() # Get tokens dynamically
    print("Authentication tokens:", auth_tokens)  # Debug print to verify token
    if auth_tokens:
        search_params = get_user_search_parameters()
        if search_params:
            print("Fetching real estate data...")
            # Ensure fetch_real_estate_data is called with auth_tokens
            buildings_data = fetch_real_estate_data(search_params, auth_tokens)
            if buildings_data:
                print("Creating Excel report...")
                create_excel_report(buildings_data)
               # export_json_variable_to_pdf(buildings=buildings_data,pdf_path=r"E:\Business\TOCOnnect\Code\Python Practice\building_report.pdf")
           
            else:
                print("Failed to fetch data or no data found.")
        else:
            print("Search parameters not provided.")
    else:
        print("Authentication failed. Cannot proceed with data fetching.")



# ---- Run the function ----
