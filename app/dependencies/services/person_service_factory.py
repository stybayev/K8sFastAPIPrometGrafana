from functools import cache

from fastapi import Depends
from elasticsearch import AsyncElasticsearch
from redis import Redis
from app.db.elastic import get_elastic
from app.db.redis import get_redis
from app.dependencies.registrator import add_factory_to_mapper
from app.models.persons import Person, Persons
from app.models.film import Films, Film
from app.services.person import (PersonService, PersonServiceABC,
                                 PersonRepository, PersonCacheRepository)
from app.services.film import FilmRepository, FilmCacheRepository


@add_factory_to_mapper(PersonServiceABC)
@cache
def create_person_service(
        session: AsyncElasticsearch = Depends(get_elastic),
        redis_session: Redis = Depends(get_redis)
) -> PersonService:
    return PersonService(
        repository=PersonRepository(
            model=Person,
            paginated_model=Persons,
            elastic=session,
            index="persons"
        ),
        cache_repository=PersonCacheRepository(
            model=Person,
            paginated_model=Persons,
            redis=redis_session,
            index="persons"
        ),
        cache_repository_with_film=FilmCacheRepository(
            model=Film,
            paginated_model=Films,
            redis=redis_session,
            index="movies"
        ),
        repository_with_film=FilmRepository(
            model=Film,
            paginated_model=Films,
            elastic=session,
            index="movies"
        )
    )
