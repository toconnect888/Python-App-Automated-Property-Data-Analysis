import pandas as pd
file_path = "real_estate_report.xlsx"
df = pd.read_excel(file_path, header=None)

# The field names are in rows 2 to 21 (20 rows)
headers = df.iloc[2:22, 0].reset_index(drop=True)

# Prepare list for all building data
all_data = []
print(f"There are total {len(df)} rows in your excel file") # Check total number of rows 
# Each building’s data starts every 24 rows, after a 2-row offset
num_buildings = (len(df) - 2) // 24 + 1

for building_index in range(num_buildings):
    start_row = building_index * 24 + 2
    end_row = start_row + 20

    if start_row >= len(df):
        break

    # Extract data (skip the first column with field names)
    data = df.iloc[start_row:end_row, 1:].reset_index(drop=True)

    # Transpose so each building is one row
    data_t = data.T.reset_index(drop=True)
    all_data.append(data_t)

# Combine all buildings
all_data = pd.concat(all_data, ignore_index=True)
all_data.columns = headers  # set field names as columns

unique_address_map = {addr: i+1 for i, addr in enumerate(all_data['Address'].unique())}
all_data.insert(0, 'No', all_data['Address'].map(unique_address_map))

# Save to Excel and CSV
all_data.to_excel("formatted_buildings.xlsx", index=False)
all_data.to_csv("formatted_buildings.csv", index=False)

print(f" {len(all_data)} buildings, saved to formatted_building.xlsx and formatted_buildings.csv")