from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import shutil
from datetime import datetime

from pdf_extractor import extract_pdf
from agents import format_article
from accessibility import review_html


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
OUTPUT_ROOT = os.path.join(PROJECT_ROOT, "output")


app = Flask(
    __name__,
    static_folder="../frontend",
    static_url_path=""
)
CORS(app)


def save_html_bundle(html, document):
    """Save a packaged HTML export with all extracted images in one folder."""
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle_dir = os.path.join(OUTPUT_ROOT, f"article_{timestamp}")
    images_dir = os.path.join(bundle_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    copied_images = set()
    for page in document.get("pages", []):
        for block in page.get("blocks", []):
            if block.get("type") != "image":
                continue

            source_path = block.get("path")
            filename = block.get("filename")

            if not source_path or not filename or filename in copied_images:
                continue

            copied_images.add(filename)

            destination = os.path.join(images_dir, filename)
            if os.path.exists(source_path):
                shutil.copy2(source_path, destination)

    bundle_html = html.replace('src="/extracted_images/', 'src="images/')
    bundle_html = bundle_html.replace('src="images/', 'src="images/')

    html_path = os.path.join(bundle_dir, "index.html")
    with open(html_path, "w", encoding="utf-8") as html_file:
        html_file.write(bundle_html)

    download_url = f"/exports/{os.path.basename(bundle_dir)}/index.html"

    return {
        "bundle_dir": bundle_dir,
        "bundle_name": os.path.basename(bundle_dir),
        "html_path": html_path,
        "download_url": download_url,
        "image_count": len(copied_images),
    }


@app.route("/")
def index():
    """Serve the frontend HTML"""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/exports/<path:relative_path>")
def serve_export(relative_path):
    """Serve saved HTML bundles and their images."""
    return send_from_directory(OUTPUT_ROOT, relative_path)


@app.route("/extracted_images/<filename>")
def serve_image(filename):
    """Serve extracted images to the frontend"""
    images_dir = os.path.join(os.path.dirname(__file__), "extracted_images")
    return send_from_directory(images_dir, filename)


@app.route("/convert", methods=["POST"])
def convert():

    # -----------------------------------------
    # Check that a PDF was uploaded
    # -----------------------------------------

    if "pdf" not in request.files:
        return jsonify({
            "error": "No PDF file uploaded"
        }), 400

    pdf = request.files["pdf"]

    if pdf.filename == "":
        return jsonify({
            "error": "No PDF file selected"
        }), 400

    if not pdf.filename.lower().endswith(".pdf"):
        return jsonify({
            "error": "File must be a PDF"
        }), 400

    try:

        # -----------------------------------------
        # STEP 1: Extract PDF
        # -----------------------------------------

        pdf_bytes = pdf.read()

        document = extract_pdf(pdf_bytes)

        # -----------------------------------------
        # STEP 2: Ask AI to create accessible HTML
        # -----------------------------------------

        html = format_article(document)

        # Save a self-contained bundle for export/download.
        export_bundle = save_html_bundle(html, document)

        # -----------------------------------------
        # Fix image paths for frontend context
        # Replace "images/filename" with "/extracted_images/filename"
        # -----------------------------------------

        browser_html = html.replace('src="images/', 'src="/extracted_images/')

        # -----------------------------------------
        # STEP 3: Review the generated HTML
        # -----------------------------------------

        issues = review_html(browser_html)

        # -----------------------------------------
        # STEP 4: Send everything to frontend
        # -----------------------------------------

        return jsonify({
            "html": browser_html,
            "issues": issues,
            "document": document,
            "bundle": export_bundle
        })

    except Exception as error:

        print("Conversion error:", error)

        return jsonify({
            "error": str(error)
        }), 500


if __name__ == "__main__":
    app.run(
        host="localhost",
        port=5001,
        debug=True
    )