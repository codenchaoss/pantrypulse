import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, chat, recipe, menu, supplier, description, pricing, optimization, rebuild, spring_proxy
from openclaw.api import orchestrate
from openclaw.routes import application, workflow_completion
from app.core.middleware import RequestLoggingMiddleware
from app.schemas.response import ApiResponse

logger = logging.getLogger("app.api")

app = FastAPI(
    title="KitchenSync AI Service",
    description="Enterprise REST API microservice for restaurant Back-of-House (BOH) operations.",
    version="1.1",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)

# Register routers
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(recipe.router, tags=["Recipe"])
app.include_router(menu.router, tags=["Menu"])
app.include_router(supplier.router, tags=["Supplier"])
app.include_router(description.router, tags=["Description"])
app.include_router(pricing.router, tags=["Pricing"])
app.include_router(optimization.router, tags=["Optimization"])
app.include_router(orchestrate.router, tags=["Orchestration"])
app.include_router(application.router, tags=["Integration"])
app.include_router(workflow_completion.router, tags=["Operations"])
app.include_router(rebuild.router, tags=["Database Rebuild"])
app.include_router(spring_proxy.router, tags=["Spring Boot Proxy"])

@app.on_event("startup")
def startup_prewarm():
    logger.info("FastAPI Startup: Pre-warming AI microservices & singleton handles...")
    try:
        from app.api.recipe import get_recipe_service
        from app.api.menu import get_menu_service
        from app.api.optimization import get_optimizer_service
        get_recipe_service()
        get_menu_service()
        get_optimizer_service()
        logger.info("FastAPI Startup: AI microservices successfully pre-warmed.")
    except Exception as e:
        logger.error(f"FastAPI Startup: Pre-warming encountered notice: {str(e)}")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(f"Request ID: {request_id} | Validation failed: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ApiResponse(
            success=True,
            data={"errors": exc.errors()},
            message="Request parameters failed validation checks."
        ).model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"Request ID: {request_id} | Unhandled server exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiResponse(
            success=True,
            data={"error_details": str(exc)},
            message="An unexpected server error occurred."
        ).model_dump()
    )

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI Application Startup: Loading PantryPulse AI REST controller module, cache, fallback, typing, recipe, menu, description, optimization, orchestrator, validation, temperature, orchestrate_cache, schemas, type_resilience, greets, timeouts, fireworks, together, bugfixes, telugu and keys instances...")
    from app.core import config
    logger.info(f"Loaded config. Active Vector Store Type: {getattr(config, 'VECTOR_STORE', 'faiss')}")
    
    if getattr(config, "VECTOR_STORE", "faiss").lower() == "pinecone":
        from app.services.pinecone_service import PineconeService
        pinecone_svc = PineconeService()
        health = pinecone_svc.health_check()
        logger.info(f"FastAPI Startup: Pinecone healthcheck validation result: {health}")
    else:
        import os
        faiss_exists = os.path.exists(config.FAISS_INDEX_PATH)
        logger.info(f"FastAPI Startup: Local FAISS database file check. Present: {faiss_exists}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("FastAPI Application Shutdown: Cleaning connections...")
