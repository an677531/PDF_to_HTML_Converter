import json

from pdf_extractor import extract_pdf


PDF_FILE = "../sample.pdf"


with open(PDF_FILE, "rb") as file:
    pdf_bytes = file.read()


document = extract_pdf(pdf_bytes)


print("\n========== PDF METADATA ==========\n")

print(
    json.dumps(
        document["metadata"],
        indent=2
    )
)


print("\n========== PAGES ==========\n")


for page in document["pages"]:

    print(
        f"PAGE {page['page_number']}"
    )

    print(
        f"Size: {page['width']} x {page['height']}"
    )

    print(
        f"Blocks: {len(page['blocks'])}"
    )

    for block in page["blocks"]:

        if block["type"] == "text":

            print("\nTEXT:")
            print(f"BBox: {block['bbox']}")
            print(block["text"])

        elif block["type"] == "image":

            print("\nIMAGE:")

            print(
                f"Size: "
                f"{block['width']}x{block['height']}"
            )

            print(
                f"BBox: {block.get('bbox')}"
            )

            print(
                f"Filename: "
                f"{block.get('filename')}"
            )

    print("\n--------------------------------\n")