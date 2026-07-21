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
            if route_result.route == Route.SPRING_INVENTORY:
                # Differentiate between live stock levels vs historical orders if history keyword matched
                if any(w in q_low for w in ["history", "order", "orders", "purchase history"]):
                    spring_calls.append("GET /api/historical-orders")
                    orders = await spring_client.get_historical_orders()
                    live_data = {"historical_orders": orders}
                else:
                    spring_calls.append("GET /api/inventory")
                    inv = await spring_client.get_inventory()
                    live_data = {"inventory": inv}
                    
            elif route_result.route == Route.SPRING_RECIPES:
                spring_calls.append("GET /api/recipes")
                res = await spring_client.get_recipes()
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
                sups = await spring_client.get_suppliers()
                live_data = {"suppliers": sups}
                
            elif route_result.route == Route.SPRING_EXPIRATION:
                spring_calls.append("GET /api/expiration/expiring")
                exp = await spring_client.get_expiring_items()
                live_data = {"expiring": exp}
                
            elif route_result.route == Route.SPRING_DASHBOARD:
                spring_calls.append("GET /api/dashboard/summary")
                dash = await spring_client.get_dashboard_summary()
                live_data = dash if isinstance(dash, dict) else {"summary": dash}
                
            elif route_result.route == Route.SPRING_AI_INPUT:
                spring_calls.append("GET /api/recommendation/ai-input")
                ai_in = await spring_client.get_ai_input()
                live_data = ai_in if isinstance(ai_in, dict) else {"items": ai_in}
                
            # 2. Route to Pinecone vector store semantic retrieval
            elif route_result.route == Route.PINECONE:
                pinecone_used = True
                try:
                    knowledge = await asyncio.to_thread(self.retriever.retrieve, question)
                except Exception as p_err:
                    logger.error(f"[CONTEXT_BUILDER] Pinecone query failed: {str(p_err)}")
                    knowledge = []
                    
            # 3. Route to Hybrid route (both Spring Inventory + Spring Recipes + Pinecone recipe/menu RAG search)
            elif route_result.route == Route.HYBRID:
                spring_calls.append("GET /api/inventory")
                spring_calls.append("GET /api/recipes")
                pinecone_used = True
                
                # Fetch all three sources concurrently
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

                async def fetch_rag():
                    try:
                        return await asyncio.to_thread(self.retriever.retrieve, question)
                    except Exception as p_err:
                        logger.error(f"[CONTEXT_BUILDER] Pinecone query failed in Hybrid route: {str(p_err)}")
                        return []

                inv_data, recipes_data, knowledge = await asyncio.gather(
                    fetch_inv(),
                    fetch_recipes(),
                    fetch_rag()
                )
                
                live_data = {
                    "inventory": inv_data,
                    "recipes": recipes_data
                }

            # 4. Handle default/unknown fallbacks
            else:
                pass
                
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
