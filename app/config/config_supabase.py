from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    model_config = SettingsConfigDict(env_file = ".env.supabase")
    
    
settings = Settings()