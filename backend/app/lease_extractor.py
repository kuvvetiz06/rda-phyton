"""PDF'ten kira sözleşmesi alan çıkarımı için servis fonksiyonları."""

from __future__ import annotations

import json
from typing import Iterable

from openai import OpenAI
from pydantic import ValidationError

from app.config import settings
from app.lease_models import LeaseExtractionResult
from app.lease_schema import lease_json_schema
from app.pdf_reader import PdfReadError, read_pdf_text

SYSTEM_PROMPT = (
    "Aşağıdaki PDF metninden kira/mağaza sözleşmesi alanlarını çıkar. "
    "Türkçe çalış ve belirsiz kaldığında normalized alanlarını null bırak, "
    "confidence değerini düşük ver."
)


class LeaseExtractionError(RuntimeError):
    """LLM veya doğrulama hatalarında fırlatılır."""


def build_user_prompt(text: str) -> str:
    """LLM'e gönderilecek kullanıcı mesajını hazırlar."""

    instructions: Iterable[str] = (
        "Metni dikkatlice incele ve istenen alanları doldur.",
        "Belirsiz sayısal değerleri normalize edemiyorsan normalized alanını null bırak.",
        "Tüm çıktı Türkçe olmalı.",
        "Ham alıntılarda ilgili cümleleri kullan.",
    )
    prefix = "\n".join(f"- {item}" for item in instructions)
    return f"Talimatlar:\n{prefix}\n\nPDF Metni:\n{text.strip()}"


def _parse_llm_response(payload: str) -> LeaseExtractionResult:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:  # pragma: no cover - savunma
        raise LeaseExtractionError("LLM yanıtı JSON formatında değil") from exc

    try:
        return LeaseExtractionResult.model_validate(data)
    except ValidationError as exc:
        raise LeaseExtractionError("LLM yanıtı beklenen şema ile uyuşmuyor") from exc


def extract_lease_from_pdf(pdf_path: str, client: OpenAI | None = None) -> LeaseExtractionResult:
    """PDF yolundan kira alanlarını çıkarır."""

    try:
        text = read_pdf_text(pdf_path)
    except PdfReadError as exc:
        raise LeaseExtractionError(str(exc)) from exc

    if not text:
        raise LeaseExtractionError("PDF metni boş")

    api_client = client or OpenAI(api_key=settings.openai_api_key)
    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(text)},
    ]

    try:
        response = api_client.chat.completions.create(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "lease_extraction",
                    "schema": lease_json_schema,
                    "strict": True,
                },
            },
        )
    except Exception as exc:  # pragma: no cover - OpenAI hata türü ortama bağlı
        raise LeaseExtractionError("LLM isteği başarısız oldu") from exc

    choice = response.choices[0].message
    if not choice.content:
        raise LeaseExtractionError("LLM boş yanıt döndürdü")

    return _parse_llm_response(choice.content)


__all__ = ["extract_lease_from_pdf", "LeaseExtractionError"]
