import time
import random
import logging
from typing import Dict, Any, Optional, List
from fastapi import HTTPException
from app.rag.retriever import KnowledgeRetriever
from app.prompts.supplier_prompt import build_supplier_prompt
from app.llm.llm_router import LLMRouter
from app.llm.output_parser import OutputParser

logger = logging.getLogger("app.api")

import re

def detect_language(text: str) -> str:
    """
    Heuristic helper to detect language (english | telugu | tenglish).
    Uses regex word boundaries, interjections, and suffix patterns to prevent false positives.
    """
    if not text:
        return "english"
        
    if any(0x0C00 <= ord(char) <= 0x0C7F for char in text):
        return "telugu"
        
    text_lower = text.lower()
    tenglish_words = {
        "ohh", "oh", "oho", "ohho", "hurray", "hurey", "hurrah", "alright", "alrighty", "knaww",
        "knoww", "kneww", "accha", "aachcha", "acha", "aah", "aha", "ahha", "abba", "abbha",
        "ammo", "ammow", "ayyo", "ayyyo", "arey", "areyy", "are", "rey", "reyy", "ra", "raa",
        "bey", "bhey", "boss", "bro", "dude", "sir", "ji", "mama", "macha", "machi", "machan",
        "garu", "gaaru", "andi", "aandi", "ayya", "bhayya", "bhai", "bhaya", "anna", "annayya",
        "cheyyali", "migilindi", "ela", "enti", "avuthundi", "undhi", "vundhi", "leka", "mari",
        "kuda", "ala", "ippudu", "vacham", "cheddam", "ivvali", "ledu", "chesi", "tinna", "tinali",
        "chudu", "kavali", "ekkada", "vunai", "ayipoindhi", "valla", "cheyyi", "supliers", "nunchi",
        "kavalo", "tiskoni", "pettali", "kaavali", "undha", "kooda", "kaani", "enduku", "eppudu",
        "elaga", "alaage", "kudaa", "enni", "yenni", "etla", "yetla", "yela", "yenti", "yem", "emi",
        "sarlu", "saarlu", "chesukuntadu", "chesukuntaru", "chesukovali", "chesukoni", "chesku"
    }
    
    words = set(re.findall(r'\b[a-z]+\b', text_lower))
    if words.intersection(tenglish_words):
        return "tenglish"
        
    tenglish_regex = r'\b[a-z]+(?:kuntadu|kuntaru|kuntam|kovali|kovalani|kovalane|thundi|thunnaru|thari|thamu)\b'
    if re.search(tenglish_regex, text_lower):
        return "tenglish"
        
    return "english"

