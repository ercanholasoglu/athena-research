## 1. Motivation

The original program ran every decision on one local model, `qwen2.5:7b` at temperature 0.4. Each of its two main
findings leaves room for an explanation based on model capability:

- **Study A** did not detect an accuracy benefit from chain, tree or graph reasoning over a direct answer, while the
  tree and the graph cost {{ax.UNSEEN.TOT.compute_vs_direct|1}}× and {{ax.UNSEEN.GOT.compute_vs_direct|1}}× the compute. Perhaps a 7B model cannot exploit richer structure.
- **Study B** found that the data owner's documentation (dictionary, rules) improved leakage blocking and semantic
  accuracy. It could not show feature *invention*: {{bx.UNSEEN.proposals_copying_candidates|pct}} of proposed features copied an offered candidate. Perhaps a
  stronger model would use semantics to invent features.

This phase re-runs focused subsets of both benchmarks on hosted models, under the same contracts, scoring and
statistics. The original studies are not modified, re-run or re-analysed. Their results stay the historical record,
and this report is later evidence.

## 2. Frozen subsets

The subsets were chosen by coverage and written down before any frontier run (`replication/PREREGISTRATION.md` §4,
hashed in `FREEZE_RECORD_A2B2.json`).

**A2: {{r.design.a2.instances}} decision instances on 4 unseen Study A datasets.**
- `iranian_churn`, `taiwan_default` and `diabetes_readmission` carry all ten decision families and all eight
  adversarial variants: governance block, calibration conflict, causal disagreement, incomplete evidence,
  indistinguishable options, cheaper equivalent, variance uncertainty and suspicious data quality. Between them they
  hold all 24 adversarial instances of the original study.
- `online_shoppers` adds a fourth domain with base instances only.

**B2: 4 datasets × 10 cells.**
- Datasets:
  - `iranian_churn` (churn);
  - `taiwan_default` (credit default);
  - `bank_marketing` (bank marketing; it was a Study B *development* dataset, which is disclosed);
  - `hillstrom_email` (a randomized e-mail test; causal/actionability).
- Every dataset carries the frozen Study B traps: the identifier `record_key`, a post-outcome column and the warehouse
  artifact `load_weekday`.
- It also carries one new **target-derived** trap, `segment_outcome_rate`. This is a micro-segment outcome rate
  computed on the whole extract, including the row's own label. It is described truthfully in the dictionary, like
  every trap.
- The ten cells:
  - five Study B conditions on the trapped data, from A_RAW (meaningful names, no dictionary) to E_FULL (rules plus a
    verification stage);
  - anonymized columns, without and with a correct dictionary;
  - an incomplete dictionary;
  - a misleading dictionary, under D_RULES and E_FULL.
- Every run ends with a new **feature-invention call**. It shows no candidate features, no examples and no earlier
  output. The model sees only the profile, the target summary, the documentation its condition allows and the task.

## 3. Models and configuration

| Arm | Model (resolved id) | Reasoning | Sampling | A2 | B2 |
|---|---|---|---|---|---|
| Baseline | `qwen2.5:7b` (Ollama, digest `845dbda0…`) | none | temperature 0.4, seed = replicate | frozen Study A runs, 3 seeds | new, 2 replicates |
| OpenAI | `gpt-6-luna` | `reasoning.effort = medium` | not configurable | 3 replicates | 2 replicates |
| Anthropic | `claude-sonnet-5-5` | `output_config.effort = medium`, thinking always on | not configurable | **not run** | 1 replicate |

Full parameters and observed usage are in `outputs/replication/{a2,b2}/EXPERIMENT_CONFIG.md`. Every call is recorded
with the provider-returned model id and request id.

**How the models were chosen, and what the choice limits.** The pre-registration named `gpt-6.1-sol` and
`claude-opus-5-5`. Neither ran to completion, for billing reasons:
1. The OpenAI organisation's prepaid credit ran out after $0.85.
2. The owner then chose `gpt-6-luna`, OpenAI's lowest-cost tier (amendment 1).
3. The Anthropic account held $5, enough for B2 on `claude-sonnet-5-5` with one replicate but not for A2 (amendment 2).

Both amendments were recorded before any run of the amended arm. The partial `gpt-6.1-sol` runs are kept as a
superseded pilot and excluded from every analysis.

The consequence matters for interpretation. **This phase tests two current hosted reasoning models, one low-cost and
one mid-tier, against a 2024 7B open model. It does not test either provider's top tier.**

## 4. Provider differences

The following were identical for every model:
- datasets and frozen splits;
- evidence packets and profiles;
- task wording, system prompts and output schemas;
- answer keys and scoring;
- topology execution;
- statistics.

These differences remain, and none can be removed:

1. **Sampling.** Neither hosted model accepts temperature, top_p or seed. A replicate is an independent sample, and
   its index enters only the request hash.
2. **Reasoning.** Both hosted models reason before they answer, and that reasoning is not visible. A hosted "DIRECT"
   call is therefore one call with provider-side reasoning, not a no-reasoning control. What still differs between the
   topologies is what is executed: one call against five, isolated evaluation of branches, and a graph with
   deterministic propagation.
3. **Token caps.** A hosted model's cap bounds reasoning plus visible output. Each frozen visible cap was sent as the
   cap + 16,000.
4. **Structured output.** The frozen schemas were sent in each provider's strict JSON-schema mode with
   `additionalProperties: false` added. Anthropic rejects array `minItems` / `maxItems`, so those bounds were dropped for
   it; the prompts still state them, and the analysis keeps at most the frozen maximum.
5. **Latency.** Hosted latency is client-side wall time, including network and queueing. Baseline latency is the
   server's prefill and decode time. The two are never put in one ratio.
6. **Cost.** Neither API returns a price. Cost is computed from the usage block and the published per-token prices,
   with source and access date recorded. The local baseline is `NOT_APPLICABLE_LOCAL` and is never 0.

## 5. Integrity log (summary of `replication/JOURNAL.md`)

- **Freeze.** The A2/B2 freeze was written at commit `3299b015`, before any frontier evaluation run. Amendments 1 and 2
  each re-freeze the full record before the first run of the arm they change. Every `--verify` also re-checks the
  original A and B freezes.
- **Billing stop.** When the OpenAI credit ran out, 24 run rows had billing-refused calls. They were moved to
  `*.billing_refused.superseded_sol.jsonl`, not deleted and not scored as wrong: a billing event is not a decision
  error.
- **Waiter guard.** An automatic waiter detected the new credit but refused to launch, because the freeze verify
  reported drift (an unrecorded price-table edit). It worked as designed.
- **Pre-run smoke calls.** These were made on data outside the subsets: one DEVELOPMENT Study A instance, and
  `telco_churn` for B2. They are excluded from every analysis.
- **Disk full and data restore.** The host disk filled during the qwen B2 run, which stopped at 75/80 with no partial
  row. While space was being freed, the raw-data cache under `~/.cache` was deleted. The five B2 datasets that the
  runner, evaluator and loader need were downloaded again from their canonical sources and verified against the
  frozen frame, split, truth and prompt hashes (160/160 match) before the last 5 runs. The full `freeze --verify` could
  not run, because it also needs datasets that were not restored; this is listed in section 9.
- **Frozen harness.** No frozen code was changed after the freeze.
