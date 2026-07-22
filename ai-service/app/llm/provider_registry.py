from typing import Dict, Any, List
from app.core import config
from app.llm.providers.gemini_provider import GeminiProvider
from app.llm.providers.grok_provider import GrokProvider
from app.llm.providers.openrouter_provider import OpenRouterProvider
from app.llm.providers.together_provider import TogetherProvider
from app.llm.providers.fireworks_provider import FireworksProvider
from app.llm.providers.deepseek_provider import DeepSeekProvider
from app.llm.providers.mistral_provider import MistralProvider

class ProviderRegistry:
    """
    Registry for configuring, tracking, and prioritizing LLM providers.
    """
    # Cache to store permanently unhealthy/failing providers dynamically during runtime
    _unhealthy_providers = set()

    def __init__(self):
        # 1. Instantiate provider clients
        self.providers = {
            "gemini": GeminiProvider(),
            "grok": GrokProvider(),
            "openrouter": OpenRouterProvider(),
            "together_ai": TogetherProvider(),
            "fireworks_ai": FireworksProvider(),
            "deepseek": DeepSeekProvider(),
            "mistral": MistralProvider()
        }

        # 2. Configure default priority ranking based on config.PRIMARY_PROVIDER and config.FALLBACK_PROVIDER
        primary = getattr(config, "PRIMARY_PROVIDER", "gemini")
        fallback = getattr(config, "FALLBACK_PROVIDER", "openrouter")
        
        defaults = [
            "gemini",
            "openrouter",
            "together_ai",
            "deepseek",
            "mistral",
            "fireworks_ai",
            "grok"
        ]
        
        self.priority_order = []
        if primary in defaults:
            self.priority_order.append(primary)
        if fallback in defaults and fallback != primary:
            self.priority_order.append(fallback)
        for p in defaults:
            if p not in self.priority_order:
                self.priority_order.append(p)

    def get_provider(self, name: str) -> Any:
        return self.providers.get(name)

    def get_active_providers_in_order(self) -> List[str]:
        """
        Returns list of provider names sorted by priority, filtered to only those with configured, valid API keys.
        """
        active_list = []
        for name in self.priority_order:
            if name in ProviderRegistry._unhealthy_providers:
                continue
            provider = self.providers.get(name)
            if provider and provider.api_key:
                k = provider.api_key.lower().strip()
                # Exclude dummy/placeholder keys
                if not k or k.startswith("your-") or k.endswith("-here") or "placeholder" in k or k == "none" or k == "null":
                    continue
                active_list.append(name)
        return active_list
