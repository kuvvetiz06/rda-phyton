"""Lease extraction konfigürasyonu."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Ortam değişkenlerinden yüklenen ayarlar."""

    openai_api_key: str = Field(..., description="OpenAI API anahtarı")
    openai_model: str = Field(
        "gpt-4o-mini",
        description="LLM modeli",
    )
    openai_temperature: float = Field(
        0.1,
        ge=0.0,
        le=1.0,
        description="LLM sıcaklık ayarı",
    )
    default_currency: str = Field(
        "TRY",
        description="Sayısal tutarların varsayılan para birimi",
    )
    language: str = Field(
        "tr",
        description="PDF içerikleri için varsayılan dil kodu",
    )

    class Config:
        env_prefix = "LEASE_"
        case_sensitive = False


settings = Settings()

__all__ = ["settings"]
