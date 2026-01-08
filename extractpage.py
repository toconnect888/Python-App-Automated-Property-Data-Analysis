
import os
from PyPDF2 import PdfReader, PdfWriter, Transformation
import fitz

# Constants for Letter size in points
LETTER_WIDTH = 612  # 8.5 inches
LETTER_HEIGHT = 792  # 11 inches

# Folder with PDFs
folder_path = r"E:\Business\TOCOnnect\Code\Python Practice\flyers"
output_path = r"E:\Business\TOCOnnect\Code\Python Practice\flyers\extracted"
output_folder = os.path.join(folder_path, "extracted")
os.makedirs(output_folder, exist_ok=True)
# Mapping of PDF filenames to pages to extract (0-based)
# e.g., "filename.pdf": [0, 2] means extract pages 1 and 3
# pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
# if not pdf_files:
#     print("No PDF files found in the folder!")
# else:
#     for filename in pdf_files:
#         input_pdf = os.path.join(folder_path, filename)
#         base_name = os.path.splitext(filename)[0]
#         output_pdf = os.path.join(output_folder, f"{base_name}_extracted.pdf")
        
#         reader = PdfReader(input_pdf)
#         num_pages = len(reader.pages)
#         print(f"\n'{filename}' has {num_pages} pages.")
        
#         # Ask user which pages to extract (1-based)
#         pages_input = input(f"Enter pages to extract for '{filename}' (space-separated, e.g. 1 3 5), or Enter to skip: ")
#         if not pages_input.strip():
#             print(f"Skipped '{filename}'")
#             continue
        
#         try:
#             pages_to_extract = [int(p) for p in pages_input.split()]
#         except ValueError:
#             print("Invalid input, skipping this file.")
#             continue
        
#         writer = PdfWriter()
#         for page_num in pages_to_extract:
#             page_index = page_num - 1  # convert 1-based to 0-based
#             if 0 <= page_index < num_pages:
#                 writer.add_page(reader.pages[page_index])
#             else:
#                 print(f"Page {page_num} not found in {filename}")
        
#         # Save extracted PDF
#         with open(output_pdf, "wb") as f:
#             writer.write(f)
        
#         print(f"Extracted pages for '{filename}' saved as '{output_pdf}'")

# print("\nAll done! Extracted PDFs are in the 'extracted' folder.")


pdf_pages_map = {
        #"96 Inspire Blvd - Brochure Nov 2025.pdf": [1, 2, 3,4,5,6],
       # "220 pinebush.pdf": [2,3,4,6,8],
        #"1080 southgate.pdf": [1,2,3,4,6],  
        #"6440 Fifth Line, Milton.pdf": [2, 3, 4],
       # "6450 Cantay - Flyer October 2025 - web.pdf": [1,2,3,5],
       # "FINAL 8705 Torbram Road_Brochure_v8.pdf": [1,2,3,4],
        #"120 Allendale_275 Intermarket.pdf": [2,3,4,5,7,9],
        "1574 Eagle Street - Flyer.pdf": [1,3,4,5]
    }

for filename, pages_to_extract in pdf_pages_map.items():
    input_pdf = os.path.join(folder_path, filename)

    if not os.path.exists(input_pdf):
            print(f"File not found: {filename}")
            continue
    
    # Prepare output filename
    base_name = os.path.splitext(filename)[0]
    output_pdf = os.path.join(output_path, f"extracted_{base_name}.pdf")

    # Read and extract pages
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    new_doc = fitz.open()
    for page_num in pages_to_extract:
        page_index = page_num - 1  # convert 1-based to 0-based
        if 0 <= page_index < len(reader.pages):
            #writer.add_page(reader.pages[page_index])
            page = reader.pages[page_index]
        # Resize page to Letter portrait
            page = doc.load_page(page_num)
                # Get original size
            orig_rect = page.rect
            # Scale to Letter size
            zoom_x = LETTER_WIDTH / orig_rect.width
            zoom_y = LETTER_HEIGHT / orig_rect.height
            zoom = min(zoom_x, zoom_y)
            mat = fitz.Matrix(zoom, zoom)
            
            pix = page.get_pixmap(matrix=mat)
            # Create new page in Letter size
            new_page = new_doc.new_page(width=LETTER_WIDTH, height=LETTER_HEIGHT)
            # Insert the scaled page as image
            new_page.insert_image(new_page.rect, pixmap=pix)
        
            writer.add_page(page)
        else:
            print(f"Page {page_num} not found in {filename}")
    
    # Save the new PDF
    with open(output_pdf, "wb") as f:
        writer.write(f)
    
    print(f"Extracted pages for {filename} saved as {output_pdf}")
