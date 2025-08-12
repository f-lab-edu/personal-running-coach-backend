from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class CommonConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

class TokenConfig(CommonConfig):
    secret: str = Field(default="secret", alias="JWT_SECRET")
    algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")

class DatabaseConfig(CommonConfig):
    url: str = Field(default="sqlite+aiosqlite:///./db.sqlite3", alias="DATABASE_URL")
    echo: bool = Field(default=True, alias="DATABASE_ECHO")

class CORSConfig(CommonConfig):
    origins: str = Field(default="*", alias="CORS_ORIGINS")
    credentials: bool = Field(default=True, alias="CORS_CREDENTIALS")
    methods: str = Field(default="*", alias="CORS_METHODS")
    headers: str = Field(default="*", alias="CORS_HEADERS")

class WebConfig(CommonConfig):
    host: str = Field(default="0.0.0.0", alias="WEB_HOST")
    port: int = Field(default=8000, alias="WEB_PORT")
    
class GoogleConfig(CommonConfig):
    client_id: str = Field(default="", alias="GOOGLE_CLIENT_ID")
    client_secret: str = Field(default="", alias="GOOGLE_CLIENT_SECRET")
    redirect_uri: str = Field(default="", alias="GOOGLE_REDIRECT_URI")
    scope: str = Field(default="", alias="GOOGLE_SCOPE")
    auth_endpoint: str = Field(default="", alias="GOOGLE_AUTH_ENDPOINT")
    token_url:str = Field(default="https://oauth2.googleapis.com/token")

db = DatabaseConfig()
cors = CORSConfig()
web = WebConfig()
google = GoogleConfig()
token_config = TokenConfig()