# Study A — Does reasoning topology change decision quality? (design & pre-registration)

Status: **pre-registered before any UNSEEN run.** The commit that adds this file precedes the first UNSEEN ledger entry.
Anything decided after looking at UNSEEN results is labelled *exploratory* in the summary.

## Research question

With the same analytical task and the same evidence, do Chain of Thought (CoT), Tree of Thought (ToT) and Graph of Thought
(GoT) differ in decision quality, robustness, efficiency or generalization? A no-reasoning arm (DIRECT) is included as a
control, so "reasoning helps at all" and "topology matters" can be told apart.

## Why a new harness

Athena ships `council/{chain,tree,graph}_of_thoughts.py`. Those modules are **post-hoc aggregations** of the same persona
answers: the model calls are identical whichever mode is selected. Comparing them would compare labels, not execution. The
study therefore implements four topologies whose *execution* differs (`study_a/topologies.py`). Production code is not changed.

| Mode | Calls | Execution semantics | Observable structure recorded |
|---|---|---|---|
| DIRECT | 1 | decision fields only | — |
| COT | 1 | schema forces 3-6 ordered steps; step k declares `depends_on_step = k-1` and cites evidence ids; decision generated after the steps | steps, dependency respected, evidence ids per step |
| TOT | 5 | (1) propose 3 distinct candidate branches → (2-4) **one isolated call per branch**: 2 refinement leaves, each scored, plus branch score and fatal-flaw flag → deterministic prune to top-2 → (5) select among survivors only | branches, leaves, pruned, duplicate proposals, leaf scores |
| GOT | 5 | (1) atomic claim nodes from evidence (shared by all candidates) → (2) candidate nodes → (3) typed edges: claim→candidate supports/contradicts and claim↔claim conflicts → deterministic weighted propagation (conflicted claims ×0.5, contradicting concerns ×1.5) → (4) aggregation call: recombine top-2 into a merged node when compatible → (5) decide over the graph summary | claim / candidate / merged nodes, edges, conflict edges, reused claims (fan-out ≥ 2), branching factor, `is_dag_beyond_tree` |

GoT's claims are shared parents of several candidates, so its structure is a DAG with multi-parent nodes. Each run records
whether that actually happened (`is_dag_beyond_tree`).

## Controls

Held fixed: model (`qwen2.5:7b`, Q4_K_M, Ollama digest recorded per call), provider (local Ollama), temperature 0.4, seed =
repeat index (1, 2, 3), byte-identical task prefix (system prompt, task, policy, evidence, options), identical final-decision
schema, identical option set (always including UNDETERMINED), identical evaluation authority.

Not equalised (by design, measured instead): number of calls, tokens and compute time. ToT and GoT need more calls; that cost
is the thing being traded and is reported next to quality.

Order effects: Ollama caches the shared prefix, so the first mode to run on an instance pays the prefill. Mode order rotates
by instance and seed (Latin-square style). Latency is the server-reported prefill+decode time.

**Substrate limitation (forced):** the Anthropic key had no credit and no other provider key was configured. All results are
for one 7B open-weight model. They are not claims about frontier models.

## Tasks

10 task families: MODEL_FAMILY, HPO_DEPTH, FE_STRATEGY, FS_STRATEGY, IMBALANCE, VALIDATION, CALIBRATION, EXPLANATION,
CAUSAL_VS_PREDICTIVE, TRUST_PLAN. The evidence for the first seven is **measured**: every option was actually executed on the
dataset (`study_a/evidence.py`). See `study-a-task-contracts.md`.

8 adversarial kinds (A5): calibration_conflict, variance_uncertain, cheaper_equivalent, governance_block, causal_disagreement,
data_quality_suspicious, indistinguishable, incomplete_evidence. Each is instantiated on 2 DEVELOPMENT and 3 UNSEEN datasets,
anchored on measured numbers with the perturbations listed per instance.

## Datasets and split

Fixed in `common/data.py` before any run (see `study-a-datasets.md`):

