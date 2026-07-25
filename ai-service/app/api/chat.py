import logging
from fastapi import APIRouter, Depends
from app.schemas.request import ChatRequest
from app.schemas.response import ApiResponse, ChatResponseData
from app.services.chatbot_service import ChatbotService

router = APIRouter()
logger = logging.getLogger("app.api")

def get_chatbot_service() -> ChatbotService:
    return ChatbotService()

@router.post("/chat", response_model=ApiResponse[ChatResponseData])
def chat(request: ChatRequest, service: ChatbotService = Depends(get_chatbot_service)):
    """
    Exposes conversational BOH operations. Receives question, invokes RAG, and returns solution.
    """
    logger.info(f"[TIMING 1: AiController.chat START] Question: '{request.question}' | History present: {bool(request.history)}")
    import time
    start = time.time()
    
    result = service.generate_response(request.question, request.history)
    
    elapsed = time.time() - start
    logger.info(f"[TIMING 1: AiController.chat END] Total elapsed: {elapsed:.3f}s")
    
    response_data = ChatResponseData(
        question=result.get("question", ""),
        language=result.get("language", ""),
        confidence=result.get("confidence", 0.95),
        answer=result.get("answer", ""),
        sources=result.get("sources", []),
        retrieved_chunks=result.get("retrieved_chunks", 0),
        provider=result.get("provider", ""),
        fallback_used=result.get("fallback_used", False),
        response_time_ms=result.get("response_time_ms", 0)
    )
    return ApiResponse(data=response_data)
