from functools import cache

from fastapi import Depends
from elasticsearch import AsyncElasticsearch
from redis import Redis
from app.db.elastic import get_elastic
from app.db.redis import get_redis
from app.dependencies.registrator import add_factory_to_mapper
from app.models.genre import Genre, Genres
from app.services.genres import (GenreService, GenreServiceABC,
                                 GenreRepository, GenreCacheRepository)


@add_factory_to_mapper(GenreServiceABC)
@cache
def create_genre_service(
    session: AsyncElasticsearch = Depends(get_elastic),
    redis_session: Redis = Depends(get_redis)
) -> GenreService:
    return GenreService(
        repository=GenreRepository(
            model=Genre,
            paginated_model=Genres,
            elastic=session,
            index="genres"
        ),
        cache_repository=GenreCacheRepository(
            model=Genre,
            paginated_model=Genres,
            redis=redis_session,
            index="genres"
        )
    )
