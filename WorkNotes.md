============================================================
ACCESSIBLE NEWS AI CONVERTER — SESSION NOTES
============================================================

Date: August 24, 2026

PROJECT:
PDFHMTLConverter

CURRENT GOAL:
Convert PDF documents into accessible semantic HTML while preserving
the original source text.

IMPORTANT DESIGN PRINCIPLE:

"AI determines what the text IS; AI does not determine what the text SAYS."

The source PDF text must be preserved.

Ollama should classify extracted content rather than generate HTML.

============================================================
CURRENT PROJECT STRUCTURE
============================================================

PDFHMTLConverter/

    sample.pdf

    frontend/
        index.html
        style.css
        app.js

    backend/
        app.py
        pdf_extractor.py
        ollama_client.py
        agents.py
        accessibility.py

        test_extraction.py
        test_formatter.py

        extracted_images/
            page_1_image_1.png

    requirements.txt

The project has intentionally NOT been split into lots of additional
files. Keep the architecture simple unless a new file is genuinely
necessary.

============================================================
DEPENDENCIES
============================================================

Installed successfully:

flask
flask-cors
pymupdf
requests

IMPORTANT:

The correct package is:

requests

NOT:

request

requirements.txt exists but was previously empty.

NEXT SESSION:
Populate requirements.txt with the actual dependencies.

Likely contents:

Flask
flask-cors
PyMuPDF
requests

Do not install unnecessary packages.

============================================================
OLLAMA
============================================================

Ollama is installed and working.

Installed/tested model:

llama3.2

Python -> Ollama connection works.

Ollama previously returned malformed JSON on at least one request.

Example error:

JSON error: Invalid \escape: line 32 column 306 (char 1608)

Then another request successfully returned HTTP 200.

This means the Ollama pipeline is functional but JSON output needs
more robust handling/validation.

============================================================
PDF EXTRACTION
============================================================

PyMuPDF extraction is working.

sample.pdf is the current test PDF.

The extractor currently captures:

- page metadata
- page number
- page width
- page height
- text blocks
- text bounding boxes
- image detection
- image width
- image height
- image xref
- image extension
- extracted image filename
- extracted image path

IMAGE EXTRACTION IS NOW WORKING.

The sample PDF produced:

page_1_image_1.png

The image was inspected manually and looks correct.

Current extracted image metadata looks like:

{
    "type": "image",
    "index": 1,
    "xref": 75,
    "extension": "png",
    "width": 720,
    "height": 216,
    "filename": "page_1_image_1.png",
    "path": ".../backend/extracted_images/page_1_image_1.png"
}

IMPORTANT:
Image extraction should now be considered WORKING.

Do NOT spend the next session redoing basic image extraction unless
a specific bug appears.

============================================================
PDF EXTRACTION TEST
============================================================

test_extraction.py successfully extracts sample.pdf.

The output shows:

PDF METADATA
page_count = 3

PAGE 1
14 blocks

Page 1 contains one extracted image:

720x216
page_1_image_1.png

PAGE 2
11 text blocks

PAGE 3
8 text blocks

Bounding boxes are also being printed.

The extractor is therefore producing useful structured document data.

============================================================
CURRENT pdf_extractor.py
============================================================

The extractor was modified so images are actually written to:

backend/extracted_images/

and image metadata is stored in the document JSON.

This part is working.

============================================================
CURRENT BACKEND
============================================================

Flask backend is in:

backend/app.py

Current route:

POST /convert

The backend does:

1. Check PDF upload.
2. Read PDF bytes.
3. Call extract_pdf().
4. Pass structured document to format_article().
5. Pass resulting HTML to review_html().
6. Return JSON containing:

{
    "html": ...,
    "issues": ...,
    "document": ...
}

Current Flask endpoint is working on PORT 5001.

IMPORTANT:
Port 5000 is being occupied by macOS AirPlay/Control Center.

Previously:

lsof -i :5000

showed:

ControlCe ... LISTEN
Python ... LISTEN

Attempting to run Flask on port 5000 caused:

Address already in use

and curl to port 5000 reached AirTunes/AirPlay instead of Flask.

Therefore:

USE PORT 5001 FOR NOW.

Current command:

python3 app.py

runs Flask on:

http://localhost:5001

Current Flask configuration:

host="localhost"
port=5001
debug=True

