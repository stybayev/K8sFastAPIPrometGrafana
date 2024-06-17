from dataclasses import dataclass
from uuid import UUID
from multidict import CIMultiDictProxy


@dataclass
class Response:
    body: list[dict]
    header: CIMultiDictProxy[str]
    status: int


@dataclass
class Params:
    page_size: int
    page_number: int
    genre: str | None = None
    sort: str = None
    query: str | None = None
    person_id: UUID | None = None
