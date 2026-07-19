import logging
from typing import List, Dict, Any, Optional
from app.core import config
from app.retrievers.faiss_retriever import FAISSRetriever
from app.retrievers.pinecone_retriever import PineconeRetriever

logger = logging.getLogger("app.rag")

class MockVectorStore:
    """
    Exposes an empty chunks list to maintain compatibility with 
    the chatbot exact-spelling check fallback when FAISS database is offline.
    """
    def __init__(self):
        self.chunks = []

class KnowledgeRetriever:
    """
    Unified entry point for semantic RAG retrieval.
    Routes query vector search searches to FAISSRetriever or PineconeRetriever
    based on the configured VECTOR_STORE setting.
    """
    def __init__(self, top_k: int = config.DEFAULT_TOP_K):
        self.top_k = top_k
        self.vector_store_type = getattr(config, "VECTOR_STORE", "faiss").lower()

        if self.vector_store_type == "pinecone":
            logger.info("KnowledgeRetriever: Selecting Pinecone Cloud vector store.")
            self.active_retriever = PineconeRetriever(top_k=top_k)
            self.vector_store = MockVectorStore()
        else:
            logger.info("KnowledgeRetriever: Selecting local FAISS vector store.")
            self.active_retriever = FAISSRetriever(top_k=top_k)
            # Expose the internal FAISS vector store
            self.vector_store = getattr(self.active_retriever, "vector_store", MockVectorStore())

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieves matching context chunks using the active database store.
        """
        return self.active_retriever.retrieve(query, top_k=top_k)
