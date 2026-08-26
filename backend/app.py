from flask import Flask, request, jsonify
from flask_cors import CORS

from pdf_extractor import extract_pdf
from agents import format_article
from accessibility import review_html


app = Flask(__name__)
CORS(app)


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

        # -----------------------------------------
        # STEP 3: Review the generated HTML
        # -----------------------------------------

        issues = review_html(html)

        # -----------------------------------------
        # STEP 4: Send everything to frontend
        # -----------------------------------------

        return jsonify({
            "html": html,
            "issues": issues,
            "document": document
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