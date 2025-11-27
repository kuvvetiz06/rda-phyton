from typing import List

from pydantic import BaseModel


class LLMResult(BaseModel):
    summary: str
    key_points: List[str]


class ProcessResponse(BaseModel):
    text: str
    summary: str
    key_points: List[str]
