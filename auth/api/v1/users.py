import uuid
from typing import List, Annotated
from fastapi import APIRouter, Depends, Path, HTTPException, Query, status, Header

from auth.schema.tokens import TokenResponse, LoginRequest
from auth.schema.users import UserResponse, UserCreate, UpdateUserCredentialsRequest

from fastapi import Depends, HTTPException, status

from auth.services.users import UserService, get_user_service
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from auth.utils.dc_objects import Token

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
async def login_user(user: LoginRequest, service: UserService = Depends(get_user_service),
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
    tokens = await service.login(login=user.login, password=user.password, Authorize=Authorize)
    return tokens


@router.post("/token/refresh", response_model=Token)
async def refresh_access_token(
        authorization: str = Header(None),
        service: UserService = Depends(get_user_service),
        authorize: AuthJWT = Depends()
):
    """
    Обновление access-токена
    """
    return await service.refresh_access_token(authorize, authorization)


@router.post("/logout", response_model=dict)
async def logout_user():
    """
    Выход пользователя из аккаунта
    """
    pass


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
    try:
        Authorize.jwt_required()
    except AuthJWTException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

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


@router.get("/login/history", response_model=List[dict])
async def get_login_history():
    """
    Получение истории входов пользователя
    """
    pass
