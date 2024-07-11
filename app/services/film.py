from http import HTTPStatus
from fastapi import HTTPException

import orjson

from abc import ABC, abstractmethod
from hashlib import md5
from app.models.film import Film, Films
from app.models.base_model import SearchParams
from uuid import UUID
from app.services.base import RepositoryElastic, RepositoryRedis
from typing import List

from auth.services.tokens import TokenService


class FilmRepository(RepositoryElastic[Film, Films]):
    ...


class FilmCacheRepository(RepositoryRedis[Film, Films]):
    ...


class FilmServiceABC(ABC):
    @abstractmethod
    async def get_by_id(self, doc_id: UUID, user_roles: List[str]) -> Film or None:
        ...

    @abstractmethod
    async def get_films(
            self,
            params: SearchParams
    ) -> List[Films]:
        ...


class FilmService(FilmServiceABC):
    def __init__(
            self,
            repository: FilmRepository,
            cache_repository: FilmCacheRepository,
            token_service: TokenService
    ) -> None:
        self._repository = repository
        self.cache_repository = cache_repository
        self.token_service = token_service

    async def get_by_id(self, doc_id: UUID,
                        user_roles: List[str]) -> Film | None:
        """
        Функция получения фильма по его идентификатору
        :param doc_id: идентификатор фильма
        :return: модель типа Film
        """
        # достаем из кеша
        entity = await self.cache_repository.find(doc_id=doc_id)
        # если нет в кеше достаем из БД
        if not entity:
            entity = await self._repository.find(doc_id=doc_id)
            if not entity:
                return None
            # сохраняем запись в кеш
            await self.cache_repository.put(entity=entity)

        # проверяем права доступа
        if entity.label and entity.label not in user_roles:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail='You do not have the required permissions'
            )

        return entity

    async def get_films(
            self,
            params: SearchParams
    ) -> List[Films] or []:
        # ищем данные в кеше
        param_hash = md5(orjson.dumps(dict(params))).hexdigest()
        cached_films = await self.cache_repository.find_multy(
            param_hash=param_hash
        )
        if cached_films:
            return cached_films
        # если нет в кеше, ищем в БД
        films = await self._repository.find_multy(
            params=params
        )
        # если фильмы нашлись, добавляем записи в кеш
        if films:
            await self.cache_repository.put_multy(
                entities=films,
                params=dict(params)
            )
        return films
