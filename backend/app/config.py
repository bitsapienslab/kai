from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://bussola:bussola@localhost:5433/bussola"
    jwt_secret: str = "change-me-before-production"

    # OpenAI — set OPENAI_API_KEY in environment or .env file
    openai_api_key: str = ""
    model_name: str = "gpt-4o-mini"

    # Legacy fields kept for backwards compatibility
    open_webui_url: str = "http://localhost:3000"
    model_api_url: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

