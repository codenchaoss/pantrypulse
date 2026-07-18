import time
import logging
import re
from typing import Dict, Any, Optional, List
from app.rag.retriever import KnowledgeRetriever
from app.prompts.chatbot_prompt import build_chat_prompt
from app.llm.llm_router import LLMRouter

logger = logging.getLogger("app.llm")

def detect_language(text: str) -> str:
    """
    Heuristic helper to detect language (english | telugu | roman_telugu).
    """
    text_lower = text.lower()
    # 1. Check if Telugu script characters exist (Unicode block 0C00-0C7F)
    has_telugu = any(0x0C00 <= ord(char) <= 0x0C7F for char in text)
    if has_telugu:
        return "telugu"
        
    # 2. Check for common Romanized Tenglish keywords
    tenglish_keywords = [
        "cheyyali", "migilindi", "ela", "enti", "avuthundi", "undhi", "undha", "vundha", "vundhi",
        "leka", "mari", "kuda", "ala", "ippudu", "vacham", "cheddam", "kavali", "garu", "ayya",
        "ivvali", "ledu", "chesi", "tinna", "tinali", "chudu", "andi", "vunda", "telusukovali", "unnaya"
    ]
    if any(word in text_lower for word in tenglish_keywords):
        return "roman_telugu"
        
    return "english"

def get_language_confidence(text: str, lang: str) -> float:
    """
    Computes language detection confidence score.
    """
    if lang == "telugu":
        return 0.99
    if lang == "roman_telugu":
        return 0.95
    return 0.90

def clean_ai_response(text: str) -> str:
    """
    Cleans markdown, duplicate whitespace, and literal escape characters (like raw \\n) from the response.
    """
    if not text:
        return ""
    
    # Replace literal escape sequences with actual whitespace formatting
    text = text.replace("\\\\n", "\n").replace("\\\\t", "\t").replace("\\\\r", "\r")
    text = text.replace("\\n", "\n").replace("\\t", "\t").replace("\\r", "\r")
    
    # 1. Strip markdown symbols
    markdown_symbols = ["**", "__", "###", "##", "#", "---", "```", ">", "`"]
    for sym in markdown_symbols:
        text = text.replace(sym, "")
        
    # 2. Normalize whitespace and newlines
    lines = [line.strip() for line in text.splitlines()]
    non_empty_lines = []
    consecutive_blank = 0
    for line in lines:
        if line == "":
            consecutive_blank += 1
            if consecutive_blank <= 1:
                non_empty_lines.append("")
        else:
            consecutive_blank = 0
            non_empty_lines.append(line)
            
    text = "\n".join(non_empty_lines)
    return text.strip()

