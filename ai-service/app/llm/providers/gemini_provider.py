import time
import httpx
import logging
from typing import Dict, Any, Generator
from app.core import config
from app.llm.base_provider import BaseProvider

logger = logging.getLogger("app.llm")

class GeminiProvider(BaseProvider):
    """
    Google Gemini API Provider implementation.
    """
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        self.model = getattr(config, "PRIMARY_MODEL", "gemini-2.5-flash")

    def initialize(self) -> None:
        pass

    def health(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "unhealthy", "latency_ms": 0, "message": "Gemini API key is missing."}

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": "healthcheck"}]}],
            "generationConfig": {"maxOutputTokens": 1}
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

    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "error", "text": "", "error": "Gemini API key is not configured."}

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
        temperature = kwargs.get("temperature", 0.2)
        max_tokens = kwargs.get("max_tokens", 600)
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }

        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    text = candidates[0].get("content", {}).get("parts", [])[0].get("text", "")
                    return {"status": "success", "text": text, "error": None}
                return {"status": "error", "text": "", "error": "Gemini returned empty candidates."}
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
