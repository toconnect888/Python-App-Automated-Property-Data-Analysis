# import fitz  # PyMuPDF
# import re
# from pdf2image import convert_from_path
# import pytesseract
# from PIL import Image

# # --------------------------
# # Paths
# pdf_path = "flyer.pdf"
# output_path = "DebrandedFlyer.pdf"
# patterns_file = "redact_list2.txt"
# # --------------------------

# # --- Load regex patterns ---
# patterns = []
# with open(patterns_file, "r", encoding="utf-8") as f:
#     for line in f:
#         line = line.strip()
#         if line:
#             patterns.append(re.compile(line, re.IGNORECASE))

# # Additional patterns
# phone_pattern = re.compile(r"\d{3}[\s\-–—]?\d{3}[\s\-–—]?\d{4}")
# brokerage_pattern = re.compile(r'[A-Z&\s\.\-/,]+(REALTY|REAL ESTATE|GROUP|INC|LTD)\.?', re.IGNORECASE)
# name_pattern = re.compile(r"[A-Z][A-Za-z\s]+(Manager|Broker|Agent|Director|Sales|Commercial Properties)", re.IGNORECASE)

# # patterns.extend([phone_pattern, brokerage_pattern, name_pattern])
# patterns = [phone_pattern, brokerage_pattern, name_pattern]

# # Open PDF
# doc = fitz.open(pdf_path)
# SHRINK = 1  # shrink redaction box slightly

# # --- Loop through pages ---
# for page_num, page in enumerate(doc, start=1):
#     # Convert PDF page to image for OCR
#     pix = page.get_pixmap(dpi=300)
#     img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

#     # OCR with coordinates
#     ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

#     total_rects = []
#     num_words = len(ocr_data['text'])

#     # --- Combine words into phrases to match patterns ---
#     for i in range(num_words):
#         word = ocr_data['text'][i].strip()
#         if not word:
#             continue

#         # Combine up to 5 words as a phrase
#         for j in range(i, min(i + 5, num_words)):
#             phrase_words = ocr_data['text'][i:j + 1]
#             phrase = " ".join([w for w in phrase_words if w.strip()])
#             if not phrase:
#                 continue

#             for pattern in patterns:
#                 if pattern.search(phrase):
#                     # Get bounding box covering all words in the phrase
#                     x0 = min([ocr_data['left'][k] for k in range(i, j + 1)])
#                     y0 = min([ocr_data['top'][k] for k in range(i, j + 1)])
#                     x1 = max([ocr_data['left'][k] + ocr_data['width'][k] for k in range(i, j + 1)])
#                     y1 = max([ocr_data['top'][k] + ocr_data['height'][k] for k in range(i, j + 1)])

#                     # Scale coordinates to PDF page
#                     page_width, page_height = page.rect.width, page.rect.height
#                     img_width, img_height = img.size
#                     rect = fitz.Rect(
#                         x0 * page_width / img_width + SHRINK,
#                         y0 * page_height / img_height + SHRINK,
#                         x1 * page_width / img_width - SHRINK,
#                         y1 * page_height / img_height - SHRINK
#                     )
#                     total_rects.append(rect)
#                     break  # stop after first matching pattern

#     # Apply redactions
#     for rect in total_rects:
#         page.add_redact_annot(rect, fill=None)  # transparent redaction
#     page.apply_redactions()

#     print(f"Page {page_num}: {len(total_rects)} phrase(s) redacted")

# # Save new PDF
# doc.save(output_path)
# doc.close()
# print(f"\nRedacted PDF saved to: {output_path}")




import fitz  # PyMuPDF
import re
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

# --------------------------
# Paths
pdf_path = "flyer.pdf"
output_path = "DebrandedFlyer.pdf"
patterns_file = "redact_list2.txt"
# --------------------------

# --- Load regex patterns ---
patterns = []

with open(patterns_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            # Only keep specific patterns you want to redact
            patterns.append(re.compile(line, re.IGNORECASE))

# --- Refined regex ---
phone_pattern = re.compile(r"\d{3}[\s\-–—]?\d{3}[\s\-–—]?\d{4}")
brokerage_pattern = re.compile(
    r'\b[A-Z&\s\.\-/,]+(?:REALTY|REAL ESTATE|GROUP|INC|LTD)\b\.?', re.IGNORECASE
)
name_pattern = re.compile(
    r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\s+(Manager|Broker|Agent|Director|Sales|Commercial Properties)\b',
    re.IGNORECASE
)

# Only these three types of info
patterns = [phone_pattern, brokerage_pattern, name_pattern]

# Open PDF
doc = fitz.open(pdf_path)
SHRINK = 1  # shrink redaction box slightly

# --- Loop through pages ---
for page_num, page in enumerate(doc, start=1):
    # Convert PDF page to image for OCR
    pix = page.get_pixmap(dpi=300)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # OCR with coordinates
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    total_rects = []
    num_words = len(ocr_data['text'])

    # --- Phrase-based matching ---
    for i in range(num_words):
        word = ocr_data['text'][i].strip()
        if not word:
            continue

        # --- Detect brokerage + phone pairs ---
        if phone_pattern.search(word):
            start = max(0, i-3)  # look up to 3 words before
            phrase_words = ocr_data['text'][start:i+1]
            phrase = " ".join([w for w in phrase_words if w.strip()])
            if brokerage_pattern.search(phrase):
                # Redact phrase
                x0 = min([ocr_data['left'][k] for k in range(start, i+1)])
                y0 = min([ocr_data['top'][k] for k in range(start, i+1)])
                x1 = max([ocr_data['left'][k]+ocr_data['width'][k] for k in range(start, i+1)])
                y1 = max([ocr_data['top'][k]+ocr_data['height'][k] for k in range(start, i+1)])

                page_width, page_height = page.rect.width, page.rect.height
                img_width, img_height = img.size
                rect = fitz.Rect(
                    x0 * page_width / img_width + SHRINK,
                    y0 * page_height / img_height + SHRINK,
                    x1 * page_width / img_width - SHRINK,
                    y1 * page_height / img_height - SHRINK
                )
                total_rects.append(rect)
                continue  # move to next word

        # --- Detect names with titles ---
        for pattern in [name_pattern]:
            # Look ahead 2-3 words to capture full title
            end = min(i+3, num_words)
            phrase_words = ocr_data['text'][i:end]
            phrase = " ".join([w for w in phrase_words if w.strip()])
            if pattern.search(phrase):
                x0 = min([ocr_data['left'][k] for k in range(i, end)])
                y0 = min([ocr_data['top'][k] for k in range(i, end)])
                x1 = max([ocr_data['left'][k]+ocr_data['width'][k] for k in range(i, end)])
                y1 = max([ocr_data['top'][k]+ocr_data['height'][k] for k in range(i, end)])

                page_width, page_height = page.rect.width, page.rect.height
                img_width, img_height = img.size
                rect = fitz.Rect(
                    x0 * page_width / img_width + SHRINK,
                    y0 * page_height / img_height + SHRINK,
                    x1 * page_width / img_width - SHRINK,
                    y1 * page_height / img_height - SHRINK
                )
                total_rects.append(rect)
                break  # stop after first match

    # Apply redactions
    for rect in total_rects:
        page.add_redact_annot(rect, fill=None)  # transparent
    page.apply_redactions()

    print(f"Page {page_num}: {len(total_rects)} phrase(s) redacted")

# Save new PDF
doc.save(output_path)
doc.close()
print(f"\nRedacted PDF saved to: {output_path}")
