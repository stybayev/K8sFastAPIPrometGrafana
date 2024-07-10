from typing import List
from http import HTTPStatus
from fastapi import APIRouter, Depends, Path, HTTPException
from app.services.genres import GenreServiceABC
from app.models.genre import Genre, Genres
from app.models.base_model import SearchParams
from app.utils.dc_objects import PaginatedParams
from uuid import UUID

from auth.core.jwt import security_jwt
from fastapi_jwt_auth import AuthJWT

router = APIRouter()


@router.get("/", response_model=List[Genres])
async def get_genres(
        *,
        authorize: AuthJWT = Depends(),
        user: dict = Depends(security_jwt),
        service: GenreServiceABC = Depends(),
        page_size: int = PaginatedParams.page_size,
        page_number: int = PaginatedParams.page_number
) -> List[Genres]:
    """
    ## Получение списка жанров

    Этот эндпоинт позволяет получить список жанров с возможностью пагинации.

    ### Параметры:
    - **page_size**: Количество жанров на странице (по умолчанию: `10`).
    - **page_number**: Номер страницы (по умолчанию: `1`).

    ### Возвращает:
    - Список жанров с информацией о каждом жанре.
    """
    genres = await service.get_genres(
        params=SearchParams(
            page_size=page_size,
            page_number=page_number
        )
    )
    return genres


@router.get("/{genre_id}", response_model=Genre)
async def get_genre(
        *,
        authorize: AuthJWT = Depends(),
        user: dict = Depends(security_jwt),
        service: GenreServiceABC = Depends(),
        genre_id: UUID = Path(..., description="genre id")
) -> Genre or None:
    """
    ## Получение информации о жанре

    Этот эндпоинт позволяет получить подробную информацию о жанре по его уникальному идентификатору.

    ### Параметры:
    - **genre_id**: Уникальный идентификатор жанра.

    ### Возвращает:
    - Объект жанра с подробной информацией.
    - Если жанр не найден, возвращает ошибку `404 Not Found`.
    """
    genre = await service.get_by_id(doc_id=genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="genre not found"
        )
    return genre
