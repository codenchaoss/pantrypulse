import zipfile
import csv
import io
import os
import ast
import json
import re

# Resolve the absolute path to the "ai-service" folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_path(*paths):
    return os.path.join(BASE_DIR, *paths)

def create_dirs():
    os.makedirs(get_path("datasets", "processed"), exist_ok=True)
    os.makedirs(get_path("datasets", "converted_json"), exist_ok=True)
    os.makedirs(get_path("app", "knowledge"), exist_ok=True)

def find_zip_file(filename):
    # Check parent workspace directory and datasets/raw
    paths = [
        os.path.join(os.path.dirname(BASE_DIR), filename),
        get_path("datasets", "raw", filename)
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def find_csv_in_zip(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as z:
        csv_files = [f for f in z.namelist() if f.endswith('.csv') and not f.startswith('__MACOSX')]
        for f in csv_files:
            if "recipes" in f.lower() or "indian" in f.lower():
                return f
        if csv_files:
            return csv_files[0]
    return None

def clean_string_list(val):
    if not val:
        return []
    val = val.strip()
    if val.startswith('[') and val.endswith(']'):
        try:
            parsed = ast.literal_eval(val)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if item]
        except Exception:
            pass
    items = re.split(r'[,;\n]', val)
    cleaned = []
    for item in items:
        item = re.sub(r'^[-\s\*\d\.]+', '', item).strip()
        item = item.strip("'\" \t")
        if item:
            cleaned.append(item)
    return cleaned

def clean_instructions(val):
    if not val:
        return []
    val = val.strip()
    if val.startswith('[') and val.endswith(']'):
        try:
            parsed = ast.literal_eval(val)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if item]
        except Exception:
            pass
    steps = re.split(r'(?:\r?\n)+|(?<=\w\.)\s+(?=\d+\.|\*|[A-Z])', val)
    cleaned = []
    for step in steps:
        step = re.sub(r'^\d+[\.\)]\s*', '', step).strip()
        step = step.strip("'\" \t*")
        if step and len(step) > 3:
            cleaned.append(step)
    return cleaned

def infer_difficulty(prep_time, num_steps):
    if prep_time < 20 or num_steps < 5:
        return "Easy"
    elif prep_time < 50 or num_steps < 12:
        return "Medium"
    else:
        return "Hard"

def infer_category(tags_list, name=""):
    tags_lower = [t.lower() for t in tags_list]
    name_lower = name.lower()
    
    if any(k in tags_lower for k in ["desserts", "sweet", "baking", "cake", "cookie"]) or "dessert" in name_lower:
        return "Desserts"
    if any(k in tags_lower for k in ["breakfast", "brunch", "morning"]) or "breakfast" in name_lower:
        return "Breakfast"
    if any(k in tags_lower for k in ["beverages", "drinks", "cocktails", "smoothies"]) or "drink" in name_lower or "juice" in name_lower:
        return "Beverages"
    if any(k in tags_lower for k in ["salads", "salad"]) or "salad" in name_lower:
        return "Salads"
    if any(k in tags_lower for k in ["soups", "soup", "stew"]) or "soup" in name_lower or "stew" in name_lower:
        return "Soups"
    if any(k in tags_lower for k in ["appetizers", "starter", "sides", "snacks"]) or "appetizer" in name_lower:
        return "Appetizers"
    
    return "Main Course"

def infer_cuisine(tags_list):
    cuisine_map = {
        "italian": "Italian",
        "mexican": "Mexican",
        "chinese": "Chinese",
        "japanese": "Japanese",
        "french": "French",
        "thai": "Thai",
        "mediterranean": "Mediterranean",
        "greek": "Greek",
        "indian": "Indian",
        "spanish": "Spanish",
        "american": "American"
    }
    for tag in tags_list:
        tag_lower = tag.lower()
        if tag_lower in cuisine_map:
            return cuisine_map[tag_lower]
    return "International"

def build_search_keywords(name, category, cuisine, tags):
    words = re.findall(r'\b\w{3,}\b', name.lower())
    words.append(category.lower())
    words.append(cuisine.lower())
    for tag in tags[:5]:
        words.append(tag.lower())
    return list(set(words))

