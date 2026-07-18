import logging
from typing import List
from sentence_transformers import SentenceTransformer
from app.core import config

logger = logging.getLogger(__name__)

class EmbeddingEngine:
    """
    Service wrapper for loading and executing semantic vector representations 
    using local SentenceTransformers models.
    """
    _model_instance = None

    def __init__(self, model_name: str = config.EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        if EmbeddingEngine._model_instance is None:
            logger.info(f"Initializing embedding model: {self.model_name}...")
            try:
                EmbeddingEngine._model_instance = SentenceTransformer(self.model_name)
                logger.info("Embedding model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load SentenceTransformer model {self.model_name}: {str(e)}")
                raise e
        else:
            logger.info("Reusing already loaded embedding model instance.")
            
        self.model = EmbeddingEngine._model_instance

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates dense vector embeddings for a list of text inputs.
        """
        if not texts:
            return []
        try:
            embeddings = self.model.encode(texts, show_progress_bar=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise e

    def get_query_embedding(self, query: str) -> List[float]:
        """
        Generates embedding representation for a single question or search query.
        """
        try:
            embedding = self.model.encode(query, show_progress_bar=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise e
