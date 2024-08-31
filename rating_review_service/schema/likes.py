from pydantic import BaseModel, Field
from uuid import uuid4


class Like(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    movie_id: str = Field(default_factory=lambda: str(uuid4()))
    rating: int = Field(..., ge=0, le=10)
