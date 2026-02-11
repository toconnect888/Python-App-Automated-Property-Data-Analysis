import fitz  # PyMuPDF
import os

# Folder with PDFs
INPUT_DIR = r"E:\Business\TOCOnnect\Code\Python Practice\media"

# Where extracted images go
OUTPUT_DIR = r"E:\Business\TOCOnnect\Code\Python Practice\media"

# def parse_pages(text):
#     """
#     Convert: "1,3,5-7" → [1,3,5,6,7]
#     """
#     pages = set()

#     parts = text.split(",")

#     for part in parts:

#         part = part.strip()

#         if "-" in part:
#             start, end = part.split("-")

#             for i in range(int(start), int(end) + 1):
#                 pages.add(i)

#         else:
#             pages.add(int(part))

#     return sorted(pages)

# def main():
#     # Find PDFs
#     pdfs = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]

#     if not pdfs:
#         print(" No PDFs found.")
#         return

#     print("\nFound PDF files:\n")

#     for i, pdf in enumerate(pdfs, start=1):
#         print(f"{i}. {pdf}")
#     print("\n---------------------------\n")

#     os.makedirs(OUTPUT_DIR, exist_ok=True)

#     for pdf in pdfs:
#         print(f"\n Processing: {pdf}")

#         pages_input = input(
#             "Enter pages to extract (example: 1,3,5-7 or Enter to skip): "
#         ).strip()

#         if not pages_input:
#             print("Skipped.")
#             continue
#         try:
#             pages = parse_pages(pages_input)
#         except:
#             print("Invalid format. Skipping.")
#             continue

#         pdf_path = os.path.join(INPUT_DIR, pdf)
#         doc = fitz.open(pdf_path)
#         base = os.path.splitext(pdf)[0]
#         out_dir = os.path.join(OUTPUT_DIR, base)
#         os.makedirs(out_dir, exist_ok=True)

#         for p in pages:
#             idx = p - 1
#             if idx < 0 or idx >= len(doc):
#                 print(f" Page {p} out of range")
#                 continue

#             page = doc[idx]
#             images = page.get_images(full=True)

#             if images:
#                 for i, img in enumerate(images, 1):
#                     data = doc.extract_image(img[0])
#                     ext = data["ext"]
#                     name = f"page{p}_img{i}.{ext}"
#                     with open(os.path.join(out_dir, name), "wb") as f:
#                         f.write(data["image"])
#             else:
#                 # Fallback: render whole page
#                 pix = page.get_pixmap(dpi=300)
#                 name = f"page{p}_render.png"
#                 pix.save(os.path.join(out_dir, name))

#         doc.close()
#         print("Done.")
#     print("\n All PDFs processed.")

# if __name__ == "__main__":
#     main()

# Process all pages of all PDFs without user input

def extract_all_pages():

    pdfs = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]
    if not pdfs:
        print("No PDFs found.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for pdf in pdfs:
        print(f"\n Processing: {pdf}")
        pdf_path = os.path.join(INPUT_DIR, pdf)
        doc = fitz.open(pdf_path)
        base = os.path.splitext(pdf)[0]
        out_dir = os.path.join(OUTPUT_DIR, base)

        os.makedirs(out_dir, exist_ok=True)

        for page_index in range(len(doc)):

            page = doc[page_index]
            page_num = page_index + 1

            images = page.get_images(full=True)

            # Case 1: Extract embedded images
            if images:
                for i, img in enumerate(images, 1):
                    data = doc.extract_image(img[0])
                    ext = data["ext"]
                    name = f"page{page_num}_img{i}.{ext}"
                    path = os.path.join(out_dir, name)
                    with open(path, "wb") as f:
                        f.write(data["image"])

            # Case 2: No images → render full page
            else:
                pix = page.get_pixmap(dpi=300)
                name = f"page{page_num}.png"
                pix.save(os.path.join(out_dir, name))

        doc.close()
        print(" Done.")
    print("\n All PDFs processed.")


if __name__ == "__main__":
    extract_all_pages()

    