# Study B — semantic condition contracts

Source of truth: `study_b/conditions.py` (prompts and schemas), `study_b/profile.py` (what every condition sees),
`study_b/score.py` (acceptance sets). This file restates them; on any conflict the code wins.

## What every condition receives (identical bytes)

* System prompt: the semantic-understanding layer must work only from what it is shown; names may be uninformative,
  documentation may be incomplete or wrong.
* `DATASET PROFILE (development split)`: for each column, dtype, integer-valued flag, min/median/max or top-4 values with
  shares, number and ratio of unique values, missing share, Spearman correlation with row position, and univariate
  association with the target (folded ROC-AUC, out-of-fold target-mean for text; |Spearman| for regression).
* Target summary (class shares or range).
* The same analysis task text and the same JSON schema (21 fields), then the same feature-engineering task text, schema and
  candidate list.

## What differs

| Condition | Extra context | Extra stage before analysis | Calls |
|---|---|---|---|
| A_RAW | — | — | 2 |
| B_SELF | — | **self-inference**: dataset meaning, target meaning, row meaning, `role ∈ {identifier, pre_outcome_feature, post_outcome, target_derived, artifact, time, group_key, treatment, unknown}` + meaning guess for every column. Its output is shown to the analysis stage. | 3 |
| C_DICT | `DATA OWNER DOCUMENTATION`: description + dictionary | — | 2 |
| D_RULES | C + business rules + code dictionary + known constraints | — | 2 |
| E_FULL | same as D | **verification**: every documented column judged plausible / contradicted / unverifiable against the profile, with evidence; overall trust. Its output is shown to the analysis stage. | 3 |

Token caps: inference/verification 3,200; analysis 1,500; FE 1,800 (identical wherever the stage exists).

## Scored analysis fields → metric (B6)

| Field | Metric | Scoring |
|---|---|---|
| business_problem | TASK UNDERSTANDING | ∈ acceptance set (`PROBLEM_OK`) |
| target_meaning | TARGET SEMANTIC | contains a dataset keyword (`TARGET_KW`, e.g. telco: churn/leave/left/cancel) |
| prediction_unit | ENTITY / GRAIN | ∈ `UNIT_OK` |
| temporal_structure | TEMPORAL RECOGNITION | ∈ `TEMPORAL_OK` |
| id_columns | ID DETECTION | recall / precision vs ids ∪ {record_key}; `id_trap_caught` = record_key blocked anywhere |
| post_outcome_columns (+ artifacts, exclusions) | POST-EVENT LEAKAGE | recall of post-outcome ∪ target-derived columns |
| post ∪ artifact ∪ excluded | LEAKAGE DETECTION | `leak_recall`, `leak_precision`, `all_traps_blocked` |
| actionable_columns | ACTIONABILITY | precision vs truth actionable; protected attributes named actionable counted |
| intervention_column | CAUSAL VS PREDICTIVE | `lever_actionable`; `lever_is_predictive_trap` = equals the strongest non-actionable predictor |
| analysis_intent | CAUSAL VS PREDICTIVE | causal ∪ both for Hillstrom; predictive ∪ both elsewhere |
| primary_metric | METRIC SELECTION | ∈ truth `metrics_ok` |
| split_strategy | SPLIT STRATEGY | ∈ truth `split_ok` |
| model_family | MODEL FAMILY | Hillstrom: uplift_meta_learner; elsewhere recorded, not scored (all tabular families are defensible) |
| excluded_columns | over-exclusion | count of excluded columns that are not ids / leaks / protected / ambiguous |
| missing_semantics | T3 | recall of the removed definitions |
| dictionary_contradictions (+ E verification) | T4 | recall of falsified columns; false contradictions counted |

`core_semantic_accuracy` = mean of task, target, grain, temporal, intent, metric, split.

## Feature engineering (B3, B7)

The FE stage sees its own analysis, proposes ≤ 6 DSL features (`ratio, diff, product, sum, mean, log1p, is_zero`) with
semantic rationale, statistical rationale, leakage assessment and business interpretation, and judges every candidate. The
evaluator executes every proposal; see `study-b-design.md` for the rubric and validator.

## Acceptance sets (verbatim from `score.py`)

Problem: telco/iranian churn; german/taiwan credit_default; bank/coil cross_sell or purchase_intent; adult
income_classification; bike demand_forecast; diabetes readmission; fraud fraud; online purchase_intent; thyroid
medical_diagnosis; hillstrom uplift.
Unit: telco/iranian customer|account; german applicant|customer|person; bank customer|person; adult person; bike
time_period; taiwan customer|account|person; coil customer|household; diabetes encounter; fraud transaction; online session;
thyroid patient|person; hillstrom customer.
Temporal: bank time_ordered_rows|none; bike time_ordered_rows; iranian/taiwan observation_window_then_outcome; diabetes
repeated_entities; fraud time_ordered_rows|repeated_entities; online none|time_ordered_rows; hillstrom
observation_window_then_outcome|none; all others none.
Split: as `truth.split_ok` (diabetes group_kfold; bike time_based; fraud time_based|group_kfold; bank and online
stratified|time_based; others stratified).
