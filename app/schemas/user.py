import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import User


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not any(c.islower() for c in value):
            raise ValueError("A senha deve conter pelo menos uma letra minúscula")
        if not any(c.isupper() for c in value):
            raise ValueError("A senha deve conter pelo menos uma letra maiúscula")
        if not any(c.isdigit() for c in value):
            raise ValueError("A senha deve conter pelo menos um dígito")
        return value


class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    is_active: bool | None = None
    password: str | None = Field(None, min_length=6, max_length=128)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
