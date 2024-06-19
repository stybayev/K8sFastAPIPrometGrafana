from typing import List
from fastapi import APIRouter, Depends, Path, HTTPException, Query, status
from uuid import UUID
from auth.models.users import Role
from auth.schema.roles import RoleSchema
from auth.services.roles import RoleService, get_role_service

router = APIRouter()


@router.post("/roles", response_model=dict)
async def create_role():
    """
    Создание роли
    """
    return {'123': 123}


# @router.delete("/{role_id}", response_model=Role)
# async def delete_role(role_id: UUID = Path(..., description="Role ID")):
#     """
#     Удаление роли
#     """
#     pass
#
#
# @router.patch("/{role_id}", response_model=Role)
# async def update_role(role_id: UUID = Path(..., description="Role ID")):
#     """
#     Изменение роли
#     """
#     pass
#
#
# @router.get("/", response_model=List[Role])
# async def get_roles():
#     """
#     Просмотр всех ролей
#     """
#     pass
#
#
# @router.post("/users/{user_id}/roles/{role_id}", response_model=dict)
# async def assign_role_to_user(user_id: UUID = Path(..., description="User ID"),
#                               role_id: UUID = Path(..., description="Role ID")):
#     """
#     Назначение роли пользователю
#     """
#     pass
#
#
# @router.delete("/users/{user_id}/roles/{role_id}", response_model=dict)
# async def remove_role_from_user(user_id: UUID = Path(..., description="User ID"),
#                                 role_id: UUID = Path(..., description="Role ID")):
#     """
#     Отобрать роль у пользователя
#     """
#     pass
#
#
# @router.get("/users/me/permissions", response_model=List[dict])
# async def check_user_permissions():
#     """
#     Проверка наличия прав у пользователя
#     """
#     pass
#
#
# @router.post("/logout/others", response_model=dict)
# async def logout_other_sessions():
#     """
#     Реализация кнопки "Выйти из остальных аккаунтов"
#     """
#     pass
