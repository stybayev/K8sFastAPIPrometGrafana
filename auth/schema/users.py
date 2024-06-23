from pydantic import BaseModel
from uuid import UUID


class UserBase(BaseModel):
    login: str
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
