from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseRetriever(ABC):
    """
    Common abstract interface for semantic query retrieval.
    """
    @abstractmethod
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Runs query vector search and returns prioritized metadata chunks.
        """
        pass
