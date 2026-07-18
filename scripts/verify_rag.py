import os
import sys
import time
import json
import pickle
import logging
import re
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Resolve base directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)

if os.path.basename(PARENT_DIR) == "ai-service":
    BASE_DIR = PARENT_DIR
else:
    BASE_DIR = os.path.join(PARENT_DIR, "ai-service")

sys.path.insert(0, BASE_DIR)

# Configuration imports
try:
    from app.core import config
except ImportError:
    logger.error("Configuration app.core.config could not be imported.")
    sys.exit(1)

VERIFICATION_REPORT_PATH = os.path.join(BASE_DIR, "rag_verification_report.json")

def verify_step_1() -> Dict[str, Any]:
    """Verify python environment and packages."""
    logger.info("=== STEP 1: Verifying Python Environment ===")
    status = "PASS"
    details = {}
    
    # Check Python version
    py_version = sys.version
    details["python_version"] = py_version
    logger.info(f"Python version: {py_version}")
    
    # Check virtual environment
    venv = os.environ.get("VIRTUAL_ENV", "None")
    details["virtual_env"] = venv
    logger.info(f"Virtual environment active: {venv}")
    
    # Check requirements.txt dependencies
    req_file = os.path.join(PARENT_DIR, "requirements.txt")
    if not os.path.exists(req_file):
        req_file = os.path.join(BASE_DIR, "requirements.txt")
        
    dependencies = []
    if os.path.exists(req_file):
        with open(req_file, "r", encoding="utf-8") as f:
            for line in f:
                line_clean = line.strip()
                if line_clean and not line_clean.startswith("#"):
                    dependencies.append(line_clean)
    details["declared_dependencies"] = dependencies
    
    # Test imports and verify
    imported_libs = {}
    libs_to_test = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "pydantic": "pydantic",
        "sentence_transformers": "sentence_transformers",
        "faiss": "faiss",
        "httpx": "httpx"
    }
    
    for lib_name, import_name in libs_to_test.items():
        try:
            mod = __import__(import_name)
            version = getattr(mod, "__version__", "unknown")
            imported_libs[lib_name] = {"installed": True, "version": version}
            logger.info(f"Successfully imported {lib_name} (v{version})")
        except ImportError:
            imported_libs[lib_name] = {"installed": False, "version": None}
            logger.error(f"Missing dependency: {lib_name}")
            status = "FAIL"
            
    details["installed_libraries"] = imported_libs
    return {"status": status, "details": details}

def verify_step_2() -> Dict[str, Any]:
    """Verify raw JSON knowledge base files."""
    logger.info("=== STEP 2: Verifying Knowledge Base Files ===")
    status = "PASS"
    details = {}
    
    files = {
        "recipes.json": config.RECIPES_JSON,
        "ingredients.json": config.INGREDIENTS_JSON,
        "pairing.json": config.PAIRING_JSON,
        "chef_notes.json": config.CHEF_NOTES_JSON,
        "suppliers.json": config.SUPPLIERS_JSON,
        "seasonal.json": config.SEASONAL_JSON,
        "safety.json": config.SAFETY_JSON
    }
    
    for filename, file_path in files.items():
        file_details = {"exists": False, "valid_json": False, "encoding": "unknown", "size_bytes": 0, "records_count": 0}
        if os.path.exists(file_path):
            file_details["exists"] = True
            file_details["size_bytes"] = os.path.getsize(file_path)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    file_details["valid_json"] = True
                    file_details["encoding"] = "utf-8"
                    file_details["records_count"] = len(data) if isinstance(data, list) else 1
                logger.info(f"Verified {filename}: {file_details['records_count']} records, size: {file_details['size_bytes']} bytes")
            except json.JSONDecodeError as je:
                logger.error(f"{filename} has invalid JSON formatting: {str(je)}")
                status = "FAIL"
            except Exception as e:
                logger.error(f"Error checking {filename}: {str(e)}")
                status = "FAIL"
        else:
            logger.error(f"File missing: {filename} at {file_path}")
            status = "FAIL"
            
        details[filename] = file_details
        
    return {"status": status, "details": details}

