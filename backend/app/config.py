"""Application configuration for lease processing services."""

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Lease extraction configuration loaded from environment variables."""

    default_currency: str = "USD"
    payment_frequency: str = "monthly"
    language: str = "en"

    class Config:
        env_prefix = "LEASE_"
        case_sensitive = False


settings = Settings()
