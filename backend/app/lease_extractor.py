"""Logic for extracting lease data from documents."""

from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from app.pdf_reader import PDFReader
from app.lease_models import LeaseDocument, LeaseParty, LeaseTerm
from app.lease_schema import LeaseDocumentSchema, LeasePartySchema, LeaseTermSchema


class LeaseExtractor:
    """Extract structured lease information from PDF content."""

    def __init__(self, reader: PDFReader | None = None) -> None:
        self.reader = reader or PDFReader()

    def extract(self, content: bytes) -> LeaseDocumentSchema:
        """Parse raw PDF bytes and return structured lease data."""

        raw_text = self.reader.read_text(content)
        lease_document = self._build_document(raw_text)
        return self._serialize(lease_document)

    def _build_document(self, raw_text: str) -> LeaseDocument:
        """Create a LeaseDocument from raw text using placeholder heuristics."""

        parties = self._extract_parties(raw_text)
        terms = self._extract_terms(raw_text)
        return LeaseDocument(parties=parties, terms=terms, raw_text=raw_text)

    def _extract_parties(self, raw_text: str) -> list[LeaseParty]:
        """Derive lease parties from the text."""

        if not raw_text:
            return []

        placeholder_roles: Iterable[str] = ("landlord", "tenant")
        return [LeaseParty(name=role.title(), role=role) for role in placeholder_roles]

    def _extract_terms(self, raw_text: str) -> LeaseTerm:
        """Derive lease terms from the text."""

        if not raw_text:
            return LeaseTerm()

        return LeaseTerm(rent_amount=0.0, currency="USD", payment_frequency="monthly")

    @staticmethod
    def _serialize(document: LeaseDocument) -> LeaseDocumentSchema:
        party_schemas = [LeasePartySchema(**asdict(party)) for party in document.parties]
        term_schema = LeaseTermSchema(**asdict(document.terms))
        return LeaseDocumentSchema(parties=party_schemas, terms=term_schema, raw_text=document.raw_text)
