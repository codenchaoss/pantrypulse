import json
import os

# Resolve paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECIPES_PATH = os.path.join(BASE_DIR, "app", "knowledge", "recipes.json")

def generate_breakfast_recipes(start_id):
    recipes = []
    
    # Variations & templates
    variations = [
        "Plain", "Masala", "Onion", "Cheese", "Paneer", "Egg", "Ghee", "Rava", "Ragi", "Oats",
        "Mint", "Garlic", "Chilli", "Spinach", "Mushroom", "Butter", "Spicy", "Special", "Classic",
        "Schezwan", "Sweet", "Chocolate", "Honey", "Banana", "Strawberry", "Mango", "Mixed Fruit",
        "Vegetable", "Corn", "Potato", "Tomato", "Capsicum", "Ginger", "Coriander", "Curd", "Coconut",
        "Peanut", "Almond", "Cashew", "Pista", "Raisin", "Dry Fruit", "Double", "Triple", "Mini",
        "Jumbo", "Paper", "Thin", "Crispy", "Soft", "Thick", "Hot", "Sweet & Sour", "Tangy"
    ]
    
    bases = [
        ("Dosa", "South Indian", "Rice, Black Gram", "Grind batter, ferment, spread on hot griddle, drizzle oil/ghee, cook till crispy."),
        ("Idli", "South Indian", "Rice, Urad Dal", "Steam fermented rice-lentil batter in molds for 10-12 minutes."),
        ("Vada", "South Indian", "Urad Dal, Green Chilli", "Shape lentil paste into donuts and deep fry till golden brown."),
        ("Uttapam", "South Indian", "Rice Batter, Onion", "Pour thick batter on griddle, top with onions/chillies, cook both sides."),
        ("Paratha", "North Indian", "Whole Wheat Flour, Butter", "Stuff dough with potato/paneer, roll out, pan-fry with ghee."),
        ("Poha", "North Indian", "Flattened Rice, Mustard Seeds", "Wash flattened rice, sauté onions/potatoes, mix with turmeric."),
        ("Upma", "South Indian", "Semolina (Rava), Curry Leaves", "Dry roast semolina, sauté veggies, boil water, add semolina slowly."),
        ("Puri", "North Indian", "Wheat Flour, Oil", "Roll dough into small circles, deep fry till puffed up."),
        ("Omelette", "Continental", "Eggs, Black Pepper", "Whisk eggs with onions/chillies, pour in hot pan, fold when cooked."),
        ("Sandwich", "Western", "Bread Slices, Butter", "Spread butter/chutney, place cheese/veggies, toast or grill.")
    ]
    
    id_counter = start_id
    
    # Let's generate 400 breakfast recipes
    count = 0
    while count < 400:
        base_name, cuisine, main_ing, prep_desc = bases[count % len(bases)]
        var = variations[(count // len(bases)) % len(variations)]
        
        recipe_name = f"{var} {base_name}"
        recipe_id = f"R{id_counter}"
        id_counter += 1
        
        ingredients = [main_ing] + [var.split(" ")[0]] + ["Salt", "Water", "Oil", "Green Chilli"]
        instructions = [
            f"Prepare the primary base ingredients including {main_ing}.",
            f"Add the {var} flavoring elements and blend/stuff appropriately.",
            prep_desc,
            "Serve hot with chutney, sambar, or butter."
        ]
        
        # Spelling variations & synonyms
        synonyms = [recipe_name.lower()]
        if "rava" in recipe_name.lower():
            synonyms.append(recipe_name.lower().replace("rava", "ravva"))
            synonyms.append(recipe_name.lower().replace("rava", "rawa"))
        if "dosa" in recipe_name.lower():
            synonyms.append(recipe_name.lower().replace("dosa", "dosha"))
            synonyms.append(recipe_name.lower().replace("dosa", "dose"))
            
        recipes.append({
            "recipe_id": recipe_id,
            "recipe_name": recipe_name,
            "description": f"Delicious BOH style {recipe_name} prepared fresh daily.",
            "ingredients": list(set(ingredients)),
            "instructions": instructions,
            "category": "Breakfast",
            "cuisine": cuisine,
            "preparation_time_minutes": 15 + (count % 15),
            "difficulty": "Easy" if (count % 3 == 0) else "Medium",
            "estimated_calories": 150 + (count % 150),
            "tags": ["Breakfast", cuisine, "Veg", var],
            "search_keywords": synonyms + [recipe_name.lower().split(" ")[0], base_name.lower(), "indian breakfast"]
        })
        count += 1
        
    return recipes, id_counter

def generate_lunch_recipes(start_id):
    recipes = []
    variations = [
        "Hyderabadi", "Lucknowi", "Mughlai", "Kashmiri", "Punjabi", "South Indian Style", "Chettinad",
        "Malabar", "Goan", "Bengali", "Szechuan", "Garlic", "Ginger", "Pepper", "Lemon", "Tomato",
        "Coconut", "Butter", "Kadhai", "Handi", "Korma", "Masala", "Tikka", "Keema", "Makhani",
        "Palak", "Methi", "Jeera", "Schezwan", "Manchurian", "Chilli", "Sweet & Sour", "Hunan",
        "Singapore", "Hong Kong", "Tandoori", "Roasted", "Fried", "Spicy", "Mild", "Home Style"
    ]
    
    bases = [
        ("Biryani", "Indian", "Basmati Rice, Spices, Yogurt", "Layer parboiled rice over marinated protein/veggies, cook on dum."),
        ("Pulao", "Indian", "Rice, Green Peas", "Sauté spices and veggies, add soaked rice and water, cook till dry."),
        ("Curry", "Indian", "Onions, Tomatoes, Spices", "Prepare onion-tomato gravy, add spices, cook protein or paneer."),
        ("Fried Rice", "Chinese", "Rice, Soy Sauce, Veggies", "Stir-fry cold cooked rice with veggies, sauce, and spring onions."),
        ("Dal", "Indian", "Lentils, Garlic, Cumin", "Boil lentils, temper with hot oil containing cumin, garlic, and chillies."),
        ("Kootu", "South Indian", "Lentils, Coconut Paste", "Boil mixed vegetables, add lentils and coconut-cumin paste, temper."),
        ("Sambar", "South Indian", "Toor Dal, Tamarind", "Boil dal and veggies, mix tamarind paste and sambar powder, simmer.")
    ]
    
    id_counter = start_id
    count = 0
    while count < 400:
        base_name, cuisine, main_ing, prep_desc = bases[count % len(bases)]
        var = variations[(count // len(bases)) % len(variations)]
        
        # Mix Veg and Non-Veg
        is_veg = count % 2 == 0
        protein = "Paneer" if is_veg else "Chicken"
        if "Dal" in base_name or "Sambar" in base_name or "Kootu" in base_name:
            protein = "Veggies"
            is_veg = True
            
        recipe_name = f"{var} {protein} {base_name}"
        recipe_id = f"R{id_counter}"
        id_counter += 1
        
        ingredients = main_ing.split(", ") + [protein, "Oil", "Onion", "Ginger-Garlic Paste", "Garam Masala"]
        instructions = [
            f"Prep all base ingredients: {', '.join(ingredients[:3])}.",
            f"Sauté onions and ginger-garlic paste till golden brown.",
            prep_desc,
            "Garnish with fresh coriander leaves and serve hot with Naan or Rice."
        ]
        
        synonyms = [recipe_name.lower()]
        if "biryani" in recipe_name.lower():
            synonyms.append(recipe_name.lower().replace("biryani", "biriyani"))
            synonyms.append(recipe_name.lower().replace("biryani", "briyani"))
            
        recipes.append({
            "recipe_id": recipe_id,
            "recipe_name": recipe_name,
            "description": f"Savory BOH style {recipe_name} prepared by the head chef.",
            "ingredients": list(set(ingredients)),
            "instructions": instructions,
            "category": "Lunch",
            "cuisine": cuisine,
            "preparation_time_minutes": 30 + (count % 30),
            "difficulty": "Medium" if (count % 2 == 0) else "Hard",
            "estimated_calories": 400 + (count % 300),
            "tags": ["Lunch", cuisine, "Veg" if is_veg else "Non-Veg", protein],
            "search_keywords": synonyms + [recipe_name.lower().split(" ")[0], base_name.lower(), "indian thali"]
        })
        count += 1
        
    return recipes, id_counter

def generate_snacks_recipes(start_id):
    recipes = []
    variations = [
        "Crispy", "Spicy", "Sweet", "Onion", "Potato", "Cheese", "Paneer", "Garlic", "Mint",
        "Schezwan", "Chilli", "Butter", "Corn", "Vegetable", "Egg", "Chicken", "Bhel", "Dry",
        "Hot", "Tangy", "Baked", "Fried", "Baked & Healthy", "Mini", "Jumbo", "Street Style",
        "Classic", "Cocktail", "Kurkure", "Aloo", "Gobi", "Mushroom", "Baby Corn", "Spring"
    ]
    
    bases = [
        ("Samosa", "Indian", "All Purpose Flour, Potatoes", "Roll pastry dough, stuff with spiced potatoes, shape into triangles, deep fry."),
        ("Pakora", "Indian", "Gram Flour (Besan), Ajwain", "Mix chopped veggies in gram flour batter and deep fry till golden."),
        ("Chaat", "Indian", "Papdi, Curd, Tamarind Chutney", "Assemble crisp papdi, boiled potatoes, yogurt, and sweet/spicy chutneys."),
        ("Cutlet", "Indian", "Mashed Potatoes, Breadcrumbs", "Shape mashed potato-vegetable mixture into patties, coat in breadcrumbs, pan fry."),
        ("Vada Pav", "Indian", "Pav (Bread), Potato Vada", "Place deep-fried potato dumpling inside slit bread bun with dry garlic chutney."),
        ("Spring Roll", "Chinese", "Wrapper Sheets, Cabbage", "Stuff wrappers with sautéed vegetables, roll tightly, deep fry."),
        ("French Fries", "Western", "Potatoes, Sea Salt", "Slice potatoes, soak in water, double deep fry, season with salt.")
    ]
    
    id_counter = start_id
    count = 0
    while count < 350:
        base_name, cuisine, main_ing, prep_desc = bases[count % len(bases)]
        var = variations[(count // len(bases)) % len(variations)]
        
        is_veg = count % 4 != 0  # Mostly Veg
        protein = "Chicken" if not is_veg else "Veg"
        if "Chaat" in base_name or "Vada Pav" in base_name:
            is_veg = True
            protein = "Veg"
            
        recipe_name = f"{var} {protein} {base_name}" if "Veg" not in protein else f"{var} {base_name}"
        recipe_id = f"R{id_counter}"
        id_counter += 1
        
        ingredients = main_ing.split(", ") + ["Salt", "Oil", "Green Chilli"]
        instructions = [
            f"Prepare the primary components: {main_ing}.",
            f"Add {var} spices and mix thoroughly.",
            prep_desc,
            "Serve hot as an evening snack with tea or green chutney."
        ]
        
        synonyms = [recipe_name.lower()]
        recipes.append({
            "recipe_id": recipe_id,
            "recipe_name": recipe_name,
            "description": f"Perfect BOH style evening snack: {recipe_name}.",
            "ingredients": list(set(ingredients)),
            "instructions": instructions,
            "category": "Snacks",
            "cuisine": cuisine,
            "preparation_time_minutes": 15 + (count % 20),
            "difficulty": "Easy" if (count % 2 == 0) else "Medium",
            "estimated_calories": 200 + (count % 150),
            "tags": ["Snacks", cuisine, "Veg" if is_veg else "Non-Veg"],
            "search_keywords": synonyms + [recipe_name.lower().split(" ")[0], base_name.lower(), "evening snacks"]
        })
        count += 1
        
    return recipes, id_counter

def generate_dinner_recipes(start_id):
    recipes = []
    variations = [
        "Tandoori", "Kadhai", "Mughlai", "Afghani", "Peshawari", "Reshmi", "Malai", "Hariyali",
        "Schezwan", "Manchurian", "Ginger", "Garlic", "Chilli", "Butter", "Masala", "Tikka", "Kebab",
        "Seekh", "Korma", "Jalfrezi", "Vindaloo", "Rogan Josh", "Dopiaza", "Saag", "Kofta",
        "Noodles", "Manchow", "Hot & Sour", "Pepper Fry", "Ghee Roast", "Fry", "Grill", "BBQ"
    ]
    
    bases = [
        ("Kebab", "Indian", "Minced Protein, Yogurt", "Mix minced protein/veggies with spices, shape on skewers, grill in tandoor."),
        ("Tikka", "Indian", "Protein Cubes, Mustard Oil", "Marinate cubes in yogurt/spices, grill until charred at edges."),
        ("Noodles", "Chinese", "Boiled Noodles, Cabbage", "Stir-fry noodles with shredded vegetables, soy sauce, and vinegar."),
        ("Soup", "International", "Broth, Corn Starch", "Boil broth with vegetables/protein, thicken with corn starch, season."),
        ("Roti/Naan", "Indian", "Wheat Flour, Yeast", "Knead dough, roll out, stretch, bake in tandoor or pan-sear."),
        ("Pulao", "Indian", "Basmati Rice, Cumin", "Sauté cumin, add soaked rice and broth, cook till tender.")
    ]
    
    id_counter = start_id
    count = 0
    while count < 400:
        base_name, cuisine, main_ing, prep_desc = bases[count % len(bases)]
        var = variations[(count // len(bases)) % len(variations)]
        
        is_veg = count % 2 == 0
        protein = "Paneer" if is_veg else "Chicken"
        if "Roti" in base_name or "Naan" in base_name or "Pulao" in base_name:
            protein = "Garlic"
            is_veg = True
            
        recipe_name = f"{var} {protein} {base_name}"
        recipe_id = f"R{id_counter}"
        id_counter += 1
        
        ingredients = main_ing.split(", ") + [protein, "Oil", "Onion", "Chilli Powder", "Ginger"]
        instructions = [
            f"Gather and prepare all raw ingredients.",
            f"Marinate or sauté with {var} spices and let rest.",
            prep_desc,
            "Serve hot alongside fresh mint chutney and onion rings."
        ]
        
        synonyms = [recipe_name.lower()]
        recipes.append({
            "recipe_id": recipe_id,
            "recipe_name": recipe_name,
            "description": f"Hearty dinner dish: {recipe_name}.",
            "ingredients": list(set(ingredients)),
            "instructions": instructions,
            "category": "Dinner",
            "cuisine": cuisine,
            "preparation_time_minutes": 25 + (count % 25),
            "difficulty": "Medium" if (count % 3 != 0) else "Hard",
            "estimated_calories": 300 + (count % 250),
            "tags": ["Dinner", cuisine, "Veg" if is_veg else "Non-Veg"],
            "search_keywords": synonyms + [recipe_name.lower().split(" ")[0], base_name.lower(), "indian dinner"]
        })
        count += 1
        
    return recipes, id_counter

def main():
    print("==================================================")
    print("Starting Recipes Knowledge Base Expansion...")
    print("==================================================")
    
    # 1. Load existing recipes
    if os.path.exists(RECIPES_PATH):
        with open(RECIPES_PATH, "r", encoding="utf-8") as f:
            existing_recipes = json.load(f)
        print(f"Loaded {len(existing_recipes)} existing recipes.")
    else:
        existing_recipes = []
        print("No existing recipes found. Creating new database.")
        
    # Find next recipe ID
    start_id = 1000
    if existing_recipes:
        ids = []
        for r in existing_recipes:
            try:
                ids.append(int(r["recipe_id"].replace("R", "")))
            except:
                pass
        if ids:
            start_id = max(ids) + 1
            
    print(f"Generating new records starting at ID: R{start_id}")
    
    # 2. Generate categories
    breakfast_list, start_id = generate_breakfast_recipes(start_id)
    lunch_list, start_id = generate_lunch_recipes(start_id)
    snacks_list, start_id = generate_snacks_recipes(start_id)
    dinner_list, start_id = generate_dinner_recipes(start_id)
    
    new_recipes = breakfast_list + lunch_list + snacks_list + dinner_list
    total_expanded = existing_recipes + new_recipes
    
    # 3. Write expanded recipes back to file
    with open(RECIPES_PATH, "w", encoding="utf-8") as f:
        json.dump(total_expanded, f, indent=2, ensure_ascii=False)
        
    print(f"[SUCCESS] Appended {len(new_recipes)} dishes to recipes.json.")
    print(f"New total recipes count: {len(total_expanded)}")
    print("==================================================")

if __name__ == "__main__":
    main()
