import orjson

from abc import ABC, abstractmethod
from hashlib import md5
from app.models.persons import Persons, Person
from app.models.film import Films
from app.services.film import FilmCacheRepository, FilmRepository
from app.models.base_model import SearchParams
from uuid import UUID
from app.services.base import RepositoryElastic, RepositoryRedis
from typing import List


class PersonRepository(RepositoryElastic[Person, Persons]):
    ...


class PersonCacheRepository(RepositoryRedis[Person, Persons]):
    ...


class PersonServiceABC(ABC):
    @abstractmethod
    async def get_by_id(self, doc_id: UUID) -> Person or None:
        ...

    @abstractmethod
    async def get_persons(
            self,
            params: SearchParams
    ) -> List[Persons]:
        ...

    @abstractmethod
    async def get_films_with_person(
            self,
            params: SearchParams
    ) -> List[Films]:
        ...


class PersonService(PersonServiceABC):
    def __init__(
            self,
            repository: PersonRepository,
            cache_repository: PersonCacheRepository,
            repository_with_film: FilmRepository,
            cache_repository_with_film: FilmCacheRepository
    ) -> None:
        self._repository = repository
        self.cache_repository = cache_repository
        self.repository_with_film = repository_with_film
        self.cache_repository_with_film = cache_repository_with_film

    async def get_by_id(self, doc_id: UUID) -> Person or None:
        # Достаем из кеша
        entity = await self.cache_repository.find(doc_id=doc_id)
        # если нет в кеше достаем из БД
        if not entity:
            entity = await self._repository.find(doc_id=doc_id)
            if not entity:
                return None
            await self.cache_repository.put(entity=entity)
        return entity

    async def get_persons(
            self,
            params: SearchParams
    ) -> List[Persons] or []:
        # ищем данные в кеше
        param_hash = md5(orjson.dumps(dict(params))).hexdigest()
        cached_persons = await self.cache_repository.find_multy(
            param_hash=param_hash
        )
        if cached_persons:
            return cached_persons
        # если нет в кеше, ищем в БД
        persons = await self._repository.find_multy(
            params=params
        )
        # если персоны нашлись, добавляем записи в кеш
        if persons:
            await self.cache_repository.put_multy(
                entities=persons,
                params=dict(params)
            )
        return persons

    async def get_films_with_person(
            self,
            params: SearchParams
    ) -> List[Films] or []:
        param_hash = md5(orjson.dumps(dict(params))).hexdigest()
        cached_films = await self.cache_repository_with_film.find_multy(
            param_hash=param_hash
        )
        if cached_films:
            return cached_films
        films = await self.repository_with_film.find_multy(
            params=params
        )
        if films:
            await self.cache_repository_with_film.put_multy(
                entities=films,
                params=dict(params)
            )
        return films

