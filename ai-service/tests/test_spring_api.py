import unittest
import asyncio
from unittest.mock import patch, MagicMock
from app.services.spring_api import SpringApiClient

class TestSpringApiClient(unittest.TestCase):
    """
    Unit tests for SpringApiClient integration layer.
    """

    def setUp(self):
        self.client = SpringApiClient(base_url="https://pantrypulse-production-up.up.railway.app", timeout=5)

    def test_client_initialization(self):
        self.assertEqual(self.client.base_url, "https://pantrypulse-production-up.up.railway.app")
        self.assertEqual(self.client.timeout, 5)

    @patch("httpx.AsyncClient.get")
    def test_get_inventory_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"ingredient": "Chicken", "quantity": 15, "unit": "kg"},
            {"ingredient": "Rice", "quantity": 50, "unit": "kg"}
        ]
        
        async def run_test():
            mock_get.return_value = mock_response
            res = await self.client.get_inventory()
            self.assertEqual(len(res), 2)
            self.assertEqual(res[0]["ingredient"], "Chicken")

        asyncio.run(run_test())

    @patch("httpx.AsyncClient.get")
    def test_get_suppliers_graceful_error(self, mock_get):
        mock_get.side_effect = Exception("Connection refused")
        
        async def run_test():
            res = await self.client.get_suppliers()
            self.assertEqual(res, [])

        asyncio.run(run_test())

    @patch("httpx.Client.get")
    def test_get_inventory_sync_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"ingredient": "Tomatoes", "quantity": 10}]
        mock_get.return_value = mock_response

        res = self.client.get_inventory_sync()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["ingredient"], "Tomatoes")

    @patch("httpx.AsyncClient.get")
    def test_get_dashboard_summary_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "totalIngredients": 15,
            "totalRecipes": 35,
            "lowStockItems": 2
        }
        
        async def run_test():
            mock_get.return_value = mock_response
            res = await self.client.get_dashboard_summary()
            self.assertEqual(res["totalIngredients"], 15)
            self.assertEqual(res["lowStockItems"], 2)

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
