from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import Paragraph, Image, Table, TableStyle, SimpleDocTemplate, Spacer , PageBreak
from reportlab.pdfbase.pdfmetrics import stringWidth
import pandas as pd
from geopy.geocoders import Nominatim
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import folium
import pdfkit
from PIL import Image as PILImage
from io import BytesIO
import base64
import os
import time
from reportlab.platypus import Image as RLImage
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from selenium.common.exceptions import TimeoutException
from PIL import Image
from reportlab.lib.pagesizes import letter, landscape
#create full report PDF with cover, property pages, summary, and back cover
pdfmetrics.registerFont(TTFont('HelveticaNeueLTStd-Lt', r"E:\Business\TOCOnnect\Code\Fonts\HelveticaNeueLTStd-Lt.ttf"))
pdfmetrics.registerFont(TTFont('HelveticaNeueLTStd-Th', r"E:\Business\TOCOnnect\Code\Fonts\HelveticaNeueLTStd-Th.ttf"))
pdfmetrics.registerFont(TTFont('GeorgiaBold', r"E:\Business\TOCOnnect\Code\Fonts\GeorgiaBold.ttf"))
brand_color = colors.HexColor("#5B4E46")
styles = getSampleStyleSheet()
normal = styles["Normal"]
header_style = ParagraphStyle('header_style',parent=normal,textColor=colors.white,fontName='HelveticaNeueLTStd-Th',fontSize=10,alignment=0)

def format_field_name(column_name):
    name = column_name.replace('_', ' ').title()
    replacements = {'Rba': 'Total Building Area', 'Rent/Sf/Yr': 'Net Rent', 'Total Available Space (Sf)' : 'Total Available Space'}
    for old, new in replacements.items():
        name = name.replace(old, new)
    return name

def create_property_table_data(row, exclude_columns=None):
    skip_cols = {'Percent Leased', 'Possession'}  # columns to skip
    if exclude_columns is None:
        exclude_columns = []
    table_data = [['', '']]

    for col, val in row.items():
        if col in exclude_columns or col in skip_cols:
            continue
        field_name = format_field_name(col)
        value = '-' if pd.isna(val) else str(val)

        if col.strip().lower() in ['office area', 'total building area', 'typical floor','direct available area','total available area', 'typical floor size','total available space (sf)', 'direct available space','rba']:
            if pd.isna(val): value = "-"
            else:
                try:
                    number = float(str(val).replace(',', ''))
                    value = f"{number:,.0f} SF"
                except (ValueError, TypeError):
                    value = str(val)
        
        elif col.strip().lower() in ['direct available rate', 'total available rate']:
            if pd.isna(val): value = "-"
            else:
                try:
                    percentage = float(val) * 100
                    value = f"{percentage:.1f}%"
                except (ValueError, TypeError):
                    value = str(val)

        elif col.strip().lower() in ['direct asking rate', 'total additional rate', 'gross rent', 'total additional rent']:
            if pd.isna(val): value = "-"
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
    if spaces_df.empty:  #check if no data in table, return no spaces available, if data exists, proceed continues
        return [['Space Information', ''], ['No spaces available', '']]

    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    normal.fontName = "HelveticaNeueLTStd-Lt"
    normal.fontSize = 10
    normal.leading = 12 

    # skip certain columns
    skip_cols = ['', 'Possession']  # if you don't want these columns, put column names here
    colomns = [col for col in spaces_df.columns if col not in skip_cols]
    spaces_df = spaces_df[colomns]

    columns = [col for col in spaces_df.columns[2:] if col.lower() != 'property_id']
    header = [Paragraph(format_field_name(col), header_style) for col in columns]
    table_data = [header]
    
    for _, row in spaces_df.iterrows():
        space_row = []   
        for col in columns:
            if col.strip().lower() in ['size']:
                if pd.isna(row[col]): value = "-"
                else:
                    try:
                        number = float(str(row[col]).replace(',', ''))
                        value = f"{number:,.0f}"
                    except (ValueError, TypeError):
                        value = str(row[col])
            elif col.strip().lower() in ['direct asking rate','net rent','total additional rate', 'gross rent', 'additional rent']:
                if pd.isna(row[col]): value = "-"
                else:
                    try:
                        number = float(str(row[col]).replace(',', '').replace('$', ''))
                        value = f"${number:,.2f}"
                    except (ValueError, TypeError):
                        value = str(row[col])
            else:
                value = "N/A" if pd.isna(row[col]) else str(row[col])
            space_row.append(Paragraph(value, normal))
        
        table_data.append(space_row)
    return table_data

