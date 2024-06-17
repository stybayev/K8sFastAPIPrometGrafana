import asyncio
from hashlib import md5

import orjson
import pytest
from tests.functional.utils.dc_objects import Params
from tests.functional.testdata.data import PARAMETERS


@pytest.mark.parametrize(
    'query_data, expected_answer',
    PARAMETERS['limit']
)
@pytest.mark.fixt_data('limit')
@pytest.mark.asyncio
async def test_search_limit(
        es_write_data,
        make_get_request,
        es_data: list[dict],
        query_data: dict,
        expected_answer: dict
) -> None:
    """
    Проверка, что поиск по названию фильма
    возвращает только первые 10 результатов
    :return:
    """
    # Загружаем данные в ES
    await es_write_data(es_data, 'movies')
    response = await make_get_request('films/search', query_data)

    # Проверяем ответ
    assert response.status == expected_answer['status']
    assert len(response.body) == expected_answer['length']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    PARAMETERS['validation']
)
@pytest.mark.fixt_data('validation')
@pytest.mark.asyncio
async def test_search_validation(
        es_write_data,
        make_get_request,
        es_data,
        query_data: dict,
        expected_answer: dict
) -> None:
    # Загружаем данные в ES
    await es_write_data(es_data, 'movies')
    response = await make_get_request('films/search', query_data)

    # Проверяем ответ
    assert response.status == expected_answer['status']
    assert len(response.body) == expected_answer['length']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    PARAMETERS['phrase']
)
@pytest.mark.fixt_data('phrase')
@pytest.mark.asyncio
async def test_search_phrase(
        es_write_data,
        make_get_request,
        es_data,
        query_data: dict,
        expected_answer: dict
) -> None:
    # Загружаем данные в ES
    await es_write_data(es_data, 'movies')
    response = await make_get_request('films/search', query_data)

    # Проверяем ответ
    assert response.status == expected_answer['status']
    assert len(response.body) == expected_answer['length']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    PARAMETERS['redis_search']
)
@pytest.mark.fixt_data('redis_search')
@pytest.mark.asyncio
async def test_search_with_redis_cache(
        es_write_data,
        make_get_request,
        redis_client,
        es_data: list[dict],
        query_data,
        expected_answer
) -> None:
    # Загружаем данные в ES
    await es_write_data(es_data, 'movies')

    # Первый запрос, который запишет данные в кэш
    response = await make_get_request('films/search', query_data)
    assert response.status == expected_answer['status']
    assert len(response.body) == expected_answer['length']

    # Даем время для записи в кэш
    await asyncio.sleep(1)

    # Создаем ключ для проверки кэша
    params = Params(query='Star', page_size=10, page_number=1)

    params_json = orjson.dumps(params)
    cache_key = md5(params_json).hexdigest()

    # Получаем данные из кэша по созданному ключу
    cached_data = await redis_client.get(f'movies:{cache_key}')
    assert cached_data is not None, 'Данные должны быть в кэше'

    # Повторный запрос, который должен извлечь данные из кэша
    response_cached = await make_get_request('films/search', query_data)
    assert response_cached.status == response.status
    assert response_cached.body == response.body

    # Проверка, что данные из кэша совпадают с первоначальными данными
    cached_films = orjson.loads(cached_data)
    assert len(cached_films) == expected_answer['length'], 'Количество фильмов из кэша должно совпадать'
