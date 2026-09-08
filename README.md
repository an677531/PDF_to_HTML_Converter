# PDF to HTML Converter with Local LLM

> ✅ **STATUS: READY FOR USE AND TESTING**
>
> The application is ready for local use, integration testing, and user feedback. Production deployment and official release still require environment hardening and confirmation of intellectual property ownership.

Convert PDF documents into semantic, accessible HTML using a local Large Language Model (LLM).

**Key Principle:** AI determines document structure; AI does not rewrite content. Original source text is always preserved.

---

## Project Overview

### How It Works

```text
PDF Document
    ↓
PyMuPDF Extraction (text + images + layout)
    ↓
Structured Document JSON
    ↓
Local LLM (via Ollama) - Semantic Classification
    ↓
Python HTML Generation
    ↓
Accessibility Review
    ↓
Portable HTML Bundle (HTML + images)
```

### What the LLM Does

The LLM classifies text blocks as:
- **heading** — Document titles/section headers
- **paragraph** — Body text
- **caption** — Figure/image captions
- **byline** — Author/attribution lines
- **list** — Bulleted or numbered lists
- **other** — Uncategorized content

The LLM **does not** generate HTML, rewrite content, or modify text. Python handles all HTML generation.

---

## System Requirements

### Minimum Requirements
- **CPU:** 4+ cores (8+ recommended)
- **RAM:** 8GB minimum, 16GB+ recommended
- **Disk:** 5GB free (for LLM model)
- **OS:** macOS, Linux, Windows 10/11

### Recommended for Production
- **GPU:** NVIDIA CUDA-capable GPU (8GB+ VRAM)
- **RAM:** 32GB+
- **Disk:** 10GB+ SSD
- **OS:** Linux (Ubuntu 20.04+)

### For NVIDIA Spark Machines
- NVIDIA CUDA 12.x
- cuDNN 9.x
- NVIDIA driver 550+
- 24GB+ VRAM recommended

---

## LLM Setup Guide

### Step 1: Install Ollama

Ollama is a lightweight framework for running LLMs locally.

#### macOS
```bash
# Download and install from:
# https://ollama.ai

# Or use Homebrew:
brew install ollama

# Verify installation:
ollama --version
```

#### Linux (Ubuntu/Debian)
```bash
# Install Ollama:
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation:
ollama --version

# Enable GPU support (NVIDIA):
# The installation script automatically detects NVIDIA GPUs
# For manual CUDA setup, see GPU Optimization section below
```

#### Windows
```bash
# Download installer from:
# https://ollama.ai/download/windows

# Run the installer and follow prompts
# Verify installation in PowerShell:
ollama --version
```

### Step 2: Choose and Pull an LLM

**Model Selection Guide:**

| Model | Size | Speed | Quality | VRAM | Best For |
|-------|------|-------|---------|------|----------|
| **llama2** | 7B | Fast | Good | 4GB | Entry-level, testing |
| **llama3** | 8B | Fast | Better | 4-5GB | Recommended default |
| **llama3.2** | 11B | Medium | Very Good | 6-8GB | Current default |
| **mixtral** | 46B | Slow | Excellent | 16GB | High accuracy |
| **neural-chat** | 7B | Very Fast | Good | 4GB | Speed-focused |
| **mistral** | 7B | Fast | Good | 4-5GB | Balanced |
| **llama3.1:70b** | 70B | Very Slow | Best-in-class | 48GB | NVIDIA Spark (elite) |

**Recommendations:**

- **Testing/Development:** `llama3.2` (best balance)
- **CPU-only machines:** `llama3` (8B)
- **Fast processing:** `neural-chat` (7B)
- **NVIDIA GPU (consumer):** `mixtral` (46B) or `llama3.2`
- **NVIDIA Spark (enterprise):** `llama3.1:70b` (70B)

### Step 3: Pull Your Chosen Model

```bash
# Pull the recommended model (llama3.2):
ollama pull llama3.2

# Or pull a different model:
ollama pull mixtral
ollama pull llama3.1:70b

# List installed models:
ollama list
```

