import os
import logging
from fastapi import APIRouter
from app.core import config
from app.llm.health_monitor import HealthMonitor
from app.schemas.response import ApiResponse, HealthResponseData

router = APIRouter()
logger = logging.getLogger("app.api")

@router.get("/health", response_model=ApiResponse[HealthResponseData])
def check_health():
    """
    Checks structural availability of vector database indexes, configs, 
    and checks communication with LLM provider endpoints.
    """
    logger.info("HealthController: Checking systems health...")
    
    # 1. Check FAISS & Metadata paths
    faiss_exists = os.path.exists(config.FAISS_INDEX_PATH)
    meta_json_exists = os.path.exists(config.FAISS_METADATA_JSON_PATH)
    meta_pkl_exists = os.path.exists(config.FAISS_METADATA_PATH)
    
    faiss_status = "healthy" if faiss_exists else "unhealthy"
    rag_status = "healthy" if (meta_json_exists or meta_pkl_exists) else "unhealthy"
    
    # 2. Check all LLM Providers via HealthMonitor
    monitor = HealthMonitor()
    provider_report = monitor.check_all_providers()
    
    gemini_status = provider_report.get("gemini", {}).get("status", "unhealthy")
    openrouter_status = provider_report.get("openrouter", {}).get("status", "unhealthy")
    
    # 3. Determine active provider & fallback availability
    # The active provider is the highest priority healthy provider in the registry order
    active_provider = "RAG-only Fallback"
    for name in monitor.registry.priority_order:
        p_status = provider_report.get(name, {}).get("status", "unhealthy")
        if p_status == "healthy":
            active_provider = name
            break
            
    # Fallback is available if any provider other than the first healthy one is healthy,
    # or if we have at least one fallback configured and healthy
    fallback_available = False
    for name in monitor.registry.priority_order[1:]:
        p_status = provider_report.get(name, {}).get("status", "unhealthy")
        if p_status == "healthy":
            fallback_available = True
            break
            
    # Overall Status
    overall_status = "healthy"
    if faiss_status == "unhealthy" or rag_status == "unhealthy":
        overall_status = "unhealthy"
    
    # If all configured providers are offline, report unhealthy
    all_unhealthy = True
    for name in monitor.registry.priority_order:
        p_status = provider_report.get(name, {}).get("status", "unhealthy")
        if p_status == "healthy":
            all_unhealthy = False
            break
            
    if all_unhealthy:
        overall_status = "unhealthy"
        
    health_data = HealthResponseData(
        status=overall_status,
        rag=rag_status,
        faiss=faiss_status,
        gemini=gemini_status,
        openrouter=openrouter_status,
        version="1.1",
        providers=provider_report,
        active_provider=active_provider,
        fallback_available=fallback_available
    )
    
    message = "All core systems are operational." if overall_status == "healthy" else "One or more services are currently degraded."
    return ApiResponse(
        success=(overall_status == "healthy"),
        data=health_data,
        message=message
    )
