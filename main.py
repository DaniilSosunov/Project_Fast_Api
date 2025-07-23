from fastapi import FastAPI, HTTPException
import uvicorn
from fastapi.routing import APIRoute
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

class User(Base):
     __tablename__ = "users"

     user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
     name = Column(String, nullable=False)
     surname = Column(String, nullable=False)
     email = Column(String, nullable=False, unique=True)
     is_active = Column(Boolean(), default=True)

###################################