class ChatbotService:
    """
    Handles conversational BOH operations by querying retrieved context and sending to the LLM router.
    """
    def __init__(self):
        self.retriever = KnowledgeRetriever()
        self.router = LLMRouter()

    def generate_response(self, question: str, history: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs the hybrid RAG Chatbot v2 pipeline (language detection, text normalization,
        dish extraction, exact search, similarity search, category mapping, RAG generation, and cleanup).
        """
        logger.info(f"ChatbotService: Processing query: '{question}' | History: {bool(history)}")
        start_time = time.time()
        
        # 1. Detect language
        detected_lang = detect_language(question)
        confidence_score = get_language_confidence(question, detected_lang)
        logger.info(f"ChatbotService: Detected query language: {detected_lang} (confidence: {confidence_score})")
        
        # 2. Retrieve knowledge chunks (from FAISS vector db search)
        try:
            vector_chunks = self.retriever.retrieve(question)
        except Exception as e:
            logger.error(f"ChatbotService: Retriever error: {str(e)}")
            vector_chunks = []
            
        # 3. Hybrid Search & Dish Extraction
        query_lower = question.lower()
        
        # Standard spelling adjustments (spelling normalization)
        spelling_map = {
            "ravvaupma": "rava upma",
            "ravva": "rava",
            "rawa": "rava",
            "vullipaya": "onion",
            "ullipaya": "onion",
            "ullipayya": "onion",
            "gobi": "cauliflower",
            "alugadda": "potato"
        }
        for wrong, right in spelling_map.items():
            query_lower = query_lower.replace(wrong, right)
            
        # Define common stop words to filter out from keyword search
        stop_words = {
            "with", "this", "that", "available", "vunda", "vundi", "undhi", "undha", "kavali", 
            "garu", "ayya", "andi", "unnaya", "is", "are", "was", "were", "have", "has", "had", 
            "what", "where", "how", "when", "who", "which", "whose", "why", "want", "need", "please",
            "gurinchi", "vunte", "okati", "parcel", "today", "using", "uses", "based", "from"
        }
        
        # Synonym expansions for similarity mappings
        synonym_expansions = {
            "chapati": ["chapati", "roti", "naan", "phulka", "flatbread", "paratha"],
            "roti": ["roti", "chapati", "naan", "phulka", "flatbread", "paratha"],
            "naan": ["naan", "roti", "chapati", "paratha"],
            "aloo": ["aloo", "potato", "potato curry", "aloo masala"],
            "potato": ["potato", "aloo", "potato curry", "aloo masala"],
            "paneer": ["paneer", "cottage cheese"],
            "curry": ["curry", "gravy", "masala"],
            "dosa": ["dosa", "dosha", "dose"],
            "upma": ["upma", "uppuma"]
        }
        
        all_chunks = []
        if self.retriever.vector_store and self.retriever.vector_store.chunks:
            all_chunks = self.retriever.vector_store.chunks
            
        # Split query by conjunctions to find multiple dish components
        parts = re.split(r'\b(?:with|and|&)\b', query_lower)
        extracted_components = []
        for part in parts:
            part_words = [w for w in re.findall(r'\b\w+\b', part) if len(w) > 3 and w not in stop_words]
            if part_words:
                extracted_components.append(part_words)
                
        logger.info(f"ChatbotService: Extracted components: {extracted_components}")
        
        exact_chunks = []
        similar_chunks = []
        
        # Perform query extraction matching
        if extracted_components:
            for comp_words in extracted_components:
                # Synonym expansion for this component
                comp_expanded = []
                for w in comp_words:
                    comp_expanded.append(w)
                    if w in synonym_expansions:
                        comp_expanded.extend(synonym_expansions[w])
                comp_expanded = list(set(comp_expanded))
                
                # Check for exact titles
                comp_exact_found = False
                for chunk in all_chunks:
                    if chunk.get("source") == "recipes":
                        title = chunk.get("title", "").lower()
                        # If component matches title exactly (e.g. "masala dosa" matches "Masala Dosa")
                        if title in " ".join(comp_words) or " ".join(comp_words) in title:
                            exact_chunks.append(chunk)
                            comp_exact_found = True
                            
                # Fallback to similarity check for this component
                if not comp_exact_found:
                    comp_matches = []
                    for chunk in all_chunks:
                        if chunk.get("source") == "recipes":
                            title = chunk.get("title", "").lower()
                            if any(w in title for w in comp_expanded):
                                comp_matches.append(chunk)
                                if len(comp_matches) >= 3:
                                    break
                    similar_chunks.extend(comp_matches)
                    
        # Filter duplicates and limit chunks
        combined_chunks = []
        seen_ids = set()
        
        for chunk in exact_chunks:
            chunk_id = chunk.get("chunk_id")
            if chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                chunk_copy = chunk.copy()
                chunk_copy["content"] = f"[EXACT DISH FOUND IN MENU]\n{chunk_copy['content']}"
                combined_chunks.append(chunk_copy)
                
        for chunk in similar_chunks:
            chunk_id = chunk.get("chunk_id")
            if chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                chunk_copy = chunk.copy()
                chunk_copy["content"] = f"[ALTERNATIVE SUGGESTION]\n{chunk_copy['content']}"
                combined_chunks.append(chunk_copy)
                
        # Determine search strategy
        search_strategy = "vector_only"
        if exact_chunks and similar_chunks:
            search_strategy = "exact_and_similarity"
        elif exact_chunks:
            search_strategy = "exact_match"
        elif similar_chunks:
            search_strategy = "similarity_match"

        # If still empty, fallback to vector_chunks
        if not combined_chunks:
            combined_chunks = vector_chunks
            search_strategy = "vector_fallback"
            
        # Limit total context chunks
        combined_chunks = combined_chunks[:8]
        
        # 4. Format context block
        context_strs = []
        sources = []
        for i, chunk in enumerate(combined_chunks):
            source = chunk.get("source", "unknown")
            sources.append(source)
            title = chunk.get("title", "unknown")
            content = chunk.get("content", "")
            context_strs.append(f"[Document #{i+1}] (Source: {source}, Title: {title})\n{content}\n")
            
        context_block = "\n".join(context_strs) if context_strs else "No relevant contexts retrieved."
        sources = list(set(sources))
        if not sources:
            sources = ["general"]
            
        # 5. Build prompt
        prompt = build_chat_prompt(question, context_block, history, detected_lang)
        
        # 6. Execute LLM Router
        try:
            router_result = self.router.generate(prompt, context_chunks=combined_chunks)
        except Exception as e:
            logger.error(f"ChatbotService: LLM routing failed: {str(e)}")
            router_result = {
                "status": "failed",
                "provider": "none",
                "response": "I couldn't find an exact match for your request. Can I help you with another menu item?",
                "response_time_ms": 0,
                "fallback_used": False
            }
            
        # 7. Response cleanup
        raw_answer = router_result.get("response", "")
        clean_answer = clean_ai_response(raw_answer)
        
        # Handle cases where model returned empty or fallback
        if not clean_answer:
            clean_answer = "I couldn't find an exact match for your request. Can I help you with another menu item?"
            
        # Proper capitalisation for provider
        raw_provider = router_result.get("provider", "gemini")
        provider_name = "Gemini" if raw_provider.lower() == "gemini" else raw_provider.capitalize()
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # 8. Observability & Telemetry log
        api_logger = logging.getLogger("app.api")
        api_logger.info(
            f"[TELEMETRY] Query: '{question}' | Lang: {detected_lang} (conf: {confidence_score}) | "
            f"Strategy: {search_strategy} | Chunks: {len(combined_chunks)} | Provider: {provider_name} | "
            f"Fallback: {router_result.get('fallback_used', False)} | Latency: {response_time_ms}ms"
        )
        
        return {
            "question": question,
            "language": detected_lang,
            "confidence": confidence_score,
            "answer": clean_answer,
            "sources": sources,
            "retrieved_chunks": len(combined_chunks),
            "provider": provider_name,
            "fallback_used": router_result.get("fallback_used", False),
            "response_time_ms": response_time_ms
        }
