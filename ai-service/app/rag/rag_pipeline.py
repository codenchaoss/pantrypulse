import logging
from typing import Dict, Any, Optional
from app.rag.retriever import KnowledgeRetriever
from app.llm.prompt_builder import PromptBuilder
from app.llm.ollama_client import OllamaClient
from app.llm.output_parser import OutputParser

logger = logging.getLogger(__name__)

class RAGPipeline:
    """
    Orchestration layer that controls the unified flow:
    Question -> Semantic Retriever -> Prompt Formatter -> LLM Generation -> Output Parser.
    """
    def __init__(self):
        try:
            self.retriever = KnowledgeRetriever()
            self.llm_client = OllamaClient()
            logger.info("RAG Pipeline initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize RAG Pipeline components: {str(e)}")

    def run(self, query: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        """
        Executes a single RAG cycle for a user query.
        """
        logger.info(f"Executing RAG pipeline for query: '{query}'")
        
        # 1. Retrieve relevant contexts
        try:
            retrieved_chunks = self.retriever.retrieve(query, top_k=top_k)
        except Exception as e:
            logger.error(f"Pipeline retrieval failed: {str(e)}")
            retrieved_chunks = []

        # 2. Build system context prompt
        try:
            prompt = PromptBuilder.build_prompt(query, retrieved_chunks)
        except Exception as e:
            logger.error(f"Pipeline prompt building failed: {str(e)}")
            prompt = f"User Question: {query}"

        # 3. Call LLM for generation
        try:
            raw_response = self.llm_client.generate(prompt)
        except Exception as e:
            logger.error(f"Pipeline LLM call failed: {str(e)}")
            raw_response = "[ERROR] Generation failed during LLM execution."

        # Propagate Ollama offline status dictionary immediately
        if isinstance(raw_response, dict) and raw_response.get("status") == "offline":
            logger.warning("Ollama is offline. Propagating offline response.")
            return raw_response

        # 4. Clean and parse output
        clean_response = OutputParser.clean_text(raw_response)
        
        # 5. Return structured orchestration result
        result = {
            "query": query,
            "prompt": prompt,
            "response": clean_response,
            "source_documents": retrieved_chunks
        }
        
        logger.info("RAG pipeline execution complete.")
        return result

if __name__ == "__main__":
    # Test script run
    logging.basicConfig(level=logging.INFO)
    pipeline = RAGPipeline()
    res = pipeline.run("What are the storage guidelines for Salmon?")
    print("\n--- LLM Response ---")
    print(res["response"])
