from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str

    @property
    def get_db_url(self):
        return f"sqlite+aiosqlite:///db.sqlite3"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

def get_auth_data():
    return {"secret_key": settings.SECRET_KEY, 'algorithm': settings.ALGORITHM}