**Expected sizes:**
- llama3.2 (11B) → ~7GB
- mixtral (46B) → ~28GB
- llama3.1:70b (70B) → ~42GB

### Step 4: Verify Ollama is Running

```bash
# Start Ollama in the background:
ollama serve

# In another terminal, test connectivity:
curl http://localhost:11434/api/tags

# Should return JSON listing your models
```

---

## Project Setup

### Prerequisites
- Python 3.8+
- pip or conda
- Ollama running with a model installed

### Complete Setup Instructions

#### 1. Clone/Navigate to Project
```bash
cd /path/to/PDFHMTLConverter
```

#### 2. Install Python Dependencies
```bash
pip install -r backend/requirements.txt
```

Expected packages:
- `Flask` — Web framework
- `flask-cors` — Cross-origin requests
- `PyMuPDF` — PDF extraction
- `requests` — HTTP client

#### 3. Verify Ollama Connection
```bash
cd backend

# Test Ollama connectivity:
python3 -c "
import requests
try:
    response = requests.get('http://localhost:11434/api/tags')
    print('✓ Ollama is running')
    print('Available models:', response.json())
except:
    print('✗ Cannot connect to Ollama')
    print('  Make sure: ollama serve is running')
"
```

#### 4. Start the Backend API
```bash
cd backend
python3 app.py
```

Expected output:
```
 * Serving Flask app 'app'
 * Running on http://localhost:5001
 * Debug mode: on
```

#### 5. Launch the Frontend (Optional, in another terminal)
```bash
cd frontend
python3 -m http.server 8080

# Access at: http://localhost:8080
```

---

## Replacing the Placeholder CSS

The converter generates semantic HTML classes rather than article-specific markup, so the visual design should be swapped via CSS instead of rewriting the HTML structure.

### Current placeholder file

The default temporary stylesheet lives in:

- frontend/article-placeholder.css

This file is intentionally neutral so a future project can replace it with the final publication theme without changing the generator logic.

### Required class contract

The generated article HTML should continue using the same semantic classes:

```html
<article class="article">
  <h1 class="article-heading article-heading--1">Title</h1>
  <p class="article-byline">By Jane Doe</p>
  <p class="article-paragraph">Body text</p>
  <figure class="article-figure">
    <img class="article-image" src="images/example.png" alt="Example image">
    <figcaption class="article-caption">Caption</figcaption>
  </figure>
</article>
```

Do not rename these classes unless you also update the generator in backend/agents.py and the stylesheet selectors together.

### How to swap in the final CSS

#### Option 1: Replace the placeholder file directly

1. Open frontend/article-placeholder.css
2. Replace the placeholder variables and selectors with the intended publication styling
3. Save the file
4. Refresh the browser

This is the simplest path for stage-one design work.

#### Option 2: Create a new theme file

1. Create a new file such as frontend/theme-brand.css
2. Copy the same class structure from the placeholder file
3. Update the HTML to link to the new stylesheet
4. Keep the generated article classes unchanged

Example:

```html
<link rel="stylesheet" href="theme-brand.css">
```

#### Option 3: Update the exported bundle CSS

When the converter creates a downloadable article bundle, it copies the stylesheet into the output folder and links it in the export HTML. If you want to use a different final stylesheet for exports:

1. Create the new CSS file
2. Place it in the same folder as the exported HTML file
3. Update the link inside the generated HTML to match the new file name
4. Keep the semantic class names the same

### Important rule

The generator owns the article structure. The stylesheet owns the visual appearance. As long as the semantic classes remain stable, any future design can replace the placeholder without breaking the converter flow.

---

## Testing the Application

### Test via API (cURL)

```bash
# From project root:
curl -X POST \
  -F "pdf=@sample.pdf" \
  http://localhost:5001/convert | python3 -m json.tool
```

Expected response:
```json
{
  "bundle": {
    "bundle_dir": "/path/to/output/article_YYYYMMDD_HHMMSS",
    "bundle_name": "article_YYYYMMDD_HHMMSS",
    "html_path": "/path/to/output/article_YYYYMMDD_HHMMSS/index.html",
    "image_count": 3
  },
  "document": { ... },
  "html": "...",
  "issues": [...]
}
```