============================================================
FRONTEND STATUS
============================================================

FRONTEND IS BEING SKIPPED FOR NOW.

Do not spend the next session debugging frontend/CORS unless specifically
requested.

The frontend previously had issues because index.html was opened directly
using file://.

Then it was correctly served using:

cd "/Users/tony/Desktop/CAH Computer Support/PDFHMTLConverter/frontend"

python3 -m http.server 8080

Frontend then loaded successfully at:

http://localhost:8080

However, for now we are intentionally focusing on the backend.

============================================================
TESTING THE BACKEND
============================================================

Use curl directly instead of the frontend.

From the project root:

curl -s -X POST \
  -F "pdf=@sample.pdf" \
  http://localhost:5001/convert

This successfully reached Flask.

The server returned:

HTTP 200

and JSON.

IMPORTANT:

A GET request to /convert is NOT a valid test.

This:

curl http://localhost:5001/convert

returns:

405 METHOD NOT ALLOWED

because /convert only accepts POST.

Correct test:

curl -s -X POST -F "pdf=@sample.pdf" http://localhost:5001/convert

============================================================
CURRENT END-TO-END RESULT
============================================================

The backend currently successfully performs:

PDF
 ↓
PyMuPDF extraction
 ↓
structured document JSON
 ↓
Ollama
 ↓
HTML generation
 ↓
accessibility review
 ↓
JSON response

The final curl response included:

"document": {
    ...
}

"html": "<article>\n<h1>EXACT SOURCE TEXT</h1>\n</article>"

"issues": [
    {
        "message": "Missing alt text for the image or other media, making it inaccessible to screen readers and visually impaired users.",
        "severity": "error",
        "type": "missing_alt"
    }
]

IMPORTANT:
The backend pipeline itself is now responding successfully.

However, the HTML result:

<h1>EXACT SOURCE TEXT</h1>

is NOT the desired final output.

This indicates the current Ollama/agents prompt or fallback behavior needs
to be corrected.

============================================================
CURRENT AI ARCHITECTURE
============================================================

Desired pipeline:

PDF
 ↓
PyMuPDF
 ↓
Structured document JSON
 ↓
Ollama semantic classification
 ↓
Python generates HTML
 ↓
HTML validation/sanitization
 ↓
Accessibility reviewer
 ↓
Final HTML + issues

Ollama MUST NOT generate HTML.

Ollama should return JSON such as:

{
    "blocks": [
        {
            "type": "heading",
            "text": "From the Guest Editor"
        },
        {
            "type": "paragraph",
            "text": "On Monday, January 28, 2013..."
        }
    ]
}

Python then turns that into HTML.

============================================================
AI CLASSIFICATION TYPES
============================================================

Ollama should classify text blocks as:

- heading
- paragraph
- caption
- byline
- list
- other

Potentially later:

- quote
- link
- section heading
- author

But keep the first implementation simple.

============================================================
IMPORTANT CONTENT RULE
============================================================

AI is NOT allowed to rewrite the source text.

AI determines:

"What is this block?"

AI does NOT determine:

"What should this text say?"

The original extracted text should be passed through unchanged.

This is important for preserving the integrity of academic/news/publication
content.

============================================================
agents.py
============================================================

agents.py currently:

- sends structured PDF text to Ollama
- asks Ollama to classify blocks
- parses JSON
- validates the response
- calls build_html()
- Python generates HTML
- escape_html() protects generated HTML from raw source text

A validation improvement was added after:

data = json.loads(result)

The code should contain:

if "blocks" not in data:

    raise ValueError(
        "Ollama response does not contain a blocks array."
    )

if not isinstance(data["blocks"], list):

    raise ValueError(
        "Ollama blocks value is not a list."
    )

Then:

return build_html(data)

============================================================
KNOWN OLLAMA PROBLEM
============================================================

At least one Ollama response failed JSON parsing:

JSON error:
Invalid \escape: line 32 column 306 (char 1608)

Then a later request succeeded.

This is likely because the model occasionally returns invalid JSON
characters/escaping.

NEXT SESSION:
Improve JSON reliability.

Possible approaches, in order:

