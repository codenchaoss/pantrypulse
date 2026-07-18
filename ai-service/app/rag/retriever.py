import logging
from typing import List, Dict, Any, Optional
from app.core import config
from app.rag.embedding import EmbeddingEngine
from app.rag.vector_store import VectorStoreManager

logger = logging.getLogger(__name__)

class KnowledgeRetriever:
    """
    Handles natural language query translation to query vector embedding, 
    FAISS similarity search execution, and result normalization.
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
            # Attempt pre-loading of FAISS database
            self.vector_store.load_store()
        except Exception as e:
            logger.error(f"Failed to initialize retriever services: {str(e)}")

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Translates query text to semantic embedding, searches the FAISS index, 
        and extracts the matched chunk details.
        """
        k = top_k if top_k is not None else self.top_k
        logger.info(f"Retrieving top {k} contexts for query: '{query}'...")
        
        if not self.embedder or not self.vector_store:
            logger.error("Retriever is not fully initialized. Initializing now...")
            self._initialize()
            if not self.embedder or not self.vector_store:
                return []
                
        try:
            # Step 1: Embed query text
            query_vector = self.embedder.get_query_embedding(query)
            
            # Step 2: Search FAISS Index
            search_results = self.vector_store.search(query_vector, top_k=k)
            
            # Step 3: Extract and normalize chunks (enrich with search scores)
            retrieved_chunks = []
            for chunk, distance in search_results:
                # Convert L2 distance to similarity score
                # Since embeddings are normalized, L2 distance squared ranges from 0 to 4.
                # Cosine similarity = 1 - distance/2
                similarity_score = round(max(0.0, min(1.0, 1.0 - (distance / 2.0))), 4)
                
                chunk_copy = chunk.copy()
                chunk_copy["score"] = similarity_score
                retrieved_chunks.append(chunk_copy)
                
            logger.info(f"Successfully retrieved {len(retrieved_chunks)} relevant contexts.")
            return retrieved_chunks
        except Exception as e:
            logger.error(f"Retrieval operation failed: {str(e)}")
            return []
