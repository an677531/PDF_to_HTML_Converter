# PDFHMTLConverter

> ⚠️ **Work in progress — currently not working reliably.**
>
> This project is still under development. The majority of basic pieces are in place, but the full PDF → accessible HTML conversion is **not finished and should not be used yet.**.

A small Python project that converts PDFs into semantic, accessible HTML.

The main idea is simple:

**AI decides what a piece of text is. It does not rewrite the text.**

## How it works

```text
PDF
 ↓
PyMuPDF
 ↓
Extract text + images
 ↓
Ollama classifies the text
 ↓
Python builds the HTML
 ↓
Accessibility check
```

The original PDF text stays unchanged. Ollama only classifies blocks as things like:

* heading
* paragraph
* caption
* byline
* list
* other

## Tech

* Python
* Flask
* PyMuPDF
* Ollama
* llama3.2
* HTML/CSS/JavaScript

## Project structure

```text
PDFHMTLConverter/
├── backend/
│   ├── app.py
│   ├── pdf_extractor.py
│   ├── ollama_client.py
│   ├── agents.py
│   ├── accessibility.py
│   └── tests
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
│
├── sample.pdf
└── README.md
```

## Run it

Install the Python dependencies:

```bash
pip install -r backend/requirements.txt
```

Make sure Ollama is running and `llama3.2` is installed:

```bash
ollama list
```

Start the backend:

```bash
cd backend
python3 app.py
```

The API runs on:

```text
http://localhost:5001
```

## Test the API

From the `backend` folder:

```bash
curl -X POST \
  -F "pdf=@../sample.pdf" \
  http://localhost:5001/convert
```

The response contains:

```json
{
  "document": {},
  "html": "...",
  "issues": []
}
```

## Current status

The basic pieces of the PDF → HTML pipeline are working, but the project as a whole is **not finished**.

Working or partially working:

* PDF text extraction
* Image extraction
* Ollama classification
* Semantic HTML generation
* Accessibility checking
* Flask API

Still being worked on:

* Better image/caption handling
* AI-generated image alt text
* More accessibility checks
* Browser testing
* More automated tests
* Overall reliability

## Why this project?

PDFs often contain useful information but are not very accessible.

The goal of this project is to turn that content into cleaner semantic HTML while **keeping the original text intact**.

The AI helps understand the structure of the document. Python controls the actual output.

**This is a development project, not a finished application.**
