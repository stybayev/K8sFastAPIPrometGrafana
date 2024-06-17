import asyncio

import pytest
from tests.functional.testdata.data import PARAMETERS
from hashlib import md5
from tests.functional.utils.dc_objects import Params

import orjson


@pytest.mark.parametrize(
    'query_data, expected_answer',
    PARAMETERS['film_search']
)
@pytest.mark.fixt_data('film')
@pytest.mark.asyncio
async def test_get_film_by_id(
        es_write_data,
        make_get_request,
        es_data,
        query_data: dict,
        expected_answer: dict
) -> None:
    """
    Тест на поиск фильма по идентификатору. Проверяет также поиск несуществующего фильма.
    :param es_write_data: фикстура для записи данных в ES
    :param make_get_request: фикстура для формирования и отправки запроса
    :param es_data: фикстура генерации данных для последующего добавления в ES
    :param query_data: данные запроса
    :param expected_answer: данные ожидаемого ответа
    :return: None
    """
    # Загружаем данные в ES
    await es_write_data(es_data, 'movies')
    response = await make_get_request('films', query_data)
    # Проверяем ответ
    assert response.status == expected_answer['status']
    if 'id' in expected_answer:
        assert response.body['id'] == expected_answer['id']
    else:
        assert response.body['detail'] == expected_answer['answer']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    PARAMETERS['all_films']
)
@pytest.mark.fixt_data('all_films')
@pytest.mark.asyncio
async def test_get_all_films(
        es_write_data,
        make_get_request,
        es_data,
        query_data: dict,
        expected_answer: dict
) -> None:
    # Загружаем данные в ES
    await es_write_data(es_data, 'movies')
    response = await make_get_request('films', query_data)
    # Проверяем ответ
    assert response.status == expected_answer['status']
    assert len(response.body) == expected_answer['length']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    PARAMETERS['films_validation']
)
@pytest.mark.fixt_data('films_validation')
@pytest.mark.asyncio
async def test_validation_films(
        es_write_data,
        make_get_request,
        es_data,
        query_data: dict,
        expected_answer: dict
) -> None:
    """
    Тест на валидность всех данных
    """
    await es_write_data(es_data, 'movies')
    response = await make_get_request('films', query_data)
    # Проверяем ответ
    assert response.status == expected_answer['status']
    assert len(response.body) == expected_answer['length']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    PARAMETERS['redis_films']
)
@pytest.mark.fixt_data('redis_films')
@pytest.mark.asyncio
async def test_films_with_redis_cache(
        es_write_data,
        make_get_request,
        redis_client,
        es_data: list[dict],
        query_data,
        expected_answer
) -> None:
    """
    Тест поиск с учётом кеша в Redis на метод /film
    """
    await es_write_data(es_data, 'movies')
    # Первый запрос, который запишет данные в кэш
    response = await make_get_request('films', query_data)
    assert response.status == expected_answer['status']
    assert len(response.body) == expected_answer['length']

    # Даем время для записи в кэш
    await asyncio.sleep(1)

    # Создаем ключ для проверки кэша
    params = Params(
        genre=None,
        sort='-imdb_rating',
        page_size=10,
        page_number=1
    )

    params_json = orjson.dumps(params)
    cache_key = md5(params_json).hexdigest()

    # Получаем данные из кэша по созданному ключу
    cached_data = await redis_client.get(f'movies:{cache_key}')
    assert cached_data is not None, 'Данные должны быть в кэше'

    # Повторный запрос, который должен извлечь данные из кэша
    response_cached = await make_get_request('films', query_data)
    assert response_cached.status == response.status
    assert response_cached.body == response.body

    # Проверка, что данные из кэша совпадают с первоначальными данными
    cached_films = orjson.loads(cached_data)
    assert len(cached_films) == expected_answer['length'], 'Количество фильмов из кэша должно совпадать'


@pytest.mark.parametrize(
    'query_data, expected_answer',
    PARAMETERS['redis_films_id']
)
@pytest.mark.fixt_data('redis_films_id')
@pytest.mark.asyncio
async def test_film_id_with_redis_cache(
        es_write_data,
        make_get_request,
        redis_client,
        es_data: list[dict],
        query_data,
        expected_answer
) -> None:
    """
    Тест поиск с учётом кеша в Redis на метод /film{id}
    """
    await es_write_data(es_data, 'movies')
    # Первый запрос, который запишет данные в кэш
    response = await make_get_request('films', query_data)
    assert response.status == expected_answer['status']
    assert response.body['title'] == expected_answer['title']
    assert response.body['id'] == expected_answer['id']

    # Даем время для записи в кэш
    await asyncio.sleep(1)

    # Получаем данные из кэша по созданному ключу
    cached_data = await redis_client.get(f'movies:{query_data["id"]}')
    assert cached_data is not None, 'Данные должны быть в кэше'

    # Повторный запрос, который должен извлечь данные из кэша
    response_cached = await make_get_request('films', query_data)
    assert response_cached.status == response.status
    assert response_cached.body == response.body

