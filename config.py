import os

from pydantic import EmailStr, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API Configurations
    GEMINI_API_KEY: SecretStr

    # Gmail IMAP Configurations
    GMAIL_EMAIL: EmailStr
    GMAIL_APP_PASSWORD: SecretStr

    # Twilio WhatsApp Configurations
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: SecretStr
    TWILIO_FROM_NUMBER: str
    TWILIO_TO_NUMBER: str

    @field_validator("TWILIO_FROM_NUMBER", "TWILIO_TO_NUMBER")
    @classmethod
    def validate_whatsapp_prefix(cls, v: str) -> str:
        if not v.startswith("whatsapp:"):
            return f"whatsapp:{v}"
        return v

    model_config = SettingsConfigDict(
        # Load from .env if it exists, otherwise fall back to environment variables
        env_file=os.path.join(os.path.dirname(__file__), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


try:
    settings = Settings()
except Exception as e:
    print(f"\n[Configuration Error] Failed to load configuration settings: \n{e}\n")
    raise SystemExit(1)
