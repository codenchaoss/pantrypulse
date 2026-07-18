import os
import json
import logging
from fastapi import APIRouter
from app.schemas.response import ApiResponse

# RAG components
from app.rag.chunking import run_all_chunking
from app.rag.vector_store import VectorStoreManager

router = APIRouter()
logger = logging.getLogger("app.api")

# Resolve paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECIPES_PATH = os.path.join(BASE_DIR, "knowledge", "recipes.json")

def generate_breakfast_recipes(start_id):
    recipes = []
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
        ("French Fries", "Western", "Potatoes, Sea Salt", "Slice potatoes, double deep fry, season with salt.")
    ]
    id_counter = start_id
    count = 0
    while count < 350:
        base_name, cuisine, main_ing, prep_desc = bases[count % len(bases)]
        var = variations[(count // len(bases)) % len(variations)]
        is_veg = count % 4 != 0
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

def get_regional_dishes():
    """
    Returns traditional Andhra, Telangana, and Karnataka specialties for knowledge base enrichment.
    """
    return [
        {
            "recipe_id": "R_REG001",
            "recipe_name": "Ragi Sangati",
            "description": "Traditional wholesome Andhra style Ragi Mudda prepared from finger millet and rice.",
            "ingredients": ["Ragi Flour", "Rice", "Water", "Salt", "Ghee"],
            "instructions": [
                "Boil water in a heavy bottomed vessel and add soaked rice.",
                "Once rice is cooked soft, add ragi flour in the center without stirring.",
                "Let it cook on low heat for 5-7 minutes, then blend thoroughly using a wooden stick.",
                "Shape into balls using wet hands and top with fresh ghee."
            ],
            "category": "Lunch",
            "cuisine": "Andhra",
            "preparation_time_minutes": 25,
            "difficulty": "Medium",
            "estimated_calories": 250,
            "tags": ["Traditional", "Andhra", "Lunch", "Veg", "Healthy"],
            "search_keywords": ["ragi sangati", "ragi sangati mudda", "ragi mudda", "ragisankati", "ragi ball", "sankati", "mudda"]
        },
        {
            "recipe_id": "R_REG002",
            "recipe_name": "Sarvapindi",
            "description": "Telangana traditional savory rice flour pancake with peanuts and chana dal.",
            "ingredients": ["Rice Flour", "Peanuts", "Chana Dal", "Green Chilli", "Sesame Seeds", "Onion", "Curry Leaves"],
            "instructions": [
                "Mix rice flour, soaked chana dal, peanuts, sesame seeds, chopped onions, chillies, and salt.",
                "Knead into a soft dough adding water gradually.",
                "Grease a wide copper or iron pan (sarva), press the dough evenly into a thin layer.",
                "Make small holes, fill with oil, cover and cook on medium flame till golden and crispy."
            ],
            "category": "Snacks",
            "cuisine": "Telangana",
            "preparation_time_minutes": 20,
            "difficulty": "Medium",
            "estimated_calories": 300,
            "tags": ["Traditional", "Telangana", "Snacks", "Veg", "Crispy"],
            "search_keywords": ["sarvapindi", "sarva pindi", "ginna pappa", "telangana snack"]
        },
        {
            "recipe_id": "R_REG003",
            "recipe_name": "Akki Roti",
            "description": "Karnataka style rice flour flatbread with onions, dill leaves, and green chillies.",
            "ingredients": ["Rice Flour", "Dill Leaves", "Onion", "Green Chilli", "Grated Coconut", "Cumin Seeds"],
            "instructions": [
                "Mix rice flour with finely chopped dill leaves, onions, green chillies, grated coconut, and cumin seeds.",
                "Add water and knead to a soft dough.",
                "Pat the dough directly onto a cold greased griddle.",
                "Cook covered on medium flame, drizzle oil, flip and cook till crispy."
            ],
            "category": "Breakfast",
            "cuisine": "Karnataka",
            "preparation_time_minutes": 20,
            "difficulty": "Medium",
            "estimated_calories": 220,
            "tags": ["Breakfast", "Karnataka", "Veg", "Healthy"],
            "search_keywords": ["akki roti", "akki rotti", "rice flatbread", "karnataka breakfast"]
        },
        {
            "recipe_id": "R_REG004",
            "recipe_name": "Bisi Bele Bath",
            "description": "Rich traditional hot lentil rice dish from Karnataka cuisine.",
            "ingredients": ["Rice", "Toor Dal", "Mixed Vegetables", "Bisi Bele Bath Powder", "Tamarind Juice", "Ghee", "Cashews"],
            "instructions": [
                "Pressure cook rice and toor dal till mushy.",
                "Boil mixed vegetables with tamarind juice and bisi bele bath masala powder.",
                "Combine cooked rice, dal, and veggies, simmer together with ghee and water to reach flowing consistency.",
                "Temper with mustard seeds, curry leaves, and roasted cashews."
            ],
            "category": "Lunch",
            "cuisine": "Karnataka",
            "preparation_time_minutes": 35,
            "difficulty": "Medium",
            "estimated_calories": 380,
            "tags": ["Traditional", "Karnataka", "Lunch", "Veg", "Rice"],
            "search_keywords": ["bisi bele bath", "bisi bele bhath", "hot lentil rice", "karnataka thali"]
        },
        {
            "recipe_id": "R_REG005",
            "recipe_name": "Andhra Chicken Curry",
            "description": "Spicy and aromatic traditional Andhra style chicken gravy cooked with special spice mix.",
            "ingredients": ["Chicken", "Garam Masala", "Chilli Powder", "Onion", "Ginger-Garlic Paste", "Coconut Powder", "Curry Leaves"],
            "instructions": [
                "Marinate chicken with turmeric, chilli powder, salt, and ginger-garlic paste for 30 minutes.",
                "Sauté onions, green chillies, and curry leaves in oil.",
                "Add marinated chicken and cook till water evaporates.",
                "Stir in coconut powder and ground spice paste, add water and simmer till gravy thickens."
            ],
            "category": "Lunch",
            "cuisine": "Andhra",
            "preparation_time_minutes": 40,
            "difficulty": "Medium",
            "estimated_calories": 450,
            "tags": ["Lunch", "Dinner", "Andhra", "Non-Veg", "Spicy"],
            "search_keywords": ["andhra chicken curry", "andhra chicken", "spicy chicken curry", "kodi kura", "natu kodi"]
        },
        {
            "recipe_id": "R_REG006",
            "recipe_name": "Gongura Chicken Curry",
            "description": "Spicy chicken curry prepared with tangy sorrel leaves (Gongura) in Andhra style.",
            "ingredients": ["Chicken", "Gongura Leaves (Sorrel)", "Onion", "Green Chilli", "Ginger-Garlic Paste", "Spices"],
            "instructions": [
                "Boil gongura leaves with green chillies, mash into a fine paste and set aside.",
                "Sauté onions and spices, add chicken and cook till tender.",
                "Add the mashed gongura paste to the chicken curry.",
                "Simmer for 10 minutes to allow the chicken to absorb the tangy gongura flavor."
            ],
            "category": "Lunch",
            "cuisine": "Andhra",
            "preparation_time_minutes": 45,
            "difficulty": "Medium",
            "estimated_calories": 420,
            "tags": ["Lunch", "Dinner", "Andhra", "Non-Veg", "Tangy"],
            "search_keywords": ["gongura chicken curry", "gongura chicken", "gongura kodi", "sorrel leaves chicken"]
        },
        {
            "recipe_id": "R_REG007",
            "recipe_name": "Natu Kodi Pulusu",
            "description": "Country chicken (Natu Kodi) curry cooked in a fiery, thin gravy, popular in Rayalaseema.",
            "ingredients": ["Country Chicken", "Andhra Chili Powder", "Poppy Seeds Paste", "Onion", "Ginger-Garlic Paste", "Garam Masala"],
            "instructions": [
                "Clean country chicken and pressure cook with turmeric and salt until tender.",
                "Sauté onions, curry leaves, and tomatoes in a deep pot.",
                "Add ginger-garlic paste and poppy seeds paste, fry until oil separates.",
                "Add chicken, cooked broth, chili powder, and garam masala, simmer on high heat to form pulusu gravy."
            ],
            "category": "Dinner",
            "cuisine": "Andhra",
            "preparation_time_minutes": 50,
            "difficulty": "Hard",
            "estimated_calories": 480,
            "tags": ["Dinner", "Andhra", "Non-Veg", "Rayalaseema", "Fiery"],
            "search_keywords": ["natu kodi pulusu", "nattu kodi pulusu", "country chicken curry", "natu kodi kura"]
        }
    ]

@router.get("/rebuild")
def rebuild_database():
    """
    1. Loads existing recipes from recipes.json
    2. Appends 1,550+ unique Indian dishes (Breakfast, Lunch, Snacks, Dinner)
    3. Appends regional dishes (Andhra, Telangana, Karnataka)
    4. Runs the chunking script pipeline
    5. Regenerates unified FAISS vector embeddings cache
    """
    logger.info("API Rebuild: Starting knowledge base update and FAISS regeneration.")
    
    if os.path.exists(RECIPES_PATH):
        with open(RECIPES_PATH, "r", encoding="utf-8") as f:
            existing_recipes = json.load(f)
    else:
        existing_recipes = []
        
    # Check if we already expanded (avoid duplicate appends if run twice)
    already_expanded = len(existing_recipes) > 500
    
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
            
    if not already_expanded:
        logger.info(f"API Rebuild: Generating new recipes starting from ID: R{start_id}")
        b_list, start_id = generate_breakfast_recipes(start_id)
        l_list, start_id = generate_lunch_recipes(start_id)
        s_list, start_id = generate_snacks_recipes(start_id)
        d_list, start_id = generate_dinner_recipes(start_id)
        
        new_recipes = b_list + l_list + s_list + d_list
        existing_recipes.extend(new_recipes)
        
    # Check for regional dishes append (always append if missing)
    has_regional = any(r.get("recipe_name") == "Ragi Sangati" for r in existing_recipes)
    if not has_regional:
        logger.info("API Rebuild: Injecting regional South Indian specialty dishes...")
        regional_dishes = get_regional_dishes()
        existing_recipes.extend(regional_dishes)
        
    with open(RECIPES_PATH, "w", encoding="utf-8") as f:
        json.dump(existing_recipes, f, indent=2, ensure_ascii=False)
    logger.info(f"API Rebuild: Total recipes in database is now {len(existing_recipes)}.")

    # 2. Trigger chunking pipeline
    logger.info("API Rebuild: Triggering Chunking pipeline...")
    chunks_count = run_all_chunking()
    
    # 3. Trigger FAISS rebuild
    logger.info("API Rebuild: Triggering VectorStore rebuild...")
    store = VectorStoreManager()
    store.build_database(force_rebuild=True)
    
    return {
        "status": "success",
        "recipes_total": len(existing_recipes),
        "chunks_generated": chunks_count,
        "vector_store": "rebuilt"
    }
