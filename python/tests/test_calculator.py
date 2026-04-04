"""Tests for LLM cost calculator."""

import pytest
from llm_cost_calculator import calculate_cost, compare_costs, get_model_pricing, list_models, list_providers, find_cheapest, estimate_monthly_cost


def test_list_models():
    models = list_models()
    assert len(models) >= 20
    assert "gpt-4o" in models
    assert "claude-sonnet-4" in models


def test_list_providers():
    providers = list_providers()
    assert "openai" in providers
    assert "anthropic" in providers
    assert "google" in providers


def test_get_model_pricing():
    p = get_model_pricing("gpt-4o")
    assert p is not None
    assert p.provider == "openai"
    assert p.input_per_1m > 0


def test_get_unknown_model():
    assert get_model_pricing("nonexistent-model") is None


def test_calculate_realtime():
    est = calculate_cost("gpt-4o", input_tokens=1000, output_tokens=500)
    assert est.model == "gpt-4o"
    assert est.mode == "realtime"
    assert est.total_cost > 0
    assert est.total_cost == est.input_cost + est.output_cost


def test_calculate_batch():
    realtime = calculate_cost("gpt-4o", 1000, 500, mode="realtime")
    batch = calculate_cost("gpt-4o", 1000, 500, mode="batch")
    assert batch.total_cost < realtime.total_cost  # Batch should be cheaper


def test_calculate_cached():
    realtime = calculate_cost("claude-sonnet-4", 1000, 500, mode="realtime")
    cached = calculate_cost("claude-sonnet-4", 1000, 500, mode="cached")
    assert cached.total_cost < realtime.total_cost  # Cached input should be cheaper


def test_calculate_unknown_model_raises():
    with pytest.raises(ValueError, match="not found"):
        calculate_cost("fake-model", 1000, 500)


def test_compare_costs():
    results = compare_costs(1000, 500)
    assert len(results) > 5
    # Should be sorted cheapest first
    for i in range(len(results) - 1):
        assert results[i].total_cost <= results[i + 1].total_cost


def test_compare_costs_filter_provider():
    results = compare_costs(1000, 500, providers=["anthropic"])
    assert all(r.provider == "anthropic" for r in results)


def test_find_cheapest():
    cheapest = find_cheapest(1000, 500)
    assert cheapest is not None
    assert cheapest.total_cost > 0


def test_find_cheapest_with_vision():
    cheapest = find_cheapest(1000, 500, requires_vision=True)
    assert cheapest is not None


def test_estimate_monthly():
    monthly = estimate_monthly_cost("gpt-4o-mini", daily_requests=1000, avg_input_tokens=500, avg_output_tokens=200)
    assert monthly > 0
    assert monthly < 1000  # Sanity check — shouldn't be astronomical
