import pandas as pd

file_path = "real_estate_report.xlsx"  # Load the Excel file, you can replace with your file path
df = pd.read_excel(file_path, header=None)  # Read the first sheet (no header since the first column holds field names)
print (df)

headers = df.iloc[2:22, 0]  # Extract field names from rows 2 to 21 (20 rows)
all_data = []  # Prepare an empty python list to hold all building data
building_index= 0
while True:
    start_row = building_index * 24 +2  # Each building's data starts every 24 rows, with a 2-row offset
    end_row = start_row + 20  # Each building has 20 rows of data
    data = df.iloc[start_row:end_row, 1:]  # Get the data for the current building (skip the first column)
    if start_row >= len(df):
      break  
    building_index += 1 # Concatenate all building data into a single DataFrame
    all_data.append(data.reset_index(drop=True).T)   #reset data index from 0, and transpose data, add each dataframe to all_data list

all_data1 = pd.concat(all_data, ignore_index=True, axis=0)  #take all one-row df in all_data and combine them into a single df 
all_data1.columns = headers  # Set the header names
unique_address_map = {addr: i+1 for i, addr in enumerate(all_data1['Address'].unique())}
all_data1.insert(0, 'No', all_data1['Address'].map(unique_address_map))

print (all_data1)
all_data1.to_excel("search_results.xlsx")  # # Save to a new Excel file
all_data1.to_csv("search_results.csv")  # # Save to a new Excel file
print(f"{len(all_data1)} buildings, saved to search_results.xlsx and search_results.csv.")

