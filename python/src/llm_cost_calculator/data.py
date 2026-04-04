"""Loads pricing data from the bundled JSON database."""

from __future__ import annotations

import json
from pathlib import Path

from llm_cost_calculator.types import ModelPricing

_db_cache: dict[str, ModelPricing] | None = None

DATA_PATH = Path(__file__).parent.parent.parent.parent / "data" / "pricing.json"


def get_pricing_db() -> dict[str, ModelPricing]:
    """Load and cache the pricing database."""
    global _db_cache
    if _db_cache is not None:
        return _db_cache

    with open(DATA_PATH) as f:
        raw = json.load(f)

    _db_cache = {}
    for m in raw["models"]:
        p = m.get("pricing", {})
        _db_cache[m["id"]] = ModelPricing(
            id=m["id"],
            provider=m["provider"],
            display_name=m.get("display_name", m["id"]),
            tier=m.get("tier", "mid"),
            input_per_1m=p.get("input_per_1m_tokens", 0),
            output_per_1m=p.get("output_per_1m_tokens", 0),
            cached_input_per_1m=p.get("cached_input_per_1m_tokens"),
            batch_input_per_1m=p.get("batch_input_per_1m_tokens"),
            batch_output_per_1m=p.get("batch_output_per_1m_tokens"),
            context_window=m.get("context_window", 0),
            max_output_tokens=m.get("max_output_tokens", 0),
            supports_vision=m.get("supports_vision", False),
            supports_tools=m.get("supports_tools", False),
            supports_batch=m.get("supports_batch", False),
        )

    return _db_cache
