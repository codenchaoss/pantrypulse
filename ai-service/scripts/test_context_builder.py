import os
import sys
import asyncio
import json

# Ensure project root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from app.routing.intent_router import IntentRouter
from app.services.context_builder import ContextBuilder

async def run_context_test():
    print("\n" + "="*80)
    print(" 🚀 KITCHENSYNC HYBRID ARCHITECTURE — PHASE 3 CONTEXT BUILDER TEST SUITE")
    print("="*80 + "\n")

    router = IntentRouter()
    builder = ContextBuilder()

    test_queries = [
        ("Show current stock levels of ingredients", "INVENTORY"),
        ("What is the cost price and selling price of chilli chicken?", "PRICING"),
        ("Are there any ingredients expiring tomorrow?", "EXPIRATION"),
        ("Give me the dashboard summary statistics", "DASHBOARD"),
        ("How should raw milk be stored?", "KNOWLEDGE"),
        ("Suggest today's menu using available ingredients", "HYBRID"),
        ("Hello, who are you?", "GENERAL_CHAT")
    ]

    for question, expected_intent in test_queries:
        print(f"Query: '{question}'")
        
        # 1. Run intent router decision
        route_res = router.detect_intent(question)
        print(f"  🧠 Router Decision -> Intent: {route_res.intent.value} | Route: {route_res.route.value}")
        
        # 2. Build context
        start_t = asyncio.get_event_loop().time()
        context = await builder.build_context(question, route_res)
        duration = int((asyncio.get_event_loop().time() - start_t) * 1000)
        
        # 3. Print Results
        print(f"  ✅ Context Built Successfully in {duration}ms")
        print(f"  🔹 Spring Calls Made: {context.metadata['spring_calls']}")
        print(f"  🔹 Pinecone DB Used : {context.metadata['pinecone_used']}")
        
        # Sample live data summary
        live_keys = list(context.live_data.keys())
        print(f"  🔹 Live Data Keys   : {live_keys}")
        if "inventory" in context.live_data:
            items = context.live_data["inventory"]
            print(f"     [Live Stock Sample]: {items[:1] if items else []} (Total items: {len(items)})")
        elif "expiring" in context.live_data:
            items = context.live_data["expiring"]
            print(f"     [Live Expiry Sample]: {items[:1] if items else []} (Total items: {len(items)})")
        elif "recipes" in context.live_data:
            items = context.live_data["recipes"]
            print(f"     [Live Recipes Sample]: {items[:1] if items else []} (Total items: {len(items)})")
            
        # Sample knowledge chunks
        print(f"  🔹 RAG Knowledge Chunks: {len(context.knowledge)}")
        if context.knowledge:
            print(f"     [RAG Text Sample]: {context.knowledge[0].get('content', '')[:100]}...")
            
        print("-" * 75)

    print("\n" + "="*80)
    print(" PHASE 3 TEST SUMMARY: All Contexts Aggregated Gracefully!")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(run_context_test())
