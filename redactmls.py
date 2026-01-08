import fitz
import re
import sys
#Best version for debrand MLS client sheet
#  Regex stands for “regular expression”.  can find not just exact words, but patterns like: phone, emails, name etc

pdf_path = "MLS.pdf"
output_path = "MLS_redacted.pdf"
patterns_file = "redact_list.txt"

# Load patterns
patterns = []
with open(patterns_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip() # removes whitespace characters from the start and end of a string.  "   Hello World   \n" becomes Hello World
        if not line:  #If the line is now empty , not line is True. then continue (skips this line and goes to the next line)
            continue  
        # if "#" in line:
        #     line = line.split("#", 1)[0].strip()
        if line:
            patterns.append(re.compile(line, re.IGNORECASE))  #converts each line into a regex pattern (case-insensitive).

# brokerage_pattern = re.compile(r"\d{3}[\s\-–—]?\d{3}[\s\-–—]?\d{4}")
# patterns.append(brokerage_pattern)

    # phone_pattern = re.compile(r"\d{3}[\s\-–—]?\d{3}[\s\-–—]?\d{4}")
    # patterns.append(phone_pattern)


 # print(patterns)
print(f"Loaded {len(patterns)} patterns")

# Open PDF
doc = fitz.open(pdf_path)

# Amount to shrink box
SHRINK_X = 0.5
SHRINK_Y = 0.5

for page_num, page in enumerate(doc, start=1):  #loop through every page. total_rects store all rectangles that need redaction 
    total_rects = []
    for pattern in patterns:
        # quads is a list of “boxes” (Quad objects) that cover all the places where this pattern appears on the page
        # Each “quad” is like a tight box around the text we want to remove.
        quads = page.search_for(pattern.pattern, flags=3, quads=True)    

       # pattern itself is a regex object.  pattern.pattern gives the original string inside that regex object. quads=true (give the exact shape around each character)
        # matches = pattern.findall(page.get_text("text"))
        # print(f"Pattern: {pattern.pattern}")
    
        for q in quads:  #Each quad is a complex object representing four points around the text.
            # Get rect for the quad
            r = q.rect  #converts it into a simple rectangle for redaction (drawing the white box).
            # Shrink the rectangle slightly
            r.x0 += SHRINK_X #moves the left side slightly to the right by 0.5
            r.x1 -= SHRINK_X #moves the right side slightly to the left
            r.y0 += SHRINK_Y #moves the top side slightly down
            r.y1 -= SHRINK_Y  #moves the bottom side slightly up
            total_rects.append(r)

    # Apply redactions
    for rect in total_rects:
        page.add_redact_annot(rect, fill=(1, 1, 1))

    page.apply_redactions()
    
    print(f"Page {page_num}: {len(total_rects)} items redacted")

# Save output
doc.save(output_path)
doc.close()
print(f"\nRedacted PDF saved to: {output_path}")




# # --- LOAD PATTERNS ---
# patterns = []
# with open(patterns_file, "r", encoding="utf-8") as f:
#     for line in f:
#         line = line.strip()
#         if not line:
#             continue
#         if "#" in line:
#             line = line.split("#")[0].strip()  # strip comments
#         if line:
#             patterns.append(re.compile(line, re.IGNORECASE))

# print(f"Loaded {len(patterns)} patterns")
# doc = fitz.open(pdf_path)
# phone_pattern = r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"

# phone_regex = re.compile(phone_pattern)

# for page in doc:
#     page_text = page.get_text()

#     matches = phone_regex.findall(page_text)

#     for match in matches:
#         rects = page.search_for(match)
#         for r in rects:
#             page.add_redact_annot(r)
#         page.apply_redactions()


# # --- PROCESS PDF ---
# doc = fitz.open(pdf_path)

# for page_num, page in enumerate(doc, start=1):
#     instances = []

#     for pattern in patterns:
#         rects = page.search_for(pattern.pattern, flags=3)
#         instances.extend(rects)

#     for r in instances:
#         page.add_redact_annot(r, fill=(1, 1, 1))

#     page.apply_redactions()
#     print(f" Page {page_num}: {len(instances)} redactions applied")

# doc.save(output_path)
# doc.close()
# print(f"Saved to {output_path}")