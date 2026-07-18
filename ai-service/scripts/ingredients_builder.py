import json
import os
import re
from collections import Counter, defaultdict

# Resolve the absolute path to the "ai-service" folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_path(*paths):
    return os.path.join(BASE_DIR, *paths)

def load_recipes():
    path = get_path("app", "knowledge", "recipes.json")
    if not os.path.exists(path):
        print(f"[ERROR] recipes.json not found at {path}. Run dataset_converter.py first.")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def clean_ingredient_name(name):
    name = name.lower().strip()
    name = re.sub(r'\s+', ' ', name)
    name = re.sub(r'^(fresh|raw|dried|ground|powdered|organic|cold)\s+', '', name)
    name = re.sub(r'\s+(fillets|fillet|breasts|breast|cloves|clove|leaves|leaf|ground|powder|diced|sliced|chopped|minced|halves|halved|cubed)$', '', name)
    
    if name.endswith('s') and not name.endswith('ss'):
        name = name[:-1]
        
    return name.title().strip()

# Comprehensive database of common ingredients for precise manual enrichment
INGREDIENT_DATABASE = {
    # Meat & Poultry
    "Chicken": {"category": "Poultry", "unit": "kg", "shelf_life": 3, "storage": "Refrigerator", "alert": 10.0, "usage": "Grilled entrees, curries, and soups"},
    "Chicken Breast": {"category": "Poultry", "unit": "kg", "shelf_life": 3, "storage": "Refrigerator", "alert": 8.0, "usage": "Seared, baked, or shredded chicken dishes"},
    "Chicken Thigh": {"category": "Poultry", "unit": "kg", "shelf_life": 3, "storage": "Refrigerator", "alert": 8.0, "usage": "Slow cooking, baking, and grilling"},
    "Beef": {"category": "Meat", "unit": "kg", "shelf_life": 4, "storage": "Refrigerator", "alert": 6.0, "usage": "Steaks, stews, and stir-fries"},
    "Pork": {"category": "Meat", "unit": "kg", "shelf_life": 4, "storage": "Refrigerator", "alert": 5.0, "usage": "Roasts, chops, and Asian stir-fries"},
    "Mutton": {"category": "Meat", "unit": "kg", "shelf_life": 4, "storage": "Refrigerator", "alert": 5.0, "usage": "Biryanis, stews, and traditional curries"},
    "Bacon": {"category": "Meat", "unit": "kg", "shelf_life": 14, "storage": "Refrigerator", "alert": 4.0, "usage": "Breakfast, salad toppings, and flavor base"},
    
    # Seafood
    "Salmon": {"category": "Seafood", "unit": "kg", "shelf_life": 2, "storage": "Refrigerator", "alert": 5.0, "usage": "Pan-searing, baking, and smoking"},
    "Fresh Salmon Fillet": {"category": "Seafood", "unit": "kg", "shelf_life": 2, "storage": "Refrigerator", "alert": 5.0, "usage": "Gourmet fish entrees and seafood specials"},
    "Prawn": {"category": "Seafood", "unit": "kg", "shelf_life": 2, "storage": "Refrigerator", "alert": 6.0, "usage": "Garlic prawn appetizers and curries"},
    "Shrimp": {"category": "Seafood", "unit": "kg", "shelf_life": 2, "storage": "Refrigerator", "alert": 6.0, "usage": "Stir-fries, pasta, and shrimp cocktails"},
    "Fish": {"category": "Seafood", "unit": "kg", "shelf_life": 2, "storage": "Refrigerator", "alert": 10.0, "usage": "Fish fry, baking, and fish curries"},
    "Tuna": {"category": "Seafood", "unit": "kg", "shelf_life": 3, "storage": "Refrigerator", "alert": 4.0, "usage": "Salads, sandwiches, and sushi bowls"},

    # Produce
    "Spinach": {"category": "Produce", "unit": "kg", "shelf_life": 4, "storage": "Refrigerator", "alert": 5.0, "usage": "Salads, sauteed sides, and cream sauces"},
    "Avocado": {"category": "Produce", "unit": "pcs", "shelf_life": 4, "storage": "Refrigerator", "alert": 15, "usage": "Salads, guacamole, and sandwich spreads"},
    "Tomato": {"category": "Produce", "unit": "kg", "shelf_life": 7, "storage": "Refrigerator", "alert": 10.0, "usage": "Sauces, salads, and curries"},
    "Cherry Tomato": {"category": "Produce", "unit": "kg", "shelf_life": 7, "storage": "Refrigerator", "alert": 5.0, "usage": "Salads, skewers, and roasting"},
    "Garlic": {"category": "Produce", "unit": "kg", "shelf_life": 45, "storage": "Pantry", "alert": 5.0, "usage": "Essential flavor base for most cuisines"},
    "Garlic Clove": {"category": "Produce", "unit": "pcs", "shelf_life": 45, "storage": "Pantry", "alert": 50, "usage": "Crushed or minced flavor base"},
    "Ginger": {"category": "Produce", "unit": "kg", "shelf_life": 21, "storage": "Refrigerator", "alert": 3.0, "usage": "Asian stir-fries, marinades, and curries"},
    "Onion": {"category": "Produce", "unit": "kg", "shelf_life": 30, "storage": "Pantry", "alert": 15.0, "usage": "Base aromatic for savory dishes"},
    "Lemon": {"category": "Produce", "unit": "pcs", "shelf_life": 14, "storage": "Refrigerator", "alert": 20, "usage": "Garnishes, salad dressing, and juices"},
    "Lemon Juice": {"category": "Produce", "unit": "L", "shelf_life": 14, "storage": "Refrigerator", "alert": 2.0, "usage": "Marinades, salad dressings, and drinks"},
    "Lime": {"category": "Produce", "unit": "pcs", "shelf_life": 14, "storage": "Refrigerator", "alert": 20, "usage": "Mexican food, drinks, and garnishes"},
    "Fresh Basil": {"category": "Produce", "unit": "kg", "shelf_life": 4, "storage": "Refrigerator", "alert": 1.0, "usage": "Caprese salad, pesto, and garnishing"},
    "Basil": {"category": "Produce", "unit": "kg", "shelf_life": 4, "storage": "Refrigerator", "alert": 1.0, "usage": "Seasoning, sauces, and stews"},
    "Fresh Dill": {"category": "Produce", "unit": "kg", "shelf_life": 4, "storage": "Refrigerator", "alert": 1.0, "usage": "Seafood garnishes and creamy sauces"},
    "Potato": {"category": "Produce", "unit": "kg", "shelf_life": 30, "storage": "Pantry", "alert": 20.0, "usage": "Mash, roasting, baking, and curries"},
    "Carrot": {"category": "Produce", "unit": "kg", "shelf_life": 21, "storage": "Refrigerator", "alert": 10.0, "usage": "Soups, stews, salads, and stocks"},
    "Cilantro": {"category": "Produce", "unit": "kg", "shelf_life": 5, "storage": "Refrigerator", "alert": 2.0, "usage": "Garnish for Mexican and Indian dishes"},
    "Coriander": {"category": "Produce", "unit": "kg", "shelf_life": 5, "storage": "Refrigerator", "alert": 2.0, "usage": "Indian curries, garnishing, and salsas"},
    "Bell Pepper": {"category": "Produce", "unit": "kg", "shelf_life": 7, "storage": "Refrigerator", "alert": 5.0, "usage": "Stir-fries, fajitas, and salads"},
    "Mushroom": {"category": "Produce", "unit": "kg", "shelf_life": 6, "storage": "Refrigerator", "alert": 4.0, "usage": "Pizza, creamy pasta, and sides"},

    # Dairy
    "Unsalted Butter": {"category": "Dairy", "unit": "kg", "shelf_life": 30, "storage": "Refrigerator", "alert": 5.0, "usage": "Baking, frying, and making sauces"},
    "Butter": {"category": "Dairy", "unit": "kg", "shelf_life": 30, "storage": "Refrigerator", "alert": 5.0, "usage": "Searing, roasting, and general cooking"},
    "Heavy Cream": {"category": "Dairy", "unit": "L", "shelf_life": 14, "storage": "Refrigerator", "alert": 4.0, "usage": "Soups, pasta sauces, and desserts"},
    "Mozzarella Cheese": {"category": "Dairy", "unit": "kg", "shelf_life": 10, "storage": "Refrigerator", "alert": 5.0, "usage": "Pizzas, salads, and sandwiches"},
    "Parmesan Cheese": {"category": "Dairy", "unit": "kg", "shelf_life": 45, "storage": "Refrigerator", "alert": 3.0, "usage": "Gratings over pasta, risotto, and salads"},
    "Cheese": {"category": "Dairy", "unit": "kg", "shelf_life": 14, "storage": "Refrigerator", "alert": 5.0, "usage": "Melting, sandwiches, and burger toppings"},
    "Milk": {"category": "Dairy", "unit": "L", "shelf_life": 7, "storage": "Refrigerator", "alert": 10.0, "usage": "Baking, white sauces, and breakfast cereals"},
    "Yogurt": {"category": "Dairy", "unit": "kg", "shelf_life": 14, "storage": "Refrigerator", "alert": 6.0, "usage": "Indian marinades, dips, and baking"},
    "Ghee": {"category": "Dairy", "unit": "kg", "shelf_life": 90, "storage": "Pantry", "alert": 3.0, "usage": "Indian cooking, tempering, and sweets"},
    "Egg": {"category": "Dairy", "unit": "pcs", "shelf_life": 21, "storage": "Refrigerator", "alert": 60, "usage": "Baking, breakfasts, and binder"},

    # Pantry & Spices
    "Olive Oil": {"category": "Pantry", "unit": "L", "shelf_life": 365, "storage": "Pantry", "alert": 10.0, "usage": "Salad dressings, sautéing, and finishing"},
    "Vegetable Oil": {"category": "Pantry", "unit": "L", "shelf_life": 365, "storage": "Pantry", "alert": 15.0, "usage": "Frying, baking, and high-heat cooking"},
    "Honey": {"category": "Pantry", "unit": "kg", "shelf_life": 365, "storage": "Pantry", "alert": 2.0, "usage": "Glazes, dressings, and baking sweetness"},
    "Soy Sauce": {"category": "Pantry", "unit": "L", "shelf_life": 180, "storage": "Pantry", "alert": 4.0, "usage": "Asian stir-fries, glazes, and dipping"},
    "Balsamic Vinegar": {"category": "Pantry", "unit": "L", "shelf_life": 365, "storage": "Pantry", "alert": 2.0, "usage": "Salad dressings, glaze reductions"},
    "Flour": {"category": "Pantry", "unit": "kg", "shelf_life": 180, "storage": "Pantry", "alert": 20.0, "usage": "Baking, thickening roux, coating proteins"},
    "Sugar": {"category": "Pantry", "unit": "kg", "shelf_life": 365, "storage": "Pantry", "alert": 15.0, "usage": "Desserts, sauces, balancing savory flavors"},
    "Salt": {"category": "Pantry", "unit": "kg", "shelf_life": 365, "storage": "Pantry", "alert": 10.0, "usage": "Universal seasoning agent"},
    "Black Pepper": {"category": "Pantry", "unit": "kg", "shelf_life": 365, "storage": "Pantry", "alert": 2.0, "usage": "Seasoning steaks, sauces, and soups"},
    "Rice": {"category": "Pantry", "unit": "kg", "shelf_life": 365, "storage": "Pantry", "alert": 25.0, "usage": "Biryani, fried rice, and side dishes"},
    "Pasta": {"category": "Pantry", "unit": "kg", "shelf_life": 365, "storage": "Pantry", "alert": 10.0, "usage": "Italian main courses and pasta salads"},
    "Turmeric": {"category": "Pantry", "unit": "kg", "shelf_life": 180, "storage": "Pantry", "alert": 2.0, "usage": "Aromatic yellow spice for Indian curries"},
    "Chili Powder": {"category": "Pantry", "unit": "kg", "shelf_life": 180, "storage": "Pantry", "alert": 3.0, "usage": "Adding heat and color to curries and meats"},
    "Cumin Seed": {"category": "Pantry", "unit": "kg", "shelf_life": 180, "storage": "Pantry", "alert": 2.0, "usage": "Tempering oils, spice base for Indian cuisine"},
    "Garam Masala": {"category": "Pantry", "unit": "kg", "shelf_life": 180, "storage": "Pantry", "alert": 2.0, "usage": "Finishing spice for Indian curries"}
}

