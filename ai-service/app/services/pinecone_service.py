import time
import logging
from typing import Dict, Any, List, Optional
from pinecone import Pinecone
from app.core import config

logger = logging.getLogger("app.api")

class PineconeService:
    """
    Service wrapper for Pinecone Vector DB operations.
    Handles indexing, upserting, querying, and health status monitoring.
    """
    def __init__(self):
        self.api_key = config.PINECONE_API_KEY
        self.index_name = config.PINECONE_INDEX_NAME
        self.pc = None
        self.index = None
        self.initialized = False

    def initialize(self) -> bool:
        """
        Connects to Pinecone client and validates index existence.
        """
        if self.initialized:
            return True

        if not self.api_key:
            logger.error("PineconeService: API Key is missing in environment.")
            return False

        try:
            logger.info("PineconeService: Initializing Pinecone client...")
            self.pc = Pinecone(api_key=self.api_key)
            
            # Check if index exists
            active_indexes = [idx.name for idx in self.pc.list_indexes()]
            if self.index_name not in active_indexes:
                logger.error(f"PineconeService: Index '{self.index_name}' not found. Available indexes: {active_indexes}")
                return False

            self.index = self.pc.Index(self.index_name)
            self.initialized = True
            logger.info(f"PineconeService: Connected to index '{self.index_name}' successfully.")
            return True
        except Exception as e:
            logger.error(f"PineconeService: Connection failed: {str(e)}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """
        Checks connectivity, dimensions, and latency of Pinecone.
        """
        if not self.initialize():
            return {
                "status": "unhealthy",
                "message": "Initialization failed. Check API Key or Index Name."
            }

        start_time = time.time()
        try:
            # Describe index stats
            stats = self.index.describe_index_stats()
            latency = int((time.time() - start_time) * 1000)
            
            dimension = stats.get("dimension")
            if dimension != 384:
                return {
                    "status": "unhealthy",
                    "message": f"Dimension mismatch. Expected 384, index has {dimension}."
                }
                
            return {
                "status": "healthy",
                "latency_ms": latency,
                "total_records": stats.get("total_vector_count", 0),
                "message": f"Successfully connected. Index matches required 384 dimensions."
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Query check failed: {str(e)}"
            }

    def upsert_vectors(self, vectors: List[Dict[str, Any]]) -> bool:
        """
        Upserts a batch of vectors.
        Each vector item must be structured as:
        {
            "id": str,
            "values": List[float] (len=384),
            "metadata": Dict[str, Any]
        }
        """
        if not self.initialize():
            return False

        try:
            # Pinecone requires tuples of (id, values, metadata)
            formatted_vectors = []
            for item in vectors:
                formatted_vectors.append((
                    item["id"],
                    item["values"],
                    item["metadata"]
                ))
            
            logger.info(f"PineconeService: Upserting batch of {len(formatted_vectors)} vectors...")
            self.index.upsert(vectors=formatted_vectors)
            return True
        except Exception as e:
            logger.error(f"PineconeService: Upsert failed: {str(e)}")
            return False

    def query_vectors(self, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Queries Pinecone index using the input float vector.
        """
        if not self.initialize():
            return []

        try:
            logger.info(f"PineconeService: Querying index for top_{top_k} matches...")
            res = self.index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=True
            )
            
            normalized_results = []
            for match in res.get("matches", []):
                normalized_results.append({
                    "id": match.get("id"),
                    "score": match.get("score", 0.0),
                    "metadata": match.get("metadata", {})
                })
            return normalized_results
        except Exception as e:
            logger.error(f"PineconeService: Query failed: {str(e)}")
            return []
