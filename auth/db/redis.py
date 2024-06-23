from redis.asyncio import Redis

connection: Redis | None = None


async def get_redis() -> Redis:
    if not connection:
        raise ValueError("Redis connection is not initialized")
    return connection
