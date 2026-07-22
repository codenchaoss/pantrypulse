import time
import httpx
import sys

BASE_URL = "http://127.0.0.1:8000"

# Define target endpoints, methods, and valid payloads
ENDPOINTS = [
    {
        "name": "Health Status Check",
        "path": "/health",
        "method": "GET",
        "payload": None
    },
    {
        "name": "Chatbot Orchestration",
        "path": "/chat",
        "method": "POST",
        "payload": {
            "question": "What is the recommended storage temperature of fresh salmon?"
        }
    },
    {
        "name": "Recipe Recommendation",
        "path": "/recipe",
        "method": "POST",
        "payload": {
            "ingredients": ["chicken", "potato", "tomato"]
        }
    },
    {
        "name": "Daily Specials Menu",
        "path": "/menu",
        "method": "POST",
        "payload": {
            "inventory": [
                {"ingredient": "potato", "quantity": "1kg", "expiry_days": 1}
            ]
        }
    },
    {
        "name": "Supplier Replenishment",
        "path": "/supplier",
        "method": "POST",
        "payload": {
            "ingredient": "chicken",
            "required_quantity": "5kg",
            "required_date": "tomorrow"
        }
    },
    {
        "name": "Menu Descriptions",
        "path": "/description",
        "method": "POST",
        "payload": {
            "dishes": [
                {"dish": "Chicken Biryani", "category": "Main Course"}
            ]
        }
    },
    {
        "name": "Profit Pricing Suggestions",
        "path": "/pricing",
        "method": "POST",
        "payload": {
            "dish": "Chicken Biryani",
            "ingredient_cost": 250.0
        }
    },
    {
        "name": "Inventory Optimization",
        "path": "/optimization",
        "method": "POST",
        "payload": {
            "inventory": [
                {"ingredient": "potato", "quantity": 1.0, "unit": "kg", "expiry_days": 1}
            ]
        }
    },
    {
        "name": "Orchestrate Workflow",
        "path": "/orchestrate",
        "method": "POST",
        "payload": {
            "inventory": [
                {"ingredient": "potato", "quantity": 1.0, "unit": "kg", "expiry_days": 1}
            ]
        }
    },
    {
        "name": "Publish Workflow Result",
        "path": "/workflow/publish",
        "method": "POST",
        "payload": {
            "optimization": {
                "recommended_dishes": [
                    {"dish": "Chicken Biryani", "servings": 30, "profit": 12000, "priority": "High"}
                ],
                "estimated_revenue": 18000,
                "currency": "INR",
                "purchase_required": True,
                "purchase_items": ["Chicken"],
                "reason": "Chicken expires in 1 day.",
                "language": "English"
            },
            "recipe": {"recipes": []},
            "menu": {"special_menu": []},
            "pricing": [],
            "description": {"descriptions": []},
            "supplier": [],
            "warnings": [],
            "workflow_status": "completed"
        }
    },
    {
        "name": "Update Application Plan",
        "path": "/application/update",
        "method": "POST",
        "payload": {
            "optimization": {
                "recommended_dishes": [
                    {"dish": "Chicken Biryani", "servings": 30, "profit": 12000, "priority": "High"}
                ],
                "estimated_revenue": 18000,
                "currency": "INR",
                "purchase_required": True,
                "purchase_items": ["Chicken"],
                "reason": "Chicken expires in 1 day.",
                "language": "English"
            },
            "recipe": {"recipes": []},
            "menu": {"special_menu": []},
            "pricing": [],
            "description": {"descriptions": []},
            "supplier": [],
            "warnings": [],
            "workflow_status": "completed"
        }
    }
]

def run_integration_tests():
    print("\n" + "="*80)
    print(" 🚀 KITCHENSYNC API LAYER INTEGRATION & SUCCESS STATUS CHECK")
    print("="*80)
    print(f"Target Server URL: {BASE_URL}")
    print("="*80 + "\n")

    passed_count = 0
    total_count = len(ENDPOINTS)

    client = httpx.Client(timeout=10.0)

    for i, ep in enumerate(ENDPOINTS, 1):
        name = ep["name"]
        path = ep["path"]
        method = ep["method"]
        payload = ep["payload"]

        url = f"{BASE_URL}{path}"
        print(f"[{i}/{total_count}] Testing {method} {path} ({name}) ...")

        start = time.time()
        try:
            if method == "GET":
                res = client.get(url)
            else:
                res = client.post(url, json=payload)
            
            latency = int((time.time() - start) * 1000)
            status_code = res.status_code
            
            # Parse response json
            data = res.json()
            success_status = data.get("success", False)
            
            # Check success condition
            is_ok = (status_code == 200 or status_code == 201) and success_status is True

            if is_ok:
                print(f"  ✅ Status: {status_code} | success: {success_status} | Latency: {latency}ms")
                passed_count += 1
            else:
                print(f"  ❌ Status: {status_code} | success: {success_status} | Latency: {latency}ms")
                print(f"     Response Body: {data}")
        except Exception as e:
            latency = int((time.time() - start) * 1000)
            print(f"  ❌ Error: {str(e)} | Latency: {latency}ms")
        
        print("-" * 70)

    client.close()

    print("\n" + "="*80)
    print(f" INTEGRATION STATUS SUMMARY: {passed_count}/{total_count} Endpoints Verified!")
    print("="*80 + "\n")

    if passed_count == total_count:
        print("🎉 ALL ENDPOINTS RETURNED STATUS 200 AND SUCCESS: TRUE!")
        sys.exit(0)
    else:
        print("⚠️ SOME ENDPOINTS ENCOUNTERED ERRORS OR RETURNED FAILED STATUS!")
        sys.exit(1)

if __name__ == "__main__":
    run_integration_tests()
