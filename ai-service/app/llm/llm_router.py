import time
import logging
from typing import Dict, Any, List, Optional
from app.llm.provider_manager import ProviderManager
from app.llm.output_parser import OutputParser

logger = logging.getLogger("app.llm")

class LLMRouter:
    """
    Central decision and routing layer.
    Exposes a unified interface that routes prompts to the ProviderManager
    and formats responses using the OutputParser schema.
    """
    def __init__(self):
        self.manager = ProviderManager()

    def generate(self, prompt: str, context_chunks: Optional[List[Dict[str, Any]]] = None, **kwargs) -> Dict[str, Any]:
        """
        Executes LLM request through the ProviderManager with multi-provider fallback.
        """
        start_time = time.time()
        
        # Execute manager routing
        res = self.manager.generate(prompt, context_chunks, **kwargs)
        
        response_time_ms = int((time.time() - start_time) * 1000)
        provider_name = res.get("provider", "none")
        model_name = res.get("model", "none")
        text = res.get("text", "")
        
        # Determine fallback usage (fallback is True if the successful provider is not gemini)
        fallback_used = (provider_name.lower() != "gemini")
        status = "success" if text else "failed"

        logger.info(
            f"LLMRouter: Handled request via '{provider_name}' | Model: '{model_name}' | "
            f"Fallback Used: {fallback_used} | Latency: {response_time_ms}ms"
        )

        return OutputParser.format_output(
            response=text,
            provider=provider_name,
            model=model_name,
            response_time_ms=response_time_ms,
            fallback_used=fallback_used,
            status=status
        )
