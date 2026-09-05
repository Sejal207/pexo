from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Pexo - HR Service"
    DATABASE_URL: str = "postgresql+asyncpg://neondb_owner:npg_YxFm38qyQWGK@ep-shiny-mouse-aewlrwri-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"
    DB_SCHEMA: str = "public"
    SECRET_KEY: str = "supersecretjwtkey_change_in_production_Pexo"
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
