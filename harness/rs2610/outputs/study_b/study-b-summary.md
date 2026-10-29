## 17. Study B results

All numbers in this section are UNSEEN (8 datasets: iranian_churn, taiwan_default, coil_caravan, diabetes_readmission, card_fraud_synth, online_shoppers, thyroid_sick, hillstrom_email),
seeds 1-2, 116 runs, 276 model calls, 2 failed
calls. The main grid is the *trapped* variant: n = 16 runs per condition
(8 datasets × 2 seeds). Brackets are 95 % dataset-cluster
bootstrap intervals.

### 17.1 Semantic decisions (trapped grid)

| | A_RAW | B_SELF | C_DICT | D_RULES | E_FULL |
|---|---|---|---|---|---|
| core semantic accuracy | 76.8% | 80.4% | 81.2% | 85.7% | 87.5% |
| task understood (problem, target, unit) | 75.0% | 87.5% | 87.5% | 100.0% | 100.0% |
| identifier trap caught | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| post-outcome recall | 59.4% | 81.2% | 93.8% | 100.0% | 78.1% |
| warehouse artifact caught | 81.2% | 100.0% | 93.8% | 93.8% | 81.2% |
| all traps blocked | 43.8% | 75.0% | 81.2% | 93.8% | 56.2% |
| leak precision | 100.0% | 91.7% | 100.0% | 89.2% | 85.4% |
| over-exclusion (clean columns blocked, per run) | 0.06 | 0.25 | 0.06 | 0.19 | 0.12 |
| intervention lever actionable | 0.0% | 10.0% | 40.0% | 30.0% | 40.0% |
| lever = strongest non-actionable predictor (T8) | 12.5% | 12.5% | 12.5% | 12.5% | 25.0% |
| split strategy correct | 75.0% | 75.0% | 75.0% | 75.0% | 75.0% |
| self-reported semantic confidence | 0.92 | 0.91 | 0.92 | 0.93 | 0.91 |

Table B1. UNSEEN, trapped grid, n = 16 runs per condition. Source:
`outputs/study_b/study-b-results.csv`.

Every condition caught the target-ordered identifier in every run; the identifier trap did not separate the conditions.
What separated them was post-outcome leakage: A_RAW blocked 59.4% of post-outcome
columns, D_RULES 100.0%. E_FULL, which adds a verification stage to D_RULES,
blocked 78.1% and blocked all traps in
56.2% of runs against 93.8% for
D_RULES. The model's self-reported confidence was between 0.91 and 0.93
in every condition and did not track any of this (section 17.5).

### 17.2 Deployment-realistic downstream (B8)

| | A_RAW | B_SELF | C_DICT | D_RULES | E_FULL |
|---|---|---|---|---|---|
| deployment collapse (> 0.05 lost at deployment) | 43.8% | 18.8% | 6.2% | 6.2% | 25.0% |
| median gap to the truth-clean model | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| mean deployed score (AUC / R²) | 0.750 | 0.772 | 0.793 | 0.782 | 0.769 |
| mean optimism (recorded − deployed) | 0.122 | 0.073 | 0.008 | 0.008 | 0.067 |

Table B2. The model each run would ship, scored on the test split as deployment would see it. Source:
`outputs/study_b/study-b-results.csv`.

The downstream effect is concentrated. On `online_shoppers` the shipped model's deployed AUC was
0.61 with A_RAW and 0.93
with C_DICT and D_RULES; on `iranian_churn` every condition shipped a model scoring between 0.98 and 0.99.
The mean deployed score therefore moves little (0.750 → 0.782)
while the collapse rate moves a lot: A_RAW shipped a model that lost more than 0.05 at deployment in
43.8% of runs, C_DICT and D_RULES in 6.2%.
Per-dataset values: `outputs/study_b/study-b-per-dataset.csv`.

### 17.3 Adversarial variants (T1 anonymized, T3 incomplete, T4 misleading)

