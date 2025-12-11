import pandas as pd
# For PDF generation
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER , TA_LEFT
from reportlab.lib.units import inch

pdfmetrics.registerFont(TTFont('HelveticaNeueLTStd-Lt', r"E:\Business\TOCOnnect\Code\Fonts\HelveticaNeueLTStd-Th.ttf"))
pdfmetrics.registerFont(TTFont('GeorgiaBold', r"E:\Business\TOCOnnect\Code\Fonts\GeorgiaBold.ttf"))
brand_color = colors.HexColor("#5B4E46")

def export_multiple_buildings_to_pdf(excel_path, pdf_path):
    # Read Excel with no headers, treat first column as label, second as value
    df = pd.read_excel(excel_path, header=None, names=["Label", "Value"])
    df = df.dropna(how="all")  # remove fully empty rows
    doc = SimpleDocTemplate(pdf_path, pagesize=LETTER)
    styles = getSampleStyleSheet()
    elements = []
    
    heading1 = ParagraphStyle(
        name='RightHeading',
        fontName='HelveticaNeueLTStd-Lt',         # or your custom font
        fontSize=20,                  # font size
        textColor=colors.HexColor("#5B4E46"),  # match table header color
        alignment=TA_LEFT,           # right-align
        leading=16  )                  # line spacing


    # Identify indices where new building profiles start
    building_start_indices = df.index[df['Label'] == 'Building Profile'].tolist()

    for i, start_idx in enumerate(building_start_indices):
        # Determine end of building section
        end_idx = building_start_indices[i + 1] if i + 1 < len(building_start_indices) else len(df)
        building_df = df.loc[start_idx:end_idx - 1].reset_index(drop=True)
        current_section = None
        table_data = []

        for _, row in building_df.iterrows():
            label = str(row["Label"]).strip()
            value = str(row["Value"]).strip() if pd.notna(row["Value"]) else ""
            
            # Detect section headers
            if "Profile" in label:
                # Output previous section if exists
                if current_section and table_data:
                    address = building_df.iloc[2,1] # Aaddress is in the second row of building section
                    elements.append(Paragraph(f"<b>{address}</b>", heading1))
                    elements.append(Spacer(1, 36))
                    table = Table(table_data, colWidths=[150, 150])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#5B4E46")),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('FONTNAME', (0, 0), (-1, -1), 'HelveticaNeueLTStd-Lt'),
                        ('FONTSIZE', (0, 0), (-1, -1), 11),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                    table.hAlign = 'RIGHT'
                    elements.append(table)
                    elements.append(Spacer(1, 16))
                    table_data = []

                current_section = label
                continue

            # Regular key-value row
            if label and value:
                table_data.append([label, value])

        # Add the last section for this building
        if current_section and table_data:
            # elements.append(Paragraph(f"<b>{current_section}</b>", heading1))
            # elements.append(Spacer(1, 6))
            table = Table(table_data, colWidths=[150, 150])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'HelveticaNeueLTStd-Lt'),
                ('FONTSIZE', (0, 0), (-1, -1), 10.5),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            table.hAlign = 'RIGHT'
            elements.append(table)

        # Add a page break after each building except the last
        if i < len(building_start_indices) - 1:
            elements.append(PageBreak())

    doc.build(elements)
    print(f"building_report.pdf created at: {pdf_path}")

# ---- Run the function ----
export_multiple_buildings_to_pdf(
    excel_path=r"E:\Business\TOCOnnect\Code\Python Practice\real_estate_report.xlsx",
    pdf_path=r"E:\Business\TOCOnnect\Code\Python Practice\building_report.pdf"
)


# # # Example usage
# df = pd.read_excel(r"E:\Business\TOCOnnect\Code\Python Practice\real_estate_report.xlsx")
# export_excel_to_pdf(df, r"E:\Business\TOCOnnect\Code\Python Practice\styled_excel_table.pdf")


# def export_json_variable_to_pdf(buildings, pdf_path):
#     doc = SimpleDocTemplate(pdf_path, pagesize=LETTER)
#     styles = getSampleStyleSheet()
#     elements = []

#     for b_idx, building in enumerate(buildings):
#         for section_name, section_data in building.items():
#             elements.append(Paragraph(f"<b>{section_name}</b>", styles["Heading2"]))
#             elements.append(Spacer(1, 8))

#             # Convert dictionary to table data
#             table_data = [["Field", "Value"]] + [[k, str(v)] for k, v in section_data.items()]

#             table = Table(table_data, colWidths=[180, 300])
#             table.setStyle(TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#5B4E46")),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
#                 ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
#                 ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
#                 ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ]))
#             elements.append(table)
#             elements.append(Spacer(1, 12))

#         # Page break after each building except the last
#         if b_idx < len(buildings) - 1:
#             elements.append(PageBreak())

#     doc.build(elements)
#     print(f"✅ PDF successfully created at: {pdf_path}")
