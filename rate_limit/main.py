import datetime
import logging
import os
import json
import aiohttp
import aioredis
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

# Настройки лимитов запросов
REQUEST_LIMIT_PER_MINUTE = 20  # Установим лимит на 20 запросов в минуту
EXPIRED_TIME = 59  # Время жизни ключей
# Хранилище запросов
REDIS_URL = f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}"
redis_conn = aioredis.from_url(REDIS_URL, decode_responses=True)

SERVICE_MAP = {
    "/api/auth": "http://auth:8082",
    "/api/v1/auth": "http://auth:8082",
    "/api/films": "http://app:8000",
    "/api/v1/films": "http://app:8000",
    "/api/files": "http://file_api:8081",
    "/api/v1/files": "http://file_api:8081",
    "/admin": "http://django_admin:8001",
    "/minio/": "http://minio:9000"
}

logging.basicConfig(level=logging.INFO, format='%(levelname)s:     %(message)s')
logger = logging.getLogger(__name__)


@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    client_ip = request.client.host
    now = datetime.datetime.now()
    key = f'{client_ip}:{now.minute}'

    async with redis_conn.pipeline() as pipe:
        # Увеличиваем значение и задаем время жизни ключа
        pipe.incr(key)
        pipe.expire(key, EXPIRED_TIME)
        result = await pipe.execute()

    request_number = result[0]
    logger.info(f"Client IP: {client_ip}, Request number: {request_number}")

    if request_number > REQUEST_LIMIT_PER_MINUTE:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(status_code=429, content={"message": "Too Many Requests"})

    response = await call_next(request)
    return response


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, path: str):
    target_path = f"/{path}"
    target_url = None

    for key, value in SERVICE_MAP.items():
        if target_path.startswith(key):
            target_url = value
            break

    if not target_url:
        raise HTTPException(status_code=400, detail="Invalid target path")

    async with aiohttp.ClientSession() as client:
        request_body = await request.body()
        headers = dict(request.headers)
        params = dict(request.query_params)
        method = request.method
        url = f"{target_url}{target_path}"

        if request_body:
            # Если есть тело запроса, отправляем его как data
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=request_body
            )
        else:
            # Если нет тела запроса, просто отправляем запрос без данных
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params
            )

        # Проверяем тип содержимого ответа перед декодированием как JSON
        if response.headers.get("Content-Type") == "application/json":
            response_content = await response.json()
        else:
            response_content = await response.text()
        logger.info(f"Proxied request to {url} with status {response.status}")
        return JSONResponse(status_code=response.status, content=response_content)
