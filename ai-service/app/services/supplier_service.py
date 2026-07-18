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
        "ivvali", "ledu", "chesi", "tinna", "tinali", "chudu", "kavali", "kalla"
    ]
    if any(word in text_lower for word in tenglish_keywords):
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
        
        # If ingredients list is provided, consolidate it to ingredient string
        if ingredients:
            ingredient_display = ", ".join([ing.strip() for ing in ingredients if ing.strip()])
        else:
            ingredient_display = ingredient.strip() if ingredient else ""

        logger.info(
            f"SupplierService: Drafting replenishment message. Supplier: {supplier_name} | "
            f"Ingredients: {ingredient_display} | Qty: {quantity} | Date: {required_date}"
        )
        
        # 1. Parameter Validation
        if not ingredient_display:
            raise HTTPException(status_code=400, detail="Ingredient name or list cannot be empty.")
        if not quantity or not quantity.strip():
            raise HTTPException(status_code=400, detail="Required quantity cannot be empty.")
        if not required_date or not required_date.strip():
            raise HTTPException(status_code=400, detail="Required date cannot be empty.")

        clean_supplier = supplier_name.strip() if (supplier_name and supplier_name.strip()) else "Supplier"
        clean_quantity = quantity.strip()
        clean_date = required_date.strip()

        # 2. Retrieve vendor context
        search_query = f"Supplier details for: {ingredient_display} {clean_supplier}"
        retriever_start = time.time()
        try:
            chunks = self.retriever.retrieve(search_query, top_k=10)
        except Exception as e:
            logger.error(f"SupplierService: Retriever failed: {str(e)}")
            chunks = []
        retriever_time_ms = int((time.time() - retriever_start) * 1000)

        # Filter chunks to suppliers only
        supplier_chunks = [c for c in chunks if "suppliers" in c.get("source", "").lower()]
        logger.info(f"SupplierService: Retrieved {len(chunks)} chunks, filtered to {len(supplier_chunks)} supplier chunks in {retriever_time_ms}ms")

        # 3. Format context block
        context_strs = []
        for i, chunk in enumerate(supplier_chunks):
            title = chunk.get("title", "unknown")
            content = chunk.get("content", "")
            context_strs.append(f"[Supplier Info #{i+1}] (Title: {title})\n{content}\n")
        context_block = "\n".join(context_strs) if context_strs else "No supplier contexts found."

        # 4. Construct Prompt
        try:
            prompt = build_supplier_prompt(
                clean_supplier, 
                ingredient_display, 
                clean_quantity, 
                clean_date, 
                context_block,
                restaurant_name=restaurant_name,
                contact_person=contact_person,
                supplier_email=supplier_email,
                supplier_phone=supplier_phone,
                urgency_level=urgency_level,
                language_preference=language_preference
            )
        except Exception as e:
            logger.error(f"SupplierService: Prompt creation failed: {str(e)}")
            prompt = f"Supplier: {clean_supplier}\nIngredient: {ingredient_display}\nQty: {clean_quantity}\nDate: {clean_date}\nContext: {context_block}"

        # 5. Call LLM Router
        router_result = None
        try:
            router_result = self.router.generate(prompt)
        except Exception as e:
            logger.error(f"SupplierService: Router call failed: {str(e)}")

        # 6. Parse structured response
        message_body = ""
        detected_lang = language_preference if language_preference else detect_language(clean_supplier + " " + ingredient_display)
        provider_used = "none"
        fallback_used = False
        
        if router_result and router_result.get("status") == "success":
            raw_text = router_result.get("response", "")
            provider_used = router_result.get("provider", "Gemini")
            fallback_used = router_result.get("fallback_used", False)
            
            try:
                parsed = OutputParser.parse_json(raw_text)
                message_body = parsed.get("message", "").strip()
                detected_lang = parsed.get("language", detected_lang)
            except Exception as e:
                logger.error(f"SupplierService: JSON parsing failed: {str(e)}")

        # 7. Post-processing (Trim whitespace, remove duplicate blank lines, unescape, enforce fallbacks)
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
            
        # Clean double-escaped newlines to render as actual formatted text
        message_body = message_body.replace("\\n", "\n")
        
        # Clean double empty lines and whitespace
        lines = [line.strip() for line in message_body.split("\n")]
        cleaned_lines = []
        for i, line in enumerate(lines):
            if i > 0 and line == "" and lines[i-1] == "":
                continue  # skip consecutive blank lines
            cleaned_lines.append(line)
        message_body = "\n".join(cleaned_lines).strip()

        # Generate a structured subject line
        subject = f"[{urgency_level.upper()}] Purchase Request: {ingredient_display} ({clean_quantity})"
        
        # Generate a unique tracking order ID
        order_id = f"KS-PR-{random.randint(10000, 99999)}"

        # Map provider name
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
