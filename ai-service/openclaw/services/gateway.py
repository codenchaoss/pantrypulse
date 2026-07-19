import httpx
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("app.openclaw")

class KitchenSyncGateway:
    """
    OpenClaw API Client Gateway.
    Funnels OpenClaw skill tool executions directly to the FastAPI backend AI microservice.
    """
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        import os
        # Overwrite default localhost URL dynamically in production or containers
        if base_url == "http://127.0.0.1:8000":
            env_url = os.environ.get("BACKEND_URL")
            if env_url:
                base_url = env_url
            else:
                port = os.environ.get("PORT")
                if port:
                    base_url = f"http://127.0.0.1:{port}"
        self.base_url = base_url

    def _post(self, endpoint: str, json_data: Any) -> Dict[str, Any]:
        """
        Helper method to send HTTP POST requests to FastAPI and unpack the ApiResponse data.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        logger.info(f"OpenClaw Gateway: POST {url}")
        
        try:
            with httpx.Client(timeout=45.0) as client:
                response = client.post(url, json=json_data)
                response.raise_for_status()
                
                resp_json = response.json()
                
                # Check for standard FastAPI ApiResponse wrapper
                if "data" in resp_json:
                    return resp_json["data"]
                return resp_json
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenClaw Gateway: HTTP Error {e.response.status_code} from {url}: {e.response.text}")
            raise RuntimeError(f"FastAPI service returned error code {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"OpenClaw Gateway: Network connection failed to {url}: {str(e)}")
            raise ConnectionError(f"Failed to connect to FastAPI backend at {url}. Make sure the server is running.")

    def trigger_recipe_recommendation(self, ingredients: List[str]) -> Dict[str, Any]:
        """
        Invokes Recipe Recommendation endpoint (POST /recipe).
        """
        payload = {"ingredients": ingredients}
        return self._post("/recipe", payload)

    def trigger_menu_generation(self, inventory: List[Dict[str, Any]], recipes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Invokes Daily Menu Generator endpoint (POST /menu).
        """
        payload = {"inventory": inventory}
        if recipes:
            payload["recipes"] = recipes
        return self._post("/menu", payload)

    def trigger_pricing_suggestions(self, dish: str, cost: float) -> Dict[str, Any]:
        """
        Invokes Profit Suggestion Engine endpoint (POST /pricing).
        """
        payload = {"dish": dish, "ingredient_cost": cost}
        return self._post("/pricing", payload)

    def trigger_description_generation(self, dishes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Invokes Menu Description Generator endpoint (POST /description).
        """
        payload = {"dishes": dishes}
        return self._post("/description", payload)

    def trigger_supplier_messaging(self, supplier_name: str, ingredient: str, qty: str, date: str) -> Dict[str, Any]:
        """
        Invokes Supplier Message Generator endpoint (POST /supplier).
        """
        payload = {
            "supplier_name": supplier_name,
            "ingredient": ingredient,
            "required_quantity": qty,
            "required_date": date
        }
        return self._post("/supplier", payload)

    def trigger_inventory_optimization(self, inventory: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Invokes Ingredient Usage Optimization Engine endpoint (POST /optimization).
        """
        payload = {"inventory": inventory}
        return self._post("/optimization", payload)
