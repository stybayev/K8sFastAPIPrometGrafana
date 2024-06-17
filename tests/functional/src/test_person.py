import asyncio

import pytest
from orjson import orjson

from tests.functional.testdata.data import PARAMETERS
from tests.functional.utils.films_utils import get_es_data
from tests.functional.testdata.data import TEST_DATA_PERSON


@pytest.mark.parametrize(
    'query_data, expected_answer',
    PARAMETERS['limit_persons']
)
@pytest.mark.fixt_data('limit_person')
@pytest.mark.asyncio
async def test_person_limit(
        es_write_data,
        make_get_request,
        es_data: list[dict],
        query_data: dict,
        expected_answer: dict
) -> None:
    """
    Проверяем вывод всех персон
    :return:
    """
    # Загружаем данные в ES
    await es_write_data(es_data, 'persons')
    response = await make_get_request('persons', query_data)

    # Проверяем ответ
    assert response.status == expected_answer['status']
    assert len(response.body) == expected_answer['length']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    PARAMETERS['search_person']
)
@pytest.mark.fixt_data('person')
@pytest.mark.asyncio
async def test_search_person(
        es_write_data,
        make_get_request,
        es_data,
        query_data: dict,
        expected_answer: dict
) -> None:
    # Загружаем данные в ES
    await es_write_data(es_data, 'persons')
    response = await make_get_request('persons', query_data)
    # Проверяем ответ
    assert response.status == expected_answer['status']
    assert response.body == expected_answer['answer']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    PARAMETERS['person_validation']
)
@pytest.mark.fixt_data('person_validation')
@pytest.mark.asyncio
async def test_validation_person(
        es_write_data,
        make_get_request,
        es_data,
        query_data: dict,
        expected_answer: dict
) -> None:
    # Загружаем данные в ES
    await es_write_data(es_data, 'persons')
    response = await make_get_request('persons', query_data)
    # Проверяем ответ
    assert response.status == expected_answer['status']
    assert len(response.body) == expected_answer['length']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    PARAMETERS['person_films']
)
@pytest.mark.fixt_data('person_films')
@pytest.mark.asyncio
async def test_films_by_person(
        es_write_data,
        make_get_request,
        es_data,
        query_data: dict,
        expected_answer: dict
) -> None:
    await es_write_data(es_data, 'movies')
    data = get_es_data([TEST_DATA_PERSON], 'persons')
    await es_write_data(data, 'persons')


@pytest.mark.parametrize(
    'query_data, expected_answer',
    PARAMETERS['redis_person']
)
@pytest.mark.fixt_data('redis_person')
@pytest.mark.asyncio
async def test_person_with_redis_cache(
        es_write_data,
        make_get_request,
        redis_client,
        es_data: list[dict],
        query_data,
        expected_answer
) -> None:
    # Загружаем данные в ES
    await es_write_data(es_data, 'persons')

    # Первый запрос, который запишет данные в кэш
    response = await make_get_request('persons', query_data)
    assert response.status == expected_answer['status']
    assert response.body['full_name'] == expected_answer['full_name']
    assert response.body['id'] == expected_answer['id']

    # Даем время для записи в кэш
    await asyncio.sleep(1)

    # Получаем данные из кэша по созданному ключу
    cached_data = await redis_client.get(f"persons:{expected_answer['id']}")
    assert cached_data is not None, 'Данные должны быть в кэше'

    # Повторный запрос, который должен извлечь данные из кэша
    response_cached = await make_get_request('persons', query_data)
    assert response_cached.status == response.status
    assert response_cached.body == response.body

    # Проверка, что данные из кэша совпадают с первоначальными данными
    cached_genres = orjson.loads(cached_data)
    assert cached_genres['full_name'] == expected_answer['full_name']
    assert cached_genres['id'] == expected_answer['id']
