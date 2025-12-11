from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import pandas as pd

#create full report PDF with cover, property pages, summary, and back cover

pdfmetrics.registerFont(TTFont('HelveticaNeueLTStd-Lt', r"E:\Business\TOCOnnect\Code\Fonts\HelveticaNeueLTStd-Lt.ttf"))
pdfmetrics.registerFont(TTFont('HelveticaNeueLTStd-Th', r"E:\Business\TOCOnnect\Code\Fonts\HelveticaNeueLTStd-Th.ttf"))
pdfmetrics.registerFont(TTFont('GeorgiaBold', r"E:\Business\TOCOnnect\Code\Fonts\GeorgiaBold.ttf"))
brand_color = colors.HexColor("#5B4E46")


def format_field_name(column_name):
    name = column_name.replace('_', ' ').title()
    replacements = {'Sqft': 'sq ft', 'Id': 'ID', 'Sq Ft': 'sq ft'}
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
                    number = float(str(val).replace(',', ''))
                    value = f"{number:,.0f}"
                except (ValueError, TypeError):
                    value = str(val)
        
        elif col.strip().lower() in ['direct available rate', 'total available rate']:
            if pd.isna(val): value = "N/A"
            else:
                try:
                    percentage = float(val) * 100
                    value = f"{percentage:.1f}%"
                except (ValueError, TypeError):
                    value = str(val)

        elif col.strip().lower() in ['direct asking rate', 'total additional rate', 'gross rent', 'total additional rent']:
            if pd.isna(val): value = "N/A"
            else:
                try:
                    number = float(str(val).replace(',', '').replace('$', ''))
                    value = f"${number:,.2f}"
                except (ValueError, TypeError):
                    value = str(val)
        else:
            value = str(val)

        table_data.append([field_name, value])
    
    return table_data

def create_spaces_table_data(spaces_df):
    if spaces_df.empty:
        return [['Space Information', ''], ['No spaces available', '']]
    columns = [col for col in spaces_df.columns[2:] if col.lower() != 'property_id']
    
    header = [format_field_name(col) for col in columns]
    table_data = [header]
    
    for _, row in spaces_df.iterrows():
        space_row = []   
        for col in columns:
            if col.strip().lower() in ['size']:
                if pd.isna(row[col]): value = "N/A"
                else:
                    try:
                        number = float(str(row[col]).replace(',', ''))
                        value = f"{number:,.0f} SF"
                    except (ValueError, TypeError):
                        value = str(row[col])
            elif col.strip().lower() in ['direct asking rate','net rent','total additional rate', 'gross rent', 'additional rent']:
                if pd.isna(row[col]): value = "N/A"
                else:
                    try:
                        number = float(str(row[col]).replace(',', '').replace('$', ''))
                        value = f"${number:,.2f}"
                    except (ValueError, TypeError):
                        value = str(row[col])
            else:
                value = "N/A" if pd.isna(row[col]) else str(row[col])
            space_row.append(value)
        
        table_data.append(space_row)
    return table_data

def draw_tables_on_canvas(c, property_data, spaces_data, page_width, page_height):
    margin = 50
    property_table = Table(property_data, colWidths=[1.5*inch, 2*inch])
    property_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (-1, 0)),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
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
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.grey)
    ]))
    
    property_table.wrapOn(c, page_width, page_height)
    prop_width, prop_height = property_table.wrap(0, 0)
    property_x = page_width - margin - prop_width
    property_y = page_height - margin - prop_height - 20
    property_table.drawOn(c, property_x, property_y)

    available_width = page_width - 2*margin
    spaces_width, spaces_height = spaces_table.wrap(available_width, page_height - 2*margin)
    spaces_x = margin
    spaces_y = margin + 150

    if spaces_y + spaces_height > page_height - 200:
        spaces_y = page_height - 200 - spaces_height
    spaces_table.wrapOn(c, available_width, page_height - 2*margin)
    spaces_table.drawOn(c, spaces_x, spaces_y)

    header_y = spaces_y + spaces_height + 20
    c.setFont("HelveticaNeueLTStd-Lt", 20)
    c.setFillColor(colors.HexColor("#FF4C00"))
    c.drawString(spaces_x, header_y, "Available Space")