def fallback_enrich(name):
    name_lower = name.lower()
    
    if any(k in name_lower for k in ["chicken", "turkey", "duck"]):
        return {"category": "Poultry", "unit": "kg", "shelf_life": 3, "storage": "Refrigerator", "alert": 5.0, "usage": "Roasting, grilling, and stewing"}
    elif any(k in name_lower for k in ["beef", "pork", "mutton", "lamb", "steak", "meat"]):
        return {"category": "Meat", "unit": "kg", "shelf_life": 4, "storage": "Refrigerator", "alert": 5.0, "usage": "Main meat dishes, roasting, and stews"}
    elif any(k in name_lower for k in ["salmon", "shrimp", "prawn", "fish", "tuna", "crab", "lobster", "seafood"]):
        return {"category": "Seafood", "unit": "kg", "shelf_life": 2, "storage": "Refrigerator", "alert": 4.0, "usage": "Seafood appetizers, pastas, and main dishes"}
    elif any(k in name_lower for k in ["cheese", "milk", "butter", "cream", "yogurt", "ghee", "curd"]):
        return {"category": "Dairy", "unit": "kg" if "cheese" in name_lower or "butter" in name_lower else "L", "shelf_life": 14, "storage": "Refrigerator", "alert": 4.0, "usage": "Sauces, toppings, baking, and desserts"}
    elif any(k in name_lower for k in ["oil", "salt", "sugar", "sauce", "powder", "flour", "rice", "pasta", "honey", "vinegar", "spices", "chili", "turmeric", "pepper", "clove", "cinnamon"]):
        return {"category": "Pantry", "unit": "kg" if "flour" in name_lower or "sugar" in name_lower or "rice" in name_lower else "L" if "oil" in name_lower or "sauce" in name_lower or "vinegar" in name_lower else "g", "shelf_life": 180, "storage": "Pantry", "alert": 5.0, "usage": "Seasoning, cooking base, and shelf-stable staple"}
    else:
        return {"category": "Produce", "unit": "kg", "shelf_life": 6, "storage": "Refrigerator", "alert": 5.0, "usage": "Salad bases, garnishes, and side dishes"}

