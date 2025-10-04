from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from pathlib import Path

ENV_DIR = Path(__file__).resolve().parent.parent

class CommonConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_DIR / ".env",
        extra="ignore",
    )
    
class SecurityConfig(CommonConfig):
    bcrypt_rounds: int = Field(default=12, alias="BCRYPT_ROUNDS")
    encryption_key_refresh: str = Field(alias="ENCRYPTION_KEY_REFRESH")
    encryption_key_strava: str = Field(alias="ENCRYPTION_KEY_STRAVA")
    
    
    @field_validator("encryption_key_refresh", "encryption_key_strava")
    def validate_encryption_key(cls, v:str) -> str:
        if len(v) != 44:
            raise ValueError("Encryption key length not valid")
        return v

class JWTConfig(CommonConfig):
    secret: str = Field(default="secret", alias="JWT_SECRET")
    algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")

class DatabaseConfig(CommonConfig):
    url: str = Field(default="sqlite+aiosqlite:///./db.sqlite3", alias="DATABASE_URL")
    echo: bool = Field(default=True, alias="DATABASE_ECHO")

class RedisConfig(CommonConfig):
    host: str = Field(default="redis", alias="REDIS_HOST")
    port: int = Field(default=6379, alias="REDIS_PORT")

class CORSConfig(CommonConfig):
    origins: str = Field(default="*", alias="CORS_ORIGINS")
    credentials: bool = Field(default=True, alias="CORS_CREDENTIALS")
    methods: str = Field(default="*", alias="CORS_METHODS")
    headers: str = Field(default="*", alias="CORS_HEADERS")
    
    @field_validator("origins", mode="after")  # after로 처리
    def split_origins(cls, v):
        return [o.strip() for o in v.split(",")]

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

class StravaConfig(CommonConfig):
    client_id: str = Field(default="", alias="STRAVA_CLIENT_ID")
    client_secret: str = Field(default="", alias="STRAVA_CLIENT_SECRET")
    redirect_uri: str = Field(default="", alias="STRAVA_REDIRECT_URI")
    scope: str = Field(default="", alias="STRAVA_SCOPE")
    token_url: str = Field(default="https://www.strava.com/oauth/token", alias="STRAVA_TOKEN_URL")
    api_url: str = Field(default="https://www.strava.com/api/v3/", alias="STRAVA_API_URL")
    auth_endpoint: str = Field(default="https://www.strava.com/oauth/authorize", alias="STRAVA_AUTH_ENDPOINT")
    deauth_endpoint: str = Field(default="https://www.strava.com/oauth/deauthorize", alias="STRAVA_DEAUTH_ENDPOINT")

class LLMConfig(CommonConfig):
    secret:str = Field(default="", alias="OPENAI_SECRET")

db = DatabaseConfig()
redisdb = RedisConfig()
cors = CORSConfig()
web = WebConfig()
google = GoogleConfig()
jwt_config = JWTConfig()
security = SecurityConfig()
strava = StravaConfig()
llm = LLMConfig()