import dataclasses
import datetime
import functools
import logging
import os
import time
import typing

import psycopg2
import redis
import requests
from adapters.elasticsearch_loader import ElasticsearchLoader
from adapters.postgres_extractor import PostgresExtractor
from adapters.redis_state import RedisStorage, State
from backoff import backoff
from config import DBParams, ElasticParams, RedisParams
from connection import postgres_connection
from data_transform import DataTransform
from psycopg2.extensions import connection as _connection

# Максимальный размер выгружаемой пачки
FETCH_LIMIT = 100


@dataclasses.dataclass
class ModelInfo:
    state_name: str
    index_name: str
    pg_func: typing.Callable
    transform_func: typing.Callable


def load(
    state: State,
    elasticsearch_loader: ElasticsearchLoader,
    model_info: ModelInfo,
):
    """Процесс загрузки данных для фильмов."""
    last = state.get_state(model_info.state_name)
    last_modified = last["modified"] if last else None

    for batch in model_info.pg_func(
        last_modified=last_modified,
        fetch_limit=FETCH_LIMIT,
    ):
        prepared_batch = model_info.transform_func(rows=batch)
        elasticsearch_loader.save_batch(
            batch=prepared_batch, index_name=model_info.index_name
        )

    state.set_state(
        key=model_info.state_name,
        value={"modified": datetime.datetime.utcnow().isoformat()},
    )


def load_related_data(
    state: State,
    postgres_extractor: PostgresExtractor,
    elasticsearch_loader: ElasticsearchLoader,
    model_info: ModelInfo,
):
    """Процесс загрузки данных для связанных данных."""

    last_state = state.get_state(model_info.state_name)
    last_state_modified = last_state["modified"] if last_state else None

    for filmwork_ids in model_info.pg_func(
        last_modified=last_state_modified,
        fetch_limit=FETCH_LIMIT,
    ):
        filmwork_ids_list = [filmwork["film_work_id"] for filmwork in filmwork_ids]
        for batch in postgres_extractor.get_filmworks_by_ids(
            ids=filmwork_ids_list,
            fetch_limit=FETCH_LIMIT,
        ):
            prepared_batch = model_info.transform_func(rows=batch)
            elasticsearch_loader.save_batch(
                batch=prepared_batch, index_name=model_info.index_name
            )

    state.set_state(
        key=model_info.state_name,
        value={"modified": datetime.datetime.utcnow().isoformat()},
    )


def load_from_postgres_to_elasticsearch(
    pg_conn: _connection,
    session: requests.Session,
    redis_conn: redis.Redis,
):
    """Основной процесс загрузки данных из Postgres в Elasticsearch."""
    postgres_extractor = PostgresExtractor(connection=pg_conn)
    elasticsearch_loader = ElasticsearchLoader(params=ElasticParams(), session=session)
    redis_storage = RedisStorage(redis_adapter=redis_conn)
    state = State(storage=redis_storage)
    data_transform = DataTransform()

    loader = functools.partial(
        load,
        state=state,
        elasticsearch_loader=elasticsearch_loader,
    )
    related_loader = functools.partial(
        load_related_data,
        state=state,
        elasticsearch_loader=elasticsearch_loader,
        postgres_extractor=postgres_extractor,
    )

    loader(
        model_info=ModelInfo(
            index_name="movies",
            state_name="last_filmwork",
            pg_func=postgres_extractor.get_filmworks,
            transform_func=data_transform.filmwork_from_pg_to_elastic,
        ),
    )
    loader(
        model_info=ModelInfo(
            index_name="persons",
            state_name="last_person",
            pg_func=postgres_extractor.get_persons,
            transform_func=data_transform.person_from_pg_to_elastic,
        ),
    )
    loader(
        model_info=ModelInfo(
            index_name="genres",
            state_name="last_genre",
            pg_func=postgres_extractor.get_genres,
            transform_func=data_transform.genre_from_pg_to_elastic,
        ),
    )
    related_loader(
        model_info=ModelInfo(
            index_name="movies",
            state_name="last_person_filmwork",
            pg_func=postgres_extractor.get_changed_filmworks_by_persons,
            transform_func=data_transform.filmwork_from_pg_to_elastic,
        ),
    )
    related_loader(
        model_info=ModelInfo(
            index_name="movies",
            state_name="last_genre_filmwork",
            pg_func=postgres_extractor.get_changed_filmworks_by_genres,
            transform_func=data_transform.filmwork_from_pg_to_elastic,
        ),
    )


@backoff(
    exceptions=(
        redis.exceptions.ConnectionError,
        requests.exceptions.ConnectionError,
        psycopg2.OperationalError,
    ),
    border_sleep_time=10000,
)
def start():
    """Функция инициализации коннектов ко всей необходимой инфраструктуре и
    их передачи в главный процесс загрузки.
    """
    dbparams = DBParams()
    redis_params = RedisParams()
    with (
        postgres_connection(params=dbparams) as pg_conn,
        requests.Session() as session,
        redis.Redis(
            **redis_params.dict(),
            decode_responses=True,
        ) as redis_conn,
    ):
        load_from_postgres_to_elasticsearch(
            pg_conn=pg_conn,
            session=session,
            redis_conn=redis_conn,
        )


class ESIndexNotFoundException(Exception):
    pass


def check_index_exists(index_name: str):
    elastic_params = ElasticParams()

    response = requests.get(
        url=f"http://{elastic_params.url()}/{index_name}",
    )
    if response.status_code == 404:
        os.system(
            f"bash scripts/{index_name}.sh host={elastic_params.host} port={elastic_params.port}",
        )
        raise ESIndexNotFoundException


def main():
    """Главная функция для запуска всего ETL процесса."""
    while True:
        try:
            check_index_exists(index_name="movies")
            check_index_exists(index_name="persons")
            check_index_exists(index_name="genres")
            start()
        except ESIndexNotFoundException:
            logging.error("ES: No index")
        except requests.exceptions.ConnectionError:
            logging.error("ES: No connection")
        finally:
            sleep_timeout = 5
            logging.info(f"Next etl run in {sleep_timeout} seconds")
            time.sleep(sleep_timeout)


if __name__ == "__main__":
    main()
