import time
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.models.intent_models import Intent, Route, IntentResult
from app.models.context_models import UnifiedContext
from app.services.spring_api import spring_client
from app.rag.retriever import KnowledgeRetriever

# Setup logger for Context Builder
logger = logging.getLogger("app.services.context_builder")

class ContextBuilder:
    """
    Data Aggregation & Context Merger Layer.
    Consumes intent routing decisions and orchestrates live Spring Boot REST fetches
    and Pinecone semantic vector retrievals to form one standardized UnifiedContext object.
    """

    def __init__(self):
        self.retriever = KnowledgeRetriever()

    async def build_context(self, question: str, route_result: IntentResult) -> UnifiedContext:
        """
        Asynchronously aggregates required BOH operational datasets based on Route decision.
        Handles failures and unauthorized endpoints gracefully to provide non-blocking fallbacks.
        """
        start_time = time.time()
        intent_val = route_result.intent.value
        route_val = route_result.route.value
        
        live_data = {}
        knowledge = []
        spring_calls = []
        pinecone_used = False
        
        q_low = question.lower()
        
        try:
            # 1. Route to correct Spring Boot APIs
            # 1. Route to correct Spring Boot APIs
            if route_result.route == Route.SPRING_INVENTORY:
                # Differentiate between live stock levels vs historical orders if history keyword matched
                pinecone_used = True
                async def fetch_rag():
                    try:
                        return await asyncio.to_thread(self.retriever.retrieve, question)
                    except Exception as p_err:
                        logger.error(f"[CONTEXT_BUILDER] Pinecone query failed: {str(p_err)}")
                        return []
                if any(w in q_low for w in ["history", "order", "orders", "purchase history"]):
                    spring_calls.append("GET /api/historical-orders")
                    async def fetch_orders():
                        return await spring_client.get_historical_orders()
                    orders, knowledge = await asyncio.gather(fetch_orders(), fetch_rag())
                    live_data = {"historical_orders": orders}
                else:
                    spring_calls.append("GET /api/inventory")
                    async def fetch_inv():
                        return await spring_client.get_inventory()
                    inv, knowledge = await asyncio.gather(fetch_inv(), fetch_rag())
                    live_data = {"inventory": inv}
                    
            elif route_result.route == Route.SPRING_RECIPES:
                spring_calls.append("GET /api/recipes")
                pinecone_used = True
                async def fetch_recipes():
                    return await spring_client.get_recipes()
                async def fetch_rag():
                    try:
                        return await asyncio.to_thread(self.retriever.retrieve, question)
                    except Exception as p_err:
                        logger.error(f"[CONTEXT_BUILDER] Pinecone query failed: {str(p_err)}")
                        return []
                res, knowledge = await asyncio.gather(fetch_recipes(), fetch_rag())
                # Parse Spring Boot Page<Recipe> paginated response structure if present
                if isinstance(res, dict) and "content" in res:
                    recipes_list = res.get("content", [])
                elif isinstance(res, list):
                    recipes_list = res
                else:
                    recipes_list = []
                live_data = {"recipes": recipes_list}
                
            elif route_result.route == Route.SPRING_SUPPLIERS:
                spring_calls.append("GET /api/suppliers")
                pinecone_used = True
                async def fetch_sups():
                    return await spring_client.get_suppliers()
                async def fetch_rag():
                    try:
                        return await asyncio.to_thread(self.retriever.retrieve, question)
                    except Exception as p_err:
                        logger.error(f"[CONTEXT_BUILDER] Pinecone query failed: {str(p_err)}")
                        return []
                sups, knowledge = await asyncio.gather(fetch_sups(), fetch_rag())
                live_data = {"suppliers": sups}
                
            elif route_result.route == Route.SPRING_EXPIRATION:
                spring_calls.extend(["GET /api/inventory", "GET /api/expiration/expiring"])
                pinecone_used = True
                async def fetch_inv():
                    try:
                        return await spring_client.get_inventory()
                    except Exception as s_err:
                        logger.error(f"[CONTEXT_BUILDER] Spring API failed for inventory in Expiration route: {str(s_err)}")
                        return []
                async def fetch_exp():
                    try:
                        return await spring_client.get_expiring_items()
                    except Exception as s_err:
                        logger.error(f"[CONTEXT_BUILDER] Spring API failed for expiring in Expiration route: {str(s_err)}")
                        return []
                async def fetch_rag():
                    try:
                        return await asyncio.to_thread(self.retriever.retrieve, question)
                    except Exception as p_err:
                        logger.error(f"[CONTEXT_BUILDER] Pinecone query failed: {str(p_err)}")
                        return []
                inv, exp, knowledge = await asyncio.gather(fetch_inv(), fetch_exp(), fetch_rag())
                live_data = {"inventory": inv, "expiring": exp}
                
            elif route_result.route == Route.SPRING_DASHBOARD:
                spring_calls.append("GET /api/dashboard/summary")
                pinecone_used = True
                async def fetch_dash():
                    return await spring_client.get_dashboard_summary()
                async def fetch_rag():
                    try:
                        return await asyncio.to_thread(self.retriever.retrieve, question)
                    except Exception as p_err:
                        logger.error(f"[CONTEXT_BUILDER] Pinecone query failed: {str(p_err)}")
                        return []
                dash, knowledge = await asyncio.gather(fetch_dash(), fetch_rag())
                live_data = dash if isinstance(dash, dict) else {"summary": dash}
                
            elif route_result.route == Route.SPRING_AI_INPUT:
                spring_calls.append("GET /api/recommendation/ai-input")
                pinecone_used = True
                async def fetch_ai():
                    return await spring_client.get_ai_input()
                async def fetch_rag():
                    try:
                        return await asyncio.to_thread(self.retriever.retrieve, question)
                    except Exception as p_err:
                        logger.error(f"[CONTEXT_BUILDER] Pinecone query failed: {str(p_err)}")
                        return []
                ai_in, knowledge = await asyncio.gather(fetch_ai(), fetch_rag())
                live_data = ai_in if isinstance(ai_in, dict) else {"items": ai_in}
                
            elif route_result.route == Route.SPRING_SETTINGS:
                spring_calls.append("GET /api/settings")
                pinecone_used = True
                async def fetch_settings():
                    return await spring_client.get_restaurant_settings()
                async def fetch_rag():
                    try:
                        return await asyncio.to_thread(self.retriever.retrieve, question)
                    except Exception as p_err:
                        logger.error(f"[CONTEXT_BUILDER] Pinecone query failed: {str(p_err)}")
                        return []
                settings_data, knowledge = await asyncio.gather(fetch_settings(), fetch_rag())
                live_data = {"settings": settings_data}
                
            # 2. Route to Pinecone vector store semantic retrieval
            elif route_result.route == Route.PINECONE:
                pinecone_used = True
                try:
                    knowledge = await asyncio.to_thread(self.retriever.retrieve, question)
                except Exception as p_err:
                    logger.error(f"[CONTEXT_BUILDER] Pinecone query failed: {str(p_err)}")
                    knowledge = []
                    
            elif route_result.route == Route.GEMINI_ONLY:
                # No live API calls or Pinecone RAG queries needed for general chat
                live_data = {}
                knowledge = []
                
            # 3. Route to Hybrid route (both Spring Inventory + Spring Recipes + Pinecone recipe/menu RAG search)
            elif route_result.route == Route.HYBRID:
                spring_calls.extend([
                    "GET /api/inventory",
                    "GET /api/recipes",
                    "GET /api/suppliers",
                    "GET /api/historical-orders",
                    "GET /api/expiration/expiring",
                    "GET /api/recommendation/ai-input",
                    "GET /api/dashboard/summary",
                    "GET /api/settings"
                ])
                pinecone_used = True
                
                async def fetch_inv():
                    try:
                        return await spring_client.get_inventory()
                    except Exception as s_err:
                        logger.error(f"[CONTEXT_BUILDER] Spring API failed for inventory in Hybrid route: {str(s_err)}")
                        return []

                async def fetch_recipes():
                    try:
                        res = await spring_client.get_recipes()
                        if isinstance(res, dict) and "content" in res:
                            return res["content"]
                        elif isinstance(res, list):
                            return res
                        return []
                    except Exception as s_err:
                        logger.error(f"[CONTEXT_BUILDER] Spring API failed for recipes in Hybrid route: {str(s_err)}")
                        return []

                async def fetch_suppliers():
                    try:
                        return await spring_client.get_suppliers()
                    except Exception as s_err:
                        logger.error(f"[CONTEXT_BUILDER] Spring API failed for suppliers in Hybrid route: {str(s_err)}")
                        return []

                async def fetch_orders():
                    try:
                        return await spring_client.get_historical_orders()
                    except Exception as s_err:
                        logger.error(f"[CONTEXT_BUILDER] Spring API failed for historical orders in Hybrid route: {str(s_err)}")
                        return []

                async def fetch_expiration():
                    try:
                        return await spring_client.get_expiring_items()
                    except Exception as s_err:
                        logger.error(f"[CONTEXT_BUILDER] Spring API failed for expiration in Hybrid route: {str(s_err)}")
                        return []

                async def fetch_ai_input():
                    try:
                        return await spring_client.get_ai_input()
                    except Exception as s_err:
                        logger.error(f"[CONTEXT_BUILDER] Spring API failed for AI input in Hybrid route: {str(s_err)}")
                        return {}

                async def fetch_dashboard():
                    try:
                        return await spring_client.get_dashboard_summary()
                    except Exception as s_err:
                        logger.error(f"[CONTEXT_BUILDER] Spring API failed for dashboard in Hybrid route: {str(s_err)}")
                        return {}

                async def fetch_settings():
                    try:
                        return await spring_client.get_restaurant_settings()
                    except Exception as s_err:
                        logger.error(f"[CONTEXT_BUILDER] Spring API failed for settings in Hybrid route: {str(s_err)}")
                        return {}

                async def fetch_rag():
                    try:
                        return await asyncio.to_thread(self.retriever.retrieve, question)
                    except Exception as p_err:
                        logger.error(f"[CONTEXT_BUILDER] Pinecone query failed in Hybrid route: {str(p_err)}")
                        return []

                inv_data, recipes_data, suppliers_data, orders_data, expiration_data, ai_input_data, dashboard_data, settings_data, knowledge = await asyncio.gather(
                    fetch_inv(),
                    fetch_recipes(),
                    fetch_suppliers(),
                    fetch_orders(),
                    fetch_expiration(),
                    fetch_ai_input(),
                    fetch_dashboard(),
                    fetch_settings(),
                    fetch_rag()
                )
                
                live_data = {
                    "inventory": inv_data,
                    "recipes": recipes_data,
                    "suppliers": suppliers_data,
                    "historical_orders": orders_data,
                    "expiring": expiration_data,
                    "expiringIngredients": ai_input_data.get("expiringIngredients") if isinstance(ai_input_data, dict) else None,
                    "candidateRecipes": ai_input_data.get("candidateRecipes") if isinstance(ai_input_data, dict) else None,
                    "totalIngredients": dashboard_data.get("totalIngredients", 0) if isinstance(dashboard_data, dict) else 0,
                    "totalRecipes": dashboard_data.get("totalRecipes", 0) if isinstance(dashboard_data, dict) else 0,
                    "lowStockItems": dashboard_data.get("lowStockItems", 0) if isinstance(dashboard_data, dict) else 0,
                    "expiringSoon": dashboard_data.get("expiringSoon", 0) if isinstance(dashboard_data, dict) else 0,
                    "expiredItems": dashboard_data.get("expiredItems", 0) if isinstance(dashboard_data, dict) else 0,
                    "settings": settings_data
                }

            # 4. Handle default/unknown fallbacks
            else:
                spring_calls.extend([
                    "GET /api/inventory",
                    "GET /api/recipes",
                    "GET /api/suppliers",
                    "GET /api/historical-orders",
                    "GET /api/expiration/expiring",
                    "GET /api/recommendation/ai-input",
                    "GET /api/dashboard/summary",
                    "GET /api/settings"
                ])
                pinecone_used = True
                
                async def fetch_inv():
                    try:
                        return await spring_client.get_inventory()
                    except Exception as s_err:
                        logger.error(f"[CONTEXT_BUILDER] Spring API failed for inventory in fallback route: {str(s_err)}")
                        return []

                async def fetch_recipes():
                    try:
                        res = await spring_client.get_recipes()
                        if isinstance(res, dict) and "content" in res:
                            return res["content"]
                        elif isinstance(res, list):
                            return res
                        return []
                    except Exception as s_err:
                        logger.error(f"[CONTEXT_BUILDER] Spring API failed for recipes in fallback route: {str(s_err)}")
                        return []

                async def fetch_suppliers():
                    try:
                        return await spring_client.get_suppliers()
                    except Exception as s_err:
                        logger.error(f"[CONTEXT_BUILDER] Spring API failed for suppliers in fallback route: {str(s_err)}")
                        return []

                async def fetch_orders():
                    try:
                        return await spring_client.get_historical_orders()
                    except Exception as s_err:
                        logger.error(f"[CONTEXT_BUILDER] Spring API failed for historical orders in fallback route: {str(s_err)}")
                        return []

                async def fetch_expiration():
                    try:
                        return await spring_client.get_expiring_items()
                    except Exception as s_err:
                        logger.error(f"[CONTEXT_BUILDER] Spring API failed for expiration in fallback route: {str(s_err)}")
                        return []

                async def fetch_ai_input():
                    try:
                        return await spring_client.get_ai_input()
                    except Exception as s_err:
                        logger.error(f"[CONTEXT_BUILDER] Spring API failed for AI input in fallback route: {str(s_err)}")
                        return {}

                async def fetch_dashboard():
                    try:
                        return await spring_client.get_dashboard_summary()
                    except Exception as s_err:
                        logger.error(f"[CONTEXT_BUILDER] Spring API failed for dashboard in fallback route: {str(s_err)}")
                        return {}

                async def fetch_settings():
                    try:
                        return await spring_client.get_restaurant_settings()
                    except Exception as s_err:
                        logger.error(f"[CONTEXT_BUILDER] Spring API failed for settings in fallback route: {str(s_err)}")
                        return {}

                async def fetch_rag():
                    try:
                        return await asyncio.to_thread(self.retriever.retrieve, question)
                    except Exception as p_err:
                        logger.error(f"[CONTEXT_BUILDER] Pinecone query failed in fallback route: {str(p_err)}")
                        return []

                inv_data, recipes_data, suppliers_data, orders_data, expiration_data, ai_input_data, dashboard_data, settings_data, knowledge = await asyncio.gather(
                    fetch_inv(),
                    fetch_recipes(),
                    fetch_suppliers(),
                    fetch_orders(),
                    fetch_expiration(),
                    fetch_ai_input(),
                    fetch_dashboard(),
                    fetch_settings(),
                    fetch_rag()
                )
                
                live_data = {
                    "inventory": inv_data,
                    "recipes": recipes_data,
                    "suppliers": suppliers_data,
                    "historical_orders": orders_data,
                    "expiring": expiration_data,
                    "expiringIngredients": ai_input_data.get("expiringIngredients") if isinstance(ai_input_data, dict) else None,
                    "candidateRecipes": ai_input_data.get("candidateRecipes") if isinstance(ai_input_data, dict) else None,
                    "totalIngredients": dashboard_data.get("totalIngredients", 0) if isinstance(dashboard_data, dict) else 0,
                    "totalRecipes": dashboard_data.get("totalRecipes", 0) if isinstance(dashboard_data, dict) else 0,
                    "lowStockItems": dashboard_data.get("lowStockItems", 0) if isinstance(dashboard_data, dict) else 0,
                    "expiringSoon": dashboard_data.get("expiringSoon", 0) if isinstance(dashboard_data, dict) else 0,
                    "expiredItems": dashboard_data.get("expiredItems", 0) if isinstance(dashboard_data, dict) else 0,
                    "settings": settings_data
                }
                
        except Exception as err:
            logger.error(f"[CONTEXT_BUILDER ERROR] Critical error during context aggregation: {str(err)}")
            
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Construct unified standardized metadata block
        from datetime import timezone
        metadata = {
            "spring_calls": spring_calls,
            "pinecone_used": pinecone_used,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latency_ms": latency_ms
        }
        
        context_result = UnifiedContext(
            intent=intent_val,
            route=route_val,
            live_data=live_data,
            knowledge=knowledge,
            metadata=metadata
        )
        
        logger.info(
            f"[CONTEXT_BUILDER] Context built | Route: {route_val} | "
            f"Spring Calls: {spring_calls} | RAG Chunks: {len(knowledge)} | Latency: {latency_ms}ms"
        )
        return context_result
