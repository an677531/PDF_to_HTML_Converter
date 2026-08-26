import fitz
import os


def extract_pdf(pdf_bytes):

    document = {
        "metadata": {},
        "pages": []
    }

    # -----------------------------------------
    # Create image output directory
    # -----------------------------------------

    extracted_images_dir = os.path.join(
        os.path.dirname(__file__),
        "extracted_images"
    )

    os.makedirs(extracted_images_dir, exist_ok=True)

    # Open PDF from memory
    pdf = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    document["metadata"] = {
        "page_count": len(pdf)
    }

    # -----------------------------------------
    # Process each page
    # -----------------------------------------

    for page_number, page in enumerate(pdf, start=1):

        page_data = {
            "page_number": page_number,
            "width": page.rect.width,
            "height": page.rect.height,
            "blocks": []
        }

        # -----------------------------------------
        # Extract text
        # -----------------------------------------

        text_blocks = page.get_text("dict")["blocks"]

        for block in text_blocks:

            # type 0 = text
            if block["type"] != 0:
                continue

            lines = []

            for line in block.get("lines", []):

                line_text = ""

                for span in line.get("spans", []):

                    line_text += span.get("text", "")

                if line_text.strip():
                    lines.append(line_text.strip())

            text = "\n".join(lines).strip()

            if not text:
                continue

            page_data["blocks"].append({
                "type": "text",
                "bbox": block["bbox"],
                "text": text
            })

        # -----------------------------------------
        # Extract images
        # -----------------------------------------

                # -----------------------------------------
        # Extract images
        # -----------------------------------------

        for image_index, image in enumerate(
            page.get_images(full=True),
            start=1
        ):

            xref = image[0]

            image_data = pdf.extract_image(xref)

            extension = image_data["ext"]

            filename = (
                f"page_{page_number}_image_{image_index}.{extension}"
            )

            image_path = os.path.join(
                extracted_images_dir,
                filename
            )

            # Save the actual image to disk
            with open(image_path, "wb") as image_file:
                image_file.write(image_data["image"])

            # Find where this image appears on the page
            image_rects = page.get_image_rects(xref)

            for rect_index, rect in enumerate(image_rects):

                page_data["blocks"].append({
                    "type": "image",
                    "index": image_index,
                    "xref": xref,
                    "extension": extension,
                    "width": image_data["width"],
                    "height": image_data["height"],
                    "filename": filename,
                    "path": image_path,
                    "bbox": [
                        rect.x0,
                        rect.y0,
                        rect.x1,
                        rect.y1
                    ]
                })

        document["pages"].append(page_data)

    pdf.close()

    return document