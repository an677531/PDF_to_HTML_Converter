import json

from ollama_client import ask_ollama
from image_association import associate_images_with_captions
from image_alt_text import generate_alt_text_for_image


def format_article(document):

    # Associate images with nearby captions
    document_with_associations = associate_images_with_captions(document)

    simplified_document = {
        "metadata": document_with_associations["metadata"],
        "pages": []
    }
    source_blocks = []
    source_blocks_by_page = []
    page_image_associations = []  # Track image associations for HTML building

    for page_number, page in enumerate(document_with_associations["pages"], start=1):

        page_data = {
            "page_number": page_number,
            "blocks": []
        }

        text_index = 0
        page_source_blocks = []
        page_associations = page.get("image_associations", {})

        for block in page["blocks"]:

            if block["type"] == "text":

                text_index += 1
                block_id = f"page-{page_number}-text-{text_index}"

                source_block = {
                    "id": block_id,
                    "text": block["text"]
                }
                source_blocks.append(source_block)
                page_source_blocks.append(source_block)

                page_data["blocks"].append({
                    "id": block_id,
                    "text": block["text"]
                })

            elif block["type"] == "image":

                page_data["blocks"].append({
                    "type": "image",
                    "index": block["index"],
                    "width": block["width"],
                    "height": block["height"],
                    "filename": block["filename"],
                    "path": block["path"]
                })

        simplified_document["pages"].append(page_data)
        source_blocks_by_page.append(page_source_blocks)
        page_image_associations.append(page_associations)

    classifications = {"blocks": []}

    for page_source_blocks in source_blocks_by_page:
        page_classifications = classify_source_blocks(page_source_blocks)
        classifications["blocks"].extend(page_classifications["blocks"])

    return build_html(
        classifications,
        source_blocks,
        document_with_associations,
        page_image_associations
    )


def classify_source_blocks(source_blocks):

    prompt = f"""
You are analyzing a newspaper or magazine PDF.

Your ONLY job is to classify the existing extracted text.

DO NOT write HTML.
DO NOT summarize.
DO NOT rewrite.
DO NOT add information.
DO NOT invent headings.
DO NOT invent paragraphs.
DO NOT invent dates, URLs, authors, footnotes, titles,
sections, or copyright information.

For each text block, determine its semantic role. Return the block id
and classification only. Python will supply the source text unchanged.

Allowed types:
heading
paragraph
caption
byline
list
other

For headings, assign a level:

1 = document title
2 = major section
3 = subsection

If you are uncertain, use:

"type": "other"

Return ONLY valid JSON. Do not use Markdown or code fences. Do not add
explanatory text before or after the JSON. Return exactly
{len(source_blocks)} classification objects, one for every source block ID.

Use exactly this structure:

{{
    "blocks": [
        {{
            "id": "page-1-text-1",
            "type": "heading",
            "level": 1
        }}
    ]
}}

    SOURCE TEXT BLOCKS:

{json.dumps(
    source_blocks,
    indent=2,
    ensure_ascii=False
)}
"""

    source_ids = {block["id"] for block in source_blocks}
    result = ask_ollama(prompt)

    try:
        data = parse_classification_response(result, source_ids)
    except (json.JSONDecodeError, ValueError) as first_error:
        retry_prompt = (
            f"{prompt}\n\n"
            "Your previous response was invalid JSON or had an invalid "
            "classification structure. Return a corrected JSON object only, "
            "with no Markdown, code fences, or explanation."
        )
        retry_result = ask_ollama(retry_prompt)

        try:
            data = parse_classification_response(retry_result, source_ids)
        except json.JSONDecodeError as retry_error:
            raise ValueError(
                "Ollama returned invalid JSON after one retry."
            ) from retry_error
        except ValueError as retry_error:
            raise ValueError(
                "Ollama returned an invalid classification after one retry: "
                f"{retry_error}"
            ) from retry_error

    return data


