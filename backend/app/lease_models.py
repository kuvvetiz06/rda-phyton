"""Domain models for lease data."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class LeaseParty:
    """Represents one party in the lease agreement."""

    name: str
    role: str


@dataclass
class LeaseTerm:
    """Captures the primary financial terms of a lease."""

    start_date: Optional[date] = None
    end_date: Optional[date] = None
    rent_amount: Optional[float] = None
    currency: str = "USD"
    payment_frequency: str = "monthly"


@dataclass
class LeaseDocument:
    """Aggregated lease information extracted from a source document."""

    parties: List[LeaseParty] = field(default_factory=list)
    terms: LeaseTerm = field(default_factory=LeaseTerm)
    raw_text: str = ""
