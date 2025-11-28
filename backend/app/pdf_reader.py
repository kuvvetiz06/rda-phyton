"""PDF reading utilities."""

from __future__ import annotations

from typing import Callable


class PDFReader:
    """Simple PDF reader abstraction.

    The reader uses a configurable parser callable to convert raw PDF bytes
    into text. The default parser performs a best-effort UTF-8 decode so the
    class can be used in tests without requiring external dependencies.
    """

    def __init__(self, parser: Callable[[bytes], str] | None = None) -> None:
        self._parser = parser or self._default_parser

    def read_text(self, content: bytes) -> str:
        """Return plain text extracted from the given PDF bytes."""

        text = self._parser(content)
        return text.strip()

    @staticmethod
    def _default_parser(content: bytes) -> str:
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return ""
