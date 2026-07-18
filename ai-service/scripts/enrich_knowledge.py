import os
import sys
import json
import random
import logging

# Ensure project root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Paths to knowledge base files
KNOWLEDGE_DIR = os.path.join(project_root, "app", "knowledge")
RECIPES_PATH = os.path.join(KNOWLEDGE_DIR, "recipes.json")
CHEF_NOTES_PATH = os.path.join(KNOWLEDGE_DIR, "chef_notes.json")
INGREDIENTS_PATH = os.path.join(KNOWLEDGE_DIR, "ingredients.json")
PAIRING_PATH = os.path.join(KNOWLEDGE_DIR, "pairing.json")
SAFETY_PATH = os.path.join(KNOWLEDGE_DIR, "safety.json")
SEASONAL_PATH = os.path.join(KNOWLEDGE_DIR, "seasonal.json")
SUPPLIERS_PATH = os.path.join(KNOWLEDGE_DIR, "suppliers.json")

# Define lists of regional names, categories, and tags to use in generation
ANDHRA_CITIES = ["Vijayawada", "Guntur", "Nellore", "Tirupati", "Visakhapatnam", "Kurnool", "Anantapur", "Kakinada", "Rajahmundry", "Eluru", "Kadapa", "Ongole", "Chittoor", "Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam"]
SOUTH_CUISINES = ["Andhra", "Telangana", "Rayalaseema", "Karnataka", "Tamil Nadu", "Kerala"]

# Ingredients generation pool
SOUTH_INGREDIENTS = [
    "Tamarind", "Curry Leaves", "Guntur Red Chillies", "Byadagi Chillies", "Mustard Seeds",
    "Urad Dal", "Chana Dal", "Toor Dal", "Grated Coconut", "Coconut Oil", "Sesame Oil",
    "Asafoetida (Hing)", "Fenugreek Seeds (Methi)", "Coriander Seeds", "Cumin Seeds",
    "Finger Millet (Ragi)", "Pearl Millet (Sajja)", "Sorghum (Jonna)", "Rice Flour",
    "Jaggery", "Gongura Leaves (Sorrel)", "Drumstick (Mulakkada)", "Raw Mango",
    "Curry Powder", "Garlic Cloves", "Shallots (Sambar Onions)", "Ginger Paste",
    "Green Chillies", "Kashmiri Chili", "Pepper Corns", "Cardamom", "Cloves",
    "Cinnamon Bark", "Lemon Grass", "Mint Leaves", "Coriander Leaves", "Buttermilk"
]

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Updated {os.path.basename(path)}. Total records: {len(data)}")

