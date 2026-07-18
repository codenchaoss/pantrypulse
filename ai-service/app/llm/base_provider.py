from abc import ABC, abstractmethod
from typing import Dict, Any, Generator

class BaseProvider(ABC):
    """
    Common abstract interface for all LLM providers in the registry.
    """
    @abstractmethod
    def initialize(self) -> None:
        """Initializes any required internal configurations or state."""
        pass

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """
        Verifies provider connectivity and returns health metrics.
        Returns:
            Dict[str, Any]: {
                "status": "healthy" | "unhealthy",
                "latency_ms": int,
                "message": str | None
            }
        """
        pass

    @abstractmethod
    def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Generates a structured text response for the prompt.
        Returns:
            Dict[str, Any]: {
                "status": "success" | "error",
                "text": str,
                "error": str | None
            }
        """
        pass

    @abstractmethod
    def stream(self, prompt: str) -> Generator[str, None, None]:
        """Generates streaming text response chunks."""
        pass

    @abstractmethod
    def supports_json(self) -> bool:
        """Indicates if the provider has native JSON mode capabilities."""
        pass

    @abstractmethod
    def supports_function_calling(self) -> bool:
        """Indicates if the provider supports tool/function calling."""
        pass
