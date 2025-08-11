from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    supabase_url: str
    supabase_service_key: str
    google_api_key : str
    class Config:
        env_file = ".env"
        extra = "ignore"  # Optional: prevent errors if extra vars appear later


settings = Settings()
