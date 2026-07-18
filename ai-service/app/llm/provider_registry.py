from typing import Dict, Any, List
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

        # 2. Configure default priority ranking (Gemini -> Grok -> OpenRouter -> Together -> Fireworks -> DeepSeek -> Mistral)
        self.priority_order = [
            "gemini",
            "grok",
            "openrouter",
            "together_ai",
            "fireworks_ai",
            "deepseek",
            "mistral"
        ]

    def get_provider(self, name: str) -> Any:
        return self.providers.get(name)

    def get_active_providers_in_order(self) -> List[str]:
        """
        Returns list of provider names sorted by priority, filtered to only those with configured API keys.
        """
        active_list = []
        for name in self.priority_order:
            provider = self.providers.get(name)
            if provider and provider.api_key:
                active_list.append(name)
        return active_list
