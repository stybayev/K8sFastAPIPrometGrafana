import orjson

from abc import ABC, abstractmethod
from hashlib import md5
from app.models.genre import Genre, Genres
from app.models.base_model import SearchParams
from uuid import UUID
from app.services.base import RepositoryElastic, RepositoryRedis
from typing import List


class GenreRepository(RepositoryElastic[Genre, Genres]):
    ...


class GenreCacheRepository(RepositoryRedis[Genre, Genres]):
    ...


class GenreServiceABC(ABC):
    @abstractmethod
    async def get_by_id(self, doc_id: UUID) -> Genre or None:
        ...

    @abstractmethod
    async def get_genres(
            self,
            params: SearchParams
    ) -> List[Genres]:
        ...


class GenreService(GenreServiceABC):
    def __init__(
            self,
            repository: GenreRepository,
            cache_repository: GenreCacheRepository
    ) -> None:
        self._repository = repository
        self.cache_repository = cache_repository

    async def get_by_id(self, doc_id: UUID) -> Genre or None:
        # Достаем из кеша
        entity = await self.cache_repository.find(doc_id=doc_id)
        # если нет в кеше достаем из БД
        if not entity:
            entity = await self._repository.find(doc_id=doc_id)
            if not entity:
                return None
            await self.cache_repository.put(entity=entity)
        return entity

    async def get_genres(
            self,
            params: SearchParams
    ) -> List[Genres] or []:
        # ищем данные в кеше
        param_hash = md5(orjson.dumps(dict(params))).hexdigest()
        cached_genres = await self.cache_repository.find_multy(
            param_hash=param_hash
        )
        if cached_genres:
            return cached_genres
        # если нет в кеше, ищем в БД
        genres = await self._repository.find_multy(
            params=params
        )
        # если фильмы нашлись, добавляем записи в кеш
        if genres:
            await self.cache_repository.put_multy(
                entities=genres,
                params=dict(params)
            )
        return genres
