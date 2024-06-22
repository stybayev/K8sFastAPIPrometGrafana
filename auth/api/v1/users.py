from typing import List
from fastapi import APIRouter, Depends, Path, HTTPException, Query, status

from auth.schema.tokens import TokenResponse, LoginRequest
from auth.schema.users import UserResponse, UserCreate

from fastapi import Depends, HTTPException, status

from auth.services.users import UserService, get_user_service
from fastapi_jwt_auth import AuthJWT

router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
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
    Вход пользователя в аккаунт
    """
    tokens = await service.login(login=user.login, password=user.password, Authorize=Authorize)
    return tokens


@router.post("/token/refresh", response_model=dict)
async def refresh_access_token():
    """
    Обновление access-токена
    """
    pass


@router.post("/logout", response_model=dict)
async def logout_user():
    """
    Выход пользователя из аккаунта
    """
    pass


@router.patch("/users/me", response_model=dict)
async def update_user_credentials():
    """
    Изменение логина или пароля
    """
    pass


@router.get("/login/history", response_model=List[dict])
async def get_login_history():
    """
    Получение истории входов пользователя
    """
    pass
