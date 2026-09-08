import json

from pdf_extractor import extract_pdf
from agents import format_article


PDF_FILE = "../sample.pdf"


with open(PDF_FILE, "rb") as file:
    pdf_bytes = file.read()


document = extract_pdf(pdf_bytes)


html = format_article(document)


print("\n========== GENERATED HTML ==========\n")

print(html)


with open(
    "../generated_article.html",
    "w",
    encoding="utf-8"
) as file:

    file.write(html)


print("\n====================================")
print("Saved to generated_article.html")