import json
import os
import re
import sys
from collections import Counter

# Resolve paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_path(*paths):
    return os.path.join(BASE_DIR, *paths)

# Output files
REPORT_JSON_PATH = get_path("validation_report.json")

# Regex for email validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
# Regex for temperature validation (e.g. 15°C to 22°C, 2°C to 4°C, -1°C to 1°C)
TEMP_REGEX = re.compile(r"^-?\d+°[CF](?:\s+to\s+-?\d+°[CF])?$")

VALID_SEASONS = {"Spring", "Summer", "Autumn", "Winter"}
VALID_STORAGE_TYPES = {"Pantry", "Refrigerator", "Freezer"}

def is_empty(val):
    if val is None:
        return True
    if isinstance(val, str):
        return len(val.strip()) == 0
    if isinstance(val, (list, dict, set)):
        return len(val) == 0
    return False

def is_invalid_number(val, allow_zero=False):
    if val is None:
        return True
    if not isinstance(val, (int, float)) or isinstance(val, bool):
        return True
    if allow_zero:
        return val < 0
    return val <= 0

def load_json_file(file_path):
    if not os.path.exists(file_path):
        return None, f"File not found at {file_path}"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON formatting: {str(e)}"
    except Exception as e:
        return None, f"Error reading file: {str(e)}"

