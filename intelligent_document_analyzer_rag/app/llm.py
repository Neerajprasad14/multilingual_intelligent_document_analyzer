import requests


class OllamaLLM:
    def __init__(self, model="llama3.2:3b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str, temperature=0.2) -> str:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            },
            timeout=300
        )
        response.raise_for_status()
        return response.json()["response"].strip()