def draw_tables_on_canvas(c, property_data, spaces_data, page_width, page_height):
    margin = 50
    property_table = Table(property_data, colWidths=[1.5*inch, 2*inch])
    property_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (-1, 0)),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'HelveticaNeueLTStd-Lt'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#5B4E46")),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.grey)
    ]))
    
    num_columns = len(spaces_data[0]) if spaces_data else 1
    col_width = (page_width - (2 * margin)) / num_columns
    spaces_table = Table(spaces_data, col_width, repeatRows=1)
    spaces_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#5B4E46")), #header background
        #('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'HelveticaNeueLTStd-Lt'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (1, 1), (-1, -1), colors.HexColor("#5B4E46")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    property_table.wrapOn(c, page_width, page_height)
    prop_width, prop_height = property_table.wrap(0, 0)
    property_x = page_width - margin - prop_width
    property_y = page_height - margin - prop_height - 40
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

def get_group_row_spans(df, group_col, span_cols):
    """
    ('SPAN', (1, 3), (1, 9)),understands as: “Merge column 1 from row 3 to row 9.”
    """
    spans = []
    start_row = 1  # table row index (0 is header)
    current_val = None

    for i, val in enumerate(df[group_col]):
        table_row = i + 1  # offset for header

    #     if val != current_val:
    #         if current_val is not None and table_row - start_row > 1:
    #             for col_idx in span_cols:
    #                 spans.append(
    #                     ('SPAN', (col_idx, start_row), (col_idx, table_row - 1))
    #                 )
    #         current_val = val
    #         start_row = table_row

    # # handle last group
    # if current_val is not None and table_row - start_row > 1:
    #     for col_idx in span_cols:
    #         spans.append(
    #             ('SPAN', (col_idx, start_row), (col_idx, table_row))
    #             )

        if val != current_val:
            if current_val is not None:
                end_row = table_row - 1
                if end_row >= start_row:  # include even 1-row spans
                    for col_idx in span_cols:
                        spans.append(('SPAN', (col_idx, start_row), (col_idx, end_row)))
            current_val = val
            start_row = table_row

    # handle last group
        end_row = table_row
        if current_val is not None and end_row >= start_row:
            for col_idx in span_cols:
                spans.append(('SPAN', (col_idx, start_row), (col_idx, end_row)))

    return spans

