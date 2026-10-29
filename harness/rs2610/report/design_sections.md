## 2. Research questions

**Study A (reasoning topology).** With the same model, the same evidence, the same option set and the same evaluation
authority, does the *execution topology* of the reasoning (a single sequential chain, a tree of isolated branches with
deterministic pruning, or a graph of shared claims with typed edges and aggregation) materially change decision quality,
generalization to unseen datasets, robustness to adversarial evidence, or efficiency, in bounded AutoML decisions? A
no-reasoning arm (DIRECT) separates "reasoning helps at all" from "topology matters".

**Study B (semantic context).** Does semantic context (none, self-inference, a data dictionary, dictionary plus business
rules, or everything plus an independent verification stage) change the analytical decisions an AutoML system makes before
training, in a way that is more correct, safer (fewer leaks shipped) and still holds on datasets the harness was not
developed on? The question is not whether a model can *read* a dictionary; it is whether the decisions change, and whether
the change is useful.

## 3. Hypotheses

Pre-registered before any UNSEEN run (`outputs/study_a/study-a-design.md`, `outputs/study_b/study-b-design.md`); the
confirmatory families and corrections are fixed there. Anything decided after looking at UNSEEN results is labelled
*exploratory* in this report.

| | Hypothesis | Test | Correction |
|---|---|---|---|
| H1 | accuracy differs for at least one pair of {DIRECT, COT, TOT, GOT} | exact McNemar on instance-majority correctness | Holm, 6 pairs |
| H2 | TOT and GOT beat COT on adversarial instances | exact McNemar | Holm, 2 |
| H3 | TOT and GOT preserve uncertainty more than COT / DIRECT where uncertainty is the right answer | exact McNemar | Holm, 4 |
| H4 | accuracy per 1k output tokens is highest for DIRECT / COT | paired dataset-cluster bootstrap | Holm, 4 |
| H5 | core semantic accuracy higher in C, D, E than in A | Wilcoxon signed-rank + exact sign test, pairs = (dataset, seed) | Holm, 4 contrasts |
| H6 | leakage avoidance (all traps blocked, leak recall) higher in C, D, E | same | same |
| H7 | candidate-judgement accuracy and valid-and-leak-free proposal share higher in C, D, E | same | same |
| H8 | deployment collapse rarer and gap to the truth-clean model smaller in C, D, E | same | same |
| H9 | under a misleading dictionary, E detects more falsified entries than C and D | descriptive (2 datasets × 2 seeds) | — |
| H10 | under anonymized names, C and E recover more semantics than A | descriptive | — |

## 4. Experimental design

Both studies share one harness (`common/`): a local LLM client that records every call in an append-only ledger, the
dataset registry with its evaluation authority, preprocessing, and a deterministic holdout.

**Study A** turns measured AutoML evidence into bounded decisions. For each dataset every option of each decision was
actually executed (`study_a/evidence.py`: model families, HPO depths, FE and FS strategies, imbalance and calibration
methods, validation schemes), and the evidence packet shows what a practitioner would see on the development split. Ten
task families are instantiated per dataset plus eight adversarial perturbations on a subset, and scripted causal-vs-
predictive and Trust-plan questions. The correct set (`accept`) and the measured utility of every option come from the
evidence and from an untouched test split; the model never sees either.

**Study B** gives each condition a byte-identical column profile of a *trapped* dataset: every dataset carries a
target-ordered identifier (`record_key`), a post-outcome column (natural or inserted, truthfully documented) and a warehouse
load-day artifact (positives loaded on Fridays). The model writes a structured semantic analysis, proposes features in an
executable DSL and judges six offered candidate features, among them an ID transform, a post-outcome flag, the Friday flag
and a full-table target-mean encoding, each shown with its real univariate AUC. Everything is executed and scored against a
truth the model never sees, including the model each run would ship, under deployment-realistic conditions.

## 5. Dataset selection