def verify_step_3() -> Dict[str, Any]:
    """Verify chunk generation pipeline."""
    logger.info("=== STEP 3: Verifying Chunking Pipeline ===")
    status = "PASS"
    details = {}
    
    try:
        from app.rag.chunking import run_all_chunking
        total_chunks = run_all_chunking()
        details["total_chunks_count"] = total_chunks
    except Exception as e:
        logger.error(f"Failed to run chunking module: {str(e)}")
        return {"status": "FAIL", "details": {"error": str(e)}}
        
    chunk_files = {
        "recipes_chunks.json": config.RECIPES_CHUNKS,
        "ingredient_chunks.json": config.INGREDIENTS_CHUNKS,
        "supplier_chunks.json": config.SUPPLIERS_CHUNKS,
        "chef_chunks.json": config.CHEF_CHUNKS,
        "safety_chunks.json": config.SAFETY_CHUNKS,
        "seasonal_chunks.json": config.SEASONAL_CHUNKS
    }
    
    required_keys = {"chunk_id", "source", "document_id", "title", "content", "metadata"}
    
    for filename, file_path in chunk_files.items():
        file_details = {"exists": False, "valid_schema": True, "count": 0}
        if os.path.exists(file_path):
            file_details["exists"] = True
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    file_details["count"] = len(data)
                    for idx, chunk in enumerate(data):
                        missing_keys = required_keys - set(chunk.keys())
                        if missing_keys:
                            logger.error(f"Schema violation in {filename} index {idx}: missing keys {missing_keys}")
                            file_details["valid_schema"] = False
                            status = "FAIL"
                logger.info(f"Verified chunks {filename}: {file_details['count']} chunks, valid schema: {file_details['valid_schema']}")
            except Exception as e:
                logger.error(f"Error validating {filename}: {str(e)}")
                status = "FAIL"
                file_details["valid_schema"] = False
        else:
            logger.error(f"Chunk file missing: {filename}")
            status = "FAIL"
            
        details[filename] = file_details
        
    return {"status": status, "details": details}

def verify_step_4() -> Dict[str, Any]:
    """Verify local embedding engine."""
    logger.info("=== STEP 4: Verifying Embedding Generation ===")
    status = "PASS"
    details = {}
    
    try:
        from app.rag.embedding import EmbeddingEngine
        start_time = time.time()
        engine = EmbeddingEngine()
        details["load_time_seconds"] = time.time() - start_time
        
        test_text = "Salmon must be stored inside a refrigerator below 4 degrees Celsius."
        test_emb = engine.get_query_embedding(test_text)
        
        details["model_loaded"] = True
        details["dimension"] = len(test_emb)
        details["sample_embedding_len"] = len(test_emb)
        logger.info(f"Embedding engine loaded successfully in {details['load_time_seconds']:.2f}s.")
        logger.info(f"Vector dimension verification: {details['dimension']} (expected: 384)")
        
        if len(test_emb) != 384:
            logger.warning(f"Unexpected vector dimension: {len(test_emb)} (BGE Small expected 384)")
            status = "FAIL"
            
        # Test singleton behavior
        start_time2 = time.time()
        engine2 = EmbeddingEngine()
        load_time2 = time.time() - start_time2
        details["singleton_load_time_seconds"] = load_time2
        
        # Verify the same underlying model is reused
        is_same_model = (engine.model is engine2.model)
        details["singleton_verified"] = is_same_model
        logger.info(f"Second instantiation load time: {load_time2:.6f}s (Singleton verified: {is_same_model})")
        if not is_same_model:
            logger.warning("Singleton check failed: engine instances do not reuse the same model.")
            status = "FAIL"
    except Exception as e:
        logger.error(f"Failed to verify embedding engine: {str(e)}")
        status = "FAIL"
        details["model_loaded"] = False
        details["error"] = str(e)
        
    return {"status": status, "details": details}

