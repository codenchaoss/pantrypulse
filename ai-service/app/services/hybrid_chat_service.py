import logging
import time
import asyncio
import threading
from typing import Dict, Any, Optional

from app.routing.intent_router import IntentRouter
from app.services.context_builder import ContextBuilder
from app.services.prompt_builder import PromptBuilder
from app.services.gemini_service import GeminiService
from app.services.chatbot_service import detect_language, get_language_confidence

# Setup logger for Hybrid Orchestrator
logger = logging.getLogger("app.services.hybrid_chat_service")

def run_async_synchronously(coro):
    """
    Helper to run an async coroutine synchronously in a background thread.
    Prevents loop conflict in FastAPI/Uvicorn or CLI execution.
    """
    result = []
    exception = []

    def target():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(coro)
            result.append(res)
        except Exception as e:
            exception.append(e)
        finally:
            loop.close()

    thread = threading.Thread(target=target)
    thread.start()
    thread.join()

    if exception:
        raise exception[0]
    return result[0]

class HybridChatService:
    """
    Central Orchestration Pipeline for BOH AI Operations.
    Implements: Query -> IntentRouter -> ContextBuilder -> PromptBuilder -> GeminiService
    """
    def __init__(self):
        self.router = IntentRouter()
        self.context_builder = ContextBuilder()
        self.prompt_builder = PromptBuilder()
        self.gemini_service = GeminiService()

    async def get_response(self, question: str, history: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes the full hybrid orchestration pipeline asynchronously.
        Handles errors gracefully at each step.
        """
        start_time = time.time()
        
        # 1. Detect query language
        detected_lang = detect_language(question)
        confidence_score = get_language_confidence(question, detected_lang)
        
        # 2. Run Query Intent decision Router (Phase 2)
        try:
            route_res = self.router.detect_intent(question)
        except Exception as e:
            logger.error(f"[HYBRID_ORCHESTRATOR] Router failed: {str(e)}")
            from app.models.intent_models import IntentResult, Intent, Route
            route_res = IntentResult(intent=Intent.GENERAL_CHAT, route=Route.GEMINI_ONLY, confidence=0.5, matched_keywords=[])

        # 3. Gather Context Object (Phase 3 + Phase 5 HYBRID improvement)
        try:
            context = await self.context_builder.build_context(question, route_res)
        except Exception as e:
            logger.error(f"[HYBRID_ORCHESTRATOR] ContextBuilder failed: {str(e)}")
            from app.models.context_models import UnifiedContext
            context = UnifiedContext(
                intent=route_res.intent.value,
                route=route_res.route.value,
                live_data={},
                knowledge=[],
                metadata={"spring_calls": [], "pinecone_used": False, "error": str(e)}
            )

        # 4. Compile prompt (Phase 4)
        try:
            prompt_obj = self.prompt_builder.build_prompt(question, context)
        except Exception as e:
            logger.error(f"[HYBRID_ORCHESTRATOR] PromptBuilder failed: {str(e)}")
            from app.models.prompt_models import PromptObject
            prompt_obj = PromptObject(
                system_prompt="You are KitchenSync AI, a professional restaurant management assistant.",
                user_prompt=f"Question: {question}",
                intent=route_res.intent.value,
                route=route_res.route.value
            )

        # 5. Invoke LLM Manager (Phase 4)
        try:
            gemini_res = self.gemini_service.generate_response(prompt_obj)
        except Exception as e:
            logger.error(f"[HYBRID_ORCHESTRATOR] GeminiService failed: {str(e)}")
            from app.models.prompt_models import GeminiResponse
            gemini_res = GeminiResponse(
                response="Sorry, I couldn't generate a response at the moment.",
                metadata={"intent": route_res.intent.value, "route": route_res.route.value, "success": False}
            )

        # 6. Calculate total telemetry metrics
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Calculate retrieved chunk count
        retrieved_chunks = len(context.knowledge)
        
        # Extract sources based on context
        sources = []
        if context.knowledge:
            sources.extend(list(set(c.get("source", "unknown") for c in context.knowledge)))
        if context.live_data:
            sources.extend(list(context.live_data.keys()))
        sources = list(set(sources))
        if not sources:
            sources = ["general"]

        # Log complete request tracing
        logger.info(
            f"[TELEMETRY TRACE] Query: '{question}' | Intent: {route_res.intent.value} | "
            f"Route: {route_res.route.value} | Spring Calls: {context.metadata.get('spring_calls', [])} | "
            f"RAG Used: {context.metadata.get('pinecone_used', False)} | "
            f"Provider: {gemini_res.metadata.get('provider', 'Gemini')} | "
            f"Model: {gemini_res.metadata.get('model', 'unknown')} | "
            f"Success: {gemini_res.metadata.get('success', False)} | Latency: {latency_ms}ms"
        )

        return {
            "question": question,
            "language": detected_lang,
            "confidence": confidence_score,
            "answer": gemini_res.response,
            "sources": sources,
            "retrieved_chunks": retrieved_chunks,
            "provider": gemini_res.metadata.get("provider", "Gemini"),
            "fallback_used": not gemini_res.metadata.get("success", True),
            "response_time_ms": latency_ms,
            "intent": route_res.intent.value,
            "route": route_res.route.value
        }

    def get_response_sync(self, question: str, history: Optional[str] = None) -> Dict[str, Any]:
        """
        Synchronous entry point that runs the async orchestration pipeline in a safe background event loop.
        """
        return run_async_synchronously(self.get_response(question, history))
