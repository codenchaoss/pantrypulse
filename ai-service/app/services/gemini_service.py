import time
import logging
from app.models.prompt_models import PromptObject, GeminiResponse
from app.llm.provider_manager import ProviderManager

# Setup logger for Gemini Service
logger = logging.getLogger("app.services.gemini_service")

class GeminiService:
    """
    Integrates PromptBuilder output with Google Gemini Client.
    Executes content generation prompts and formats results into a structured GeminiResponse.
    """

    def __init__(self):
        # Reuse existing Enterprise Provider Manager with built-in multi-provider fallbacks
        self.manager = ProviderManager()

    def generate_response(self, prompt_obj: PromptObject) -> GeminiResponse:
        """
        Invokes Gemini API using the formatted PromptObject.
        Utilizes ProviderManager to handle fallback models (OpenRouter, Gemini) when rate limited (HTTP 429).
        """
        start_time = time.time()
        
        # Combine System Prompt and User Prompt to fit existing base client signature
        combined_prompt = f"{prompt_obj.system_prompt}\n\n{prompt_obj.user_prompt}"
        prompt_len = len(combined_prompt)
        
        logger.info(
            f"[GEMINI_SERVICE] Invoking ProviderManager | "
            f"Intent: {prompt_obj.intent} | Route: {prompt_obj.route} | Prompt Len: {prompt_len} chars"
        )
        
        try:
            # Generate content using the prioritised provider queue (OpenRouter -> Gemini -> Fallback)
            res = self.manager.generate(combined_prompt)
            latency_ms = int((time.time() - start_time) * 1000)
            
            if res.get("status") == "success":
                response_text = res.get("text", "").strip()
                metadata = {
                    "intent": prompt_obj.intent,
                    "route": prompt_obj.route,
                    "success": True,
                    "latency_ms": latency_ms,
                    "provider": res.get("provider", "unknown"),
                    "model": res.get("model", "unknown")
                }
                logger.info(f"[GEMINI_SERVICE SUCCESS] Generation completed via {metadata['provider']} in {latency_ms}ms")
                return GeminiResponse(response=response_text, metadata=metadata)
            else:
                err_msg = res.get("error", "All LLM providers failed to respond.")
                logger.error(f"[GEMINI_SERVICE ERROR] All providers failed: {err_msg}")
                metadata = {
                    "intent": prompt_obj.intent,
                    "route": prompt_obj.route,
                    "success": False,
                    "latency_ms": latency_ms,
                    "error": err_msg
                }
                fallback_txt = "Sorry, I couldn't generate a response at the moment."
                return GeminiResponse(response=fallback_txt, metadata=metadata)
                
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"[GEMINI_SERVICE EXCEPTION] Unexpected error during manager execution: {str(e)}")
            metadata = {
                "intent": prompt_obj.intent,
                "route": prompt_obj.route,
                "success": False,
                "latency_ms": latency_ms,
                "error": str(e)
            }
            fallback_txt = "Sorry, I couldn't generate a response at the moment."
            return GeminiResponse(response=fallback_txt, metadata=metadata)
