from typing import Optional, List

from pydantic import BaseModel
from uuid import UUID


class RoleSchema(BaseModel):
    name: str
    description: str | None = None
    permissions: Optional[List[str]] = None


class RoleUpdateSchema(BaseModel):
    name: Optional[str]
    description: Optional[str]
    permissions: Optional[List[str]]


class RoleResponse(RoleSchema):
    id: UUID

    class Config:
        orm_mode = True