def validate():
    failures = []
    
    # Load all files
    recipes_path = get_path("app", "knowledge", "recipes.json")
    ingredients_path = get_path("app", "knowledge", "ingredients.json")
    pairing_path = get_path("app", "knowledge", "pairing.json")
    safety_path = get_path("app", "knowledge", "safety.json")
    seasonal_path = get_path("app", "knowledge", "seasonal.json")
    suppliers_path = get_path("app", "knowledge", "suppliers.json")
    chef_notes_path = get_path("app", "knowledge", "chef_notes.json")

    recipes_data, recipes_err = load_json_file(recipes_path)
    ingredients_data, ingredients_err = load_json_file(ingredients_path)
    pairing_data, pairing_err = load_json_file(pairing_path)
    safety_data, safety_err = load_json_file(safety_path)
    seasonal_data, seasonal_err = load_json_file(seasonal_path)
    suppliers_data, suppliers_err = load_json_file(suppliers_path)
    chef_notes_data, chef_notes_err = load_json_file(chef_notes_path)

    # If any file fails to load/parse
    if recipes_err:
        failures.append({"file": "recipes.json", "record_identifier": "File Load", "error_type": "JSON Format Error", "details": recipes_err, "suggested_correction": "Fix JSON syntax errors."})
    if ingredients_err:
        failures.append({"file": "ingredients.json", "record_identifier": "File Load", "error_type": "JSON Format Error", "details": ingredients_err, "suggested_correction": "Fix JSON syntax errors."})
    if pairing_err:
        failures.append({"file": "pairing.json", "record_identifier": "File Load", "error_type": "JSON Format Error", "details": pairing_err, "suggested_correction": "Fix JSON syntax errors."})
    if safety_err:
        failures.append({"file": "safety.json", "record_identifier": "File Load", "error_type": "JSON Format Error", "details": safety_err, "suggested_correction": "Fix JSON syntax errors."})
    if seasonal_err:
        failures.append({"file": "seasonal.json", "record_identifier": "File Load", "error_type": "JSON Format Error", "details": seasonal_err, "suggested_correction": "Fix JSON syntax errors."})
    if suppliers_err:
        failures.append({"file": "suppliers.json", "record_identifier": "File Load", "error_type": "JSON Format Error", "details": suppliers_err, "suggested_correction": "Fix JSON syntax errors."})
    if chef_notes_err:
        failures.append({"file": "chef_notes.json", "record_identifier": "File Load", "error_type": "JSON Format Error", "details": chef_notes_err, "suggested_correction": "Fix JSON syntax errors."})

    # Summaries
    stats = {
        "recipes": {"total": 0, "valid": 0, "invalid": 0, "duplicates_id": 0, "duplicates_name": 0},
        "ingredients": {"total": 0, "valid": 0, "invalid": 0, "duplicates_id": 0, "duplicates_name": 0},
        "pairing": {"total": 0, "valid": 0, "invalid": 0},
        "suppliers": {"total": 0, "valid": 0, "invalid": 0},
        "chef_notes": {"total": 0, "valid": 0, "invalid": 0},
        "safety": {"total": 0, "valid": 0, "invalid": 0},
        "seasonal": {"total": 0, "valid": 0, "invalid": 0}
    }

    # Reference sets for cross validation
    ingredient_names = set()
    ingredient_id_to_name = {}
    recipe_names = set()
    recipe_id_to_name = {}

    # ------------------
    # 1. INGREDIENTS VALIDATION
    # ------------------
    seen_ing_ids = set()
    seen_ing_names = set()
    
    if ingredients_data is not None:
        stats["ingredients"]["total"] = len(ingredients_data)
        for idx, ing in enumerate(ingredients_data):
            ing_id = ing.get("ingredient_id")
            ing_name = ing.get("ingredient_name")
            category = ing.get("category")
            storage_type = ing.get("storage_type")
            shelf_life = ing.get("average_shelf_life_days")
            common_usage = ing.get("common_usage")
            
            identifier = ing_id or ing_name or f"Index {idx}"
            is_valid = True
            
            # Check ID
            if is_empty(ing_id):
                failures.append({
                    "file": "ingredients.json",
                    "record_identifier": identifier,
                    "error_type": "Empty ingredient ID",
                    "details": "ingredient_id is missing or empty",
                    "suggested_correction": "Provide a unique, non-empty ingredient ID."
                })
                is_valid = False
            elif ing_id in seen_ing_ids:
                failures.append({
                    "file": "ingredients.json",
                    "record_identifier": identifier,
                    "error_type": "Duplicate ingredient ID",
                    "details": f"ingredient_id '{ing_id}' is duplicated",
                    "suggested_correction": "Change to a unique ingredient ID."
                })
                stats["ingredients"]["duplicates_id"] += 1
                is_valid = False
            else:
                seen_ing_ids.add(ing_id)

            # Check Name
            if is_empty(ing_name):
                failures.append({
                    "file": "ingredients.json",
                    "record_identifier": identifier,
                    "error_type": "Empty ingredient name",
                    "details": "ingredient_name is missing or empty",
                    "suggested_correction": "Provide a non-empty ingredient name."
                })
                is_valid = False
            elif ing_name in seen_ing_names:
                failures.append({
                    "file": "ingredients.json",
                    "record_identifier": identifier,
                    "error_type": "Duplicate ingredient name",
                    "details": f"ingredient_name '{ing_name}' is duplicated",
                    "suggested_correction": "Remove or merge duplicate ingredient entries."
                })
                stats["ingredients"]["duplicates_name"] += 1
                is_valid = False
            else:
                seen_ing_names.add(ing_name)
                if ing_id and ing_name:
                    ingredient_id_to_name[ing_id] = ing_name
                    ingredient_names.add(ing_name)

            # Check Category
            if is_empty(category):
                failures.append({
                    "file": "ingredients.json",
                    "record_identifier": identifier,
                    "error_type": "Empty category",
                    "details": "category is missing or empty",
                    "suggested_correction": "Provide a valid category name."
                })
                is_valid = False

            # Check Storage Type
            if is_empty(storage_type):
                failures.append({
                    "file": "ingredients.json",
                    "record_identifier": identifier,
                    "error_type": "Empty storage type",
                    "details": "storage_type is missing or empty",
                    "suggested_correction": "Provide a valid storage type (Pantry, Refrigerator, Freezer)."
                })
                is_valid = False

            # Check Shelf Life
            if shelf_life is None:
                failures.append({
                    "file": "ingredients.json",
                    "record_identifier": identifier,
                    "error_type": "Missing shelf life",
                    "details": "average_shelf_life_days is missing",
                    "suggested_correction": "Provide a non-negative shelf life integer."
                })
                is_valid = False
            elif is_invalid_number(shelf_life, allow_zero=True):
                failures.append({
                    "file": "ingredients.json",
                    "record_identifier": identifier,
                    "error_type": "Negative/Invalid shelf life",
                    "details": f"average_shelf_life_days is {shelf_life}",
                    "suggested_correction": "Set average_shelf_life_days to a non-negative number."
                })
                is_valid = False

            # Check Common Usage
            if is_empty(common_usage):
                failures.append({
                    "file": "ingredients.json",
                    "record_identifier": identifier,
                    "error_type": "Empty common usage",
                    "details": "common_usage is missing or empty",
                    "suggested_correction": "Provide a common usage description string."
                })
                is_valid = False

            if is_valid:
                stats["ingredients"]["valid"] += 1
            else:
                stats["ingredients"]["invalid"] += 1

    # ------------------
    # 2. RECIPES VALIDATION
    # ------------------
    seen_recipe_ids = set()
    seen_recipe_names = set()
    recipe_ingredients_map = {}
    
    if recipes_data is not None:
        stats["recipes"]["total"] = len(recipes_data)
        for idx, recipe in enumerate(recipes_data):
            r_id = recipe.get("recipe_id")
            r_name = recipe.get("recipe_name")
            desc = recipe.get("description")
            ingredients = recipe.get("ingredients")
            instructions = recipe.get("instructions")
            category = recipe.get("category")
            cuisine = recipe.get("cuisine")
            prep_time = recipe.get("preparation_time_minutes")
            calories = recipe.get("estimated_calories")
            tags = recipe.get("tags")
            keywords = recipe.get("search_keywords")
            
            identifier = r_id or r_name or f"Index {idx}"
            is_valid = True
            
            # Check ID
            if is_empty(r_id):
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Empty recipe ID",
                    "details": "recipe_id is missing or empty",
                    "suggested_correction": "Provide a unique, non-empty recipe ID."
                })
                is_valid = False
            elif r_id in seen_recipe_ids:
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Duplicate recipe ID",
                    "details": f"recipe_id '{r_id}' is duplicated",
                    "suggested_correction": "Change to a unique recipe ID."
                })
                stats["recipes"]["duplicates_id"] += 1
                is_valid = False
            else:
                seen_recipe_ids.add(r_id)

            # Check Name
            if is_empty(r_name):
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Empty recipe name",
                    "details": "recipe_name is missing or empty",
                    "suggested_correction": "Provide a non-empty recipe name."
                })
                is_valid = False
            elif r_name in seen_recipe_names:
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Duplicate recipe name",
                    "details": f"recipe_name '{r_name}' is duplicated",
                    "suggested_correction": "Remove or rename the duplicate recipe."
                })
                stats["recipes"]["duplicates_name"] += 1
                is_valid = False
            else:
                seen_recipe_names.add(r_name)
                if r_id and r_name:
                    recipe_id_to_name[r_id] = r_name
                    recipe_names.add(r_name)
                    recipe_ingredients_map[r_name] = ingredients

            # Check Description
            if is_empty(desc):
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Empty description",
                    "details": "description is missing or empty",
                    "suggested_correction": "Provide a recipe description."
                })
                is_valid = False

            # Check Ingredients
            if ingredients is None or not isinstance(ingredients, list):
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Invalid ingredient list",
                    "details": "ingredients must be a non-empty JSON list",
                    "suggested_correction": "Provide a list of ingredient strings."
                })
                is_valid = False
            elif len(ingredients) == 0:
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Empty ingredient list",
                    "details": "ingredients list is empty",
                    "suggested_correction": "Add at least one ingredient to the recipe."
                })
                is_valid = False
            else:
                for idx_ing, ing in enumerate(ingredients):
                    if is_empty(ing):
                        failures.append({
                            "file": "recipes.json",
                            "record_identifier": identifier,
                            "error_type": "Empty ingredient entry",
                            "details": f"Ingredient at index {idx_ing} is empty",
                            "suggested_correction": "Remove empty ingredient names."
                        })
                        is_valid = False

            # Check Instructions
            if instructions is None or not isinstance(instructions, list):
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Invalid instructions",
                    "details": "instructions must be a non-empty JSON list",
                    "suggested_correction": "Provide a list of instruction strings."
                })
                is_valid = False
            elif len(instructions) == 0:
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Empty instructions list",
                    "details": "instructions list is empty",
                    "suggested_correction": "Add at least one cooking step."
                })
                is_valid = False
            else:
                for idx_ins, ins in enumerate(instructions):
                    if is_empty(ins):
                        failures.append({
                            "file": "recipes.json",
                            "record_identifier": identifier,
                            "error_type": "Empty instruction step",
                            "details": f"Instruction step at index {idx_ins} is empty",
                            "suggested_correction": "Remove empty instruction steps."
                        })
                        is_valid = False

            # Check Category
            if is_empty(category):
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Missing category",
                    "details": "category is missing or empty",
                    "suggested_correction": "Specify a food category."
                })
                is_valid = False

            # Check Cuisine
            if is_empty(cuisine):
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Missing cuisine",
                    "details": "cuisine is missing or empty",
                    "suggested_correction": "Specify a valid cuisine (e.g. Indian, Italian)."
                })
                is_valid = False

            # Check Preparation Time
            if prep_time is None:
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Missing preparation time",
                    "details": "preparation_time_minutes is missing",
                    "suggested_correction": "Specify a positive preparation time."
                })
                is_valid = False
            elif is_invalid_number(prep_time):
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Invalid preparation time",
                    "details": f"preparation_time_minutes is {prep_time}",
                    "suggested_correction": "Set preparation_time_minutes to a positive number."
                })
                is_valid = False

            # Check Calories
            if calories is None:
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Missing calories",
                    "details": "estimated_calories is missing",
                    "suggested_correction": "Specify estimated calories."
                })
                is_valid = False
            elif is_invalid_number(calories, allow_zero=True):
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Invalid calories",
                    "details": f"estimated_calories is {calories}",
                    "suggested_correction": "Set estimated_calories to a non-negative number."
                })
                is_valid = False

            # Check Tags
            if tags is None or not isinstance(tags, list):
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Missing tags",
                    "details": "tags list is missing or invalid",
                    "suggested_correction": "Provide a list of tag strings."
                })
                is_valid = False
            elif len(tags) == 0:
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Empty tags list",
                    "details": "tags list is empty",
                    "suggested_correction": "Provide at least one descriptive tag."
                })
                is_valid = False

            # Check Keywords
            if keywords is None or not isinstance(keywords, list):
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Missing search keywords",
                    "details": "search_keywords list is missing or invalid",
                    "suggested_correction": "Provide a list of search keyword strings."
                })
                is_valid = False
            elif len(keywords) == 0:
                failures.append({
                    "file": "recipes.json",
                    "record_identifier": identifier,
                    "error_type": "Empty search keywords list",
                    "details": "search_keywords list is empty",
                    "suggested_correction": "Provide at least one search keyword."
                })
                is_valid = False

            if is_valid:
                stats["recipes"]["valid"] += 1
            else:
                stats["recipes"]["invalid"] += 1

    # ------------------
    # 3. PAIRINGS VALIDATION
    # ------------------
    seen_pair_ingredients = set()
    
    if pairing_data is not None:
        stats["pairing"]["total"] = len(pairing_data)
        for idx, pair_obj in enumerate(pairing_data):
            main_ing = pair_obj.get("ingredient")
            pairs = pair_obj.get("pairs")
            
            identifier = main_ing or f"Index {idx}"
            is_valid = True
            
            # Check duplicate entry for same ingredient
            if main_ing and main_ing in seen_pair_ingredients:
                failures.append({
                    "file": "pairing.json",
                    "record_identifier": identifier,
                    "error_type": "Duplicate pairing entry",
                    "details": f"Multiple pairing records found for ingredient '{main_ing}'",
                    "suggested_correction": "Merge pairing lists under a single entry."
                })
                is_valid = False
            elif main_ing:
                seen_pair_ingredients.add(main_ing)

            # Check Main Ingredient existence in ingredients.json
            if is_empty(main_ing):
                failures.append({
                    "file": "pairing.json",
                    "record_identifier": identifier,
                    "error_type": "Empty ingredient",
                    "details": "ingredient field is missing or empty",
                    "suggested_correction": "Provide a valid ingredient name."
                })
                is_valid = False
            elif ingredients_data is not None and main_ing not in ingredient_names:
                failures.append({
                    "file": "pairing.json",
                    "record_identifier": identifier,
                    "error_type": "Missing reference (Ingredient)",
                    "details": f"Ingredient '{main_ing}' does not exist in ingredients.json",
                    "suggested_correction": f"Add '{main_ing}' to ingredients.json or correct the spelling."
                })
                is_valid = False

            # Check Pairs List
            if pairs is None or not isinstance(pairs, list):
                failures.append({
                    "file": "pairing.json",
                    "record_identifier": identifier,
                    "error_type": "Invalid pairs list",
                    "details": "pairs field must be a JSON list",
                    "suggested_correction": "Provide a list of paired ingredient strings."
                })
                is_valid = False
            elif len(pairs) == 0:
                failures.append({
                    "file": "pairing.json",
                    "record_identifier": identifier,
                    "error_type": "Empty pair list",
                    "details": "pairs list is empty",
                    "suggested_correction": "Add at least one paired ingredient."
                })
                is_valid = False
            else:
                # Check for self pairing
                if main_ing in pairs:
                    failures.append({
                        "file": "pairing.json",
                        "record_identifier": identifier,
                        "error_type": "Self pairing",
                        "details": f"Ingredient '{main_ing}' is paired with itself in pairs list",
                        "suggested_correction": "Remove the self-pairing from the pairs list."
                    })
                    is_valid = False

                # Check for duplicate pairings in the pairs list
                pairs_counter = Counter(pairs)
                for pair, count in pairs_counter.items():
                    if count > 1:
                        failures.append({
                            "file": "pairing.json",
                            "record_identifier": identifier,
                            "error_type": "Duplicate pairing in list",
                            "details": f"Paired ingredient '{pair}' is listed {count} times",
                            "suggested_correction": "Remove duplicate pairings from the list."
                        })
                        is_valid = False

                # Check existence of each pair in ingredients.json
                for p_idx, pair in enumerate(pairs):
                    if is_empty(pair):
                        failures.append({
                            "file": "pairing.json",
                            "record_identifier": identifier,
                            "error_type": "Empty pair entry",
                            "details": f"Pair at index {p_idx} is empty",
                            "suggested_correction": "Remove empty elements from pairs list."
                        })
                        is_valid = False
                    elif ingredients_data is not None and pair not in ingredient_names:
                        failures.append({
                            "file": "pairing.json",
                            "record_identifier": identifier,
                            "error_type": "Missing reference (Pair)",
                            "details": f"Paired ingredient '{pair}' (index {p_idx}) does not exist in ingredients.json",
                            "suggested_correction": f"Add '{pair}' to ingredients.json or correct the spelling."
                        })
                        is_valid = False

            if is_valid:
                stats["pairing"]["valid"] += 1
            else:
                stats["pairing"]["invalid"] += 1

    # ------------------
    # 4. SUPPLIERS VALIDATION
    # ------------------
    seen_supplier_ids = set()
    
    if suppliers_data is not None:
        stats["suppliers"]["total"] = len(suppliers_data)
        for idx, sup in enumerate(suppliers_data):
            sup_id = sup.get("supplier_id")
            sup_name = sup.get("supplier_name")
            email = sup.get("contact_email")
            del_time = sup.get("delivery_time_hours")
            sup_ings = sup.get("supported_ingredients")
            
            identifier = sup_id or sup_name or f"Index {idx}"
            is_valid = True
            
            # Check ID
            if is_empty(sup_id):
                failures.append({
                    "file": "suppliers.json",
                    "record_identifier": identifier,
                    "error_type": "Empty supplier ID",
                    "details": "supplier_id is missing or empty",
                    "suggested_correction": "Provide a unique, non-empty supplier ID."
                })
                is_valid = False
            elif sup_id in seen_supplier_ids:
                failures.append({
                    "file": "suppliers.json",
                    "record_identifier": identifier,
                    "error_type": "Duplicate supplier ID",
                    "details": f"supplier_id '{sup_id}' is duplicated",
                    "suggested_correction": "Change to a unique supplier ID."
                })
                is_valid = False
            else:
                seen_supplier_ids.add(sup_id)

            # Check Name
            if is_empty(sup_name):
                failures.append({
                    "file": "suppliers.json",
                    "record_identifier": identifier,
                    "error_type": "Empty supplier name",
                    "details": "supplier_name is missing or empty",
                    "suggested_correction": "Provide a valid supplier name."
                })
                is_valid = False

            # Check Email format
            if is_empty(email):
                failures.append({
                    "file": "suppliers.json",
                    "record_identifier": identifier,
                    "error_type": "Empty contact email",
                    "details": "contact_email is missing or empty",
                    "suggested_correction": "Provide a valid supplier contact email."
                })
                is_valid = False
            elif not EMAIL_REGEX.match(email):
                failures.append({
                    "file": "suppliers.json",
                    "record_identifier": identifier,
                    "error_type": "Invalid email format",
                    "details": f"contact_email '{email}' is formatted incorrectly",
                    "suggested_correction": "Correct the email address format."
                })
                is_valid = False

            # Check Delivery Time
            if del_time is None:
                failures.append({
                    "file": "suppliers.json",
                    "record_identifier": identifier,
                    "error_type": "Missing delivery time",
                    "details": "delivery_time_hours is missing",
                    "suggested_correction": "Provide a positive delivery time integer."
                })
                is_valid = False
            elif is_invalid_number(del_time):
                failures.append({
                    "file": "suppliers.json",
                    "record_identifier": identifier,
                    "error_type": "Invalid delivery time",
                    "details": f"delivery_time_hours is {del_time}",
                    "suggested_correction": "Set delivery_time_hours to a positive number."
                })
                is_valid = False

            # Check Supported Ingredients list
            if sup_ings is None or not isinstance(sup_ings, list):
                failures.append({
                    "file": "suppliers.json",
                    "record_identifier": identifier,
                    "error_type": "Invalid supported ingredients list",
                    "details": "supported_ingredients must be a JSON list",
                    "suggested_correction": "Provide a list of supported ingredient name strings."
                })
                is_valid = False
            elif len(sup_ings) == 0:
                failures.append({
                    "file": "suppliers.json",
                    "record_identifier": identifier,
                    "error_type": "Empty supported ingredient list",
                    "details": "supported_ingredients list is empty",
                    "suggested_correction": "Add at least one supported ingredient."
                })
                is_valid = False
            else:
                for s_idx, sup_ing in enumerate(sup_ings):
                    if is_empty(sup_ing):
                        failures.append({
                            "file": "suppliers.json",
                            "record_identifier": identifier,
                            "error_type": "Empty supported ingredient entry",
                            "details": f"Supported ingredient at index {s_idx} is empty",
                            "suggested_correction": "Remove empty strings from supported_ingredients."
                        })
                        is_valid = False
                    elif ingredients_data is not None and sup_ing not in ingredient_names:
                        failures.append({
                            "file": "suppliers.json",
                            "record_identifier": identifier,
                            "error_type": "Missing reference (Supplier Ingredient)",
                            "details": f"Supported ingredient '{sup_ing}' (index {s_idx}) does not exist in ingredients.json",
                            "suggested_correction": f"Add '{sup_ing}' to ingredients.json or correct the spelling."
                        })
                        is_valid = False

            if is_valid:
                stats["suppliers"]["valid"] += 1
            else:
                stats["suppliers"]["invalid"] += 1

    # ------------------
    # 5. CHEF NOTES VALIDATION
    # ------------------
    if chef_notes_data is not None:
        stats["chef_notes"]["total"] = len(chef_notes_data)
        for idx, note in enumerate(chef_notes_data):
            recipe = note.get("recipe")
            tip = note.get("tip")
            
            identifier = recipe or f"Index {idx}"
            is_valid = True
            
            # Check empty recipe
            if is_empty(recipe):
                failures.append({
                    "file": "chef_notes.json",
                    "record_identifier": identifier,
                    "error_type": "Empty recipe reference",
                    "details": "recipe field is missing or empty",
                    "suggested_correction": "Provide a recipe name."
                })
                is_valid = False
            elif recipes_data is not None and recipe not in recipe_names:
                failures.append({
                    "file": "chef_notes.json",
                    "record_identifier": identifier,
                    "error_type": "Missing reference (Recipe)",
                    "details": f"Recipe '{recipe}' does not exist in recipes.json",
                    "suggested_correction": f"Add '{recipe}' to recipes.json or correct the spelling."
                })
                is_valid = False

            # Check empty tip
            if is_empty(tip):
                failures.append({
                    "file": "chef_notes.json",
                    "record_identifier": identifier,
                    "error_type": "Empty tip",
                    "details": "tip field is missing or empty",
                    "suggested_correction": "Provide a valid tip string."
                })
                is_valid = False

            if is_valid:
                stats["chef_notes"]["valid"] += 1
            else:
                stats["chef_notes"]["invalid"] += 1

    # ------------------
    # 6. SAFETY VALIDATION
    # ------------------
    ing_to_storage_type = {}
    if ingredients_data is not None:
        for ing in ingredients_data:
            name = ing.get("ingredient_name")
            st = ing.get("storage_type")
            if name and st:
                ing_to_storage_type[name] = st

    if safety_data is not None:
        stats["safety"]["total"] = len(safety_data)
        for idx, record in enumerate(safety_data):
            ing = record.get("ingredient")
            storage = record.get("storage")
            temp = record.get("recommended_temperature")
            max_shelf = record.get("maximum_shelf_life_days")
            
            identifier = ing or f"Index {idx}"
            is_valid = True
            
            # Check ingredient existence
            if is_empty(ing):
                failures.append({
                    "file": "safety.json",
                    "record_identifier": identifier,
                    "error_type": "Empty ingredient reference",
                    "details": "ingredient field is missing or empty",
                    "suggested_correction": "Provide a valid ingredient name."
                })
                is_valid = False
            elif ingredients_data is not None and ing not in ingredient_names:
                failures.append({
                    "file": "safety.json",
                    "record_identifier": identifier,
                    "error_type": "Missing reference (Ingredient)",
                    "details": f"Ingredient '{ing}' does not exist in ingredients.json",
                    "suggested_correction": f"Add '{ing}' to ingredients.json or correct spelling."
                })
                is_valid = False

            # Check storage type
            if is_empty(storage):
                failures.append({
                    "file": "safety.json",
                    "record_identifier": identifier,
                    "error_type": "Empty storage type",
                    "details": "storage is missing or empty",
                    "suggested_correction": "Provide a valid storage type (Pantry, Refrigerator, Freezer)."
                })
                is_valid = False
            elif storage not in VALID_STORAGE_TYPES:
                failures.append({
                    "file": "safety.json",
                    "record_identifier": identifier,
                    "error_type": "Invalid storage type",
                    "details": f"storage type '{storage}' is invalid",
                    "suggested_correction": "Change to Pantry, Refrigerator, or Freezer."
                })
                is_valid = False
            elif ing in ing_to_storage_type and storage != ing_to_storage_type[ing]:
                failures.append({
                    "file": "safety.json",
                    "record_identifier": identifier,
                    "error_type": "Storage type mismatch",
                    "details": f"safety.json storage is '{storage}' but ingredients.json storage_type is '{ing_to_storage_type[ing]}'",
                    "suggested_correction": f"Update safety.json storage to '{ing_to_storage_type[ing]}'."
                })
                is_valid = False

            # Check temperature format
            if is_empty(temp):
                failures.append({
                    "file": "safety.json",
                    "record_identifier": identifier,
                    "error_type": "Empty temperature",
                    "details": "recommended_temperature is missing or empty",
                    "suggested_correction": "Provide temperature constraints (e.g. 2°C to 4°C)."
                })
                is_valid = False
            elif not TEMP_REGEX.match(temp):
                failures.append({
                    "file": "safety.json",
                    "record_identifier": identifier,
                    "error_type": "Invalid temperature format",
                    "details": f"recommended_temperature '{temp}' is formatted incorrectly",
                    "suggested_correction": "Format as '<num>°C to <num>°C' or '<num>°C'."
                })
                is_valid = False

            # Check shelf life
            if max_shelf is None:
                failures.append({
                    "file": "safety.json",
                    "record_identifier": identifier,
                    "error_type": "Missing maximum shelf life",
                    "details": "maximum_shelf_life_days is missing",
                    "suggested_correction": "Provide maximum shelf life days."
                })
                is_valid = False
            elif is_invalid_number(max_shelf):
                failures.append({
                    "file": "safety.json",
                    "record_identifier": identifier,
                    "error_type": "Invalid maximum shelf life",
                    "details": f"maximum_shelf_life_days is {max_shelf}",
                    "suggested_correction": "Set maximum_shelf_life_days to a positive integer."
                })
                is_valid = False

            if is_valid:
                stats["safety"]["valid"] += 1
            else:
                stats["safety"]["invalid"] += 1

    # ------------------
    # 7. SEASONAL VALIDATION
    # ------------------
    seen_season_weeks = set()
    
    if seasonal_data is not None:
        stats["seasonal"]["total"] = len(seasonal_data)
        for idx, item in enumerate(seasonal_data):
            season = item.get("season")
            week = item.get("week_number")
            cats = item.get("recommended_categories")
            s_ings = item.get("seasonal_ingredients")
            
            identifier = f"{season} Week {week}" if season and week else f"Index {idx}"
            is_valid = True
            
            # Check valid season
            if is_empty(season):
                failures.append({
                    "file": "seasonal.json",
                    "record_identifier": identifier,
                    "error_type": "Empty season",
                    "details": "season field is missing or empty",
                    "suggested_correction": "Provide a valid season (Spring, Summer, Autumn, Winter)."
                })
                is_valid = False
            elif season not in VALID_SEASONS:
                failures.append({
                    "file": "seasonal.json",
                    "record_identifier": identifier,
                    "error_type": "Invalid season name",
                    "details": f"season '{season}' is invalid",
                    "suggested_correction": "Set season to one of: Spring, Summer, Autumn, Winter."
                })
                is_valid = False

            # Check duplicate season + week
            if season and week is not None:
                combo = (season, week)
                if combo in seen_season_weeks:
                    failures.append({
                        "file": "seasonal.json",
                        "record_identifier": identifier,
                        "error_type": "Duplicate season and week combination",
                        "details": f"Entry for {season} week {week} is duplicated",
                        "suggested_correction": "Ensure only one entry exists per season and week."
                    })
                    is_valid = False
                else:
                    seen_season_weeks.add(combo)

            # Check recommended categories
            if cats is None or not isinstance(cats, list):
                failures.append({
                    "file": "seasonal.json",
                    "record_identifier": identifier,
                    "error_type": "Invalid recommended categories list",
                    "details": "recommended_categories is missing or invalid",
                    "suggested_correction": "Provide a list of category strings."
                })
                is_valid = False
            elif len(cats) == 0:
                failures.append({
                    "file": "seasonal.json",
                    "record_identifier": identifier,
                    "error_type": "Empty recommended categories list",
                    "details": "recommended_categories is empty",
                    "suggested_correction": "Provide at least one recommended category."
                })
                is_valid = False
            else:
                for c_idx, cat in enumerate(cats):
                    if is_empty(cat):
                        failures.append({
                            "file": "seasonal.json",
                            "record_identifier": identifier,
                            "error_type": "Empty category entry",
                            "details": f"Category at index {c_idx} is empty",
                            "suggested_correction": "Remove empty category strings."
                        })
                        is_valid = False

            # Check seasonal ingredients (optional verification for non-empty)
            if s_ings is not None and isinstance(s_ings, list):
                for s_idx, s_ing in enumerate(s_ings):
                    if is_empty(s_ing):
                        failures.append({
                            "file": "seasonal.json",
                            "record_identifier": identifier,
                            "error_type": "Empty seasonal ingredient entry",
                            "details": f"Seasonal ingredient at index {s_idx} is empty",
                            "suggested_correction": "Remove empty strings from seasonal_ingredients."
                        })
                        is_valid = False

            if is_valid:
                stats["seasonal"]["valid"] += 1
            else:
                stats["seasonal"]["invalid"] += 1

    # ------------------
    # 8. CROSS VALIDATION & MISSING REFERENCES
    # ------------------
    missing_refs = {
        "recipes_to_ingredients": [],
        "chef_notes_to_recipes": [],
        "suppliers_to_ingredients": [],
        "pairings_to_ingredients": []
    }

    # Cross Val 1: Recipes to Ingredients
    if recipes_data is not None and ingredients_data is not None:
        for recipe in recipes_data:
            r_id = recipe.get("recipe_id")
            r_name = recipe.get("recipe_name")
            r_ings = recipe.get("ingredients")
            if r_ings and isinstance(r_ings, list):
                for ing in r_ings:
                    if ing and ing not in ingredient_names:
                        missing_refs["recipes_to_ingredients"].append({
                            "recipe_id": r_id,
                            "recipe_name": r_name,
                            "missing_ingredient": ing,
                            "suggested_correction": f"Add '{ing}' to ingredients.json or update recipes.json to use a valid ingredient name."
                        })
                        failures.append({
                            "file": "recipes.json",
                            "record_identifier": f"{r_id} ({r_name})",
                            "error_type": "Cross-validation: Ingredient not found",
                            "details": f"Recipe uses ingredient '{ing}' which does not exist in ingredients.json",
                            "suggested_correction": f"Add '{ing}' to ingredients.json."
                        })

    # Cross Val 2: Chef Notes to Recipes
    if chef_notes_data is not None and recipes_data is not None:
        for note in chef_notes_data:
            recipe = note.get("recipe")
            tip = note.get("tip")
            if recipe and recipe not in recipe_names:
                missing_refs["chef_notes_to_recipes"].append({
                    "chef_note_recipe": recipe,
                    "tip_snippet": tip[:40] + "..." if tip and len(tip) > 40 else tip,
                    "suggested_correction": f"Ensure recipes.json contains a recipe named '{recipe}'."
                })

    # Cross Val 3: Suppliers to Ingredients
    if suppliers_data is not None and ingredients_data is not None:
        for sup in suppliers_data:
            sup_id = sup.get("supplier_id")
            sup_name = sup.get("supplier_name")
            sup_ings = sup.get("supported_ingredients")
            if sup_ings and isinstance(sup_ings, list):
                for ing in sup_ings:
                    if ing and ing not in ingredient_names:
                        missing_refs["suppliers_to_ingredients"].append({
                            "supplier_id": sup_id,
                            "supplier_name": sup_name,
                            "missing_ingredient": ing,
                            "suggested_correction": f"Add '{ing}' to ingredients.json or remove it from supplier's supported list."
                        })

    # Cross Val 4: Pairings to Ingredients
    if pairing_data is not None and ingredients_data is not None:
        for pair_obj in pairing_data:
            main_ing = pair_obj.get("ingredient")
            pairs = pair_obj.get("pairs")
            if main_ing and main_ing not in ingredient_names:
                missing_refs["pairings_to_ingredients"].append({
                    "pairing_ingredient": main_ing,
                    "context": "Main ingredient",
                    "suggested_correction": f"Add '{main_ing}' to ingredients.json."
                })
            if pairs and isinstance(pairs, list):
                for pair in pairs:
                    if pair and pair not in ingredient_names:
                        missing_refs["pairings_to_ingredients"].append({
                            "pairing_ingredient": pair,
                            "context": f"Paired with {main_ing}",
                            "suggested_correction": f"Add '{pair}' to ingredients.json."
                        })

    # Overall validation status
    has_failures = len(failures) > 0
    overall_status = "FAIL" if has_failures else "PASS"

    # Compile json report
    report = {
        "overall_status": overall_status,
        "summary": {
            "recipes": {
                "status": "FAIL" if stats["recipes"]["invalid"] > 0 or stats["recipes"]["duplicates_id"] > 0 or stats["recipes"]["duplicates_name"] > 0 else "PASS",
                "total_records": stats["recipes"]["total"],
                "valid_records": stats["recipes"]["valid"],
                "invalid_records": stats["recipes"]["invalid"],
                "duplicate_ids": stats["recipes"]["duplicates_id"],
                "duplicate_names": stats["recipes"]["duplicates_name"]
            },
            "ingredients": {
                "status": "FAIL" if stats["ingredients"]["invalid"] > 0 or stats["ingredients"]["duplicates_id"] > 0 or stats["ingredients"]["duplicates_name"] > 0 else "PASS",
                "total_records": stats["ingredients"]["total"],
                "valid_records": stats["ingredients"]["valid"],
                "invalid_records": stats["ingredients"]["invalid"],
                "duplicate_ids": stats["ingredients"]["duplicates_id"],
                "duplicate_names": stats["ingredients"]["duplicates_name"]
            },
            "pairing": {
                "status": "FAIL" if stats["pairing"]["invalid"] > 0 else "PASS",
                "total_records": stats["pairing"]["total"],
                "valid_records": stats["pairing"]["valid"],
                "invalid_records": stats["pairing"]["invalid"]
            },
            "suppliers": {
                "status": "FAIL" if stats["suppliers"]["invalid"] > 0 else "PASS",
                "total_records": stats["suppliers"]["total"],
                "valid_records": stats["suppliers"]["valid"],
                "invalid_records": stats["suppliers"]["invalid"]
            },
            "chef_notes": {
                "status": "FAIL" if stats["chef_notes"]["invalid"] > 0 else "PASS",
                "total_records": stats["chef_notes"]["total"],
                "valid_records": stats["chef_notes"]["valid"],
                "invalid_records": stats["chef_notes"]["invalid"]
            },
            "safety": {
                "status": "FAIL" if stats["safety"]["invalid"] > 0 else "PASS",
                "total_records": stats["safety"]["total"],
                "valid_records": stats["safety"]["valid"],
                "invalid_records": stats["safety"]["invalid"]
            },
            "seasonal": {
                "status": "FAIL" if stats["seasonal"]["invalid"] > 0 else "PASS",
                "total_records": stats["seasonal"]["total"],
                "valid_records": stats["seasonal"]["valid"],
                "invalid_records": stats["seasonal"]["invalid"]
            }
        },
        "missing_references": missing_refs,
        "failures": failures
    }

    # Write JSON report
    with open(REPORT_JSON_PATH, "w", encoding="utf-8") as rf:
        json.dump(report, rf, indent=2, ensure_ascii=False)

    # ------------------
    # PRINT CONSOLE REPORT
    # ------------------
    def get_status_str(sec_name):
        return report["summary"][sec_name]["status"]

    print("==================================")
    print("KitchenSync AI Validation Report")
    print("==================================")
    
    # Recipes Section
    print("Recipes")
    print(get_status_str("recipes"))
    print(f"{stats['recipes']['valid']} Valid")
    print("Duplicates")
    print(f"{stats['recipes']['duplicates_id'] + stats['recipes']['duplicates_name']}")
    print()

    # Ingredients Section
    print("Ingredients")
    print(get_status_str("ingredients"))
    print(f"{stats['ingredients']['valid']} Valid")
    print("Missing")
    total_missing_references = len(missing_refs["recipes_to_ingredients"]) + len(missing_refs["suppliers_to_ingredients"]) + len(missing_refs["pairings_to_ingredients"])
    print(f"{total_missing_references}")
    print()

    # Suppliers Section
    print("Suppliers")
    print(get_status_str("suppliers"))
    print(f"{stats['suppliers']['valid']} Valid")
    print()

    # Chef Notes Section
    print("Chef Notes")
    print(get_status_str("chef_notes"))
    print(f"{stats['chef_notes']['valid']} Valid")
    print()

    # Pairings Section
    print("Pairings")
    print(get_status_str("pairing"))
    print(f"{stats['pairing']['valid']} Valid")
    print()

    # Overall Status Section
    print("Overall Status")
    print(overall_status)
    print("==================================")

    # Display failure details if there are any
    if has_failures:
        print("\n!!! VALIDATION FAILURES DETECTED !!!")
        print(f"Total failures/warnings found: {len(failures)}")
        print("Details can be found in: validation_report.json\n")
        # Display first 10 failures as a preview
        for i, fail in enumerate(failures[:10]):
            print(f"{i+1}. [{fail['file']}] {fail['error_type']} at '{fail['record_identifier']}'")
            print(f"   Reason: {fail['details']}")
            print(f"   Correction: {fail['suggested_correction']}")
        if len(failures) > 10:
            print(f"... and {len(failures) - 10} more failures. See validation_report.json.")
        sys.exit(1)
    else:
        print("\nAll files passed validation successfully!")
        sys.exit(0)

if __name__ == "__main__":
    validate()
