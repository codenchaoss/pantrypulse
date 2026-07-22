import requests
import json

def test_workflow_publish_and_update():
    base_url = "http://127.0.0.1:8000"
    
    # Payload matching the exact failing cases (float price_confidence and string purchase_items)
    payload = {
        "optimization": {
            "recommended_dishes": [
                {
                    "dish": "Chicken Biryani",
                    "servings": 30,
                    "profit": 12000,
                    "priority": "High"
                }
            ],
            "estimated_revenue": 18000,
            "currency": "INR",
            "purchase_required": True,
            "purchase_items": ["Chicken", "Curd", "Mint"],
            "reason": "Chicken expires in 1 day.",
            "language": "English"
        },
        "recipe": {
            "recipes": [
                {
                    "recipe_id": "REC001",
                    "recipe_name": "Chicken Biryani",
                    "description": "Delicious spiced chicken biryani.",
                    "matched_ingredients": ["Chicken"],
                    "missing_ingredients": ["Curd"],
                    "match_percentage": 90,
                    "preparation_time_minutes": 45,
                    "difficulty": "Medium",
                    "estimated_calories": 500,
                    "reason_for_recommendation": "High margin and utilizes chicken nearing expiry.",
                    "confidence": 0.95
                }
            ]
        },
        "menu": {
            "special_menu": [
                {
                    "dish": "Chicken Biryani",
                    "reason": "Uses chicken nearing expiry.",
                    "matched_inventory": ["chicken"],
                    "missing_ingredients": [],
                    "estimated_profit": "₹450",
                    "priority": "HIGH",
                    "preparation_time": 45,
                    "difficulty": "Medium",
                    "confidence": 0.95
                }
            ]
        },
        "pricing": [
            {
                "dish": "Chicken Biryani",
                "ingredient_cost": 250.0,
                "recommended_price": 550,
                "estimated_profit": 300,
                "profit_margin": 54,
                "pricing_strategy": "Premium",
                "market_position": "Upscale",
                "price_confidence": 0.96
            }
        ],
        "description": {
            "descriptions": [
                {
                    "dish": "Chicken Biryani",
                    "description": "Spiced chicken cooked with premium basmati rice.",
                    "tone": "enticing",
                    "language": "English"
                }
            ]
        },
        "supplier": [
            {
                "supplier_name": "Fresh Foods Inc",
                "ingredient": "Curd",
                "message": "Please deliver 5 kg of curd by tomorrow.",
                "language": "English",
                "subject": "Replenishment order for Curd",
                "order_id": "ORD999",
                "urgency": "Normal"
            }
        ],
        "warnings": [],
        "workflow_status": "completed"
    }

    print("Testing POST /workflow/publish...")
    r1 = requests.post(f"{base_url}/workflow/publish", json=payload)
    print("Status:", r1.status_code)
    print("Response:", r1.text)
    assert r1.status_code == 200
    assert r1.json()["success"] is True

    print("\nTesting POST /application/update...")
    r2 = requests.post(f"{base_url}/application/update", json=payload)
    print("Status:", r2.status_code)
    print("Response:", r2.text)
    assert r2.status_code == 200
    assert r2.json()["success"] is True

    print("\nAll integration validation tests passed successfully!")

if __name__ == "__main__":
    test_workflow_publish_and_update()
