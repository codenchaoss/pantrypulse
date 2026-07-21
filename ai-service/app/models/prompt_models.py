from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class PromptObject(BaseModel):
    system_prompt: str = Field(..., description="System instructions and constraints for the LLM")
    user_prompt: str = Field(..., description="Formatted context and user query")
    intent: str = Field(..., description="The detected query intent")
    route: str = Field(..., description="The routing path")

class GeminiResponse(BaseModel):
    response: str = Field(..., description="The natural language generated response")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata with intent, route, latency, and status")
