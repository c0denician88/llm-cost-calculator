"""Tests for the Anoman AI gateway cost model."""

import pytest
from llm_cost_calculator import (
    list_anoman_tiers, weighted_tokens, weighted_tokens_for_model,
    anoman_token_cost, estimate_monthly_anoman_cost, recommend_anoman_tier,
    calculate_cost,
)


def test_list_anoman_tiers():
    tiers = list_anoman_tiers()
    ids = {t.id for t in tiers}
    assert {"starter", "pro", "payg", "enterprise"} <= ids
    starter = next(t for t in tiers if t.id == "starter")
    assert starter.platform_fee_usd_month == 12
    assert starter.included_weighted_tokens == 500_000
    assert starter.model_access == ["budget"]
    pro = next(t for t in tiers if t.id == "pro")
    assert pro.included_weighted_tokens == 20_000_000
    assert "premium" in pro.model_access


def test_weighted_tokens_formula():
    # budget/cloud_direct/realtime = all multipliers 1 → weighted == raw
    assert weighted_tokens(1000, "budget", "cloud_direct", "realtime") == 1000
    # premium multiplier is 17
    assert weighted_tokens(1000, "premium") == 17_000
    # batch halves the weight; local_id provider is 0.3
    assert weighted_tokens(1000, "mid", "local_id", "batch") == 1000 * 4 * 0.3 * 0.5
    # cache_hit is free
    assert weighted_tokens(1000, "ultra", "cloud_direct", "cache_hit") == 0.0


def test_weighted_tokens_unknown_raises():
    with pytest.raises(ValueError):
        weighted_tokens(1000, model_class="nope")


def test_weighted_tokens_for_model_resolves_class():
    # gpt-4o is tier "mid" → multiplier 4
    assert weighted_tokens_for_model("gpt-4o", 1000) == 4000
    # gpt-4o-mini is tier "budget" → multiplier 1
    assert weighted_tokens_for_model("gpt-4o-mini", 1000) == 1000


def test_anoman_token_cost_is_zero_markup():
    # Anoman charges provider price for tokens (0% markup) → identical to calculate_cost.
    a = anoman_token_cost("gpt-4o", 10_000, 5_000)
    b = calculate_cost("gpt-4o", 10_000, 5_000)
    assert a.total_cost == b.total_cost


def test_monthly_cost_starter_within_cap():
    e = estimate_monthly_anoman_cost(400_000, "starter")
    assert e["feasible"] is True
    assert e["total_usd"] == 12


def test_monthly_cost_starter_hard_cap_exceeded():
    e = estimate_monthly_anoman_cost(600_000, "starter")
    assert e["feasible"] is False
    assert e["total_usd"] is None


def test_monthly_cost_pro_within_allowance():
    e = estimate_monthly_anoman_cost(10_000_000, "pro")
    assert e["total_usd"] == 39
    assert e["overage_usd"] == 0.0


def test_monthly_cost_pro_overage():
    # 25M weighted = 5M over the 20M allowance @ $1.20/1M = $6 overage
    e = estimate_monthly_anoman_cost(25_000_000, "pro")
    assert e["overage_usd"] == 6.0
    assert e["total_usd"] == 45.0


def test_monthly_cost_payg_is_usage_based():
    e = estimate_monthly_anoman_cost(999, "payg")
    assert e["platform_fee_usd"] == 9
    assert e["total_usd"] is None  # depends on raw usage


def test_recommend_small_workload_is_starter():
    r = recommend_anoman_tier(300_000)
    assert r["recommended"] == "starter"
    assert r["recommended_total_usd"] == 12


def test_recommend_mid_workload_is_pro():
    r = recommend_anoman_tier(5_000_000)
    assert r["recommended"] == "pro"
    assert r["recommended_total_usd"] == 39


def test_recommend_over_starter_cap_skips_starter():
    # 1M weighted exceeds Starter's 500K cap → Starter infeasible → Pro wins.
    r = recommend_anoman_tier(1_000_000)
    assert r["recommended"] == "pro"
    assert r["tiers"]["starter"]["feasible"] is False
