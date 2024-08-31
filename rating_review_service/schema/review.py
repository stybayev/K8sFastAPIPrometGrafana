from pydantic import BaseModel, Field
from typing import Optional
from uuid import uuid4
from datetime import datetime


class Review(BaseModel):
    movie_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    text: str
    publication_date: datetime = Field(default_factory=datetime.utcnow)
    author: str
    rating: int | None = Field(None, ge=0, le=10)
    likes: int = 0
    dislikes: int = 0


class ReviewResponse(Review):
    id: str
