from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    mail_from_name: str
    model_config = SettingsConfigDict(env_file='.env.mail')
    
        
setting = Settings()

