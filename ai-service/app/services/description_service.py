import re
import time
import logging
from typing import List, Dict, Any
from fastapi import HTTPException
from app.rag.retriever import KnowledgeRetriever
from app.prompts.description_prompt import build_description_prompt
from app.llm.llm_router import LLMRouter
from app.llm.output_parser import OutputParser

logger = logging.getLogger("app.api")

def clean_menu_description(desc: str) -> str:
    """
    Strips raw scraping syntax, metadata headers, and website names from menu descriptions.
    """
    if not desc:
        return ""
    
    # Strip markdown symbols
    desc = desc.replace("**", "").replace("__", "").replace("*", "").replace("`", "")
    
    # Strip prefixes like "Recipe Name: ... Description: ..."
    desc = re.sub(r'\b(?:recipe name|description|category|cuisine|difficulty|prep time|prep time minutes|instructions|ingredients|bengali recipes|goan recipes|andhra recipes|telangana recipes|karnataka recipes)\b:?', "", desc, flags=re.IGNORECASE)
    
    # Strip specific scraping residue patterns
    scraped_patterns = [
        r'\b(?:www\.)?[a-zA-Z0-9-]+\.(?:com|org|net|edu|gov|co|info)\b',
        r'\b(?:click here|read more|adapted from|photo by|submitted by|recipe by|print recipe|newsletter|subscribe|yummly)\b'
    ]
    for pat in scraped_patterns:
        desc = re.sub(pat, "", desc, flags=re.IGNORECASE)
        
    # Clean up excess spaces and punctuation
    desc = re.sub(r'\s+', " ", desc)
    desc = desc.replace(" .", ".").replace(" ,", ",").strip()
    
    return desc

def detect_language(text: str) -> str:
    """
    Heuristic helper to detect language (english | telugu | tenglish).
    """
    text_lower = text.lower()
    has_telugu = any(0x0C00 <= ord(char) <= 0x0C7F for char in text)
    if has_telugu:
        return "telugu"
    tenglish_keywords = [
        "cheyyali", "migilindi", "ela", "enti", "avuthundi", "undhi", 
        "leka", "mari", "kuda", "ala", "ippudu", "vacham", "cheddam", 
        "ivvali", "ledu", "chesi", "tinna", "tinali", "chudu"
    ]
    if any(word in text_lower for word in tenglish_keywords):
        return "tenglish"
    return "english"

class DescriptionService:
    """
    Enterprise AI Menu Description Generator Service.
    Crafts elegant, premium customer-facing menu descriptions for suggested specials.
    """
    def __init__(self):
        self.retriever = KnowledgeRetriever()
        self.router = LLMRouter()

    def generate_descriptions(self, dishes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates premium descriptions for a list of target dishes.
        """
        start_time = time.time()
        logger.info(f"DescriptionService: Generating descriptions for dishes count: {len(dishes)}")
        
        # 1. Input Validation
        if not dishes:
            raise HTTPException(status_code=400, detail="Dishes list cannot be empty.")
            
        for item in dishes:
            name = item.get("dish")
            if not name or not name.strip():
                raise HTTPException(status_code=400, detail="Dish name cannot be empty.")

        # Remove duplicate input dishes to prevent wasteful LLM generation
        unique_dishes = []
        seen_names = set()
        for item in dishes:
            name = item.get("dish", "").strip()
            if name.lower() not in seen_names:
                unique_dishes.append(item)
                seen_names.add(name.lower())

        # 2. Retrieve relevant recipe chunks
        search_query = "Recipes description for: " + ", ".join([d.get("dish", "") for d in unique_dishes])
        retriever_start = time.time()
        try:
            chunks = self.retriever.retrieve(search_query, top_k=15)
        except Exception as e:
            logger.error(f"DescriptionService: Retriever failed: {str(e)}")
            chunks = []
        retriever_time_ms = int((time.time() - retriever_start) * 1000)
        
        # Filter chunks to recipes only
        recipe_chunks = [c for c in chunks if "recipes" in c.get("source", "").lower()]
        logger.info(f"DescriptionService: Retrieved {len(chunks)} chunks, filtered to {len(recipe_chunks)} recipe chunks in {retriever_time_ms}ms")

        # 3. Format context block
        context_strs = []
        for i, chunk in enumerate(recipe_chunks):
            title = chunk.get("title", "unknown")
            content = chunk.get("content", "")
            context_strs.append(f"[Recipe Info #{i+1}] (Title: {title})\n{content}\n")
        context_block = "\n".join(context_strs) if context_strs else "No context info retrieved."

        # 4. Construct prompt
        try:
            prompt = build_description_prompt(unique_dishes, context_block)
        except Exception as e:
            logger.error(f"DescriptionService: Prompt creation failed: {str(e)}")
            prompt = f"Target: {unique_dishes}\nContext: {context_block}"

        # 5. Call LLM Router
        router_result = None
        try:
            router_result = self.router.generate(prompt)
        except Exception as e:
            logger.error(f"DescriptionService: Router call failed: {str(e)}")

        # 6. Parse structured response
        generated_list = []
        provider_used = "none"
        fallback_used = False
        
        if router_result and router_result.get("status") == "success":
            raw_text = router_result.get("response", "")
            provider_used = router_result.get("provider", "Gemini")
            fallback_used = router_result.get("fallback_used", False)
            
            try:
                parsed = OutputParser.parse_json(raw_text)
                if "descriptions" in parsed and isinstance(parsed["descriptions"], list):
                    generated_list = parsed["descriptions"]
                else:
                    logger.warning("DescriptionService: Parsed JSON missing expected 'descriptions' key.")
            except Exception as e:
                logger.error(f"DescriptionService: JSON parsing failed: {str(e)}")

        # 7. Post-processing & Output sanitization
        # Map generated descriptions by dish name for O(1) lookup
        out_map = {item.get("dish", "").lower().strip(): item for item in generated_list}
        
        final_descriptions = []
        for dish_item in dishes:
            name = dish_item.get("dish", "").strip()
            category = dish_item.get("category", "")
            matched_item = out_map.get(name.lower())
            
            if matched_item:
                desc_text = clean_menu_description(matched_item.get("description", "").strip())
                # Verify description is not empty, if so use fallback
                if not desc_text:
                    desc_text = self._get_fallback_text(name, category, recipe_chunks)
                tone = matched_item.get("tone", "Premium")
                lang = matched_item.get("language", detect_language(name))
            else:
                desc_text = self._get_fallback_text(name, category, recipe_chunks)
                tone = "Premium"
                lang = detect_language(name)
                
            final_descriptions.append({
                "dish": name,
                "description": desc_text,
                "tone": tone,
                "language": lang
            })

        total_latency = int((time.time() - start_time) * 1000)
        logger.info(
            f"DescriptionService: Completed. Latency: {total_latency}ms | Provider: {provider_used} | Fallback used: {fallback_used}"
        )
        
        return {
            "descriptions": final_descriptions
        }

    def _get_fallback_text(self, name: str, category: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Generates a premium restaurant description fallback for the given dish.
        """
        cat_str = f" delicious {category.lower()}" if category else " culinary creation"
        return f"A premium{cat_str} featuring {name.title()}, prepared fresh using select spices and high-quality local ingredients for a truly authentic taste."
