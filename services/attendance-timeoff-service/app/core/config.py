from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "PeoplePay360 - Attendance & TimeOff Service"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/peoplepay360"
    DB_SCHEMA: str = "attendance_timeoff"
    SECRET_KEY: str = "supersecretjwtkey_change_in_production_peoplepay360"
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
