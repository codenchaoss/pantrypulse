import os
import sys
import json
import logging
from typing import Dict, Any, List

# Ensure project root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from app.core import config
from app.rag.chunking import run_all_chunking
from app.rag.embedding import EmbeddingEngine
from app.services.pinecone_service import PineconeService

# Setup standard logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("sync_pinecone")

def clean_and_flatten_metadata(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cleans metadata to match Pinecone constraints.
    Values must be string, int, float, bool, or List[str].
    """
    clean_meta = {}
    for k, v in chunk.items():
        if k == "content":
            clean_meta["text"] = v
        elif isinstance(v, (str, int, float, bool)):
            clean_meta[k] = v
        elif isinstance(v, list):
            clean_meta[k] = [str(item) for item in v]
        else:
            clean_meta[k] = str(v)
            
    if "text" not in clean_meta:
        clean_meta["text"] = ""
    if "source" not in clean_meta:
        clean_meta["source"] = "general"
    if "title" not in clean_meta:
        clean_meta["title"] = "unknown"
        
    return clean_meta

def main():
    logger.info("=== KitchenSync Master Pinecone Cloud Synchronization ===")
    
    # Step 1: Regenerate text chunks from all 7 knowledge base JSON files
    logger.info("Step 1: Processing all 7 Knowledge Base JSON files into vector chunks...")
    total_chunks_generated = run_all_chunking()
    logger.info(f"Generated {total_chunks_generated} total chunks across recipes, ingredients, pairing, suppliers, chef notes, safety, and seasonal databases.")

    # Step 2: Initialize Pinecone Connection
    logger.info("Step 2: Connecting to Pinecone Cloud Vector Index...")
    pinecone_svc = PineconeService()
    if not pinecone_svc.initialize():
        logger.error("Failed to connect to Pinecone. Please verify PINECONE_API_KEY in your .env file.")
        sys.exit(1)
        
    health = pinecone_svc.health_check()
    logger.info(f"Pinecone Cloud Index Health: {health}")
    
    # Step 3: Read generated chunks
    chunk_files = [
        config.RECIPES_CHUNKS,
        config.INGREDIENTS_CHUNKS,
        config.PAIRING_CHUNKS,
        config.SUPPLIERS_CHUNKS,
        config.CHEF_CHUNKS,
        config.SAFETY_CHUNKS,
        config.SEASONAL_CHUNKS
    ]
    
    all_chunks = []
    for file_path in chunk_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_chunks.extend(data)
                        logger.info(f"Loaded {len(data)} chunks from {os.path.basename(file_path)}")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {str(e)}")
                
    total_chunks = len(all_chunks)
    logger.info(f"Total chunks ready for Pinecone upload: {total_chunks}")
    if total_chunks == 0:
        logger.error("No chunks found to upload!")
        sys.exit(1)

    # Step 4: Load local embedding model
    logger.info(f"Step 3: Initializing local embedding engine ({config.EMBEDDING_MODEL_NAME})...")
    embedder = EmbeddingEngine()
    
    # Step 5: Clear old index vectors for clean sync
    logger.info("Step 4: Clearing old vectors in Pinecone index for clean synchronization...")
    try:
        pinecone_svc.index.delete(delete_all=True)
        logger.info("Wiped old vectors successfully.")
    except Exception as e:
        logger.warning(f"Index clear notice: {str(e)}")

    # Step 6: Batch generate embeddings and upsert
    batch_size = 100
    vectors_to_upsert = []
    logger.info("Step 5: Generating 384-dimension vector embeddings and uploading batches to Pinecone...")
    
    for idx, chunk in enumerate(all_chunks):
        content = chunk.get("content", "")
        if not content:
            continue
            
        try:
            vector_vals = embedder.get_query_embedding(content)
            vector_id = chunk.get("chunk_id") or f"chunk-{idx:05d}"
            metadata = clean_and_flatten_metadata(chunk)
            
            vectors_to_upsert.append({
                "id": vector_id,
                "values": vector_vals,
                "metadata": metadata
            })
            
            if len(vectors_to_upsert) >= batch_size:
                success = pinecone_svc.upsert_vectors(vectors_to_upsert)
                if success:
                    logger.info(f"Uploaded batch: {idx + 1}/{total_chunks} vectors upserted to Pinecone.")
                else:
                    logger.error(f"Batch upsert failed at index {idx}")
                vectors_to_upsert = []
                
        except Exception as e:
            logger.error(f"Error embedding chunk {idx}: {str(e)}")
            
    if vectors_to_upsert:
        success = pinecone_svc.upsert_vectors(vectors_to_upsert)
        if success:
            logger.info(f"Uploaded final batch. Total vectors successfully synced to Pinecone: {total_chunks}")
        else:
            logger.error("Failed to upload the final batch.")
            
    logger.info("=== KitchenSync Master Pinecone Cloud Synchronization Complete! ===")

if __name__ == "__main__":
    main()
