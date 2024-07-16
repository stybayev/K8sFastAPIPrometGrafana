import httpx
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from auth.core.config import settings
from auth.services.users import UserService, get_user_service
from auth.schema.tokens import TokenResponse
from auth.schema.users import UserCreate, UserResponse

router = APIRouter()

YANDEX_AUTH_URL = "https://oauth.yandex.ru/authorize"
YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"
YANDEX_USER_INFO_URL = "https://login.yandex.ru/info"


@router.get("/yandex/login")
async def yandex_login():
    redirect_uri = settings.YANDEX_REDIRECT_URI
    client_id = settings.YANDEX_CLIENT_ID
    return {
        "auth_url": f"{YANDEX_AUTH_URL}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
    }


@router.get("/yandex/callback")
async def yandex_callback(
        request: Request,
        Authorize: AuthJWT = Depends(),
        service: UserService = Depends(get_user_service)
):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Authorization code not provided")

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': settings.YANDEX_CLIENT_ID,
        'client_secret': settings.YANDEX_CLIENT_SECRET,
        'redirect_uri': settings.YANDEX_REDIRECT_URI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    async with httpx.AsyncClient() as client:
        response = await client.post(YANDEX_TOKEN_URL, data=data, headers=headers)
        response_data = response.json()

    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to get access token")

    access_token = response_data['access_token']

    user_info_response = await client.get(YANDEX_USER_INFO_URL, headers={"Authorization": f"OAuth {access_token}"})
    user_info = user_info_response.json()

    if user_info_response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to get user info")

    yandex_id = user_info.get("id")
    email = user_info.get("default_email")
    first_name = user_info.get("first_name")
    last_name = user_info.get("last_name")

    user = await service.get_by_login(email)
    if not user:
        user_data = UserCreate(
            login=email,
            password="",
            first_name=first_name,
            last_name=last_name,
        )
        user = await service.create_user(
            login=user_data.login,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )

    roles = await service.get_user_roles(user.id)
    user_claims = {"id": str(user.id), "roles": roles}
    tokens = await service.token_service.generate_tokens(Authorize, user_claims, str(user.id))

    return TokenResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token)
