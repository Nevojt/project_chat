from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mail_username: str
#     mail_password: str
#     mail_from: str
#     mail_port: int
#     mail_server: str
#     mail_from_name: str
    
    class Config:
        env_file = ".env"
        
reset = Settings()