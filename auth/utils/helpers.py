from typing import AsyncGenerator
import httpx

async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Генератор для получения httpx.AsyncClient
    """
    async with httpx.AsyncClient() as client:
        yield client
