from pydantic import BaseModel, Field
from uuid import uuid4


class Bookmark(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    movie_id: str = Field(default_factory=lambda: str(uuid4()))
