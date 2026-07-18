from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AgentConfig(BaseModel):
    """Configuration structure for registering custom agents in OpenClaw."""
    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Display name of the agent")
    emoji: str = Field(..., description="Avatar emoji character")
    description: str = Field(..., description="Description of tasks owned by agent")
    workspace: str = Field(..., description="Subfolder workspace for context storage")

class GatewayState(BaseModel):
    """Holds active endpoint status metrics for OpenClaw Gateway connections."""
    base_url: str
    active: bool = Field(default=False)
    registered_skills: List[str] = Field(default_factory=list)

# =========================================================
# RECIPE SKILL SCHEMAS
# =========================================================
class RecipeSkillRequest(BaseModel):
    ingredients: List[str] = Field(..., min_length=1)

class RecipeRecommendationItem(BaseModel):
    recipe_id: str
    recipe_name: str
    description: str
    matched_ingredients: List[str]
    missing_ingredients: List[str]
    match_percentage: int
    preparation_time_minutes: int
    difficulty: str
    estimated_calories: int
    reason_for_recommendation: str
    confidence: float = 0.95

class RecipeSkillResponse(BaseModel):
    recipes: List[RecipeRecommendationItem]

# =========================================================
# MENU SKILL SCHEMAS
# =========================================================
class MenuInventoryItem(BaseModel):
    ingredient: str
    quantity: str
    expiry_days: int

class MenuSkillRequest(BaseModel):
    inventory: List[MenuInventoryItem] = Field(..., min_length=1)

class MenuSpecialItem(BaseModel):
    dish: str
    reason: str
    matched_inventory: List[str]
    missing_ingredients: List[str] = []
    estimated_profit: str
    priority: str
    preparation_time: int
    difficulty: str
    confidence: float

class MenuSkillResponse(BaseModel):
    special_menu: List[MenuSpecialItem]

# =========================================================
# PRICING SKILL SCHEMAS
# =========================================================
class PricingSkillRequest(BaseModel):
    dish: str
    ingredient_cost: float

class PricingSkillResponse(BaseModel):
    dish: str
    ingredient_cost: float
    recommended_price: int
    estimated_profit: int
    profit_margin: int
    pricing_strategy: str
    market_position: str
    price_confidence: int

# =========================================================
# DESCRIPTION SKILL SCHEMAS
# =========================================================
class DescriptionDishItem(BaseModel):
    dish: str
    category: Optional[str] = None

class DescriptionSkillRequest(BaseModel):
    dishes: List[DescriptionDishItem] = Field(..., min_length=1)

class DescriptionSkillItem(BaseModel):
    dish: str
    description: str
    tone: str
    language: str

class DescriptionSkillResponse(BaseModel):
    descriptions: List[DescriptionSkillItem]

# =========================================================
# SUPPLIER SKILL SCHEMAS
# =========================================================
class SupplierSkillRequest(BaseModel):
    supplier_name: Optional[str] = None
    ingredient: str
    required_quantity: str
    required_date: str
    ingredients: Optional[List[str]] = None
    restaurant_name: Optional[str] = "KitchenSync Bistro"
    contact_person: Optional[str] = "Kitchen Manager"
    supplier_email: Optional[str] = None
    supplier_phone: Optional[str] = None
    urgency_level: Optional[str] = "Normal"
    language_preference: Optional[str] = "English"

class SupplierSkillResponse(BaseModel):
    supplier_name: str
    ingredient: str
    message: str
    language: str
    subject: Optional[str] = None
    order_id: Optional[str] = None
    urgency: Optional[str] = None

# =========================================================
# OPTIMIZATION SKILL SCHEMAS
# =========================================================
class OptimizationInventoryItem(BaseModel):
    ingredient: str
    quantity: float
    unit: str
    expiry_days: int

class OptimizationSkillRequest(BaseModel):
    inventory: List[OptimizationInventoryItem] = Field(..., min_length=1)

class RecommendedDishItem(BaseModel):
    dish: str
    servings: int
    profit: int
    priority: str

class OptimizationUsageItem(BaseModel):
    ingredient: str
    used_quantity: float
    unit: str

class OptimizationRemainingItem(BaseModel):
    ingredient: str
    remaining_quantity: float
    unit: str

class OptimizationSkillResponse(BaseModel):
    recommended_dishes: List[RecommendedDishItem]
    inventory_usage: List[OptimizationUsageItem]
    estimated_revenue: int
    currency: str = "INR"
    waste_saved: Dict[str, Any]
    remaining_inventory: List[OptimizationRemainingItem]
    purchase_required: bool
    purchase_items: List[Dict[str, Any]] = []
    reason: str
    language: str
