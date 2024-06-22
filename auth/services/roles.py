from functools import lru_cache
from typing import Optional, List

from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, or_, update
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from auth.db.postgres import get_db_session
from auth.models.users import Role
from auth.schema.roles import RoleSchema, RoleResponse, RoleUpdateSchema


class RoleService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_role(self, role: RoleSchema) -> RoleSchema | None:
        """
        Создание роли
        """
        role_exist = await self.is_exist(role_name=role.name)
        if role_exist:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exist")

        new_role = Role(**role.dict())
        self.db_session.add(new_role)
        await self.db_session.commit()
        await self.db_session.refresh(new_role)
        return new_role

    async def delete_role(self, role_id: UUID = None, role_name: str = None) -> dict:
        """
        Удаление роли
        """
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

    async def update_role(self, role_id: UUID, data: RoleUpdateSchema):
        """
        Обновление роли
        """
        role_exist = await self.is_exist(role_id=role_id)

        if not role_exist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

        update_data = data.dict(exclude_unset=True)
        await self.db_session.execute(update(Role).where(Role.id == role_exist.id).values(**update_data))
        await self.db_session.commit()

        # Получение обновленной записи из базы данных
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


@lru_cache()
def get_role_service(db_session: AsyncSession = Depends(get_db_session)) -> RoleService:
    return RoleService(db_session)