def draw_cover_page(c, page_width, page_height):
    

    c.setFont("HelveticaNeueLTStd-Th", 32)
    title = "Market Survey"
    title_width = c.stringWidth(title, "HelveticaNeueLTStd-Th", 48)
    c.drawString((page_width - title_width) / 2, page_height / 2 + 50, title)
    
    # Subtitle
    c.setFont("HelveticaNeueLTStd-Lt", 24)
    subtitle = "Building Report 2024"
    subtitle_width = c.stringWidth(subtitle, "HelveticaNeueLTStd-Lt", 24)
    c.drawString((page_width - subtitle_width) / 2, page_height / 2, subtitle)
    
    # Date (optional)
    from datetime import datetime
    date_str = datetime.now().strftime("%B %Y")
    c.setFont("HelveticaNeueLTStd-Lt", 14)
    date_width = c.stringWidth(date_str, "HelveticaNeueLTStd-Lt", 14)
    c.drawString((page_width - date_width) / 2, page_height / 2 - 50, date_str)

def draw_building_summary_page(c, summary_df, page_width, page_height):
    
    margin = 50
    c.setFont("HelveticaNeueLTStd-Th", 32)
    c.setFillColor(colors.HexColor("#5B4E46"))
    c.drawString(margin, page_height - 60, "Building Summary")
    
    # Convert dataframe to table format
    table_data = [summary_df.columns.tolist()]  # Header row
    for _, row in summary_df.iterrows():
        table_data.append(row.tolist())
    
    # Calculate column widths
    available_width = page_width - (2 * margin)
    num_columns = len(table_data[0])
    col_width = available_width / num_columns
    
    # Create table
    summary_table = Table(table_data, colWidths=[col_width] * num_columns)
    summary_table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#5B4E46")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'HelveticaNeueLTStd-Lt'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        
        # Data rows
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#5B4E46")),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        
        # Padding and grid
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    # Position and draw table
    summary_table.wrapOn(c, available_width, page_height - 150)
    table_height = summary_table._height
    table_y = page_height - 120 - table_height
    summary_table.drawOn(c, margin, table_y)

def draw_back_cover(c, page_width, page_height):
    
    logo_path = r"E:\Business\TOCOnnect\Code\Python Practice\Logo.png"  # your logo file
    img = ImageReader(logo_path)
    orig_w, orig_h = img.getSize()
    max_width = 150
    scale = max_width / orig_w
    new_w = orig_w * scale
    new_h = orig_h * scale
    c.drawImage(logo_path, 50, 130, width=new_w, height=new_h, mask="auto")

    contact_lines = ["200-55 University Avenue","Toronto, Ontario M5J 2H7"]
    y_position = 110
    c.setFillColor(colors.grey)
    c.setFont("HelveticaNeueLTStd-Th", 8)
    for line in contact_lines:
        c.drawString(50 , y_position, line)
        y_position -= 10
    
    c.setFillColor(colors.HexColor("#FF4C00"))
    c.drawString(50, 80, "Lennard.com")

    # Footer
    from datetime import datetime
    year = datetime.now().year
    footer = ["Although, the information contained within is from sources believed to be reliable, ",
          "no warranty or representation is made as to its accuracy being subject to errors, ",
          "omissions, conditions, prior lease, withdrawal or other changes without notice and ",
          "same should not be relied upon without independent verification. ",
          f"©{year} Lennard Commercial Real Estate, Brokerage"]
    c.setFillColor(colors.grey)
    c.setFont("HelveticaNeueLTStd-Th", 7)
    y_pos = 60
    for line in footer:
        c.drawString(50, y_pos, line)
        y_pos -= 8

