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


class ReviewResponse(Review):
    id: str


class ReviewLike(BaseModel):
    review_id: str
    user_id: str
    like: bool  # True для лайка, False для дизлайка


class LikeDislikeResponse(BaseModel):
    review_id: str
    user_id: str
    like: bool
    message: str