| variant | condition | n | core accuracy | … same datasets, trapped | all traps blocked | … same datasets, trapped | deployment collapse |
|---|---|---|---|---|---|---|---|
| T1 anonymized | A_RAW | 4 | 71.4% | 89.3% | 0.0% | 50.0% | 50.0% |
| T1 anonymized | C_DICT | 4 | 96.4% | 96.4% | 50.0% | 100.0% | 0.0% |
| T1 anonymized | E_FULL | 4 | 92.9% | 96.4% | 75.0% | 75.0% | 0.0% |
| T3 incomplete | C_DICT | 4 | 78.6% | 75.0% | 50.0% | 75.0% | 50.0% |
| T3 incomplete | D_RULES | 4 | 82.1% | 78.6% | 25.0% | 100.0% | 75.0% |
| T3 incomplete | E_FULL | 4 | 75.0% | 82.1% | 100.0% | 100.0% | 0.0% |
| T4 misleading | C_DICT | 4 | 92.9% | 89.3% | 50.0% | 75.0% | 0.0% |
| T4 misleading | D_RULES | 4 | 89.3% | 85.7% | 100.0% | 100.0% | 0.0% |
| T4 misleading | E_FULL | 4 | 89.3% | 89.3% | 50.0% | 100.0% | 25.0% |

Table B3. Adversarial variants, UNSEEN, 2 datasets × 2 seeds each (descriptive; n is too small for tests). The "same
datasets, trapped" columns are the main-grid result of the same condition on the same two datasets, the like-for-like
reference (T1: taiwan_default, iranian_churn; T3: taiwan_default, diabetes_readmission; T4: taiwan_default,
card_fraud_synth).

**T1 (anonymized names, H10).** With names replaced by `f01…fNN`, A_RAW's core accuracy fell from
89.3% (same datasets, real names) to
71.4%, and it blocked all traps in none of
4 runs. With the (correct) dictionary, C_DICT scored
96.4% anonymized and 96.4%
with real names: the dictionary carried what the names had carried. Consistent with H10, on 4 runs per cell.

**T3 (incomplete dictionary).** No condition reported a single one of the removed definitions as missing
(missing-semantics recall 0.0% in E_FULL, the same in C and D). E_FULL
nevertheless blocked all traps in 100.0% of its runs (same datasets,
complete dictionary: 100.0%); D_RULES fell from
100.0% to 25.0%.
The incomplete variant also drops the business rules, so D_RULES under T3 has less context than C_DICT in the main
grid. Whatever E caught, it caught from the profile, not from noticing a gap.

**T4 (misleading dictionary, H9).** Each misleading dictionary contains two swapped meanings and one post-outcome leak
described innocently. E_FULL's verification stage marked 7 of
8 swapped entries as contradicted, but only 1
of 4 hidden leaks; C_DICT and D_RULES, which have no verification stage, listed
1 and 0 of
8 swapped entries as contradictions. So E challenges metadata that conflicts with the
profile (a "credit limit" whose values look like ages), and does not challenge an innocent-sounding description of a
leak. The leak itself was still blocked as post-outcome in 4/4
(C), 4/4 (D) and
3/4 (E) runs; this benchmark cannot say which
signal did it (the column names `chargeback_filed` and `collections_referral_oct` remain readable). E also raised
2.0 false contradictions per run against correct entries, and under the
misleading dictionary it blocked all traps in 50.0% of runs against
100.0% on the same datasets with the truthful dictionary. Per-entry
verdicts: `outputs/study_b/t4-falsified-entries.csv`.

### 17.4 Stability across seeds

Agreement of the two seeds per dataset (trapped grid): the business problem, split strategy, primary metric, model family
and HPO depth agreed in every dataset and condition. The set of blocked columns agreed in
62.5% (A_RAW), 62.5% (C_DICT),
62.5% (D_RULES) and 25.0% (E_FULL)
of datasets. Source: `outputs/study_b/study-b-stability.csv`.

### 17.5 Confidence versus correctness

| | A_RAW | B_SELF | C_DICT | D_RULES | E_FULL |
|---|---|---|---|---|---|
| mean confidence | 0.92 | 0.91 | 0.92 | 0.93 | 0.90 |
| mean core accuracy | 0.76 | 0.80 | 0.85 | 0.86 | 0.87 |
| overconfidence | +16.0 pp | +10.3 pp | +7.4 pp | +7.0 pp | +2.9 pp |
| Spearman(confidence, accuracy) | 0.03 | -0.09 | -0.11 | 0.23 | 0.09 |

