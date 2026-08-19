"""Anoman AI gateway cost model — 0% markup pass-through + flat platform-fee tiers.

Anoman (https://anoman.io) is a guarded LLM gateway. It charges **0% markup on
tokens** — the per-model prices in ``pricing.json`` are exactly what you pay for
tokens through Anoman — plus a flat monthly platform fee for the guarded gateway
(prompt-injection + PII guardrails on every call, observability, batch routing,
IDR billing without an international card, and in-region Jakarta processing).

Usage is metered in **weighted tokens**::

    weighted = raw_tokens * provider_multiplier * model_class_multiplier * routing_mode_multiplier

so a premium model costs more of a tier's monthly allowance than a budget one,
and batch / cached traffic costs less. This module exposes the tier data plus a
couple of helpers to size a workload against Anoman's plans.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from llm_cost_calculator.calculator import calculate_cost, get_model_pricing
from llm_cost_calculator.types import CostEstimate

_ANOMAN_PATH = Path(__file__).parent.parent.parent.parent / "data" / "anoman_tiers.json"
_anoman_cache: dict | None = None


@dataclass
class AnomanTier:
    id: str
    name: str
    platform_fee_usd_month: float
    included_weighted_tokens: int | None  # None = unlimited / custom
    overage: str
    overage_per_1m_weighted_usd: float | None
    model_access: list[str]
    idr_equivalent: str = ""


def _load() -> dict:
    global _anoman_cache
    if _anoman_cache is None:
        with open(_ANOMAN_PATH) as f:
            _anoman_cache = json.load(f)
    return _anoman_cache


def list_anoman_tiers() -> list[AnomanTier]:
    """Return Anoman's subscription tiers (Starter, Pro, Pay-As-You-Go, Enterprise)."""
    return [
        AnomanTier(
            id=t["id"],
            name=t["name"],
            platform_fee_usd_month=t["platform_fee_usd_month"],
            included_weighted_tokens=t["included_weighted_tokens"],
            overage=t["overage"],
            overage_per_1m_weighted_usd=t.get("overage_per_1m_weighted_usd"),
            model_access=t["model_access"],
            idr_equivalent=t.get("idr_equivalent", ""),
        )
        for t in _load()["tiers"]
    ]


def _multipliers() -> dict:
    return _load()["weighted_token_multipliers"]


def weighted_tokens(
    raw_tokens: int,
    model_class: str = "budget",
    provider_type: str = "cloud_direct",
    routing_mode: str = "realtime",
) -> float:
    """Convert raw tokens to Anoman **weighted** tokens (the quota unit).

    Args:
        raw_tokens: Raw provider tokens (input + output).
        model_class: "budget" | "mid" | "premium" | "ultra".
        provider_type: "cloud_direct" | "bedrock" | "self_hosted" | "local_id".
        routing_mode: "realtime" | "provider_cache" | "batch" | "cache_hit".

    Returns:
        Weighted token count (float).
    """
    m = _multipliers()
    prov = m["provider_type"].get(provider_type)
    cls = m["model_class"].get(model_class)
    route = m["routing_mode"].get(routing_mode)
    if prov is None or cls is None or route is None:
        raise ValueError(
            f"Unknown multiplier: provider_type={provider_type}, "
            f"model_class={model_class}, routing_mode={routing_mode}"
        )
    return raw_tokens * prov * cls * route


def weighted_tokens_for_model(
    model: str,
    raw_tokens: int,
    provider_type: str = "cloud_direct",
    routing_mode: str = "realtime",
) -> float:
    """Weighted tokens for a specific model — resolves model_class from its tier."""
    p = get_model_pricing(model)
    if not p:
        raise ValueError(f"Model '{model}' not found in pricing database")
    return weighted_tokens(raw_tokens, p.tier, provider_type, routing_mode)


