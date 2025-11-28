"""Pydantic schemas for lease extraction API responses."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class LeasePartySchema(BaseModel):
    name: str
    role: str


class LeaseTermSchema(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    rent_amount: Optional[float] = None
    currency: str = "USD"
    payment_frequency: str = "monthly"


class LeaseDocumentSchema(BaseModel):
    parties: List[LeasePartySchema] = []
    terms: LeaseTermSchema = LeaseTermSchema()
    raw_text: str = ""
