import os

# Resolve base directories
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(APP_DIR)

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    dotenv_path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(dotenv_path):
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()


# Knowledge Base path configuration
KNOWLEDGE_DIR = os.path.join(APP_DIR, "knowledge")
RECIPES_JSON = os.path.join(KNOWLEDGE_DIR, "recipes.json")
INGREDIENTS_JSON = os.path.join(KNOWLEDGE_DIR, "ingredients.json")
PAIRING_JSON = os.path.join(KNOWLEDGE_DIR, "pairing.json")
CHEF_NOTES_JSON = os.path.join(KNOWLEDGE_DIR, "chef_notes.json")
SUPPLIERS_JSON = os.path.join(KNOWLEDGE_DIR, "suppliers.json")
SEASONAL_JSON = os.path.join(KNOWLEDGE_DIR, "seasonal.json")
SAFETY_JSON = os.path.join(KNOWLEDGE_DIR, "safety.json")

# Chunk output path configuration
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")
CHUNKS_DIR = os.path.join(VECTOR_DB_DIR, "chunks")
RECIPES_CHUNKS = os.path.join(CHUNKS_DIR, "recipes_chunks.json")
INGREDIENTS_CHUNKS = os.path.join(CHUNKS_DIR, "ingredient_chunks.json")
PAIRING_CHUNKS = os.path.join(CHUNKS_DIR, "pairing_chunks.json")
SUPPLIERS_CHUNKS = os.path.join(CHUNKS_DIR, "supplier_chunks.json")
CHEF_CHUNKS = os.path.join(CHUNKS_DIR, "chef_chunks.json")
SAFETY_CHUNKS = os.path.join(CHUNKS_DIR, "safety_chunks.json")
SEASONAL_CHUNKS = os.path.join(CHUNKS_DIR, "seasonal_chunks.json")

# FAISS database output path configuration
FAISS_DIR = os.path.join(VECTOR_DB_DIR, "faiss_index")
FAISS_INDEX_PATH = os.path.join(FAISS_DIR, "index.faiss")
FAISS_METADATA_PATH = os.path.join(FAISS_DIR, "metadata.pkl")
FAISS_METADATA_JSON_PATH = os.path.join(FAISS_DIR, "metadata.json")
EMBEDDINGS_CACHE_PATH = os.path.join(FAISS_DIR, "embeddings.npy")

# Log paths configuration
LOGS_DIR = os.path.join(BASE_DIR, "logs")
RAG_LOG_PATH = os.path.join(LOGS_DIR, "rag.log")
LLM_LOG_PATH = os.path.join(LOGS_DIR, "llm.log")
API_LOG_PATH = os.path.join(LOGS_DIR, "api.log")

# RAG & Embedding Settings
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
DEFAULT_TOP_K = 5
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "pantrypulse-rag")
VECTOR_STORE = os.environ.get("VECTOR_STORE", "faiss")

# LLM Provider Configuration Settings
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GROK_API_KEY = os.environ.get("GROK_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY", "")
FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY", "")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "")

PRIMARY_PROVIDER = os.environ.get("PRIMARY_PROVIDER", "gemini")
FALLBACK_PROVIDER = os.environ.get("FALLBACK_PROVIDER", "openrouter")
PRIMARY_MODEL = os.environ.get("PRIMARY_MODEL", "gemini-2.5-flash")
FALLBACK_MODEL = os.environ.get("FALLBACK_MODEL", "meta-llama/llama-3.1-8b-instruct")

# Spring Boot Backend API Configuration Settings
SPRING_API_BASE_URL = os.environ.get("SPRING_API_BASE_URL", "https://pantrypulse-production-up.up.railway.app").rstrip("/")
SPRING_API_TIMEOUT = int(os.environ.get("SPRING_API_TIMEOUT", "10"))
SPRING_API_AUTH_TOKEN = os.environ.get("SPRING_API_AUTH_TOKEN", "")

# Ensure target directories exist
os.makedirs(CHUNKS_DIR, exist_ok=True)
os.makedirs(FAISS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Logger setup
def setup_logging():
    import logging
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    def add_handler_if_needed(logger_obj, file_path):
        abs_path = os.path.abspath(file_path)
        for h in logger_obj.handlers:
            if isinstance(h, logging.FileHandler) and os.path.abspath(h.baseFilename) == abs_path:
                return
        handler = logging.FileHandler(file_path, encoding="utf-8")
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        logger_obj.addHandler(handler)

    rag_logger = logging.getLogger("app.rag")
    rag_logger.setLevel(logging.INFO)
    add_handler_if_needed(rag_logger, RAG_LOG_PATH)

    llm_logger = logging.getLogger("app.llm")
    llm_logger.setLevel(logging.INFO)
    add_handler_if_needed(llm_logger, LLM_LOG_PATH)

    api_logger = logging.getLogger("app.api")
    api_logger.setLevel(logging.INFO)
    add_handler_if_needed(api_logger, API_LOG_PATH)

setup_logging()

