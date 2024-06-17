from app.models.base_model import BaseMixin, PaginatedParams
from typing import Optional


class Genre(BaseMixin):
    name: str
    description: Optional[str] = None


class Genres(Genre, PaginatedParams):
    pass
