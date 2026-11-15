# Council ablation — a pre-registered test of model councils on ML-governance questions

Status: frozen 2026-11-04 before the first model call, 2 amendments recorded before any result was read, evaluated
once. Retrospective in this repository: the run happened in the Athena development repository, and this folder
publishes its protocol, non-raw answers, analysis and notebooks.

**Result: `REJECTED_ON_THIS_BENCHMARK`.**
- The strong single model (`{{council:solo.model}}`) answered {{council:solo.correct}} of {{council:cases.evaluation}}
  held-out cases correctly.
- No council condition beat it: {{council:conditions.tied}} tied it and {{council:conditions.below}} scored
  {{council:conditions.below_correct}}/{{council:cases.evaluation}}. All {{council:conditions.rejected}} council conditions are
  REJECTED under the pre-registered rule.
- Every council cost more per decision than the cheapest equally accurate single model (`{{council:haiku.model}}`,
  USD {{council:haiku.cost_per_1k|2}} per 1 000 decisions) and added no accuracy. The judge condition cost
  {{council:E.cost_ratio|1}}× and took {{council:E.latency_ratio|1}}× the latency of the strong single model. The
  Haiku-only councils B1 and B2 were cheaper than the strong single model, and less accurate.
- The benchmark sits at a ceiling, so it cannot show whether councils help on questions a frontier model gets wrong.

This is a scoped negative result. It is **not** evidence that councils never work.

## Read

| What | File |
|---|---|
| Write-up (English) | [`writeups/council-ablation.en.md`](writeups/council-ablation.en.md) |
| Write-up (Türkçe) | [`writeups/council-ablation.tr.md`](writeups/council-ablation.tr.md) |
| Every write-up number and its source, recomputed | [`EVIDENCE_MAP.md`](EVIDENCE_MAP.md) |
| Article facts and their trace | [`results/facts.json`](results/facts.json), [`TRACE.md`](TRACE.md) |
| Protocol (frozen before the first call) | [`protocol/PREREGISTRATION.md`](protocol/PREREGISTRATION.md), [`protocol/AMENDMENTS.md`](protocol/AMENDMENTS.md) |
| Original results note | [`protocol/RESULTS.md`](protocol/RESULTS.md) |
| Methodology and planned research | [`METHODOLOGY.md`](METHODOLOGY.md) |
| Limitations | [`LIMITATIONS.md`](LIMITATIONS.md) |
| How to reproduce | [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) |
| Data and model terms | [`DATA_AND_MODEL_LICENSES.md`](DATA_AND_MODEL_LICENSES.md) |

## Design

- **Cases:** {{council:cases.total}} closed-answer ML-governance cases in nine families, split before the first call
  into {{council:cases.calibration}} calibration and {{council:cases.evaluation}} evaluation cases. Ground truth comes
  from public dataset documentation or from a rule stated in the case; no label is produced by a model.
- **Members:** `{{council:solo.model}}` and `{{council:haiku.model}}` (temperature 1, provider-enforced), local
  `qwen2.5:7b` and `qwen2.5:1.5b` (temperature 0).
- **Conditions:** A (single model), B1 same-provider roles, B2 same-provider sampling, C multi-provider,
  D characteristic-diverse, E judge, F adaptive routing.
- **Statistics:** 95 % paired bootstrap intervals, 2 000 resamples, seed 11, on the evaluation cases.

## Results (evaluation cases, n = {{council:cases.evaluation}})

