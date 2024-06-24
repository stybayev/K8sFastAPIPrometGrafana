from functools import lru_cache
from typing import List

from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from redis.asyncio import Redis
from sqlalchemy import delete, or_, update, and_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from auth.db.postgres import get_db_session
from auth.db.redis import get_redis
from auth.models.users import Role, UserRole, User
from auth.schema.roles import RoleSchema, RoleResponse, RoleUpdateSchema, UserRoleSchema, UserPermissionsSchema


class RoleService:
    def __init__(self, db_session: AsyncSession, redis: Redis):
        self.db_session = db_session
        self.redis = redis

    async def create_role(self, role: RoleSchema, Authorize: AuthJWT) -> RoleSchema | None:
        """
        Создание роли
        """
        if not await self.is_admin(Authorize):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissions denied")

        role_exist = await self.is_exist(role_name=role.name)
        if role_exist:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exist")

        new_role = Role(**role.dict())
        self.db_session.add(new_role)
        await self.db_session.commit()
        await self.db_session.refresh(new_role)
        return new_role

    async def delete_role(self, Authorize: AuthJWT, role_id: UUID = None, role_name: str = None) -> dict:
        """
        Удаление роли
        """
        if not await self.is_admin(Authorize):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissions denied")

        if not any([role_id, role_name]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either role_id or role_name must be provided"
            )
        result = await self.db_session.execute(select(Role).where(or_(Role.id == role_id, Role.name == role_name)))
        role_exist = result.scalars().first()

        if not role_exist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

        await self.db_session.execute(delete(Role).where(Role.id == role_exist.id))
        await self.db_session.commit()
        return {"message": f"Role '{role_exist.name}' deleted successfully"}

    async def update_role(self, role_id: UUID, data: RoleUpdateSchema, Authorize: AuthJWT):
        """
        Обновление роли
        """
        if not await self.is_admin(Authorize):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissions denied")

        role_exist = await self.is_exist(role_id=role_id)

        if not role_exist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

        update_data = data.dict(exclude_unset=True)
        await self.db_session.execute(update(Role).where(Role.id == role_exist.id).values(**update_data))
        await self.db_session.commit()

        result = await self.db_session.execute(select(Role).where(Role.id == role_id))
        updated_role = result.scalars().first()

        return updated_role

    async def get_all_roles(self) -> List[RoleResponse]:
        """
        Просмотр всех ролей
        """
        roles = await self.db_session.execute(select(Role))
        return [RoleResponse.from_orm(role) for role in roles.scalars().all()]

    async def is_exist(self, role_id: UUID = None, role_name: str = None) -> Role | None:
        result = None
        if role_id:
            result = await self.db_session.execute(select(Role).where(Role.id == role_id))
        if role_name:
            result = await self.db_session.execute(select(Role).where(Role.name == role_name))
        return result.scalar_one_or_none()

    async def assign_role_to_user(self, user_id, role_id, Authorize: AuthJWT) -> UserRoleSchema:
        """
        Добавление роли пользователю
        """
        if not await self.is_admin(Authorize):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissions denied")

        result = await self.db_session.execute(
            select(UserRole).where(and_(UserRole.user_id == user_id, UserRole.role_id == role_id)))
        user_role_exist = result.scalar_one_or_none()

        if user_role_exist:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="UserRole already exist")

        new_user_role = UserRole(user_id=user_id, role_id=role_id)
        self.db_session.add(new_user_role)
        await self.db_session.commit()
        await self.db_session.refresh(new_user_role)
        return new_user_role

    async def remove_role_from_user(self, user_id, role_id, Authorize: AuthJWT) -> dict:
        """
        Удаление роли пользователя
        """
        if not await self.is_admin(Authorize):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissions denied")

        result = await self.db_session.execute(
            select(UserRole).where(and_(UserRole.user_id == user_id, UserRole.role_id == role_id)))
        user_role_exist = result.scalar_one_or_none()

        if not user_role_exist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="UserRole not found")

        await self.db_session.execute(
            delete(UserRole).where(and_(UserRole.user_id == user_id, UserRole.role_id == role_id)))
        await self.db_session.commit()
        return {"message": f"UserRole '{user_role_exist}' deleted successfully"}

    async def get_user_permissions(self, user_id: UUID) -> UserPermissionsSchema:
        result = await self.db_session.execute(
            select(User).where(User.id == user_id).options(selectinload(User.roles))
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user_permissions = []
        for role in user.roles:
            user_permissions += role.permissions

        return UserPermissionsSchema(user_id=user_id, permissions=user_permissions)

    async def is_admin(self, Authorize: AuthJWT) -> bool:
        """
        Проверка, что пользователь admin
        """
        Authorize.jwt_required()

        current_user = Authorize.get_jwt_subject()
        user_data = await self.db_session.execute(
            select(User).where(User.id == current_user).options(selectinload(User.roles))
        )
        user_data = user_data.scalar_one_or_none()
        user_roles = [role.name for role in user_data.roles]
        return "admin" in user_roles


@lru_cache()
def get_role_service(db_session: AsyncSession = Depends(get_db_session),
                     redis: Redis = Depends(get_redis)) -> RoleService:
    return RoleService(db_session, redis)