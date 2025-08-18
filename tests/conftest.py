# import pytest
# import asyncio
# from fastapi.testclient import TestClient
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker
# from app.config import settings
# from main import app
# from app.db.session import get_db
# from app.models.user import Base, User
#
#
# @pytest.fixture(scope="session")
# async def engine():
#     engine = create_async_engine(settings.TEST_DATABASE_URL)
#     yield engine
#     await engine.dispose()
#
#
# @pytest.fixture(scope="session")
# async def setup_db(engine):
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#
#
# @pytest.fixture
# async def db_session(engine, setup_db):
#     async_session = sessionmaker(
#         engine, expire_on_commit=False, class_=AsyncSession
#     )
#     async with async_session() as session:
#         yield session
#
#
# @pytest.fixture
# def client(db_session):
#     async def override_get_db():
#         async with db_session as session:
#             yield session
#
#     app.dependency_overrides[get_db] = override_get_db
#
#     with TestClient(app) as client:
#         yield client
#
#
# @pytest.fixture
# async def create_user(client):
#     async def _create_user(user_data: dict):
#         response = client.post("/user/", json=user_data)
#         assert response.status_code == 200
#         return response.json()
#
    #return _create_user

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from alembic.config import Config
from alembic import command

from app.config import settings
from app.db.session import get_db, async_session
from main import app

CLEAN_TABLES = ["users"]  # <---- ВОТ ОНА!





async def run_async_alembic_upgrade(engine):
    """Запускает миграции Alembic асинхронно."""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", str(engine.url))

    # Используем async_migration context для асинхронного выполнения миграций
    from alembic import command
    from alembic.runtime.migration import MigrationContext
    from sqlalchemy import pool

    async with engine.begin() as conn:
        context = MigrationContext.configure(
            connection=conn,
            opts={"name": "alembic"},
        )

        if context.script is None:
            print("No Alembic repository found, please create one.")
            return

        command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session")
async def engine():
    """Создает асинхронный engine для тестов."""
    engine = create_async_engine(settings.TEST_DATABASE_URL, echo=True)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
async def prepare_database(engine):
    """Запускает миграции перед началом тестов."""
    await run_async_alembic_upgrade(engine)


@pytest.fixture
async def db_session(engine):
    """Создает сессию для работы с базой данных."""
    async with async_session(bind=engine) as session:
        yield session
        await session.rollback()  # Откатываем транзакцию после каждого теста


@pytest.fixture
async def client(db_session):
    """Создает тестовый клиент FastAPI с подмененной зависимостью get_db."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Используем ASGITransport для интеграции с FastAPI
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    # Очищаем overrides после использования.  Это важно, чтобы не повлиять на другие тесты.
    app.dependency_overrides.pop(get_db, None)






