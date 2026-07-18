import time
import httpx
import logging
from typing import Dict, Any, Generator
from app.core import config
from app.llm.base_provider import BaseProvider

logger = logging.getLogger("app.llm")

class MistralProvider(BaseProvider):
    """
    Mistral API Provider implementation.
    """
    def __init__(self):
        self.api_key = config.MISTRAL_API_KEY
        self.model = "open-mistral-7b"

    def initialize(self) -> None:
        pass

    def health(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "unhealthy", "latency_ms": 0, "message": "Mistral API key is missing."}

        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 1
        }

        start_time = time.time()
        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=5.0)
            latency = int((time.time() - start_time) * 1000)
            if response.status_code == 200:
                return {"status": "healthy", "latency_ms": latency, "message": "Online"}
            return {"status": "unhealthy", "latency_ms": latency, "message": f"HTTP status {response.status_code}"}
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            return {"status": "unhealthy", "latency_ms": latency, "message": str(e)}

    def generate(self, prompt: str) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "error", "text": "", "error": "Mistral API key is not configured."}

        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
                choices = data.get("choices", [])
                if choices:
                    text = choices[0].get("message", {}).get("content", "")
                    return {"status": "success", "text": text, "error": None}
                return {"status": "error", "text": "", "error": "Mistral returned empty choices."}
            return {"status": "error", "text": "", "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"status": "error", "text": "", "error": str(e)}

    def stream(self, prompt: str) -> Generator[str, None, None]:
        res = self.generate(prompt)
        yield res.get("text", "")

    def supports_json(self) -> bool:
        return True

    def supports_function_calling(self) -> bool:
        return True
