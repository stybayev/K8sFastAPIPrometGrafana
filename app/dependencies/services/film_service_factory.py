from functools import cache

from fastapi import Depends
from elasticsearch import AsyncElasticsearch
from redis import Redis
from app.db.elastic import get_elastic
from app.db.redis import get_redis
from app.dependencies.registrator import add_factory_to_mapper
from app.models.film import Film, Films
from app.services.film import (FilmService, FilmRepository,
                               FilmServiceABC, FilmCacheRepository)


@add_factory_to_mapper(FilmServiceABC)
@cache
def create_film_service(
    session: AsyncElasticsearch = Depends(get_elastic),
    redis_session: Redis = Depends(get_redis)
) -> FilmService:
    return FilmService(
        repository=FilmRepository(
            model=Film,
            paginated_model=Films,
            elastic=session,
            index="movies"
        ),
        cache_repository=FilmCacheRepository(
            model=Film,
            paginated_model=Films,
            redis=redis_session,
            index="movies"
        )
    )
