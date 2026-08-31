"""
Image Alt Text Generation Module

Uses Ollama with a vision model (llava) to generate descriptive alt text
for images based on the actual image content.

Important: Alt text describes visual information only; it does not replace
original captions extracted from the PDF.
"""

import base64
import json
import os
from ollama_client import ask_ollama


def generate_alt_text_for_image(image_path, max_length=200):
    """
    Generate descriptive alt text for an image using a vision model.

    Args:
        image_path: Full path to the image file
        max_length: Maximum length of alt text to generate

    Returns:
        Dict with 'alt_text' and 'confidence' keys, or None if generation fails
    """

    if not os.path.exists(image_path):
        return {
            "alt_text": None,
            "confidence": 0,
            "error": f"Image file not found: {image_path}"
        }

    try:
        # Read and encode the image
        with open(image_path, "rb") as img_file:
            image_data = base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        return {
            "alt_text": None,
            "confidence": 0,
            "error": f"Failed to read image: {str(e)}"
        }

    prompt = f"""You are generating alt text (alternative text) for an image in an academic publication.

Alt text is read aloud by screen readers for visually impaired users. It should:
- Describe what is visually present in the image
- Be factual and objective
- Be concise (aim for {max_length} characters or less)
- NOT include phrases like "image of" or "photo of"
- NOT repeat captions (those are provided separately)
- NOT make assumptions about people's identities

Focus on: objects, composition, colors, text visible in the image, and activities shown.

Respond with a JSON object containing:
{{
    "alt_text": "Your concise alt text here",
    "description_type": "photograph|screenshot|diagram|graph|illustration|other"
}}

Return ONLY valid JSON with no additional text, markdown, or code fences."""

    try:
        # Try using llava first (vision model)
        result = ask_ollama_with_image(prompt, image_data, model="llava")

        # Parse the response
        try:
            data = json.loads(result.strip())
            return {
                "alt_text": data.get("alt_text", ""),
                "description_type": data.get("description_type", "other"),
                "confidence": 1.0,
                "model_used": "llava"
            }
        except json.JSONDecodeError:
            # If parsing fails, try a retry
            retry_result = ask_ollama_with_image(
                prompt + "\n\nYour previous response was not valid JSON. "
                "Return only valid JSON with no markdown or code fences.",
                image_data,
                model="llava"
            )
            data = json.loads(retry_result.strip())
            return {
                "alt_text": data.get("alt_text", ""),
                "description_type": data.get("description_type", "other"),
                "confidence": 0.9,
                "model_used": "llava"
            }

    except (RuntimeError, json.JSONDecodeError) as vision_error:
        # Fallback: Try with text-only model and context-based description
        print(f"[Alt Text] Vision model unavailable ({str(vision_error)}). Using fallback.")

        try:
            filename = os.path.basename(image_path)
            fallback_prompt = f"""Generate a brief, accessible alt text (max {max_length} characters) for an academic publication image.
The image file is: {filename}

Guidelines:
- Describe visual content objectively
- Keep it concise
- No "image of" phrases
- Return only the alt text, no JSON or explanation"""

            import requests
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": "llama3.2",
                "prompt": fallback_prompt,
                "stream": False,
                "temperature": 0.3,
                "num_predict": 256
            }

            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            alt_text = response.json().get("response", "").strip()

            # Clean up the response
            if alt_text:
                # Remove markdown or other artifacts
                alt_text = alt_text.split('\n')[0].strip()
                if len(alt_text) > max_length:
                    alt_text = alt_text[:max_length].strip()

            return {
                "alt_text": alt_text or "Academic publication image",
                "description_type": "other",
                "confidence": 0.5,
                "model_used": "llama3.2 (fallback)",
                "warning": "Using text-only model; vision analysis unavailable"
            }

        except Exception as fallback_error:
            return {
                "alt_text": None,
                "confidence": 0,
                "error": f"Both vision and fallback models failed: {str(fallback_error)}",
                "model_used": "none"
            }


def ask_ollama_with_image(prompt, image_data, model="llava"):
    """
    Send a prompt and image to Ollama for processing with a vision model.

    Args:
        prompt: Text prompt
        image_data: Base64-encoded image data
        model: Ollama model to use (should be a vision model)

    Returns:
        Model response text
    """

    import requests

    url = "http://localhost:11434/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "images": [image_data],
        "stream": False,
        "temperature": 0.3,  # Lower temperature for more deterministic output
        "num_predict": 512   # Shorter output for alt text
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Cannot connect to Ollama at http://localhost:11434. "
            "Is Ollama running? Start with: ollama serve"
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("Ollama vision model took too long to respond")
    except Exception as e:
        raise RuntimeError(f"Ollama API error: {str(e)}")


def generate_alt_text_batch(image_paths):
    """
    Generate alt text for multiple images.

    Args:
        image_paths: List of image file paths

    Returns:
        List of alt text results, one per image path
    """

    results = []
    for image_path in image_paths:
        alt_text_result = generate_alt_text_for_image(image_path)
        results.append({
            "image_path": image_path,
            "result": alt_text_result
        })

    return results
