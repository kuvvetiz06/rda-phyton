"""Lease extraction domain modelleri.

Bu modül, LLM çıktısını güvenilir biçimde temsil etmek için
Pydantic modelleri sağlar. Her alan, ham alıntı ve normalize
edilmiş değer ile birlikte güven skorunu tutar.
"""

from __future__ import annotations

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")


class LeaseField(BaseModel, Generic[T]):
    """Tek bir kira alanını ham ve normalize edilmiş biçimde temsil eder."""

    model_config = ConfigDict(extra="ignore")

    raw: Optional[str] = Field(
        None,
        description="Sözleşme metnindeki ham değer.",
    )
    normalized: Optional[T] = Field(
        None,
        description="Tarih, tutar veya sayı gibi normalize edilmiş değer.",
    )
    confidence: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Alan tespitine ait güven skoru (0-1).",
    )
    source_quote: Optional[str] = Field(
        None,
        description="Ham değerin geldiği cümle veya paragraf alıntısı.",
    )


class LeaseExtractionResult(BaseModel):
    """LLM'den dönen kira sözleşmesi çıkarımı."""

    model_config = ConfigDict(extra="ignore")

    document_type: Optional[str] = Field(
        None,
        description='Belge türü, ör. "Sozlesme".',
    )
    summary: Optional[str] = Field(
        None,
        description="Kısa Türkçe özet.",
    )
    Mahal_Kodu: LeaseField[str] = Field(
        default_factory=LeaseField[str],
        description="Mağaza veya mahal kodu.",
    )
    M2: LeaseField[float] = Field(
        default_factory=LeaseField[float],
        description="Kiralanan alan metrekare cinsinden.",
    )
    Asgari_Kira: LeaseField[float] = Field(
        default_factory=LeaseField[float],
        description="Asgari kira bedeli.",
    )
    Ciro_Kira_Orani: LeaseField[float] = Field(
        default_factory=LeaseField[float],
        description="Ciro kirası yüzdesi.",
    )
    Dekorasyon_Koordinasyon: LeaseField[float] = Field(
        default_factory=LeaseField[float],
        description="Dekorasyon/koordinasyon bedeli.",
    )
    Mali_Sorumluluk_Sigortasi: LeaseField[float] = Field(
        default_factory=LeaseField[float],
        description="Mali sorumluluk sigortası bedeli veya yüzdesi.",
    )
    Gecikme_Faizi: LeaseField[float] = Field(
        default_factory=LeaseField[float],
        description="Gecikme faizi oranı.",
    )
    Bir_Yil_Uzama_Artis: LeaseField[float] = Field(
        default_factory=LeaseField[float],
        description="İlk yıl uzatma artış oranı.",
    )
    Bir_Yil_Uzama_Ciro_Kira: LeaseField[float] = Field(
        default_factory=LeaseField[float],
        description="İlk yıl uzatma sonrası ciro kirası oranı.",
    )
    Ceza_Bedeli: LeaseField[float] = Field(
        default_factory=LeaseField[float],
        description="Cezai şart bedeli.",
    )


__all__ = [
    "LeaseField",
    "LeaseExtractionResult",
]
