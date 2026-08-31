"""
Image and Caption Association Module

Associates extracted images with their nearby caption text blocks
using bounding box proximity analysis.

This module enriches the document structure so that:
- Each image knows which text blocks are its captions
- Caption text is preserved unchanged
- Images and captions can be rendered together as semantic <figure> elements
- Vision AI can later generate alt text for images
"""

import math


def associate_images_with_captions(document):
    """
    Analyzes each page and associates images with nearby text blocks
    that are likely captions.

    Args:
        document: The extracted document structure from pdf_extractor.py

    Returns:
        Enhanced document with image-caption associations
    """

    enhanced_document = {
        "metadata": document["metadata"],
        "pages": []
    }

    for page in document["pages"]:
        enhanced_page = associate_page_images(page)
        enhanced_document["pages"].append(enhanced_page)

    return enhanced_document


def associate_page_images(page):
    """
    For a single page, find images and their nearby caption blocks.

    Strategy:
    1. Separate blocks into text and image blocks
    2. For each image, find the closest text blocks
    3. Prefer text blocks directly below or above the image
    4. Mark found text blocks with image association metadata
    5. Return enriched page structure
    """

    text_blocks = []
    image_blocks = []
    other_blocks = []

    # Separate blocks by type
    for idx, block in enumerate(page.get("blocks", [])):
        block_with_idx = {**block, "original_index": idx}

        if block["type"] == "text":
            text_blocks.append(block_with_idx)
        elif block["type"] == "image":
            image_blocks.append(block_with_idx)
        else:
            other_blocks.append(block_with_idx)

    # For each image, find its caption
    image_associations = {}

    for image_block in image_blocks:
        image_bbox = image_block["bbox"]
        caption_blocks = find_caption_blocks(
            image_bbox,
            text_blocks
        )
        image_associations[image_block["original_index"]] = {
            "image": image_block,
            "captions": caption_blocks
        }

    # Reconstruct page with metadata about associations
    enhanced_page = {
        "page_number": page["page_number"],
        "width": page.get("width"),
        "height": page.get("height"),
        "blocks": [],
        "image_associations": image_associations
    }

    for idx, block in enumerate(page.get("blocks", [])):
        enhanced_block = block.copy()

        # Mark text blocks that are captions
        if block["type"] == "text":
            enhanced_block["is_caption"] = False
            enhanced_block["caption_for_image_index"] = None

            for img_idx, assoc in image_associations.items():
                for caption_info in assoc["captions"]:
                    if caption_info["original_index"] == idx:
                        enhanced_block["is_caption"] = True
                        enhanced_block["caption_for_image_index"] = img_idx
                        break

        enhanced_page["blocks"].append(enhanced_block)

    return enhanced_page


def find_caption_blocks(image_bbox, text_blocks, max_distance=150):
    """
    Find text blocks that are likely captions for an image.

    Strategy:
    - Look for text blocks immediately above or below the image
    - Calculate vertical distance (preferred) and horizontal overlap
    - Return blocks sorted by proximity
    - Typically one or two blocks are captions

    Args:
        image_bbox: [x0, y0, x1, y1] bounding box of image
        text_blocks: List of text block dicts with bbox
        max_distance: Maximum pixels away to consider as caption

    Returns:
        List of text block metadata dicts, sorted by proximity
    """

    img_x0, img_y0, img_x1, img_y1 = image_bbox

    candidates = []

    for text_block in text_blocks:
        text_bbox = text_block["bbox"]
        txt_x0, txt_y0, txt_x1, txt_y1 = text_bbox

        # Calculate vertical distance
        # Negative if text is above image, positive if below
        if txt_y1 < img_y0:
            # Text is above image
            vertical_distance = img_y0 - txt_y1
            position = "above"
        elif txt_y0 > img_y1:
            # Text is below image
            vertical_distance = txt_y0 - img_y1
            position = "below"
        else:
            # Text overlaps vertically with image - not a caption
            vertical_distance = float('inf')
            position = "overlapping"

        if vertical_distance > max_distance:
            continue

        # Calculate horizontal overlap
        # If text is directly above/below, prefer good horizontal alignment
        x_overlap = max(0, min(img_x1, txt_x1) - max(img_x0, txt_x0))
        text_width = txt_x1 - txt_x0
        overlap_ratio = x_overlap / text_width if text_width > 0 else 0

        # Calculate total proximity score (lower is better)
        # Prefer text that is close vertically and aligned horizontally
        proximity_score = vertical_distance

        if overlap_ratio < 0.3:
            # Penalize text that doesn't overlap much horizontally
            proximity_score += 50

        candidates.append({
            "block": text_block,
            "original_index": text_block["original_index"],
            "text": text_block["text"],
            "vertical_distance": vertical_distance,
            "position": position,
            "overlap_ratio": overlap_ratio,
            "proximity_score": proximity_score
        })

    # Sort by proximity score and return top candidates
    candidates.sort(key=lambda x: x["proximity_score"])

    # Usually 1-2 blocks are captions; return top 2
    return candidates[:2]


def get_figure_element_for_image(
    page,
    image_idx,
    source_blocks_by_id
):
    """
    Generate a <figure> element for an image with its caption.

    Once classifications have been done, this function can construct
    the proper HTML figure element including the image, caption,
    and eventual alt text.

    Args:
        page: Page data with image_associations metadata
        image_idx: Index of the image in the page
        source_blocks_by_id: Dict mapping block IDs to their source text

    Returns:
        Dict with figure metadata for HTML rendering, or None if no image found
    """

    if "image_associations" not in page:
        return None

    if image_idx not in page["image_associations"]:
        return None

    assoc = page["image_associations"][image_idx]
    image_block = assoc["image"]
    caption_blocks = assoc["captions"]

    figure_data = {
        "type": "figure",
        "image": {
            "filename": image_block["filename"],
            "path": image_block["path"],
            "width": image_block["width"],
            "height": image_block["height"],
            "alt_text": None  # Will be filled in by vision AI
        },
        "captions": []
    }

    for caption_info in caption_blocks:
        figure_data["captions"].append({
            "text": caption_info["text"],
            "original_index": caption_info["original_index"]
        })

    return figure_data
