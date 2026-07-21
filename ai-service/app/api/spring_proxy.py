from fastapi import APIRouter, HTTPException
from app.services.spring_api import spring_client
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/api/proxy", tags=["Spring Boot Proxy"])

@router.get("/inventory")
async def proxy_inventory():
    try:
        data = await spring_client.get_inventory()
        return ApiResponse(success=True, data=data, message="Fetched live inventory from Spring Boot.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Spring Boot connection error: {str(e)}")

@router.get("/recipes")
async def proxy_recipes():
    try:
        data = await spring_client.get_recipes()
        return ApiResponse(success=True, data=data, message="Fetched live recipes from Spring Boot.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Spring Boot connection error: {str(e)}")

@router.get("/suppliers")
async def proxy_suppliers():
    try:
        data = await spring_client.get_suppliers()
        return ApiResponse(success=True, data=data, message="Fetched live suppliers from Spring Boot.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Spring Boot connection error: {str(e)}")

@router.get("/historical-orders")
async def proxy_historical_orders():
    try:
        data = await spring_client.get_historical_orders()
        return ApiResponse(success=True, data=data, message="Fetched live historical orders from Spring Boot.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Spring Boot connection error: {str(e)}")

@router.get("/expiration")
async def proxy_expiration():
    try:
        data = await spring_client.get_expiring_items()
        return ApiResponse(success=True, data=data, message="Fetched live expiring items from Spring Boot.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Spring Boot connection error: {str(e)}")

@router.get("/ai-input")
async def proxy_ai_input():
    try:
        data = await spring_client.get_ai_input()
        return ApiResponse(success=True, data=data, message="Fetched live AI recommendation inputs from Spring Boot.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Spring Boot connection error: {str(e)}")

@router.get("/dashboard")
async def proxy_dashboard():
    try:
        data = await spring_client.get_dashboard_summary()
        return ApiResponse(success=True, data=data, message="Fetched live dashboard summary from Spring Boot.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Spring Boot connection error: {str(e)}")

@router.get("/settings")
async def proxy_settings():
    try:
        data = await spring_client.get_restaurant_settings()
        return ApiResponse(success=True, data=data, message="Fetched live restaurant settings from Spring Boot.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Spring Boot connection error: {str(e)}")
