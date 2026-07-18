import httpx
import logging
from typing import Any
from app.core import config

logger = logging.getLogger(__name__)

class OllamaClient:
    """
    Communicates with local Ollama service for prompt inference.
    """
    def __init__(self, base_url: str = config.OLLAMA_BASE_URL, model: str = config.OLLAMA_MODEL):
        self.base_url = base_url
        self.model = model

    def check_health(self) -> dict:
        """
        Verifies if Ollama server is active and reachable.
        """
        try:
            response = httpx.get(self.base_url, timeout=2.0)
            if response.status_code == 200 or "Ollama is running" in response.text:
                return {"status": "online"}
        except Exception as e:
            logger.warning(f"Ollama health check failed: {str(e)}")
            
        return {
            "status": "offline",
            "message": "Ollama service is not running.",
            "suggestion": [
                "Run: ollama serve",
                "Run: ollama pull llama3"
            ]
        }

    def generate(self, prompt: str) -> Any:
        """
        Sends generation request to local Ollama. Falls back to mock text on error.
        Checks service health before sending request.
        """
        health = self.check_health()
        if health["status"] == "offline":
            return health

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        logger.info(f"Sending prompt to Ollama model '{self.model}' at {url}...")
        try:
            response = httpx.post(url, json=payload, timeout=60.0)
            if response.status_code == 200:
                data = response.json()
                generation = data.get("response", "")
                logger.info("Generation successful.")
                return generation
            else:
                logger.warning(f"Ollama returned HTTP error {response.status_code}. Using fallback mock response.")
        except Exception as e:
            logger.warning(f"Failed to communicate with Ollama service: {str(e)}. Using fallback mock response.")

        # Fallback Mock Response for Local Testing (when Ollama is offline)
        return (
            "[MOCK RESPONSE] Ollama service is currently offline or unreachable. "
            "Here is a mock response based on RAG context. Please ensure Ollama is "
            "running locally on http://localhost:11434 with llama3 model loaded."
        )