def parse_r_vector(val):
    if not val:
        return []
    val = val.strip()
    val = val.replace('\n', ' ')
    if val.startswith('c(') and val.endswith(')'):
        content = val[2:-1]
        items = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', content)
        return [item.strip() for item in items if item]
    return clean_string_list(val)

def parse_iso_duration(val):
    if not val:
        return 0
    val = val.upper().strip()
    if not val.startswith('PT'):
        return 0
    
    hours = 0
    minutes = 0
    
    match_h = re.search(r'(\d+)H', val)
    match_m = re.search(r'(\d+)M', val)
    
    if match_h:
        hours = int(match_h.group(1))
    if match_m:
        minutes = int(match_m.group(1))
        
    return hours * 60 + minutes

def process_food_com(zip_path, target_count=300):
    csv_file = find_csv_in_zip(zip_path)
    if not csv_file:
        print(f"No CSV file found in {zip_path}")
        return []
    
    print(f"Reading from Food.com: {csv_file}")
    recipes = []
    seen_names = set()
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        with z.open(csv_file) as f:
            f_text = io.TextIOWrapper(f, encoding='utf-8', errors='ignore')
            reader = csv.DictReader(f_text)
            
            count = 0
            for row in reader:
                name = row.get('Name', '').strip()
                if not name or name.lower() in seen_names:
                    continue
                
                desc = row.get('Description', '').strip()
                ingredients = parse_r_vector(row.get('RecipeIngredientParts', ''))
                instructions = parse_r_vector(row.get('RecipeInstructions', ''))
                
                if len(ingredients) < 3 or len(instructions) < 2 or not desc:
                    continue
                
                prep_min = parse_iso_duration(row.get('PrepTime', ''))
                cook_min = parse_iso_duration(row.get('CookTime', ''))
                total_min = prep_min + cook_min
                if total_min <= 0:
                    total_min = 30
                
                calories = 350
                try:
                    cal_val = row.get('Calories', '')
                    if cal_val:
                        calories = int(float(cal_val))
                except:
                    pass
                
                tags = parse_r_vector(row.get('Keywords', ''))
                category = row.get('RecipeCategory', '').strip()
                if not category:
                    category = infer_category(tags, name)
                
                cuisine = infer_cuisine(tags)
                difficulty = infer_difficulty(total_min, len(instructions))
                
                recipe_name = name.title()
                seen_names.add(name.lower())
                
                desc = re.sub(r'\s+', ' ', desc).strip()
                
                recipe = {
                    "recipe_id": f"R{1000 + count:04d}",
                    "recipe_name": recipe_name,
                    "description": desc,
                    "ingredients": ingredients,
                    "instructions": instructions,
                    "category": category,
                    "cuisine": cuisine,
                    "preparation_time_minutes": total_min,
                    "difficulty": difficulty,
                    "estimated_calories": calories,
                    "tags": tags[:10],
                    "search_keywords": build_search_keywords(recipe_name, category, cuisine, tags[:5])
                }
                
                recipes.append(recipe)
                count += 1
                if count >= target_count:
                    break
                    
    print(f"Loaded {len(recipes)} recipes from Food.com")
    return recipes

