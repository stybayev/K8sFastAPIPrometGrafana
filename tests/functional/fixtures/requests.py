import asyncio
import uuid
import random
import aiohttp
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from copy import deepcopy

from redis.asyncio.client import Redis

from tests.functional.settings import test_settings
from tests.functional.testdata.data import TEST_DATA, TEST_DATA_GENRE, TEST_DATA_PERSON
from tests.functional.utils.dc_objects import Response
from tests.functional.utils.films_utils import generate_films


@pytest_asyncio.fixture(name='es_write_data')
def es_write_data(es_client: AsyncElasticsearch, redis_client: Redis, request):
    async def inner(data: list[dict], index: str) -> None:
        await redis_client.flushdb()
        if await es_client.indices.exists(index=index):
            await es_client.indices.delete(index=index)

        await es_client.indices.create(index=index)

        # refresh="wait_for" - опция для ожидания обновления индекса после выполнения async_bulk
        updated, errors = await async_bulk(client=es_client, actions=data, refresh="wait_for")

        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner


@pytest_asyncio.fixture(name='make_get_request')
def make_get_request(session_client):
    async def inner(type_api, query_data) -> Response:
        url = f'{test_settings.service_url}/api/v1/{type_api}/'
        if 'id' in query_data:
            url += query_data['id']
        get_params = {'query': query_data.get(type_api)}
        if not get_params['query']:
            get_params = None
        async with session_client.get(url, params=get_params) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return Response(body, headers, status)

    return inner


@pytest_asyncio.fixture()
def es_data(request) -> list[dict]:
    es_data = []
    type_test = request.node.get_closest_marker("fixt_data").args[0]
    index = 'movies'
    # выберем по какому индексу будет проходить тест
    for setting_index in test_settings.es_index:
        if type_test in test_settings.es_index[setting_index]:
            index = setting_index

    copy_film_data = deepcopy(TEST_DATA)
    copy_genre_data = deepcopy(TEST_DATA_GENRE)
    copy_person_data = deepcopy(TEST_DATA_PERSON)
    # Генерируем данные для ES
    if type_test == 'limit':
        for _ in range(60):
            copy_film_data['id'] = str(uuid.uuid4())
            es_data.append(deepcopy(copy_film_data))

    if type_test == 'validation':
        for _ in range(3):
            copy_film_data['id'] = str(uuid.uuid4())
            es_data.append(deepcopy(copy_film_data))
        copy_film_data['id'] = str(uuid.uuid4())
        copy_film_data['imdb_rating'] = 15
        es_data.append(deepcopy(copy_film_data))
        copy_film_data['id'] = str(uuid.uuid4())
        copy_film_data['imdb_rating'] = -2
        es_data.append(deepcopy(copy_film_data))
        copy_film_data['id'] = '1123456'
        copy_film_data['imdb_rating'] = 5
        es_data.append(deepcopy(copy_film_data))

    if type_test == 'films_validation':
        for _ in range(3):
            copy_film_data['id'] = str(uuid.uuid4())
            es_data.append(deepcopy(copy_film_data))
        # добавляем фильм с невалидным id
        copy_film_data['id'] = '123456'
        es_data.append(deepcopy(copy_film_data))
        # добавляем фильм с невалидным рейтингом
        copy_film_data['id'] = str(uuid.uuid4())
        copy_film_data['imdb_rating'] = 15
        es_data.append(deepcopy(copy_film_data))
        copy_film_data['id'] = str(uuid.uuid4())
        copy_film_data['imdb_rating'] = -2

    if type_test == 'redis_search':
        for _ in range(6):
            copy_film_data['id'] = str(uuid.uuid4())
            copy_film_data['title'] = 'The Star'
            es_data.append(deepcopy(copy_film_data))

    if type_test == 'redis_films':
        for _ in range(6):
            copy_film_data['id'] = str(uuid.uuid4())
            copy_film_data['title'] = 'The Star'
            es_data.append(deepcopy(copy_film_data))

    if type_test == 'redis_films_id':
        copy_films_data = deepcopy(TEST_DATA)
        es_data.append(deepcopy(copy_films_data))

    if type_test == 'redis_genre':
        copy_genre_data = deepcopy(TEST_DATA_GENRE)
        es_data.append(deepcopy(copy_genre_data))

    if type_test == 'redis_person':
        copy_person_data = deepcopy(TEST_DATA_PERSON)
        es_data.append(deepcopy(copy_person_data))

    if type_test == 'phrase':
        for _ in range(3):
            copy_film_data['id'] = str(uuid.uuid4())
            copy_film_data['title'] = 'The Star'
            es_data.append(deepcopy(copy_film_data))
        for _ in range(3):
            copy_film_data['id'] = str(uuid.uuid4())
            copy_film_data['title'] = 'Star Roger'
            es_data.append(deepcopy(copy_film_data))
        copy_film_data['id'] = str(uuid.uuid4())
        copy_film_data['title'] = 'Roger Philips'
        es_data.append(deepcopy(copy_film_data))

    if type_test == 'limit_genre':
        for _ in range(60):
            copy_genre_data['id'] = str(uuid.uuid4())
            copy_genre_data['name'] = f'Action{_}'
            es_data.append(deepcopy(copy_genre_data))

    if type_test == 'limit_person':
        for i in range(60):
            copy_person_data['id'] = str(uuid.uuid4())
            copy_person_data['full_name'] = f'Test_person{i}'
            es_data.append(deepcopy(copy_person_data))

    if type_test == 'genre_validation':
        for _ in range(3):
            copy_genre_data['id'] = str(uuid.uuid4())
            copy_genre_data['name'] = f'Action{_}'
            es_data.append(deepcopy(copy_genre_data))
        copy_genre_data['id'] = '123456'
        copy_genre_data['name'] = f'Action'
        es_data.append(deepcopy(copy_genre_data))

    if type_test == 'person_validation':
        for i in range(3):
            copy_person_data['id'] = str(uuid.uuid4())
            copy_person_data['name'] = f'Test{i}'
            es_data.append(deepcopy(copy_person_data))
        copy_person_data['id'] = '123456'
        copy_person_data['name'] = f'Ann'
        es_data.append(deepcopy(copy_person_data))

    if type_test == 'all_films':
        count = random.randint(50, 100)
        films = generate_films(count=count)
        es_data.extend(films)

    copy_film_data = deepcopy(TEST_DATA)
    if type_test == 'film':
        es_data.append(deepcopy(copy_film_data))
        for _ in range(60):
            copy_film_data['id'] = str(uuid.uuid4())
            es_data.append(deepcopy(copy_film_data))

    if type_test == 'genre':
        copy_genre_data = deepcopy(TEST_DATA_GENRE)
        es_data.append(deepcopy(copy_genre_data))
        genres = ['Melodrama', 'Sci-Fi', 'Comedy', 'Tragedy']
        for genre in genres:
            copy_genre_data['id'] = str(uuid.uuid4())
            copy_genre_data['name'] = genre
            es_data.append(deepcopy(copy_genre_data))

    if type_test == 'person':
        es_data.append(deepcopy(copy_person_data))
        persons_names = ['Ann', 'Bob', 'Ben', 'Howard']
        for name in persons_names:
            copy_person_data['id'] = str(uuid.uuid4())
            copy_person_data['full_name'] = name + ' Test'
            es_data.append(deepcopy(copy_person_data))

    if type_test == 'person_films':
        count = 15
        films = generate_films(count=count)
        es_data.extend(films)

    bulk_query: list[dict] = []
    for row in es_data:
        data = {'_index': index, '_id': row['id']}
        data.update({'_source': row})
        bulk_query.append(data)

    return bulk_query