1. Strengthen the prompt.
2. Explicitly require valid JSON.
3. Tell the model not to use markdown/code fences.
4. Tell the model to preserve text exactly.
5. Validate JSON after parsing.
6. If needed, strip accidental ```json fences before json.loads().
7. If needed, retry once when invalid JSON is returned.

Do NOT jump immediately to a complicated architecture.

============================================================
HTML GENERATION
============================================================

Python should generate the HTML.

The earlier formatter test successfully produced HTML resembling:

<article>

<h3>Rhetorical Treasure Hunting: Geocaching and the Usage of Multiple Literacies</h3>

<p>In B. Moe` Corbett’s study, “Rhetorical Treasure Hunting:
Geocaching and the Usage of Multiple Literacies,” the author took
her hobby of geocaching and turned it into a research project
for her ENC1102 class...</p>

</article>

This was considered a successful formatter test.

However, the current live /convert response returned:

<h1>EXACT SOURCE TEXT</h1>

Therefore, the formatter currently needs investigation.

Likely first task tomorrow:

Inspect agents.py and determine why the current live request is returning
the placeholder/fallback HTML instead of the actual classified blocks.

============================================================
ACCESSIBILITY REVIEW
============================================================

accessibility.py currently reviews the generated HTML.

The current response correctly detected the extracted image as lacking
alt text.

Example:

{
    "severity": "error",
    "type": "missing_alt",
    "message": "Missing alt text for the image or other media, making it inaccessible to screen readers and visually impaired users."
}

This is actually useful because it proves the accessibility reviewer
is seeing the generated HTML.

Eventually the frontend should display:

- errors
- warnings
- info

But frontend work is deferred.

============================================================
IMAGE ACCESSIBILITY PLAN
============================================================

Image extraction is DONE.

Next image-related work should be:

1. Associate extracted images with nearby captions/text.
2. Determine which text is a real figure caption.
3. Preserve original captions as <figcaption>.
4. Choose/configure a vision-capable Ollama model.
5. Send image to vision model.
6. Generate useful alt text.
7. Insert alt text into generated HTML.
8. Run accessibility review.

IMPORTANT DISTINCTION:

AI-generated alt text describes visual information.

The original PDF caption remains the actual figcaption.

Never replace an original caption with AI-generated alt text.

Desired eventual HTML:

<figure>

    <img
        src="images/page-3-image-1.jpg"
        alt="A student presenting research at the Knights Write Showcase."
    >

    <figcaption>
        Nicole Minnis presents her research at the Knights Write Showcase.
    </figcaption>

</figure>

============================================================
CURRENT DEVELOPMENT PRIORITY
============================================================

The original plan was:

1. Modify pdf_extractor.py to save images.                  DONE
2. Run extraction on sample.pdf.                           DONE
3. Inspect extracted images.                               DONE
4. Add image metadata/caption association.                 NEXT
5. Choose/configure vision-capable Ollama model.           LATER
6. Build image accessibility agent.                        LATER
7. Integrate image alt text into HTML.                      LATER
8. Add HTML validation/sanitization.                       LATER
9. Build accessibility reviewer.                           PARTIAL
10. Connect everything through Flask /convert.              DONE/PARTIAL
11. Test from frontend.                                     DEFERRED

BUT:

Before continuing with image AI, fix the current HTML generation
problem.

The current backend response proves the pipeline works, but the HTML
output is still a placeholder.

============================================================
TOMORROW'S RECOMMENDED ORDER
============================================================

START HERE:

1. Do NOT touch the frontend.

2. Do NOT add more files unless necessary.

3. Do NOT redesign the whole project.

4. Open agents.py.

5. Inspect why /convert is returning:

   <article>
   <h1>EXACT SOURCE TEXT</h1>
   </article>

6. Run test_formatter.py separately.

7. Compare test_formatter.py output against /convert output.

8. Fix the discrepancy.

9. Make sure Ollama returns valid classification JSON.

10. Make sure Python builds real semantic HTML from those classifications.

11. Test:

   curl -s -X POST -F "pdf=@sample.pdf" \
   http://localhost:5001/convert

12. Confirm the response contains actual source text, not the placeholder.

13. Only after that, continue with image/caption association.

============================================================
IMPORTANT COMMANDS
============================================================

Start backend:

cd backend
python3 app.py

Backend:

http://localhost:5001

Test endpoint:

curl -s -X POST -F "pdf=@sample.pdf" \
http://localhost:5001/convert

Test extraction:

cd backend
python3 test_extraction.py

