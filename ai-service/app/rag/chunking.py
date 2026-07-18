import json
import os
import logging
from app.core import config

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def load_json(path):
    if not os.path.exists(path):
        logger.error(f"File not found: {path}")
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading JSON at {path}: {str(e)}")
        return []

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Successfully generated chunks: {path} ({len(data)} records)")
    except Exception as e:
        logger.error(f"Error saving JSON to {path}: {str(e)}")

def chunk_recipes():
    logger.info("Chunking recipes...")
    recipes = load_json(config.RECIPES_JSON)
    chunks = []
    
    for idx, r in enumerate(recipes):
        recipe_id = r.get("recipe_id")
        recipe_name = r.get("recipe_name", "Unknown")
        desc = r.get("description", "")
        ingredients = r.get("ingredients", [])
        instructions = r.get("instructions", [])
        
        # Build text content
        content_parts = [
            f"Recipe Name: {recipe_name}",
            f"Description: {desc}",
            f"Ingredients: {', '.join(ingredients)}",
            "Instructions:\n" + "\n".join(f"{i+1}. {step}" for i, step in enumerate(instructions))
        ]
        content = "\n".join(content_parts)
        
        chunk = {
            "chunk_id": f"CHK{idx + 1:06d}",
            "source": "recipes",
            "document_id": recipe_id,
            "title": recipe_name,
            "category": r.get("category", ""),
            "cuisine": r.get("cuisine", ""),
            "difficulty": r.get("difficulty", ""),
            "tags": r.get("tags", []),
            "search_keywords": r.get("search_keywords", []),
            "content": content,
            "metadata": {
                "preparation_time": r.get("preparation_time_minutes", 0),
                "calories": r.get("estimated_calories", 0),
                "knowledge_type": "recipe"
            }
        }
        chunks.append(chunk)
        
    save_json(config.RECIPES_CHUNKS, chunks)
    return chunks

def chunk_ingredients():
    logger.info("Chunking ingredients...")
    ingredients = load_json(config.INGREDIENTS_JSON)
    chunks = []
    
    for ing in ingredients:
        ing_id = ing.get("ingredient_id")
        ing_name = ing.get("ingredient_name", "Unknown")
        category = ing.get("category", "")
        shelf_life = ing.get("average_shelf_life_days", 0)
        storage_type = ing.get("storage_type", "")
        
        content = f"{ing_name} belongs to {category} category. Average shelf life is {shelf_life} days. Storage type {storage_type}."
        
        chunk = {
            "chunk_id": ing_id,
            "source": "ingredients",
            "document_id": ing_id,
            "title": ing_name,
            "content": content,
            "metadata": {
                "knowledge_type": "ingredient"
            }
        }
        chunks.append(chunk)
        
    save_json(config.INGREDIENTS_CHUNKS, chunks)
    return chunks

def chunk_suppliers():
    logger.info("Chunking suppliers...")
    suppliers = load_json(config.SUPPLIERS_JSON)
    chunks = []
    
    for sup in suppliers:
        sup_id = sup.get("supplier_id")
        sup_name = sup.get("supplier_name", "Unknown")
        supported_ingredients = sup.get("supported_ingredients", [])
        delivery_time = sup.get("delivery_time_hours", 0)
        
        content = f"{sup_name} supplies {', '.join(supported_ingredients)}. Delivery time {delivery_time} hours."
        
        chunk = {
            "chunk_id": sup_id,
            "source": "suppliers",
            "document_id": sup_id,
            "title": sup_name,
            "content": content,
            "metadata": {
                "knowledge_type": "supplier"
            }
        }
        chunks.append(chunk)
        
    save_json(config.SUPPLIERS_CHUNKS, chunks)
    return chunks

def chunk_chef_notes():
    logger.info("Chunking chef notes...")
    notes = load_json(config.CHEF_NOTES_JSON)
    chunks = []
    
    for idx, note in enumerate(notes):
        recipe = note.get("recipe", "Unknown")
        tip = note.get("tip", "")
        chunk_id = f"CHEF{idx + 1:03d}"
        
        chunk = {
            "chunk_id": chunk_id,
            "source": "chef_notes",
            "document_id": chunk_id,
            "title": recipe,
            "content": tip,
            "metadata": {
                "knowledge_type": "chef_note"
            }
        }
        chunks.append(chunk)
        
    save_json(config.CHEF_CHUNKS, chunks)
    return chunks

def chunk_safety():
    logger.info("Chunking safety rules...")
    safety_records = load_json(config.SAFETY_JSON)
    chunks = []
    
    for idx, record in enumerate(safety_records):
        ing = record.get("ingredient", "Unknown")
        storage = record.get("storage", "")
        temp = record.get("recommended_temperature", "")
        max_shelf = record.get("maximum_shelf_life_days", 0)
        chunk_id = f"SAFE{idx + 1:03d}"
        
        content = f"Store at {temp} ({storage}). Maximum shelf life {max_shelf} days."
        
        chunk = {
            "chunk_id": chunk_id,
            "source": "safety",
            "document_id": chunk_id,
            "title": ing,
            "content": content,
            "metadata": {
                "knowledge_type": "safety"
            }
        }
        chunks.append(chunk)
        
    save_json(config.SAFETY_CHUNKS, chunks)
    return chunks

def chunk_seasonal():
    logger.info("Chunking seasonal schedules...")
    seasonal_records = load_json(config.SEASONAL_JSON)
    chunks = []
    
    for idx, item in enumerate(seasonal_records):
        season = item.get("season", "")
        week = item.get("week_number", 0)
        cats = item.get("recommended_categories", [])
        ingredients = item.get("seasonal_ingredients", [])
        pricing_trend = item.get("pricing_trend", "")
        tip = item.get("special_menu_tip", "")
        chunk_id = f"SEAS{idx + 1:03d}"
        
        title = f"{season} Week {week}"
        content = (
            f"Recommended categories: {', '.join(cats)}. "
            f"Seasonal ingredients: {', '.join(ingredients)}. "
            f"Pricing trend: {pricing_trend}. "
            f"Menu tip: {tip}"
        )
        
        chunk = {
            "chunk_id": chunk_id,
            "source": "seasonal",
            "document_id": chunk_id,
            "title": title,
            "content": content,
            "metadata": {
                "knowledge_type": "seasonal"
            }
        }
        chunks.append(chunk)
        
    save_json(config.SEASONAL_CHUNKS, chunks)
    return chunks

def run_all_chunking():
    logger.info("Starting knowledge base chunking pipeline...")
    recipe_chunks = chunk_recipes()
    ing_chunks = chunk_ingredients()
    sup_chunks = chunk_suppliers()
    chef_chunks = chunk_chef_notes()
    safety_chunks = chunk_safety()
    seasonal_chunks = chunk_seasonal()
    
    total_chunks = len(recipe_chunks) + len(ing_chunks) + len(sup_chunks) + len(chef_chunks) + len(safety_chunks) + len(seasonal_chunks)
    logger.info(f"Chunking pipeline complete. Total chunks generated: {total_chunks}")
    return total_chunks

if __name__ == "__main__":
    run_all_chunking()
