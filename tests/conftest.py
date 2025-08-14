import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from main import app
from app.db.session import get_db
from app.models.user import base


db_lock = asyncio.Lock()

@pytest.fixture(scope="session")
def event_loop():
    """Создаем новый event loop для каждой сессии"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    """Инициализация тестовой БД"""
    engine = create_async_engine(settings.TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.drop_all)
        await conn.run_sync(base.metadata.create_all)
    await engine.dispose()

@pytest.fixture
async def db_session():
    """Изолированная сессия для каждого теста"""
    engine = create_async_engine(settings.TEST_DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()  # Явный откат изменений

    await engine.dispose()

@pytest.fixture(autouse=True)
async def clean_tables(db_session):
    """Полная очистка таблиц перед каждым тестом"""
    async with db_lock:  # Блокировка для избежания race condition
        for table in reversed(base.metadata.sorted_tables):
            await db_session.execute(table.delete())
        await db_session.commit()

@pytest.fixture
def client(db_session):
    """Тестовый клиент с изолированным подключением"""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()