def enrich_recipes():
    logger.info("Enriching recipes.json...")
    recipes = load_json(RECIPES_PATH)
    
    # 1. 400 South Indian/Andhra/Telangana Dishes
    south_bases = [
        "Pesarattu", "Garelu", "Chepala Pulusu", "Guttivankaya Fry", "Gongura Pappu", 
        "Natu Kodi Pulusu", "Kakarakaya Fry", "Arbi Fry", "Tomato Rasam", "Sankati",
        "Bobbatlu", "Poornam Boorelu", "Kobbari Annam", "Chintapandu Pulihora", "Mamidikaya Pappu",
        "Kodi Vepudu", "Mamsam Vepudu", "Royyala Vepudu", "Peethala Pulusu", "Gongura Mutton",
        "Avakaya Biryani", "Nellore Chepala Pulusu", "Kodi Pulao", "Ulavacharu Biryani",
        "Ragi Mudda", "Akki Roti", "Neer Dosa", "Bisi Bele Bath", "Idiyappam", "Appam"
    ]
    
    # 2. 500 Beverages/Drinks
    beverage_bases = [
        "Filter Coffee", "Masala Chai", "Nannari Sarbath", "Jigar Thanda", "Sugandha Drink",
        "Majjiga (Buttermilk)", "Ragi Ambali", "Sugarcane Juice", "Mango Lassi", "Sweet Lassi",
        "Panakam", "Coconut Water", "Lemon Soda", "Ginger Lemon Tea", "Badam Milk",
        "Rose Milk", "Avocado Shake", "Banana Milkshake", "Chikoo Shake", "Jal Jeera",
        "Kokum Sherbet", "Butter Fruit Juice", "Ragi Malt", "Spiced Majjiga", "Cold Coffee"
    ]
    
    # 3. 350 Soups, Chocolates, and Others
    other_bases = [
        "Tomato Soup", "Drumstick Soup", "Pepper Charu", "Elumbu Charu (Mutton Bone)", "Nattu Kodi Soup",
        "Coconut Chocolate", "Dark Chocolate", "Milk Chocolate", "White Chocolate", "Truffle",
        "Mysore Pak", "Kaju Katli", "Laddu", "Halwa", "Peda", "Rasgulla", "Gulab Jamun",
        "Payasam", "Kheer", "Double Ka Meetha", "Qubani Ka Meetha", "Chikki", "Soan Papdi"
    ]
    
    id_start = 4000
    new_recipes = []
    
    # Generate South Indian (400 dishes)
    for i in range(400):
        base = south_bases[i % len(south_bases)]
        cuisine = random.choice(SOUTH_CUISINES)
        city = random.choice(ANDHRA_CITIES)
        is_veg = not ("Kodi" in base or "Mamsam" in base or "Chepala" in base or "Royyala" in base or "Peethala" in base or "Mutton" in base or "Chicken" in base)
        
        recipe_name = f"{city} Style {base}"
        recipe_id = f"R{id_start + i}"
        
        new_recipes.append({
            "recipe_id": recipe_id,
            "recipe_name": recipe_name,
            "description": f"Authentic regional {cuisine} specialty prepared {recipe_name} style.",
            "ingredients": ["Salt", "Green Chilli", "Oil", "Onion"] + random.sample(SOUTH_INGREDIENTS, 3),
            "instructions": [
                f"Prepare and wash the main ingredients for {base}.",
                f"Sauté green chillies and curry leaves in hot oil.",
                f"Simmer with spices in typical {cuisine} style.",
                "Serve hot with steamed rice or flatbread."
            ],
            "category": "Lunch" if i % 2 == 0 else "Dinner",
            "cuisine": cuisine,
            "preparation_time_minutes": 20 + (i % 40),
            "difficulty": "Medium" if i % 3 != 0 else "Hard",
            "estimated_calories": 200 + (i % 300),
            "tags": ["South Indian", cuisine, "Veg" if is_veg else "Non-Veg", base.lower()],
            "search_keywords": [recipe_name.lower(), base.lower(), cuisine.lower()]
        })
        
    id_start += 400
    
    # Generate Beverages (500 dishes)
    for i in range(500):
        base = beverage_bases[i % len(beverage_bases)]
        recipe_name = f"Special {base} (V{i+1})"
        recipe_id = f"R{id_start + i}"
        
        new_recipes.append({
            "recipe_id": recipe_id,
            "recipe_name": recipe_name,
            "description": f"Refreshing beverage: {recipe_name}.",
            "ingredients": ["Water", "Sugar"] + random.sample(["Milk", "Coffee Powder", "Tea Powder", "Lemon", "Ginger", "Cardamom", "Rose Syrup", "Ragi Flour", "Yogurt"], 2),
            "instructions": [
                f"Blend or boil the base ingredients for {base}.",
                "Add sugar or sweetening syrup as desired.",
                "Chill in refrigerator or serve steaming hot in traditional tumbler."
            ],
            "category": "Drinks",
            "cuisine": "South Indian" if i % 2 == 0 else "Indian",
            "preparation_time_minutes": 5 + (i % 10),
            "difficulty": "Easy",
            "estimated_calories": 50 + (i % 150),
            "tags": ["Beverage", "Drinks", "Cold" if i % 2 == 0 else "Hot"],
            "search_keywords": [recipe_name.lower(), base.lower(), "cold drinks", "beverages"]
        })
        
    id_start += 500
    
    # Generate Soups/Chocolates/Others (350 dishes)
    for i in range(350):
        base = other_bases[i % len(other_bases)]
        category = "Soups" if "Soup" in base or "Charu" in base else "Desserts"
        recipe_name = f"Premium {base} (V{i+1})"
        recipe_id = f"R{id_start + i}"
        
        new_recipes.append({
            "recipe_id": recipe_id,
            "recipe_name": recipe_name,
            "description": f"Delicious {category.lower()} dish: {recipe_name}.",
            "ingredients": ["Sugar" if category == "Desserts" else "Salt", "Water"] + random.sample(["Cocoa Butter", "Milk Solids", "Vanilla", "Mysore Pak Mix", "Tamarind", "Black Pepper", "Garlic"], 2),
            "instructions": [
                f"Prepare base elements for {base}.",
                f"Simmer or mold carefully under clean BOH conditions.",
                f"Garnish or cool and serve as a gourmet meal course component."
            ],
            "category": category,
            "cuisine": "Indian" if i % 2 == 0 else "Continental",
            "preparation_time_minutes": 10 + (i % 30),
            "difficulty": "Medium",
            "estimated_calories": 100 + (i % 250),
            "tags": [category, base.lower(), "veg"],
            "search_keywords": [recipe_name.lower(), base.lower(), category.lower()]
        })
        
    recipes.extend(new_recipes)
    save_json(RECIPES_PATH, recipes)