| Condition | Correct | Accuracy | Δ vs single model [95 % CI] | Cost per 1 000 decisions (USD) | Latency / decision (s) | Decision |
|---|---|---|---|---|---|---|
| A single model (`{{council:solo.model}}`) | {{council:solo.correct}} | {{council:solo.accuracy|pct}} | — | {{council:solo.cost_per_1k|2}} | {{council:solo.latency_s|2}} | reference |
| A single model (`{{council:haiku.model}}`) | {{council:haiku.correct}} | {{council:haiku.accuracy|pct}} | {{council:haiku.delta|pp}} | {{council:haiku.cost_per_1k|2}} | {{council:haiku.latency_s|2}} | cheapest equally accurate |
| B1 same-provider roles | {{council:B1.correct}} | {{council:B1.accuracy|pct}} | {{council:B1.delta|pp}} [{{council:B1.ci_low|pp}}, {{council:B1.ci_high|pp}}] pp | {{council:B1.cost_per_1k|2}} | {{council:B1.latency_s|2}} | {{council:B1.decision}} |
| B2 same-provider sampling | {{council:B2.correct}} | {{council:B2.accuracy|pct}} | {{council:B2.delta|pp}} [{{council:B2.ci_low|pp}}, {{council:B2.ci_high|pp}}] pp | {{council:B2.cost_per_1k|2}} | {{council:B2.latency_s|2}} | {{council:B2.decision}} |
| C multi-provider | {{council:C.correct}} | {{council:C.accuracy|pct}} | {{council:C.delta|pp}} [{{council:C.ci_low|pp}}, {{council:C.ci_high|pp}}] pp | {{council:C.cost_per_1k|2}} | {{council:C.latency_s|2}} | {{council:C.decision}} |
| D characteristic-diverse | {{council:D.correct}} | {{council:D.accuracy|pct}} | {{council:D.delta|pp}} [{{council:D.ci_low|pp}}, {{council:D.ci_high|pp}}] pp | {{council:D.cost_per_1k|2}} | {{council:D.latency_s|2}} | {{council:D.decision}} |
| E judge | {{council:E.correct}} | {{council:E.accuracy|pct}} | {{council:E.delta|pp}} [{{council:E.ci_low|pp}}, {{council:E.ci_high|pp}}] pp | {{council:E.cost_per_1k|2}} | {{council:E.latency_s|2}} | {{council:E.decision}} |
| F adaptive routing | {{council:F.correct}} | {{council:F.accuracy|pct}} | {{council:F.delta|pp}} [{{council:F.ci_low|pp}}, {{council:F.ci_high|pp}}] pp | {{council:F.cost_per_1k|2}} | {{council:F.latency_s|2}} | {{council:F.decision}} |

- **Cost** is provider-reported (MEASURED); local models cost 0.
- **Council latency** is ESTIMATED: the slowest member plus the judge.
- **F** sent {{council:F.escalated}} of {{council:cases.evaluation}} decisions to human review, at
  {{council:F.calls_per_decision|2}} calls per decision.
- **Diversity (H2, descriptive).** Over {{council:H2.combinations}} three-member combinations, the Spearman
  correlation of gain was {{council:H2.spearman_double_fault|2}} with double-fault rate and
  {{council:H2.spearman_provider_count|2}} with provider count.

**Total provider-reported cost:** USD {{council:cost.total_usd|2}} for {{council:cost.calls|int}} distinct calls.

**Correction.** An earlier internal total of USD {{council:cost.double_counted_usd|2}} counted the archived 300-token
pass twice. Its rows are the first rows of the final answer file. The {{council:cost.reasked}} re-asked calls are
counted once.

## Notebooks

Every notebook reads `evidence/` and the JEV study's evidence only. None makes a model, provider or network call, so
re-running a notebook cannot change a result. {{council:notebooks.pass}} of {{council:notebooks.count}} pass a
clean-kernel Restart + Run All ([`evidence/notebook_runs.json`](evidence/notebook_runs.json)).

| Notebook | Content |
|---|---|
| [`00_protocol_and_datasets`](notebooks/00_protocol_and_datasets.ipynb) | Protocol, case set, ground-truth provenance, integrity of copied files |
| [`01_routing_and_jev`](notebooks/01_routing_and_jev.ipynb) | Adaptive routing (condition F); Jev bounded decisions on a separate corpus |
| [`02_cot_tot_got`](notebooks/02_cot_tot_got.ipynb) | What the product council's CoT / ToT / GoT labels do (confidence / tie-break aggregation); mock-only evidence |
| [`03_council_judge_critic`](notebooks/03_council_judge_critic.ipynb) | Conditions A–F, member characteristics, diversity, the outvoted critic |
| [`04_react_reflexion_pot`](notebooks/04_react_reflexion_pot.ipynb) | Status of ReAct, Reflexion, Program-of-Thought (none evaluated) |
| [`05_mcts_feature_strategy`](notebooks/05_mcts_feature_strategy.ipynb) | Status of MCTS (not implemented) |
| [`06_cost_latency_calibration`](notebooks/06_cost_latency_calibration.ipynb) | Cost, latency and calibration tables |
| [`07_results_and_recommendations`](notebooks/07_results_and_recommendations.ipynb) | One status table across all methods; recommendations |

