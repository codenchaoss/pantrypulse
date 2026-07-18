import httpx
import logging
from typing import Dict, Any
from app.core import config
from app.llm.base_client import BaseLLMClient

logger = logging.getLogger("app.llm")

class GeminiClient(BaseLLMClient):
    """
    Client for Google Gemini API.
    """
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model = model or getattr(config, "PRIMARY_MODEL", "gemini-2.5-flash")
        
    def health_check(self) -> Dict[str, Any]:
        """
        Checks connectivity and credentials with Google Gemini API by running a tiny query.
        """
        if not self.api_key:
            return {"status": "unhealthy", "message": "Google Gemini API Key is missing."}
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": "healthcheck"}]}],
            "generationConfig": {"maxOutputTokens": 1}
        }
        
        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=5.0)
            if response.status_code == 200:
                return {"status": "healthy", "message": "Successfully connected to Google Gemini API."}
            
            # Handle error status codes
            try:
                err_data = response.json()
                err_msg = err_data.get("error", {}).get("message", response.text)
            except Exception:
                err_msg = response.text
                
            if response.status_code in (400, 403):
                return {"status": "unhealthy", "message": f"Authentication / Invalid API Key error (HTTP {response.status_code}): {err_msg}"}
            elif response.status_code == 429:
                return {"status": "unhealthy", "message": f"Rate limit / Quota exceeded (HTTP 429): {err_msg}"}
            else:
                return {"status": "unhealthy", "message": f"Gemini API returned status code {response.status_code}: {err_msg}"}
                
        except httpx.TimeoutException:
            return {"status": "unhealthy", "message": "Timeout occurred connecting to Google Gemini API."}
        except httpx.NetworkError as ne:
            return {"status": "unhealthy", "message": f"Network error connecting to Google Gemini API: {str(ne)}"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"Unexpected error during Google Gemini health check: {str(e)}"}

    def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Generates text using Google Gemini API. Handles failures gracefully and returns a structured dict.
        """
        if not self.api_key:
            return {
                "status": "error",
                "text": "",
                "error": "Gemini API key is not configured."
            }
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        logger.info(f"GeminiClient: Sending generation request to {self.model}...")
        
        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
            
            if response.status_code == 200:
                data = response.json()
                try:
                    candidates = data.get("candidates", [])
                    if candidates:
                        text = candidates[0].get("content", {}).get("parts", [])[0].get("text", "")
                        return {
                            "status": "success",
                            "text": text,
                            "error": None
                        }
                    else:
                        return {
                            "status": "error",
                            "text": "",
                            "error": "Gemini API returned success but empty candidates list."
                        }
                except (IndexError, KeyError, TypeError) as parse_err:
                    return {
                        "status": "error",
                        "text": "",
                        "error": f"Failed to parse Gemini API response structure: {str(parse_err)}"
                    }
            else:
                try:
                    err_data = response.json()
                    err_msg = err_data.get("error", {}).get("message", response.text)
                except Exception:
                    err_msg = response.text
                
                logger.error(f"GeminiClient: API failed with status code {response.status_code}: {err_msg}")
                return {
                    "status": "error",
                    "text": "",
                    "error": f"Gemini API error (HTTP {response.status_code}): {err_msg}"
                }
                
        except httpx.TimeoutException as te:
            logger.error(f"GeminiClient: Request timed out: {str(te)}")
            return {
                "status": "error",
                "text": "",
                "error": f"Gemini API request timed out: {str(te)}"
            }
        except httpx.NetworkError as ne:
            logger.error(f"GeminiClient: Network error: {str(ne)}")
            return {
                "status": "error",
                "text": "",
                "error": f"Gemini API network error: {str(ne)}"
            }
        except Exception as e:
            logger.error(f"GeminiClient: Unexpected error: {str(e)}")
            return {
                "status": "error",
                "text": "",
                "error": f"Gemini API unexpected error: {str(e)}"
            }