def verify_step_5() -> Dict[str, Any]:
    """Verify unified FAISS vector database build."""
    logger.info("=== STEP 5: Verifying FAISS Database build ===")
    status = "PASS"
    details = {}
    
    try:
        from app.rag.vector_store import VectorStoreManager
        store = VectorStoreManager()
        start_time = time.time()
        # Test force_rebuild = False behavior (uses cache if exists)
        success = store.build_database(force_rebuild=False)
        details["build_time_seconds"] = time.time() - start_time
        details["build_success"] = success
        
        if success:
            logger.info(f"FAISS database built and indexed in {details['build_time_seconds']:.2f}s.")
            
            # Check file presence
            faiss_exists = os.path.exists(config.FAISS_INDEX_PATH)
            meta_exists = os.path.exists(config.FAISS_METADATA_PATH)
            meta_json_exists = os.path.exists(config.FAISS_METADATA_JSON_PATH)
            emb_cache_exists = os.path.exists(config.EMBEDDINGS_CACHE_PATH)
            
            details["faiss_index_exists"] = faiss_exists
            details["metadata_pkl_exists"] = meta_exists
            details["metadata_json_exists"] = meta_json_exists
            details["embeddings_cache_exists"] = emb_cache_exists
            
            if faiss_exists and meta_exists and meta_json_exists and emb_cache_exists:
                store.load_store()
                details["vector_count"] = store.index.ntotal
                details["metadata_records_count"] = len(store.chunks)
                logger.info(f"FAISS total index vectors: {details['vector_count']}")
                logger.info(f"Metadata records indexed: {details['metadata_records_count']}")
                
                if details["vector_count"] != details["metadata_records_count"]:
                    logger.error("Mismatch: total vectors inside FAISS index does not match total metadata records.")
                    status = "FAIL"
                    
                # Verify metadata.json format and schema
                try:
                    with open(config.FAISS_METADATA_JSON_PATH, "r", encoding="utf-8") as f:
                        json_data = json.load(f)
                    details["json_records_count"] = len(json_data)
                    
                    # Verify each record has vector_position matching its list index
                    all_positions_correct = True
                    for idx, record in enumerate(json_data):
                        if record.get("vector_position") != idx:
                            all_positions_correct = False
                            logger.error(f"Record at index {idx} has invalid vector_position: {record.get('vector_position')}")
                            break
                    details["json_vector_positions_verified"] = all_positions_correct
                    if not all_positions_correct:
                        status = "FAIL"
                except Exception as je:
                    logger.error(f"Failed to read or parse metadata.json: {str(je)}")
                    status = "FAIL"
            else:
                logger.error(
                    f"FAISS build files are missing: "
                    f"faiss_index: {faiss_exists}, metadata_pkl: {meta_exists}, "
                    f"metadata_json: {meta_json_exists}, embeddings_cache: {emb_cache_exists}"
                )
                status = "FAIL"
        else:
            logger.error("FAISS build database function returned success=False")
            status = "FAIL"
    except Exception as e:
        logger.error(f"Failed to execute FAISS build step: {str(e)}")
        status = "FAIL"
        details["build_success"] = False
        details["error"] = str(e)
        
    return {"status": status, "details": details}

def verify_step_6() -> Dict[str, Any]:
    """Verify Knowledge Retriever accuracy and speed."""
    logger.info("=== STEP 6: Verifying Knowledge Retriever ===")
    status = "PASS"
    details = {}
    
    test_questions = [
        "Need spicy chicken recipes",
        "Need seafood recipes",
        "How should salmon be stored?",
        "Need butter supplier"
    ]
    
    try:
        from app.rag.retriever import KnowledgeRetriever
        retriever = KnowledgeRetriever()
        
        search_results = {}
        total_time = 0.0
        
        for q in test_questions:
            start_time = time.time()
            chunks = retriever.retrieve(q, top_k=5)
            elapsed = time.time() - start_time
            total_time += elapsed
            
            chunk_list = []
            for idx, c in enumerate(chunks):
                # Verify required fields are present in each chunk
                required_keys = {"chunk_id", "document_id", "source", "title", "score", "content", "metadata"}
                missing_keys = required_keys - set(c.keys())
                if missing_keys:
                    logger.error(f"Retrieved chunk at index {idx} for query '{q}' is missing keys: {missing_keys}")
                    status = "FAIL"
                    
                score = c.get("score", 0.0)
                # Verify that score is a similarity score in the range [0.0, 1.0]
                if not (0.0 <= score <= 1.0):
                    logger.error(f"Retrieved chunk score is not a normalized similarity score: {score}")
                    status = "FAIL"

                chunk_list.append({
                    "chunk_id": c.get("chunk_id"),
                    "document_id": c.get("document_id"),
                    "title": c.get("title"),
                    "score": score,
                    "source": c.get("source"),
                    "metadata": c.get("metadata")
                })
            search_results[q] = {
                "retrieved_count": len(chunks),
                "time_seconds": elapsed,
                "chunks": chunk_list
            }
            logger.info(f"Retrieved {len(chunks)} contexts for query: '{q}' in {elapsed:.4f}s")
            if len(chunks) < 1:
                logger.warning(f"Search returned 0 results for: '{q}'")
                status = "FAIL"
                
        details["queries"] = search_results
        details["average_retrieval_time_seconds"] = total_time / len(test_questions)
        logger.info(f"Average retrieval execution speed: {details['average_retrieval_time_seconds']:.4f} seconds.")
    except Exception as e:
        logger.error(f"Failed to verify retriever: {str(e)}")
        status = "FAIL"
        details["error"] = str(e)
        
    return {"status": status, "details": details}

