import logging
from typing import List, Dict, Any, Optional
from app.retrievers.base_retriever import BaseRetriever
from app.rag.embedding import EmbeddingEngine
from app.rag.vector_store import VectorStoreManager
from app.core import config

logger = logging.getLogger("app.rag")

class FAISSRetriever(BaseRetriever):
    """
    FAISS-based implementation of the BaseRetriever.
    Runs query text embedder locally and queries local FAISS DB.
    """
    def __init__(self, top_k: int = config.DEFAULT_TOP_K):
        self.top_k = top_k
        self.embedder = None
        self.vector_store = None
        self._initialize()

    def _initialize(self):
        try:
            self.embedder = EmbeddingEngine()
            self.vector_store = VectorStoreManager()
            self.vector_store.load_store()
        except Exception as e:
            logger.error(f"FAISSRetriever: Failed to load FAISS store: {str(e)}")

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        k = top_k if top_k is not None else self.top_k
        
        if not self.embedder or not self.vector_store:
            self._initialize()
            if not self.embedder or not self.vector_store:
                logger.error("FAISSRetriever: Not initialized.")
                return []

        try:
            query_vector = self.embedder.get_query_embedding(query)
            search_results = self.vector_store.search(query_vector, top_k=k)
            
            retrieved_chunks = []
            for chunk, distance in search_results:
                similarity_score = round(max(0.0, min(1.0, 1.0 - (distance / 2.0))), 4)
                chunk_copy = chunk.copy()
                chunk_copy["score"] = similarity_score
                retrieved_chunks.append(chunk_copy)
                
            return retrieved_chunks
        except Exception as e:
            logger.error(f"FAISSRetriever: Search failed: {str(e)}")
            return []
