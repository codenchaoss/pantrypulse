import logging
from typing import List, Dict, Any, Optional
from app.retrievers.base_retriever import BaseRetriever
from app.rag.embedding import EmbeddingEngine
from app.services.pinecone_service import PineconeService
from app.core import config

logger = logging.getLogger("app.rag")

class PineconeRetriever(BaseRetriever):
    """
    Pinecone-based implementation of the BaseRetriever.
    Queries the cloud-hosted Pinecone index.
    """
    def __init__(self, top_k: int = config.DEFAULT_TOP_K):
        self.top_k = top_k
        self.embedder = None
        self.pinecone = None
        self._initialize()

    def _initialize(self):
        try:
            self.embedder = EmbeddingEngine()
            self.pinecone = PineconeService()
            self.pinecone.initialize()
        except Exception as e:
            logger.error(f"PineconeRetriever: Failed to initialize dependencies: {str(e)}")

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        k = top_k if top_k is not None else self.top_k
        
        if not self.embedder or not self.pinecone:
            self._initialize()
            if not self.embedder or not self.pinecone:
                logger.error("PineconeRetriever: Service is not fully initialized.")
                return []

        try:
            # 1. Embed query
            query_vector = self.embedder.get_query_embedding(query)
            
            # 2. Query Pinecone
            matches = self.pinecone.query_vectors(query_vector, top_k=k)
            
            # 3. Format matches into exact same schema as FAISS
            retrieved_chunks = []
            for match in matches:
                metadata = match.get("metadata", {})
                
                # Align fields
                chunk = {
                    "chunk_id": metadata.get("chunk_id", match.get("id")),
                    "source": metadata.get("source", "unknown"),
                    "title": metadata.get("title", "unknown"),
                    "content": metadata.get("text", ""), # Pinecone text metadata mapped to content
                    "score": round(match.get("score", 0.0), 4)
                }
                
                # Copy additional metadata properties
                for key, val in metadata.items():
                    if key not in chunk and key != "text":
                        chunk[key] = val
                        
                retrieved_chunks.append(chunk)
                
            return retrieved_chunks
        except Exception as e:
            logger.error(f"PineconeRetriever: Query failed: {str(e)}")
            return []
