from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from fastapi import Query


class BaseMixin(BaseModel):
    id: UUID


class BaseFilm(BaseMixin):
    title: str
    imdb_rating: Optional[float] = Query(ge=1, le=10, description="Film rating")


class PaginatedParams(BaseModel):
    page_size: int = Query(ge=1, description="Pagination page size")
    page_number: int = Query(ge=1, description="Pagination page number")


class SearchParams(PaginatedParams):
    genre: Optional[str]
    sort: Optional[str]
    query: Optional[str]
    person_id: Optional[UUID]
