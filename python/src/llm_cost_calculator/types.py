"""Types for LLM cost calculator."""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ModelPricing:
    id: str
    provider: str
    display_name: str
    tier: str
    input_per_1m: float
    output_per_1m: float
    cached_input_per_1m: float | None = None
    batch_input_per_1m: float | None = None
    batch_output_per_1m: float | None = None
    context_window: int = 0
    max_output_tokens: int = 0
    supports_vision: bool = False
    supports_tools: bool = False
    supports_batch: bool = False


@dataclass
class CostEstimate:
    model: str
    provider: str
    input_cost: float
    output_cost: float
    total_cost: float
    mode: str = "realtime"
