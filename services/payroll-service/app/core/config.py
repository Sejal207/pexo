from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Pexo - Payroll Service"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/Pexo"
    DB_SCHEMA: str = "payroll"
    REDIS_URL: str = "redis://redis:6379/0"
    SECRET_KEY: str = "supersecretjwtkey_change_in_production_Pexo"
    ALGORITHM: str = "HS256"

    HR_SERVICE_URL: str = "http://hr-service:8001"
    ATTENDANCE_SERVICE_URL: str = "http://attendance-timeoff-service:8002"
    AZURE_STORAGE_CONNECTION_STRING: str = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://azurite:10000/devstoreaccount1;"
    AZURE_CONTAINER_NAME: str = "payslips"

    # Local/CI testing without a real Redis broker: tasks run synchronously,
    # in-process, the moment they're "sent." Never enable in docker-compose/prod.
    CELERY_TASK_ALWAYS_EAGER: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
