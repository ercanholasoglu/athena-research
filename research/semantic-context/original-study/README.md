# Study B: semantic context with `qwen2.5:7b`

Pre-registered, frozen on 2026-10-27 (the first freeze was superseded before any unseen run; see
[HISTORY](../../../docs/HISTORY.md)) and evaluated once on unseen data. Full report: sections on Study B in
[FINAL_RESEARCH_REPORT.md](../../../harness/rs2610/FINAL_RESEARCH_REPORT.md).
Design: [study-b-design.md](../../../harness/rs2610/outputs/study_b/study-b-design.md).

## Conditions

Every condition receives byte-identical profile, target summary, task text, schema and candidate list. Only the
following differ ([semantic-condition-contracts.md](../../../harness/rs2610/outputs/study_b/semantic-condition-contracts.md)):

| condition | extra context | extra stage | calls |
|---|---|---|---|
| A_RAW | — | — | 2 |
| B_SELF | — | self-inference of dataset, target and row meaning and of every column's role; shown to the analysis | 3 |
| C_DICT | owner documentation: description and dictionary | — | 2 |
| D_RULES | C + business rules, code dictionary, constraints | — | 2 |
| E_FULL | as D | verification: each documented column judged plausible / contradicted / unverifiable against the profile | 3 |

- **Builder.** The prompt builder and the dictionary and rules injection are
  [`study_b/conditions.py`](../../../harness/rs2610/study_b/conditions.py) (`documentation()`); listed in
  [conditions/](conditions/).

## Traps

Every dataset carries the same traps ([`study_b/variants.py`](../../../harness/rs2610/study_b/variants.py),
[traps/](traps/)):

| trap type | how it is built |
|---|---|
| identifier | `record_key`, unique per row, assigned in target order during an extract |
| post-outcome | a natural post-outcome column (e.g. bank `duration`, Hillstrom `visit`/`spend`), or one inserted with a truthful description |
| warehouse artifact | `load_weekday`: positives were batch-loaded on Fridays |
| leakage in candidates | an identifier transform, a post-outcome flag, the Friday flag and a target-mean encoding on the full table, each shown with its univariate AUC |
| causal vs predictive | `intervention_column` must be an actionable lever, not the strongest non-actionable predictor |

Adversarial dictionary variants:

- **anonymized:** all names x1…xn, correct dictionary;
- **incomplete:** definitions of identifiers, post-outcome and artifact columns and the target removed;
- **misleading:** 3 entries per dataset rewritten to false claims that the profile contradicts.

**Scoring.** The truth that decisions are scored against (`truth` in `common/data.py`, trap metadata, acceptance sets
in `study_b/score.py`) is never shown to the model.

## Result (unseen, trapped grid)

8 datasets × 2 seeds; 116 runs, 276 calls.

| condition | all traps blocked | deployment collapse | Holm p vs A_RAW (all traps blocked) |
|---|---|---|---|
| A_RAW | 43.8% | 43.8% | — |
| C_DICT | 81.2% | 6.2% | 0.102 |
| D_RULES | 93.8% | 6.2% | 0.046 |
| E_FULL | 56.2% | 25.0% | 0.480 |

- **Documentation and traps.** Rules and a dictionary raised trap blocking. D_RULES was the only contrast surviving
  Holm.
- **Verification pass.** E_FULL did not add to D_RULES.
- **Candidate copying.** 97.8% of feature proposals copied a listed
  candidate.
- **Material.** Every test is in [study-b-statistics.md](../../../harness/rs2610/outputs/study_b/study-b-statistics.md).

## Folders

| folder | contents |
|---|---|
| [configs/](configs/) | freeze record, design, the superseded first freeze |
| [conditions/](conditions/) | A_RAW … E_FULL builder, profile |
| [traps/](traps/) | trap and variant construction, dictionaries, falsified entries |
| [contracts/](contracts/) | analysis, feature-engineering, inference and verification schemas and enums (exported by `tools/export_prompts.py`) |
| [prompts/examples/](prompts/examples/) | the exact prompts and outputs of one dataset in all five conditions, replayed from the ledger |
| [evaluation/](evaluation/) | scoring, feature execution and held-out evaluation, runner |
| [statistics/](statistics/) | tests and sensitivity analyses |
| [results/](results/) | aggregate, per-dataset and run-level tables, run records, ledger |
| [figures/](figures/) | figures |
| [TRACE.md](TRACE.md) | article numbers → table, row, run, ledger, prompt, model, dataset hash |

## Limitations

- One local 7B model; 8 unseen datasets × 2 seeds.
- Token caps bound on the widest unseen dataset (post-freeze finding).
- More: [docs/LIMITATIONS.md](../../../docs/LIMITATIONS.md).
