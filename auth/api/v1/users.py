import uuid
import datetime

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from typing import List
from fastapi import APIRouter, Depends, Path, HTTPException, Query, status, Request

from auth.schema.tokens import TokenResponse, LoginRequest
from auth.schema.users import UserResponse, UserCreate, UpdateUserCredentialsRequest, LoginHistoryResponse
from auth.models.users import LoginHistory

from fastapi import Depends, HTTPException, status

from auth.services.users import UserService, get_user_service
from collections.abc import Sequence
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    """
    ## Регистрация нового пользователя

    Этот эндпоинт позволяет зарегистрировать нового пользователя в системе.
    Пользовательские данные сохраняются в базе данных PostgreSQL.

    ### Параметры:
    - **user**: Объект, содержащий данные для регистрации пользователя.
        - **login**: Логин пользователя.
        - **password**: Пароль пользователя.
        - **first_name**: Имя пользователя (необязательно).
        - **last_name**: Фамилия пользователя (необязательно).

    ### Возвращает:
      - `id`: Уникальный идентификатор пользователя.
      - `login`: Логин пользователя.
      - `first_name`: Имя пользователя.
      - `last_name`: Фамилия пользователя.
    """

    new_user = await service.create_user(login=user.login, password=user.password, first_name=user.first_name,
                                         last_name=user.last_name)
    return UserResponse(id=new_user.id, login=new_user.login, first_name=new_user.first_name,
                        last_name=new_user.last_name)


@router.post("/login", response_model=TokenResponse)
async def login_user(user: LoginRequest, request: Request, service: UserService = Depends(get_user_service),
                     Authorize: AuthJWT = Depends()):
    """
    ## Вход пользователя

    Этот эндпоинт позволяет пользователю войти в систему, используя свои учетные данные.

    ### Параметры:
    - **user**: Объект, содержащий данные для входа пользователя.
        - **login**: Логин пользователя.
        - **password**: Пароль пользователя.

    ### Возвращает:
      - **access_token**: Токен доступа, используемый для авторизации.
      - **refresh_token**: Токен обновления, используемый для получения нового токена доступа.
    """
    user_agent = request.headers.get("user-agent")
    tokens = await service.login(
        login=user.login,
        password=user.password,
        Authorize=Authorize,
        user_agent=user_agent
    )
    return tokens


@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_access_token(
        service: UserService = Depends(get_user_service),
        authorize: AuthJWT = Depends()
):
    """
    ## Обновление Access токена

    Этот эндпоинт позволяет обновить Access токен пользователя используя его Refresh токен.
    При этом старый Refresh токен добавляется в невалидные и пользователю выдается новая
    пара Access, Refresh токенов

    ### Возвращает:
      - `access-token`: Access токен.
      - `refresh-token`: Refresh токен.
    """
    return await service.refresh_access_token(authorize)


@router.post("/logout", response_model=bool)
async def logout_user(
        service: UserService = Depends(get_user_service),
        authorize: AuthJWT = Depends()
):
    """
    ## Выход пользователя из аккаунта

    Этот эндпоинт реализует выход пользователя из аккаунта. Добавляет текущие Refresh и Access токены в невалидные

    ### Возвращает:
      - `True`: в случае успешного выхода.
    """
    return await service.logout_user(authorize)


@router.patch("/update-credentials",
              response_model=UserResponse,
              )
async def update_user_credentials(
        user_credentials: UpdateUserCredentialsRequest,
        service: UserService = Depends(get_user_service),
        Authorize: AuthJWT = Depends()
):
    """
    ## Обновление данных пользователя

    Этот эндпоинт позволяет пользователю изменить свои учетные данные, такие как логин и пароль.

    ### Параметры:
    - **login**: Новый логин пользователя (необязательно).
    - **password**: Новый пароль пользователя (необязательно).

    ### Возвращает:
      - `id`: Уникальный идентификатор пользователя.
      - `login`: Обновленный логин пользователя.
      - `first_name`: Имя пользователя.
      - `last_name`: Фамилия пользователя.
    """
    Authorize.jwt_required()

    user_id = uuid.UUID(Authorize.get_jwt_subject())

    updated_user = await service.update_user_credentials(
        user_id=user_id,
        login=user_credentials.login,
        password=user_credentials.password
    )
    return UserResponse(
        id=updated_user.id,
        login=updated_user.login,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
    )


@router.get("/login/history", response_model=List[LoginHistoryResponse])
async def get_login_history(
        service: UserService = Depends(get_user_service),
        authorize: AuthJWT = Depends()
):
    """
    ## Получение истории авторизации пользователя в системе

    Endpoint запрашивает историю авторизации пользователя в системе по его идентификатору, указанному в токене

    ### Возвращает:
      - `user_agent`: устройство, с которого была произведена авторизация
      - `login_time`: время авторизации
    """
    history = [
        LoginHistoryResponse(
            user_agent=h.user_agent,
            login_time=h.login_time
        ) for h in await service.get_login_history(authorize)
    ]
    return history
