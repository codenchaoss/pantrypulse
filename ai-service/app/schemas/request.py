from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Culinary or restaurant BOH question to ask KitchenSync AI")
    history: Optional[str] = Field(None, description="Optional conversation history context")

class RecipeRequest(BaseModel):
    ingredients: List[str] = Field(..., min_length=1, description="List of ingredients currently available")

class InventoryItem(BaseModel):
    ingredient: str = Field(..., min_length=1, description="Name of the ingredient")
    quantity: str = Field(..., min_length=1, description="Quantity in stock (e.g. 5kg, 10 units)")
    expiry_days: int = Field(..., ge=0, description="Remaining shelf life in days")

class MenuRequest(BaseModel):
    inventory: List[InventoryItem] = Field(..., min_length=1, description="List of expiring ingredients in inventory")
    recipes: Optional[List[str]] = Field(None, description="Optional list of recipe names from step 2 to build specials from")

class SupplierRequest(BaseModel):
    supplier_name: Optional[str] = Field(None, description="Name of the supplier")
    ingredient: str = Field(..., min_length=1, description="Ingredient name to replenish")
    required_quantity: str = Field(..., min_length=1, description="Replenishment quantity (e.g. 20 kg)")
    required_date: str = Field(..., min_length=1, description="Date/time required (e.g. Tomorrow)")
    ingredients: Optional[List[str]] = Field(None, description="Optional list of ingredients to support multi-item requests")
    restaurant_name: Optional[str] = Field("KitchenSync Bistro", description="Name of the restaurant sending the request")
    contact_person: Optional[str] = Field("Kitchen Manager", description="Name of the contact person/sender")
    supplier_email: Optional[str] = Field(None, description="Optional supplier email address")
    supplier_phone: Optional[str] = Field(None, description="Optional supplier phone number")
    urgency_level: Optional[str] = Field("Normal", description="Urgency level of the order (Normal | Urgent | Critical)")
    language_preference: Optional[str] = Field("English", description="Language preferred for drafting the request")

class DishItem(BaseModel):
    dish: str = Field(..., min_length=1, description="Name of the dish")
    category: Optional[str] = Field(None, description="Category of the dish (e.g. Main Course, Seafood)")

class DescriptionRequest(BaseModel):
    dishes: List[DishItem] = Field(..., min_length=1, description="List of dishes to generate descriptions for")

class PricingRequest(BaseModel):
    dish: str = Field(..., min_length=1, description="Name of the recipe dish")
    ingredient_cost: float = Field(..., ge=0.0, description="Estimated total cost of ingredients for this dish")

class OptimizationInventoryItem(BaseModel):
    ingredient: str = Field(..., min_length=1, description="Name of the ingredient")
    quantity: float = Field(..., ge=0.0, description="Numerical quantity in stock")
    unit: str = Field(..., min_length=1, description="Unit of measurement (e.g. kg, liters)")
    expiry_days: int = Field(..., ge=0, description="Days remaining until expiry")

class OptimizationRequest(BaseModel):
    inventory: List[OptimizationInventoryItem] = Field(..., min_length=1, description="List of inventory items to optimize")
