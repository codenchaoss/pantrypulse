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
    Uses regex word boundaries, interjection lexicons, and suffix patterns for accurate Tenglish detection.
    """
    if not text:
        return "english"
        
    # 1. Check if Telugu script characters exist (Unicode block 0C00-0C7F)
    if any(0x0C00 <= ord(char) <= 0x0C7F for char in text):
        return "telugu"
        
    text_lower = text.lower()
    
    # 2. Comprehensive Romanized Telugu (Tenglish) words, interjections & stems
    tenglish_words = {
        # Conversational Interjections, Slang & Fillers
        "ohh", "oh", "oho", "ohho", "hurray", "hurey", "hurrah", "alright", "alrighty", "knaww",
        "knoww", "kneww", "accha", "aachcha", "acha", "aah", "aha", "ahha", "abba", "abbha",
        "ammo", "ammow", "ayyo", "ayyyo", "arey", "areyy", "are", "rey", "reyy", "ra", "raa",
        "bey", "bhey", "boss", "bro", "dude", "sir", "ji", "mama", "macha", "machi", "machan",
        "garu", "gaaru", "andi", "aandi", "ayya", "ayyachya", "bhayya", "bhai", "bhaya", "anna",
        "annayya", "akka", "akkayya", "tammudu", "chello", "pilla", "potti", "babu", "bangaram",
        "chelli", "gurinchi", "sangathi", "sangati", "visayam", "vishayam", "batti", "valana",
        
        # Question words & Pronouns
        "enni", "yenni", "etla", "yetla", "ela", "yela", "enti", "yenti", "yem", "emi", "yemi",
        "evaru", "yevaru", "yeda", "ekkada", "yekkada", "akkada", "yakkada", "yenduku", "enduku",
        "eppudu", "yeppudu", "elaga", "yelaga", "evarki", "yevarki", "yavaru", "manaki", "manaku",
        "naaku", "naku", "neeku", "tanaku", "vaallu", "vallu", "vaallaki", "vallaki", "athanu",
        "atanu", "aavida", "idi", "adi", "ivi", "avi", "ikada", "akada",
        
        # Quantity, Time, Frequency & Manner
        "sarlu", "saarlu", "sari", "saari", "chala", "chaala", "koncham", "konchem", "motham",
        "mottham", "sariga", "sarigga", "thwaraga", "twaraga", "roju", "rojoo", "rojuki", "repu",
        "ivvala", "eevala", "ninna", "ippudu", "appudu", "sepu", "sepati", "koddiseapu", "nundi", "nunchi",
        
        # Verbs & Auxiliary stems
        "chesukuntadu", "chesukuntaru", "chesukuntam", "chesukuntadhi", "chesukuntai", "chesukovali",
        "chesuko", "chesukoni", "cheyyali", "cheyali", "chesta", "chestha", "chestaru", "chestanu",
        "chestam", "cheddam", "chesthunnaru", "chesthunna", "chesanu", "chesaru", "chesadu", "chesindi",
        "chesav", "chesam", "chey", "cheyyi", "cheyi", "chesi", "chesinappudu", "chese", "chesetappudu",
        "tinali", "tinna", "tinadam", "thinaru", "thintaru", "thinte", "tine", "thine", "tagali",
        "thaagali", "tagina", "vundhi", "undhi", "vundi", "undi", "vundha", "undha", "vunda", "unda",
        "vunnai", "unai", "unnayi", "unayi", "vunnaru", "unnaru", "vunnar", "unnar", "vuntadhi",
        "vuntadi", "untadi", "untadhi", "vuntai", "untai", "avuthundi", "avutundi", "aipoyindi",
        "ayipoindhi", "aipoyindhi", "migilindi", "migilindhi", "migilipoyindi", "leka", "ledu", "ledhu",
        "ivvali", "ivvandi", "ivvu", "ivvacha", "pettali", "pettandi", "pettukovali", "tiskoni",
        "theskoni", "theskovalane", "tisukoni", "thesukoni", "kavalo", "kavali", "kaavali", "kavalane",
        "cheppandi", "cheppu", "cheppava", "cheppara", "chudu", "chudandi", "vacham", "vacha", "vachindi",
        "vacharu", "vastadi", "vasthundhi", "vastaru", "vastanu", "povali", "potha", "pothanu", "potharu",
        "poindi", "poyindi", "kuda", "kooda", "kudaa", "mari", "ala", "alaage", "alaga", "alage", "valla", "supliers"
    }
    
    words = set(re.findall(r'\b[a-z]+\b', text_lower))
    if words.intersection(tenglish_words):
        return "roman_telugu"
        
    # Regex pattern for compound Tenglish verb suffixes
    tenglish_regex = r'\b[a-z]+(?:kuntadu|kuntaru|kuntam|kovali|kovalani|kovalane|thundi|thunnaru|thari|thamu)\b'
    if re.search(tenglish_regex, text_lower):
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
        
        # 4.5 Multi-JSON Knowledge Base Context Injector (Scanning all 7 Knowledge Base Files)
        kb = self._get_knowledge_base()
        q_low = question.lower()
        additional_contexts = []

        # A. Suppliers
        if any(w in q_low for w in ["supplier", "supliers", "inform", "restock", "replenish", "contact", "vendor", "expiring", "purchase", "gas", "fuel", "cylinder", "plate", "plates", "tissue", "tissues", "table", "tables", "dining", "infra", "infrastructure", "furniture", "crockery", "water", "drink", "drinks", "milk", "ice cream", "coffee", "tea", "bakery", "frozen"]):
            sup_data = kb.get("suppliers.json", [])
            sup_strs = ["=== SUPPLIER DIRECTORY & CONTACTS ==="]
            for s in sup_data:
                sup_strs.append(
                    f"• {s.get('supplier_name')} (Category: {s.get('ingredient_category')}, City: {s.get('city')})\n"
                    f"  Contact: {s.get('contact_email')} | Delivery: {s.get('delivery_time_hours')}h | Rating: {s.get('rating')}/5\n"
                    f"  Supplies: {', '.join(s.get('supported_ingredients', []))}"
                )
            additional_contexts.append("\n".join(sup_strs))
            sources.append("suppliers")

        # B. Food Safety, First Aid & BOH Emergency Safety Protocols (75+ Categories)
        safety_triggers = [
            "safety", "temp", "temperature", "hygiene", "hygienic", "storage", "haccp", "clean", "shelf", "spoilage",
            "cut", "cutiyindhi", "cutayindhi", "bleeding", "turmeric", "pasupu", "burn", "injury", "finger",
            "hand", "handwash", "wound", "first aid", "aid", "leak", "oil", "migilithe", "fire", "manta", "mantalu",
            "smell", "wasana", "current", "power", "chemical", "glass", "pagilithe", "pest", "chicken",
            "egg", "guddu", "rice", "annam", "blender", "mixi", "knife", "kathi", "thaw", "defrost",
            "mold", "fifo", "hair", "juttu", "hood", "spoiled", "rotten", "cooker", "electric",
            "shock", "choking", "heimlich", "heavy", "lift", "allergy", "ice", "scoop", "honey", "teflon",
            "parasite", "fish", "dilution", "nail", "gollu", "ring", "jewelry", "apron", "sickness", "board",
            "fridge", "danger", "cooling", "label", "tasting", "mop", "slicer", "sink", "cloth", "glove",
            "gloves", "closing", "opening", "pedal", "dustbin", "trash", "sarlu", "sarl"
        ]
        if any(w in q_low for w in safety_triggers):
            safe_data = kb.get("safety.json", [])
            safe_strs = ["=== BOH SAFETY, FIRST AID & EMERGENCY PROTOCOLS ==="]
            
            matched_safety = []
            for sf in safe_data:
                topic = str(sf.get("topic", "")).lower()
                title = str(sf.get("title", "")).lower()
                desc = str(sf.get("description", "")).lower()
                if any(t in topic or t in title or t in desc for t in safety_triggers if t in q_low):
                    matched_safety.append(sf)
            
            if not matched_safety:
                matched_safety = [sf for sf in safe_data if "topic" in sf or "title" in sf]
                if not matched_safety:
                    matched_safety = safe_data[-30:]
                    
            for sf in matched_safety[:5]:
                title = sf.get("title") or sf.get("topic", "Safety Rule")
                rule = sf.get("rule") or sf.get("description") or sf.get("content", "")
                if title and rule:
                    safe_strs.append(f"• {title}:\n  {rule}")
            additional_contexts.append("\n".join(safe_strs))
            sources.append("safety")

        if any(w in q_low for w in ["chef", "note", "tip", "practice", "prep", "technique", "kitchen"]):
            notes_data = kb.get("chef_notes.json", [])
            note_strs = ["=== CHEF NOTES & BOH BEST PRACTICES ==="]
            for n in notes_data[:5]:
                topic = n.get("topic") or n.get("title", "Chef Tip")
                note = n.get("note") or n.get("description") or n.get("content", "")
                if topic and note:
                    note_strs.append(f"• {topic}: {note}")
            additional_contexts.append("\n".join(note_strs))
            sources.append("chef_notes")

        seasonal_triggers = [
            "season", "seasonal", "monsoon", "summer", "winter", "spring", "autumn", "month", "masam",
            "chaitram", "vaisakham", "jyeshtam", "aashadham", "shravanam", "bhadrapadam", "aashwayujam",
            "karthikam", "margasiram", "pushyam", "magham", "phalgunam", "ugadi", "sankranti", "dasara"
        ]
        if any(w in q_low for w in seasonal_triggers):
            sea_data = kb.get("seasonal.json", [])
            sea_strs = ["=== SEASONAL & TELUGU MASAMULU CALENDAR ==="]
            
            matched_items = []
            for sc in sea_data:
                season_name = str(sc.get("season", "")).lower()
                telugu_m = str(sc.get("telugu_month", "")).lower()
                if any(t in season_name or t in telugu_m for t in seasonal_triggers if len(t) > 3 and t in q_low):
                    matched_items.append(sc)
            
            if not matched_items:
                matched_items = sea_data[-12:]
                
            for sc in matched_items[:6]:
                period = sc.get("telugu_month") or sc.get("season") or "Season"
                sub_s = sc.get("sub_season", "")
                ings = sc.get("seasonal_ingredients") or sc.get("ingredients", [])
                tip = sc.get("special_menu_tip", "")
                sea_strs.append(
                    f"• {period} ({sub_s}):\n"
                    f"  Ingredients: {', '.join(ings) if isinstance(ings, list) else ings}\n"
                    f"  Chef Tip: {tip}"
                )
            additional_contexts.append("\n".join(sea_strs))
            sources.append("seasonal")

        if any(w in q_low for w in ["pair", "pairing", "side", "combo", "combination", "serve with", "match"]):
            pair_data = kb.get("pairing.json", [])
            pair_strs = ["=== RECOMMENDED REGIONAL & SEASONAL DISH PAIRINGS ==="]
            
            matched_pairings = []
            for p in pair_data:
                ing_name = str(p.get("ingredient", "")).lower()
                if any(k in ing_name for k in ["ragi", "rayalaseema", "godavari", "guntur", "nellore", "chettinad", "kerala", "mysore", "bisi", "summer", "monsoon", "autumn", "winter"] if k in q_low):
                    matched_pairings.append(p)
            
            if not matched_pairings:
                matched_pairings = pair_data[-16:]
                
            for p in matched_pairings[:6]:
                ing = p.get("ingredient") or "Dish"
                pairs = p.get("pairs", [])
                if ing and pairs:
                    pair_strs.append(f"• {ing}:\n  Pairs best with: {', '.join(pairs) if isinstance(pairs, list) else pairs}")
            additional_contexts.append("\n".join(pair_strs))
            sources.append("pairing")

        if any(w in q_low for w in ["cost", "unit", "shelf", "price", "avg_cost"]):
            ing_data = kb.get("ingredients.json", [])
            ing_strs = ["=== INGREDIENT MASTER DATA ==="]
            for ig in ing_data[:5]:
                name = ig.get("name") or ig.get("ingredient")
                cost = ig.get("avg_cost") or ig.get("cost", "N/A")
                unit = ig.get("unit", "kg")
                if name:
                    ing_strs.append(f"• {name}: Avg Cost ₹{cost}/{unit}")
            additional_contexts.append("\n".join(ing_strs))
            sources.append("ingredients")

        if any(w in q_low for w in ["knife", "knives", "tool", "tools", "utensil", "utensils", "pan", "board", "cutting board", "equipment", "station", "cutlery", "spoon", "fork", "apron", "towel", "trash", "dustbin", "bin", "plate", "plates", "key", "locker"]):
            equip_strs = [
                "=== BOH KITCHEN EQUIPMENT, STORAGE & CASUAL STAFF LAYOUT ===",
                "• Chef Knives & Slicers: Main BOH Prep Station magnetic knife bar near the main prep counter.",
                "• Aprons & Staff Linens: Stored in the BOH Linen Rack / Staff Locker Shelf near the staff entrance.",
                "• Cutting Boards: Color-coded boards (Red: Meat, Green: Produce, Yellow: Poultry, Blue: Seafood) next to the main wash sink.",
                "• Clean Plates & Cutlery: Clean dish drying racks located at the Pass-through counter / Dishwashing station.",
                "• Waste Bins & Trash: Organic food waste bins located under the main prep counter and wash sink; Dry waste bins near the storage exit.",
                "• Cleaning Towels & Sanitizer: Towel dispenser and sanitizer station located at the BOH Handwash Sink.",
                "• Cookware & Pans: Stainless steel pans and kadais stored on the lower shelving below the stove ranges.",
                "• Storage Keys & Supplies: Kept at the Head Chef / Shift Manager Desk at the main BOH office."
            ]
            additional_contexts.append("\n".join(equip_strs))
            sources.append("chef_notes")

        if additional_contexts:
            context_block = "\n\n".join(additional_contexts) + "\n\n" + context_block

        sources = list(set(sources))
        if not sources:
            sources = ["general"]
            
        prompt = build_chat_prompt(question, context_block, history, detected_lang)
        
        try:
            router_result = self.router.generate(prompt, context_chunks=combined_chunks, temperature=0.4, max_tokens=600)
        except Exception as e:
            logger.error(f"ChatbotService: LLM routing failed: {str(e)}")
            router_result = {
                "status": "failed",
                "provider": "none",
                "response": "I couldn't find an exact match for your request. Can I help you with another menu item?",
                "response_time_ms": 0,
                "fallback_used": False
            }
            
        raw_answer = router_result.get("response", "")
        clean_answer = clean_ai_response(raw_answer)
        
        if not clean_answer:
            clean_answer = "I couldn't find an exact match for your request. Can I help you with another menu item?"
            
        raw_provider = router_result.get("provider", "gemini")
        provider_name = "Gemini" if raw_provider.lower() == "gemini" else raw_provider.capitalize()
        response_time_ms = int((time.time() - start_time) * 1000)
        
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

    _knowledge_cache = None

    def _get_knowledge_base(self) -> Dict[str, Any]:
        import os, json
        if ChatbotService._knowledge_cache is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            kb_dir = os.path.join(base_dir, "knowledge")
            kb_data = {}
            for fname in ["recipes.json", "ingredients.json", "suppliers.json", "safety.json", "chef_notes.json", "seasonal.json", "pairing.json"]:
                fpath = os.path.join(kb_dir, fname)
                if os.path.exists(fpath):
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            kb_data[fname] = json.load(f)
                    except Exception as e:
                        logger.error(f"ChatbotService: Failed to load {fname}: {e}")
                        kb_data[fname] = []
                else:
                    kb_data[fname] = []
            ChatbotService._knowledge_cache = kb_data
        return ChatbotService._knowledge_cache