def verify_step_7_and_9() -> Dict[str, Any]:
    """Verify pipeline orchestration flow."""
    logger.info("=== STEP 7 & 9: Verifying RAG Pipeline Integration ===")
    status = "PASS"
    details = {}
    
    test_query = "What is the recommended storage temperature for Salmon?"
    
    try:
        from app.rag.rag_pipeline import RAGPipeline
        pipeline = RAGPipeline()
        
        start_time = time.time()
        result = pipeline.run(test_query)
        elapsed = time.time() - start_time
        
        details["execution_time_seconds"] = elapsed
        details["response_received"] = "response" in result
        details["response_text"] = result.get("response")
        details["retrieved_documents_count"] = len(result.get("source_documents", []))
        
        logger.info(f"Completed pipeline test in {elapsed:.2f}s.")
        logger.info(f"Orchestrated Answer:\n{details['response_text']}")
        
        if not details["response_received"] or not details["response_text"]:
            logger.error("RAG pipeline failed to return a valid text response.")
            status = "FAIL"
    except Exception as e:
        logger.error(f"Failed to verify RAG pipeline: {str(e)}")
        status = "FAIL"
        details["error"] = str(e)
        
    return {"status": status, "details": details}

def verify_step_8() -> Dict[str, Any]:
    """Verify local LLM (Ollama and Llama3)."""
    logger.info("=== STEP 8: Verifying LLM (Ollama & Llama3) ===")
    status = "PASS"
    details = {"ollama_active": False, "llama3_available": False}
    
    import httpx
    # Attempt to query Ollama's base URL API tags
    url = f"{config.OLLAMA_BASE_URL}/api/tags"
    logger.info(f"Checking Ollama service connectivity at {url}...")
    try:
        response = httpx.get(url, timeout=5.0)
        if response.status_code == 200:
            details["ollama_active"] = True
            logger.info("Ollama is installed and running.")
            
            models_data = response.json()
            models_list = [m.get("name") for m in models_data.get("models", [])]
            details["installed_models"] = models_list
            logger.info(f"Installed Ollama models: {models_list}")
            
            # Check for Llama3
            llama3_found = any("llama3" in m.lower() for m in models_list)
            if llama3_found:
                details["llama3_available"] = True
                logger.info("llama3 model is available in Ollama.")
            else:
                logger.error("llama3 model is missing in Ollama. Please run: ollama pull llama3")
                status = "FAIL"
        else:
            logger.error(f"Ollama health check returned HTTP {response.status_code}.")
            status = "FAIL"
            
        # Verify OllamaClient check_health method is working
        from app.llm.ollama_client import OllamaClient
        client = OllamaClient()
        health = client.check_health()
        details["client_health_check"] = health
        logger.info(f"OllamaClient health check output: {health}")
        if "status" not in health:
            logger.error("OllamaClient health check output missing 'status' key.")
            status = "FAIL"
            
    except Exception as e:
        logger.error(f"Could not connect to Ollama: {str(e)}")
        logger.error("Please start Ollama service on your local machine.")
        status = "FAIL"
        details["error"] = str(e)
        
        # Verify that health check correctly returns offline status when unreachable
        try:
            from app.llm.ollama_client import OllamaClient
            client = OllamaClient()
            health = client.check_health()
            details["client_health_check"] = health
            logger.info(f"OllamaClient offline health check output: {health}")
            if health.get("status") != "offline":
                logger.error("OllamaClient did not return 'offline' status when server is down.")
                status = "FAIL"
        except Exception as ex:
            logger.error(f"Failed to verify offline health check fallback: {str(ex)}")
            status = "FAIL"
        
    return {"status": status, "details": details}

