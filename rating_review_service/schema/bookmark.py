from pydantic import BaseModel, Field
from typing import List
from uuid import uuid4


class Bookmark(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    movie_id: str = Field(default_factory=lambda: str(uuid4()))


class BookmarkResponse(BaseModel):
    bookmark_id: str


class BookmarksListResponse(BaseModel):
    bookmarks: List[Bookmark]
