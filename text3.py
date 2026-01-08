import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

pdf_path = "flyer.pdf"       # Your image-based PDF
output_path = "searchable.pdf" # Output searchable PDF

# Convert PDF pages to images
images = convert_from_path(pdf_path, dpi=300)

# Create a new PDF
new_doc = fitz.open()

for img in images:
    # Perform OCR
    text = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
    
    # Load OCR output as a PDF page
    ocr_pdf = fitz.open("pdf", text)
    
    # Insert each page into the new document
    new_doc.insert_pdf(ocr_pdf)

# Save the searchable PDF
new_doc.save(output_path)
new_doc.close()

print(f"Searchable PDF saved as: {output_path}")
