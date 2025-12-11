from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd
pdfmetrics.registerFont(TTFont('HelveticaNeueLTStd-Lt', r"E:\Business\TOCOnnect\Code\Fonts\HelveticaNeueLTStd-Lt.ttf"))
pdfmetrics.registerFont(TTFont('HelveticaNeueLTStd-Th', r"E:\Business\TOCOnnect\Code\Fonts\HelveticaNeueLTStd-Th.ttf"))
pdfmetrics.registerFont(TTFont('GeorgiaBold', r"E:\Business\TOCOnnect\Code\Fonts\GeorgiaBold.ttf"))
brand_color = colors.HexColor("#5B4E46")


def format_field_name(column_name):
    name = column_name.replace('_', ' ').title()      #Convert column names to readable format"""
    replacements = {
        'Sqft': 'sq ft', 'Id': 'ID', 'Sq Ft': 'sq ft',}
    for old, new in replacements.items():
        name = name.replace(old, new)
    return name

def create_property_table_data(row, exclude_columns=None):
    if exclude_columns is None:
        exclude_columns = []
    table_data = [['', '']]
    for col, val in row.items():
        if col in exclude_columns:
            continue
        field_name = format_field_name(col)
        value = 'N/A' if pd.isna(val) else str(val)

        if col.strip().lower() in ['office area', 'total building area', 'typical floor','direct available area','total available area']:
            if pd.isna(val): value = "N/A"
            else:
                try:
                    number = float(str(val).replace(',', ''))  # Remove existing commas first
                    value = f"{number:,.0f}"  # Format with commas, no decimals
                except (ValueError, TypeError):
                    value = str(val)  # Fallback if conversion fails
        
        elif col.strip().lower() in ['direct available rate', 'total available rate']:
            if pd.isna(val): value = "N/A"
            else:
                try:
                    percentage = float(val) * 100  # Convert 0.75 to 75
                    value = f"{percentage:.1f}%"   #.1f = 1 decimal place,  :.2f would give "75.00%" , :.0f would give "75%"
                except (ValueError, TypeError):
                    value = str(val)

        elif col.strip().lower() in ['direct asking rate', 'total additional rate', 'gross rent', 'total additional rent']:
            if pd.isna(val): value = "N/A"
            else:
                try:
                    # Remove any existing $ or commas
                    number = float(str(val).replace(',', '').replace('$', ''))
                    value = f"${number:,.2f}"  # $900,000.00
                except (ValueError, TypeError):
                    value = str(val)
        else:
            value = str(val)

        table_data.append([field_name, value])
    
    return table_data

def create_spaces_table_data(spaces_df):
    
    if spaces_df.empty:
        return [['Space Information', ''], ['No spaces available', '']]
    # Get columns (exclude Property_ID)
    columns = [col for col in spaces_df.columns[2:] if col.lower() != 'property_id']
    
    # Create header
    header = [format_field_name(col) for col in columns]
    table_data = [header]
    # Add each space as a row
    for _, row in spaces_df.iterrows():
        space_row = []   
        for col in columns :
            #'N/A' if pd.isna(row[col]) else str(row[col])     
            if col.strip().lower() in ['size']:
                if pd.isna(row[col]): value = "N/A"
                else:
                    try:
                        number = float(str(row[col]).replace(',', ''))  # Remove existing commas first
                        value = f"{number:,.0f} SF"  # Format with commas, no decimals
                    except (ValueError, TypeError):
                        value = str(row[col])  # Fallback if conversion fails
            elif col.strip().lower() in ['direct asking rate','net rent','total additional rate', 'gross rent', 'additional rent']:
                if pd.isna(row[col]): value = "N/A"
                else:
                    try:
                        number = float(str(row[col]).replace(',', '').replace('$', ''))
                        value = f"${number:,.2f}"  # $900,000.00
                    except (ValueError, TypeError):
                        value = str(row[col])
            else:
                value = "N/A" if pd.isna(row[col]) else str(row[col])
            space_row.append(value)
        
        table_data.append(space_row)
    return table_data

