from typing import List
from http import HTTPStatus
from fastapi import APIRouter, Depends, Path, HTTPException
from app.services.person import PersonServiceABC
from app.models.persons import Person, Persons
from app.models.film import Films
from app.models.base_model import SearchParams
from app.utils.dc_objects import PaginatedParams
from uuid import UUID
from auth.core.jwt import security_jwt
from fastapi_jwt_auth import AuthJWT

router = APIRouter()


@router.get("/", response_model=List[Persons])
async def get_persons(
        *,
        authorize: AuthJWT = Depends(),
        user: dict = Depends(security_jwt),
        service: PersonServiceABC = Depends(),
        page_size: int = PaginatedParams.page_size,
        page_number: int = PaginatedParams.page_number
) -> List[Persons]:
    """
    ## Получение списка участников

    Этот эндпоинт позволяет получить список участников с возможностью пагинации.

    ### Параметры:
    - **page_size**: Количество участников на странице (по умолчанию: `10`).
    - **page_number**: Номер страницы (по умолчанию: `1`).

    ### Возвращает:
    - Список участников с информацией о каждом человеке.
    """
    persons = await service.get_persons(
        params=SearchParams(
            page_size=page_size,
            page_number=page_number
        )
    )
    return persons


@router.get("/{person_id}", response_model=Person)
async def get_person(
        *,
        authorize: AuthJWT = Depends(),
        user: dict = Depends(security_jwt),
        service: PersonServiceABC = Depends(),
        person_id: UUID = Path(..., description="person id")
) -> Person or None:
    """
    ## Получение информации об участнике

    Этот эндпоинт позволяет получить подробную информацию об участнике по его уникальному идентификатору.

    ### Параметры:
    - **person_id**: Уникальный идентификатор участника.

    ### Возвращает:
    - Объект участника с подробной информацией.
    - Если участник не найден, возвращает ошибку `404 Not Found`.
    """
    person = await service.get_by_id(doc_id=person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="person not found"
        )
    return person


@router.get("/{person_id}/film", response_model=list[Films])
async def get_film_with_persons_by_id(
        *,
        authorize: AuthJWT = Depends(),
        user: dict = Depends(security_jwt),
        service: PersonServiceABC = Depends(),
        person_id: UUID = Path(..., description="person's id"),
        page_size: int = PaginatedParams.page_size,
        page_number: int = PaginatedParams.page_number
) -> List[Films]:
    """
    ## Получение фильмов с участием персоны

    Этот эндпоинт позволяет получить список фильмов, в которых участвовал персона, по его уникальному идентификатору.

    ### Параметры:
    - **person_id**: Уникальный идентификатор персоны.
    - **page_size**: Количество фильмов на странице (по умолчанию: `10`).
    - **page_number**: Номер страницы (по умолчанию: `1`).

    ### Возвращает:
    - Список фильмов, в которых участвовал персона.
    """
    films = await service.get_films_with_person(
        params=SearchParams(
            person_id=person_id,
            page_size=page_size,
            page_number=page_number
        )
    )
    return films
