from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Pexo - API Gateway"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/Pexo"
    DB_SCHEMA: str = "gateway"
    REDIS_URL: str = "redis://redis:6379/0"
    SECRET_KEY: str = "supersecretjwtkey_change_in_production_Pexo"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    HR_SERVICE_URL: str = "http://hr-service:8001"
    ATTENDANCE_SERVICE_URL: str = "http://attendance-timeoff-service:8002"
    PAYROLL_SERVICE_URL: str = "http://payroll-service:8003"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
