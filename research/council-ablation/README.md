# Council ablation — a pre-registered test of model councils on ML-governance questions

Status: frozen 2026-11-04 before the first model call, 2 amendments recorded before any result was read, evaluated
once. Retrospective in this repository: the run happened in the Athena development repository, and this folder
publishes its protocol, non-raw answers, analysis and notebooks.

**Result: `REJECTED_ON_THIS_BENCHMARK`.**
- The strong single model (`claude-sonnet-5-5`) answered 70 of 71
  held-out cases correctly.
- No council condition beat it: 2 tied it and 4 scored
  69/71. All 6 council conditions are
  REJECTED under the pre-registered rule.
- Every council cost more per decision than the cheapest equally accurate single model (`claude-haiku-5-5`,
  USD 0.13 per 1 000 decisions) and added no accuracy. The judge condition cost
  2.5× and took 2.3× the latency of the strong single model. The
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

- **Cases:** 110 closed-answer ML-governance cases in nine families, split before the first call
  into 39 calibration and 71 evaluation cases. Ground truth comes
  from public dataset documentation or from a rule stated in the case; no label is produced by a model.
- **Members:** `claude-sonnet-5-5` and `claude-haiku-5-5` (temperature 1, provider-enforced), local
  `qwen2.5:7b` and `qwen2.5:1.5b` (temperature 0).
- **Conditions:** A (single model), B1 same-provider roles, B2 same-provider sampling, C multi-provider,
  D characteristic-diverse, E judge, F adaptive routing.
- **Statistics:** 95 % paired bootstrap intervals, 2 000 resamples, seed 11, on the evaluation cases.

## Results (evaluation cases, n = 71)

| Condition | Correct | Accuracy | Δ vs single model [95 % CI] | Cost per 1 000 decisions (USD) | Latency / decision (s) | Decision |
|---|---|---|---|---|---|---|
| A single model (`claude-sonnet-5-5`) | 70 | 98.6% | — | 1.99 | 2.31 | reference |
| A single model (`claude-haiku-5-5`) | 70 | 98.6% | 0.0 | 0.13 | 1.77 | cheapest equally accurate |
| B1 same-provider roles | 69 | 97.2% | −1.4 [−4.2, 0.0] pp | 0.49 | 2.43 | REJECTED |
| B2 same-provider sampling | 69 | 97.2% | −1.4 [−4.2, 0.0] pp | 0.38 | 2.10 | REJECTED |
| C multi-provider | 70 | 98.6% | 0.0 [0.0, 0.0] pp | 2.12 | 2.71 | REJECTED |
| D characteristic-diverse | 69 | 97.2% | −1.4 [−4.2, 0.0] pp | 2.18 | 2.72 | REJECTED |
| E judge | 70 | 98.6% | 0.0 [0.0, 0.0] pp | 4.90 | 5.26 | REJECTED |
| F adaptive routing | 69 | 97.2% | −1.4 [−4.2, 0.0] pp | 2.03 | 3.07 | REJECTED |

- **Cost** is provider-reported (MEASURED); local models cost 0.
- **Council latency** is ESTIMATED: the slowest member plus the judge.
- **F** sent 36 of 71 decisions to human review, at
  3.35 calls per decision.
- **Diversity (H2, descriptive).** Over 35 three-member combinations, the Spearman
  correlation of gain was -0.83 with double-fault rate and
  -0.18 with provider count.

**Total provider-reported cost:** USD 0.71 for 1,506 distinct calls.

**Correction.** An earlier internal total of USD 1.04 counted the archived 300-token
pass twice. Its rows are the first rows of the final answer file. The 186 re-asked calls are
counted once.

## Notebooks

Every notebook reads `evidence/` and the JEV study's evidence only. None makes a model, provider or network call, so
re-running a notebook cannot change a result. 8 of 8 pass a
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

9 methods have no measured result on this case set. Each is recorded as a pre-registration-ready
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
