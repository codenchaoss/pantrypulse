import logging
from fastapi import APIRouter, Depends
from app.schemas.request import RecipeRequest
from app.schemas.response import ApiResponse, RecipeResponseData
from app.services.recipe_service import RecipeService

router = APIRouter()
logger = logging.getLogger("app.api")

_recipe_service_instance = None

def get_recipe_service() -> RecipeService:
    global _recipe_service_instance
    if _recipe_service_instance is None:
        _recipe_service_instance = RecipeService()
    return _recipe_service_instance

@router.post("/recipe", response_model=ApiResponse[RecipeResponseData])
def recommend_recipe(request: RecipeRequest, service: RecipeService = Depends(get_recipe_service)):
    """
    Exposes recipe recommendation. Receives available ingredients, optimizes usage, and suggests recipes.
    """
    logger.info(f"RecipeController: Received request for ingredients: {request.ingredients}")
    result = service.generate_recipe(request.ingredients)
    
    response_data = RecipeResponseData(
        recipes=result.get("recipes", [])
    )
    return ApiResponse(data=response_data)