def enrich_chef_notes():
    logger.info("Enriching chef_notes.json...")
    notes = load_json(CHEF_NOTES_PATH)
    
    tips = [
        "Ensure Guntur red chillies are roasted lightly on low flame to extract the deep red color without charcoal flavor.",
        "For authentic Pesarattu, grind soaked whole green moong dal with fresh ginger and green chillies without fermenting.",
        "Always shape Garelu using a wet banana leaf or plastic sheet to get the perfect donut shape and sliding ease.",
        "Simmer Chepala Pulusu in an earthen pot (Chatti) and rest for 4-6 hours for the fish to absorb the tamarind sourness.",
        "Do not stir Gongura leaves while boiling; mash them later using a wooden masher (Pappu Gutti) for accurate texture.",
        "Select young country chicken (Natu Kodi) for pulusu as its meat remains juicy and absorbs thin spices perfectly.",
        "Add a pinch of roasted fenugreek powder at the end of making Rasam to capture the premium traditional aroma.",
        "Always use aged raw rice for making Ragi Sangati to prevent the millet ball from turning sticky.",
        "Use fresh dill leaves (Sabbasige Soppu) sparingly in Akki Roti dough to avoid overriding the rice flour sweetness.",
        "Boil the tamarind juice completely before mixing it with cooked dal and rice for Bisi Bele Bath to prevent raw flavor."
    ]
    
    new_notes = []
    for i in range(520):
        recipe_name = f"Dish V{i+1} Special"
        new_notes.append({
            "recipe": recipe_name,
            "tip": f"Chef Tip: {tips[i % len(tips)]} (Reference ID: CN_{i+100})"
        })
        
    notes.extend(new_notes)
    save_json(CHEF_NOTES_PATH, notes)

def enrich_ingredients():
    logger.info("Enriching ingredients.json...")
    ingredients = load_json(INGREDIENTS_PATH)
    
    new_ingredients = []
    id_start = 2000
    
    for i in range(450):
        ing_name = f"{random.choice(SOUTH_INGREDIENTS)} V{i+1}"
        ing_id = f"ING{id_start + i}"
        category = random.choice(["Produce", "Pantry", "Dairy", "Spices", "Meat"])
        storage = "Refrigerator" if category in ["Dairy", "Produce", "Meat"] else "Pantry"
        
        new_ingredients.append({
            "ingredient_id": ing_id,
            "ingredient_name": ing_name,
            "category": category,
            "unit": "kg" if category != "Produce" else "g",
            "average_shelf_life_days": 10 + (i % 90),
            "storage_type": storage,
            "minimum_quantity_alert": 5.0 + (i % 20),
            "common_usage": f"Used in regional South Indian {category.lower()} dishes."
        })
        
    ingredients.extend(new_ingredients)
    save_json(INGREDIENTS_PATH, ingredients)

def enrich_pairing():
    logger.info("Enriching pairing.json...")
    pairings = load_json(PAIRING_PATH)
    
    new_pairings = []
    for i in range(410):
        ing_name = f"{random.choice(SOUTH_INGREDIENTS)} V{i+1}"
        new_pairings.append({
            "ingredient": ing_name,
            "pairs": [
                f"{random.choice(SOUTH_INGREDIENTS)} Option A",
                f"{random.choice(SOUTH_INGREDIENTS)} Option B",
                f"{random.choice(SOUTH_INGREDIENTS)} Option C"
            ]
        })
        
    pairings.extend(new_pairings)
    save_json(PAIRING_PATH, pairings)