def main():
    recipes = load_recipes()
    if not recipes:
        return
        
    print(f"Analyzing {len(recipes)} recipes to extract ingredients...")
    
    raw_ingredient_counts = Counter()
    recipe_ingredient_sets = []
    
    for r in recipes:
        ing_list = r.get("ingredients", [])
        cleaned_ings = []
        for ing in ing_list:
            cleaned = clean_ingredient_name(ing)
            if cleaned:
                cleaned_ings.append(cleaned)
        recipe_ingredient_sets.append(set(cleaned_ings))
        raw_ingredient_counts.update(cleaned_ings)
        
    top_ingredients = [item for item, count in raw_ingredient_counts.most_common(135)]
    print(f"Extracted {len(top_ingredients)} unique ingredients based on frequency.")
    
    enriched_ingredients = []
    for idx, ing_name in enumerate(top_ingredients):
        db_data = INGREDIENT_DATABASE.get(ing_name)
        if not db_data:
            db_data = fallback_enrich(ing_name)
            
        enriched_ingredients.append({
            "ingredient_id": f"ING{1001 + idx:04d}",
            "ingredient_name": ing_name,
            "category": db_data["category"],
            "unit": db_data["unit"],
            "average_shelf_life_days": db_data["shelf_life"],
            "storage_type": db_data["storage"],
            "minimum_quantity_alert": db_data["alert"],
            "common_usage": db_data["usage"]
        })
        
    # Write to ai-service/app/knowledge/ingredients.json
    ingredients_output = get_path("app", "knowledge", "ingredients.json")
    with open(ingredients_output, "w", encoding="utf-8") as f:
        json.dump(enriched_ingredients, f, indent=2, ensure_ascii=False)
    print(f"[SUCCESS] Created: {ingredients_output}")
    
    # Infer Pairings using co-occurrence matrix
    co_occurrence = defaultdict(Counter)
    selected_ingredients_set = set(top_ingredients)
    
    for ings_set in recipe_ingredient_sets:
        filtered_ings = ings_set.intersection(selected_ingredients_set)
        for ing1 in filtered_ings:
            for ing2 in filtered_ings:
                if ing1 != ing2:
                    co_occurrence[ing1][ing2] += 1
                    
    pairings = []
    for ing in top_ingredients:
        pairs_counter = co_occurrence[ing]
        top_pairs = [pair for pair, count in pairs_counter.most_common(5)]
        
        if len(top_pairs) < 3:
            db_entry = INGREDIENT_DATABASE.get(ing)
            if db_entry:
                if db_entry["category"] in ["Poultry", "Meat"]:
                    top_pairs.extend(["Garlic", "Butter", "Black Pepper", "Onion"])
                elif db_entry["category"] == "Seafood":
                    top_pairs.extend(["Lemon", "Unsalted Butter", "Fresh Dill", "Garlic"])
                elif db_entry["category"] == "Produce":
                    top_pairs.extend(["Olive Oil", "Salt", "Onion", "Garlic"])
            top_pairs = list(dict.fromkeys([p for p in top_pairs if p != ing]))[:5]
            
        pairings.append({
            "ingredient": ing,
            "pairs": top_pairs
        })
        
    # Write to ai-service/app/knowledge/pairing.json
    pairing_output = get_path("app", "knowledge", "pairing.json")
    with open(pairing_output, "w", encoding="utf-8") as f:
        json.dump(pairings, f, indent=2, ensure_ascii=False)
    print(f"[SUCCESS] Created: {pairing_output}")

if __name__ == "__main__":
    main()
