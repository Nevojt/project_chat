from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    mail_from_name: str
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    supabase_url: str
    supabase_key: str
    backblaze_id: str
    backblaze_key: str
    url_address_dns: str
    key_crypto: str
    model_config = SettingsConfigDict(env_file = ".env")
   



settings = Settings()