from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class UnifiedContext(BaseModel):
    intent: str = Field(..., description="The detected query intent")
    route: str = Field(..., description="The routing path")
    live_data: Dict[str, Any] = Field(default_factory=dict, description="Live database JSON retrieved from Spring Boot")
    knowledge: List[Dict[str, Any]] = Field(default_factory=list, description="Culinary safety, storage, or menu knowledge retrieved from RAG")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution performance metrics and telemetry logging details")
