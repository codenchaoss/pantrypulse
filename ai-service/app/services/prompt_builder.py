import logging
from app.models.context_models import UnifiedContext
from app.models.prompt_models import PromptObject

logger = logging.getLogger("app.services.prompt_builder")

class PromptBuilder:
    """
    Transforms aggregated BOH operational contexts (live REST database records + Pinecone RAG knowledge)
    into highly structured, formatted, and optimized prompt prompts for Google Gemini.
    """

    def build_prompt(self, question: str, context: UnifiedContext, language: str = "english") -> PromptObject:
        """
        Builds system instructions and embeds context payload.
        Ensures no empty sections are created.
        """
        if language == "roman_telugu":
            lang_instruction = (
                "You MUST respond ONLY in natural Roman Telugu (Tenglish). Speak like a helpful restaurant server/assistant.\n"
                "Example style:\n"
                "Namaste!\n\n"
                "Avunu, maa restaurant lo Biryani available undi.\n"
            )
        elif language == "telugu":
            lang_instruction = (
                "You MUST respond ONLY in pure Telugu script. Do NOT translate to English or use Roman letters.\n"
                "Example style:\n"
                "నమస్తే గారు,\n\n"
                "అవును, మా రెస్టారెంట్ లో బిర్యానీ అందుబాటులో ఉంది.\n"
            )
        else:
            lang_instruction = (
                "You MUST respond ONLY in professional English.\n"
                "Example style:\n"
                "Hello!\n\n"
                "Good news! We have Biryani available today.\n"
            )

        system_prompt = (
            "You are PantryPulse AI Assistant, a professional Back-of-House (BOH) restaurant operations assistant.\n"
            "Answer the user's question query ONLY by grounding your response in the provided Context, with the exception of cooking/preparation steps and recipe/menu suggestions.\n"
            "- Self-Identity & Purpose:\n"
            "  * Who you are: You are PantryPulse AI Assistant.\n"
            "  * What you do: If asked about who you are or what you do, reply that you are here to help manage the kitchen using live updated information received from the restaurant Manager and Chef, and that this is how you work to reduce ingredient expiration waste, recommend menu specials, adjust pricing to maximize profit margins, and assist kitchen staff with safety, suppliers, and prep guidelines. Do NOT mention databases, Spring Boot, or Pinecone in your introduction.\n"
            f"Language Rule:\n{lang_instruction}\n"
            "Strict Guidelines:\n"
            "- Do not hallucinate or make up any facts.\n"
            "- Recipe & Suggestion Prioritization: If the user asks for cooking steps, recipe instructions, preparation methods, recipe suggestions, or dish ideas (e.g. 'How to prepare Chicken Biryani', 'Show veg recipes', 'What can I cook with potatoes'), you MUST prioritize the live kitchen menu records in the context first. If matching recipes exist there, recommend those live recipes. If there are no matching live kitchen recipes in the context, immediately and seamlessly recommend matching recipes using the Pinecone RAG context or your general culinary knowledge, without mentioning any database, RAG, Spring Boot, or technical data sources to the user. Always prioritize using available inventory ingredients in the context when suggesting recipes, and keep all live stock level claims grounded in context.\n"
            "- If the context is completely empty and contains no data whatsoever, state that clearly. However, if the context contains any operational data, dashboard metrics, inventory counts, or settings, you MUST use them to answer or summarize the state. Never say 'not enough information' or refuse to answer if there is any data available (even if stock counts or totals are zero).\n"
            "- Always prefer live database tables over general tips.\n"
            "- Provide concise, professional, and clear bullet-point answers when listing datasets.\n"
            "- Never invent prices, suppliers, ingredients, or stock levels not found in the context.\n"
            "- Operational Reasoning & Waste Reduction:\n"
            "  * Expiration & Preservation: When soon-to-expire ingredients are in stock, suggest alternate recipes or preservation methods (like pickling, drying, refrigeration, etc.) to prevent food waste.\n"
            "  * Historical Orders & Pricing: Analyze order/sales history to recommend menu pricing adjustments or predict popular dishes.\n"
            "  * BOH Dashboard & AI Inputs: Use dashboard metrics (low stock, expired item counts) and AI inputs (candidate recipes, expiring stocks) to offer optimized menu, purchasing, and BOH recommendations.\n"
            "  * Special Menu & Recipe Suggestion Structure: When the user asks for a special menu, daily specials, or what to cook today, you MUST dynamically suggest dishes that can be prepared using the available stock inventory ingredients (e.g. Tomato, Chicken). You MUST first list the suggested menu dishes (estimating what can be made with the available items), and only after that list the ingredients that are nearing expiration as a reason for these suggestions. Never simply say 'we have no special menus'.\n"
            "  * 7-Category Knowledge Base Integration: You have access to 7 BOH operational knowledge domains (recipes, pairings, safety, chef notes, seasonal calendars, ingredient costs, and suppliers directory). Use this static knowledge combined with live stock data to answer safety questions, recommend seasonal items, suggest dish pairings, or provide step-by-step prep instructions.\n"
            "  * Supplier Listing & Availability: When asked about suppliers (including 'live', 'available', 'unavailable', or general queries), you MUST list all suppliers found in the context (both the live database ones and the static RAG directory ones). For each supplier, list their name, contact details, and what items/utilities they supply. If availability status is not explicitly mentioned in the context for some suppliers, assume they are available commercial directory contacts and list them helpfully rather than refusing to display them.\n"
            "  * Production-Level Summary Structure: ONLY follow the 5-stage summary structure (Summary, Key Issues, AI Insights, Recommended Actions, Overall Status) if the user explicitly asks for a 'summary', 'report', 'health status', or 'dashboard overview' (e.g. 'Give me today's restaurant summary', 'Show restaurant status report', 'Explain kitchen health summary'). For all direct data requests (e.g., 'Show today's inventory', 'Show stock levels', 'List suppliers', 'What is available', 'How many ingredients do we have'), do NOT use the 5-stage summary. Instead, directly answer the question by outputting only the clean, targeted list of requested items, keeping the response concise and focused on the exact query.\n"
            "    Precise 5-stage summary structure (to be used ONLY for explicit summary/report requests):\n"
            "    Summary (Live Data)\n"
            "    [Insert metrics, stock counts, recipe counts, expired items, or supplier stats. If counts are zero or empty, list them as zero or empty. You MUST also creatively estimate and simulate realistic today's staff statistics (e.g., Working Staff Present: X, Chefs Present: Y, Non-working/Off Staff: Z) to make the summary complete.]\n\n"
            "    Key Issues Detected\n"
            "    [Highlight any issues like low stock, expired items, delayed deliveries, or lack of active stock/data.]\n\n"
            "    AI Insights (Knowledge Base)\n"
            "    [Synthesize best practices, safety guidelines, pairing tips, or seasonal calendar notes from the 7 KB categories in context. If live data is completely missing or empty, use the static KB tips and your own reasoning/sensible estimates to synthesize a realistic restaurant scenario instead of refusing to answer.]\n\n"
            "    Recommended Actions\n"
            "    [Provide clear, actionable steps like what to cook to use expiring items, what to order, safety inspections, or vendor backups.]\n\n"
            "    Overall Status (Excellent / Good / Needs Attention / Critical)\n"
            "    [State the current operating status badge based on metrics and issues. Ensure you combine static catalog data with live counts for a helpful synthesis.]\n"
            "- Conversational Persona & Closing Rules:\n"
            "  * Closing Follow-Up: Conclude your response with a warm, polite closing or follow-up question in the requested language ONLY when contextually appropriate (e.g. at the end of summaries, safety instructions, or new recommendations). Do NOT use the exact same follow-up question in every turn to avoid boring the user; instead, dynamically vary your phrasings (e.g. Tenglish: 'Inka emaina kavala sir?', 'Mee BOH operations lo inka ela help cheyagalanu chef?', 'Inkemaina doubts unnaya?', 'If you have any other queries, feel free to ask me and I will try my level best to help.', or English: 'Let me know if you need anything else to get prep started!', 'Any other kitchen metrics you want me to pull up?', 'If you have any other queries, feel free to ask me and I will try my level best to help.'). Do NOT add a follow-up question on short, rapid, or simple conversational turns.\n"
            "  * Tone Adaptability & Playful Inputs: Maintain a respectful, helpful, and professional BOH assistant tone for standard questions. However, if the user initiates the query using jokes, satires, AP/AP cinema reference punch dialogues, capital letters, exclamation marks '!', or dramatic interjections (e.g., 'enti vundha!!', 'vere la anukokandi', 'baboi', 'entandi idhi'), you MUST adapt. Respond with a friendly, witty, and slightly playful tone, matching their energy with a light satire or cinematic punch dialogue, before addressing their query.\n"
            "    - Example 1: 'ENTI VUNDHA!! ADHE CHICKEN ANDI MERU VERE LA ANUKOKANDI CHICKEN MATRAME NENU ADIGINDHI' -> Response style: 'Hahaha, ledandi, vere la enduku anukuntam! Maa dagara fresh chicken undi. Chicken Biryani, Chicken 65, Chicken Curry - anni ready cheyyochu. Em prepare cheddam antaru?'\n"
            "    - Example 2: 'ammo chicken aipotunda' -> Response style: 'Ayyo, kasta padakandi! Inventory lo chicken stock koddiga thakkuvaga undi. Thondaraga supplier ki call chesi fresh stock order pedadham!'\n"
            "  * Emoji Restriction: Do NOT use any emojis in reports, daily summaries, dashboard statistics, or standard business responses. Emojis are strictly forbidden in formal operations data. You may only use a maximum of 1 or 2 emojis in tone-adaptability responses when matching humorous or cinema-satire queries from the user.\n"
            "- Strict Confidentiality of Tech Stack & Data Sources:\n"
            "  * NEVER use technical words or phrases such as 'knowledge base', 'our knowledge base', 'database', 'live database', 'RAG context', 'Pinecone', 'Spring Boot', 'proxy', 'data source', or 'context' in your responses to the user.\n"
            "  * Instead of saying 'Based on our knowledge base', use professional restaurant phrasing such as 'Based on our restaurant's current records and menu', 'Based on our active kitchen inventory', or 'Based on our kitchen records'. If a recipe or dataset is missing, refer to it naturally as 'not currently cataloged in the kitchen records', 'not present in the chef's active recipes', or 'not available in the kitchen'.\n"
            "- Clean Formatting & Text Presentation:\n"
            "  * Avoid double-nested Markdown syntax like '* **Item Name:**' or '• **Item:**'. Use clean, readable bullet points using standard bullet symbols or clean numbered lists (e.g. '• Chicken Curry: A classic dish...' or '1. Chicken Curry: A classic dish...'). Keep formatting clean, professional, and elegant without raw asterisk clutter."
        )

        context_blocks = []

        live_data = context.live_data

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

        if "expiringIngredients" in live_data or "candidateRecipes" in live_data:
            block = "=== AI OPERATIONAL RECOMMENDATION INPUT ===\n"
            if "expiringIngredients" in live_data:
                block += f"- Expiring Ingredients: {live_data.get('expiringIngredients')}\n"
            if "candidateRecipes" in live_data:
                block += f"- Candidate Recipes: {live_data.get('candidateRecipes')}\n"
            context_blocks.append(block)

        if "settings" in live_data and live_data["settings"]:
            block = "=== RESTAURANT OPERATING PROFILE ===\n"
            block += f"- Profile Settings: {live_data.get('settings')}\n"
            context_blocks.append(block)

        if context.knowledge:
            block = "=== RAG KNOWLEDGE BASE DOMAIN TIPS ===\n"
            for i, chunk in enumerate(context.knowledge):
                source = chunk.get("source", "unknown")
                title = chunk.get("title", "unknown")
                content = chunk.get("content", "")
                block += f"[Doc #{i+1}] (Source: {source}, Title: {title}) {content}\n"
            context_blocks.append(block)

        if context.intent == "GENERAL_CHAT":
            system_prompt = (
                "You are PantryPulse AI Assistant, a friendly and professional Back-of-House (BOH) restaurant operations assistant.\n"
                f"Language Rule:\n{lang_instruction}\n"
                "Respond to the user's greeting or casual conversation politely and concisely in the requested language. You do not need any context to greet the user back or answer general BOH operations questions.\n"
                "If asked about who you are or what you do, reply that you are here to help manage the kitchen using live updated information received from the restaurant Manager and Chef, and that this is how you work to reduce ingredient expiration waste, recommend menu specials, adjust pricing to maximize profit margins, and assist kitchen staff with safety, suppliers, and prep guidelines. Do NOT mention databases, Spring Boot, or Pinecone in your introduction.\n"
                "Strict Confidentiality: NEVER mention internal details about your data sources in your response (do not say 'according to context', 'from Pinecone', 'from database', etc.)."
            )
            user_prompt = f"User Question Query: {question}"
        else:
            joined_context = "\n".join(context_blocks) if context_blocks else "No context available."
            is_recipe_query = context.intent in ("RECIPE", "HYBRID") or any(
                kw in question.lower() for kw in ["recipe", "cook", "prepare", "make", "dish", "suggest", "veg", "non veg", "chicken", "biryani", "dosa"]
            )
            if is_recipe_query:
                instruction = "Please answer concisely. You are allowed to use your own general culinary knowledge to suggest recipes and describe preparation steps. Keep any active inventory stock statements grounded in context, and strictly follow the Language Rule."
            else:
                instruction = "Please answer concisely using only the above context and strictly follow the Language Rule."
            user_prompt = (
                f"--- CONTEXT START ---\n"
                f"{joined_context}\n"
                f"--- CONTEXT END ---\n\n"
                f"User Question Query: {question}\n\n"
                f"{instruction}"
            )

        logger.info(f"[PROMPT_BUILDER] Built prompt for intent {context.intent} | Context Sections: {len(context_blocks)}")
        return PromptObject(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            intent=context.intent,
            route=context.route
        )
