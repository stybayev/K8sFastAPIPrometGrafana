from pydantic import BaseModel, Field
from typing import Dict, Any


class BaseEventData(BaseModel):
    event_type: str = Field(..., description="Type of the event")
    timestamp: str = Field(..., description="Timestamp of the event")
    data: Dict[str, Any] = Field(..., description="Additional data for the event")
    source: str = Field(..., description="Source of the event")


class EventData(BaseEventData):
    pass


class EventResponse(BaseEventData):
    user_id: str = Field(..., description="User ID")
