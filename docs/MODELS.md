# Models

Every model that produced a scored result, plus the two that were planned and not used. Parameters are the ones that
ran: for rs2610 they come from the freeze records and the ledgers (generated per arm in
[`a2/EXPERIMENT_CONFIG.md`](../harness/rs2610/outputs/replication/a2/EXPERIMENT_CONFIG.md) and
[`b2/EXPERIMENT_CONFIG.md`](../harness/rs2610/outputs/replication/b2/EXPERIMENT_CONFIG.md)), for JEV from its evidence files.

**Reasoning controls are not comparable across providers.** `qwen2.5:7b` has no reasoning mode. `gpt-6-luna`
ran with OpenAI `reasoning.effort = "medium"`, and its reasoning tokens are counted separately. `claude-sonnet-5-5` ran
with Anthropic `output_config.effort = "medium"` and adaptive thinking (provider default, always on), and the API does
not report thinking tokens separately. "medium" on one API is not the same setting as "medium" on the other, and
neither is "no reasoning". A hosted DIRECT call therefore includes reasoning the caller never sees: A2 compares
orchestration, not reasoning against no reasoning.

## rs2610 (Studies A, A2, B, B2)

| | `qwen2.5:7b` | `gpt-6-luna` | `claude-sonnet-5-5` |
|---|---|---|---|
| role | baseline in A, B, A2, B2 | hosted arm in A2 and B2 | hosted arm in B2 only (amendment 2) |
| provider / access | local, Ollama HTTP API | OpenAI Responses API, `openai-python` 3.41.0 | Anthropic Messages API (streaming), `anthropic-python` 2.3.0 |
| requested id | `qwen2.5:7b` | `gpt-6-luna` | `claude-sonnet-5-5` |
| resolved id | `qwen2.5:7b` (Ollama tag) | `gpt-6-luna` (provider-returned `model`, every ledger row) | `claude-sonnet-5-5` (provider-returned `model`, every ledger row) |
| version pin | digest `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`, checked before runs | provider alias; no digest is exposed | provider id; no digest is exposed |
| freeze dates | Study B 2026-10-27, Study A 2026-10-28, A2/B2 2026-10-29 | 2026-10-29 (amendment 1) | 2026-10-29 (amendment 2) |
| call timestamps | every ledger row | every ledger row, with provider request id | every ledger row, with provider request id |
| reasoning | none | `reasoning.effort = "medium"` | `output_config.effort = "medium"`, adaptive thinking always on |
| temperature | 0.4 | NOT_CONFIGURABLE (not sent; recorded as such per call) | NOT_CONFIGURABLE (not sent; recorded as such per call) |
| top_p | Ollama default | NOT_CONFIGURABLE | NOT_CONFIGURABLE |
| seed | `seed` = replicate index (Ollama option) | NOT_CONFIGURABLE; the replicate index enters the request hash only | NOT_CONFIGURABLE |
| context | `num_ctx` 12288 | provider default | provider default |
| visible-output cap | frozen per call: A2 250–1200, B2 1500 / 1800 / 2200 / 3200 by call type | the same frozen cap + 16000 reasoning allowance (`max_output_tokens`) | the same frozen cap + 16000 (`max_tokens`) |
| structured output | JSON schema via Ollama `format` | `text.format` `json_schema`, `strict: true`; `store: false` | `output_config.format` `json_schema`; array `minItems`/`maxItems` removed because the API rejected them (HTTP 400 in the 2026-10-29 smoke); the task text still states the bounds and the analysis keeps at most the frozen `maxItems` items |
| request caching | `sha256` of model, messages, schema, options | `sha256` of provider, model, effort, system, user, schema, replicate, cap | same as OpenAI |
| cost status | NOT_APPLICABLE_LOCAL | CALCULATED_FROM_PUBLISHED_PRICES: $0.10 input / $0.01 cached input / $0.50 output per MTok (developers.openai.com/api/docs/pricing, accessed 2026-10-29) | CALCULATED_FROM_PUBLISHED_PRICES: $2 input / $0.20 cached input / $10 output per MTok (Anthropic model table, accessed 2026-10-29) |
| spend | — | A2 $0.7539, B2 $0.2806 | B2 $2.4526 |
| calls | Study A 3,633 (unseen), Study B 276 (unseen), B2 240 | A2 2,304, B2 249 | B2 124 |

Costs are computed from token counts in the ledgers and the published prices above; they are not invoices. The exact
request each client sends is in [`replication/providers.py`](../harness/rs2610/replication/providers.py) and
[`common/llm.py`](../harness/rs2610/common/llm.py); what the schema looks like after provider adaptation is in
[`providers/`](../research/reasoning-topology/frontier-replication/providers/).

### Planned and not used

| model | status | why |
|---|---|---|
| `gpt-6.1-sol` | superseded pilot, excluded from every result | The OpenAI account hit a billing stop after $0.85 of pilot calls. Amendment 1 replaced it with `gpt-6-luna` before any Luna run. Pilot rows are kept under `*.superseded_sol.jsonl`, billing-refused rows under `*.billing_refused.superseded_sol.jsonl`. |
| `claude-opus-5-5` | pre-registered, never run | One smoke call only. The Anthropic account did not have credit for the planned arm; amendment 2 replaced it with `claude-sonnet-5-5`, B2 only, 1 replicate, before any Sonnet run. There is no Anthropic arm in A2. |

## JEV

| | Jev | comparators |
|---|---|---|
| provider / access | TypeSafe Jev API, `POST /v1/systemone`, the author's personal credential | rules (hand-written), local bounded model (standardised features + logistic regression), hybrid and agentic methods using the local `ollama/qwen2.5:1.5b` |
| requested id | alias `jev-latest` | — |
| resolved id | `jev-1.13.0` in A, B and C/D/E (recorded in each evidence file) | — |
| reasoning / temperature / top_p / seed | NOT EXPOSED by the API | local model defaults; NOT RECOVERABLE beyond the evidence files |
| request shape | one choice question; state = decision description + typed declared features; disclosure classes SCHEMA, AGGREGATED_STATISTICS | — |
| structured output | provider-native single choice with confidence and per-option probabilities | — |
| calls | A 309, B 339 (309 + 30 in phase B1), C/D/E 640 | — |
| tokens (C/D/E) | input 895,816, output 48,668 | — |
| cost status | UNKNOWN: the API returns token usage but no price or balance | NOT_APPLICABLE_LOCAL |
