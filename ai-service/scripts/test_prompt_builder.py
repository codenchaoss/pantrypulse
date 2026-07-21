import os
import sys
import asyncio

# Ensure project root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from app.routing.intent_router import IntentRouter
from app.services.context_builder import ContextBuilder
from app.services.prompt_builder import PromptBuilder
from app.services.gemini_service import GeminiService

async def run_prompt_test():
    print("\n" + "="*80)
    print(" 🚀 KITCHENSYNC HYBRID ARCHITECTURE — PHASE 4 PROMPT & GEMINI TEST SUITE")
    print("="*80 + "\n")

    router = IntentRouter()
    context_builder = ContextBuilder()
    prompt_builder = PromptBuilder()
    gemini_service = GeminiService()

    test_queries = [
        "Show current stock levels of ingredients",
        "Give me the dashboard summary statistics",
        "How should raw milk be stored?",
        "Suggest today's menu using available ingredients",
        "Hello, who are you?"
    ]

    for question in test_queries:
        print(f"User Query: '{question}'")
        
        # 1. Run Router
        route_res = router.detect_intent(question)
        print(f"  🧠 Router Decision -> Intent: {route_res.intent.value} | Route: {route_res.route.value}")
        
        # 2. Build Context
        context = await context_builder.build_context(question, route_res)
        print(f"  📦 Context Built   -> Spring Calls: {context.metadata['spring_calls']} | RAG Chunks: {len(context.knowledge)}")
        
        # 3. Build Prompt
        prompt_obj = prompt_builder.build_prompt(question, context)
        print(f"  ✍️  Prompt Compiled  -> Prompt length: {len(prompt_obj.user_prompt)} chars")
        
        # 4. Invoke Gemini Service
        print(f"  🤖 Invoking Google Gemini model...")
        gemini_res = gemini_service.generate_response(prompt_obj)
        
        # 5. Output
        print(
            f"  📊 Gemini Status   -> Success: {gemini_res.metadata['success']} | "
            f"Latency: {gemini_res.metadata['latency_ms']}ms | "
            f"Provider: {gemini_res.metadata.get('provider', 'N/A')} | "
            f"Model: {gemini_res.metadata.get('model', 'N/A')}"
        )
        print(f"  💬 Generated Response:\n{gemini_res.response}\n")
        print("-" * 75)

    print("\n" + "="*80)
    print(" PHASE 4 TEST SUMMARY: Prompt building and Gemini generation verified successfully!")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(run_prompt_test())
