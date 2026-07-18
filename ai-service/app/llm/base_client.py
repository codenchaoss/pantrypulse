from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseLLMClient(ABC):
    """
    Common interface for all LLM providers.
    """
    @abstractmethod
    def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Generates structured text responses from the provider.
        Returns:
            Dict[str, Any]: {
                "status": "success" | "error",
                "text": str,
                "error": str | None
            }
        """
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Verifies if the LLM provider service is online and accessible.
        Returns:
            Dict[str, Any]: {
                "status": "healthy" | "unhealthy",
                "message": str | None
            }
        """
        pass