Test formatter:

cd backend
python3 test_formatter.py

Check port 5000:

lsof -i :5000

Check port 5001:

lsof -i :5001

============================================================
PORT ISSUE
============================================================

Port 5000 is currently problematic because macOS Control Center /
AirPlay Receiver is listening there.

Do NOT waste time trying to force Flask onto port 5000.

Use:

5001

for the backend.

============================================================
WHAT IS WORKING
============================================================

✓ Ollama installed
✓ llama3.2 installed
✓ Python -> Ollama connection works
✓ PyMuPDF installed
✓ PDF extraction works
✓ Text blocks extracted
✓ Bounding boxes extracted
✓ Images detected
✓ Images saved to disk
✓ Extracted image looks correct
✓ Structured document JSON works
✓ Flask works
✓ /convert POST endpoint works
✓ CORS is configured
✓ curl can successfully POST PDF to Flask
✓ Accessibility reviewer detects missing alt text
✓ Backend can return JSON with document/html/issues

============================================================
WHAT IS NOT FINISHED
============================================================

✗ Live HTML generation currently returns placeholder HTML
✗ Ollama occasionally returns invalid JSON
✗ Image/caption association not implemented
✗ Vision model not configured
✗ AI alt text not implemented
✗ Final HTML validation/sanitization not implemented
✗ Accessibility reviewer needs expansion
✗ requirements.txt needs to be populated
✗ Frontend integration is deferred

============================================================
BIG PICTURE
============================================================

The project is actually in a good place.

The infrastructure works.

The next goal is NOT to add more architecture.

The next goal is to make the existing pipeline produce correct,
source-preserving semantic HTML consistently.

Once that works:

PDF
 ↓
structured extraction
 ↓
semantic classification
 ↓
Python-generated HTML
 ↓
image/caption handling
 ↓
vision alt text
 ↓
accessibility review
 ↓
final accessible article

Keep the implementation simple and incremental.

============================================================
END OF SESSION NOTES
============================================================


============================================================
CURRENT HANDOFF - AUGUST 25, 2026
============================================================

This section supersedes stale status above. The older notes are retained
as project history, but the current verified state is described here.

============================================================
VERIFIED CURRENT STATE
============================================================

The backend conversion pipeline works end to end:

sample.pdf
        -> PyMuPDF extraction
        -> page-level Ollama semantic classification
        -> Python-generated semantic HTML
        -> Ollama accessibility review
        -> Flask JSON response

The core rule remains:

"AI determines what the text IS; AI does not determine what the text SAYS."

Python owns the authoritative extracted source text. Ollama returns only
classification data using block IDs. Python maps those IDs back to source
blocks and renders escaped HTML. Ollama cannot replace source text.

Verified environment:

- Python 3.14.3
- Python executable: /usr/local/bin/python3
- PyMuPDF 1.27.2.3 imports as fitz
- Ollama 0.20.6
- Ollama executable: /usr/local/bin/ollama
- Ollama server: http://127.0.0.1:11434
- Installed model: llama3.2:latest
- Flask backend: http://localhost:5001

The declared dependencies are in backend/requirements.txt:

Flask
flask-cors
PyMuPDF
requests

============================================================
CURRENT FILE RESPONSIBILITIES
============================================================

backend/app.py

- Exposes POST /convert on port 5001.
- Validates the uploaded PDF.
- Calls extract_pdf(), format_article(), and review_html().
- Returns document, html, and issues.

backend/pdf_extractor.py

- Extracts page metadata, text blocks, bounding boxes, and images.
- Saves extracted images under backend/extracted_images/.
- Basic extraction is working. Do not redo it unless a specific bug appears.

backend/agents.py

- Builds stable page-N-text-N block IDs.
- Sends one page of source text blocks to Ollama at a time.
- Requires exactly one classification for every source block on that page.
- Allows heading, paragraph, caption, byline, list, and other.
- Rejects unknown or duplicate IDs, missing IDs, invalid types, and invalid
    heading levels before HTML rendering.
- Strips accidental json code fences safely.
- Retries malformed JSON or invalid classification structure at most once
    per page. A second failure raises ValueError; it never fabricates or
    silently discards source blocks.
- Generates HTML in Python and escapes source text.

backend/ollama_client.py

