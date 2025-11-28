"""PDF okuma yardımcıları."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


class PdfReadError(RuntimeError):
    """PDF metni okunamadığında fırlatılır."""


def read_pdf_text(pdf_path: str) -> str:
    """PDF dosyasından basit metin çıkarır.

    Parameters
    ----------
    pdf_path: str
        Okunacak PDF dosyasının yolu.

    Returns
    -------
    str
        PDF sayfalarından birleştirilmiş metin.

    Raises
    ------
    PdfReadError
        Dosya erişimi, bozuk PDF veya metin çıkarma hatalarında.
    """

    path = Path(pdf_path)
    if not path.exists():
        raise PdfReadError(f"PDF bulunamadı: {pdf_path}")

    try:
        reader = PdfReader(str(path))
    except Exception as exc:  # pragma: no cover - pypdf özel hatası bağlama bağlı
        raise PdfReadError(f"PDF açılamadı: {pdf_path}") from exc

    texts: list[str] = []
    try:
        for page in reader.pages:
            page_text = page.extract_text() or ""
            texts.append(page_text.strip())
    except Exception as exc:  # pragma: no cover - pypdf özel hatası bağlama bağlı
        raise PdfReadError("PDF metni çıkarılırken hata oluştu") from exc

    combined = "\n".join(filter(None, texts)).strip()
    if not combined:
        raise PdfReadError("PDF'den metin çıkarılamadı")

    return combined


__all__ = ["read_pdf_text", "PdfReadError"]