def generate_reports(step_results: Dict[str, Dict[str, Any]]):
    """Generate final verification reports and compile health score."""
    # 1. Compile Health Score
    passed_steps = 0
    total_steps = len(step_results)
    for name, res in step_results.items():
        if res["status"] == "PASS":
            passed_steps += 1
            
    health_percentage = int((passed_steps / total_steps) * 100)
    overall_status = "PASS" if health_percentage == 100 else "FAIL"
    
    # 2. Extract metrics for Performance Report
    knowledge_count = sum(
        step_results["step_2"]["details"].get(f, {}).get("records_count", 0) 
        for f in step_results["step_2"]["details"]
    )
    chunks_count = step_results["step_3"]["details"].get("total_chunks_count", 0)
    embedding_dimension = step_results["step_4"]["details"].get("dimension", 0)
    vector_count = step_results["step_5"]["details"].get("vector_count", 0)
    avg_retrieval_time = step_results["step_6"]["details"].get("average_retrieval_time_seconds", 0.0)
    
    # 3. Create report dictionary
    verification_report = {
        "overall_status": overall_status,
        "project_health_score": f"{health_percentage}%",
        "performance_metrics": {
            "total_knowledge_records": knowledge_count,
            "total_chunks_generated": chunks_count,
            "embedding_dimension": embedding_dimension,
            "faiss_total_vectors": vector_count,
            "average_retrieval_time_seconds": avg_retrieval_time,
            "memory_usage_estimate": "Minimal (<50MB index footprint)"
        },
        "step_verifications": step_results
    }
    
    # Write to disk
    with open(VERIFICATION_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(verification_report, f, indent=2, ensure_ascii=False)
        
    # Print Console Report
    print("\n==================================")
    print("KitchenSync AI RAG Verification Report")
    print("==================================")
    print("Knowledge Base")
    print(step_results["step_2"]["status"])
    print(f"{knowledge_count} Records Valid")
    print()
    print("Chunking")
    print(step_results["step_3"]["status"])
    print(f"{chunks_count} Chunks Generated")
    print()
    print("Embeddings")
    print(step_results["step_4"]["status"])
    print(f"Dimension: {embedding_dimension}")
    print()
    print("FAISS Index")
    print(step_results["step_5"]["status"])
    print(f"{vector_count} Vectors Indexed")
    print()
    print("Retriever")
    print(step_results["step_6"]["status"])
    print(f"Average Speed: {avg_retrieval_time:.4f}s")
    print()
    print("LLM (Ollama & Llama3)")
    print(step_results["step_8"]["status"])
    print(f"Llama3 available: {step_results['step_8']['details']['llama3_available']}")
    print()
    print("RAG Pipeline")
    print(step_results["step_7_and_9"]["status"])
    print()
    print("Overall Status")
    print(overall_status)
    print("==================================")
    
    print("\n==================================")
    print("KitchenSync AI Health Report")
    print("==================================")
    for name, res in step_results.items():
        step_display = name.replace("step_", "Step ").replace("_and_", " & ")
        print(f"{step_display:<20} {res['status']}")
    print("----------------------------------")
    print(f"Overall Health       {health_percentage}%")
    print("==================================")
    
    if overall_status == "FAIL":
        print("\n!!! WARNING: RAG ENGINE CONTAINS FAILURES !!!")
        print("Please check rag_verification_report.json for details.")
        sys.exit(1)
    else:
        print("\nAll integration checks passed successfully! Ready for FastAPI deployment.")
        sys.exit(0)

if __name__ == "__main__":
    step_results = {}
    
    step_results["step_1"] = verify_step_1()
    step_results["step_2"] = verify_step_2()
    step_results["step_3"] = verify_step_3()
    step_results["step_4"] = verify_step_4()
    step_results["step_5"] = verify_step_5()
    step_results["step_6"] = verify_step_6()
    step_results["step_8"] = verify_step_8()
    # Execute Pipeline check last as it depends on all other components
    step_results["step_7_and_9"] = verify_step_7_and_9()
    
    generate_reports(step_results)
