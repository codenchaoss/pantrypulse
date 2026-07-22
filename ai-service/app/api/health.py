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
    Checks structural availability of vector database indexes (Pinecone or local FAISS), 
    and checks communication with LLM provider endpoints.
    """
    logger.info("HealthController: Checking systems health...")
    
    vector_store_type = getattr(config, "VECTOR_STORE", "faiss").lower()
    
    if vector_store_type == "pinecone":
        # 1. Check Pinecone Cloud Index Health
        from app.services.pinecone_service import PineconeService
        pinecone_svc = PineconeService()
        pinecone_health = pinecone_svc.health_check()
        
        faiss_status = "deprecated"
        rag_status = "healthy" if (pinecone_health.get("status") == "healthy") else "unhealthy"
        logger.info(f"HealthController: Pinecone status is {rag_status}. Health stats: {pinecone_health}")
    else:
        # Check local FAISS & Metadata paths
        faiss_exists = os.path.exists(config.FAISS_INDEX_PATH)
        meta_json_exists = os.path.exists(config.FAISS_METADATA_JSON_PATH)
        meta_pkl_exists = os.path.exists(config.FAISS_METADATA_PATH)
        
        faiss_status = "healthy" if faiss_exists else "unhealthy"
        rag_status = "healthy" if (meta_json_exists or meta_pkl_exists) else "unhealthy"
        logger.info(f"HealthController: FAISS status is {faiss_status}, RAG status is {rag_status}")
    
    # 2. Check all LLM Providers via HealthMonitor
    monitor = HealthMonitor()
    provider_report = monitor.get_status_report()
    
    gemini_status = provider_report.get("gemini", {}).get("status", "unhealthy")
    openrouter_status = provider_report.get("openrouter", {}).get("status", "unhealthy")
    
    # 3. Determine active provider & fallback availability
    active_provider = "RAG-only Fallback"
    for name in monitor.registry.priority_order:
        p_status = provider_report.get(name, {}).get("status", "unhealthy")
        if p_status == "healthy":
            active_provider = name
            break
            
    fallback_available = False
    for name in monitor.registry.priority_order[1:]:
        p_status = provider_report.get(name, {}).get("status", "unhealthy")
        if p_status == "healthy":
            fallback_available = True
            break
            
    # 4. Overall Health Status Decision
    overall_status = "healthy"
    if rag_status == "unhealthy":
        overall_status = "unhealthy"
    
    # If all configured LLM providers are offline/unhealthy, set overall status to unhealthy
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