def draw_building_summary_page(c, summary_df, page_width, page_height, png_path):
    margin = 50  # 50 points
    top_margin = 100        # title + spacing
    bottom_margin = 60
    map_height = page_height * 0.45  # map takes ~45% of page
    available_height = page_height - top_margin - bottom_margin 

    c.setFont("HelveticaNeueLTStd-Th", 32)
    c.setFillColor(colors.HexColor("#A49389"))
    c.drawString(margin, page_height - 60, "Building Summary")
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    normal.fontName = "HelveticaNeueLTStd-Lt"
    normal.fontSize = 10

    skip_cols = ['Door', 'Door.1', 'Possession']  
    # skip_cols = ['']
    colomns = [col for col in summary_df.columns if col not in skip_cols]
    summary_df["No"] = summary_df["No"].ffill()
    summary_df["Address"] = summary_df["Address"].ffill()
    summary_df = summary_df[colomns]
    header = [Paragraph(str(col),header_style) for col in summary_df.columns.tolist()]
    
    body_rows = []
    for _, row in summary_df.iterrows():
        body_row = []
        for col in summary_df.columns:
            cell = row[col]
            if col.strip().lower() in ['direct asking rate','net rent','total additional rate', 'gross rent', 'additional rent']:
                if pd.isna(cell): value = "-"
                else:
                    try:
                        clean = str(cell).replace(',', '').replace('$', '')
                        number = float(clean)
                        value = f"${number:,.2f}"
                    except (ValueError, TypeError):
                        value = str(cell)
            elif col.strip().lower() in ['annual rent']:
                if pd.isna(cell): value = "-"
                else:
                    try:
                        clean = str(cell).replace(',', '').replace('$', '')
                        number = float(clean)
                        value = f"${number:,.0f}"
                    except (ValueError, TypeError):
                        value = str(cell)
            elif col.strip().lower() in ["no", "no."]:
                if pd.isna(cell):
                    value = ""
                else:
                    value = str(int(cell))  # convert to int for display
            elif col.strip().lower() in ['size','office area', 'total building area', 'typical floor','direct available area','total available area']:
                if pd.isna(cell): value = "-"
                else:
                    try:
                        number = float(str(cell).replace(',', ''))
                        value = f"{number:,.0f}"
                    except (ValueError, TypeError):
                        value = str(cell)
            else:
                #value = "N/A" if pd.isna(str(row[col])) else str((row[col]))
                if pd.isna(cell):
                    value = "-"
                elif isinstance(cell, (int, float)):
                    value = f"{cell:,}"  # ensure comma for any numeric
                else:
                    value = str(cell)
            body_row.append(Paragraph(value, normal))
        body_rows.append(body_row)
    table_data = [header] + body_rows

    summary_table = Table(table_data,repeatRows=1,hAlign='LEFT')
    no_col_idx = summary_df.columns.get_loc("No")
    address_col_idx = summary_df.columns.get_loc("Address")
    group_spans = get_group_row_spans(summary_df,group_col="No",span_cols=[no_col_idx, address_col_idx])
    
    available_width = page_width - (2 * margin)
    if available_width <= 0:
        raise ValueError("Available width for table is too small")
    num_columns = len(table_data[0])
    PARAGRAPH_COLS = {4, 5,6,7,8}   # fixed colomns 
    FIXED_PARA_WIDTH = 60   # points
    MIN_COL_WIDTH = 30
    col_widths = []
    for col_idx in range(num_columns):
        if col_idx in PARAGRAPH_COLS:
            # Fixed width for wrapped text
            col_widths.append(FIXED_PARA_WIDTH)
        elif col_idx ==0 or col_idx ==9:
            col_widths.append(30)
        else:
            # Auto-size based on text length
            max_width = 0
            for row in summary_df.itertuples(index=False):
                text = "" if row[col_idx] is None else str(row[col_idx])
                max_width = max(
                    max_width,
                    stringWidth(text, normal.fontName, normal.fontSize)
                )
            col_widths.append(max_width + 5)  # padding

    total_width = sum(col_widths)  
    if total_width > available_width:
        scale = available_width / total_width
        col_widths = [
            max(w * scale, MIN_COL_WIDTH)
            for w in col_widths]   
    # Create table
    summary_table = Table(table_data, colWidths=col_widths,repeatRows=1, hAlign='LEFT')
    table_style= [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#5B4E46")), #header row
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'HelveticaNeueLTStd-Lt'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0,0), (-1,0), 'TOP'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white), #data rows
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#A49389")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,1), (-1,-1), 'MIDDLE')]
    table_style.extend(group_spans)
    summary_table.setStyle(TableStyle(table_style))

    table_width, table_height = summary_table.wrap(available_width, page_height)  #KNOW how tall the table is (in points).
    draw_map_same_page = (table_height + map_height) <= available_height
    table_x = margin

    # Ensure table does not go off the page
    table_y = max(bottom_margin, page_height - top_margin - table_height)
    summary_table.drawOn(c, table_x, table_y)
    
    if draw_map_same_page:
        img = Image.open(png_path)
        px_w, px_h = img.size
        pt_w = px_w * 72 / 300
        pt_h = px_h * 72 / 300

        max_map_width = page_width - 2 * margin
        # scale = max_map_width / pt_w
        # pt_w *= scale
        # pt_h *= scale
        map_y = bottom_margin
        c.drawImage(ImageReader(png_path),margin,map_y,width=pt_w,height=pt_h)

    else:
        c.showPage()  # NEW PAGE
        c.setFont("HelveticaNeueLTStd-Th", 28)
        c.setFillColor(colors.HexColor("#A49389"))
        c.drawString(margin, page_height - 60, "Building Locations")
        img = Image.open(png_path)
        px_w, px_h = img.size
        pt_w = px_w * 72 / 300
        pt_h = px_h * 72 / 300

        max_map_width = page_width - 2 * margin
        map_y = (page_height - pt_h) / 2
        c.drawImage(ImageReader(png_path),margin,map_y,width=pt_w,height=pt_h)

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
                             png_path='map.png',
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
    
    # 2. BUILDING SUMMARY PAGE
    print(f"Generating page {current_page}/{total_pages}: Building Summary")
    draw_building_summary_page(c, summary_df, page_width, page_height, png_path)
    c.setFont("Helvetica", 7)
    c.drawString(page_width - 100, 30, f"Page {current_page} of {total_pages}")
    c.showPage()
    current_page += 1

    # 3. PROPERTY PAGES
    for page_num, (_, property_row) in enumerate(properties_df.iterrows(), 1):
        property_id = property_row[property_id_col]
        print(f"Generating page {current_page}/{total_pages}: {property_id}")
        
        property_spaces = spaces_df[spaces_df[property_id_col] == property_id]
        # Add page header
        c.setFont("HelveticaNeueLTStd-Th", 32)
        c.setFillColor(colors.HexColor("#A49389")) 
        c.drawString(50, page_height - 60, f"{property_row['Address']}")
        
        # Create and draw tables
        property_table_data = create_property_table_data(property_row, exclude_property_cols)
        spaces_table_data = create_spaces_table_data(property_spaces)
        draw_tables_on_canvas(c, property_table_data, spaces_table_data, page_width, page_height)
        
        # Page number
        c.setFont("Helvetica", 7)
        c.drawString(page_width - 100, 30, f"Page {current_page}")
        
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
        properties_excel_path='CostarExport.xlsx',
        spaces_excel_path='spaces.xlsx',
        property_id_col='No',
        properties_sheet=0,      # Sheet1 - Individual properties
        summary_sheet=0,         # Sheet2 - Building summary table
        spaces_sheet=0,          # Sheet1 in spaces.xlsx
        exclude_property_cols=['No', 'Internal_Notes','Unnamed: 12', 
                              'Leasing Profile', 'Number of Parking Stalls', 
                              'Parking Ratio (1 per)'])