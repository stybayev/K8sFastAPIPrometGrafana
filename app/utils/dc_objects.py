from fastapi import Query
from dataclasses import dataclass


@dataclass
class PaginatedParams:
    page_size: int = Query(10, ge=1, description="Pagination page size")
    page_number: int = Query(1, ge=1, description="Pagination page number")