* DEVELOPMENT (6): telco_churn, german_credit, bank_marketing, adult_income, bike_sharing (regression), vehicle_silhouettes (multiclass)
* UNSEEN (8 + 1 causal-only): iranian_churn, taiwan_default, coil_caravan, diabetes_readmission, card_fraud_synth,
  online_shoppers, thyroid_sick, image_segment (multiclass); hillstrom_email (causal tasks only)

DEVELOPMENT was used to debug the harness (4 bugs so far, see JOURNAL.md). Prompts, schemas, topologies, reference rules and
analysis code are frozen at the pre-registration commit. UNSEEN is run once with seeds 1-3.

## Reference contract

* `accept`: options not significantly worse than the best on the dev-split CV (paired t-test over the same 5 folds,
  two-sided p ≥ 0.05). HPO depth: depths whose test score is within 0.005 of the best depth. VALIDATION / EXPLANATION /
  CAUSAL: rule-based from dataset facts.
* `parsimonious`: simplest member of `accept` (declared complexity order). An accepted but more complex choice counts as
  *unnecessary complexity*, not as an error.
* `utility`: per-option score on the untouched 25 % test split. **Regret** = best utility − chosen utility. Families without
  a measured outcome → regret UNKNOWN (never 0). An UNDETERMINED answer → regret ABSTAINED.
* `uncertainty_expected` instances are scored on *preserved uncertainty* = UNDETERMINED or confidence ≤ 0.65.

## Metrics (A6)

decision accuracy; regret; consistency (pairwise decision agreement across seeds); generalization (DEVELOPMENT vs UNSEEN);
calibration (ECE over runs, Brier of confidence, AUROC of confidence for correctness, share of wrong answers at confidence ≥ 0.9);
evidence utilization (share of key evidence ids cited; a cited GoT claim id counts as the evidence it rests on); contradiction handling (conflict ids named in `contradictions`, same resolution);
unnecessary complexity; abstention; parse failures; efficiency (prompt/output tokens ACTUAL, calls, server compute seconds
ACTUAL, cost NOT_APPLICABLE_LOCAL); topology statistics; topology fidelity (did the final call follow the structure's own ranking?).

## Hypotheses (confirmatory, UNSEEN)

* **H1** decision accuracy differs between at least one pair of {DIRECT, COT, TOT, GOT}.
* **H2** TOT and GOT have higher accuracy than COT on adversarial instances.
* **H3** TOT and GOT preserve uncertainty more often than COT/DIRECT on `uncertainty_expected` instances.
* **H4** accuracy per 1k output tokens is highest for DIRECT/COT.

## Statistical analysis (A7)

* Unit of pairing: task instance. Per instance, correctness is averaged over seeds; McNemar uses majority correctness
  (> 0.5). Exact McNemar for each of the 6 mode pairs, **Holm** correction across the 6.
* 95 % CIs: **dataset-cluster bootstrap** (2,000 resamples of datasets) for accuracy and for paired differences.
* Regret: paired by instance over instances where both modes have measured regret; bootstrap CI.
* Non-significance is reported as "no statistically distinguishable difference detected in this benchmark", never as equivalence.
* Confirmatory table: `study-a-confirmatory.csv` (H1 6 pairs; H2 TOT/GOT vs COT on adversarial instances; H3 TOT/GOT vs
  COT and vs DIRECT on uncertainty-expected instances, all exact McNemar on instance-majority; H4 accuracy per 1k output
  tokens, DIRECT/COT vs TOT/GOT, paired dataset-cluster bootstrap, two-sided bootstrap p). **Holm within each hypothesis.**
* Caveat fixed in advance: with 8-9 dataset clusters the cluster bootstrap is coarse and can be anti-conservative; McNemar
  (instance-level) and the bootstrap CI are both reported and a claim needs both.
* Exploratory: per-family breakdowns (`study-a-paired-by-family.csv`, Holm across all family tests, labelled EXPLORATORY) and
  per-adversarial-kind breakdowns (descriptive only).
