import fitz
import re
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import os

#best version for debranding flyer woth OCR
pdf_path = r"E:\Business\TOCOnnect\Code\Python Practice\96 Inspire Blvd - Brochure Nov 2025.pdf"
output_path = "DebrandedFlyer.pdf"
patterns_file = "redact_list2.txt"
output_path1 = "searchable.pdf" # Output searchable PDF

# Convert PDF pages to images
# images = convert_from_path(pdf_path, dpi=300)
# # Create a new PDF
# new_doc = fitz.open()
# for img in images:
#     # Perform OCR
#     text = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
#     # Load OCR output as a PDF page
#     ocr_pdf = fitz.open("pdf", text)
#     # Insert each page into the new document
#     new_doc.insert_pdf(ocr_pdf)
# # Save the searchable PDF
# new_doc.save(output_path1)
# new_doc.close()

# Load patterns from file
patterns = []
with open(patterns_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        patterns.append(re.compile(line, re.IGNORECASE))
#print(f"Loaded {len(patterns)} patterns")
phone_pattern = re.compile(r"\d{3}[\s\-–—]?\d{3}[\s\-–—]?\d{4}")
patterns.append(phone_pattern)

# Matches any brokerage name (letters, spaces, ., /, -, ,) followed by a phone number
brokerage_pattern = re.compile(r'[A-Z&\s\.\-/,]+(REALTY|REAL ESTATE|GROUP|INC|LTD)\.?', re.IGNORECASE)
patterns.append(brokerage_pattern)
name_pattern = re.compile(r"[A-Z][A-Za-z\s]+(Manager|Broker|Agent|Director|Sales|Commercial Properties)", re.IGNORECASE)  # Titles
patterns.append(name_pattern)
patterns.extend([phone_pattern, brokerage_pattern,name_pattern])

doc = fitz.open(pdf_path)
SHRINK = 1
# shrink redaction box

for page_num, page in enumerate(doc, start=1):
    blocks = page.get_text("blocks")  # get all text blocks
    total_rects = []

    for block in blocks:
        x0, y0, x1, y1, text, *_ = block  # extract text + rectangle
        text = text.strip()

        # Check if any pattern matches the entire block text
        for pattern in patterns:
            if pattern.search(text):
                rect = fitz.Rect(x0 + SHRINK, y0 + SHRINK, x1 - SHRINK, y1 - SHRINK)
                total_rects.append(rect)
                break  # avoid adding duplicate matches for same block

    # # Apply redactions
    for rect in total_rects:
        page.add_redact_annot(rect, fill=None) #draw transparent box

    page.apply_redactions()

    print(f"Page {page_num}: {len(total_rects)} line(s) redacted")

doc.save(output_path)
doc.close()

print(f"\nRedacted PDF saved to: {output_path}")