{{design.A.DEVELOPMENT.datasets}} DEVELOPMENT and {{design.A.UNSEEN.datasets}} UNSEEN datasets for Study A;
{{design.B.DEVELOPMENT.datasets}} DEVELOPMENT and {{design.B.UNSEEN.datasets}} UNSEEN for Study B. Selection criteria,
sources, row counts and sampling are in `outputs/study_a/study-a-datasets.md` and
`outputs/study_b/datasets-and-dictionaries.md` (generated from code). The set covers churn, credit, cross-sell, medical,
fraud (synthetic, documented generator), e-commerce, demand forecasting (regression), multiclass geometry and a randomized
uplift experiment (Hillstrom), with imbalanced, high-dimensional, high-row-count and mixed-type cases.

* Study A DEVELOPMENT: {{design.A.DEVELOPMENT.dataset_list}}
* Study A UNSEEN: {{design.A.UNSEEN.dataset_list}}
* Study B DEVELOPMENT: {{design.B.DEVELOPMENT.dataset_list}}
* Study B UNSEEN: {{design.B.UNSEEN.dataset_list}}

## 6. Development vs unseen split

The split is by dataset and was fixed in `common/data.py` before any model run. DEVELOPMENT was used for everything that
can change a measurement: harness debugging, contract validation, scoring, parsing, statistics and figures. UNSEEN was run
once, after a freeze record per study (`outputs/FREEZE_RECORD_A.json`, `outputs/FREEZE_RECORD_B.json`) that hashes every
source file that defines prompts, topologies, conditions, task contracts, scoring, evaluation and statistics, every
rendered UNSEEN prompt, every candidate list, every loaded dataset frame and the model digest. `python -m rs2610.freeze
--verify A|B` recomputes all of it; it ran before and after each UNSEEN evaluation (logs in
`artifacts/study_*/unseen_run.log`).

Within each dataset a 25 % test split mirrors deployment (time-ordered for temporal data, grouped for repeated entities,
stratified otherwise, seed 20261027). It is used only for regret (Study A) and deployed quality (Study B).

## 7. Model and runtime configuration

| | |
|---|---|
| Model | `qwen2.5:7b` (Q4_K_M), Ollama digest `845dbda0ea48…` recorded on every call |
| Runtime | local Ollama, one inference slot; requests are served one at a time |
| Decoding | temperature 0.4, LLM seed = repeat index, context 12,288 tokens, JSON-schema constrained output |
| Seeds | Study A: DEVELOPMENT 1, UNSEEN 1-3. Study B: DEVELOPMENT 1, UNSEEN 1-2 (compute budget fixed before results) |
| Latency | server compute = prefill + decode time reported by the server (ACTUAL), audited for host suspend (§24.1); wall time is kept separately and is contaminated by queueing |
| Tokens | prompt and output tokens reported by the server (ACTUAL) |
| Cost | `NOT_APPLICABLE_LOCAL`: no provider bill; energy use UNKNOWN and never converted to zero |

The substrate was forced: the Anthropic key in the environment had no credit and no other provider key was configured. A
1.5B model was tried and rejected during setup because it switched language mid-output. **Every result in this report is a
result about one local 7B open-weight model**, not about frontier models.

## 8. Controlled variables

Held fixed across arms: model and digest, runtime, temperature, seed design, system prompt, task wording, evidence or
profile bytes, option sets (Study A always includes UNDETERMINED), output contract of the final decision, evaluation
authority, DEVELOPMENT/UNSEEN split. Not equalised by design and measured instead: number of calls, tokens and compute time
(Study A: that is what topology costs; Study B: the extra stages of B and E). Study A rotates mode order by instance and
seed (Latin-square style) because the server caches the shared prefix and the first mode on an instance pays its prefill.

## 9. Study A topology implementations

Athena ships `council/{chain,tree,graph}_of_thoughts.py`; those are post-hoc aggregations of the same persona answers, so
the model calls are identical whichever mode is selected. Comparing them would compare labels. The study therefore uses a
research harness (`study_a/topologies.py`) whose topologies differ in *execution*:

| Mode | Calls | Execution | Recorded structure |
|---|---|---|---|
| DIRECT | 1 | decision fields only | — |
| COT | 1 | schema forces 3-6 ordered steps; step k declares `depends_on_step = k − 1` and cites evidence ids; the decision is generated after the steps | steps, dependency respected, evidence per step |
| TOT | 5 | propose 3 distinct branches → one **isolated** call per branch (2 refinement leaves, scores, fatal-flaw flag) → deterministic prune to the top 2 → select among survivors only | branches, leaves, pruned, duplicates, leaf scores |
| GOT | 5 | atomic claim nodes from the evidence (shared by all candidates) → candidate nodes → typed edges (claim → candidate supports / contradicts, claim ↔ claim conflicts) → deterministic weighted propagation (conflicted claims × 0.5, contradicting concerns × 1.5) → aggregation call (merge the top two when compatible) → decide over the graph summary | claim / candidate / merged nodes, edges, conflict edges, reused claims, `is_dag_beyond_tree` |

Only structured, observable artifacts are stored: ids, scores, edges, evidence references, the selected option, rejected
options and a ≤ 40-word rationale. No hidden chain-of-thought is requested, stored or published.

## 14. Study B semantic conditions

| Condition | Extra context | Extra stage before the analysis | Calls |
|---|---|---|---|
| A_RAW | — | — | 2 |
| B_SELF | — | self-inference: dataset, target and row meaning, a role and meaning for every column | 3 |
| C_DICT | data-owner description + dictionary | — | 2 |
| D_RULES | C + business rules, code dictionary, known constraints | — | 2 |
| E_FULL | same as D | verification: every documented column judged plausible / contradicted / unverifiable against the profile, with evidence | 3 |

Every call lists the allowed values of every enum in its schema (`conditions.enum_legend`), and the feature-engineering
contract has one required judgement per offered candidate, keyed by its exact id (`conditions.fe_schema`). Both are
corrections of contract defects found during DEVELOPMENT (section 24).

## 15. Study B adversarial design

`outputs/study_b/adversarial-cases.md` lists every construction. T1 anonymized names with a correct dictionary (A, C, E); T2
names without a dictionary (= A_RAW); T3 incomplete dictionary (definitions of ids, leaks, artifacts and the target removed;
C, D, E); T4 misleading dictionary (three false entries per dataset, one of which hides a leak behind an innocent
description; C, D, E); T5 identifier trap; T6 post-outcome leakage; T7 warehouse artifact (statistically strong,
semantically absurd) and T7b target-mean encoding; T8 causal/predictive trap (`intervention_column` must be an actionable
lever, not the strongest non-actionable predictor). T5-T8 are carried by every trapped dataset in every condition.

## 16. Study B feature-engineering methodology

Every proposal is executed (DSL: `ratio, diff, product, sum, mean, log1p, is_zero`) and scored separately on:
statistical value (3-fold CV gain of LightGBM over the clean base, development rows), semantic validity (deterministic rule
table over annotated semantic types: valid / invalid / unknown), leakage risk (an input is an identifier, post-outcome
column, artifact or the target), stability (share of folds with positive gain), interpretability, and generalization (gain
on the deployment-masked test split). The **Athena validator** (truth-free) keeps a feature only if it is computable, the
run did not judge it leaky, it does not read the target, it does not use a column the run itself blocked, and its CV gain is
positive. *Statistically strong but semantically invalid* = CV gain > 0.005 and invalid or leaky.

**Deployment-realistic downstream (B8).** The model a run would ship is LightGBM on all columns minus what the run blocked
plus its retained features. It is scored on the test split as deployment would see it: post-outcome values and the target
are unknown (NaN) and identifier/artifact values carry no target information (permuted). *Deployment collapse* = the shipped
model loses more than 0.05 (AUC or R²) between the rows as recorded and the rows as deployed. References: the truth-clean
model and the use-everything model.

