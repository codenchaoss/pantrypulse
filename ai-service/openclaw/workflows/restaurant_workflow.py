import logging
from typing import List, Dict, Any, Optional
from openclaw.services.gateway import KitchenSyncGateway

logger = logging.getLogger("app.openclaw")

class RestaurantWorkflowOrchestrator:
    """
    OpenClaw Restaurant Workflow Orchestrator.
    Sequentially executes inventory optimization, recipe candidate recommendations,
    menu generation, pricing evaluations, menu descriptions, and supplier replenishment drafts.
    Guarantees zero downtime by wrapping microservice calls in try-except guards.
    """
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.gateway = KitchenSyncGateway(base_url=base_url)

    def execute_workflow(self, raw_inventory: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Runs the full BOH orchestration sequence using raw inventory items.
        """
        logger.info("OpenClaw Orchestrator: Starting Restaurant Workflow execution...")
        warnings = []
        
        # Initialize combined plan dictionary
        action_plan = {
            "optimization": None,
            "recipe": None,
            "menu": None,
            "pricing": [],
            "description": None,
            "supplier": [],
            "warnings": warnings,
            "workflow_status": "completed"
        }

        # =========================================================
        # STEP 1: Inventory Optimization
        # =========================================================
        logger.info("OpenClaw Orchestrator: Executing Step 1 - Inventory Optimization")
        try:
            opt_result = self.gateway.trigger_inventory_optimization(raw_inventory)
            action_plan["optimization"] = opt_result
        except Exception as e:
            logger.error(f"OpenClaw Orchestrator: Step 1 failed: {str(e)}")
            warnings.append(f"Inventory Optimization service failed: {str(e)}")
            action_plan["workflow_status"] = "partial_success"
            # Setup mock fallback optimization container
            opt_result = {"recommended_dishes": [], "purchase_required": False}

        # =========================================================
        # STEP 2: Recipe Recommendations
        # =========================================================
        logger.info("OpenClaw Orchestrator: Executing Step 2 - Recipe Recommendations")
        
        # Connect optimization output to recipe inputs: only recommend recipes matching used ingredients
        ingredients = []
        if opt_result and opt_result.get("inventory_usage"):
            ingredients = [
                item.get("ingredient")
                for item in opt_result.get("inventory_usage")
                if item.get("used_quantity", 0) > 0
            ]
        
        # Fallback to all raw ingredients if optimization failed/empty
        if not ingredients:
            ingredients = [item.get("ingredient") for item in raw_inventory if item.get("ingredient")]
            
        recipe_result = None
        if ingredients:
            try:
                recipe_result = self.gateway.trigger_recipe_recommendation(ingredients)
                action_plan["recipe"] = recipe_result
            except Exception as e:
                logger.error(f"OpenClaw Orchestrator: Step 2 failed: {str(e)}")
                warnings.append(f"Recipe Recommendation service failed: {str(e)}")
                action_plan["workflow_status"] = "partial_success"

        # =========================================================
        # STEP 3: Menu Generation
        # =========================================================
        logger.info("OpenClaw Orchestrator: Executing Step 3 - Menu Specials Generation")
        
        # Connect recipe recommendation names to menu generation target dishes
        recipes = []
        if recipe_result and recipe_result.get("recipes"):
            recipes = [r.get("recipe_name") for r in recipe_result.get("recipes") if r.get("recipe_name")]
            
        menu_items_input = []
        for item in raw_inventory:
            menu_items_input.append({
                "ingredient": item.get("ingredient"),
                "quantity": f"{item.get('quantity')} {item.get('unit')}",
                "expiry_days": item.get("expiry_days")
            })
            
        try:
            menu_result = self.gateway.trigger_menu_generation(menu_items_input, recipes=recipes)
            action_plan["menu"] = menu_result
        except Exception as e:
            logger.error(f"OpenClaw Orchestrator: Step 3 failed: {str(e)}")
            warnings.append(f"Menu Generation service failed: {str(e)}")
            action_plan["workflow_status"] = "partial_success"
            menu_result = {"special_menu": []}

        # =========================================================
        # STEP 4: Pricing Suggestions (Parallel Execution)
        # =========================================================
        logger.info("OpenClaw Orchestrator: Executing Step 4 - Pricing and Margins (Parallel)")
        specials = menu_result.get("special_menu", []) if menu_result else []
        pricing_results = []
        import concurrent.futures

        if specials:
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(5, len(specials))) as executor:
                futures = {
                    executor.submit(self.gateway.trigger_pricing_suggestions, spec.get("dish"), 150.0): spec.get("dish")
                    for spec in specials if spec.get("dish")
                }
                for future in concurrent.futures.as_completed(futures):
                    dish_name = futures[future]
                    try:
                        price_result = future.result()
                        pricing_results.append(price_result)
                    except Exception as e:
                        logger.error(f"OpenClaw Orchestrator: Pricing failed for '{dish_name}': {str(e)}")
                        warnings.append(f"Pricing failed for '{dish_name}': {str(e)}")
                        action_plan["workflow_status"] = "partial_success"
        action_plan["pricing"] = pricing_results

        # =========================================================
        # STEP 5: Descriptions Generation
        # =========================================================
        logger.info("OpenClaw Orchestrator: Executing Step 5 - Descriptions Generation")
        if specials:
            desc_input = [{"dish": spec.get("dish"), "category": "Main Course"} for spec in specials]
            try:
                desc_result = self.gateway.trigger_description_generation(desc_input)
                action_plan["description"] = desc_result
            except Exception as e:
                logger.error(f"OpenClaw Orchestrator: Step 5 failed: {str(e)}")
                warnings.append(f"Description Generation service failed: {str(e)}")
                action_plan["workflow_status"] = "partial_success"

        # =========================================================
        # STEP 6: Supplier Replenishment Messaging (Parallel Execution)
        # =========================================================
        logger.info("OpenClaw Orchestrator: Executing Step 6 - Supplier Messages Drafting (Parallel)")
        
        # Check optimization outputs: ONLY draft replenishment orders if optimization recommends purchase
        purchase_required = False
        purchase_items = []
        if opt_result:
            purchase_required = opt_result.get("purchase_required", False)
            purchase_items = opt_result.get("purchase_items", [])
            
        supplier_results = []
        
        if purchase_required and purchase_items:
            # Trigger supplier drafts in parallel for low-stock ingredients recommended for purchase
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(5, len(purchase_items))) as executor:
                futures = {
                    executor.submit(
                        self.gateway.trigger_supplier_messaging,
                        supplier_name="Fresh Foods Inc",
                        ingredient=item.get("ingredient"),
                        qty=item.get("required_quantity", "20 kg"),
                        date="Tomorrow"
                    ): item.get("ingredient")
                    for item in purchase_items if item.get("ingredient")
                }
                for future in concurrent.futures.as_completed(futures):
                    ing = futures[future]
                    try:
                        supplier_result = future.result()
                        supplier_results.append(supplier_result)
                    except Exception as e:
                        logger.error(f"OpenClaw Orchestrator: Supplier message failed for '{ing}': {str(e)}")
                        warnings.append(f"Supplier message failed for '{ing}': {str(e)}")
                        action_plan["workflow_status"] = "partial_success"
                    
        action_plan["supplier"] = supplier_results

        logger.info(f"OpenClaw Orchestrator: Workflow finished. Status: {action_plan['workflow_status']}")
        return action_plan
