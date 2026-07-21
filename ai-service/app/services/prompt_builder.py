import logging
from app.models.context_models import UnifiedContext
from app.models.prompt_models import PromptObject

# Setup logger for Prompt Builder
logger = logging.getLogger("app.services.prompt_builder")

class PromptBuilder:
    """
    Transforms aggregated BOH operational contexts (live REST database records + Pinecone RAG knowledge)
    into highly structured, formatted, and optimized prompt prompts for Google Gemini.
    """

    def build_prompt(self, question: str, context: UnifiedContext) -> PromptObject:
        """
        Builds system instructions and embeds context payload.
        Ensures no empty sections are created.
        """
        system_prompt = (
            "You are KitchenSync AI, a professional Back-of-House (BOH) operational assistant.\n"
            "Answer the user's question query ONLY by grounding your response in the provided Context.\n"
            "Strict Guidelines:\n"
            "- Do not hallucinate or make up any facts.\n"
            "- If the context is empty or does not contain enough information to answer, state that clearly.\n"
            "- Always prefer live database tables (inventory, suppliers, recipes) over knowledge base tips.\n"
            "- Provide concise, professional, and clear bullet-point answers when listing datasets.\n"
            "- Never invent prices, suppliers, ingredients, or stock levels not found in the context."
        )

        context_blocks = []

        # 1. Parse Live Data Sections
        live_data = context.live_data

        # A. Inventory Section
        if "inventory" in live_data and live_data["inventory"]:
            block = "=== RESTAURANT LIVE STOCK INVENTORY ===\n"
            for item in live_data["inventory"]:
                block += (
                    f"- Ingredient: {item.get('ingredientName', 'Unknown')}\n"
                    f"  Quantity: {item.get('quantity', 0.0)} {item.get('unit', '')}\n"
                    f"  Category: {item.get('category', 'N/A')}\n"
                    f"  Expiry Date: {item.get('expiryDate', 'N/A')}\n"
                    f"  Available: {item.get('available', True)}\n"
                )
            context_blocks.append(block)

        # B. Recipes Section
        if "recipes" in live_data and live_data["recipes"]:
            block = "=== RECIPE CATALOG & PRICING ===\n"
            for item in live_data["recipes"]:
                block += (
                    f"- Recipe Name: {item.get('recipeName', 'Unknown')}\n"
                    f"  Category: {item.get('category', 'N/A')}\n"
                    f"  Preparation Time: {item.get('preparationTime', 0)} mins\n"
                    f"  Cost Price: ${item.get('costPrice', 0.0)}\n"
                    f"  Selling Price: ${item.get('sellingPrice', 0.0)}\n"
                    f"  Available: {item.get('available', True)}\n"
                )
            context_blocks.append(block)

        # C. Suppliers Section
        if "suppliers" in live_data and live_data["suppliers"]:
            block = "=== COMMERICAL SUPPLIERS DIRECTORY ===\n"
            for item in live_data["suppliers"]:
                block += (
                    f"- Supplier Name: {item.get('supplierName', 'Unknown')}\n"
                    f"  Contact Person: {item.get('contactPerson', 'N/A')}\n"
                    f"  Phone: {item.get('phone', 'N/A')}\n"
                    f"  Email: {item.get('email', 'N/A')}\n"
                    f"  Address: {item.get('address', 'N/A')}\n"
                )
            context_blocks.append(block)

        # D. Expiration Section
        if "expiring" in live_data and live_data["expiring"]:
            block = "=== URGENT INGREDIENTS EXPIRATION ALERTS ===\n"
            for item in live_data["expiring"]:
                block += (
                    f"- Ingredient: {item.get('ingredientName', 'Unknown')}\n"
                    f"  Quantity: {item.get('quantity', 0.0)} {item.get('unit', '')}\n"
                    f"  Expiry Date: {item.get('expiryDate', 'N/A')}\n"
                    f"  Days Remaining: {item.get('daysRemaining', 0)} days\n"
                )
            context_blocks.append(block)

        # E. Historical Orders Section
        if "historical_orders" in live_data and live_data["historical_orders"]:
            block = "=== HISTORICAL PURCHASING ORDERS ===\n"
            for item in live_data["historical_orders"]:
                block += (
                    f"- Order ID: {item.get('id', 'N/A')}\n"
                    f"  Ingredient: {item.get('ingredientName', 'Unknown')}\n"
                    f"  Quantity: {item.get('quantity', 0.0)} {item.get('unit', '')}\n"
                    f"  Price Per Unit: ${item.get('pricePerUnit', 0.0)}\n"
                    f"  Order Date: {item.get('orderDate', 'N/A')}\n"
                )
            context_blocks.append(block)

        # F. Dashboard Summary Statistics
        # Check if the keys are present in live_data
        dash_keys = ["totalIngredients", "totalRecipes", "lowStockItems", "expiringSoon"]
        if any(k in live_data for k in dash_keys):
            block = "=== RESTAURANT PERFORMANCE DASHBOARD SUMMARY ===\n"
            block += (
                f"- Total Ingredients Cataloged: {live_data.get('totalIngredients', 0)}\n"
                f"- Total Active Recipes: {live_data.get('totalRecipes', 0)}\n"
                f"- Low Stock Alert items: {live_data.get('lowStockItems', 0)}\n"
                f"- Near Expiration Items: {live_data.get('expiringSoon', 0)}\n"
                f"- Expired items Count: {live_data.get('expiredItems', 0)}\n"
            )
            context_blocks.append(block)

        # G. Recommendation AI inputs
        if "expiringIngredients" in live_data or "candidateRecipes" in live_data:
            block = "=== AI OPERATIONAL RECOMMENDATION INPUT ===\n"
            if "expiringIngredients" in live_data:
                block += f"- Expiring Ingredients: {live_data.get('expiringIngredients')}\n"
            if "candidateRecipes" in live_data:
                block += f"- Candidate Recipes: {live_data.get('candidateRecipes')}\n"
            context_blocks.append(block)

        # H. Restaurant Profile Settings
        if "settings" in live_data and live_data["settings"]:
            block = "=== RESTAURANT OPERATING PROFILE ===\n"
            block += f"- Profile Settings: {live_data.get('settings')}\n"
            context_blocks.append(block)

        # 2. Parse Knowledge base Sections
        if context.knowledge:
            block = "=== RAG KNOWLEDGE BASE DOMAIN TIPS ===\n"
            for i, chunk in enumerate(context.knowledge):
                source = chunk.get("source", "unknown")
                title = chunk.get("title", "unknown")
                content = chunk.get("content", "")
                block += f"[Doc #{i+1}] (Source: {source}, Title: {title}) {content}\n"
            context_blocks.append(block)

        # 3. Assemble prompts
        joined_context = "\n".join(context_blocks) if context_blocks else "No context available."
        
        user_prompt = (
            f"--- CONTEXT START ---\n"
            f"{joined_context}\n"
            f"--- CONTEXT END ---\n\n"
            f"User Question Query: {question}\n\n"
            f"Please answer concisely using only the above context."
        )

        logger.info(f"[PROMPT_BUILDER] Built prompt for intent {context.intent} | Context Sections: {len(context_blocks)}")
        return PromptObject(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            intent=context.intent,
            route=context.route
        )
