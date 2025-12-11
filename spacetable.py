from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas
from io import BytesIO
import pandas as pd

def create_table_pdf(data, page_width, page_height, x_pos=50, y_pos=50):
    """Create a PDF with a formatted table"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    
    # Create table with styling
    table = Table(data)
    table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A5568')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        
        # Data rows styling
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F7FAFC')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        
        # Cell padding
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2D3748')),
    ]))
    
    # Position and draw table
    table.wrapOn(c, page_width, page_height)
    table.drawOn(c, x_pos, y_pos)
    
    c.save()
    buffer.seek(0)
    return buffer

def format_field_name(column_name):
    """Convert column names to readable field names"""
    # Remove common suffixes and replace underscores
    name = column_name.replace('_', ' ')
    
    # Capitalize properly
    name = name.title()
    
    # Handle common abbreviations
    replacements = {
        'Sqft': 'sq ft',
        'Id': 'ID',
        'Sq Ft': 'sq ft',
    }
    
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    return name

def create_table_data(row, exclude_columns=None):
    """Convert DataFrame row to table format"""
    if exclude_columns is None:
        exclude_columns = []
    
    table_data = [['Field', 'Value']]
    
    for col, val in row.items():
        # Skip excluded columns
        if col in exclude_columns:
            continue
        
        # Format field name
        field_name = format_field_name(col)
        
        # Format value (handle NaN, etc.)
        if pd.isna(val):
            value = 'N/A'
        else:
            value = str(val)
        
        table_data.append([field_name, value])
    
    return table_data

def add_tables_from_excel(input_pdf_path, output_pdf_path, excel_path, 
                          sheet_name=0, exclude_columns=None,
                          x_pos=50, y_pos=50):
    """
    Add property tables to PDF from Excel (wide format)
    
    Args:
        input_pdf_path: Path to existing PDF
        output_pdf_path: Path for output PDF
        excel_path: Path to Excel file (one property per row)
        sheet_name: Excel sheet name or index (default: 0)
        exclude_columns: List of columns to exclude from table
        x_pos: Table X position from left edge (default: 50)
        y_pos: Table Y position from bottom edge (default: 50)
    
    Excel Format Expected:
        Property_ID | Area_sqft | Price    | Bedrooms | ...
        PROP-001    | 2,500     | $450,000 | 3        | ...
        PROP-002    | 3,200     | $580,000 | 4        | ...
    """
    # Read PDF
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    
    # Read Excel data
    print(f"Reading Excel file: {excel_path}")
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    
    print(f"Found {len(df)} properties in Excel")
    print(f"PDF has {len(reader.pages)} pages")
    
    if len(df) != len(reader.pages):
        print(f"\n⚠ Warning: Excel has {len(df)} rows but PDF has {len(reader.pages)} pages")
        print("  Will process min({len(df)}, {len(reader.pages)}) pages")
    
    # Process each page
    num_pages = min(len(df), len(reader.pages))
    
    for page_num in range(num_pages):
        page = reader.pages[page_num]
        
        # Get page dimensions
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        
        # Get data for this property
        property_row = df.iloc[page_num]
        table_data = create_table_data(property_row, exclude_columns)
        
        print(f"  Page {page_num + 1}: Adding table with {len(table_data)-1} fields")
        
        # Create table PDF
        table_pdf_buffer = create_table_pdf(table_data, page_width, 
                                           page_height, x_pos, y_pos)
        table_pdf = PdfReader(table_pdf_buffer)
        
        # Merge table onto existing page
        page.merge_page(table_pdf.pages[0])
        writer.add_page(page)
    
    # Handle remaining pages without data
    for page_num in range(num_pages, len(reader.pages)):
        writer.add_page(reader.pages[page_num])
    
    # Write output
    with open(output_pdf_path, 'wb') as output_file:
        writer.write(output_file)
    
    print(f"\n✓ Successfully created: {output_pdf_path}")
    print(f"  Pages processed: {num_pages}")

# Example usage
if __name__ == "__main__":
    add_tables_from_excel(
        input_pdf_path='input_properties.pdf',
        output_pdf_path='output_with_tables.pdf',
        excel_path='property_data.xlsx',
        sheet_name='Properties',  # or 0 for first sheet
        exclude_columns=['Internal_Notes', 'Agent_ID'],  # Optional: hide certain columns
        x_pos=50,    # Distance from left edge (points)
        y_pos=50     # Distance from bottom edge (points)
    )