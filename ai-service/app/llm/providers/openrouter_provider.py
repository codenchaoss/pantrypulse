import time
import httpx
import logging
from typing import Dict, Any, Generator
from app.core import config
from app.llm.base_provider import BaseProvider

logger = logging.getLogger("app.llm")

class OpenRouterProvider(BaseProvider):
    """
    OpenRouter API Provider implementation.
    """
    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        self.model = getattr(config, "FALLBACK_MODEL", "meta-llama/llama-3.1-8b-instruct")

    def initialize(self) -> None:
        pass

    def health(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "unhealthy", "latency_ms": 0, "message": "OpenRouter API key is missing."}

        url = "https://openrouter.ai/api/v1/chat/completions"
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
            response = httpx.post(url, json=payload, headers=headers, timeout=2.5)
            latency = int((time.time() - start_time) * 1000)
            if response.status_code == 200:
                return {"status": "healthy", "latency_ms": latency, "message": "Online"}
            return {"status": "unhealthy", "latency_ms": latency, "message": f"HTTP status {response.status_code}"}
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            return {"status": "unhealthy", "latency_ms": latency, "message": str(e)}

    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "error", "text": "", "error": "OpenRouter API key is not configured."}

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        temperature = kwargs.get("temperature", 0.2)
        max_tokens = kwargs.get("max_tokens", 600)
        
        target_model = kwargs.get("model", self.model)
        if not target_model or target_model in ("gemini-1.5-flash", "gemini-2.5-flash", "gemini"):
            target_model = "google/gemini-2.5-flash"
        elif "/" not in target_model:
            target_model = f"google/{target_model}"
            
        payload = {
            "model": target_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=2.5)
            if response.status_code == 200:
                data = response.json()
                choices = data.get("choices", [])
                if choices:
                    text = choices[0].get("message", {}).get("content", "")
                    return {"status": "success", "text": text, "error": None}
                return {"status": "error", "text": "", "error": "OpenRouter returned empty choices."}
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
