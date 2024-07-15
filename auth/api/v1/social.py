from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from auth.schema.users import UserCreate
from auth.services.users import UserService, get_user_service
import httpx
from auth.core.config import settings

router = APIRouter()


@router.get("/yandex/login")
async def yandex_login():
    yandex_oauth_url = (
        f"https://oauth.yandex.ru/authorize?response_type=code"
        f"&client_id={settings.oauth.yandex_client_id}"
        f"&redirect_uri={settings.oauth.yandex_redirect_uri}"
    )
    return RedirectResponse(yandex_oauth_url)


@router.get("/yandex/callback")
async def yandex_callback(code: str, service: UserService = Depends(get_user_service)):
    try:
        token = await get_yandex_token(code)
        user_info = await get_yandex_user_info(token)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to authenticate with Yandex")

    # Check if user already exists
    user = await service.get_by_login(user_info['login'])
    if not user:
        user_create = UserCreate(
            login=user_info['login'],
            password=None,  # You can set a default password or generate one
            first_name=user_info.get('first_name'),
            last_name=user_info.get('last_name')
        )
        user = await service.create_user(**user_create.dict())

    # Generate tokens for the user
    tokens = await service.login(user.login, None, None, None)

    # Redirect to the final URL
    final_redirect_url = settings.oauth.yandex_final_redirect_uri
    return RedirectResponse(final_redirect_url)


async def get_yandex_token(code: str) -> str:
    url = "https://oauth.yandex.ru/token"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': settings.oauth.yandex_client_id,
        'client_secret': settings.oauth.yandex_client_secret,
        'redirect_uri': settings.oauth.yandex_redirect_uri,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
        return token_data['access_token']


async def get_yandex_user_info(token: str) -> dict:
    url = "https://login.yandex.ru/info"
    headers = {
        'Authorization': f'OAuth {token}'
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        user_data = response.json()
        return {
            'login': user_data['default_email'],
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name']
        }
