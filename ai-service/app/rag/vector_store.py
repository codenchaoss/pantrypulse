import json
import os
import pickle
import logging
import numpy as np
import faiss
from typing import List, Dict, Any, Tuple
from app.core import config
from app.rag.embedding import EmbeddingEngine

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """
    Manages building, saving, loading, and searching the FAISS vector database.
    Stores dense vectors in a unified FAISS index and serialized chunk records 
    in a pickle file.
    """
    def __init__(self):
        self.index = None
        self.chunks: List[Dict[str, Any]] = []

    def build_database(self, force_rebuild: bool = False) -> bool:
        """
        Loads all chunks, generates embeddings, builds the unified FAISS index,
        and saves both the index and metadata to disk.
        """
        logger.info("Initializing vector store build...")
        
        # Load all chunk files
        chunk_files = [
            config.RECIPES_CHUNKS,
            config.INGREDIENTS_CHUNKS,
            config.SUPPLIERS_CHUNKS,
            config.CHEF_CHUNKS,
            config.SAFETY_CHUNKS,
            config.SEASONAL_CHUNKS
        ]
        
        all_chunks = []
        for file_path in chunk_files:
            if not os.path.exists(file_path):
                logger.warning(f"Chunk file not found (skipping): {file_path}")
                continue
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    chunks_data = json.load(f)
                    if isinstance(chunks_data, list):
                        all_chunks.extend(chunks_data)
                        logger.info(f"Loaded {len(chunks_data)} chunks from {os.path.basename(file_path)}")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {str(e)}")

        if not all_chunks:
            logger.error("No chunks loaded. Cannot build FAISS index.")
            return False

        logger.info(f"Total chunks to embed: {len(all_chunks)}")
        
        # Check if embeddings.npy exists and can be loaded
        embeddings_np = None
        if not force_rebuild and os.path.exists(config.EMBEDDINGS_CACHE_PATH):
            logger.info("Found cached embeddings.npy. Loading cache...")
            try:
                cached_embeddings = np.load(config.EMBEDDINGS_CACHE_PATH)
                if len(cached_embeddings) == len(all_chunks):
                    embeddings_np = cached_embeddings.astype("float32")
                    logger.info(f"Loaded {len(embeddings_np)} cached embeddings from disk. Skipping regeneration.")
                else:
                    logger.warning(
                        f"Cached embeddings count ({len(cached_embeddings)}) does not match "
                        f"loaded chunks count ({len(all_chunks)}). Regenerating..."
                    )
            except Exception as e:
                logger.error(f"Failed to load cached embeddings: {str(e)}. Regenerating...")

        if embeddings_np is None:
            # Extract content for embedding
            texts = [chunk["content"] for chunk in all_chunks]
            
            # Generate embeddings
            try:
                embedder = EmbeddingEngine()
                embeddings = embedder.get_embeddings(texts)
                embeddings_np = np.array(embeddings).astype("float32")
                
                # Save generated embeddings to cache file
                np.save(config.EMBEDDINGS_CACHE_PATH, embeddings_np)
                logger.info(f"Saved generated embeddings to cache at {config.EMBEDDINGS_CACHE_PATH}")
            except Exception as e:
                logger.error(f"Embedding generation failed: {str(e)}")
                return False

        dimension = embeddings_np.shape[1]
        
        # Build FAISS index
        logger.info(f"Building unified FAISS index of dimension {dimension} using L2 similarity...")
        try:
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings_np)
            
            # Save index and metadata.pkl (Python native)
            faiss.write_index(index, config.FAISS_INDEX_PATH)
            with open(config.FAISS_METADATA_PATH, "wb") as f:
                pickle.dump(all_chunks, f)

            # Generate and save metadata.json (Spring Boot / Angular compatibility)
            json_metadata = []
            for idx, chunk in enumerate(all_chunks):
                chunk_copy = chunk.copy()
                chunk_copy["vector_position"] = idx
                json_metadata.append(chunk_copy)
                
            with open(config.FAISS_METADATA_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(json_metadata, f, indent=2, ensure_ascii=False)
                
            self.index = index
            self.chunks = all_chunks
            
            logger.info(f"Successfully saved FAISS index to {config.FAISS_INDEX_PATH}")
            logger.info(f"Successfully saved native metadata to {config.FAISS_METADATA_PATH}")
            logger.info(f"Successfully saved JSON metadata to {config.FAISS_METADATA_JSON_PATH}")
            return True
        except Exception as e:
            logger.error(f"FAISS index build failed: {str(e)}")
            return False

    def load_store(self) -> bool:
        """
        Loads the FAISS index and chunk metadata from disk.
        """
        if not os.path.exists(config.FAISS_INDEX_PATH) or not os.path.exists(config.FAISS_METADATA_PATH):
            logger.error("FAISS index or metadata files missing. Please build the database first.")
            return False
        try:
            self.index = faiss.read_index(config.FAISS_INDEX_PATH)
            with open(config.FAISS_METADATA_PATH, "rb") as f:
                self.chunks = pickle.load(f)
            logger.info(f"Successfully loaded FAISS index and {len(self.chunks)} chunk records.")
            return True
        except Exception as e:
            logger.error(f"Failed to load vector store: {str(e)}")
            return False

    def search(self, query_vector: List[float], top_k: int = config.DEFAULT_TOP_K) -> List[Tuple[Dict[str, Any], float]]:
        """
        Performs vector search against the loaded index and returns top_k matching chunks with distances.
        """
        if self.index is None or not self.chunks:
            logger.warning("Vector store is not loaded. Attempting auto-load...")
            if not self.load_store():
                logger.error("Search failed because vector store could not be loaded.")
                return []
                
        try:
            # Query vector reshaped
            query_np = np.array([query_vector]).astype("float32")
            distances, indices = self.index.search(query_np, top_k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx == -1 or idx >= len(self.chunks):
                    continue
                results.append((self.chunks[idx], float(distances[0][i])))
                
            return results
        except Exception as e:
            logger.error(f"Error performing FAISS search: {str(e)}")
            return []

if __name__ == "__main__":
    # Standard builder trigger if run directly
    logging.basicConfig(level=logging.INFO)
    store = VectorStoreManager()
    store.build_database()
