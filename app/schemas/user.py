from fastapi import HTTPException
from pydantic import BaseModel, validator, EmailStr

import uuid
import re

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")

class UserBase(BaseModel):
    """Базовый класс пользователя"""
    name: str
    surname: str
    email: EmailStr

    class Config:
        from_attributes = True


class ShowUser(UserBase):
    user_id: uuid.UUID
    is_active: bool


class UserCreate(UserBase):

    @validator("name", "surname")
    def validete_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail='The name and surname must contain only letters.'
            )
        return value