### Test via Web UI

1. Open `http://localhost:8080` in your browser
2. Upload a PDF
3. Click "Convert"
4. Watch the loading indicator animate
5. View the generated HTML and accessibility issues
6. Download the HTML bundle

### Test Batch Processing

```bash
# Frontend supports multiple files
# Select multiple PDFs and convert
# Each file processes sequentially
# Preview updates for each file
```

---

## Performance Optimization

### CPU-Based Systems

**For best performance without GPU:**

```bash
# Use faster models:
ollama pull neural-chat  # 7B, very fast
ollama pull llama3       # 8B, balanced

# Reduce context length in backend/ollama_client.py:
# num_ctx: 512  # instead of 2048
```

### NVIDIA GPU Optimization

#### Verify CUDA Setup
```bash
# Check NVIDIA driver:
nvidia-smi

# Should show CUDA version and GPU memory

# Verify Ollama sees GPU:
ollama list

# Check if model loading shows GPU memory usage in nvidia-smi
```

#### Enable NVIDIA GPU in Ollama

**Linux:**
```bash
# NVIDIA GPU support is automatic if drivers are installed
# Verify by running a model:
ollama run llama3.2

# Watch nvidia-smi in another terminal
# Should show GPU memory usage
```

**macOS with M1/M2/M3 (Metal):**
```bash
# Metal acceleration is automatic
# No additional setup needed
```

#### Optimize for NVIDIA Spark

For maximum performance on high-end NVIDIA hardware:

```bash
# Use the largest available model:
ollama pull llama3.1:70b

# In backend/ollama_client.py, increase context:
# num_ctx: 4096  # Full context window
# num_batch: 512  # Larger batch size
# num_gpu: -1    # Use all GPU layers

# Monitor GPU usage:
watch -n 1 nvidia-smi
```

**Expected on NVIDIA Spark (8x A100 40GB):**
- Model: llama3.1:70b
- Response time: 2-5 seconds per PDF
- GPU utilization: 85-95%
- Memory usage: 36-39GB VRAM

---

## Troubleshooting

### Ollama Connection Issues

**Error:** `Cannot connect to Ollama`
```bash
# Solution 1: Verify Ollama is running:
ollama serve

# Solution 2: Check port availability:
lsof -i :11434

# Solution 3: On macOS, unblock firewall:
# System Preferences → Security & Privacy → Firewall Options
```

### Out of Memory

**Error:** `CUDA out of memory` or system freezing
```bash
# Solution 1: Use smaller model:
ollama pull llama3  # 8B instead of 11B

# Solution 2: Reduce context window in backend/ollama_client.py:
num_ctx=512  # Default is 2048

# Solution 3: Close other applications

# Solution 4: Check available GPU memory:
nvidia-smi
```

### PDF Extraction Fails

**Error:** `Failed to extract PDF` or `No pages found`
```bash
# Verify PyMuPDF is installed:
python3 -c "import fitz; print(fitz.__version__)"

# Try with a different PDF:
# Some PDFs have copy protection

# Check PDF validity:
pdfinfo sample.pdf  # macOS: brew install poppler
```

### Poor Quality HTML Output

**Issue:** HTML is incomplete or poorly formatted
```bash
# Likely causes:
# 1. Model not trained on classification task
# 2. Complex PDF layout
# 3. Ollama response timing out

# Solutions:
# Use llama3.2 or better
# Increase timeout in backend/app.py
# Check backend logs for Ollama errors
```

### NVIDIA GPU Not Used

**Verify GPU acceleration:**
```bash
# Terminal 1: Run a model:
ollama run llama3.2

# Terminal 2: Monitor GPU:
watch -n 1 nvidia-smi

# If GPU memory doesn't increase:
# 1. Check NVIDIA driver: nvidia-smi
# 2. Reinstall Ollama: sudo apt remove ollama && curl -fsSL https://ollama.ai/install.sh | sh
# 3. Verify CUDA: nvcc --version
```

---

## Configuration

### Backend Settings

