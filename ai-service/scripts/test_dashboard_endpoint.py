import sys
import os
import asyncio

sys.path.insert(0, r"e:\TCWING_PRJ\ai-service")
from app.services.spring_api import SpringApiClient

async def test_dashboard():
    client = SpringApiClient()
    print("Sending request to GET /api/dashboard/summary ...")
    res = await client.get_dashboard_summary()
    print("\nResult payload:")
    print(res)

asyncio.run(test_dashboard())
