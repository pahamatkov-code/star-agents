from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    role: str | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
