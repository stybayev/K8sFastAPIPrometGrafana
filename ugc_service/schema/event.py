from pydantic import BaseModel, Field
from typing import Optional


class EventData(BaseModel):
    user_id: Optional[str] = Field(None, description="User ID")
    event_type: str = Field(..., description="Type of the event")
    timestamp: str = Field(..., description="Timestamp of the event")
    data: dict = Field(..., description="Event data")
    source: str = Field(..., description="Source of the event")
