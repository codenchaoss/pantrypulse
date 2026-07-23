import json
import logging
from typing import Dict, Any, List, Optional
from app.llm.provider_registry import ProviderRegistry
from app.llm.retry_manager import RetryManager

logger = logging.getLogger("app.llm")

class ProviderManager:
    """
    Enterprise LLM Provider Manager.
    Iterates through the prioritised LLM registry, handles retries, and executes
    RAG-only fallback responses if all cloud API providers are unavailable.
    """
    def __init__(self):
        self.registry = ProviderRegistry()

    def generate(self, prompt: str, context_chunks: Optional[List[Dict[str, Any]]] = None, **kwargs) -> Dict[str, Any]:
        """
        Routes the prompt to the highest priority active provider.
        If all fail, executes RAG-only fallback response.
        """
        active_providers = self.registry.get_active_providers_in_order()
        logger.info(f"ProviderManager: Found active provider queue: {active_providers}")

        for name in active_providers:
            provider = self.registry.get_provider(name)
            if not provider:
                continue

            logger.info(f"ProviderManager: Attempting execution with provider: {name}")

            # Define execution wrapper for retry manager
            def run_provider():
                return provider.generate(prompt, **kwargs)

            try:
                # Execute provider with retries for transient errors
                res = RetryManager.execute_with_retry(run_provider, max_retries=0)
                if res.get("status") == "success":
                    text = res.get("text", "")
                    logger.info(f"ProviderManager: Provider {name} succeeded.")
                    return {
                        "status": "success",
                        "text": text,
                        "provider": name,
                        "model": getattr(provider, "model", name),
                        "error": None
                    }
                else:
                    err_msg = str(res.get("error", ""))
                    logger.warning(f"ProviderManager: Provider {name} failed with error: {err_msg}")
                    if any(code in err_msg for code in ["404", "401", "403"]) or any(kw in err_msg.lower() for kw in ["not found", "unauthorized", "invalid", "quota"]):
                        logger.error(f"ProviderRegistry: Marking provider '{name}' as permanently unhealthy due to: {err_msg}")
                        ProviderRegistry._unhealthy_providers.add(name)
            except Exception as e:
                err_msg = str(e)
                logger.warning(f"ProviderManager: Provider {name} raised exception: {err_msg}")
                if any(code in err_msg for code in ["404", "401", "403"]) or any(kw in err_msg.lower() for kw in ["not found", "unauthorized", "invalid", "quota"]):
                    logger.error(f"ProviderRegistry: Marking provider '{name}' as permanently unhealthy due to: {err_msg}")
                    ProviderRegistry._unhealthy_providers.add(name)

        # If we reach here, all cloud providers failed. Fallback to RAG-only mode!
        logger.error("ProviderManager: All cloud LLM providers failed or are unconfigured. Triggering RAG-only fallback...")
        fallback_text = self._synthesize_rag_fallback(context_chunks, prompt)
        return {
            "status": "success",
            "text": fallback_text,
            "provider": "RAG-only Fallback",
            "model": "Local Retrieval",
            "error": None
        }

    def _synthesize_rag_fallback(self, chunks: Optional[List[Dict[str, Any]]] = None, prompt: str = "") -> str:
        """
        Constructs a structured, human-readable summary response from retrieved knowledge chunks
        without using any LLM call.
        """
        import re
        
        # Extract actual user question from the compiled prompt (which includes system instructions)
        match = re.search(r'(?:User Question Query|Question):\s*(.*?)(?:\n|$)', prompt, re.IGNORECASE)
        actual_query = match.group(1).strip() if match else prompt.strip()
        
        p_low = actual_query.lower()
        greetings = {
            "hi", "hello", "hey", "hii", "helloo", "who are you", "what is your name", "who are you?", "what are you?",
            "namaste", "namaskaram", "hai", "hlo"
        }
        
        # Check if the entire prompt is exactly a greeting or if the first word is a greeting (for short phrases)
        first_word = p_low.split()[0] if p_low else ""
        if p_low in greetings or (len(p_low.split()) <= 2 and first_word in greetings):
            return "Hello! I am KitchenSync AI, your smart kitchen and restaurant management assistant. How can I help you today?"

        if not chunks:
            return "I couldn't find the specific details you're looking for. Please contact the Restaurant Manager or the Reception desk for immediate assistance."

        # Filter out general/empty contexts
        recipes = []
        notes = []
        general = []

        for chunk in chunks:
            src = chunk.get("source", "")
            content = chunk.get("content", "")
            title = chunk.get("title", "")
            
            # Check if JSON recipe representation can be loaded
            if src == "recipes":
                try:
                    # Look for JSON structure markers
                    if "{" in content and "}" in content:
                        start_idx = content.find("{")
                        end_idx = content.rfind("}") + 1
                        recipe_data = json.loads(content[start_idx:end_idx])
                        recipes.append(recipe_data)
                    else:
                        recipes.append({"recipe_name": title, "raw_content": content})
                except Exception:
                    recipes.append({"recipe_name": title, "raw_content": content})
            elif src in ("chef_notes", "safety", "seasonal"):
                notes.append({"source": src, "title": title, "content": content})
            else:
                general.append(content)

        response_lines = [
            "I couldn't access an AI model right now, but based on the restaurant knowledge base I found the following information:\n"
        ]

        if recipes:
            for r in recipes[:3]:  # Show top 3 recipes
                name = r.get("recipe_name") or r.get("title") or "Unnamed Recipe"
                response_lines.append(f"Dish:\n{name}\n")
                
                prep = r.get("preparation_time_minutes") or r.get("prep_time") or r.get("preparation_time")
                if prep:
                    response_lines.append(f"Preparation Time:\n{prep} mins\n")
                    
                ingredients = r.get("ingredients") or r.get("matched_ingredients")
                if ingredients:
                    response_lines.append("Ingredients:")
                    if isinstance(ingredients, list):
                        for ing in ingredients[:8]:
                            response_lines.append(f"• {ing}")
                    else:
                        response_lines.append(str(ingredients))
                    response_lines.append("")
                    
                category = r.get("category") or r.get("cuisine")
                if category:
                    response_lines.append(f"Category:\n{category}\n")
                    
                desc = r.get("description")
                if desc:
                    response_lines.append(f"Description:\n{desc}\n")
                    
                steps = r.get("instructions") or r.get("steps")
                if steps:
                    response_lines.append("Preparation Steps:")
                    if isinstance(steps, list):
                        for i, step in enumerate(steps[:4]):
                            response_lines.append(f"{i+1}. {step}")
                    else:
                        response_lines.append(str(steps))
                    response_lines.append("")
                    
                if "raw_content" in r:
                    cleaned_raw = r["raw_content"]
                    # If it has [EXACT DISH FOUND IN MENU] markers
                    cleaned_raw = cleaned_raw.replace("[EXACT DISH FOUND IN MENU]", "").replace("[ALTERNATIVE SUGGESTION]", "").strip()
                    response_lines.append(f"Details:\n{cleaned_raw}\n")

        if notes:
            response_lines.append("Operational Notes & Guides:")
            for n in notes[:3]:
                title = n.get("title") or "Note"
                src = n.get("source", "").replace("_", " ").title()
                content = n.get("content", "").replace("[EXACT DISH FOUND IN MENU]", "").replace("[ALTERNATIVE SUGGESTION]", "").strip()
                response_lines.append(f"• [{src}] {title}: {content}")
            response_lines.append("")

        if general and not recipes and not notes:
            for g in general[:2]:
                response_lines.append(f"• {g.strip()}")

        response_lines.append("This information is retrieved directly from the restaurant knowledge base.")
        
        # Clean double newlines and clean formatting
        output = "\n".join(response_lines)
        while "\n\n\n" in output:
            output = output.replace("\n\n\n", "\n\n")
        return output.strip()
