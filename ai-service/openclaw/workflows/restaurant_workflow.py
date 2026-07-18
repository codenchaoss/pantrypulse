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
        # STEP 4: Pricing Suggestions
        # =========================================================
        logger.info("OpenClaw Orchestrator: Executing Step 4 - Pricing and Margins")
        specials = menu_result.get("special_menu", []) if menu_result else []
        pricing_results = []
        for spec in specials:
            dish_name = spec.get("dish")
            try:
                # Assume standard default cost of ₹150 for price suggest calculations
                price_result = self.gateway.trigger_pricing_suggestions(dish_name, 150.0)
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
        # STEP 6: Supplier Replenishment Messaging
        # =========================================================
        logger.info("OpenClaw Orchestrator: Executing Step 6 - Supplier Messages Drafting")
        
        # Check optimization outputs: ONLY draft replenishment orders if optimization recommends purchase
        purchase_required = False
        purchase_items = []
        if opt_result:
            purchase_required = opt_result.get("purchase_required", False)
            purchase_items = opt_result.get("purchase_items", [])
            
        supplier_results = []
        
        if purchase_required and purchase_items:
            # Trigger supplier drafts for low-stock ingredients recommended for purchase
            for item in purchase_items:
                ing = item.get("ingredient")
                qty = item.get("required_quantity", "20 kg")
                try:
                    supplier_result = self.gateway.trigger_supplier_messaging(
                        supplier_name="Fresh Foods Inc",
                        ingredient=ing,
                        qty=qty,
                        date="Tomorrow"
                    )
                    supplier_results.append(supplier_result)
                except Exception as e:
                    logger.error(f"OpenClaw Orchestrator: Supplier message failed for '{ing}': {str(e)}")
                    warnings.append(f"Supplier message failed for '{ing}': {str(e)}")
                    action_plan["workflow_status"] = "partial_success"
                    
        action_plan["supplier"] = supplier_results

        logger.info(f"OpenClaw Orchestrator: Workflow finished. Status: {action_plan['workflow_status']}")
        return action_plan
