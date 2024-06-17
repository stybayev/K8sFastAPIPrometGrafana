import pytest
import asyncio
import orjson
from tests.functional.testdata.data import PARAMETERS


@pytest.mark.parametrize(
    'query_data, expected_answer',
    PARAMETERS['limit_genres']
)
@pytest.mark.fixt_data('limit_genre')
@pytest.mark.asyncio
async def test_genre_limit(
        es_write_data,
        make_get_request,
        es_data: list[dict],
        query_data: dict,
        expected_answer: dict
) -> None:
    """
    Тест на вывод всех жанров
    :return:
    """
    # Загружаем данные в ES
    await es_write_data(es_data, 'genres')
    response = await make_get_request('genres', query_data)

    # Проверяем ответ
    assert response.status == expected_answer['status']
    assert len(response.body) == expected_answer['length']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    PARAMETERS['search_genre']
)
@pytest.mark.fixt_data('genre')
@pytest.mark.asyncio
async def test_search_genre(
        es_write_data,
        make_get_request,
        es_data,
        query_data: dict,
        expected_answer: dict
) -> None:
    """
    Тест на поиск жанра по идентификатору,
    в том числе несуществующего жанра
    """
    # Загружаем данные в ES
    await es_write_data(es_data, 'genres')
    response = await make_get_request('genres', query_data)
    # Проверяем ответ
    if 'id' in expected_answer:
        assert response.status == expected_answer['status']
        assert response.body['name'] == expected_answer['name']
        assert response.body['id'] == expected_answer['id']
    else:
        assert response.body['detail'] == expected_answer['answer']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    PARAMETERS['genre_validation']
)
@pytest.mark.fixt_data('genre_validation')
@pytest.mark.asyncio
async def test_validation_genre(
        es_write_data,
        make_get_request,
        es_data,
        query_data: dict,
        expected_answer: dict
) -> None:
    """
    Тест на валидность всех данных
    """
    await es_write_data(es_data, 'genres')
    response = await make_get_request('genres', query_data)
    # Проверяем ответ
    assert response.status == expected_answer['status']
    assert len(response.body) == expected_answer['length']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    PARAMETERS['redis_genre']
)
@pytest.mark.fixt_data('redis_genre')
@pytest.mark.asyncio
async def test_genre_with_redis_cache(
        es_write_data,
        make_get_request,
        redis_client,
        es_data: list[dict],
        query_data,
        expected_answer
) -> None:
    # Загружаем данные в ES
    await es_write_data(es_data, 'genres')

    # Первый запрос, который запишет данные в кэш
    response = await make_get_request('genres', query_data)
    assert response.status == expected_answer['status']
    assert response.body['name'] == expected_answer['name']
    assert response.body['id'] == expected_answer['id']

    # Даем время для записи в кэш
    await asyncio.sleep(1)

    # Получаем данные из кэша по созданному ключу
    cached_data = await redis_client.get(f"genres:{expected_answer['id']}")
    assert cached_data is not None, 'Данные должны быть в кэше'

    # Повторный запрос, который должен извлечь данные из кэша
    response_cached = await make_get_request('genres', query_data)
    assert response_cached.status == response.status
    assert response_cached.body == response.body

    # Проверка, что данные из кэша совпадают с первоначальными данными
    cached_genres = orjson.loads(cached_data)
    assert cached_genres['name'] == expected_answer['name']
    assert cached_genres['id'] == expected_answer['id']

