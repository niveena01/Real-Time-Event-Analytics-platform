from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class EventIngest(BaseModel):
    client_id: str = Field(..., example="client_app_1")
    event_type: str = Field(..., example="checkout")
    latency_ms: int = Field(..., example=120)
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class EventResponse(BaseModel):
    status: str
    event_id: str