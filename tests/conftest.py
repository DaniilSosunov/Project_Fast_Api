
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





@pytest.fixture
async def db_session(engine):
    """Создает сессию для работы с базой данных."""
    async with async_session(bind=engine) as session:
        yield session
        await session.rollback()  # Откатываем транзакцию после каждого теста


@pytest.fixture
async def client(db_session):
    """Создает тестовый клиент FastAPI с подмененной зависимостью get_db."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db
        yield client
        app.dependency_overrides.pop(get_db, None)