## 23. Threats to validity

* **One model.** All conclusions are about `qwen2.5:7b` at temperature 0.4. Frontier models may separate topologies or use
  context differently; this study cannot say.
* **Benchmark construction.** Study A's evidence packets and Study B's traps were written by the same author as the
  harness. The traps are deliberately strong (e.g. a target-ordered key with AUC ≈ 0.9) and documented truthfully; real
  leaks are subtler. Results are about these constructions.
* **Few clusters.** UNSEEN has 8-9 datasets per study. Dataset-cluster bootstrap intervals are coarse and can be
  anti-conservative with few clusters; a claim in this report needs the instance- or pair-level test as well.
* **Lenient references.** Study A's `accept` sets use a paired t-test on 5 CV folds, which accepts many options when
  differences are small (several families have more than one acceptable answer); regret on the test split is reported to
  compensate.
* **Scripted families.** CAUSAL_VS_PREDICTIVE and TRUST_PLAN are scripted, not measured; their regret is UNKNOWN by design.
* **Output contract.** Both studies use JSON-schema constrained decoding. Section 24 shows how much a contract can distort
  measurements; we fixed the defects we found, and cannot exclude ones we did not find.
* **Seeds.** 3 (Study A) and 2 (Study B) seeds on UNSEEN; seed-to-seed variance is reported, not modelled.

## 24. Harness defects discovered during development (before experimental freeze)

These were found on DEVELOPMENT data, diagnosed, fixed and journaled (`JOURNAL.md`) before the corresponding UNSEEN run.
Affected runs are preserved and excluded, never deleted.

