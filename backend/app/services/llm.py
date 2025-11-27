import json
from typing import Dict

import requests

from app.config import settings
from app.models.schemas import LLMResult


PROMPT_TEMPLATE = """
You are a concise assistant helping summarize OCR extracted content.
Given the content below, produce a JSON object with two fields:
- "summary": a 2-3 sentence overview
- "key_points": an array of bullet-point style strings highlighting the most important items.

Respond with ONLY valid JSON that can be parsed by a standard JSON parser.

Content:
{content}
"""


def _clean_json_block(raw_text: str) -> str:
    text = raw_text.strip()
    if text.startswith("```"):
        # remove code fences
        text = text.strip("`")
        # possible prefix like json\n
        if "json" in text.split("\n", 1)[0].lower():
            text = text.split("\n", 1)[1] if "\n" in text else ""
    return text.strip()


def _parse_response(raw_text: str) -> LLMResult:
    cleaned = _clean_json_block(raw_text)
    try:
        data = json.loads(cleaned)
        summary = data.get("summary", "")
        key_points = data.get("key_points", [])
        if not isinstance(key_points, list):
            key_points = [str(key_points)]
        return LLMResult(summary=str(summary), key_points=[str(k) for k in key_points])
    except json.JSONDecodeError:
        # fallback: create simple result from text
        lines = [line.strip("- ") for line in cleaned.splitlines() if line.strip()]
        summary = lines[0] if lines else cleaned
        key_points = lines[1:]
        return LLMResult(summary=summary, key_points=key_points)


def analyze_text(content: str) -> LLMResult:
    prompt = PROMPT_TEMPLATE.format(content=content)

    payload: Dict[str, object] = {
        "model": settings.llm_model_name,
        "prompt": prompt,
        "stream": False,
    }

    response = requests.post(f"{settings.ollama_base_url}/api/generate", json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    raw_text = data.get("response", "")

    return _parse_response(raw_text)
