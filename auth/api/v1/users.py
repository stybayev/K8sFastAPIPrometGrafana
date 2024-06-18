from typing import List
from fastapi import APIRouter, Depends, Path, HTTPException, Query, status

router = APIRouter()


@router.post("/users", response_model=dict)
async def register_user():
    """
    Регистрация нового пользователя
    """
    pass


@router.post("/login", response_model=dict)
async def login_user():
    """
    Вход пользователя в аккаунт
    """
    pass


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
