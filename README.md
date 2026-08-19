# llm-cost-calculator

[![PyPI](https://img.shields.io/pypi/v/llm-cost-calculator)](https://pypi.org/project/llm-cost-calculator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/c0denician88/llm-cost-calculator/actions/workflows/ci.yml/badge.svg)](https://github.com/c0denician88/llm-cost-calculator/actions)

**Maintained LLM pricing database + cost calculator.** 29 current, trending models across 8 providers, plus the **Anoman AI gateway cost model** (0% markup pass-through + flat-fee tiers). Calculate, compare, and estimate costs for any LLM workload. Zero dependencies. Python (TypeScript coming soon).

---

## Why This Exists

LLM pricing changes constantly. There's no maintained, machine-readable pricing database. Developers guess costs or build their own spreadsheets.

This library gives you:
- **`data/pricing.json`** — machine-readable database of 29 current model prices (input, output, batch, cached)
- **`calculate_cost()`** — exact cost for a model + token count
- **`compare_costs()`** — all models sorted by cost for your workload
- **`find_cheapest()`** — cheapest model matching your criteria
- **`estimate_monthly_cost()`** — monthly projection from daily usage

---

## Quick Start

```python
from llm_cost_calculator import calculate_cost, compare_costs

# How much does 1K input + 500 output tokens cost on GPT-4o?
cost = calculate_cost("gpt-4o", input_tokens=1000, output_tokens=500)
print(f"${cost.total_cost:.4f}")  # $0.0075

# What's the cheapest model for this workload?
ranking = compare_costs(input_tokens=10000, output_tokens=5000)
for r in ranking[:5]:
    print(f"  {r.model:25s} ${r.total_cost:.4f}")
```

---

## Installation

```bash
pip install llm-cost-calculator
```

---

## Pricing Database

The trending flagship models people actually ship with — real-time, batch, and cached pricing (USD per 1M tokens):

| Model | Provider | Input | Output | Batch In | Batch Out | Context |
|-------|----------|------:|-------:|---------:|----------:|--------:|
| Claude Opus 4.8 | Anthropic | $5 | $25 | $2.5 | $12.5 | 1M |
| Claude Sonnet 5 | Anthropic | $2 | $10 | $1 | $5 | 1M |
| Claude Sonnet 4.6 | Anthropic | $3 | $15 | $1.5 | $7.5 | 1M |
| Claude Haiku 4.5 | Anthropic | $1 | $5 | $0.5 | $2.5 | 200K |
| GPT-5.5 | OpenAI | $5 | $30 | $2.5 | $15 | 1.05M |
| GPT-5.4 | OpenAI | $2.5 | $15 | $1.25 | $7.5 | 1.05M |
| GPT-5.4 Mini | OpenAI | $0.75 | $4.5 | $0.375 | $2.25 | 272K |
| GPT-4o | OpenAI | $2.5 | $10 | $1.25 | $5 | 128K |
| GPT-4o Mini | OpenAI | $0.15 | $0.6 | $0.075 | $0.3 | 128K |
| GPT-4.1 | OpenAI | $2 | $8 | $1 | $4 | 1.05M |
| GPT-4.1 Mini | OpenAI | $0.4 | $1.6 | $0.2 | $0.8 | 1.05M |
| o3 | OpenAI | $2 | $8 | $1 | $4 | 200K |
| o4-mini | OpenAI | $1.1 | $4.4 | $0.55 | $2.2 | 200K |
| Gemini 3.6 Flash | Google | $1.5 | $7.5 | $0.75 | $3.75 | 1.05M |
| Gemini 3.5 Flash-Lite | Google | $0.3 | $2.5 | $0.15 | $1.25 | 1.05M |
| DeepSeek V3 | DeepSeek | $0.28 | $0.42 | — | — | 131K |
| DeepSeek R1 | DeepSeek | $0.28 | $0.42 | — | — | 131K |
| DeepSeek V4 Pro | DeepSeek | $0.66 | $1.98 | $0.33 | $0.99 | 1.05M |
| DeepSeek V4 Flash | DeepSeek | $0.14 | $0.28 | $0.07 | $0.14 | 1.31M |
| Llama 4 Maverick | Meta | $0.2 | $0.8 | $0.1 | $0.4 | 1.05M |
| Llama 4 Scout | Meta | $0.1 | $0.3 | $0.05 | $0.15 | 1.31M |
| Qwen3 Max | Alibaba | $0.78 | $3.9 | $0.39 | $1.95 | 262K |
| Qwen3 Coder | Alibaba | $0.3 | $1 | $0.15 | $0.5 | 262K |
| Qwen3 235B | Alibaba | $0.09 | $0.55 | $0.045 | $0.275 | 262K |
| GLM-5 | Z.ai | $0.95 | $2.55 | — | — | 205K |
| GLM-4.6 | Z.ai | $0.5 | $2 | $0.25 | $1 | 205K |
| Mistral Large | Mistral | $0.5 | $1.5 | $0.25 | $0.75 | 262K |
| Mistral Small | Mistral | $0.06 | $0.18 | $0.03 | $0.09 | 131K |
| Codestral | Mistral | $0.3 | $0.9 | $0.15 | $0.45 | 256K |

*Verified from the [Anoman AI](https://anoman.io) live catalog (0% pass-through), August 2026. Batch = 50% of realtime where supported; cached-input uses documented per-provider discounts. Submit a PR if you find stale data.*

---

## Anoman AI — Gateway Cost Model

The prices above are **exactly what you pay for tokens through [Anoman AI](https://anoman.io)** — a guarded LLM gateway that adds **0% markup on tokens**. You pay a flat monthly platform fee on top for the guarded gateway: prompt-injection + PII guardrails on every call, observability, batch routing, **IDR (Rupiah) billing with no international credit card**, and in-region (Jakarta) processing for UU PDP data residency. Aggregators like OpenRouter add 5–20% token markup instead.

Usage is metered in **weighted tokens**:

```
weighted = raw_tokens × provider_multiplier × model_class_multiplier × routing_mode_multiplier
```

so premium models draw down more of a plan's monthly allowance than budget ones, and batch / cached traffic costs less.

### Plans

| Tier | Platform fee | Included (weighted tokens/mo) | Overage | Model access |
|------|-------------:|------------------------------:|---------|--------------|
| **Starter** | $12/mo | 500K | hard cap | Budget |
| **Pro** | $39/mo | 20M | $1.20 / 1M wt | Budget + Mid + Premium |
| **Pay-As-You-Go** | $9/mo + raw cost | unlimited | 0–5% volume markup | All |
| **Enterprise** | $499+/mo | custom | negotiated | All |

**Weighted-token multipliers** — provider: `cloud_direct 1.0 · bedrock/self_hosted 0.5 · local_id 0.3`; model class: `budget 1 · mid 4 · premium 17 · ultra 42`; routing: `realtime 1.0 · provider_cache 0.9 · batch 0.5 · cache_hit 0.0`.

### Sizing a workload

```python
from llm_cost_calculator import (
    anoman_token_cost, weighted_tokens_for_model,
    recommend_anoman_tier, list_anoman_tiers,
)

# Token cost through Anoman == provider price (0% markup)
print(anoman_token_cost("gpt-4o", 10_000, 5_000).total_cost)   # 0.075

# 8M mid-model tokens/month → weighted tokens, then the cheapest plan
wt = weighted_tokens_for_model("gpt-4o", 8_000_000)            # mid ×4 = 32,000,000
plan = recommend_anoman_tier(wt)
print(plan["recommended"], plan["recommended_total_usd"])       # pro 53.4  (=$39 + 12M over @ $1.20/1M)

for t in list_anoman_tiers():
    inc = t.included_weighted_tokens or "custom"
    print(f"{t.name:14s} ${t.platform_fee_usd_month}/mo   {inc} weighted tokens")
```

Tier data lives in [`data/anoman_tiers.json`](data/anoman_tiers.json).

---

## API Reference

### `calculate_cost(model, input_tokens, output_tokens, mode="realtime")`

```python
cost = calculate_cost("claude-sonnet-4.6", 10000, 5000, mode="batch")
print(cost)
# CostEstimate(model='claude-sonnet-4.6', provider='anthropic', input_cost=0.015, output_cost=0.0375, total_cost=0.0525, mode='batch')
```

**Modes:** `"realtime"` (default), `"batch"` (50% off for supported models), `"cached"` (cached input pricing).

### `compare_costs(input_tokens, output_tokens, mode, providers)`

```python
# Compare all models
ranking = compare_costs(50000, 10000)

# Only Anthropic models
ranking = compare_costs(50000, 10000, providers=["anthropic"])

# Only batch-capable models
ranking = compare_costs(50000, 10000, mode="batch")
```

### `find_cheapest(input_tokens, output_tokens, **filters)`

```python
cheapest = find_cheapest(
    10000, 5000,
    requires_vision=True,
    min_context=500000,
)
print(f"Cheapest: {cheapest.model} at ${cheapest.total_cost:.4f}")
```

### `estimate_monthly_cost(model, daily_requests, avg_input, avg_output)`

```python
monthly = estimate_monthly_cost("gpt-4o-mini", daily_requests=10000, avg_input_tokens=500, avg_output_tokens=200)
print(f"Estimated monthly: ${monthly:.2f}")
```

---

## Programmatic Comparison

```python
from llm_cost_calculator import calculate_cost

# Same prompt across 5 providers
models = ["gpt-4o", "claude-sonnet-4.6", "gemini-3.6-flash", "mistral-large", "deepseek-v3"]
for model in models:
    cost = calculate_cost(model, input_tokens=50000, output_tokens=10000)
    print(f"  {cost.model:25s}  ${cost.total_cost:.4f}")
```

---

## Contributing Pricing Updates

Prices change frequently. To update:

1. Edit `data/pricing.json` with new prices
2. Update the `updated_at` field
3. Run tests: `pytest python/tests/ -v`
4. Submit a PR with the source (e.g., "Updated from provider pricing page on YYYY-MM-DD")

---

## Part of the Anoman open-source suite

Free, zero-dependency tools maintained by [Anoman AI](https://anoman.io) — the **guarded LLM gateway**: route to 35+ models at provider cost (**0% markup**) with prompt-injection + PII guardrails on every call, observability, batch routing, **IDR (Rupiah) billing with no international card**, and in-region (Jakarta) processing for UU PDP data residency.

- **llm-cost-calculator** — maintained LLM pricing database + cost calculator *(this repo)*
- [**llm-guardrails-sea**](https://github.com/c0denician88/llm-guardrails-sea) — LLM guardrails for Southeast Asia (injection, SEA PII, EN/ID moderation)
- [**anomaly-detect-realtime**](https://github.com/c0denician88/anomaly-detect-realtime) — real-time behavioral anomaly detection for LLM agents
- [**anoman-codecheck**](https://github.com/c0denician88/anoman-codecheck) — codebase security & quality scanner (OWASP/NIST, SARIF/JUnit)

Want it all managed — one dashboard, alerts, audit logs, and billing? → **[anoman.io](https://anoman.io)**

---
## Credits

Maintained by [Anoman AI](https://anoman.io) — the 0% markup LLM gateway. Route to 35+ models at provider cost with guardrails, observability, and batch routing built in.

---

## License

MIT
