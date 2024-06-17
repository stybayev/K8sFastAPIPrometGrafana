import os
import redis

from dotenv import load_dotenv

from helpers import backoff, logger

load_dotenv(dotenv_path='.env.test')

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', '6379')


@backoff()
def wait_for_redis():
    r = redis.Redis(host=redis_host, port=redis_port)
    if not r.ping():
        raise Exception("Redis is not available")
    logger.info("Redis is available")


if __name__ == '__main__':
    wait_for_redis()
