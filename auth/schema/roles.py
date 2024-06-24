from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel


class RoleSchema(BaseModel):
    name: str
    description: str | None = None
    permissions: Optional[List[str]] = None


class RoleUpdateSchema(BaseModel):
    name: Optional[str]
    description: Optional[str]
    permissions: Optional[List[str]]


class UserRoleSchema(BaseModel):
    id: UUID
    user_id: UUID
    role_id: UUID

    class Config:
        orm_mode = True


class UserPermissionsSchema(BaseModel):
    user_id: UUID
    permissions: List[str]


class RoleResponse(RoleSchema):
    id: UUID

    class Config:
        orm_mode = True


class AssignRoleResponse(BaseModel):
    user_id: UUID
    role_id: UUID
    message: str
