#!/usr/bin/env python3
"""
Test alt text generation functionality
"""

import os
import sys
import subprocess

# Add parent dir to path
sys.path.insert(0, os.path.dirname(__file__))

from image_alt_text import generate_alt_text_for_image


def check_ollama_models():
    """Check which models are available in Ollama"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print("Available Ollama models:")
        print(result.stdout)
        return result.stdout
    except Exception as e:
        print(f"Could not list Ollama models: {e}")
        return ""


def test_alt_text_generation():
    """Test generating alt text for the extracted image"""

    image_path = os.path.join(
        os.path.dirname(__file__),
        "extracted_images",
        "page_1_image_1.png"
    )

    if not os.path.exists(image_path):
        print(f"ERROR: Test image not found at {image_path}")
        print("Run test_extraction.py first to extract images.")
        return False

    print()
    print("=" * 60)
    print("IMAGE ALT TEXT GENERATION TEST")
    print("=" * 60)
    print()

    check_ollama_models()
    print()

    print(f"Testing alt text generation for: {os.path.basename(image_path)}")
    print(f"Image size: {os.path.getsize(image_path)} bytes")
    print()

    try:
        result = generate_alt_text_for_image(image_path)

        print("Result:")
        print(f"  Alt Text: {result.get('alt_text', 'N/A')}")
        print(f"  Description Type: {result.get('description_type', 'N/A')}")
        print(f"  Model Used: {result.get('model_used', 'N/A')}")
        print(f"  Confidence: {result.get('confidence', 0):.2f}")

        if result.get("warning"):
            print(f"  ⚠ Warning: {result['warning']}")

        if result.get("error"):
            print(f"  ✗ Error: {result['error']}")
            return False

        if result.get("alt_text"):
            print("\n✓ Alt text generation successful!")
            return True
        else:
            print("\n✗ Alt text generation returned empty")
            return False

    except Exception as e:
        print(f"✗ Error during alt text generation:")
        print(f"  {type(e).__name__}: {str(e)}")
        print()
        print("Troubleshooting:")
        print("  1. Is Ollama running? Start with: ollama serve")
        print("  2. Is llava model installed? Check with: ollama list")
        print("  3. If llava isn't installed yet, run: ollama pull llava")
        print("  4. System will fall back to text-only model (llama3.2)")
        return False


if __name__ == "__main__":
    print("Starting Ollama alt text test...")
    print()

    success = test_alt_text_generation()
    sys.exit(0 if success else 1)
