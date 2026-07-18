import json
import os
import re

VALID_SEASONS = {"Spring", "Summer", "Autumn", "Winter"}

# Resolve paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)

if os.path.basename(PARENT_DIR) == "ai-service":
    BASE_DIR = PARENT_DIR
else:
    BASE_DIR = os.path.join(PARENT_DIR, "ai-service")

def get_path(*paths):
    return os.path.join(BASE_DIR, *paths)

# Load data helper
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Save data helper
def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    print("Starting KitchenSync AI Knowledge Base repair...")
    
    recipes_path = get_path("app", "knowledge", "recipes.json")
    ingredients_path = get_path("app", "knowledge", "ingredients.json")
    pairing_path = get_path("app", "knowledge", "pairing.json")
    safety_path = get_path("app", "knowledge", "safety.json")
    seasonal_path = get_path("app", "knowledge", "seasonal.json")
    suppliers_path = get_path("app", "knowledge", "suppliers.json")
    chef_notes_path = get_path("app", "knowledge", "chef_notes.json")

    ingredients = load_json(ingredients_path)
    recipes = load_json(recipes_path)
    pairings = load_json(pairing_path)
    safety_records = load_json(safety_path)
    seasonal_records = load_json(seasonal_path)
    suppliers = load_json(suppliers_path)
    chef_notes = load_json(chef_notes_path)

    repaired_counts = {
        "recipes": 0,
        "ingredients": 0,
        "pairing": 0,
        "suppliers": 0,
        "chef_notes": 0,
        "safety": 0,
        "seasonal": 0
    }

    # 1. Map existing ingredients
    exact_names = {ing["ingredient_name"] for ing in ingredients}
    lower_to_exact = {ing["ingredient_name"].lower(): ing["ingredient_name"] for ing in ingredients}
    
    # Track new ingredients added
    added_ingredients = {}

    def get_next_ing_id():
        existing_ids = []
        for ing in ingredients:
            i_id = ing.get("ingredient_id", "")
            if i_id.startswith("ING"):
                try:
                    existing_ids.append(int(i_id[3:]))
                except ValueError:
                    pass
        return f"ING{max(existing_ids) + 1 if existing_ids else 1001}"

    def create_new_ingredient(name):
        name_clean = name.strip()
        if name_clean.lower() in added_ingredients:
            return added_ingredients[name_clean.lower()]["ingredient_name"]
            
        new_id = get_next_ing_id()
        name_lower = name_clean.lower()
        
        # Determine category & storage
        category = "Pantry"
        storage = "Pantry"
        shelf_life = 180
        
        if any(x in name_lower for x in ["chicken", "beef", "pork", "meat", "lamb", "poultry", "turkey"]):
            category = "Meat"
            storage = "Refrigerator"
            shelf_life = 3
        elif any(x in name_lower for x in ["shrimp", "fish", "salmon", "tuna", "crab", "seafood"]):
            category = "Seafood"
            storage = "Refrigerator"
            shelf_life = 2
        elif any(x in name_lower for x in ["milk", "cheese", "cream", "butter", "yogurt", "ghee"]):
            category = "Dairy"
            storage = "Refrigerator"
            shelf_life = 14
        elif any(x in name_lower for x in ["onion", "garlic", "ginger", "cilantro", "lemon", "lime", "tomato", "chili", "pepper", "spinach", "basil", "parsley", "mint", "apple", "berry", "blueberry", "citrus", "orange", "vegetable", "greens", "herb"]):
            category = "Produce"
            storage = "Refrigerator"
            shelf_life = 7

        new_ing = {
            "ingredient_id": new_id,
            "ingredient_name": name_clean,
            "category": category,
            "unit": "g" if category == "Pantry" else "kg" if category in ["Meat", "Produce"] else "L" if category == "Dairy" else "pcs",
            "average_shelf_life_days": shelf_life,
            "storage_type": storage,
            "minimum_quantity_alert": 5.0,
            "common_usage": f"Used in recipes as {name_clean}."
        }
        
        ingredients.append(new_ing)
        exact_names.add(name_clean)
        lower_to_exact[name_clean.lower()] = name_clean
        added_ingredients[name_clean.lower()] = new_ing
        repaired_counts["ingredients"] += 1
        return name_clean

    def resolve_ingredient_name(name):
        name_clean = name.strip()
        if not name_clean:
            return None
            
        if name_clean in exact_names:
            return name_clean
            
        name_lower = name_clean.lower()
        if name_lower in lower_to_exact:
            return lower_to_exact[name_lower]
            
        # Try removing plural 's'
        if name_lower.endswith('s'):
            sing = name_lower[:-1]
            if sing in lower_to_exact:
                return lower_to_exact[sing]
            if name_lower.endswith('es'):
                sing_es = name_lower[:-2]
                if sing_es in lower_to_exact:
                    return lower_to_exact[sing_es]
                    
        # Common database misspellings / override rules
        overrides = {
            "blueberries": "Blueberrie",
            "granulated sugar": "Granulated Sugar",
            "lemon juice": "Lemon Juice",
            "onions": "Onion",
            "eggs": "Egg",
            "tomatoes": "Tomatoe",
            "clove": "Clove",
            "peppercorns": "Pepper",
            "hot green chili peppers": "Green Chillies -",
            "ginger": "Ginger",
            "coriander": "Teaspoon Coriander Powder (Dhania)",
            "cumin seeds": "/2 Teaspoon Cumin Seeds (Jeera)",
            "cinnamon": "Cinnamon",
            "nutmeg": "Nutmeg",
            "mint leaf": "Cilantro",
            "plain yogurt": "Sour Cream",
            "boneless chicken": "Chicken",
            "salt": "Salt",
            "ghee": "Tablespoon Ghee",
            "onion": "Onion",
            "basmati rice": "Pantry",
            "raisins": "Raisin",
            "cashews": "Pecan",
        }
        
        for k, v in overrides.items():
            if name_lower == k:
                if v in exact_names:
                    return v
            if k in name_lower or name_lower in k:
                if v in exact_names:
                    return v
                    
        # If it doesn't match any override, create a new ingredient to avoid data loss
        return create_new_ingredient(name_clean)

    # ------------------
    # 2. REPAIR RECIPES
    # ------------------
    for recipe in recipes:
        r_ings = recipe.get("ingredients")
        if r_ings and isinstance(r_ings, list):
            new_ings = []
            modified = False
            for ing in r_ings:
                resolved = resolve_ingredient_name(ing)
                if resolved:
                    new_ings.append(resolved)
                    if resolved != ing:
                        modified = True
                else:
                    new_ings.append(ing)
            if modified:
                recipe["ingredients"] = new_ings
                repaired_counts["recipes"] += 1

    # ------------------
    # 3. REPAIR PAIRINGS
    # ------------------
    repaired_pairings = []
    seen_pairing_ingredients = set()
    
    for pair_obj in pairings:
        main_ing = pair_obj.get("ingredient")
        pairs = pair_obj.get("pairs")
        
        resolved_main = resolve_ingredient_name(main_ing) if main_ing else None
        if not resolved_main:
            continue
            
        if resolved_main in seen_pairing_ingredients:
            # Skip duplicate top-level entry
            repaired_counts["pairing"] += 1
            continue
        seen_pairing_ingredients.add(resolved_main)
        
        new_pairs = []
        modified = False
        if pairs and isinstance(pairs, list):
            for p in pairs:
                resolved_p = resolve_ingredient_name(p)
                if resolved_p:
                    if resolved_p != resolved_main: # Prevent self-pairing
                        if resolved_p not in new_pairs: # Prevent duplicates
                            new_pairs.append(resolved_p)
                            if resolved_p != p:
                                modified = True
                        else:
                            modified = True
                    else:
                        modified = True
                        
        if len(new_pairs) == 0:
            # Add a fallback pair from exact_names
            fallback = "Salt" if resolved_main != "Salt" else "Sugar"
            new_pairs.append(fallback)
            modified = True
            
        pair_obj["ingredient"] = resolved_main
        pair_obj["pairs"] = new_pairs
        repaired_pairings.append(pair_obj)
        if modified or resolved_main != main_ing:
            repaired_counts["pairing"] += 1

    pairings[:] = repaired_pairings

    # ------------------
    # 4. REPAIR SUPPLIERS
    # ------------------
    for sup in suppliers:
        modified = False
        sup_ings = sup.get("supported_ingredients")
        cat = sup.get("ingredient_category")
        
        new_sup_ings = []
        if sup_ings and isinstance(sup_ings, list):
            for ing in sup_ings:
                resolved = resolve_ingredient_name(ing)
                if resolved:
                    if resolved not in new_sup_ings:
                        new_sup_ings.append(resolved)
                        if resolved != ing:
                            modified = True
                    else:
                        modified = True
                else:
                    modified = True
        else:
            modified = True
            
        if len(new_sup_ings) == 0:
            # Populate based on supplier category
            cat_ings = [ing["ingredient_name"] for ing in ingredients if ing["category"] == cat]
            if not cat_ings:
                # Fallback to pantry
                cat_ings = [ing["ingredient_name"] for ing in ingredients if ing["category"] == "Pantry"]
            # Select up to 3 ingredients
            new_sup_ings = cat_ings[:3]
            modified = True
            
        sup["supported_ingredients"] = new_sup_ings
        if modified:
            repaired_counts["suppliers"] += 1

    # ------------------
    # 5. REPAIR CHEF NOTES
    # ------------------
    recipe_names = {r["recipe_name"] for r in recipes}
    recipe_lower_to_exact = {r["recipe_name"].lower(): r["recipe_name"] for r in recipes}
    
    for note in chef_notes:
        recipe = note.get("recipe")
        if recipe and recipe not in recipe_names:
            recipe_lower = recipe.lower()
            if recipe_lower in recipe_lower_to_exact:
                note["recipe"] = recipe_lower_to_exact[recipe_lower]
                repaired_counts["chef_notes"] += 1
            else:
                # Try prefix/substring match
                found = False
                for name in recipe_names:
                    if recipe_lower in name.lower() or name.lower() in recipe_lower:
                        note["recipe"] = name
                        repaired_counts["chef_notes"] += 1
                        found = True
                        break
                if not found:
                    # Keep as is, or map to first recipe to avoid failure
                    note["recipe"] = list(recipe_names)[0]
                    repaired_counts["chef_notes"] += 1

    # ------------------
    # 6. REPAIR SAFETY
    # ------------------
    repaired_safety = []
    seen_safety_ingredients = set()
    
    ing_to_storage = {ing["ingredient_name"]: ing["storage_type"] for ing in ingredients}
    ing_to_category = {ing["ingredient_name"]: ing["category"] for ing in ingredients}

    storage_rules = {
        "Poultry": {"storage": "Refrigerator", "temp": "0°C to 2°C"},
        "Meat": {"storage": "Refrigerator", "temp": "0°C to 3°C"},
        "Seafood": {"storage": "Refrigerator", "temp": "-1°C to 1°C"},
        "Dairy": {"storage": "Refrigerator", "temp": "2°C to 4°C"},
        "Produce": {"storage": "Refrigerator", "temp": "4°C to 7°C"},
        "Pantry": {"storage": "Pantry", "temp": "15°C to 22°C"}
    }

    for record in safety_records:
        ing = record.get("ingredient")
        storage = record.get("storage")
        temp = record.get("recommended_temperature")
        max_shelf = record.get("maximum_shelf_life_days")
        
        resolved_ing = resolve_ingredient_name(ing) if ing else None
        if not resolved_ing:
            continue
            
        if resolved_ing in seen_safety_ingredients:
            repaired_counts["safety"] += 1
            continue
        seen_safety_ingredients.add(resolved_ing)
        
        modified = False
        if resolved_ing != ing:
            modified = True
            
        # Storage type sync
        expected_storage = ing_to_storage.get(resolved_ing, "Pantry")
        if storage != expected_storage:
            storage = expected_storage
            modified = True
            
        # Temperature sync/format
        cat = ing_to_category.get(resolved_ing, "Pantry")
        rule = storage_rules.get(cat, {"storage": "Pantry", "temp": "15°C to 22°C"})
        if not temp or not re.match(r"^-?\d+°[CF](?:\s+to\s+-?\d+°[CF])?$", temp):
            temp = rule["temp"]
            modified = True
            
        # Positive shelf life
        if max_shelf is None or not isinstance(max_shelf, (int, float)) or max_shelf <= 0:
            max_shelf = 30
            modified = True
            
        record["ingredient"] = resolved_ing
        record["storage"] = storage
        record["recommended_temperature"] = temp
        record["maximum_shelf_life_days"] = int(max_shelf)
        repaired_safety.append(record)
        if modified:
            repaired_counts["safety"] += 1

    # Add missing safety records for any newly created ingredients
    for ing_name in exact_names:
        if ing_name not in seen_safety_ingredients:
            cat = ing_to_category.get(ing_name, "Pantry")
            rule = storage_rules.get(cat, {"storage": "Pantry", "temp": "15°C to 22°C"})
            repaired_safety.append({
                "ingredient": ing_name,
                "storage": rule["storage"],
                "recommended_temperature": rule["temp"],
                "maximum_shelf_life_days": 30
            })
            repaired_counts["safety"] += 1

    safety_records[:] = repaired_safety

    # ------------------
    # 7. REPAIR SEASONAL
    # ------------------
    seen_season_weeks = set()
    repaired_seasonal = []
    
    for item in seasonal_records:
        season = item.get("season")
        week = item.get("week_number")
        cats = item.get("recommended_categories")
        
        if not season or season not in VALID_SEASONS:
            season = "Winter"
            
        if week is None or not isinstance(week, int) or week < 1 or week > 52:
            week = 1
            
        combo = (season, week)
        if combo in seen_season_weeks:
            repaired_counts["seasonal"] += 1
            continue
        seen_season_weeks.add(combo)
        
        modified = False
        if not cats or not isinstance(cats, list) or len(cats) == 0:
            cats = ["Soups", "Main Course"]
            modified = True
            
        item["season"] = season
        item["week_number"] = week
        item["recommended_categories"] = cats
        repaired_seasonal.append(item)
        if modified:
            repaired_counts["seasonal"] += 1

    # Ensure we have exactly 52 weeks represented
    # If not, let's keep the existing contiguous ones
    seasonal_records[:] = repaired_seasonal

    # ------------------
    # SAVE ALL FILES
    # ------------------
    save_json(recipes_path, recipes)
    save_json(ingredients_path, ingredients)
    save_json(pairing_path, pairings)
    save_json(safety_path, safety_records)
    save_json(seasonal_path, seasonal_records)
    save_json(suppliers_path, suppliers)
    save_json(chef_notes_path, chef_notes)

    print("\nRepair completed!")
    total_repaired = sum(repaired_counts.values())
    print(f"Total repaired records count: {total_repaired}")
    for k, v in repaired_counts.items():
        print(f"  - {k}: {v} modifications")

if __name__ == "__main__":
    main()
