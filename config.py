from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    jwt_algorithm: str
    jwt_key: str
    expiration_time: int
    database_url: str

    model_config = SettingsConfigDict(env_file=".env")
        
@lru_cache
def get_settings():
    return Settings()  

settings: Settings = get_settings()  