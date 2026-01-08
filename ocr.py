import fitz
import re
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
# requirement:  
# pip install pdf2image pytesseract pillow
# sudo apt-get install poppler-utils
# sudo apt-get install tesseract-ocr

pdf_path = "flyer.pdf"
output_path = "DebrandedFlyer.pdf"
patterns_file = "redact_list.txt"
converted_images = convert_from_path(pdf_path)

# Load patterns from file
patterns = []
with open(patterns_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            patterns.append(re.compile(line, re.IGNORECASE))

# Additional patterns
phone_pattern = re.compile(r"\d{3}[\s\-–—]?\d{3}[\s\-–—]?\d{4}")
patterns.append(phone_pattern)

brokerage_pattern = re.compile(r'[A-Z&\s\.\-/,]+(REALTY|REAL ESTATE|GROUP|INC|LTD)\.?', re.IGNORECASE)
patterns.append(brokerage_pattern)

name_pattern = re.compile(
    r"[A-Z][A-Za-z\s]+(Manager|Broker|Agent|Director|Sales|Commercial Properties)", re.IGNORECASE
)
patterns.append(name_pattern)
patterns.extend([phone_pattern, brokerage_pattern,name_pattern])

# Open PDF with PyMuPDF
doc = fitz.open(pdf_path)
SHRINK = 1  # shrink redaction box

for page_index in range(len(doc)):
    page = doc[page_index]        # <- THIS is a real PDF page
    original_blocks = page.get_text("blocks")

    # --- OCR: convert page to image ---
    img = converted_images[page_index]   # image from pdf2image
    ocr_text = pytesseract.image_to_string(img)

    # Run OCR on the image
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    total_rects = []

    # Loop through all words detected by OCR
    for i, word in enumerate(ocr_data['text']):
        if not word.strip():
            continue

#     # for page_num, page in enumerate(ocr_data, start=1):
#         blocks = page.get_text("blocks")  # get all text blocks
#         total_rects = []

#     for block in blocks:
#         x0, y0, x1, y1, text, *_ = block  # extract text + rectangle
#         text = text.strip()

#         # Check if any pattern matches the entire block text
#         for pattern in patterns:
#             if pattern.search(text):
#                 rect = fitz.Rect(x0 + SHRINK, y0 + SHRINK, x1 - SHRINK, y1 - SHRINK)
#                 total_rects.append(rect)
#                 break  # avoid adding duplicate matches for same block

#     # # Apply redactions
#         for rect in total_rects:
#             #page.add_redact_annot(rect, fill=(1, 1, 1)) #draw white box
#             page.add_redact_annot(rect, fill=None) #draw transparent box
#             page.apply_redactions()

#     print(f"Page {page_index}: {len(total_rects)} line(s) redacted")

# doc.save(output_path)
# doc.close()

# print(f"\nRedacted PDF saved to: {output_path}")



        for pattern in patterns:
            if pattern.search(word):
                # Get coordinates of the word
                x, y, w, h = ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]
                
                # Scale coordinates to fit the PDF page
              
                rect = fitz.Rect(x + SHRINK, y + SHRINK, w - SHRINK, h - SHRINK)
                
                total_rects.append(rect)
                break  # stop at first matching pattern

    # Apply redactions
for rect in total_rects:
    page.add_redact_annot(rect, fill=(1,1,1))  # transparent box
    page.apply_redactions()

    print(f"Page {page_num}: {len(total_rects)} line(s) redacted")

# Save the new PDF
doc.save(output_path)
doc.close()
print(f"\nRedacted PDF saved to: {output_path}")
