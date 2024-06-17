from pydantic import BaseSettings


class TestSettings(BaseSettings):
    es_index: dict = {
        'movies':
            [
                'redis_search', 'redis_films', 'limit', 'validation', 'phrase',
                'film', 'all_films', 'films_validation', 'redis_films_id'
            ],
        'genres': ['limit_genre', 'genre_validation', 'redis_genre', 'genre'],
        'persons': ['limit_person', 'person', 'person_validation', 'person_films', 'redis_person']
    }

    es_host: str = 'http://127.0.0.1:9200'
    redis_host: str = 'localhost'
    redis_port: int = 6379
    service_url: str = 'http://127.0.0.1:8000'

    class Config:
        env_file = '.env.test'
        env_prefix = 'TEST_'


test_settings = TestSettings()
