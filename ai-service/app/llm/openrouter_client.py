import httpx
import logging
from typing import Dict, Any
from app.core import config
from app.llm.base_client import BaseLLMClient

logger = logging.getLogger("app.llm")

class OpenRouterClient(BaseLLMClient):
    """
    Client for OpenRouter API.
    """
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or config.OPENROUTER_API_KEY
        self.model = model or getattr(config, "FALLBACK_MODEL", "meta-llama/llama-3.1-8b-instruct")
        
    def health_check(self) -> Dict[str, Any]:
        """
        Checks connectivity and credentials with OpenRouter API by running a tiny query.
        """
        if not self.api_key:
            return {"status": "unhealthy", "message": "OpenRouter API Key is missing."}
            
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": "healthcheck"}],
            "max_tokens": 1
        }
        
        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=5.0)
            if response.status_code == 200:
                return {"status": "healthy", "message": "Successfully connected to OpenRouter API."}
            
            try:
                err_data = response.json()
                err_msg = err_data.get("error", {}).get("message", response.text)
            except Exception:
                err_msg = response.text
                
            return {"status": "unhealthy", "message": f"OpenRouter API returned status code {response.status_code}: {err_msg}"}
            
        except httpx.TimeoutException:
            return {"status": "unhealthy", "message": "Timeout occurred connecting to OpenRouter API."}
        except httpx.NetworkError as ne:
            return {"status": "unhealthy", "message": f"Network error connecting to OpenRouter API: {str(ne)}"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"Unexpected error during OpenRouter health check: {str(e)}"}

    def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Generates text using OpenRouter API. Handles failures gracefully and returns a structured dict.
        """
        if not self.api_key:
            return {
                "status": "error",
                "text": "",
                "error": "OpenRouter API key is not configured."
            }
            
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://kitchensync.ai",
            "X-Title": "KitchenSync AI"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        logger.info(f"OpenRouterClient: Sending generation request to {self.model}...")
        
        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
            
            if response.status_code == 200:
                data = response.json()
                try:
                    choices = data.get("choices", [])
                    if choices:
                        text = choices[0].get("message", {}).get("content", "")
                        return {
                            "status": "success",
                            "text": text,
                            "error": None
                        }
                    else:
                        return {
                            "status": "error",
                            "text": "",
                            "error": "OpenRouter API returned success but empty choices list."
                        }
                except (IndexError, KeyError, TypeError) as parse_err:
                    return {
                        "status": "error",
                        "text": "",
                        "error": f"Failed to parse OpenRouter API response structure: {str(parse_err)}"
                    }
            else:
                try:
                    err_data = response.json()
                    err_msg = err_data.get("error", {}).get("message", response.text)
                except Exception:
                    err_msg = response.text
                
                logger.error(f"OpenRouterClient: API failed with status code {response.status_code}: {err_msg}")
                return {
                    "status": "error",
                    "text": "",
                    "error": f"OpenRouter API error (HTTP {response.status_code}): {err_msg}"
                }
                
        except httpx.TimeoutException as te:
            logger.error(f"OpenRouterClient: Request timed out: {str(te)}")
            return {
                "status": "error",
                "text": "",
                "error": f"OpenRouter API request timed out: {str(te)}"
            }
        except httpx.NetworkError as ne:
            logger.error(f"OpenRouterClient: Network error: {str(ne)}")
            return {
                "status": "error",
                "text": "",
                "error": f"OpenRouter API network error: {str(ne)}"
            }
        except Exception as e:
            logger.error(f"OpenRouterClient: Unexpected error: {str(e)}")
            return {
                "status": "error",
                "text": "",
                "error": f"OpenRouter API unexpected error: {str(e)}"
            }
