import re
import logging
import numpy as np
from typing import Dict, Any, List
from app.models.intent_models import Intent, Route, IntentResult
from app.rag.embedding import EmbeddingEngine

# Setup logger for Intent Routing
logger = logging.getLogger("app.routing.intent_router")

class IntentRouter:
    """
    Deterministic rule-based Intent Router.
    Classifies user queries into specialized Back-of-House (BOH) operational intents
    and determines the optimal data routing path (Spring Boot APIs, Pinecone RAG, or both).
    Runs offline with zero external network or model latency.
    """

    _cached_anchor_embeddings = None

    def __init__(self):
        # Define keyword lists for each intent category
        self.keywords_map = {
            Intent.HYBRID: [
                "suggest menu", "recommend menu", "available ingredients", "today's menu",
                "todays menu", "recipe using inventory", "recipe using available ingredients",
                "best recipe today", "cook with available", "menu planner", "daily specials",
                "cook with inventory", "suggest recipes using available", "what can i cook with",
                "what can i prepare with", "menu options based on", "specials using stock",
                "recipes using current stock", "menu suggestion", "what to cook with available",
                "matching recipes with available", "dishes using inventory", "menu matching available",
                "dishes using current stock", "specials from inventory", "unna ingredients",
                "recipies list", "recipies of", "menu list of",
                "unna stock to", "unna ingredients tho", "unna vatitho", "unna vatikitho",
                "available ingredients tho", "available items to", "inventry recipes", "available recipes",
                "recommend recipe using stock", "what to prepare with stock", "what to make with stock",
                "make recipe with available", "cook menu with stock", "recipes out of inventory",
                "suggest dishes with stock", "prepare dishes with available", "menu plan for today",
                "suggest food using inventory", "cook with items", "create menu from inventory",
                "recommend dishes using inventory", "what to cook with today's stock", "dishes list from stock",
                "available ingredients recipe", "cook items in stock", "recipes using store items",
                "menu using raw materials", "recipes from kitchen stock", "suggest menu using inventory",
                "daily recipes using available", "prepare food using stock", "cook with available ingredients",
                "unna stock recipes", "unna sarakulu list", "unna sarakulato vantalu", "saruku recipes",
                "fridge lo unnavati recipes", "kitchen lo unna sarakulato", "unnavatitho vantalu",
                "what can i cook", "what can i make", "what dishes", "recommend food", "suggest lunch",
                "suggest dinner", "prepare menu", "daily menu", "today special", "chef special",
                "highest profit recipe", "cheapest recipe", "low cost dish", "best margin", "most profitable",
                "use expiring items", "recipes before expiry", "avoid waste", "consume today", "reduce waste",
                "missing ingredients", "order ingredients", "what should i buy", "create purchase list",
                "generate shopping list", "special menu", "menu enti", "special menu enti", "special enti",
                "iroju special", "iroju menu", "iroju special menu", "iroju special menu enti", "e roju menu",
                "e roju special", "e roju special menu", "today special menu", "today menu enti",
                "what is today special menu", "daily special menu",
                "unnavati to recipes", "unnavati to vantalu", "unna stock to recipes", "available stock to recipes",
                "chicken unte em cheyyali", "chicken to recipes", "tomato to recipes", "onion to recipes",
                "potato to recipes", "paner to recipes", "egg to recipes", "mutton to recipes",
                "chepalu to recipes", "fish to recipes", "rice to recipes", "milku to recipes",
                "unna stock thoti recipes", "unna ingredients list vantalu", "unnavatitho vantalu cheppu",
                "unnavatitho em cheyyochu", "unnavatitho em vandochu", "unna stock tho em vandali",
                "available sarakulatho em vandali", "e roju em prepare cheyali", "iroju em prepare cheyali",
                "special items in stock", "stock recipes enti", "available ingredients vantalu",
                "available items tho recipes", "stock list recipes", "invenoty to cook", "inventory recipes enti",
                "cook using stock", "prepare using stock", "suggest dishes based on stock",
                "recommend recipes based on stock", "special recipes with stock", "menu based on inventory",
                "menu based on stock", "specials with inventory"
            ],
            Intent.INVENTORY: [
                "inventory", "ingredient", "ingredients", "stock", "available", "quantity",
                "low stock", "vundhi", "undhi", "unnaya", "naku", "stock levels", "stock level",
                "items list", "list of ingredients", "what do we have", "materials list", "raw materials",
                "pantry items", "pantry stock", "store room", "remaining ingredients", "stock quantities",
                "current stock", "stock count", "how much is left", "how many items", "check stock",
                "verify stock", "food stock", "raw stock", "kitchen inventory", "back of house inventory",
                "what ingredients are in stock", "are we out of", "is there any", "do we have", "undha",
                "unnai", "unnavu", "stock entha", "stock enundi", "kavali", "kavaali", "pantry lo", "fridge lo",
                "whats in stock", "show inventory", "remaining stock", "total stock", "stock directory",
                "ingredient list", "stock on hand", "material stock", "fridge stock", "kitchen stock",
                "ingredients count", "available food stock", "how much stock", "any stock left", "stock status",
                "verify ingredients", "list of stock", "raw items list", "store stock", "how much gram",
                "how many kg", "quantity left", "in stock items", "out of stock items", "low stock items",
                "low inventory", "critical stock", "stock count today", "kitchen materials", "sarakulu list",
                "sarakulu", "pantry list", "pantry items", "stock entha undhi", "items unnaya", "unnaya leva",
                "is available", "availability", "in hand", "on hand", "remaining quantity", "current inventory",
                "available quantity", "kg", "grams", "litre", "liter", "ml", "packet", "packets", "pieces",
                "nos", "boxes", "cartons", "bottles", "bags", "out of stock", "almost empty", "critical stock",
                "reorder", "restock required", "stock finished", "stock exhausted", "do we have onion",
                "do we have tomato", "is chicken available", "show tomato quantity", "rice available"
            ],
            Intent.RECIPE: [
                "recipe", "recipes", "dish", "dishes", "cook", "prepare", "meal", "making",
                "how to make", "how to prepare", "make", "how do i make", "chilli chicken",
                "chicken curry", "mutton curry", "biryani", "pulao", "starter", "starters",
                "main course", "dessert", "desserts", "tiffin", "food items", "restaurant menu",
                "menu catalog", "recipe catalog", "food list", "dishes list", "cuisine specials",
                "cooking steps", "cooking method", "prep steps", "instruction", "instructions",
                "ingredients list for", "recipe for", "how do i cook", "step to prepare", "steps to cook",
                "cooking instructions", "ela cheyali", "ela vandali", "chepala pulusu", "kodi vepudu",
                "gongura pappu", "sankati", "tayaru cheyadam", "tayaree", "vandatam", "elaga",
                "recipe steps", "preparation steps", "preparation method", "how do we cook",
                "steps for recipe", "method of cooking", "dishes catalog", "menu items list", "menu book",
                "food recipe", "how to bake", "how to grill", "how to boil", "cooking guide", "recipe guide",
                "dishes recipes", "signature dish", "chef recipe", "how can i prepare", "food menu list",
                "dish instruction", "dish preparation", "curry preparation", "making steps",
                "vantalu", "vanta ela cheyali", "vandadam ela", "tayaru cheyadam ela", "curry cheyadam ela",
                "indian", "south indian", "north indian", "chinese", "italian", "continental", "megical",
                "thai", "breakfast", "lunch", "dinner", "snacks", "starter", "main course", "dessert",
                "beverage", "veg", "non veg", "spicy", "sweet", "healthy", "protein rich", "kids menu",
                "diet food", "quick recipe", "easy recipe"
            ],
            Intent.SUPPLIER: [
                "supplier", "suppliers", "vendor", "vendors", "procurement", "purchase",
                "restock", "replenish", "contact", "wholesaler", "dealer", "distributor",
                "email", "phone", "rating", "contact info", "supplier directory", "vendor list",
                "supplier email", "supplier phone", "commercial supplier", "lpg supplier", "gas supplier",
                "water supplier", "dairy supplier", "poultry supplier", "seafood supplier", "meat supplier",
                "produce supplier", "dry pantry wholesaler", "distributor details", "vendor contact",
                "supplier details", "reorder contact", "purchasing contact", "wholesalers", "orders email",
                "email address", "phone number", "contact details", "restocking contact",
                "contact supplier", "email supplier", "phone supplier", "supplier address", "vendor address",
                "supplier number", "vendor number", "who supplies", "procurement contact",
                "groceries wholesaler", "meat wholesaler", "vegetable vendor", "lpg wholesaler", "who sells",
                "wholesaler list", "supplier info", "vendor info", "supplier list", "vendor catalog",
                "supplier pricing contact", "purchase department", "vendors directory", "supplier rating",
                "vendor rating", "best supplier", "suppliers detail", "suppliers details", "dealers list",
                "dealers detail", "distributors detail", "restock supplier", "replenishment vendor",
                "delivery", "lead time", "minimum order", "moq", "payment terms", "credit", "cash", "upi",
                "supplier location", "delivery schedule", "supplier performance", "supplier ranking"
            ],
            Intent.PRICING: [
                "price", "pricing", "cost", "profit", "margin", "selling", "sellingprice",
                "costprice", "rate", "kharchu", "vilava", "prices", "selling price", "cost price",
                "profit margin", "food cost", "cost of ingredients", "retail price", "menu price",
                "price suggestions", "recommended pricing", "cost analysis", "profit analysis", "markup",
                "profit percentage", "financial margin", "dish pricing", "price list", "charge",
                "revenue suggestion", "pricing suggestions", "entha cost", "entha price", "ammaka dharalu",
                "koniya dharalu", "daralu", "entha", "selling price of", "cost price of", "profit of",
                "margin of", "how much price", "price of dish", "menu cost", "pricing analysis",
                "what is the price", "dish cost price", "dish selling price", "profit margins list",
                "recipe pricing", "pricing strategy", "rate card", "food costing", "food cost percent",
                "cost of recipes", "selling rate", "cost rate", "profit rate", "dharalu", "vilava entha",
                "rate entha", "cost entha", "ammakam rate", "konalasinna rate", "labham", "nanshtam",
                "discount", "offer", "combo price", "gst", "tax", "final price", "net profit",
                "gross profit", "revenue", "income", "expense", "food cost %", "roi"
            ],
            Intent.EXPIRATION: [
                "expire", "expiry", "expired", "fresh", "spoilage", "spoil", "spoiled",
                "rotten", "expiring", "tomorrow", "expiring tomorrow", "expiring soon", "expiry alerts",
                "shelf life", "life cycle", "expiration date", "expiry date", "expired ingredients",
                "expiring items", "fridge expiration", "waste alert", "near expiry", "rotten items",
                "bad items", "stale food", "stale items", "freshness check", "shelf-life days",
                "expiring in", "days remaining", "expiry eppudu", "paipodhi", "padu aypothadhi",
                "migilipothe", "paadaipoyina", "expiry dates", "expiry check", "expired stock",
                "shelf life alert", "expiring this week", "expiring today", "expiration list", "expire date",
                "spoiled ingredients", "rotten vegetables", "bad meat", "waste food check", "how fresh is",
                "is it expired", "check expiration", "fridge expiry date", "pantry expiry", "when will it expire",
                "shelf life remaining", "expiration status", "spoiled status", "waste items list",
                "expiry dates report", "expiry tracker", "paadaipoye items", "dates expiry", "expired list",
                "expired today", "expires today", "next week", "this week", "waste", "discard", "throw away",
                "unsafe", "spoiled meat", "bad smell", "mold", "fungus"
            ],
            Intent.DASHBOARD: [
                "dashboard", "summary", "statistics", "overview", "report", "metrics",
                "status report", "general overview", "dashboard summary", "analytics summary",
                "kpi metrics", "kitchen summary", "store metrics", "total recipes count",
                "total ingredients count", "expired count", "recent entries", "operational summary",
                "overview metrics", "daily performance summary", "dashboard report", "summary sheet",
                "stats summary", "overall metrics", "summary statistics", "status report", "report details",
                "view dashboard", "show dashboard", "daily report summary", "analytics overview",
                "kitchen dashboard", "store overview", "dashboard count", "statistics count",
                "total items overview", "general report", "metrics dashboard", "kpi summary",
                "total count summary", "kitchen metrics summary", "general stats", "analytics report",
                "operations dashboard", "BOH report", "back of house report", "daily operations summary",
                "today report", "weekly report", "monthly report", "sales report", "inventory report",
                "purchase report", "summary report", "performance", "business health", "restaurant health",
                "operations"
            ],
            Intent.KNOWLEDGE: [
                "food safety", "safety", "storage", "store", "hygiene", "hygienic",
                "chef note", "chef notes", "pairing", "pairings", "substitution", "substitutions",
                "seasonal", "temperature", "temp", "haccp", "clean", "shelf", "first aid",
                "emergency", "fire", "leak", "injury", "bleeding", "handwash", "hand washing",
                "apron rules", "cutting boards", "cross contamination", "danger zone", "hot holding",
                "cooling rules", "thawing", "pest control", "chemical segregation", "sanitizer buckets",
                "dishwashing rules", "telugu months", "lunar calendar", "monsoon tips", "summer comfort food",
                "pasupu", "turmeric", "manta", "gollu", "juttu", "masam", "chaitram", "vaisakham", "jyeshtam",
                "aashadham", "shravanam", "bhadrapadam", "karthikam", "magham", "sankranti", "ugadi", "dasara",
                "safety rules", "storage rules", "how to store", "how to keep", "refrigeration temperature",
                "freezer temperature", "dry storage rules", "allergen safety", "cross-contact",
                "hand hygiene", "glove rules", "hairnet rules", "cleaning schedules", "chemical safety",
                "burn injury", "cut first aid", "fire safety", "gas leak first aid", "emergency contact numbers",
                "chef tips", "flavor pairings", "ingredient pairing", "alternative ingredients",
                "substitute for", "seasonal calendar", "seasonal tips", "winter dishes", "summer comfort food",
                "pasupu rasa", "juttu rali", "gollu kosi", "pasupu pettadam", "chaitram nunchi", "vaisakha masam",
                "boiling", "steaming", "grilling", "baking", "frying", "roasting", "smoking", "danger zone",
                "bacteria", "salmonella", "e coli", "food poisoning", "cross contamination", "freeze",
                "refrigerate", "deep freeze", "room temperature", "airtight container", "protein",
                "carbohydrates", "vitamins", "minerals", "fiber", "calories", "knife skills",
                "cutting techniques", "mise en place", "chef techniques", "kitchen hygiene"
            ],
            Intent.GENERAL_CHAT: [
                "hello", "hi", "hey", "thanks", "thank you", "who are you", "good morning",
                "good evening", "namaste", "how are you", "hola", "sup", "greet", "greetings",
                "alright", "alrighty", "ohh", "hurray", "knaww", "boss", "mama", "dude", "bro",
                "andi", "garu", "welcome", "my pleasure", "see you", "bye", "goodbye", "take care",
                "have a nice day", "how is it going", "what's up", "hey brother", "thank you so much",
                "many thanks", "great helper", "nice talking to you", "hi bot", "hello bot", "namaskaram",
                "namaste master", "heyy", "yoo", "yo", "morning", "evening", "night", "good night",
                "good afternoon", "good night", "how's everything", "how are things", "nice", "awesome",
                "excellent", "cool", "okay", "ok", "fine", "thank you very much", "appreciate it"
            ],
            Intent.SETTINGS: [
                "settings", "restaurant settings", "restaurant profile", "operating parameter",
                "operating parameters", "operating profile", "profile settings", "restaurant config",
                "restaurant configuration", "operating profile configuration", "working hours",
                "business name", "opening time", "closing time", "tax rate", "currency", "address"
            ]
        }
        
        # Define anchor queries for semantic fallback routing
        self.anchor_queries = {
            Intent.INVENTORY: ["show inventory levels", "what stock is available", "check ingredient count", "how much raw material is left", "whats in stock"],
            Intent.RECIPE: ["show available recipes", "cook a dish", "how do I prepare curry", "view recipes list", "available recipes catalog"],
            Intent.SUPPLIER: ["who is the supplier for tomatoes", "supplier email address", "contact details of vendor", "who supplies ingredients"],
            Intent.PRICING: ["price of chicken", "what is the profit margin of Chilli Chicken", "cost price and selling price", "recommend pricing for dish"],
            Intent.EXPIRATION: ["expired items", "which ingredients are expiring soon", "shelf life alerts", "expiring tomorrow list"],
            Intent.DASHBOARD: ["dashboard overview statistics", "today summary records", "show metrics overview", "daily restaurant status"],
            Intent.KNOWLEDGE: ["how should milk be stored", "food safety guidelines", "first aid for kitchen cuts", "hazard control instructions"],
            Intent.SETTINGS: ["what are the restaurant settings", "show restaurant profile settings", "restaurant operating parameters", "configuration parameters"],
            Intent.GENERAL_CHAT: ["hello how are you", "good morning", "thank you so much", "how is it going"]
        }
        
    def _get_anchor_embeddings(self):
        if IntentRouter._cached_anchor_embeddings is None:
            logger.info("IntentRouter: Lazily computing anchor embeddings for semantic fallback...")
            import time
            start_t = time.time()
            IntentRouter._cached_anchor_embeddings = {}
            try:
                embedder = EmbeddingEngine()
                for intent_cat, queries in self.anchor_queries.items():
                    IntentRouter._cached_anchor_embeddings[intent_cat] = [embedder.get_query_embedding(q) for q in queries]
                logger.info(f"IntentRouter: Anchor embeddings pre-computed successfully in {time.time() - start_t:.2f}s.")
            except Exception as e:
                logger.error(f"IntentRouter: Failed to pre-embed anchor queries: {str(e)}")
        return IntentRouter._cached_anchor_embeddings or {}

    def detect_intent(self, question: str) -> IntentResult:
        """
        Detects query intent and routing path based on keyword match density.
        Returns an IntentResult containing intent category, route path, and confidence score.
        """
        q_low = question.lower()
        
        # Clean query punctuation to avoid token matching failures
        q_clean = re.sub(r'[^\w\s]', ' ', q_low)
        
        best_intent = Intent.UNKNOWN
        best_route = Route.UNKNOWN
        best_score = 0
        matched_kws = []
        
        # 1. Search for co-occurrence of hybrid indicators (e.g. available + recipe)
        has_available_indicators = any(w in q_clean for w in ["available", "inventory", "stock", "today", "tomorrow", "iroju", "e roju", "eraju", "unna", "unnavati"])
        has_recipe_indicators = any(w in q_clean for w in ["recipe", "recipes", "menu", "dishes", "cook", "prepare", "vantalu", "vanta", "tayaru", "tayari", "vandadam", "vandali"])
        
        # Check if it is a simple catalog listing request
        is_catalog_query = any(w in q_clean for w in ["show all", "list all", "show me all", "list of all", "all recipes", "recipes list"])
        
        # Check explicit hybrid keywords first
        hybrid_matches = [kw for kw in self.keywords_map[Intent.HYBRID] if kw in q_clean]
        if (hybrid_matches or (has_available_indicators and has_recipe_indicators)) and not is_catalog_query:
            matched_kws = hybrid_matches if hybrid_matches else ["hybrid co-occurrence"]
            result = IntentResult(
                intent=Intent.HYBRID,
                route=Route.HYBRID,
                confidence=0.98 if hybrid_matches else 0.85,
                matched_keywords=matched_kws,
                reason="Query demands recipes/menus optimized by live database inventory availability."
            )
            logger.info(f"[INTENT_ROUTER] Query: '{question}' | Intent: HYBRID | Route: HYBRID | Confidence: {result.confidence}")
            return result
 
        # 2. Iterate through all other category keywords to count matches
        # We iterate in a specific priority order: RECIPE, EXPIRATION, PRICING, SUPPLIER, INVENTORY, DASHBOARD, KNOWLEDGE, GENERAL_CHAT
        priority_order = [
            Intent.RECIPE, Intent.EXPIRATION, Intent.PRICING, Intent.SUPPLIER,
            Intent.INVENTORY, Intent.DASHBOARD, Intent.KNOWLEDGE, Intent.GENERAL_CHAT
        ]
        
        for intent_cat in priority_order:
            kw_list = self.keywords_map.get(intent_cat, [])
            matches = []
            for kw in kw_list:
                # Use word boundaries for all keywords to prevent substring overlapping conflicts
                pattern = rf"\b{re.escape(kw)}\b"
                if re.search(pattern, q_clean):
                    matches.append(kw)
                        
            score = len(matches)
            if score > best_score:
                best_score = score
                best_intent = intent_cat
                matched_kws = matches
 
        # 3. Semantic fallback search if no keywords matched
        is_semantic_fallback = False
        best_semantic_score = 0.0
        if best_intent == Intent.UNKNOWN:
            anchor_embeddings = self._get_anchor_embeddings()
            if anchor_embeddings:
                try:
                    embedder = EmbeddingEngine()
                    query_vector = embedder.get_query_embedding(question)
                    best_semantic_score = -1.0
                    best_semantic_intent = Intent.UNKNOWN
                    
                    for intent_cat, vecs in anchor_embeddings.items():
                        for vec in vecs:
                            sim = float(np.dot(query_vector, vec))
                            if sim > best_semantic_score:
                                best_semantic_score = sim
                                best_semantic_intent = intent_cat
                                
                    # Semantic match threshold
                    if best_semantic_score >= 0.70:
                        best_intent = best_semantic_intent
                        is_semantic_fallback = True
                        matched_kws = [f"semantic-match ({best_semantic_score:.2f})"]
                except Exception as e:
                    logger.error(f"[INTENT_ROUTER] Semantic routing fallback failed: {str(e)}")

        # 4. Determine Route based on Intent
        if best_intent == Intent.INVENTORY:
            best_route = Route.SPRING_INVENTORY
            reason = "Query requests real-time stock levels, available units, or ingredient quantities."
        elif best_intent == Intent.RECIPE:
            best_route = Route.SPRING_RECIPES
            reason = "Query requests dynamic menu recipes or recipe catalog listings."
        elif best_intent == Intent.SUPPLIER:
            best_route = Route.SPRING_SUPPLIERS
            reason = "Query requests commercial supplier contacts, ratings, or delivery times."
        elif best_intent == Intent.PRICING:
            best_route = Route.SPRING_RECIPES
            reason = "Query requests pricing cost analysis or margins (using recipe metadata)."
        elif best_intent == Intent.EXPIRATION:
            best_route = Route.SPRING_EXPIRATION
            reason = "Query requests near-expiry ingredients or food shelf-life alerts."
        elif best_intent == Intent.DASHBOARD:
            best_route = Route.SPRING_DASHBOARD
            reason = "Query requests dashboard overview statistics, records summary, or metrics."
        elif best_intent == Intent.KNOWLEDGE:
            best_route = Route.PINECONE
            reason = "Query requests static culinary safety, storage guidelines, chef tips, or seasonal rules."
        elif best_intent == Intent.GENERAL_CHAT:
            best_route = Route.GEMINI_ONLY
            reason = "Query is a general greeting or non-operational casual chat."
        elif best_intent == Intent.SETTINGS:
            best_route = Route.SPRING_SETTINGS
            reason = "Query requests restaurant profile configurations, operating parameters, or settings."
        else:
            best_intent = Intent.UNKNOWN
            best_route = Route.HYBRID
            reason = "No matching keywords found. Defaulting to Hybrid route to maximize live data and knowledge base integration."

        # Calculate confidence based on keyword density or semantic similarity score
        if is_semantic_fallback:
            confidence = best_semantic_score
            reason += f" (Matched semantically with confidence {best_semantic_score:.2f})"
        elif best_intent == Intent.UNKNOWN:
            confidence = 0.50
        else:
            confidence = min(0.60 + (best_score * 0.15), 0.98)

        result = IntentResult(
            intent=best_intent,
            route=best_route,
            confidence=confidence,
            matched_keywords=matched_kws,
            reason=reason
        )
        logger.info(f"[INTENT_ROUTER] Query: '{question}' | Intent: {best_intent.value} | Route: {best_route.value} | Confidence: {confidence:.2f}")
        return result
