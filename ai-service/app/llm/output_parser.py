import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class OutputParser:
    """
    Normalizes raw LLM generation outputs.
    """
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans extraneous spaces and returns text.
        """
        if not text:
            return ""
        return text.strip()

    @staticmethod
    def parse_json(text: str) -> Dict[str, Any]:
        """
        Attempts to parse LLM string output as structured JSON.
        """
        cleaned = text.strip()
        # Find JSON boundaries if LLM wrapped in backticks
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()
            
        try:
            return json.loads(cleaned)
        except Exception as e:
            logger.warning(f"Failed to parse LLM output as JSON: {str(e)}")
            return {"raw_text": text, "error": "Invalid JSON format"}

    @staticmethod
    def format_output(response: str, provider: str, model: str, response_time_ms: int, fallback_used: bool, status: str = "success") -> Dict[str, Any]:
        """
        Formats and normalizes the final output response in a uniform schema.
        """
        return {
            "status": status,
            "provider": provider,
            "model": model,
            "response": OutputParser.clean_text(response),
            "response_time_ms": response_time_ms,
            "fallback_used": fallback_used
        }

