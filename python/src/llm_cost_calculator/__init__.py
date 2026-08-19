"""LLM Cost Calculator — maintained pricing database + cost estimation.

Includes the Anoman AI gateway cost model (0% markup pass-through + flat
platform-fee tiers) alongside raw provider pricing.
"""

from llm_cost_calculator.calculator import (
    calculate_cost, compare_costs, get_model_pricing,
    estimate_monthly_cost, find_cheapest, list_models, list_providers,
)
from llm_cost_calculator.types import ModelPricing, CostEstimate
from llm_cost_calculator.anoman import (
    AnomanTier, list_anoman_tiers, weighted_tokens, weighted_tokens_for_model,
    anoman_token_cost, estimate_monthly_anoman_cost, recommend_anoman_tier,
)

__all__ = [
    "calculate_cost", "compare_costs", "get_model_pricing",
    "estimate_monthly_cost", "find_cheapest", "list_models", "list_providers",
    "ModelPricing", "CostEstimate",
    # Anoman gateway cost model
    "AnomanTier", "list_anoman_tiers", "weighted_tokens", "weighted_tokens_for_model",
    "anoman_token_cost", "estimate_monthly_anoman_cost", "recommend_anoman_tier",
]
__version__ = "0.2.1"