def generate_property_report(output_pdf_path, 
                             properties_excel_path, 
                             spaces_excel_path,
                             property_id_col='Property_ID',
                             properties_sheet=0, 
                             summary_sheet=1,  # NEW: Sheet 2 for summary
                             spaces_sheet=0,
                             exclude_property_cols=None,
                             page_size=letter):

    if exclude_property_cols is None:
        exclude_property_cols = [property_id_col]
    elif property_id_col not in exclude_property_cols:
        exclude_property_cols.append(property_id_col)
    
    # Read Excel files
    print(f"Reading properties from: {properties_excel_path}")
    properties_df = pd.read_excel(properties_excel_path, sheet_name=properties_sheet)
    summary_df = pd.read_excel(spaces_excel_path, sheet_name=summary_sheet)
    spaces_df = pd.read_excel(spaces_excel_path, sheet_name=spaces_sheet)
    
    print(f"\nFound {len(properties_df)} properties")
    print(f"Found {len(summary_df)} rows in summary")
    print(f"Found {len(spaces_df)} total spaces")
    
    # Validate Property_ID column
    if property_id_col not in properties_df.columns:
        raise ValueError(f"Column '{property_id_col}' not found in properties Excel")
    if property_id_col not in spaces_df.columns:
        raise ValueError(f"Column '{property_id_col}' not found in spaces Excel")
    
    # Create PDF
    c = canvas.Canvas(output_pdf_path, pagesize=page_size)
    page_width, page_height = page_size
    
    total_pages = 1 + len(properties_df) + 1 + 1  # Cover + Properties + Summary + Back
    current_page = 1
    
    # 1. COVER PAGE
    print(f"\nGenerating page {current_page}/{total_pages}: Cover Page")
    draw_cover_page(c, page_width, page_height)
    c.showPage()
    current_page += 1
    
    # 3. BUILDING SUMMARY PAGE
    print(f"Generating page {current_page}/{total_pages}: Building Summary")
    draw_building_summary_page(c, summary_df, page_width, page_height)
    c.setFont("Helvetica", 7)
    c.drawString(page_width - 100, 30, f"Page {current_page} of {total_pages}")
    c.showPage()
    current_page += 1

    # 2. PROPERTY PAGES
    for page_num, (_, property_row) in enumerate(properties_df.iterrows(), 1):
        property_id = property_row[property_id_col]
        print(f"Generating page {current_page}/{total_pages}: {property_id}")
        
        property_spaces = spaces_df[spaces_df[property_id_col] == property_id]

        # Add page header
        c.setFont("HelveticaNeueLTStd-Th", 32)
        c.setFillColor(colors.HexColor("#5B4E46")) 
        c.drawString(50, page_height - 60, f"{property_row['Address']}")
        
        # Create and draw tables
        property_table_data = create_property_table_data(property_row, exclude_property_cols)
        spaces_table_data = create_spaces_table_data(property_spaces)
        draw_tables_on_canvas(c, property_table_data, spaces_table_data, page_width, page_height)
        
        # Page number
        c.setFont("Helvetica", 7)
        c.drawString(page_width - 100, 30, f"Page {current_page} of {total_pages}")
        
        c.showPage()
        current_page += 1
    
   
    
    # 4. BACK COVER
    print(f"Generating page {current_page}/{total_pages}: Back Cover")
    draw_back_cover(c, page_width, page_height)
    
    # Save PDF
    c.save()
    print(f"\n✓ Successfully created: {output_pdf_path}")
    print(f"  Total pages: {total_pages}")

# Example usage
if __name__ == "__main__":
    generate_property_report(
        output_pdf_path='property_report.pdf',
        properties_excel_path='formatted_buildings.xlsx',
        spaces_excel_path='spaces.xlsx',
        property_id_col='Property_ID',
        properties_sheet=0,      # Sheet1 - Individual properties
        summary_sheet=1,         # Sheet2 - Building summary table
        spaces_sheet=0,          # Sheet1 in spaces.xlsx
        exclude_property_cols=['Property_ID', 'Internal_Notes','Unnamed: 12', 
                              'Leasing Profile', 'Number of Parking Stalls', 
                              'Parking Ratio (1 per)']
    )