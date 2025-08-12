from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REAL_DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    TEST_DATABASE_URL: str = "postgresql+asyncpg://postgres_test:postgres_test@localhost:5433/postgres_test"

settings = Settings()
