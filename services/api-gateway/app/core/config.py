from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Pexo - API Gateway"
    # Neon (and schema.sql) use one flat database with no per-service Postgres
    # schema — set DB_SCHEMA only if you deliberately namespace tables.
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/Pexo"
    DB_SCHEMA: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "supersecretjwtkey_change_in_production_Pexo"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_COOKIE_NAME: str = "refresh_token"
    COOKIE_SECURE: bool = False

    FRONTEND_ORIGIN: str = "http://localhost:5175"

    HR_SERVICE_URL: str = "http://localhost:8001"
    ATTENDANCE_SERVICE_URL: str = "http://localhost:8002"
    PAYROLL_SERVICE_URL: str = "http://localhost:8003"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
