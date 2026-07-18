import json
import os
import random

# Resolve the absolute path to the "ai-service" folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_path(*paths):
    return os.path.join(BASE_DIR, *paths)

def load_json(path):
    if not os.path.exists(path):
        print(f"[ERROR] Required file not found: {path}")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_safety_json(ingredients):
    print("Generating safety.json...")
    safety_records = []
    
    storage_rules = {
        "Poultry": {"storage": "Refrigerator", "temp": "0°C to 2°C", "factor": 1.5},
        "Meat": {"storage": "Refrigerator", "temp": "0°C to 3°C", "factor": 1.5},
        "Seafood": {"storage": "Refrigerator", "temp": "-1°C to 1°C", "factor": 1.3},
        "Dairy": {"storage": "Refrigerator", "temp": "2°C to 4°C", "factor": 1.4},
        "Produce": {"storage": "Refrigerator", "temp": "4°C to 7°C", "factor": 1.6},
        "Pantry": {"storage": "Pantry", "temp": "15°C to 22°C", "factor": 1.2}
    }
    
    for ing in ingredients:
        cat = ing.get("category", "Pantry")
        shelf_life = ing.get("average_shelf_life_days", 5)
        
        rule_details = storage_rules.get(cat)
        if not rule_details:
            rule_details = {"storage": ing.get("storage_type", "Pantry"), "temp": "15°C to 22°C", "factor": 1.2}
            
        max_shelf_life = int(round(shelf_life * rule_details["factor"]))
        if max_shelf_life == shelf_life:
            max_shelf_life += 1
            
        safety_records.append({
            "ingredient": ing["ingredient_name"],
            "storage": rule_details["storage"],
            "recommended_temperature": rule_details["temp"],
            "maximum_shelf_life_days": max_shelf_life
        })
        
    output_path = get_path("app", "knowledge", "safety.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(safety_records, f, indent=2, ensure_ascii=False)
    print(f"[SUCCESS] Created safety.json with {len(safety_records)} records.")

def build_seasonal_json(ingredients):
    print("Generating seasonal.json...")
    seasonal_records = []
    
    seasons_data = {
        "Spring": {
            "categories": ["Breakfast", "Salads", "Beverages"],
            "pricing": "Favorable wholesale prices for spring onions, herbs, and fresh greens.",
            "tip": "Incorporate spring greens and fresh coriander leaf garnishes into the morning menu."
        },
        "Summer": {
            "categories": ["Salads", "Seafood", "Beverages"],
            "pricing": "Peak harvest; low prices for tomatoes, avocados, and fresh citrus.",
            "tip": "Promote chilled avocado salads and quick seared seafood to minimize kitchen heat."
        },
        "Autumn": {
            "categories": ["Soups", "Main Course", "Desserts"],
            "pricing": "Stable pricing for root vegetables, poultry, and baking supplies.",
            "tip": "Transition to slow-roasted chicken thighs and warm root vegetable soups."
        },
        "Winter": {
            "categories": ["Soups", "Main Course", "Desserts"],
            "pricing": "Elevated prices for imported greens; stable pricing for dairy and meat.",
            "tip": "Introduce warm desserts and heavy cream-based main course curries."
        }
    }
    
    produce_items = [ing["ingredient_name"] for ing in ingredients if ing["category"] == "Produce"]
    seafood_items = [ing["ingredient_name"] for ing in ingredients if ing["category"] == "Seafood"]
    dairy_items = [ing["ingredient_name"] for ing in ingredients if ing["category"] == "Dairy"]
    meat_items = [ing["ingredient_name"] for ing in ingredients if ing["category"] == "Meat"]
    
    seasons = ["Winter", "Spring", "Summer", "Autumn"]
    
    for week in range(1, 53):
        season_idx = (week - 1) // 13
        season = seasons[season_idx]
        s_data = seasons_data[season]
        
        random.seed(week)
        
        seasonal_items = []
        if season == "Summer" and produce_items and seafood_items:
            seasonal_items = random.sample(produce_items, min(3, len(produce_items))) + random.sample(seafood_items, min(1, len(seafood_items)))
        elif season == "Winter" and dairy_items and meat_items:
            seasonal_items = random.sample(dairy_items, min(2, len(dairy_items))) + random.sample(meat_items, min(2, len(meat_items)))
        else:
            all_pool = produce_items if produce_items else [ing["ingredient_name"] for ing in ingredients]
            seasonal_items = random.sample(all_pool, min(4, len(all_pool)))
            
        seasonal_records.append({
            "season": season,
            "week_number": week,
            "recommended_categories": s_data["categories"],
            "seasonal_ingredients": seasonal_items,
            "pricing_trend": s_data["pricing"],
            "special_menu_tip": s_data["tip"]
        })
        
    output_path = get_path("app", "knowledge", "seasonal.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(seasonal_records, f, indent=2, ensure_ascii=False)
    print(f"[SUCCESS] Created seasonal.json with {len(seasonal_records)} weekly records.")

def build_suppliers_json(ingredients):
    print("Generating suppliers.json...")
    
    cities = ["Hyderabad", "Bangalore", "Mumbai", "Chennai", "Delhi", "Pune", "Kolkata"]
    supplier_bases = [
        {"name": "Oceanic Seafood Distributors", "cat": "Seafood"},
        {"name": "Bay Area Catch", "cat": "Seafood"},
        {"name": "Valley Poultry Farms", "cat": "Poultry"},
        {"name": "Royal Broiler Farms", "cat": "Poultry"},
        {"name": "GreenGrocer Organics", "cat": "Produce"},
        {"name": "Urban Harvest & Greens", "cat": "Produce"},
        {"name": "Fresh Farms Co-op", "cat": "Produce"},
        {"name": "Gourmet Dairy Corp", "cat": "Dairy"},
        {"name": "Mother Dairy Wholesalers", "cat": "Dairy"},
        {"name": "A-One Grain & Spice Mills", "cat": "Pantry"},
        {"name": "Nile Spice Merchants", "cat": "Pantry"},
        {"name": "Deccan Meat Processing", "cat": "Meat"},
        {"name": "Apex Cattle & Broiler Ltd", "cat": "Meat"},
    ]
    
    suppliers = []
    supplier_id_count = 1
    
    ingredients_by_cat = {}
    for ing in ingredients:
        cat = ing["category"]
        if cat not in ingredients_by_cat:
            ingredients_by_cat[cat] = []
        ingredients_by_cat[cat].append(ing["ingredient_name"])
        
    for i in range(35):
        base = supplier_bases[i % len(supplier_bases)]
        city = cities[i % len(cities)]
        
        name = f"{base['name']} ({city})"
        cat = base["cat"]
        
        cat_ings = ingredients_by_cat.get(cat, [])
        random.seed(i)
        supplied_subset = random.sample(cat_ings, min(6, len(cat_ings))) if cat_ings else []
        
        email_prefix = name.lower().replace(" ", "").replace("(", "").replace(")", "").replace("&", "")
        email = f"orders@{email_prefix}.example.com"
        
        rating = round(random.uniform(4.0, 4.9), 1)
        delivery_time = random.choice([12, 24, 48])
        
        suppliers.append({
            "supplier_id": f"SUP{supplier_id_count:03d}",
            "supplier_name": name,
            "ingredient_category": cat,
            "supported_ingredients": supplied_subset,
            "delivery_time_hours": delivery_time,
            "city": city,
            "contact_email": email,
            "rating": rating
        })
        supplier_id_count += 1
        
    output_path = get_path("app", "knowledge", "suppliers.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(suppliers, f, indent=2, ensure_ascii=False)
    print(f"[SUCCESS] Created suppliers.json with {len(suppliers)} records.")

def build_chef_notes_json(recipes):
    print("Generating chef_notes.json...")
    
    cuisine_tips = {
        "Indian": [
            "Toast your whole cumin seeds and cardamom pods in hot oil first to release their essential oils.",
            "Always fry the onions until deep golden brown to create a sweet, rich base for curries.",
            "Add garam masala at the very end of cooking to preserve its complex aromatic oils."
        ],
        "Italian": [
            "Cook pasta 1-2 minutes less than the package instructions and finish it directly in the sauce.",
            "Save a cup of pasta cooking water to emulsify and bind the sauce to the pasta noodles.",
            "Finely grate parmesan off the block immediately before serving for the freshest dairy aroma."
        ],
        "Asian Fusion": [
            "Add soy sauce along the dry edges of the hot wok to caramelize it slightly for smoky flavor.",
            "Combine starch with water (slurry) before adding it to hot glaze to prevent lumps.",
            "Garnish stir-fry dishes with sesame seeds and fresh scallion greens at the very last second."
        ],
        "Mediterranean": [
            "Use extra virgin olive oil as a finishing garnish rather than a high-heat cooking oil.",
            "Rub dried oregano between your palms before adding to activate the herb oils.",
            "Let marinated poultry sit for 30 minutes to absorb the lemon-herb acid blend."
        ]
    }
    
    category_tips = {
        "Seafood": [
            "Sear salmon fillets skin-side down first on medium-high heat. Do not touch for 4 minutes to ensure a crispy skin.",
            "For tender fish, baste with melted butter and garlic cloves continuously during the final cooking phase.",
            "Always dry seafood fillets thoroughly with paper towels before cooking to prevent steaming."
        ],
        "Poultry": [
            "Allow cooked chicken breasts to rest covered under foil for 5 minutes to retain their moisture.",
            "To prevent drying out, slice chicken breasts horizontally to ensure uniform thickness for pan-searing.",
            "Marinate chicken in yogurt or lemon juice for at least 2 hours to tenderize the muscle fibers."
        ],
        "Vegetarian": [
            "Salt tomatoes 10 minutes before placing in salads to drain excess water and concentrate flavor.",
            "Wrap avocados tightly in plastic wrap with the seed left inside to prevent oxidation browning.",
            "Submerge slightly wilted spinach in an ice water bath for 15 minutes to restore crispness."
        ],
        "Desserts": [
            "Ensure butter, cream, and eggs are at room temperature before creaming to guarantee a smooth emulsion.",
            "Sift dry flour and baking powder together to distribute the leavening agents evenly."
        ]
    }
    
    chef_notes = []
    
    random.seed(42)
    for idx, recipe in enumerate(recipes[:90]):
        title = recipe["recipe_name"]
        cuisine = recipe.get("cuisine", "International")
        category = recipe.get("category", "Main Course")
        
        tips_pool = cuisine_tips.get(cuisine, []) + category_tips.get(category, [])
        if not tips_pool:
            tips_pool = [
                "Always prep and measure all ingredients (mise en place) before starting the cooking process.",
                "Season with salt and pepper in layers throughout the cooking process, not just at the end."
            ]
            
        tip = random.choice(tips_pool)
        
        chef_notes.append({
            "recipe": title,
            "tip": tip
        })
        
    output_path = get_path("app", "knowledge", "chef_notes.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chef_notes, f, indent=2, ensure_ascii=False)
    print(f"[SUCCESS] Created chef_notes.json with {len(chef_notes)} records.")

def main():
    recipes = load_json(get_path("app", "knowledge", "recipes.json"))
    ingredients = load_json(get_path("app", "knowledge", "ingredients.json"))
    
    if not recipes or not ingredients:
        print("[ERROR] Could not load recipes or ingredients. Ensure previous phases ran successfully.")
        return
        
    build_safety_json(ingredients)
    build_seasonal_json(ingredients)
    build_suppliers_json(ingredients)
    build_chef_notes_json(recipes)
    
    print("\n==================================================")
    print("[SUCCESS] All static databases generated successfully!")
    print("==================================================")

if __name__ == "__main__":
    main()
