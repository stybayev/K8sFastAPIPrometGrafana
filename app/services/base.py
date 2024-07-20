import os

import orjson
import logging

from abc import ABC, abstractmethod
from hashlib import md5
import requests
from pydantic import ValidationError

from app.models.base_model import PaginatedParams, BaseModel, SearchParams
from app.models.film import Film
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from typing import TypeVar, Type, Generic, NoReturn, List
from uuid import UUID
from redis.asyncio import Redis

ModelType = TypeVar("ModelType", bound=BaseModel)
PaginatedModel = TypeVar("PaginatedModel", bound=PaginatedParams)


class Repository(ABC):
    @abstractmethod
    async def find(self, *args, **kwargs):
        ...

    @abstractmethod
    async def put(self, *args, **kwargs):
        ...

    @abstractmethod
    async def put_multy(self, *args, **kwargs):
        ...

    @abstractmethod
    async def find_multy(self, *args, **kwargs):
        ...


class RepositoryElastic(Repository, Generic[ModelType, PaginatedModel]):
    def __init__(
            self,
            model: Type[ModelType],
            paginated_model: Type[PaginatedModel],
            elastic: AsyncElasticsearch,
            index: str
    ):
        self._model = model
        self.paginated_model = paginated_model
        self.elastic = elastic
        self.index = index

    async def find(self, doc_id: UUID) -> Type[ModelType] or None:
        try:
            doc = await self.elastic.get(
                index=self.index,
                id=str(doc_id)
            )
        except NotFoundError:
            return None
        short_name = doc["_source"].get("file")
        if short_name:
            r = requests.get(f"{os.getenv('FILE_SERVICE_URL')}/presigned-url/{short_name}")
            doc["_source"]["file"] = r.json()
        return self._model(**doc["_source"])

    async def put(self):
        pass

    async def put_multy(self):
        pass

    async def find_multy(
            self,
            params: SearchParams
    ) -> List[Type[PaginatedModel]]:
        query_body = self.generate_body(params=params)
        try:
            response = await self.elastic.search(
                index=self.index,
                body=query_body
            )
        except Exception as e:
            logging.error(f"Failed to fetch model from Elasticsearch: {e}")
            return []
        models = []
        entities = response["hits"]["hits"]
        for entity in entities:
            try:
                model = self.paginated_model(
                    **entity["_source"],
                    page_size=params.page_size,
                    page_number=params.page_number
                )
            except ValidationError as e:
                logging.error(f"Error validating model data: {e}")
                continue
            models.append(model)

        return models

    @staticmethod
    def generate_body(params: SearchParams) -> dict:
        offset = (params.page_number - 1) * params.page_size
        if params.query:
            query_body = {
                "query": {
                    "multi_match": {
                        "query": params.query,
                        "fields": ["title^5", "description"]
                    },
                },
                "from": offset,
                "size": params.page_size
            }
        elif params.person_id:
            query_body = {
                "query": {
                    "bool": {
                        "should": [
                            {
                                "nested": {
                                    "path": "actors",
                                    "query": {
                                        "term": {
                                            "actors.id": params.person_id
                                        }
                                    }
                                }
                            },
                            {
                                "nested": {
                                    "path": "director",
                                    "query": {
                                        "term": {
                                            "director.id": params.person_id
                                        }
                                    }
                                }
                            },
                            {
                                "nested": {
                                    "path": "writers",
                                    "query": {
                                        "term": {
                                            "writers.id": params.person_id
                                        }
                                    }
                                }
                            }
                        ]
                    }
                },
                "from": offset,
                "size": params.page_size
            }
        else:
            query_body = {
                "query": {
                    "match_all": {}
                },
                "sort": [],
                "from": offset,
                "size": params.page_size
            }

        # Фильтрация по жанру
        if params.genre:
            if "bool" not in query_body["query"]:
                query_body["query"] = {
                    "bool": {
                        "must": []
                    }
                }
            query_body["query"]["bool"]["must"].append({
                "match": {
                    "genre": params.genre
                }
            })

        # Сортировка
        if params.sort:
            order = "desc" if params.sort.startswith("-") else "asc"
            field_name = "imdb_rating" \
                if params.sort[1:] == (
                    "imdb_rating" or params.sort == "imdb_rating"
            ) \
                else params.sort[1:] if order == "desc" \
                else params.sort
            query_body["sort"].append({
                field_name: {"order": order}
            })
        return query_body


class RepositoryRedis(Repository, Generic[ModelType, PaginatedModel]):
    def __init__(
            self,
            model: Type[ModelType],
            paginated_model: Type[PaginatedModel],
            redis: Redis,
            index: str
    ):
        self._model = model
        self.paginated_model = paginated_model
        self.redis = redis
        self.index = index
        self.cache_timeout = 60 * 5  # 5 минут

    async def find(
            self,
            doc_id: UUID
    ) -> Type[ModelType] or None:
        """
        Поиск данных в кеше Redis по идентификатору ресурса
        :params doc_id: идентификатор ресурса
        :return: найденная модель или None в случае, если модель не найдена
        """
        data = await self.redis.get(f"{self.index}:{doc_id}")
        if not data:
            return None
        return self._model.parse_raw(data)

    async def put(self, entity: Type[ModelType]) -> NoReturn:
        """
        Запись данных в кеш Redis
        :params entity: модель для записи в кеш
        """
        await self.redis.set(
            f'{self.index}:{entity.id}',
            entity.json(),
            self.cache_timeout,
        )

    async def put_multy(self, entities: List[PaginatedModel], params: dict):
        entities = [entity.json() for entity in entities]
        data = orjson.dumps(entities)
        params = md5(orjson.dumps(params)).hexdigest()
        await self.redis.set(
            f"{self.index}:{params}",
            data,
            self.cache_timeout
        )

    async def find_multy(self, param_hash) -> List[PaginatedModel]:
        data = await self.redis.get(f"{self.index}:{param_hash}")
        if not data:
            return []
        data = orjson.loads(data)
        return [self.paginated_model(**orjson.loads(entity)) for entity in data]