Table B4. All UNSEEN runs of each condition (all variants). Source: `outputs/study_b/study-b-confidence.csv`.

## 19. Study B feature-engineering results

UNSEEN, trapped grid: 317 proposals and 460 candidate judgements.

| | A_RAW | B_SELF | C_DICT | D_RULES | E_FULL |
|---|---|---|---|---|---|
| proposals | 63 | 62 | 62 | 70 | 60 |
| computable | 41 | 42 | 38 | 46 | 36 |
| leaky proposals (truth) | 24 | 21 | 16 | 24 | 19 |
| … of which the model itself called leakage "likely" | 41.7% | 66.7% | 25.0% | 58.3% | 42.1% |
| statistically strong but invalid | 16 | 15 | 11 | 13 | 12 |
| retained by the validator | 15 | 15 | 16 | 16 | 13 |
| … valid and leak-free | 13 | 11 | 13 | 11 | 11 |
| … leaky | 1 | 1 | 0 | 0 | 1 |
| invalid offered candidates rejected | 67.2% | 79.7% | 76.6% | 82.8% | 73.4% |
| valid offered candidates accepted | 89.3% | 85.7% | 100.0% | 96.4% | 96.4% |
| accepted: identifier transform | 31.2% | 6.2% | 12.5% | 12.5% | 18.8% |
| accepted: post-outcome flag | 18.8% | 25.0% | 25.0% | 12.5% | 25.0% |
| accepted: Friday load flag | 50.0% | 50.0% | 31.2% | 37.5% | 43.8% |
| accepted: full-table target mean | 6.2% | 0.0% | 25.0% | 6.2% | 18.8% |

Table B6. Feature engineering, UNSEEN trapped grid. Sources: `outputs/study_b/generated-features.csv` (one row per
proposal with operation, inputs, semantic and statistical rationale, self-reported vs scored leakage, validity, stability,
CV gain, deployment-masked test gain, retained / rejected and reason) and `outputs/study_b/candidate-judgements.csv`.

**Proposals are mostly copies.** 97.8% of proposals reproduce one of the six
offered candidates (same operation and inputs). Feature engineering in this benchmark is therefore mostly *judging* what
was offered, not inventing.

**The Friday flag is the hardest trap.** The warehouse-load artifact was accepted in
50.0% of A_RAW and 43.8% of E_FULL runs; the
lowest acceptance, C_DICT's, was 31.2%. Its univariate AUC is modest
(0.695 on `thyroid_sick`); one acceptance reason read
"The feature has a moderate univariate AUC and captures potential day-specific effects, though with a risk of leakage."

**Context also made things worse in one place.** C_DICT accepted the full-table target-mean encoding in
25.0% of runs, against 6.2% for A_RAW;
the acceptance reasons cite what the grouping column means
(`coil_caravan`: "It provides demographic insights into the likelihood of owning a mobile home and can be useful for stratifying the customer base.").

**Statistically attractive, semantically invalid, shipped.** The validator retained one leaky proposal in each of A_RAW,
B_SELF and E_FULL. The clearest: on `hillstrom_email` (B_SELF,
seed 1) the model proposed `is_zero(spend)`,
where `spend` is recorded only after a conversion, rated its own leakage risk "none",
and wrote: "The univariate AUC of 1.0 suggests that spend is a strong predictor of conversion, and the flag could capture this information.". CV gain 0.420;
gain on the deployment-masked test split 0.0009. Because the validator is
truth-free it can only refuse what the run itself flagged; this feature passed every rule it has.

**A valid feature that helped.** On `card_fraud_synth` (A_RAW) the
retained `sum(txn_count_1h|txn_count_24h)` ("A high sum could indicate a burst of transactions, which might be a red flag for fraud.")
gained 0.0063 in CV and 0.0208 on
the deployment-masked test, stable in 66.7% of folds. The best legitimate CV gain is a small
fraction of the best leaky one; a selection rule based on CV gain alone would prefer the leak.