class SupplierService:
    """
    Enterprise AI Supplier Message Generator Service.
    Drafts professional purchase orders for low-stock ingredients using vendor information.
    """
    def __init__(self):
        self.retriever = KnowledgeRetriever()
        self.router = LLMRouter()

    def generate_supplier_message(
        self, 
        ingredient: str, 
        quantity: str,
        supplier_name: Optional[str] = None,
        required_date: Optional[str] = None,
        ingredients: Optional[List[str]] = None,
        restaurant_name: Optional[str] = "KitchenSync Bistro",
        contact_person: Optional[str] = "Kitchen Manager",
        supplier_email: Optional[str] = None,
        supplier_phone: Optional[str] = None,
        urgency_level: Optional[str] = "Normal",
        language_preference: Optional[str] = "English"
    ) -> Dict[str, Any]:
        """
        Drafts order replenishment request message for the specified ingredient(s).
        """
        start_time = time.time()
        
        if ingredients:
            ingredient_display = ", ".join([ing.strip() for ing in ingredients if ing.strip()])
        else:
            ingredient_display = ingredient.strip() if ingredient else ""

        logger.info(
            f"SupplierService: Drafting replenishment message. Supplier: {supplier_name} | "
            f"Ingredients: {ingredient_display} | Qty: {quantity} | Date: {required_date}"
        )
        
        if not ingredient_display:
            raise HTTPException(status_code=400, detail="Ingredient name or list cannot be empty.")
        if not quantity or not quantity.strip():
            raise HTTPException(status_code=400, detail="Required quantity cannot be empty.")
        if not required_date or not required_date.strip():
            raise HTTPException(status_code=400, detail="Required date cannot be empty.")

        clean_supplier = supplier_name.strip() if (supplier_name and supplier_name.strip()) else "Supplier"
        clean_quantity = quantity.strip()
        clean_date = required_date.strip()

        # Invoke the hybrid orchestration pipeline
        question = (
            f"Draft order replenishment request email for supplier: {clean_supplier} for ingredient: {ingredient_display} with quantity: {clean_quantity} required by: {clean_date}. "
            "You MUST respond with a valid JSON object matching the following structure:\n"
            "{\n"
            "  \"message\": \"The drafted email message body text to the supplier.\",\n"
            "  \"language\": \"English\"\n"
            "}\n"
            "Return ONLY the raw JSON. Do not include markdown code block syntax."
        )
        
        from app.services.hybrid_chat_service import HybridChatService
        hybrid_service = HybridChatService()
        result = hybrid_service.get_response_sync(question)
        
        message_body = ""
        detected_lang = language_preference if language_preference else result.get("language", "english")
        provider_used = result.get("provider", "Gemini")
        fallback_used = result.get("fallback_used", False)
        raw_text = result.get("answer", "")
        
        try:
            parsed = OutputParser.parse_json(raw_text)
            message_body = parsed.get("message", "").strip()
            detected_lang = parsed.get("language", detected_lang)
        except Exception as e:
            logger.error(f"SupplierService: JSON parsing failed: {str(e)}")

        if not message_body:
            logger.warning("SupplierService: Generation failed or empty. Applying fallback templates.")
            message_body = self._get_fallback_message(
                clean_supplier, 
                ingredient_display, 
                clean_quantity, 
                clean_date, 
                detected_lang,
                restaurant_name=restaurant_name,
                contact_person=contact_person
            )
            
        message_body = message_body.replace("\\n", "\n")
        
        lines = [line.strip() for line in message_body.split("\n")]
        cleaned_lines = []
        for i, line in enumerate(lines):
            if i > 0 and line == "" and lines[i-1] == "":
                continue
            cleaned_lines.append(line)
        message_body = "\n".join(cleaned_lines).strip()

        subject = f"[{urgency_level.upper()}] Purchase Request: {ingredient_display} ({clean_quantity})"
        order_id = f"KS-PR-{random.randint(10000, 99999)}"

        raw_prov = provider_used.lower()
        if "gemini" in raw_prov:
            provider_name = "Gemini"
        elif "openrouter" in raw_prov:
            provider_name = "OpenRouter"
        else:
            provider_name = provider_used.capitalize()

        total_latency = int((time.time() - start_time) * 1000)
        logger.info(
            f"SupplierService: Message generation complete. Latency: {total_latency}ms | Provider: {provider_name}"
        )
        
        return {
            "supplier_name": clean_supplier,
            "ingredient": ingredient_display,
            "message": message_body,
            "language": detected_lang.capitalize(),
            "subject": subject,
            "order_id": order_id,
            "urgency": urgency_level.capitalize()
        }

    def _get_fallback_message(
        self, 
        supplier: str, 
        ingredient: str, 
        quantity: str, 
        date: str, 
        language: str,
        restaurant_name: str = "KitchenSync Bistro",
        contact_person: str = "Kitchen Manager"
    ) -> str:
        """
        Structures backup request draft using validated input parameters based on detected language script.
        """
        lang = language.lower()
        dear_tag = f"Dear {supplier}" if supplier != "Supplier" else "Dear Supplier"
        
        if "telugu" in lang:
            return (
                f"ప్రియమైన {supplier},\n\n"
                f"మా బిజినెస్ అవసరాల కోసం {date} నాటికి {quantity} {ingredient} సరఫరా చేయవలసిందిగా కోరుతున్నాము. "
                f"దయచేసి దీనిని నిర్ధారించండి.\n\n"
                f"భవదీయుడు,\n"
                f"{contact_person}\n"
                f"{restaurant_name}"
            )
        elif "tenglish" in lang:
            return (
                f"Dear {supplier},\n\n"
                f"Maku {date} kalla {quantity} {ingredient} kavali. Plz availability confirmation ivvandi.\n\n"
                f"Regards,\n"
                f"{contact_person}\n"
                f"{restaurant_name}"
            )
        else:
            return (
                f"Dear {supplier},\n\n"
                f"We would like to order {quantity} of {ingredient} required by {date} for our restaurant operations. "
                f"Kindly confirm the availability and estimated delivery time.\n\n"
                f"Regards,\n"
                f"{contact_person}\n"
                f"{restaurant_name}"
            )