## Labels

- **MEASURED:** a real provider or real run produced the number.
- **ESTIMATED:** derived from measured data by a stated formula.
- **SIMULATED:** mock runner.
- **NOT_RUN:** no result exists.
- **UNKNOWN:** the evidence does not say.

Implementation, wiring and evaluation are reported separately. Code that exists is not a measured capability.

## Not yet measured

{{council:plans.count}} methods have no measured result on this case set. Each is recorded as a pre-registration-ready
research plan, with purpose, hypothesis, baseline, task family, metric, budget, stopping rule and admission gate, in
[`evidence/reasoning_methods/research_plans.json`](evidence/reasoning_methods/research_plans.json) (rendered in
[`METHODOLOGY.md`](METHODOLOGY.md#planned-research-research_planned)):

- Hermes-style task and cost routing;
- Program-of-Thought;
- Chain-of-Thought as model reasoning (the CoT label in the product council is a confidence multiplier, not CoT);
- Tree-of-Thoughts;
- Graph-of-Thoughts;
- council, judge and critic on tasks below the ceiling;
- ReAct;
- Reflexion;
- MCTS feature search.

No performance claim is made for any of them on this case set. CoT, ToT and GoT as reasoning orchestration were
measured on a different task family in [Study A](../reasoning-topology/original-study/) and
[Study A2](../reasoning-topology/frontier-replication/), where no topology beat a direct answer.

## Relation to the other studies here

- **Study A / A2:** different task family (bounded AutoML decisions) and different models. They measure reasoning
  topology; this study measures council composition. No number is compared across the two.
- **JEV:** the Jev rows in notebook 01 and in the evidence map read
  [`research/jev/evidence/`](../jev/evidence/). This folder does not keep a second copy.

## Evidence

All evidence is machine-readable JSON or CSV under [`evidence/`](evidence/).

- **Raw model completions and free-text reasons are not published.** Each call keeps its parsed answer, confidence,
  error category, retries, latency, tokens and provider-reported cost.
- **The published answers reproduce the frozen analysis exactly**
  ([`evidence/replay_check.json`](evidence/replay_check.json)).
- **Scans.** The study-level scan ([`evidence/publication_scan.json`](evidence/publication_scan.json)) and the
  repository's release audit (`tools/check_repo.py`) check for secrets, personal data, internal hosts, absolute paths
  and raw model output.
- **Redactions.** Product source paths in two evidence files are redacted and listed in
  [docs/REDACTIONS.json](../../docs/REDACTIONS.json).

## Layout

```
writeups/    EN and TR write-ups
protocol/    pre-registration, amendments, original results note (frozen copies)
evidence/    council/ decision_methods/ reasoning_methods/ + manifests, scan, replay and notebook-run records
results/     facts.json, derived from evidence/ by tools/derive_facts.py
notebooks/   00–07 analysis notebooks (executed)
harness/     the case set and analysis harness that ran (cases.py, run.py)
tools/       facts, notebook builder and runner, replay check, evidence map, methodology renderer, study scan
```

## Licence

Code (`harness/`, `tools/`) is under Apache-2.0 ([LICENSE](../../LICENSE)). Text, notebooks, evidence and tables
are under CC BY 4.0 ([LICENSE-CC-BY-4.0.md](../../LICENSE-CC-BY-4.0.md)). Third-party dataset and model terms are
listed in [`DATA_AND_MODEL_LICENSES.md`](DATA_AND_MODEL_LICENSES.md). No third-party dataset rows are included.
