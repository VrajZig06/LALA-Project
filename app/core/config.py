from functools import lru_cache

from pydantic_settings import BaseSettings


# Select Environment
class ServerEnv(BaseSettings):
    ENV: str

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
        "case_sensitive": True,
        "enable_decoding": "utf-8",
    }


class Settings(BaseSettings):
    APP_NAME: str = "LALA"

    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRY: int
    JWT_REFRESH_TOKEN_EXPIRY: int

    # Brevo
    BREVO_API_KEY: str
    BREVO_SENDER_EMAIL: str
    BREVO_SENDER_NAME: str

    # Google Auth
    GOOGLE_CLIENT_ID: str

    # FE Links
    FRONTEND_BASE_URL: str

    # REDIS SERVER URL
    REDIS_SERVER_URL: str

    # RAZORPAY INTEGRATION
    RAZORPAY_API_KEY: str
    RAZORPAY_API_SECRET: str
    RAZORPAY_WEBHOOK_SECRET: str


    model_config = {
        "env_file": f".env.{ServerEnv().ENV}",
        "extra": "ignore",
        "case_sensitive": True,
        "enable_decoding": "utf-8",
    }


# Function: Get ENV Variables
@lru_cache
def get_settings():
    return Settings()
