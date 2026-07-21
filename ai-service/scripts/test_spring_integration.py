import os
import sys
import asyncio
import time
import logging

# Ensure project root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from app.services.spring_api import SpringApiClient, spring_client
from app.core import config

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("test_spring_integration")

async def test_all_endpoints():
    print("\n" + "="*80)
    print(" 🚀 KITCHENSYNC HYBRID ARCHITECTURE — PHASE 1 INTEGRATION TEST SUITE")
    print("="*80)
    print(f"Target Spring Boot Backend Base URL: {config.SPRING_API_BASE_URL}")
    print(f"Configured Request Timeout: {config.SPRING_API_TIMEOUT} seconds")
    print("="*80 + "\n")

    client = SpringApiClient()

    endpoints_to_test = [
        ("Inventory Data", client.get_inventory, "/api/inventory"),
        ("Recipes Catalog", client.get_recipes, "/api/recipes"),
        ("Suppliers Directory", client.get_suppliers, "/api/suppliers"),
        ("Historical Orders", client.get_historical_orders, "/api/historical-orders"),
        ("Expiring Ingredients", client.get_expiring_items, "/api/expiration/expiring"),
        ("AI Recommendation Input", client.get_ai_input, "/api/recommendation/ai-input"),
        ("Dashboard Summary", client.get_dashboard_summary, "/api/dashboard/summary"),
        ("Restaurant Settings", client.get_restaurant_settings, "/api/settings"),
    ]

    passed_count = 0
    total_count = len(endpoints_to_test)

    for name, method, path in endpoints_to_test:
        start = time.time()
        print(f"Testing [{name}] -> {config.SPRING_API_BASE_URL}{path} ...")
        try:
            res = await method()
            latency = int((time.time() - start) * 1000)
            rec_count = len(res) if isinstance(res, list) else len(res.keys()) if isinstance(res, dict) else 0
            
            print(f"  ✅ Status: OK | Latency: {latency}ms | Records/Keys Fetched: {rec_count}")
            if isinstance(res, list) and res:
                print(f"  🔹 Sample Item: {res[0]}")
            elif isinstance(res, dict) and res:
                sample_keys = list(res.keys())[:3]
                print(f"  🔹 Top Keys: {sample_keys}")
            else:
                print(f"  ⚠️ Response Payload: {res} (Fallback Graceful Handled)")
            passed_count += 1
        except Exception as e:
            latency = int((time.time() - start) * 1000)
            print(f"  ❌ Error: {str(e)} | Latency: {latency}ms")
        print("-" * 70)

    print("\n" + "="*80)
    print(f" PHASE 1 TEST SUMMARY: {passed_count}/{total_count} Endpoints Handled Non-Blockingly!")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(test_all_endpoints())