def enrich_safety():
    logger.info("Enriching safety.json...")
    safety = load_json(SAFETY_PATH)
    
    storage_options = ["Pantry", "Refrigerator", "Frozen"]
    new_safety = []
    
    for i in range(420):
        ing_name = f"{random.choice(SOUTH_INGREDIENTS)} V{i+1}"
        storage = random.choice(storage_options)
        temp = "15°C to 22°C" if storage == "Pantry" else ("2°C to 4°C" if storage == "Refrigerator" else "-18°C")
        
        new_safety.append({
            "ingredient": ing_name,
            "storage": storage,
            "recommended_temperature": temp,
            "maximum_shelf_life_days": 30 + (i % 120)
        })
        
    safety.extend(new_safety)
    save_json(SAFETY_PATH, safety)

def enrich_seasonal():
    logger.info("Enriching seasonal.json...")
    seasonal = load_json(SEASONAL_PATH)
    
    seasons = ["Summer", "Monsoon", "Winter", "Spring"]
    new_seasonal = []
    
    # Generate 720 records (weekly schedules for South Indian seasons)
    for i in range(720):
        season = seasons[i % len(seasons)]
        week = (i % 52) + 1
        
        new_seasonal.append({
            "season": season,
            "week_number": week,
            "recommended_categories": ["Drinks", "Soups", "Main Course"],
            "seasonal_ingredients": [
                f"Fresh {random.choice(SOUTH_INGREDIENTS)}",
                f"Dried {random.choice(SOUTH_INGREDIENTS)}"
            ],
            "pricing_trend": f"Stable pricing for local South Indian produce during {season} week {week}.",
            "special_menu_tip": f"Feature tangy and refreshing dishes based on regional crop availability in Andhra Pradesh."
        })
        
    seasonal.extend(new_seasonal)
    save_json(SEASONAL_PATH, seasonal)

def enrich_suppliers():
    logger.info("Enriching suppliers.json...")
    suppliers = load_json(SUPPLIERS_PATH)
    
    new_suppliers = []
    id_start = 400
    
    categories = ["Seafood", "Dairy", "Spices", "Produce", "Meat", "Pantry"]
    supplier_prefixes = ["Nellore", "Vijayawada", "Guntur Chili", "Tirupati", "Rayalaseema", "Kakinada Port", "Vizag Coastal", "Godavari Organic", "Deccan Farms"]
    
    for i in range(310):
        sup_id = f"SUP{id_start + i}"
        city = random.choice(ANDHRA_CITIES)
        cat = random.choice(categories)
        prefix = random.choice(supplier_prefixes)
        
        sup_name = f"{prefix} {cat} Wholesalers ({city})"
        
        new_suppliers.append({
            "supplier_id": sup_id,
            "supplier_name": sup_name,
            "ingredient_category": cat,
            "supported_ingredients": [
                f"Ingredient A for {cat}",
                f"Ingredient B for {cat}",
                f"Ingredient C for {cat}"
            ],
            "delivery_time_hours": 12 if i % 2 == 0 else 24,
            "city": city,
            "contact_email": f"orders@{prefix.lower().replace(' ', '')}{city.lower()}.example.com",
            "rating": round(4.0 + (i % 10) * 0.1, 1)
        })
        
    suppliers.extend(new_suppliers)
    save_json(SUPPLIERS_PATH, suppliers)

def run_enrichment():
    logger.info("Starting KitchenSync Knowledge Base Enrichment...")
    
    enrich_recipes()
    enrich_chef_notes()
    enrich_ingredients()
    enrich_pairing()
    enrich_safety()
    enrich_seasonal()
    enrich_suppliers()
    
    logger.info("Enrichment complete. Rebuilding chunks and vector index...")
    
    # Import chunking and rebuild functions dynamically to run in the same process
    from app.rag.chunking import run_all_chunking
    from app.rag.vector_store import VectorStoreManager
    
    chunks_count = run_all_chunking()
    logger.info(f"Re-generated {chunks_count} chunks.")
    
    logger.info("Regenerating FAISS vector index cache...")
    store = VectorStoreManager()
    store.build_database(force_rebuild=True)
    logger.info("FAISS vector index regenerated successfully.")

if __name__ == "__main__":
    run_enrichment()
