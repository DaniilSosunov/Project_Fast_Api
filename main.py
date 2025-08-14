from fastapi import FastAPI
from fastapi.routing import APIRouter
from app.routers.user import user_router
import uvicorn

app = FastAPI(title="top_project")

app.include_router(user_router)

