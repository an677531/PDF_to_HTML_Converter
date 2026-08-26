from ollama_client import ask_ollama


response = ask_ollama(
    "Explain in one sentence why accessible news websites are important."
)

print(response)