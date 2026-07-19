import os
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Resolve paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "app", "knowledge")

def load_json(filename):
    path = os.path.join(KNOWLEDGE_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(filename, data):
    path = os.path.join(KNOWLEDGE_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Updated {filename}. Total records: {len(data)}")

def enrich():
    logger.info("Starting Restaurant Knowledge Base Enrichment...")

    # ==========================================
    # 1. Enrich ingredients.json
    # ==========================================
    ingredients = load_json("ingredients.json")
    existing_ing_names = {item["ingredient_name"].lower().strip() for item in ingredients}
    
    new_ingredients = [
        {
            "ingredient_id": "ING9001",
            "ingredient_name": "Paneer",
            "category": "Dairy",
            "unit": "kg",
            "average_shelf_life_days": 7,
            "storage_type": "Refrigerator",
            "minimum_quantity_alert": 5.0,
            "common_usage": "Paneer is a fresh cottage cheese popular in South Asian dishes. In commercial kitchens, keep it refrigerated between 2°C to 4°C. Check for sour smell, sticky surface, or yellowing to detect spoilage. Do not freeze paneer directly as it ruins the soft texture."
        },
        {
            "ingredient_id": "ING9002",
            "ingredient_name": "Tomato",
            "category": "Produce",
            "unit": "kg",
            "average_shelf_life_days": 7,
            "storage_type": "Refrigerator",
            "minimum_quantity_alert": 10.0,
            "common_usage": "Tomatoes are fresh produce used for gravies, rasam, and salads. Keep refrigerated at 4°C to 7°C. Avoid storing them in the walk-in freezer to prevent ice crystal damage. Signs of spoilage include soft spots, leakage, or black mold."
        },
        {
            "ingredient_id": "ING9003",
            "ingredient_name": "Chicken",
            "category": "Meat",
            "unit": "kg",
            "average_shelf_life_days": 3,
            "storage_type": "Refrigerator",
            "minimum_quantity_alert": 15.0,
            "common_usage": "Raw chicken must be stored on the lowest shelf of the refrigerator at 0°C to 2°C to prevent cross-contamination. Always sanitize cutting boards and knives with food-grade sanitizer immediately after handling raw poultry."
        },
        {
            "ingredient_id": "ING9004",
            "ingredient_name": "Ghee",
            "category": "Dairy",
            "unit": "kg",
            "average_shelf_life_days": 180,
            "storage_type": "Pantry",
            "minimum_quantity_alert": 5.0,
            "common_usage": "Clarified butter (Ghee) is shelf-stable and should be stored in a dry pantry in airtight containers to prevent moisture absorption. Spoilage signs include rancid smell or discoloration."
        },
        {
            "ingredient_id": "ING9005",
            "ingredient_name": "Coriander",
            "category": "Produce",
            "unit": "kg",
            "average_shelf_life_days": 4,
            "storage_type": "Refrigerator",
            "minimum_quantity_alert": 2.0,
            "common_usage": "Fresh coriander leaves wilt quickly. Store dry, wrapped in paper towels inside a perforated container in the vegetable drawer at 4°C to 7°C. Discard if slimy or black."
        },
        {
            "ingredient_id": "ING9006",
            "ingredient_name": "Curry Leaves",
            "category": "Produce",
            "unit": "kg",
            "average_shelf_life_days": 10,
            "storage_type": "Refrigerator",
            "minimum_quantity_alert": 1.0,
            "common_usage": "Curry leaves are a key aromatic. Store dry in an airtight container under refrigeration. Blackening indicates spoilage."
        },
        {
            "ingredient_id": "ING9007",
            "ingredient_name": "Tamarind",
            "category": "Pantry",
            "unit": "kg",
            "average_shelf_life_days": 365,
            "storage_type": "Pantry",
            "minimum_quantity_alert": 5.0,
            "common_usage": "Aged tamarind pulp is shelf-stable. Store in a cool, dry pantry in glass or food-safe plastic containers. Avoid metal containers to prevent acid reaction."
        },
        {
            "ingredient_id": "ING9008",
            "ingredient_name": "Coconut",
            "category": "Produce",
            "unit": "pcs",
            "average_shelf_life_days": 14,
            "storage_type": "Refrigerator",
            "minimum_quantity_alert": 10.0,
            "common_usage": "Once cracked, fresh grated coconut must be stored in the freezer at -18°C or refrigerator at 2°C to 4°C to avoid souring. Mold or off-odor indicates spoilage."
        },
        {
            "ingredient_id": "ING9009",
            "ingredient_name": "Rice",
            "category": "Pantry",
            "unit": "kg",
            "average_shelf_life_days": 365,
            "storage_type": "Pantry",
            "minimum_quantity_alert": 50.0,
            "common_usage": "Raw rice should be kept in airtight commercial bins to avoid moisture and weevil infestation. Standard preparation involves washing and soaking for 20-30 minutes before boiling."
        },
        {
            "ingredient_id": "ING9010",
            "ingredient_name": "Maida",
            "category": "Pantry",
            "unit": "kg",
            "average_shelf_life_days": 180,
            "storage_type": "Pantry",
            "minimum_quantity_alert": 20.0,
            "common_usage": "Refined wheat flour (Maida) must be stored in dry, moisture-free pantry bins. Sift before use to check for lumps or beetles."
        },
        {
            "ingredient_id": "ING9011",
            "ingredient_name": "Besan",
            "category": "Pantry",
            "unit": "kg",
            "average_shelf_life_days": 180,
            "storage_type": "Pantry",
            "minimum_quantity_alert": 15.0,
            "common_usage": "Gram flour (Besan) is used for pakoras and batters. Keep dry in airtight containers to prevent clumping."
        },
        {
            "ingredient_id": "ING9012",
            "ingredient_name": "Soft Drinks",
            "category": "Pantry",
            "unit": "L",
            "average_shelf_life_days": 120,
            "storage_type": "Pantry",
            "minimum_quantity_alert": 24.0,
            "common_usage": "Assorted sodas, colas, and carbonated beverages. Keep in pantry or front-of-house beverage chiller at 4°C to 6°C."
        },
        {
            "ingredient_id": "ING9013",
            "ingredient_name": "Ice Cream",
            "category": "Dairy",
            "unit": "kg",
            "average_shelf_life_days": 60,
            "storage_type": "Frozen",
            "minimum_quantity_alert": 10.0,
            "common_usage": "Store walk-in freezer ice cream tubs strictly at -18°C or below. Ensure the freezer lid is tightly shut to prevent freezer burn and crystallization."
        },
        {
            "ingredient_id": "ING9014",
            "ingredient_name": "Measuring Cup",
            "category": "Pantry",
            "unit": "pcs",
            "average_shelf_life_days": 365,
            "storage_type": "Pantry",
            "minimum_quantity_alert": 5.0,
            "common_usage": "Used for standardized kitchen portions and baking measurements."
        },
        {
            "ingredient_id": "ING9015",
            "ingredient_name": "Chef Knife",
            "category": "Pantry",
            "unit": "pcs",
            "average_shelf_life_days": 365,
            "storage_type": "Pantry",
            "minimum_quantity_alert": 2.0,
            "common_usage": "Multi-purpose chef knife. Must be cleaned, dried, and stored on the magnetic strip or drawer near the preparation station."
        }
    ]

    added_ingredients = 0
    for ing in new_ingredients:
        if ing["ingredient_name"].lower().strip() not in existing_ing_names:
            ingredients.append(ing)
            added_ingredients += 1
            
    save_json("ingredients.json", ingredients)
    logger.info(f"Added {added_ingredients} new ingredients.")

    # ==========================================
    # 2. Enrich chef_notes.json
    # ==========================================
    chef_notes = load_json("chef_notes.json")
    existing_tips = {item["tip"].lower().strip() for item in chef_notes}
    
    new_tips = [
        {
            "recipe": "Special Sugandha Drink (V5)",
            "tip": "Kitchen SOP: Chef knives are stored on the magnetic strip or in the designated knife drawer near the preparation station. Boning knives are kept in the meat section. (Reference ID: CN_901)"
        },
        {
            "recipe": "Bael Ka Sharbat Recipe - Wood Apple Squash Drink",
            "tip": "Inventory Rule: Rotate milk cartons and dairy products using the First-In-First-Out (FIFO) method to ensure older stock is consumed first. (Reference ID: CN_902)"
        },
        {
            "recipe": "Special Sugandha Drink (V5)",
            "tip": "Spoilage SOP: If paneer smells sour, shows sticky surface, or turns yellow, discard immediately in the organic waste bin. (Reference ID: CN_903)"
        },
        {
            "recipe": "Bael Ka Sharbat Recipe - Wood Apple Squash Drink",
            "tip": "Hygiene SOP: Clean and sanitize chopping boards with food-grade sanitizing spray immediately after cutting raw chicken to avoid cross-contamination. (Reference ID: CN_904)"
        },
        {
            "recipe": "Special Sugandha Drink (V5)",
            "tip": "Safety SOP: Keep a Class K kitchen fire extinguisher near the cooking station. In case of an oil fire, never use water; cover with a metal lid or damp cloth. (Reference ID: CN_905)"
        },
        {
            "recipe": "Dish V512 Special",
            "tip": "Equipment SOP: Walk-in freezer ice cream tubs must be stored strictly at -18°C or below. Ensure the freezer lid is shut tightly to avoid freezer burn. (Reference ID: CN_906)"
        },
        {
            "recipe": "Dish V512 Special",
            "tip": "Safety SOP: Wash hands for at least 20 seconds with warm water and soap before prep work and after using the restroom. (Reference ID: CN_907)"
        }
    ]

    added_tips = 0
    for tip in new_tips:
        if tip["tip"].lower().strip() not in existing_tips:
            chef_notes.append(tip)
            added_tips += 1
            
    save_json("chef_notes.json", chef_notes)
    logger.info(f"Added {added_tips} new chef notes.")

    # ==========================================
    # 3. Enrich safety.json
    # ==========================================
    safety = load_json("safety.json")
    existing_safety = {item["ingredient"].lower().strip() for item in safety}
    
    new_safety = [
        {
            "ingredient": "Paneer",
            "storage": "Refrigerator",
            "recommended_temperature": "2°C to 4°C",
            "maximum_shelf_life_days": 10
        },
        {
            "ingredient": "Tomato",
            "storage": "Refrigerator",
            "recommended_temperature": "4°C to 7°C",
            "maximum_shelf_life_days": 11
        },
        {
            "ingredient": "Chicken",
            "storage": "Refrigerator",
            "recommended_temperature": "0°C to 2°C",
            "maximum_shelf_life_days": 4
        },
        {
            "ingredient": "Ghee",
            "storage": "Pantry",
            "recommended_temperature": "15°C to 22°C",
            "maximum_shelf_life_days": 240
        },
        {
            "ingredient": "Coriander",
            "storage": "Refrigerator",
            "recommended_temperature": "4°C to 7°C",
            "maximum_shelf_life_days": 6
        },
        {
            "ingredient": "Curry Leaves",
            "storage": "Refrigerator",
            "recommended_temperature": "4°C to 7°C",
            "maximum_shelf_life_days": 15
        },
        {
            "ingredient": "Tamarind",
            "storage": "Pantry",
            "recommended_temperature": "15°C to 22°C",
            "maximum_shelf_life_days": 450
        },
        {
            "ingredient": "Coconut",
            "storage": "Refrigerator",
            "recommended_temperature": "2°C to 4°C",
            "maximum_shelf_life_days": 20
        },
        {
            "ingredient": "Rice",
            "storage": "Pantry",
            "recommended_temperature": "15°C to 22°C",
            "maximum_shelf_life_days": 450
        },
        {
            "ingredient": "Maida",
            "storage": "Pantry",
            "recommended_temperature": "15°C to 22°C",
            "maximum_shelf_life_days": 240
        },
        {
            "ingredient": "Besan",
            "storage": "Pantry",
            "recommended_temperature": "15°C to 22°C",
            "maximum_shelf_life_days": 240
        },
        {
            "ingredient": "Soft Drinks",
            "storage": "Pantry",
            "recommended_temperature": "15°C to 22°C",
            "maximum_shelf_life_days": 180
        },
        {
            "ingredient": "Ice Cream",
            "storage": "Frozen",
            "recommended_temperature": "-18°C or below",
            "maximum_shelf_life_days": 90
        },
        {
            "ingredient": "Measuring Cup",
            "storage": "Pantry",
            "recommended_temperature": "15°C to 22°C",
            "maximum_shelf_life_days": 730
        },
        {
            "ingredient": "Chef Knife",
            "storage": "Pantry",
            "recommended_temperature": "15°C to 22°C",
            "maximum_shelf_life_days": 730
        }
    ]

    added_safety = 0
    for saf in new_safety:
        if saf["ingredient"].lower().strip() not in existing_safety:
            safety.append(saf)
            added_safety += 1
            
    save_json("safety.json", safety)
    logger.info(f"Added {added_safety} new safety records.")

    # ==========================================
    # 4. Enrich pairing.json
    # ==========================================
    pairing = load_json("pairing.json")
    existing_pairing = {item["ingredient"].lower().strip() for item in pairing}
    
    new_pairing = [
        {
            "ingredient": "Paneer",
            "pairs": ["Butter", "Tomato", "Spinach", "Green Peas", "Tofu (Dairy-free substitute)"]
        },
        {
            "ingredient": "Tomato",
            "pairs": ["Garlic", "Onion", "Basil", "Coriander", "Curry Leaves"]
        },
        {
            "ingredient": "Chicken",
            "pairs": ["Black Pepper", "Garlic", "Lemon", "Ghee", "Curry Leaves"]
        },
        {
            "ingredient": "Ghee",
            "pairs": ["Rice", "Dal", "Biryani", "Ragi Sangati", "Butter (Alternative substitute)"]
        },
        {
            "ingredient": "Coriander",
            "pairs": ["Lemon juice", "Mint", "Green Chilli", "Ginger"]
        },
        {
            "ingredient": "Curry Leaves",
            "pairs": ["Mustard Seeds", "Tamarind", "Coconut Oil", "Asafoetida"]
        },
        {
            "ingredient": "Tamarind",
            "pairs": ["Fish", "Rasam", "Jaggery", "Gongura Leaves"]
        },
        {
            "ingredient": "Coconut",
            "pairs": ["Rice", "Curry Leaves", "Tamarind", "Jaggery", "Coconut Milk"]
        },
        {
            "ingredient": "Rice",
            "pairs": ["Sambar", "Rasam", "Dal", "Biryani Spices", "Rava (Alternative substitute)"]
        }
    ]

    added_pairing = 0
    for pair in new_pairing:
        if pair["ingredient"].lower().strip() not in existing_pairing:
            pairing.append(pair)
            added_pairing += 1
            
    save_json("pairing.json", pairing)
    logger.info(f"Added {added_pairing} new pairing records.")

    # ==========================================
    # 5. Enrich seasonal.json
    # ==========================================
    seasonal = load_json("seasonal.json")
    
    # Let's add specific seasonal tips at the end
    seasonal.append({
        "season": "Summer",
        "week_number": 20,
        "recommended_categories": ["Drinks", "Salads"],
        "seasonal_ingredients": ["Mango", "Lemon", "Sugandha Drink"],
        "pricing_trend": "High availability, lower wholesale prices for lemons and mangoes.",
        "special_menu_tip": "Feature traditional summer coolers like Bael Ka Sharbat and Sugandha Drink on today's specials."
    })
    seasonal.append({
        "season": "Autumn",
        "week_number": 32,
        "recommended_categories": ["Soups", "Fritters"],
        "seasonal_ingredients": ["Besan", "Ginger", "Pepper"],
        "pricing_trend": "High demand for warm comfort foods; stable prices for dry pantry staples.",
        "special_menu_tip": "Feature piping hot tomato rasam and crispy besan pakoras during rainy shifts."
    })
    seasonal.append({
        "season": "Winter",
        "week_number": 48,
        "recommended_categories": ["Main Course", "Deserts"],
        "seasonal_ingredients": ["Ghee", "Ragi", "Jaggery"],
        "pricing_trend": "High wholesale rates for organic jaggery; stable rates for millets.",
        "special_menu_tip": "Feature warm Ragi Sangati with Natu Kodi Pulusu to attract dinner guests."
    })
    
    save_json("seasonal.json", seasonal)
    logger.info("Added 3 seasonal records.")

    # ==========================================
    # 6. Enrich suppliers.json
    # ==========================================
    suppliers = load_json("suppliers.json")
    
    new_suppliers = [
        {
            "supplier_id": "SUP9001",
            "supplier_name": "Fresh Farms Vegetables",
            "ingredient_category": "Produce",
            "supported_ingredients": ["Tomato", "Onion", "Coriander"],
            "delivery_time_hours": 24,
            "city": "Vijayawada",
            "contact_email": "orders@freshfarms.example.com",
            "rating": 4.8
        },
        {
            "supplier_id": "SUP9002",
            "supplier_name": "Dairy Craft Distributors",
            "ingredient_category": "Dairy",
            "supported_ingredients": ["Paneer", "Butter", "Milk", "Cream", "Ghee"],
            "delivery_time_hours": 24,
            "city": "Hyderabad",
            "contact_email": "supply@dairycraft.example.com",
            "rating": 4.9
        },
        {
            "supplier_id": "SUP9003",
            "supplier_name": "Sri Lakshmi Grain Traders",
            "ingredient_category": "Pantry",
            "supported_ingredients": ["Rice", "Maida", "Besan", "Tamarind"],
            "delivery_time_hours": 48,
            "city": "Nellore",
            "contact_email": "sales@srilakshmigrains.example.com",
            "rating": 4.7
        }
    ]

    added_suppliers = 0
    for sup in new_suppliers:
        # Check combination of supplier name to avoid duplicates
        dup = False
        for s in suppliers:
            s_id = s.get("supplier_id")
            if s_id and s_id.lower() == sup["supplier_id"].lower():
                dup = True
                break
        if not dup:
            suppliers.append(sup)
            added_suppliers += 1
            
    save_json("suppliers.json", suppliers)
    logger.info(f"Added {added_suppliers} new supplier records.")

    # Deduplicate files immediately to fix any existing duplicates and missing keys
    logger.info("Starting database deduplication...")
    deduplicate_all()
    logger.info("Restaurant Knowledge Base Enrichment Completed Successfully!")

def deduplicate_all():
    # 1. Deduplicate recipes.json
    recipes = load_json("recipes.json")
    seen_recipe_ids, seen_recipe_names = set(), set()
    cleaned_recipes = []
    recipe_names = set()
    for item in recipes:
        r_id = item.get("recipe_id", "").strip()
        r_name = item.get("recipe_name", "").strip()
        r_name_lower = r_name.lower().strip()
        if r_id and r_name and r_id not in seen_recipe_ids and r_name_lower not in seen_recipe_names:
            seen_recipe_ids.add(r_id)
            seen_recipe_names.add(r_name_lower)
            cleaned_recipes.append(item)
            recipe_names.add(r_name)
    save_json("recipes.json", cleaned_recipes)

    # 2. Deduplicate ingredients.json
    ingredients = load_json("ingredients.json")
    seen_ids, seen_names = set(), set()
    cleaned_ingredients = []
    ingredient_names = set()
    for item in ingredients:
        ing_id = item.get("ingredient_id", "").strip()
        ing_name = item.get("ingredient_name", "").strip()
        ing_name_lower = ing_name.lower().strip()
        if ing_id and ing_name and ing_id not in seen_ids and ing_name_lower not in seen_names:
            seen_ids.add(ing_id)
            seen_names.add(ing_name_lower)
            cleaned_ingredients.append(item)
            ingredient_names.add(ing_name)

    # Cross-reference with recipes.json and auto-append missing ingredients to ingredients.json
    max_numeric_id = 50000
    for ing_id in seen_ids:
        if ing_id.startswith("ING"):
            try:
                num = int(ing_id[3:])
                if num >= max_numeric_id:
                    max_numeric_id = num + 1
            except ValueError:
                pass
    missing_id_counter = max_numeric_id
    for recipe in cleaned_recipes:
        r_ings = recipe.get("ingredients")
        if r_ings and isinstance(r_ings, list):
            for ing in r_ings:
                if ing and ing not in ingredient_names:
                    ing_id = f"ING{missing_id_counter}"
                    missing_id_counter += 1
                    new_ing = {
                        "ingredient_id": ing_id,
                        "ingredient_name": ing,
                        "category": "Pantry",
                        "unit": "kg",
                        "average_shelf_life_days": 30,
                        "storage_type": "Pantry",
                        "minimum_quantity_alert": 5.0,
                        "common_usage": "Auto-generated pantry base ingredient for recipe cross-validation compatibility."
                    }
                    cleaned_ingredients.append(new_ing)
                    ingredient_names.add(ing)
                    
    save_json("ingredients.json", cleaned_ingredients)

    # 3. Clean and filter safety.json
    safety = load_json("safety.json")
    seen_safety = set()
    cleaned_safety = []
    for item in safety:
        ing = item.get("ingredient", "").strip()
        ing_lower = ing.lower()
        if ing and ing in ingredient_names and ing_lower not in seen_safety:
            seen_safety.add(ing_lower)
            cleaned_safety.append(item)
    save_json("safety.json", cleaned_safety)

    # 4. Clean and filter pairing.json
    pairing = load_json("pairing.json")
    seen_pairing = set()
    cleaned_pairing = []
    for item in pairing:
        ing = item.get("ingredient", "").strip()
        ing_lower = ing.lower()
        if ing and ing in ingredient_names and ing_lower not in seen_pairing:
            pairs = item.get("pairs", [])
            valid_pairs = [p for p in pairs if p in ingredient_names]
            if valid_pairs:
                item["pairs"] = valid_pairs
                seen_pairing.add(ing_lower)
                cleaned_pairing.append(item)
    save_json("pairing.json", cleaned_pairing)

    # 5. Clean and filter suppliers.json
    suppliers = load_json("suppliers.json")
    seen_suppliers = set()
    cleaned_suppliers = []
    for item in suppliers:
        s_id = item.get("supplier_id", "").strip().lower()
        if s_id and s_id not in seen_suppliers:
            supp_ings = item.get("supported_ingredients", [])
            valid_ings = [i for i in supp_ings if i in ingredient_names]
            if valid_ings:
                item["supported_ingredients"] = valid_ings
                seen_suppliers.add(s_id)
                cleaned_suppliers.append(item)
    save_json("suppliers.json", cleaned_suppliers)

    # Clean and filter seasonal.json
    seasonal = load_json("seasonal.json")
    seen_seasonal = set()
    cleaned_seasonal = []
    for item in seasonal:
        season = item.get("season", "").strip()
        if season.lower() == "monsoon":
            season = "Autumn"
            item["season"] = season
        week = item.get("week_number")
        if season and week is not None:
            key = (season.lower(), int(week))
            if key not in seen_seasonal:
                seen_seasonal.add(key)
                cleaned_seasonal.append(item)
    save_json("seasonal.json", cleaned_seasonal)

    # 6. Clean and filter chef_notes.json
    chef_notes = load_json("chef_notes.json")
    seen_notes = set()
    cleaned_notes = []
    for item in chef_notes:
        recipe = item.get("recipe", "").strip()
        tip = item.get("tip", "").strip()
        if recipe and tip and recipe in recipe_names:
            key = (recipe.lower(), tip.lower())
            if key not in seen_notes:
                seen_notes.add(key)
                cleaned_notes.append(item)
    save_json("chef_notes.json", cleaned_notes)

if __name__ == "__main__":
    enrich()