- Calls http://localhost:11434/api/generate using model llama3.2.
- Requests JSON output.
- Uses temperature 0 and num_predict 4096 for more deterministic output.

backend/accessibility.py

- Sends generated HTML to Ollama for accessibility review.
- Returns the review issues list.
- Further accessibility improvements are still pending.

frontend/index.html

- Defines the article preview element as id="preview".

frontend/app.js

- Uploads the selected PDF to http://localhost:5001/convert.
- Assigns the returned result.html to #preview.
- Displays conversion errors in #preview using textContent.
- Uses innerHTML only for the HTML returned by the backend conversion.

============================================================
VERIFIED TEST RESULTS
============================================================

Run backend commands from the backend directory:

cd backend

python3 test_extraction.py

PASS. sample.pdf extracts successfully:

- 3 pages
- page 1 includes one extracted image
- text blocks and bounding boxes are present

python3 test_ollama.py

PASS. llama3.2 responds through the local Ollama API.

python3 -m unittest test_agents.py -v

PASS. 8 focused mocked classification tests:

- valid JSON
- accidental json fences
- malformed JSON followed by valid JSON on retry
- malformed JSON on both attempts
- missing blocks array
- unknown block ID
- invalid classification type
- invalid heading level

python3 test_formatter.py

PASS. The sample PDF produces HTML containing real source text and
semantic elements. The test writes generated_article.html at the project
root as an inspection artifact.

Live endpoint test:

python3 app.py

In another terminal, from backend/:

curl -s -X POST \
    -F "pdf=@../sample.pdf" \
    http://localhost:5001/convert

PASS. The endpoint returned HTTP 200 and JSON containing:

- document
- html
- issues

The generated HTML contained actual sample text such as:

Work Habits: A Self Study
From the Guest Editor

It contained h1, h3, and p elements. The string:

EXACT SOURCE TEXT

was absent.

The Flask process was stopped after validation. Ollama should remain
available on port 11434 when running formatter or endpoint tests.

============================================================
FRONTEND STATUS
============================================================

The previous frontend integration bug is fixed:

- Old app.js target: #output (did not exist)
- Current target: #preview (exists in index.html)

Static validation passed:

- node --check frontend/app.js
- #preview exists in frontend/index.html
- result.html is assigned to #preview
- errors use textContent
- no editor diagnostics were reported

Browser automation was not available, so the frontend upload-to-preview
workflow has NOT been browser-tested. Do not claim browser verification.

To serve the frontend manually:

cd frontend
python3 -m http.server 8080

Open http://localhost:8080 after starting the backend on port 5001.

============================================================
REMAINING TASKS - NEXT SESSION
============================================================

Priority 1: Improve image and caption handling.

1. Associate extracted images with nearby text using layout and bounding
     boxes.
2. Distinguish real PDF captions from ordinary text.
3. Preserve source captions as figcaption.
4. Add image elements with stable paths in generated HTML.
5. Choose a vision-capable Ollama model.
6. Generate useful alt text from image content without replacing captions.
7. Re-run accessibility review and confirm missing_alt issues improve.

Priority 2: Validate the frontend in a real browser.

1. Start Ollama, Flask, and the frontend server.
2. Upload sample.pdf through the UI.
3. Confirm the article appears in #preview.
4. Confirm headings, paragraphs, source text, and error handling.
5. Confirm EXACT SOURCE TEXT remains absent.

Priority 3: Improve backend quality after image work.

- Add HTML validation and sanitization appropriate for backend-generated
    HTML.
- Expand accessibility review validation and issue handling.
- Add tests for multi-page classification and image output.
- Consider more robust Ollama response diagnostics if model reliability
    problems recur.

Do not modify frontend styling, add frameworks, add databases, or add
dependencies unless a later requirement specifically needs them.
Do not move Flask to port 5000; macOS AirPlay/Control Center may occupy it.

============================================================
NEXT SESSION START HERE
============================================================

1. Read this CURRENT HANDOFF section first.
2. Do not redo Python/PyMuPDF or basic Ollama setup.
3. Check Ollama is running with:

     ollama list
     curl -s http://localhost:11434/api/tags

4. Inspect image/caption layout data in pdf_extractor.py.
5. Implement only the smallest image/caption step that can be tested.
6. Keep original PDF text authoritative at every stage.

============================================================
END CURRENT HANDOFF
============================================================