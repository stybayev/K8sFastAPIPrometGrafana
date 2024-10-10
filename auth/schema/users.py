from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


class UserBase(BaseModel):
    login: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: UUID

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    login: str
    password: str


class UpdateUserCredentialsRequest(BaseModel):
    login: str
    password: str


class LoginHistoryResponse(BaseModel):
    user_agent: str
    login_time: datetime


class UserDetails(BaseModel):
    id: UUID
    login: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime
    roles: List[str]

    class Config:
        orm_mode = True