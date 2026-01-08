import fitz  # PyMuPDF
import re
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

# --------------------------
pdf_path = "flyer.pdf"
output_path = "DebrandedFlyer.pdf"
SHRINK = 1  # shrink redaction box slightly
# --------------------------

# --- Define regex patterns ---
phone_pattern = re.compile(r"\d{3}[\s\-–—]?\d{3}[\s\-–—]?\d{4}")
brokerage_pattern = re.compile(
    r'\b[A-Z&\s\.\-/,]+(?:REALTY|REAL ESTATE|GROUP|INC|LTD)\b\.?', re.IGNORECASE
)
name_pattern = re.compile(
    r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\s+(Manager|Broker|Agent|Director|Sales|Commercial Properties)\b',
    re.IGNORECASE
)

patterns = [phone_pattern, brokerage_pattern, name_pattern]

# --- Open PDF ---
doc = fitz.open(pdf_path)

for page_num, page in enumerate(doc, start=1):
    # Convert PDF page to image for OCR
    pix = page.get_pixmap(dpi=300)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # OCR with word-level coordinates
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    total_rects = []

    num_words = len(ocr_data['text'])
    
    # --- Loop through words and small phrases ---
    for i in range(num_words):
        word = ocr_data['text'][i].strip()
        if not word:
            continue

        # Combine 1-3 words to detect multi-word patterns like names with titles
        for end in range(i, min(i+3, num_words)):
            phrase_words = ocr_data['text'][i:end+1]
            phrase = " ".join(phrase_words).strip()
            if not phrase:
                continue

            for pattern in patterns:
                if pattern.search(phrase):
                    # Get rectangle for this exact word/phrase
                    x0 = min(ocr_data['left'][k] for k in range(i, end+1))
                    y0 = min(ocr_data['top'][k] for k in range(i, end+1))
                    x1 = max(ocr_data['left'][k] + ocr_data['width'][k] for k in range(i, end+1))
                    y1 = max(ocr_data['top'][k] + ocr_data['height'][k] for k in range(i, end+1))

                    # Scale coordinates to PDF
                    page_width, page_height = page.rect.width, page.rect.height
                    img_width, img_height = img.size
                    rect = fitz.Rect(
                        x0 * page_width / img_width + SHRINK,
                        y0 * page_height / img_height + SHRINK,
                        x1 * page_width / img_width - SHRINK,
                        y1 * page_height / img_height - SHRINK
                    )

                    total_rects.append(rect)
                    break  # stop checking other patterns for this phrase

    # --- Apply redactions ---
    for rect in total_rects:
        page.add_redact_annot(rect, fill=None)  # transparent redaction
    page.apply_redactions()

    print(f"Page {page_num}: {len(total_rects)} word/phrase(s) redacted")

# --- Save new PDF ---
doc.save(output_path)
doc.close()
print(f"\nRedacted PDF saved to: {output_path}")
