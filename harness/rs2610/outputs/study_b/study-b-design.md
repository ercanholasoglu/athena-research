# Study B — Does semantic context change Athena's decisions usefully? (design & pre-registration)

Status: **pre-registered before any UNSEEN run**; frozen in `outputs/FREEZE_RECORD_B.json` (Study A is frozen separately,
after its own DEVELOPMENT run).

## Research question

Does Athena understand what a dataset represents? And does semantic context (dictionary, rules, verification) improve task
identification, target understanding, leakage avoidance, feature engineering, model/validation decisions and deployed quality,
**on datasets it was not developed on**?

## Conditions (B1) — see `semantic-condition-contracts.md`

| | Context shown | Stages |
|---|---|---|
| A_RAW | column profile (names, dtypes, stats, univariate target association) | analysis → FE |
| B_SELF | A + an explicit self-inference stage (dataset meaning, target meaning, row meaning, a role for every column) | inference → analysis → FE |
| C_DICT | A + description + data dictionary | analysis → FE |
| D_RULES | C + business rules + code dictionary + known constraints | analysis → FE |
| E_FULL | D + a verification stage: every documented claim judged plausible / contradicted / unverifiable against the profile | verify → analysis → FE |

Same model, temperature, seeds, schemas, task wording and profile in every condition.

## Traps carried by every main-grid dataset (B4 T5-T7)

* `record_key`: unique per row, assigned in target order during an extract (an identifier trap with strong apparent signal).
* One post-outcome column: natural where it exists (bank `duration`, fraud `chargeback_filed`, bike `casual`/`registered`,
  Hillstrom `visit`/`spend`), otherwise inserted with a truthful dictionary description (e.g. telco `save_desk_outcome`).
* `load_weekday`: warehouse load weekday; positives were batch-loaded on Fridays (statistically attractive, semantically absurd).
* A candidate-feature list the model must accept or reject: 2 semantic recipes, an identifier transform, a post-outcome flag,
  the Friday flag, and a target-mean encoding computed on the full table. Each shows its measured univariate AUC.

## Adversarial variants (B4 T1, T3, T4; T2 = A_RAW; T8 within every run)

* T1 anonymized: all names → x1..xn, correct dictionary. Conditions A, C, E. Compared with A on named columns.
* T3 incomplete: definitions of ids, post-outcome/artifact columns and the target removed; rules removed. Conditions C, D, E.
* T4 misleading: 3 entries per dataset rewritten to false claims that the profile contradicts. Conditions C, D, E.
* T8 causal/predictive: `intervention_column` must be an actionable lever, not the strongest non-actionable predictor.

## Datasets and split

DEVELOPMENT: telco_churn, german_credit, bank_marketing, adult_income, bike_sharing.
UNSEEN: iranian_churn, taiwan_default, coil_caravan, diabetes_readmission, card_fraud_synth, online_shoppers, thyroid_sick, hillstrom_email.
T1/T3/T4 run on 2 DEVELOPMENT and 2 UNSEEN datasets each. DEVELOPMENT: 1 seed. UNSEEN: seeds 1-2. This is a compute budget fixed
before results: the local 7B model decodes about 25 tok/s on one slot shared with other work.

## Evaluation authority (never shown to the model)

`truth` in `common/data.py` + trap metadata in `study_b/variants.py` + acceptance sets in `study_b/score.py` (problem,
unit, temporal structure, target keywords, split, metrics, actionable and protected columns).

## Feature engineering (B3, B7)

Proposed features are written in an executable DSL (ratio, diff, product, sum, mean, log1p, is_zero) and actually computed.
Per feature, scored **separately**: statistical value (3-fold CV gain of LightGBM over the clean base), semantic validity
(deterministic rule table over annotated semantic types: valid / invalid / unknown), leakage risk (input is an id /
post-outcome / artifact / target), stability (share of folds with positive gain), interpretability, generalization (gain on
the deployment-masked test split). The Athena validator keeps a feature only if it is computable, the run itself did not judge
it leaky, it does not read the target column, it does not use a column the run blocked, and its CV gain is > 0. It does not
see the truth. (The target-column rule was added during DEVELOPMENT, before freeze: see JOURNAL ~22:30.)
`statistically_strong_semantically_invalid` flags features with CV gain > 0.005 that are invalid or leaky.

## Downstream (B8): deployment-realistic

The model a run would ship = all columns minus everything the run blocked (ids, post-outcome, artifacts, exclusions) plus
its retained features, LightGBM. It is scored on the test split **as deployment would see it**: post-outcome columns and the
target are unknown (NaN), and identifier/artifact values carry no target information (permuted). The naive test score (rows
as recorded) is reported next to it as leak inflation. **Headline downstream metrics** (fixed during DEVELOPMENT, before
freeze, because a mean over mixed AUC and unbounded R² is dominated by a single collapsed regression run):
`deploy_collapse` = leak inflation > 0.05 (share of runs, cluster-bootstrap CI) and the median of `deploy_gap_to_oracle`
(oracle-clean deployed score − the run's deployed score). Per-dataset deployed scores are reported unaggregated. References: *oracle-clean* (truth-clean features) and
*use-everything*. Validation choice is scored by |CV estimate under the run's own split − deployment score|.

## Hypotheses (confirmatory, UNSEEN, trapped grid, each condition vs A_RAW)

* **H5** task understanding (core semantic accuracy) is higher in C, D, E than in A.
* **H6** leakage avoidance (all traps blocked; leak recall) is higher in C, D, E than in A.
* **H7** feature engineering quality (candidate-judgement accuracy; valid-and-leak-free share of proposals) is higher in C, D, E.
* **H8** deployment collapse is rarer, and the gap to the oracle-clean model smaller, in C, D, E than in A.
* **H9** under T4, E detects more falsified entries than C and D.
* **H10** under T1, C and E recover more semantics than A on anonymized columns.

## Statistics

Pairs = (dataset, seed). Wilcoxon signed-rank and exact sign tests, Holm across the 4 contrasts within each metric; 95 % CIs by
dataset-cluster bootstrap. T1/T3/T4 are small (2 datasets × 2 seeds per condition on UNSEEN) and are reported descriptively.

## Development-phase changes (all before freeze; details in JOURNAL.md)

1. Enum legend: every call lists the allowed values of every enum in its schema. The 10 earlier runs are a harness defect
   discovered during development before experimental freeze; kept in `artifacts/study_b/superseded_v1/`, excluded.
2. Scored field `split` renamed `split_correct` (collided with the DEVELOPMENT/UNSEEN column).
3. Validator refuses features that read the target column.
4. Downstream headline = deployment collapse + median gap to oracle (see above).
5. Robustness only: retried JSONL appends and restart wrapper (no effect on any prompt, score or result).

## Confirmatory family and correction

Confirmatory = UNSEEN, trapped grid, each of B/C/D/E vs A_RAW, on: core semantic accuracy (H5), all traps blocked and leak
recall (H6), candidate-judgement accuracy and valid-and-leak-free share (H7), deployment collapse and gap to oracle (H8).
Holm across the 4 contrasts within each metric. Everything else (per-family, per-dataset, adversarial variants T1/T3/T4,
stability, confidence reliability, decision changes) is **exploratory** and labelled as such.
