"""Cost calculation functions."""

from __future__ import annotations

from llm_cost_calculator.data import get_pricing_db
from llm_cost_calculator.types import CostEstimate, ModelPricing


def get_model_pricing(model_id: str) -> ModelPricing | None:
    """Get pricing for a specific model."""
    db = get_pricing_db()
    return db.get(model_id)


def list_models() -> list[str]:
    """List all model IDs."""
    return list(get_pricing_db().keys())


def list_providers() -> list[str]:
    """List all unique providers."""
    return list({m.provider for m in get_pricing_db().values()})


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    mode: str = "realtime",
) -> CostEstimate:
    """Calculate cost for a model + token count.

    Args:
        model: Model ID (e.g., "gpt-4o", "claude-sonnet-4").
        input_tokens: Number of input/prompt tokens.
        output_tokens: Number of output/completion tokens.
        mode: "realtime", "batch", or "cached".

    Returns:
        CostEstimate with breakdown.

    Raises:
        ValueError: If model not found or mode not supported.
    """
    pricing = get_model_pricing(model)
    if not pricing:
        raise ValueError(f"Model '{model}' not found in pricing database")

    if mode == "batch":
        if not pricing.batch_input_per_1m:
            raise ValueError(f"Model '{model}' does not support batch pricing")
        input_rate = pricing.batch_input_per_1m
        output_rate = pricing.batch_output_per_1m or pricing.output_per_1m
    elif mode == "cached":
        input_rate = pricing.cached_input_per_1m or pricing.input_per_1m
        output_rate = pricing.output_per_1m
    else:
        input_rate = pricing.input_per_1m
        output_rate = pricing.output_per_1m

    input_cost = (input_tokens / 1_000_000) * input_rate
    output_cost = (output_tokens / 1_000_000) * output_rate

    return CostEstimate(
        model=model,
        provider=pricing.provider,
        input_cost=round(input_cost, 6),
        output_cost=round(output_cost, 6),
        total_cost=round(input_cost + output_cost, 6),
        mode=mode,
    )


def compare_costs(
    input_tokens: int,
    output_tokens: int,
    mode: str = "realtime",
    providers: list[str] | None = None,
) -> list[CostEstimate]:
    """Compare costs across all models, sorted cheapest first."""
    results = []
    for model_id, pricing in get_pricing_db().items():
        if providers and pricing.provider not in providers:
            continue
        if mode == "batch" and not pricing.supports_batch:
            continue
        try:
            est = calculate_cost(model_id, input_tokens, output_tokens, mode)
            results.append(est)
        except ValueError:
            continue
    return sorted(results, key=lambda e: e.total_cost)


def estimate_monthly_cost(
    model: str,
    daily_requests: int,
    avg_input_tokens: int,
    avg_output_tokens: int,
    mode: str = "realtime",
) -> float:
    """Estimate monthly cost for a model given daily usage."""
    per_request = calculate_cost(model, avg_input_tokens, avg_output_tokens, mode)
    return round(per_request.total_cost * daily_requests * 30, 2)


def find_cheapest(
    input_tokens: int,
    output_tokens: int,
    *,
    mode: str = "realtime",
    provider: str | None = None,
    min_context: int | None = None,
    requires_vision: bool = False,
    requires_tools: bool = False,
) -> CostEstimate | None:
    """Find the cheapest model matching criteria."""
    db = get_pricing_db()
    candidates = []

    for model_id, pricing in db.items():
        if provider and pricing.provider != provider:
            continue
        if min_context and pricing.context_window < min_context:
            continue
        if requires_vision and not pricing.supports_vision:
            continue
        if requires_tools and not pricing.supports_tools:
            continue
        if mode == "batch" and not pricing.supports_batch:
            continue
        try:
            est = calculate_cost(model_id, input_tokens, output_tokens, mode)
            candidates.append(est)
        except ValueError:
            continue

    if not candidates:
        return None
    return min(candidates, key=lambda e: e.total_cost)
