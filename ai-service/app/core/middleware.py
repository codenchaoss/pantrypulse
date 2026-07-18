import uuid
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.api")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging requests, adding tracking ID, and measuring response latency.
    """
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        # Attach tracking ID to request state
        request.state.request_id = request_id
        
        start_time = time.time()
        logger.info(f"Request ID: {request_id} | Start: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time_ms = int((time.time() - start_time) * 1000)
            
            # Inject correlation headers in response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time-Ms"] = str(process_time_ms)
            
            logger.info(
                f"Request ID: {request_id} | Completed: {request.method} {request.url.path} "
                f"| Status: {response.status_code} | Processed in: {process_time_ms}ms"
            )
            return response
        except Exception as e:
            process_time_ms = int((time.time() - start_time) * 1000)
            logger.error(
                f"Request ID: {request_id} | Exception: {request.method} {request.url.path} "
                f"| Error: {str(e)} | Processed in: {process_time_ms}ms",
                exc_info=True
            )
            raise e
