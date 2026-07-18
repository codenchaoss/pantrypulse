import os
import sys
import logging

# Ensure root directory is on PATH so it can import app modules
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "ai-service"))

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def run_test():
    logger.info("=== STEP 1: Running Chunking Pipeline ===")
    from app.rag.chunking import run_all_chunking
    total_chunks = run_all_chunking()
    logger.info(f"Chunking complete. Total chunks = {total_chunks}")
    
    logger.info("\n=== STEP 2: Building Unified FAISS Vector Store ===")
    from app.rag.vector_store import VectorStoreManager
    store = VectorStoreManager()
    success = store.build_database()
    if not success:
        logger.error("Vector store building failed.")
        sys.exit(1)
    logger.info("Vector store build successful!")
    
    logger.info("\n=== STEP 3: Testing Knowledge Retriever ===")
    from app.rag.retriever import KnowledgeRetriever
    retriever = KnowledgeRetriever()
    test_query = "What is the recommended storage temperature for Salmon?"
    chunks = retriever.retrieve(test_query, top_k=3)
    logger.info(f"Retrieved {len(chunks)} chunks for query: '{test_query}'")
    for i, chunk in enumerate(chunks):
        logger.info(f"  Match #{i+1}: [{chunk['source']}] (Score/Distance: {chunk['score']:.4f})")
        logger.info(f"    Title: {chunk['title']}")
        logger.info(f"    Content: {chunk['content']}")
        
    logger.info("\n=== STEP 4: Testing RAG Pipeline Orchestrator ===")
    from app.rag.rag_pipeline import RAGPipeline
    pipeline = RAGPipeline()
    result = pipeline.run(test_query)
    
    print("\n==============================================")
    print("TEST PIPELINE EXECUTION SUCCESSFUL")
    print("==============================================")
    print(f"QUERY: {result['query']}")
    print(f"PROMPT SENT:\n{result['prompt']}")
    print(f"PIPELINE LLM RESPONSE:\n{result['response']}")
    print("==============================================")
    
    sys.exit(0)

if __name__ == "__main__":
    run_test()