Edit `backend/app.py`:
```python
# Flask server
host = "0.0.0.0"  # or "localhost"
port = 5001
debug = True      # Set to False for production
```

Edit `backend/ollama_client.py`:
```python
OLLAMA_MODEL = "llama3.2"  # Change model here
OLLAMA_URL = "http://localhost:11434"  # Remote Ollama support
num_ctx = 2048     # Context window
num_batch = 256    # Batch size
```

### Frontend Settings

Edit `frontend/app.js`:
```javascript
// Backend URL (for remote deployment):
const backendUrl = "http://localhost:5001/convert";

// Timeout for long conversions:
const timeout = 300000; // 5 minutes
```

---

## Project Structure

```
PDFHMTLConverter/
├── backend/
│   ├── app.py              # Flask API
│   ├── pdf_extractor.py    # PDF parsing
│   ├── ollama_client.py    # LLM interface
│   ├── agents.py           # HTML generation logic
│   ├── accessibility.py    # A11y checking
│   ├── requirements.txt    # Python dependencies
│   ├── test_*.py          # Unit tests
│   └── extracted_images/   # Temporary image storage
│
├── frontend/
│   ├── index.html         # UI
│   ├── app.js             # Client logic
│   └── style.css          # Styling
│
├── output/                # Exported HTML bundles
│   └── article_YYYYMMDD_HHMMSS/
│       ├── index.html
│       └── images/
│
├── sample.pdf             # Test document
├── README.md              # This file
└── WorkNotes.md           # Development notes
```

---

## Deployment

### Local Development
```bash
# Terminal 1:
ollama serve

# Terminal 2:
cd backend && python3 app.py

# Terminal 3 (optional):
cd frontend && python3 -m http.server 8080
```

### Remote Ollama Server

If running Ollama on a different machine:

```python
# In backend/ollama_client.py:
OLLAMA_URL = "http://192.168.1.100:11434"  # Remote IP
```

### Docker (Recommended for NVIDIA Spark)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install CUDA runtime
RUN apt-get update && apt-get install -y \
    libcuda1 \
    nvidia-utils

# Install Python deps
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./

EXPOSE 5001

CMD ["python3", "app.py"]
```

Build and run:
```bash
docker build -t pdf-html-converter .

docker run --gpus all \
  -p 5001:5001 \
  --env OLLAMA_URL=http://host.docker.internal:11434 \
  pdf-html-converter
```

---

## Next Steps & Development

### Current Status
- ✅ PDF extraction
- ✅ Image handling
- ✅ LLM integration
- ✅ HTML generation
- ✅ Accessibility checking
- ✅ Batch processing
- ✅ Loading indicators
- ✅ CSS placeholder styling
- ✅ Image alt text generation
- ✅ Frontend-backend integration testing
- 📋 Production hardening (future)

### Upcoming Features
- Template-based styling system
- Advanced image alt text generation
- Support for more document types
- Performance profiling dashboard
- Multi-language support

---

## Support & Troubleshooting

For issues:

1. Check [troubleshooting section](#troubleshooting) above
2. Verify Ollama is running: `ollama serve`
3. Test LLM directly: `ollama run llama3.2`
4. Check backend logs for detailed errors
5. Ensure all dependencies are installed: `pip install -r backend/requirements.txt`

---

## License & Intellectual Property

**Application Status:** Ready for local use and testing. Production deployment and official release require additional hardening and review.

**IP Ownership Status:** The intellectual property ownership of this project requires clarification. Current development does not involve a formalized IP agreement; however, the project may still be subject to applicable **University of Central Florida (UCF)** intellectual property policies, agreements, or assignment provisions.

**Important:** UCF ownership or other applicable intellectual property rights should be verified with **UCF administration** and, where appropriate, the relevant legal or technology-transfer office before this project is used officially, distributed, licensed, or otherwise released.



---

## Acknowledgments

- **PyMuPDF** — PDF extraction
- **Ollama** — Local LLM framework
- **Meta Llama** — Language models
- **Flask** — Web framework

---

**Last Updated:** September 8, 2026
**Status:** Ready for Use and Testing
**Target Deployment:** NVIDIA Spark (enterprise GPU cluster)
