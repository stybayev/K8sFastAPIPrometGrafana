import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

from helpers import backoff, logger

load_dotenv(dotenv_path='.env.test')

es_host = os.getenv('ELASTIC_HOST', 'localhost')
es_port = os.getenv('ELASTIC_PORT', '9200')
es_url = f'http://{es_host}:{es_port}'


@backoff()
def wait_for_es():
    es_client = Elasticsearch(hosts=[es_url], verify_certs=False)
    if not es_client.ping():
        raise Exception("Elasticsearch is not available")
    logger.info("Elasticsearch is available")


if __name__ == '__main__':
    wait_for_es()
