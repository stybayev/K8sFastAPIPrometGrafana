from typing import List
from fastapi import APIRouter, Depends, Path, HTTPException, Query, status
from uuid import UUID
from auth.models.users import Role
from auth.schema.roles import RoleSchema, RoleResponse, RoleUpdateSchema, AssignRoleResponse
from auth.services.roles import RoleService, get_role_service

router = APIRouter()


@router.post("/", response_model=dict)
async def create_role(role: RoleSchema, service: RoleService = Depends(get_role_service)) -> RoleResponse:
    """
    Создание роли
    """
    new_role = await service.create_role(role)
    return RoleResponse.from_orm(new_role)


@router.delete("/")
async def delete_role(role_id: UUID = None, role_name: str = None,
                      service: RoleService = Depends(get_role_service)) -> dict:
    """
    Удалить роль по ID или имени.

    Параметры:
    - role_id: UUID (необязательно) - ID роли, которую нужно удалить.
    - name: str (необязательно) - Имя роли, которую нужно удалить.

    Необходимо указать либо role_id, либо name.
    """
    result = await service.delete_role(role_id, role_name)
    return result


@router.patch("/{role_id}")
async def update_role(role_id: UUID, data: RoleUpdateSchema,
                      service: RoleService = Depends(get_role_service)) -> RoleResponse:
    """
    Обновить роль по ID.

    Параметры:
    - role_id: UUID - ID роли, которую нужно обновить.
    - data: RoleUpdateSchema - Данные для обновления.
    """
    updated_role = await service.update_role(role_id, data)
    return RoleResponse.from_orm(updated_role)


@router.get("/")
async def get_roles(service: RoleService = Depends(get_role_service)):
    """
    Просмотр всех ролей
    """
    roles = await service.get_all_roles()
    return roles


@router.post("/users/{user_id}/roles/{role_id}", response_model=AssignRoleResponse)
async def assign_role_to_user(
        user_id: UUID = Path(..., description="User ID"),
        role_id: UUID = Path(..., description="Role ID"),
        service: RoleService = Depends(get_role_service)
):
    """
    Назначение роли пользователю

    Этот эндпоинт позволяет назначить роль существующему пользователю в системе.

    ### Параметры:
    - **user_id**: UUID - Идентификатор пользователя.
    - **role_id**: UUID - Идентификатор роли.

    ### Возвращает:
    - **user_id**: UUID - Идентификатор пользователя.
    - **role_id**: UUID - Идентификатор роли.
    - **message**: str - Сообщение о результате операции.

    ### Исключения:
    - **404 Not Found**: Пользователь или роль не найдены.
    - **400 Bad Request**: Роль уже назначена пользователю.
    """
    result = await service.assign_role_to_user(user_id, role_id)
    return AssignRoleResponse(user_id=user_id, role_id=role_id, message=result["message"])


@router.delete("/users/{user_id}/roles/{role_id}", response_model=dict)
async def remove_role_from_user(user_id: UUID = Path(..., description="User ID"),
                                role_id: UUID = Path(..., description="Role ID")):
    """
    Отобрать роль у пользователя
    """
    pass


@router.get("/users/me/permissions", response_model=List[dict])
async def check_user_permissions():
    """
    Проверка наличия прав у пользователя
    """
    pass


@router.post("/logout/others", response_model=dict)
async def logout_other_sessions():
    """
    Реализация кнопки "Выйти из остальных аккаунтов"
    """
    pass
