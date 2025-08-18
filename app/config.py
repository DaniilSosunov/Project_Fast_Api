from pydantic_settings import BaseSettings
import os
class Settings(BaseSettings):
    REAL_DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    TEST_DATABASE_URL: str = "postgresql+asyncpg://postgres_test:postgres_test@localhost:5433/postgres_test"

settings = Settings()


def get_database_url():
    mode = os.getenv("MODE", "prod")  # Получаем значение MODE или "prod" по умолчанию
    if mode == "test":
        return settings.TEST_DATABASE_URL  # Возвращаем URL тестовой базы данных
    else:
        return settings.REAL_DATABASE_URL