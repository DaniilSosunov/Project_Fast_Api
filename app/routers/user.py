from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import ShowUser, UserCreate
from app.services.create_user import _create_new_user
from app.db.session import get_db

user_router = APIRouter(prefix="/user", tags=["user"])

@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    return await _create_new_user(body)