def parse_classification_response(result, source_ids):

    data = json.loads(clean_json_response(result))

    if not isinstance(data, dict) or "blocks" not in data:
        raise ValueError(
            "Ollama response does not contain a blocks array."
        )

    if not isinstance(data["blocks"], list):
        raise ValueError(
            "Ollama blocks value is not a list."
        )

    returned_ids = []
    allowed_types = {
        "heading",
        "paragraph",
        "caption",
        "byline",
        "list",
        "other"
    }

    for block in data["blocks"]:

        if not isinstance(block, dict):
            raise ValueError("Ollama classification block is not an object.")

        block_id = block.get("id")
        block_type = block.get("type")

        if block_id not in source_ids:
            raise ValueError(
                f"Ollama returned unknown block ID: {block_id}"
            )

        if block_id in returned_ids:
            raise ValueError(
                f"Ollama returned duplicate block ID: {block_id}"
            )

        if block_type not in allowed_types:
            raise ValueError(
                f"Ollama returned invalid classification type: {block_type}"
            )

        if block_type == "heading" and block.get("level") not in [1, 2, 3]:
            raise ValueError(
                f"Ollama returned invalid heading level for block ID: {block_id}"
            )

        returned_ids.append(block_id)

    if set(returned_ids) != source_ids:
        raise ValueError(
            "Ollama response does not classify every source text block."
        )

    return data


def clean_json_response(result):

    cleaned = result.strip()

    if cleaned.startswith("```json") and cleaned.endswith("```"):
        cleaned = cleaned[7:-3].strip()
    elif cleaned.startswith("```") and cleaned.endswith("```"):
        cleaned = cleaned[3:-3].strip()

    return cleaned


def build_html(data, source_blocks=None, document_with_associations=None, page_image_associations=None):

    html = ["<article>"]

    classifications = {
        block.get("id"): block
        for block in data.get("blocks", [])
        if block.get("id")
    }

    blocks_to_render = source_blocks or [
        {
            "id": block.get("id"),
            "text": block.get("text", "")
        }
        for block in data.get("blocks", [])
    ]

    # Build a map of which text block IDs are captions for which images
    caption_to_image_map = {}  # block_id -> image_info

    if document_with_associations and page_image_associations:
        for page_num, page in enumerate(document_with_associations.get("pages", [])):
            page_associations = page_image_associations[page_num] if page_num < len(page_image_associations) else {}

            for img_idx, assoc in page_associations.items():
                for caption_info in assoc.get("captions", []):
                    # Build block ID for this caption
                    original_idx = caption_info.get("original_index")
                    # Count text blocks up to this index
                    text_count = 0
                    for i, block in enumerate(page.get("blocks", [])):
                        if block.get("type") == "text":
                            text_count += 1
                            if i == original_idx:
                                block_id = f"page-{page_num + 1}-text-{text_count}"
                                caption_to_image_map[block_id] = {
                                    "image": assoc["image"],
                                    "caption_text": caption_info.get("text", "")
                                }
                                break

    for source_block in blocks_to_render:

        block = classifications.get(source_block.get("id"), {})

        block_type = block.get("type")
        text = source_block.get("text", "").strip()

        if not text:
            continue

        if block_type == "heading":

            level = block.get("level", 2)

            if level not in [1, 2, 3]:
                level = 2

            html.append(
                f"<h{level}>{escape_html(text)}</h{level}>"
            )

        elif block_type == "paragraph":

            html.append(
                f"<p>{escape_html(text)}</p>"
            )

        elif block_type == "byline":

            html.append(
                f'<p class="byline">{escape_html(text)}</p>'
            )

        elif block_type == "caption":

            # Check if this caption is associated with an image
            block_id = source_block.get("id")
            if block_id in caption_to_image_map:
                image_info = caption_to_image_map[block_id]
                image_block = image_info["image"]

                # Generate alt text for the image
                image_path = image_block["path"]
                alt_text_result = generate_alt_text_for_image(image_path)
                alt_text = alt_text_result.get("alt_text", "")

                # Escape alt text for safety
                alt_text_escaped = escape_html(alt_text)

                # Render figure with image and caption
                html.append(
                    f'<figure><img src="images/{image_block["filename"]}" '
                    f'width="{image_block["width"]}" '
                    f'height="{image_block["height"]}" '
                    f'alt="{alt_text_escaped}"><figcaption>{escape_html(text)}</figcaption></figure>'
                )
            else:
                # Orphan caption with no associated image
                html.append(
                    f'<figure><figcaption>{escape_html(text)}</figcaption></figure>'
                )

        elif block_type == "list":

            html.append(
                f"<p>{escape_html(text)}</p>"
            )

        else:

            html.append(
                f"<p>{escape_html(text)}</p>"
            )

    html.append("</article>")

    return "\n".join(html)


def escape_html(text):

    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )