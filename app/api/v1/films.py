from typing import List
from http import HTTPStatus
from fastapi import APIRouter, Depends, Path, HTTPException, Query
from app.services.film import FilmServiceABC
from app.models.film import Film, Films
from app.models.base_model import SearchParams
from app.utils.dc_objects import PaginatedParams
from uuid import UUID
from fastapi_jwt_auth import AuthJWT

from auth.core.jwt import security_jwt

router = APIRouter()


@router.get("/{film_id}", response_model=Film)
async def get_film(
        *,
        authorize: AuthJWT = Depends(),
        user: dict = Depends(security_jwt),
        service: FilmServiceABC = Depends(),
        film_id: UUID = Path(..., description="film id")
) -> Film or None:
    film = await service.get_by_id(doc_id=film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="film not found"
        )
    return film


@router.get("/", response_model=List[Films])
async def get_films(
        *,
        service: FilmServiceABC = Depends(),
        sort: str | None = "-imdb_rating",
        genre: str | None = Query(None, description="Filter by Genre"),
        page_size: int = PaginatedParams.page_size,
        page_number: int = PaginatedParams.page_number
) -> List[Films]:
    films = await service.get_films(
        params=SearchParams(
            sort=sort,
            genre=genre,
            page_size=page_size,
            page_number=page_number
        )
    )
    return films


@router.get("/search/", response_model=List[Films])
async def search_films(
        *,
        service: FilmServiceABC = Depends(),
        query: str,
        page_size: int = PaginatedParams.page_size,
        page_number: int = PaginatedParams.page_number
) -> List[Films] or []:
    films = await service.get_films(
        params=SearchParams(
            query=query,
            page_size=page_size,
            page_number=page_number
        )
    )
    return films