def process_indian_food(zip_path, start_id_num=1300, target_count=200):
    csv_file = find_csv_in_zip(zip_path)
    if not csv_file:
        print(f"No CSV file found in {zip_path}")
        return []
    
    print(f"Reading from Indian Food: {csv_file}")
    recipes = []
    seen_names = set()
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        with z.open(csv_file) as f:
            f_text = io.TextIOWrapper(f, encoding='utf-8', errors='ignore')
            reader = csv.DictReader(f_text)
            
            headers = reader.fieldnames
            
            name_col = next((c for c in headers if c.lower() in ['recipename', 'recipe_title', 'name']), None)
            ing_col = next((c for c in headers if c.lower() in ['cleaned-ingredients', 'translatedingredients', 'ingredients', 'cleaned ingredients']), None)
            ins_col = next((c for c in headers if c.lower() in ['translatedinstructions', 'instructions', 'steps']), None)
            time_col = next((c for c in headers if c.lower() in ['totaltimeinmins', 'prep_time', 'cook_time', 'total']), None)
            cuisine_col = next((c for c in headers if c.lower() in ['cuisine']), None)
            course_col = next((c for c in headers if c.lower() in ['course']), None)
            desc_col = next((c for c in headers if c.lower() in ['description']), None)
            
            if not name_col or not ing_col or not ins_col:
                print("[ERROR] Could not identify name, ingredients, or instructions columns in Indian Food CSV.")
                return []
                
            count = 0
            for row in reader:
                name = row.get(name_col, '').strip()
                if not name or name.lower() in seen_names:
                    continue
                
                desc = row.get(desc_col, '').strip() if desc_col else ""
                ingredients = clean_string_list(row.get(ing_col, ''))
                instructions = clean_instructions(row.get(ins_col, ''))
                
                if len(ingredients) < 3 or len(instructions) < 2:
                    continue
                
                time_val = 30
                if time_col:
                    try:
                        time_val = int(row.get(time_col, 30))
                        if time_val <= 0:
                            time_val = 30
                    except:
                        pass
                
                cuisine = "Indian"
                if cuisine_col:
                    c_val = row.get(cuisine_col, '').strip()
                    if c_val:
                        cuisine = c_val.title()
                
                course = "Main Course"
                if course_col:
                    course_val = row.get(course_col, '').strip()
                    if course_val:
                        course = course_val.title()
                        if "Main" in course or "Lunch" in course or "Dinner" in course:
                            course = "Main Course"
                        elif "Appetizer" in course or "Starter" in course:
                            course = "Appetizers"
                        elif "Snack" in course:
                            course = "Appetizers"
                        elif "Dessert" in course or "Sweet" in course:
                            course = "Desserts"
                
                calories = 250 + (len(ingredients) * 20) + (time_val * 2)
                if calories > 800:
                    calories = 550
                
                if not desc:
                    desc = f"A flavorful and authentic {cuisine} recipe for {name.title()} ({course})."
                desc = re.sub(r'\s+', ' ', desc).strip()
                
                tags = [cuisine.lower(), course.lower(), "indian-cuisine", "spicy"]
                difficulty = infer_difficulty(time_val, len(instructions))
                
                recipe_name = name.title()
                seen_names.add(name.lower())
                
                recipe = {
                    "recipe_id": f"R{start_id_num + count:04d}",
                    "recipe_name": recipe_name,
                    "description": desc,
                    "ingredients": ingredients,
                    "instructions": instructions,
                    "category": course,
                    "cuisine": cuisine,
                    "preparation_time_minutes": time_val,
                    "difficulty": difficulty,
                    "estimated_calories": calories,
                    "tags": tags,
                    "search_keywords": build_search_keywords(recipe_name, course, cuisine, tags)
                }
                
                recipes.append(recipe)
                count += 1
                if count >= target_count:
                    break
                    
    print(f"Loaded {len(recipes)} recipes from Indian Food dataset")
    return recipes

def main():
    create_dirs()
    
    food_com_zip = find_zip_file("archive.zip")
    indian_zip = find_zip_file("Indian_food_dt.zip")
    
    if not food_com_zip:
        print("[ERROR] archive.zip (Food.com) not found.")
        return
    if not indian_zip:
        print("[ERROR] Indian_food_dt.zip not found.")
        return
        
    food_recipes = process_food_com(food_com_zip, target_count=300)
    indian_recipes = process_indian_food(indian_zip, start_id_num=1300, target_count=200)
    
    # Write intermediate processed JSONs in ai-service/datasets/processed/
    with open(get_path("datasets", "processed", "food_com_recipes.json"), "w", encoding="utf-8") as f:
        json.dump(food_recipes, f, indent=2, ensure_ascii=False)
        
    with open(get_path("datasets", "processed", "indian_recipes.json"), "w", encoding="utf-8") as f:
        json.dump(indian_recipes, f, indent=2, ensure_ascii=False)
        
    merged_recipes = food_recipes + indian_recipes
    print(f"Total merged recipes: {len(merged_recipes)}")
    
    # Write final recipes.json inside ai-service/app/knowledge/
    output_path = get_path("app", "knowledge", "recipes.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged_recipes, f, indent=2, ensure_ascii=False)
        
    # Write reference inside ai-service/datasets/converted_json/
    with open(get_path("datasets", "converted_json", "recipes.json"), "w", encoding="utf-8") as f:
        json.dump(merged_recipes, f, indent=2, ensure_ascii=False)
        
    print(f"[SUCCESS] Successfully created: {output_path}")

if __name__ == "__main__":
    main()
