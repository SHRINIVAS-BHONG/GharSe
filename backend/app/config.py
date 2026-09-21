import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://127.0.0.1:27017/gharse"
    REDIS_URI: str = "redis://127.0.0.1:6379/0"
    JWT_SECRET: str = "gharse_super_secret_jwt_key_for_development_2026"
    JWT_EXPIRES_IN: str = "7d"
    PORT: int = 5000
    CLIENT_URL: str = "http://localhost:5173"
    DEFAULT_COMMISSION_PERCENT: int = 15

    # Database Connection Pool Settings
    MONGO_MAX_POOL_SIZE: int = 50
    MONGO_MIN_POOL_SIZE: int = 10
    MONGO_MAX_IDLE_TIME_MS: int = 45000
    MONGO_WAIT_QUEUE_TIMEOUT_MS: int = 5000
    MONGO_CONNECT_TIMEOUT_MS: int = 5000
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int = 5000

    # Worker Concurrency Settings
    WORKERS: int = 2

    # SMTP Settings (Gmail)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
