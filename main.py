from typing import Any, Self
from fastapi import FastAPI, HTTPException
import uvicorn
from fastapi.routing import APIRouter
from sqlalchemy import Column, Boolean, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import settings
from sqlalchemy.dialects.postgresql import UUID
import uuid
import re
from pydantic import BaseModel, EmailStr, validator

##################################


engine = create_async_engine(settings.REAL_DATABASE_URL, future=True, echo=True)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


##################################

base = declarative_base()

class User(base):
     __tablename__ = "users"

     user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
     name = Column(String, nullable=False)
     surname = Column(String, nullable=False)
     email = Column(String, nullable=False, unique=True)
     is_active = Column(Boolean(), default=True)

###################################

class UserDAL:
     def __init__(self,db_session: AsyncSession):
          self.db_session = db_session

     async def create_user(
          self, name: str, surname: str, email: str
     ) -> User:
          new_user = User(
               name=name,
               surname=surname,
               email=email,
          )
          self.db_session.add(new_user)
          await self.db_session.flush()
          return new_user

###############################

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


#####################################



user_router = APIRouter(prefix="/users", tags=["users"])



async def _create_new_user(body: UserCreate) -> ShowUser:
     async with async_session() as session:
          async with session.begin():
               user_dal = UserDAL(session)
               user = await user_dal.create_user(
                    name=body.name,
                    surname=body.surname,
                    email=body.email,
               )
          return ShowUser(
               user_id=user.user_id,
               name=user.name,
               surname=user.surname,
               email=user.email,
               is_active=user.is_active
          )


@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate) -> ShowUser:
     return await _create_new_user(body)

app = FastAPI(title="User Management API")

app.include_router(user_router)