def draw_tables_on_canvas(c, property_data, spaces_data, page_width, page_height):
    # Create Property Table, Table coordinates (column, row) , 
    # (0, 0) = First column, first row , # (-1, 0) = Last column, first row, # (-1, -1) = Last column, last row
    margin = 50
    property_table = Table(property_data, colWidths=[1.5*inch, 2*inch])
    property_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (-1, 0)),  # Merge header cells 
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),  #` Data rows background`
        ('FONTNAME', (0, 1), (0, -1), 'HelveticaNeueLTStd-Lt'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#5B4E46")),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.grey)
    ]))
    
    # Create Spaces Table
    num_columns = len(spaces_data[0]) if spaces_data else 1
    col_width = (page_width - (2 * margin)) / num_columns
    spaces_table = Table(spaces_data, col_width, repeatRows=1)
    spaces_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#5B4E46")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'HelveticaNeueLTStd-Lt'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (1, 1), (-1, -1), colors.HexColor("#5B4E46")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.grey)
    ]))
    
    # Draw Property table at top
    property_table.wrapOn(c, page_width, page_height)
    prop_width, prop_height = property_table.wrap(0, 0)
    property_x = page_width - margin - prop_width  # Right align
    property_y = page_height - margin - prop_height - 20
    property_table.drawOn(c, property_x, property_y)

    # Draw Spaces table at bottom
    available_width = page_width - 2*margin
    spaces_width, spaces_height = spaces_table.wrap(available_width, page_height - 2*margin)
    spaces_x = margin
    spaces_y = margin + 150  # 150 points above bottom margin for page number

    # Safety check - if table too tall, adjust position
    if spaces_y + spaces_height > page_height - 200:
        spaces_y = page_height - 200 - spaces_height
    spaces_table.wrapOn(c, available_width, page_height - 2*margin)
    spaces_table.drawOn(c, spaces_x, spaces_y)

    header_y = spaces_y + spaces_height + 20  # 20pt above table
    c.setFont("HelveticaNeueLTStd-Lt", 20)
    c.setFillColor(colors.HexColor("#FF4C00"))  # Match your color scheme
    c.drawString(spaces_x, header_y, "Available Space")
    

def generate_property_report(output_pdf_path, 
                             properties_excel_path, 
                             spaces_excel_path,
                             property_id_col='Property_ID',
                             properties_sheet=0, 
                             spaces_sheet=0,
                             exclude_property_cols=None,
                             page_size=letter):

    if exclude_property_cols is None:
        exclude_property_cols = [property_id_col]
    elif property_id_col not in exclude_property_cols:
        exclude_property_cols.append(property_id_col)
    
    # Read Excel files
    properties_df = pd.read_excel(properties_excel_path, sheet_name=properties_sheet)
    spaces_df = pd.read_excel(spaces_excel_path, sheet_name=spaces_sheet)
    print(f"\nFound {len(properties_df)} properties")
    print(f"Found {len(spaces_df)} total spaces")
    
    # Validate Property_ID column
    if property_id_col not in properties_df.columns:
        raise ValueError(f"Column '{property_id_col}' not found in properties Excel")
    if property_id_col not in spaces_df.columns:
        raise ValueError(f"Column '{property_id_col}' not found in spaces Excel")
    
    # Create PDF
    c = canvas.Canvas(output_pdf_path, pagesize=page_size)
    page_width, page_height = page_size
    
    # Process each property
    for page_num, (_, property_row) in enumerate(properties_df.iterrows(), 1):
        property_id = property_row[property_id_col]
        
        # Get spaces for this property
        property_spaces = spaces_df[spaces_df[property_id_col] == property_id]

        # Add page header
        c.setFont("HelveticaNeueLTStd-Th", 32)
        c.setFillColor(colors.HexColor("#5B4E46")) 
        c.drawString(50, page_height - 60, f"{property_row['Address']}")
        
        # Create table data
        property_table_data = create_property_table_data(property_row, exclude_property_cols)
        spaces_table_data = create_spaces_table_data(property_spaces)
        
        # Draw tables
        draw_tables_on_canvas(c, property_table_data, spaces_table_data, page_width, page_height)
        
        # Add page number at bottom
        c.setFont("Helvetica", 7)
        c.drawString(page_width - 100, 30, f"Page {page_num} of {len(properties_df)}")
        
        # Create new page if not last property
        if page_num < len(properties_df):
            c.showPage()
    
    # Save PDF
    c.save()
    print(f"Successfully created: {output_pdf_path}")

# Example usage
if __name__ == "__main__":
    generate_property_report(
        output_pdf_path='property_report.pdf',
        properties_excel_path='formatted_buildings.xlsx',
        spaces_excel_path='spaces.xlsx',
        property_id_col='Property_ID',
        properties_sheet='Sheet1',
        spaces_sheet='Sheet1',
        exclude_property_cols= ['Property_ID', 'Internal_Notes','Unnamed: 12', 'Leasing Profile', 'Number of Parking Stalls', 'Parking Ratio (1 per)']
    )







    """
    Generate PDF report from scratch with property and space tables
    
    Args:
        output_pdf_path: Path for output PDF
        properties_excel_path: Excel with property data (1 row per property)
        spaces_excel_path: Excel with spaces data (multiple rows per property)
        property_id_col: Column name to join on (default: 'Property_ID')
        properties_sheet: Sheet name/index for properties Excel
        spaces_sheet: Sheet name/index for spaces Excel
        exclude_property_cols: Columns to exclude from property table
        page_size: PDF page size (default: letter)
    
    Expected Excel 1 (Properties):
        Property_ID | Building_Name | Total_Area | Price    | ...
        PROP-001    | Building A    | 50,000     | $5.5M    | ...
        PROP-002    | Building B    | 35,000     | $3.2M    | ...
    
    Expected Excel 2 (Spaces):
        Property_ID | Space_Name | Area_sqft | Rent_Rate | ...
        PROP-001    | Suite 101  | 2,500     | $25/sqft  | ...
        PROP-001    | Suite 102  | 3,200     | $28/sqft  | ...
        PROP-001    | Suite 103  | 1,800     | $24/sqft  | ...
    """