import json
import os
import sys
import types
from pathlib import Path
from typing import Any

import pytest

os.environ.setdefault("LEASE_OPENAI_API_KEY", "test-key")

if "openai" not in sys.modules:
    openai_stub = types.ModuleType("openai")

    class _UnavailableOpenAI:  # pragma: no cover - yalnızca eksik bağımlılık durumunda
        def __init__(self, *_: Any, **__: Any) -> None:
            raise RuntimeError("OpenAI kütüphanesi yüklü değil")

    openai_stub.OpenAI = _UnavailableOpenAI  # type: ignore[attr-defined]
    sys.modules["openai"] = openai_stub

if "pypdf" not in sys.modules:
    pypdf_stub = types.ModuleType("pypdf")

    class _UnavailablePdfReader:  # pragma: no cover - yalnızca eksik bağımlılık durumunda
        def __init__(self, *_: Any, **__: Any) -> None:
            raise RuntimeError("pypdf kütüphanesi yüklü değil")

    pypdf_stub.PdfReader = _UnavailablePdfReader  # type: ignore[attr-defined]
    sys.modules["pypdf"] = pypdf_stub

if "pydantic_settings" not in sys.modules:
    pydantic_settings_stub = types.ModuleType("pydantic_settings")

    class _DummyBaseSettings:  # pragma: no cover - yalnızca eksik bağımlılık durumunda
        def __init__(self, **_: Any) -> None:  # noqa: D401 - basit placeholder
            """Yer tutucu"""

    pydantic_settings_stub.BaseSettings = _DummyBaseSettings  # type: ignore[attr-defined]
    sys.modules["pydantic_settings"] = pydantic_settings_stub

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.lease_extractor import LeaseExtractionError, extract_lease_from_pdf
from app.lease_models import LeaseExtractionResult
from app.pdf_reader import PdfReadError, read_pdf_text


class _FakePage:
    def __init__(self, text: str) -> None:
        self._text = text

    def extract_text(self) -> str:
        return self._text


class _FakeReader:
    def __init__(self, _: str) -> None:
        self.pages = [_FakePage("Merhaba"), _FakePage("Dünya")]


class _FakeMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class _FakeChoice:
    def __init__(self, content: str) -> None:
        self.message = _FakeMessage(content)


class _FakeCompletions:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def create(self, **_: Any) -> "_FakeCompletions":
        return self

    @property
    def choices(self) -> list[_FakeChoice]:  # type: ignore[override]
        return [_FakeChoice(json.dumps(self._payload))]


class _FakeChat:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.completions = _FakeCompletions(payload)


class _FakeClient:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.chat = _FakeChat(payload)


def test_read_pdf_text_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    monkeypatch.setattr("app.pdf_reader.PdfReader", _FakeReader)

    text = read_pdf_text(str(pdf_file))

    assert text == "Merhaba\nDünya"


def test_read_pdf_text_missing_file() -> None:
    with pytest.raises(PdfReadError):
        read_pdf_text("/non/existent.pdf")


def test_extract_lease_from_pdf(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_text("dummy")

    fake_payload = {
        "document_type": "Sozlesme",
        "summary": "Kısa özet",
        "Mahal_Kodu": {"raw": "A101", "normalized": "A101", "confidence": 0.9},
        "M2": {"raw": "120 m2", "normalized": 120.0, "confidence": 0.8},
        "Asgari_Kira": {"raw": "50.000 TL", "normalized": 50000.0, "confidence": 0.7},
        "Ciro_Kira_Orani": {"raw": "%5", "normalized": 5.0, "confidence": 0.6},
        "Dekorasyon_Koordinasyon": {"raw": "10.000", "normalized": 10000.0, "confidence": 0.5},
        "Mali_Sorumluluk_Sigortasi": {"raw": "2.000", "normalized": 2000.0, "confidence": 0.5},
        "Gecikme_Faizi": {"raw": "%2", "normalized": 2.0, "confidence": 0.5},
        "Bir_Yil_Uzama_Artis": {"raw": "%15", "normalized": 15.0, "confidence": 0.5},
        "Bir_Yil_Uzama_Ciro_Kira": {"raw": "%6", "normalized": 6.0, "confidence": 0.5},
        "Ceza_Bedeli": {"raw": "5.000", "normalized": 5000.0, "confidence": 0.5},
    }

    monkeypatch.setattr("app.lease_extractor.read_pdf_text", lambda path: f"PDF: {path}")
    fake_client = _FakeClient(fake_payload)

    result = extract_lease_from_pdf(str(pdf_file), client=fake_client)

    assert isinstance(result, LeaseExtractionResult)
    assert result.document_type == "Sozlesme"
    assert result.Mahal_Kodu.normalized == "A101"
    assert result.M2.normalized == 120.0


def test_extract_lease_from_pdf_invalid_json(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_text("dummy")

    class _InvalidCompletions:
        def create(self, **_: Any) -> "_InvalidCompletions":
            return self

        @property
        def choices(self) -> list[_FakeChoice]:  # type: ignore[override]
            return [_FakeChoice("not-json")]

    class _InvalidClient:
        def __init__(self) -> None:
            self.chat = type("_Chat", (), {"completions": _InvalidCompletions()})()

    monkeypatch.setattr("app.lease_extractor.read_pdf_text", lambda _: "text")

    with pytest.raises(LeaseExtractionError):
        extract_lease_from_pdf(str(pdf_file), client=_InvalidClient())
