from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class Intent(str, Enum):
    GENERAL_CHAT = "GENERAL_CHAT"
    INVENTORY = "INVENTORY"
    RECIPE = "RECIPE"
    SUPPLIER = "SUPPLIER"
    PRICING = "PRICING"
    EXPIRATION = "EXPIRATION"
    DASHBOARD = "DASHBOARD"
    KNOWLEDGE = "KNOWLEDGE"
    HYBRID = "HYBRID"
    SETTINGS = "SETTINGS"
    UNKNOWN = "UNKNOWN"

class Route(str, Enum):
    GEMINI_ONLY = "GEMINI_ONLY"
    SPRING_INVENTORY = "SPRING_INVENTORY"
    SPRING_RECIPES = "SPRING_RECIPES"
    SPRING_SUPPLIERS = "SPRING_SUPPLIERS"
    SPRING_EXPIRATION = "SPRING_EXPIRATION"
    SPRING_DASHBOARD = "SPRING_DASHBOARD"
    SPRING_AI_INPUT = "SPRING_AI_INPUT"
    SPRING_SETTINGS = "SPRING_SETTINGS"
    PINECONE = "PINECONE"
    HYBRID = "HYBRID"
    UNKNOWN = "UNKNOWN"

class IntentResult(BaseModel):
    intent: Intent = Field(..., description="The detected query intent class")
    route: Route = Field(..., description="The determined target data routing path")
    confidence: float = Field(..., description="Confidence score from 0.0 to 1.0")
    matched_keywords: List[str] = Field(default_factory=list, description="Keywords matched in the user query")
    reason: str = Field(..., description="The logical explanation behind the routing decision")
