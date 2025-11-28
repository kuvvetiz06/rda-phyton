"""LeaseExtractionResult için JSON Schema tanımı."""

from __future__ import annotations

from app.lease_models import LeaseExtractionResult

# Pydantic'in ürettiği JSON Schema, OpenAI structured outputs ile
# birebir uyumludur. Schema nesnesi response_format altında kullanılacaktır.
lease_json_schema = LeaseExtractionResult.model_json_schema()

__all__ = ["lease_json_schema"]
