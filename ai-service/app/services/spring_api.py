import time
import logging
from typing import Dict, Any, List, Optional
import httpx

from app.core import config

# Setup dedicated logger for Spring Boot Integration Layer
logger = logging.getLogger("app.services.spring_api")

class SpringApiClient:
    """
    Spring Boot Integration Layer Client.
    Provides async and sync REST methods to fetch real-time restaurant business data
    (Inventory, Recipes, Suppliers, Orders, Expiration, Settings, AI Inputs)
    from the Spring Boot backend microservice.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None, auth_token: Optional[str] = None):
        self.base_url = (base_url or config.SPRING_API_BASE_URL).rstrip("/")
        self.timeout = timeout or config.SPRING_API_TIMEOUT
        self.auth_token = auth_token if auth_token is not None else config.SPRING_API_AUTH_TOKEN
        logger.info(f"SpringApiClient initialized | Base URL: {self.base_url} | Timeout: {self.timeout}s | Auth Configured: {bool(self.auth_token)}")

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.auth_token:
            if self.auth_token.startswith("Bearer ") or self.auth_token.startswith("Basic "):
                headers["Authorization"] = self.auth_token
            else:
                headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    async def _request_async(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Internal helper method to execute async HTTP GET requests with telemetry logging and error handling.
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        headers = self._get_headers()
        
        try:
            async with httpx.AsyncClient(timeout=float(self.timeout), follow_redirects=True, headers=headers) as client:
                response = await client.get(url, params=params)
                latency_ms = int((time.time() - start_time) * 1000)
                
                if response.status_code == 200:
                    logger.info(f"[SPRING_API SUCCESS] GET {endpoint} | Status: 200 | Latency: {latency_ms}ms")
                    try:
                        return response.json()
                    except Exception as parse_err:
                        logger.error(f"[SPRING_API PARSE_ERR] GET {endpoint} | Invalid JSON payload: {str(parse_err)}")
                        return []
                else:
                    logger.warning(
                        f"[SPRING_API WARN] GET {endpoint} | Status: {response.status_code} | Latency: {latency_ms}ms"
                    )
                    return []
                    
        except httpx.TimeoutException:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"[SPRING_API TIMEOUT] GET {endpoint} timed out after {self.timeout}s (Latency: {latency_ms}ms)")
            return []
        except httpx.RequestError as req_err:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"[SPRING_API REQ_ERR] GET {endpoint} failed: {str(req_err)} (Latency: {latency_ms}ms)")
            return []
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"[SPRING_API UNEXPECTED_ERR] GET {endpoint}: {str(e)} (Latency: {latency_ms}ms)")
            return []

    # =========================================================================
    # Async Endpoints (Primary REST Interfaces)
    # =========================================================================

    async def get_inventory(self) -> List[Dict[str, Any]]:
        """
        Fetches current real-time stock levels, units, and categories from Spring Boot (/api/inventory).
        """
        data = await self._request_async("/api/inventory")
        return data if isinstance(data, list) else data.get("data", []) if isinstance(data, dict) else []

    async def get_recipes(self) -> List[Dict[str, Any]]:
        """
        Fetches master recipe catalog and dish metadata from Spring Boot (/api/recipes).
        """
        data = await self._request_async("/api/recipes")
        return data if isinstance(data, list) else data.get("data", []) if isinstance(data, dict) else []

    async def get_suppliers(self) -> List[Dict[str, Any]]:
        """
        Fetches active commercial supplier contacts and delivery data from Spring Boot (/api/suppliers).
        """
        data = await self._request_async("/api/suppliers")
        return data if isinstance(data, list) else data.get("data", []) if isinstance(data, dict) else []

    async def get_historical_orders(self) -> List[Dict[str, Any]]:
        """
        Fetches historical restaurant order logs and sales metrics from Spring Boot (/api/historical-orders).
        """
        data = await self._request_async("/api/historical-orders")
        return data if isinstance(data, list) else data.get("data", []) if isinstance(data, dict) else []

    async def get_expiring_items(self) -> List[Dict[str, Any]]:
        """
        Fetches near-expiry ingredients and shelf-life alerts from Spring Boot (/api/expiration/expiring).
        """
        data = await self._request_async("/api/expiration/expiring")
        return data if isinstance(data, list) else data.get("data", []) if isinstance(data, dict) else []

    async def get_ai_input(self) -> Dict[str, Any]:
        """
        Fetches preprocessed AI-ready operational payloads from Spring Boot (/api/recommendation/ai-input).
        """
        data = await self._request_async("/api/recommendation/ai-input")
        return data if isinstance(data, dict) else {"items": data} if isinstance(data, list) else {}

    async def get_restaurant_settings(self) -> Dict[str, Any]:
        """
        Fetches restaurant profile, operating parameters, and settings from Spring Boot (/api/settings).
        """
        data = await self._request_async("/api/settings")
        if not data:
            data = await self._request_async("/api/settings/restaurant")
        return data if isinstance(data, dict) else {"settings": data} if isinstance(data, list) else {}

    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Fetches the restaurant dashboard metrics and summaries from Spring Boot (/api/dashboard/summary).
        """
        data = await self._request_async("/api/dashboard/summary")
        return data if isinstance(data, dict) else {"summary": data} if isinstance(data, list) else {}

    # =========================================================================
    # Synchronous Wrapper Methods (For Sync Callers)
    # =========================================================================

    def _request_sync(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        headers = self._get_headers()
        try:
            with httpx.Client(timeout=float(self.timeout), follow_redirects=True, headers=headers) as client:
                response = client.get(url, params=params)
                latency_ms = int((time.time() - start_time) * 1000)
                if response.status_code == 200:
                    logger.info(f"[SPRING_API SYNC SUCCESS] GET {endpoint} | Status: 200 | Latency: {latency_ms}ms")
                    return response.json()
                else:
                    logger.warning(f"[SPRING_API SYNC WARN] GET {endpoint} | Status: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"[SPRING_API SYNC ERR] GET {endpoint}: {str(e)}")
            return []

    def get_inventory_sync(self) -> List[Dict[str, Any]]:
        data = self._request_sync("/api/inventory")
        return data if isinstance(data, list) else data.get("data", []) if isinstance(data, dict) else []

    def get_recipes_sync(self) -> List[Dict[str, Any]]:
        data = self._request_sync("/api/recipes")
        return data if isinstance(data, list) else data.get("data", []) if isinstance(data, dict) else []

    def get_suppliers_sync(self) -> List[Dict[str, Any]]:
        data = self._request_sync("/api/suppliers")
        return data if isinstance(data, list) else data.get("data", []) if isinstance(data, dict) else []

    def get_historical_orders_sync(self) -> List[Dict[str, Any]]:
        data = self._request_sync("/api/historical-orders")
        return data if isinstance(data, list) else data.get("data", []) if isinstance(data, dict) else []

    def get_expiring_items_sync(self) -> List[Dict[str, Any]]:
        data = self._request_sync("/api/expiration/expiring")
        return data if isinstance(data, list) else data.get("data", []) if isinstance(data, dict) else []

    def get_ai_input_sync(self) -> Dict[str, Any]:
        data = self._request_sync("/api/recommendation/ai-input")
        return data if isinstance(data, dict) else {"items": data} if isinstance(data, list) else {}

    def get_restaurant_settings_sync(self) -> Dict[str, Any]:
        data = self._request_sync("/api/settings")
        if not data:
            data = self._request_sync("/api/settings/restaurant")
        return data if isinstance(data, dict) else {"settings": data} if isinstance(data, list) else {}

    def get_dashboard_summary_sync(self) -> Dict[str, Any]:
        data = self._request_sync("/api/dashboard/summary")
        return data if isinstance(data, dict) else {"summary": data} if isinstance(data, list) else {}


# Shared Global Client Instance
spring_client = SpringApiClient()
