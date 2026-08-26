import json

from pdf_extractor import extract_pdf
from agents import format_article


PDF_FILE = "../sample.pdf"


# -----------------------------------------
# Read PDF
# -----------------------------------------

with open(PDF_FILE, "rb") as file:
    pdf_bytes = file.read()


# -----------------------------------------
# Extract PDF
# -----------------------------------------

document = extract_pdf(pdf_bytes)


# -----------------------------------------
# Send document to Ollama
# -----------------------------------------

html = format_article(document)


# -----------------------------------------
# Display generated HTML
# -----------------------------------------

print("\n========== GENERATED HTML ==========\n")

print(html)


# -----------------------------------------
# Save HTML so we can inspect it
# -----------------------------------------

with open(
    "../generated_article.html",
    "w",
    encoding="utf-8"
) as file:

    file.write(html)


print("\n====================================")
print("Saved to generated_article.html")