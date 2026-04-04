# llm-cost-calculator

[![PyPI](https://img.shields.io/pypi/v/llm-cost-calculator)](https://pypi.org/project/llm-cost-calculator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/c0denician88/llm-cost-calculator/actions/workflows/ci.yml/badge.svg)](https://github.com/c0denician88/llm-cost-calculator/actions)

**Maintained LLM pricing database + cost calculator.** 22+ models across 7 providers. Calculate, compare, and estimate costs for any LLM workload. Zero dependencies. Python (TypeScript coming soon).

---

## Why This Exists

LLM pricing changes constantly. There's no maintained, machine-readable pricing database. Developers guess costs or build their own spreadsheets.

This library gives you:
- **`data/pricing.json`** — machine-readable database of 22+ model prices (input, output, batch, cached)
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

22+ models with real-time, batch, and cached pricing (USD per 1M tokens):

| Model | Provider | Input | Output | Batch In | Batch Out | Context |
|-------|----------|------:|-------:|---------:|----------:|--------:|
| Claude Opus 4 | Anthropic | $15.00 | $75.00 | $7.50 | $37.50 | 200K |
| Claude Sonnet 4 | Anthropic | $3.00 | $15.00 | $1.50 | $7.50 | 200K |
| Claude Haiku 3.5 | Anthropic | $0.80 | $4.00 | $0.40 | $2.00 | 200K |
| GPT-4o | OpenAI | $2.50 | $10.00 | $1.25 | $5.00 | 128K |
| GPT-4o Mini | OpenAI | $0.15 | $0.60 | $0.075 | $0.30 | 128K |
| GPT-4.1 | OpenAI | $2.00 | $8.00 | $1.00 | $4.00 | 1M |
| GPT-4.1 Mini | OpenAI | $0.40 | $1.60 | $0.20 | $0.80 | 1M |
| GPT-4.1 Nano | OpenAI | $0.10 | $0.40 | $0.05 | $0.20 | 1M |
| o3 | OpenAI | $10.00 | $40.00 | — | — | 200K |
| o3 Mini | OpenAI | $1.10 | $4.40 | — | — | 200K |
| o4 Mini | OpenAI | $1.10 | $4.40 | — | — | 200K |
| Gemini 2.5 Pro | Google | $1.25 | $10.00 | $0.625 | $5.00 | 1M |
| Gemini 2.5 Flash | Google | $0.15 | $0.60 | $0.075 | $0.30 | 1M |
| Gemini 2.0 Flash | Google | $0.10 | $0.40 | $0.05 | $0.20 | 1M |
| Mistral Large | Mistral | $2.00 | $6.00 | $1.00 | $3.00 | 128K |
| Mistral Small | Mistral | $0.10 | $0.30 | $0.05 | $0.15 | 128K |
| Codestral | Mistral | $0.30 | $0.90 | — | — | 256K |
| DeepSeek V3 | DeepSeek | $0.27 | $1.10 | — | — | 128K |
| DeepSeek R1 | DeepSeek | $0.55 | $2.19 | — | — | 128K |
| Llama 4 Scout | Together | $0.15 | $0.60 | — | — | 512K |
| Llama 4 Maverick | Together | $0.30 | $1.20 | — | — | 1M |
| Llama 3.3 70B | Groq | $0.59 | $0.79 | — | — | 128K |

*Pricing last verified: April 2026. Submit a PR if you find stale data.*

---

## API Reference

### `calculate_cost(model, input_tokens, output_tokens, mode="realtime")`

```python
cost = calculate_cost("claude-sonnet-4", 10000, 5000, mode="batch")
print(cost)
# CostEstimate(model='claude-sonnet-4', provider='anthropic', input_cost=0.015, output_cost=0.0375, total_cost=0.0525, mode='batch')
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
models = ["gpt-4o", "claude-sonnet-4", "gemini-2.5-pro", "mistral-large", "deepseek-v3"]
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

## Credits

Maintained by [Anoman AI](https://anoman.io) — the 0% markup LLM gateway. Route to 35+ models at provider cost with guardrails, observability, and batch routing built in.

---

## License

MIT
