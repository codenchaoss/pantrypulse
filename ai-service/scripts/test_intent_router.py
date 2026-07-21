import os
import sys

# Ensure project root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from app.routing.intent_router import IntentRouter
from app.models.intent_models import Intent, Route

def run_router_test():
    print("\n" + "="*80)
    print(" 🚀 KITCHENSYNC HYBRID ARCHITECTURE — PHASE 2 INTENT ROUTER TEST SUITE")
    print("="*80 + "\n")

    router = IntentRouter()

    test_queries = [
        # 1. Inventory Intent
        ("What is today's inventory?", Intent.INVENTORY, Route.SPRING_INVENTORY),
        ("Show current stock levels of ingredients", Intent.INVENTORY, Route.SPRING_INVENTORY),
        
        # 2. Recipes Intent
        ("How do I make Chilli Chicken?", Intent.RECIPE, Route.SPRING_RECIPES),
        ("Show my recipes catalog list", Intent.RECIPE, Route.SPRING_RECIPES),
        
        # 3. Suppliers Intent
        ("Who is the supplier for tomatoes?", Intent.SUPPLIER, Route.SPRING_SUPPLIERS),
        ("Show me vendors list and contact emails", Intent.SUPPLIER, Route.SPRING_SUPPLIERS),
        
        # 4. Pricing Intent
        ("What is the cost price and selling price of chilli chicken?", Intent.PRICING, Route.SPRING_RECIPES),
        
        # 5. Expiration Intent
        ("Are there any ingredients expiring tomorrow?", Intent.EXPIRATION, Route.SPRING_EXPIRATION),
        ("Check for expired or spoiled items in fridge", Intent.EXPIRATION, Route.SPRING_EXPIRATION),
        
        # 6. Dashboard Intent
        ("Give me the dashboard summary statistics", Intent.DASHBOARD, Route.SPRING_DASHBOARD),
        ("Show the general overview metrics report", Intent.DASHBOARD, Route.SPRING_DASHBOARD),
        
        # 7. Knowledge Intent (Pinecone)
        ("How should raw milk be stored?", Intent.KNOWLEDGE, Route.PINECONE),
        ("What is the food safety temperature danger zone?", Intent.KNOWLEDGE, Route.PINECONE),
        
        # 8. Hybrid Intent (Spring + Pinecone)
        ("Suggest today's menu using available ingredients", Intent.HYBRID, Route.HYBRID),
        ("What is the best recipe today based on my stock levels?", Intent.HYBRID, Route.HYBRID),
        
        # 9. General Chat
        ("Hello, who are you?", Intent.GENERAL_CHAT, Route.GEMINI_ONLY),
        ("Good morning, thank you for your help", Intent.GENERAL_CHAT, Route.GEMINI_ONLY),
        
        # 10. Unknown Intent
        ("What is the weather in Hyderabad today?", Intent.UNKNOWN, Route.UNKNOWN)
    ]

    passed_count = 0
    total_count = len(test_queries)

    for question, expected_intent, expected_route in test_queries:
        result = router.detect_intent(question)
        
        status = "✅ PASS" if (result.intent == expected_intent and result.route == expected_route) else "❌ FAIL"
        if status == "✅ PASS":
            passed_count += 1
            
        print(f"Query: '{question}'")
        print(f"  Result: {status}")
        print(f"  Detected Intent : {result.intent.value} (Expected: {expected_intent.value})")
        print(f"  Assigned Route  : {result.route.value} (Expected: {expected_route.value})")
        print(f"  Confidence Score: {result.confidence:.2f}")
        print(f"  Matched Keywords: {result.matched_keywords}")
        print(f"  Orchestration   : {result.reason}")
        print("-" * 75)

    print("\n" + "="*80)
    print(f" PHASE 2 TEST SUMMARY: {passed_count}/{total_count} Queries Routed Correctly!")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_router_test()