1. **Blind enums (Study B).** The schema constrained enum fields (business problem, unit, metric, split, …) but the prompt
   did not list the allowed values, so grammar-constrained decoding forced the model onto whichever allowed string its
   tokens drifted into: `business_problem = demand_forecast` in 8 of 10 runs while the free-text target meaning was correct
   in every one ("the customer has churned"). This was a measurement artifact, not a semantic failure of the model. Fix:
   an "ALLOWED VALUES" legend for every enum, identical in every condition; 4 probe calls confirmed it. The
   {{design.B.superseded_v1_runs|int}} affected runs are in `artifacts/study_b/superseded_v1/`. (The diagnosis used the first 10;
   the job ran on until stopped. The freeze record's note says 10, and the journal corrects it.)
2. **Unmatchable candidate judgements (Study B).** Free-string candidate ids let the model rename (`cand_target_mean_A1`) or
   skip candidates; 47 of 258 judgements could not be matched and counted as wrong. Found after the first Study B freeze
   but before any UNSEEN run; the freeze was superseded, the contract keyed by candidate id, DEVELOPMENT rerun. The
   {{design.B.superseded_v2_runs}} runs and the v1 freeze record are in `artifacts/study_b/superseded_v2/`.
3. **Validator did not refuse target-reading features (Study B)**: a proposal `mean(season, cnt)` (the bike target) was
   retained and the shipped model's deployed R² fell to −1.33. Rule added.
4. **Mixed-scale aggregation (Study B)**: a mean over AUCs and an unbounded R² was dominated by one collapsed run; the
   headline downstream metric became deployment collapse plus the median gap.
5. **Field collision (Study B)**: the scored field `split` overwrote the DEVELOPMENT/UNSEEN column; renamed.
6. **GoT claim references (Study A)**: GoT's decision cites its own claim nodes; evidence utilization now resolves a claim
   to the evidence it rests on.
7. **Binding token caps (Study A, GoT)**: 1 of 41 DEVELOPMENT edge calls truncated at 700 tokens; caps raised.
8. Infrastructure: pandas 3 string dtype silently blanked categoricals (failed run #1); a too-small verification cap
   (failed run #2); an MLP argument error (#3); a binary-only solver on a multiclass dataset (#4); three transient
   file-permission revocations of background jobs (#5, #6), fixed by retried appends and a restart wrapper.

### 24.1 Findings after the freeze (documented, not patched)

Two issues surfaced after the freeze while reading UNSEEN outputs. In both cases the frozen prompts, scoring rules,
topology definitions and evaluation logic were left untouched, the UNSEEN evaluation was **not** invalidated, and the
handling was decided and journaled (`JOURNAL.md`, 2026-10-28 ~13:00 and ~13:20) before any condition-level comparison
that would show which way it cuts.

1. **Token caps bind on the widest unseen dataset (Study B).** `coil_caravan` has 86 columns, wider than any
   DEVELOPMENT dataset the caps were sized from. Two UNSEEN calls hit their cap: A_RAW s1's feature-engineering stage
   (1800/1800 tokens, so 0 proposals and 0 candidate judgements) and E_FULL s2's verification stage (3200/3200; with no
   parsed verification that E run is operationally identical to D_RULES s2). The pre-registered rule counts parse failures
   as failures, so the primary analysis keeps them. An exploratory sensitivity analysis excluding `coil_caravan`
   (`study_b/sensitivity.py`, outside the freeze) changes the sign of no confirmatory contrast but flips three Holm
   verdicts at 0.05 (§18). Study A UNSEEN got the same ledger truncation audit
   ({{design.A.UNSEEN.truncated_calls|int}} truncated calls).
2. **Host suspend leaked into the server timers (latency only).** The host slept overnight during the Study B UNSEEN
   run. One call recorded 35,308 s of decode time, and seven more decoded at 3–4.5 tok/s around suspend and resume
   (median elsewhere ≈ 23–25 tok/s). During the Study A UNSEEN run the battery ran down: the host throttled from about
   15:58 and macOS forced a 70-minute sleep at 16:26. Its slow calls (15:58–16:26 and 17:36–17:42) fall under the same rule;
   {{lat.A.UNSEEN.TOT.n_known}}–{{lat.A.UNSEEN.DIRECT.n_known}} of {{lat.A.UNSEEN.DIRECT.n_runs}} runs per mode keep a known
   compute. Decisions, outputs and token counts are unaffected. In the reporting layer
   (`analyze_extra.latency_audit`), a call slower than 5 tok/s is HOST_SUSPEND_CONTAMINATED and its compute is UNKNOWN
   (never 0). A run's compute is known only if all its calls are clean. Every latency figure in this report comes from
   `outputs/study_*/latency-audit.csv`, with the number of known runs alongside it. The latency columns of the frozen
   result tables are not quoted.

## 29. Reproducibility

```
cd research
python -m rs2610.study_a.evidence                      # measured evidence (14 datasets)
python -m rs2610.study_a.run --split DEVELOPMENT --seeds 1 --tag dev
python -m rs2610.study_b.run --split DEVELOPMENT --seeds 1 --grid all --tag dev
python -m rs2610.freeze --write A ; python -m rs2610.freeze --write B
python -m rs2610.freeze --verify A ; python -m rs2610.study_a.run --split UNSEEN --seeds 1 2 3 --tag unseen
python -m rs2610.freeze --verify B ; python -m rs2610.study_b.run --split UNSEEN --seeds 1 2 --grid all --tag unseen
python -m rs2610.study_a.analyze ; python -m rs2610.study_b.analyze ; python -m rs2610.study_a.structure_fig
python -m rs2610.analyze_extra ; python -m rs2610.make_facts ; python -m rs2610.make_report
```

Every LLM response is in the ledgers (`artifacts/study_*/ledger.jsonl`, keyed by request hash), so every analysis can be
recomputed without the model: the client serves byte-identical requests from the ledger. Raw datasets are not committed;
their sources and frame hashes are in the freeze records. Trace: blog claim → its fact-key placeholder → `outputs/facts-index.md` (table,
row, column) → result CSV → run row (`artifacts/study_*/runs_*.jsonl`) → ledger request hash → model digest, prompt hash
and dataset frame hash in the freeze record.
