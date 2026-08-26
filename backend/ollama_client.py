import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "llama3.2"


def ask_ollama(prompt):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0,
                "num_predict": 4096
            }
        },
        timeout=180
    )

    response.raise_for_status()

    data = response.json()

    return data["response"]