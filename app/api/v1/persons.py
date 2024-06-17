from typing import List
from http import HTTPStatus
from fastapi import APIRouter, Depends, Path, HTTPException
from app.services.person import PersonServiceABC
from app.models.persons import Person, Persons
from app.models.film import Films
from app.models.base_model import SearchParams
from app.utils.dc_objects import PaginatedParams
from uuid import UUID

router = APIRouter()


@router.get("/{person_id}", response_model=Person)
async def get_person(
        *,
        service: PersonServiceABC = Depends(),
        person_id: UUID = Path(..., description="person id")
) -> Person or None:
    person = await service.get_by_id(doc_id=person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="person not found"
        )
    return person


@router.get("/", response_model=List[Persons])
async def get_persons(
        *,
        service: PersonServiceABC = Depends(),
        page_size: int = PaginatedParams.page_size,
        page_number: int = PaginatedParams.page_number
) -> List[Persons]:
    persons = await service.get_persons(
        params=SearchParams(
            page_size=page_size,
            page_number=page_number
        )
    )
    return persons


@router.get("/{person_id}/film", response_model=list[Films])
async def get_film_with_persons_by_id(
        *,
        service: PersonServiceABC = Depends(),
        person_id: UUID = Path(..., description="person's id"),
        page_size: int = PaginatedParams.page_size,
        page_number: int = PaginatedParams.page_number
) -> List[Films]:
    films = await service.get_films_with_person(
        params=SearchParams(
            person_id=person_id,
            page_size=page_size,
            page_number=page_number
        )
    )
    return films
