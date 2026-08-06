from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://bussola:bussola@localhost:5433/bussola"
    jwt_secret: str = "change-me-before-production"
    open_webui_url: str = "http://localhost:3000"
    model_name: str = "kai"
    model_api_url: str = "http://localhost:11434/v1/chat/completions"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

