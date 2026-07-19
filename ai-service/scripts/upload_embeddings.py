import os
import sys
import json
import logging
from typing import Dict, Any, List

# Setup path so it finds the app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core import config
from app.rag.embedding import EmbeddingEngine
from app.services.pinecone_service import PineconeService

# Setup standard logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def load_chunks_from_disk() -> List[Dict[str, Any]]:
    """
    Loads all generated chunk JSON files from the vector_db/chunks folder.
    Auto-generates chunks from knowledge base JSON files if not present.
    """
    chunk_files = [
        config.RECIPES_CHUNKS,
        config.INGREDIENTS_CHUNKS,
        config.PAIRING_CHUNKS,
        config.SUPPLIERS_CHUNKS,
        config.CHEF_CHUNKS,
        config.SAFETY_CHUNKS,
        config.SEASONAL_CHUNKS
    ]
    
    # Verify if chunks exist, if not run chunking pipeline automatically
    missing_files = [f for f in chunk_files if not os.path.exists(f)]
    if missing_files:
        logger.info("Some chunk files are missing. Running knowledge base chunking pipeline...")
        from app.rag.chunking import run_all_chunking
        run_all_chunking()
    
    all_chunks = []
    for file_path in chunk_files:
        if not os.path.exists(file_path):
            logger.warning(f"Chunk file not found (skipping): {file_path}")
            continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_chunks.extend(data)
                    logger.info(f"Loaded {len(data)} chunks from {os.path.basename(file_path)}")
        except Exception as e:
            logger.error(f"Failed to read chunks from {file_path}: {str(e)}")
            
    return all_chunks

def clean_and_flatten_metadata(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cleans metadata to match Pinecone constraints.
    Values must be only string, int, float, bool, or List[str].
    """
    clean_meta = {}
    for k, v in chunk.items():
        if k == "content":
            # Map chunk content text directly to Pinecone's standard text field
            clean_meta["text"] = v
        elif isinstance(v, (str, int, float, bool)):
            clean_meta[k] = v
        elif isinstance(v, list):
            # Flatten lists of non-strings into lists of strings
            clean_meta[k] = [str(item) for item in v]
        else:
            # Cast dicts or other objects to string
            clean_meta[k] = str(v)
            
    # Guarantee base attributes exist
    if "text" not in clean_meta:
        clean_meta["text"] = ""
    if "source" not in clean_meta:
        clean_meta["source"] = "general"
    if "title" not in clean_meta:
        clean_meta["title"] = "unknown"
        
    return clean_meta

def main():
    logger.info("Initializing Pinecone RAG Migration...")
    
    # 1. Initialize Pinecone
    pinecone_svc = PineconeService()
    if not pinecone_svc.initialize():
        logger.error("Failed to connect to Pinecone. Make sure PINECONE_API_KEY is configured in your .env.")
        sys.exit(1)
        
    # 2. Check health status
    health = pinecone_svc.health_check()
    logger.info(f"Pinecone Health Status: {health}")
    if health.get("status") != "healthy":
        logger.error(f"Index is degraded: {health.get('message')}")
        sys.exit(1)
        
    # 3. Load chunks
    chunks = load_chunks_from_disk()
    if not chunks:
        logger.error("No chunks found in 'vector_db/chunks/'. Please run scripts/enrich_knowledge.py and build_embeddings.py first.")
        sys.exit(1)
        
    logger.info(f"Total chunks loaded from local database: {len(chunks)}")
    
    # 4. Initialize Local Embedder
    logger.info(f"Loading local embedding model: {config.EMBEDDING_MODEL_NAME}...")
    embedder = EmbeddingEngine()
    
    # 5. Clear old vectors for a clean database upload
    logger.info("Clearing old vectors from Pinecone index for a clean upload...")
    try:
        pinecone_svc.index.delete(delete_all=True)
        logger.info("Wiped old vectors successfully.")
    except Exception as e:
        logger.warning(f"Non-blocking index clear warning: {str(e)}")

    # 6. Batch processing and upload
    batch_size = 100
    total_chunks = len(chunks)
    vectors_to_upsert = []
    
    logger.info("Starting embedding generation and batch upserts...")
    for idx, chunk in enumerate(chunks):
        content = chunk.get("content", "")
        if not content:
            continue
            
        # Get query/document embedding (384 dimension)
        try:
            vector_vals = embedder.get_query_embedding(content)
            
            # Format Pinecone payload
            vector_id = chunk.get("chunk_id") or f"chunk-{idx:05d}"
            metadata = clean_and_flatten_metadata(chunk)
            
            vectors_to_upsert.append({
                "id": vector_id,
                "values": vector_vals,
                "metadata": metadata
            })
            
            # Upsert in batches of 100
            if len(vectors_to_upsert) >= batch_size:
                success = pinecone_svc.upsert_vectors(vectors_to_upsert)
                if not success:
                    logger.error(f"Upsert failed at batch ending with index {idx}")
                else:
                    logger.info(f"Uploaded batch: {idx + 1}/{total_chunks} vectors upserted.")
                vectors_to_upsert = []
                
        except Exception as e:
            logger.error(f"Error processing chunk index {idx}: {str(e)}")
            
    # Upsert remainder
    if vectors_to_upsert:
        success = pinecone_svc.upsert_vectors(vectors_to_upsert)
        if success:
            logger.info(f"Uploaded final batch. Total vectors processed: {total_chunks}")
        else:
            logger.error("Failed to upload the final vector batch.")
            
    logger.info("Pinecone database migration complete!")

if __name__ == "__main__":
    main()
