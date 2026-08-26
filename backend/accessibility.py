import json

from ollama_client import ask_ollama


def review_html(html):

    prompt = f"""
You are an accessibility reviewer for news websites.

Review the following HTML for accessibility problems.

Check for:

- missing alt text
- poor alt text
- incorrect heading hierarchy
- missing semantic structure
- inaccessible links
- inappropriate tables
- unnecessary ARIA
- unclear captions
- duplicated information
- problems that could affect screen-reader users

Do NOT rewrite the HTML.

Return ONLY valid JSON.

The JSON must have exactly this structure:

{{
    "issues": [
        {{
            "severity": "error",
            "type": "missing_alt",
            "message": "Description of the problem"
        }}
    ]
}}

Severity must be one of:

error
warning
info

HTML TO REVIEW:

{html}
"""

    result = ask_ollama(prompt)

    # -----------------------------------------
    # Convert AI response into Python data
    # -----------------------------------------

    try:

        review = json.loads(result)

        return review.get("issues", [])

    except json.JSONDecodeError:

        return [{
            "severity": "warning",
            "type": "invalid_ai_response",
            "message": "The accessibility reviewer did not return valid JSON."
        }]