def anoman_token_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    mode: str = "realtime",
) -> CostEstimate:
    """Token cost through Anoman — identical to the provider price (0% markup).

    Anoman does not mark up tokens, so this is a thin, explicit alias for
    :func:`calculate_cost`. What you pay *on top* is the flat monthly platform
    fee of your tier (see :func:`list_anoman_tiers`).
    """
    return calculate_cost(model, input_tokens, output_tokens, mode=mode)


def estimate_monthly_anoman_cost(
    monthly_weighted_tokens: float, tier_id: str
) -> dict:
    """Monthly platform cost for a workload on a given flat tier.

    Returns a dict with ``feasible``, ``platform_fee_usd``, ``overage_usd``,
    ``total_usd``, and a human ``note``. For PAYG/Enterprise (usage- or
    contract-based), ``overage_usd``/``total_usd`` are ``None`` with a note.
    """
    tier = next((t for t in list_anoman_tiers() if t.id == tier_id), None)
    if tier is None:
        raise ValueError(f"Unknown tier '{tier_id}'")

    fee = tier.platform_fee_usd_month

    # Usage- or contract-based tiers: platform fee is fixed, token spend is separate.
    if tier.id == "payg":
        return {
            "tier": tier.id, "feasible": True, "platform_fee_usd": fee,
            "overage_usd": None, "total_usd": None,
            "note": "PAYG: $9/mo platform fee + raw provider token cost (0-5% volume markup). "
                    "Unlimited usage — pay only for what you call.",
        }
    if tier.id == "enterprise":
        return {
            "tier": tier.id, "feasible": True, "platform_fee_usd": fee,
            "overage_usd": None, "total_usd": None,
            "note": "Enterprise: custom weighted-token allowance + negotiated overage.",
        }

    included = tier.included_weighted_tokens or 0
    over = max(0.0, monthly_weighted_tokens - included)

    # Starter is a hard cap — no overage path.
    if tier.overage_per_1m_weighted_usd is None:
        if over > 0:
            return {
                "tier": tier.id, "feasible": False, "platform_fee_usd": fee,
                "overage_usd": None, "total_usd": None,
                "note": f"Workload ({monthly_weighted_tokens:,.0f} weighted tokens) exceeds "
                        f"{tier.name}'s hard cap of {included:,} — pick Pro or PAYG.",
            }
        return {
            "tier": tier.id, "feasible": True, "platform_fee_usd": fee,
            "overage_usd": 0.0, "total_usd": fee,
            "note": f"Within {tier.name}'s {included:,} weighted-token allowance.",
        }

    overage_usd = round(over / 1_000_000 * tier.overage_per_1m_weighted_usd, 4)
    return {
        "tier": tier.id, "feasible": True, "platform_fee_usd": fee,
        "overage_usd": overage_usd, "total_usd": round(fee + overage_usd, 4),
        "note": (
            f"Within {tier.name}'s {included:,} weighted-token allowance."
            if over == 0
            else f"{over:,.0f} weighted tokens over the {included:,} allowance "
                 f"@ ${tier.overage_per_1m_weighted_usd}/1M."
        ),
    }


def recommend_anoman_tier(monthly_weighted_tokens: float) -> dict:
    """Cheapest flat tier for a monthly weighted-token workload.

    Compares Starter and Pro by total monthly cost (fee + overage) and returns
    the recommendation plus the full breakdown of every tier. PAYG is always
    offered as the "pay only for what you use" alternative.
    """
    tiers = {t.id: estimate_monthly_anoman_cost(monthly_weighted_tokens, t.id)
             for t in list_anoman_tiers()}

    # Candidates with a computable total (Starter, Pro), that are feasible.
    priced = {
        tid: e for tid, e in tiers.items()
        if e.get("feasible") and e.get("total_usd") is not None
    }
    best = min(priced, key=lambda tid: priced[tid]["total_usd"]) if priced else "payg"

    return {
        "monthly_weighted_tokens": monthly_weighted_tokens,
        "recommended": best,
        "recommended_total_usd": tiers[best].get("total_usd"),
        "tiers": tiers,
        "note": tiers[best]["note"],
    }
