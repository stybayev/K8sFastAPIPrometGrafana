from typing import List
from http import HTTPStatus
from fastapi import APIRouter, Depends, Path, HTTPException
from app.services.genres import GenreServiceABC
from app.models.genre import Genre, Genres
from app.models.base_model import SearchParams
from app.utils.dc_objects import PaginatedParams
from uuid import UUID

router = APIRouter()


@router.get("/{genre_id}", response_model=Genre)
async def get_genre(
        *,
        service: GenreServiceABC = Depends(),
        genre_id: UUID = Path(..., description="genre id")
) -> Genre or None:
    genre = await service.get_by_id(doc_id=genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="genre not found"
        )
    return genre


@router.get("/", response_model=List[Genres])
async def get_genres(
        *,
        service: GenreServiceABC = Depends(),
        page_size: int = PaginatedParams.page_size,
        page_number: int = PaginatedParams.page_number
) -> List[Genres]:
    genres = await service.get_genres(
        params=SearchParams(
            page_size=page_size,
            page_number=page_number
        )
    )
    return genres
