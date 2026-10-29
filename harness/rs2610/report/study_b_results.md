## 17. Study B results

All numbers in this section are UNSEEN ({{design.B.UNSEEN.datasets}} datasets: {{design.B.UNSEEN.dataset_list}}),
seeds 1-2, {{design.B.UNSEEN.runs}} runs, {{design.B.UNSEEN.calls|int}} model calls, {{design.B.UNSEEN.failed_calls}} failed
calls. The main grid is the *trapped* variant: n = {{b.UNSEEN.trapped.A_RAW.n_runs}} runs per condition
({{b.UNSEEN.trapped.A_RAW.n_datasets}} datasets × {{b.UNSEEN.trapped.A_RAW.n_seeds}} seeds). Brackets are 95 % dataset-cluster
bootstrap intervals.

### 17.1 Semantic decisions (trapped grid)

| | A_RAW | B_SELF | C_DICT | D_RULES | E_FULL |
|---|---|---|---|---|---|
| core semantic accuracy | {{b.UNSEEN.trapped.A_RAW.core_semantic_accuracy|pct}} | {{b.UNSEEN.trapped.B_SELF.core_semantic_accuracy|pct}} | {{b.UNSEEN.trapped.C_DICT.core_semantic_accuracy|pct}} | {{b.UNSEEN.trapped.D_RULES.core_semantic_accuracy|pct}} | {{b.UNSEEN.trapped.E_FULL.core_semantic_accuracy|pct}} |
| task understood (problem, target, unit) | {{b.UNSEEN.trapped.A_RAW.task_understanding|pct}} | {{b.UNSEEN.trapped.B_SELF.task_understanding|pct}} | {{b.UNSEEN.trapped.C_DICT.task_understanding|pct}} | {{b.UNSEEN.trapped.D_RULES.task_understanding|pct}} | {{b.UNSEEN.trapped.E_FULL.task_understanding|pct}} |
| identifier trap caught | {{b.UNSEEN.trapped.A_RAW.id_trap_caught|pct}} | {{b.UNSEEN.trapped.B_SELF.id_trap_caught|pct}} | {{b.UNSEEN.trapped.C_DICT.id_trap_caught|pct}} | {{b.UNSEEN.trapped.D_RULES.id_trap_caught|pct}} | {{b.UNSEEN.trapped.E_FULL.id_trap_caught|pct}} |
| post-outcome recall | {{b.UNSEEN.trapped.A_RAW.post_event_recall|pct}} | {{b.UNSEEN.trapped.B_SELF.post_event_recall|pct}} | {{b.UNSEEN.trapped.C_DICT.post_event_recall|pct}} | {{b.UNSEEN.trapped.D_RULES.post_event_recall|pct}} | {{b.UNSEEN.trapped.E_FULL.post_event_recall|pct}} |
| warehouse artifact caught | {{b.UNSEEN.trapped.A_RAW.artifact_caught|pct}} | {{b.UNSEEN.trapped.B_SELF.artifact_caught|pct}} | {{b.UNSEEN.trapped.C_DICT.artifact_caught|pct}} | {{b.UNSEEN.trapped.D_RULES.artifact_caught|pct}} | {{b.UNSEEN.trapped.E_FULL.artifact_caught|pct}} |
| all traps blocked | {{b.UNSEEN.trapped.A_RAW.all_traps_blocked|pct}} | {{b.UNSEEN.trapped.B_SELF.all_traps_blocked|pct}} | {{b.UNSEEN.trapped.C_DICT.all_traps_blocked|pct}} | {{b.UNSEEN.trapped.D_RULES.all_traps_blocked|pct}} | {{b.UNSEEN.trapped.E_FULL.all_traps_blocked|pct}} |
| leak precision | {{b.UNSEEN.trapped.A_RAW.leak_precision|pct}} | {{b.UNSEEN.trapped.B_SELF.leak_precision|pct}} | {{b.UNSEEN.trapped.C_DICT.leak_precision|pct}} | {{b.UNSEEN.trapped.D_RULES.leak_precision|pct}} | {{b.UNSEEN.trapped.E_FULL.leak_precision|pct}} |
| over-exclusion (clean columns blocked, per run) | {{b.UNSEEN.trapped.A_RAW.over_exclusion|2}} | {{b.UNSEEN.trapped.B_SELF.over_exclusion|2}} | {{b.UNSEEN.trapped.C_DICT.over_exclusion|2}} | {{b.UNSEEN.trapped.D_RULES.over_exclusion|2}} | {{b.UNSEEN.trapped.E_FULL.over_exclusion|2}} |
| intervention lever actionable | {{b.UNSEEN.trapped.A_RAW.lever_actionable|pct}} | {{b.UNSEEN.trapped.B_SELF.lever_actionable|pct}} | {{b.UNSEEN.trapped.C_DICT.lever_actionable|pct}} | {{b.UNSEEN.trapped.D_RULES.lever_actionable|pct}} | {{b.UNSEEN.trapped.E_FULL.lever_actionable|pct}} |
| lever = strongest non-actionable predictor (T8) | {{b.UNSEEN.trapped.A_RAW.lever_is_predictive_trap|pct}} | {{b.UNSEEN.trapped.B_SELF.lever_is_predictive_trap|pct}} | {{b.UNSEEN.trapped.C_DICT.lever_is_predictive_trap|pct}} | {{b.UNSEEN.trapped.D_RULES.lever_is_predictive_trap|pct}} | {{b.UNSEEN.trapped.E_FULL.lever_is_predictive_trap|pct}} |
| split strategy correct | {{b.UNSEEN.trapped.A_RAW.split_correct|pct}} | {{b.UNSEEN.trapped.B_SELF.split_correct|pct}} | {{b.UNSEEN.trapped.C_DICT.split_correct|pct}} | {{b.UNSEEN.trapped.D_RULES.split_correct|pct}} | {{b.UNSEEN.trapped.E_FULL.split_correct|pct}} |
| self-reported semantic confidence | {{b.UNSEEN.trapped.A_RAW.semantic_confidence|2}} | {{b.UNSEEN.trapped.B_SELF.semantic_confidence|2}} | {{b.UNSEEN.trapped.C_DICT.semantic_confidence|2}} | {{b.UNSEEN.trapped.D_RULES.semantic_confidence|2}} | {{b.UNSEEN.trapped.E_FULL.semantic_confidence|2}} |

Table B1. UNSEEN, trapped grid, n = {{b.UNSEEN.trapped.A_RAW.n_runs}} runs per condition. Source:
`outputs/study_b/study-b-results.csv`.

Every condition caught the target-ordered identifier in every run; the identifier trap did not separate the conditions.
What separated them was post-outcome leakage: A_RAW blocked {{b.UNSEEN.trapped.A_RAW.post_event_recall|pct}} of post-outcome
columns, D_RULES {{b.UNSEEN.trapped.D_RULES.post_event_recall|pct}}. E_FULL, which adds a verification stage to D_RULES,
blocked {{b.UNSEEN.trapped.E_FULL.post_event_recall|pct}} and blocked all traps in
{{b.UNSEEN.trapped.E_FULL.all_traps_blocked|pct}} of runs against {{b.UNSEEN.trapped.D_RULES.all_traps_blocked|pct}} for
D_RULES. The model's self-reported confidence was between {{b.UNSEEN.trapped.B_SELF.semantic_confidence|2}} and {{b.UNSEEN.trapped.D_RULES.semantic_confidence|2}}
in every condition and did not track any of this (section 17.5).

### 17.2 Deployment-realistic downstream (B8)

| | A_RAW | B_SELF | C_DICT | D_RULES | E_FULL |
|---|---|---|---|---|---|
| deployment collapse (> 0.05 lost at deployment) | {{b.UNSEEN.trapped.A_RAW.deploy_collapse|pct}} | {{b.UNSEEN.trapped.B_SELF.deploy_collapse|pct}} | {{b.UNSEEN.trapped.C_DICT.deploy_collapse|pct}} | {{b.UNSEEN.trapped.D_RULES.deploy_collapse|pct}} | {{b.UNSEEN.trapped.E_FULL.deploy_collapse|pct}} |
| median gap to the truth-clean model | {{b.UNSEEN.trapped.A_RAW.deploy_gap_to_oracle_median|3}} | {{b.UNSEEN.trapped.B_SELF.deploy_gap_to_oracle_median|3}} | {{b.UNSEEN.trapped.C_DICT.deploy_gap_to_oracle_median|3}} | {{b.UNSEEN.trapped.D_RULES.deploy_gap_to_oracle_median|3}} | {{b.UNSEEN.trapped.E_FULL.deploy_gap_to_oracle_median|3}} |
| mean deployed score (AUC / R²) | {{b.UNSEEN.trapped.A_RAW.deploy_score|3}} | {{b.UNSEEN.trapped.B_SELF.deploy_score|3}} | {{b.UNSEEN.trapped.C_DICT.deploy_score|3}} | {{b.UNSEEN.trapped.D_RULES.deploy_score|3}} | {{b.UNSEEN.trapped.E_FULL.deploy_score|3}} |
| mean optimism (recorded − deployed) | {{b.UNSEEN.trapped.A_RAW.leak_inflation|3}} | {{b.UNSEEN.trapped.B_SELF.leak_inflation|3}} | {{b.UNSEEN.trapped.C_DICT.leak_inflation|3}} | {{b.UNSEEN.trapped.D_RULES.leak_inflation|3}} | {{b.UNSEEN.trapped.E_FULL.leak_inflation|3}} |

Table B2. The model each run would ship, scored on the test split as deployment would see it. Source:
`outputs/study_b/study-b-results.csv`.

The downstream effect is concentrated. On `online_shoppers` the shipped model's deployed AUC was
{{b.ds.UNSEEN.trapped.online_shoppers.A_RAW.deploy_score|2}} with A_RAW and {{b.ds.UNSEEN.trapped.online_shoppers.C_DICT.deploy_score|2}}
with C_DICT and D_RULES; on `iranian_churn` every condition shipped a model scoring between {{b.ds.UNSEEN.trapped.iranian_churn.E_FULL.deploy_score|2}} and {{b.ds.UNSEEN.trapped.iranian_churn.A_RAW.deploy_score|2}}.
The mean deployed score therefore moves little ({{b.UNSEEN.trapped.A_RAW.deploy_score|3}} → {{b.UNSEEN.trapped.D_RULES.deploy_score|3}})
while the collapse rate moves a lot: A_RAW shipped a model that lost more than 0.05 at deployment in
{{b.UNSEEN.trapped.A_RAW.deploy_collapse|pct}} of runs, C_DICT and D_RULES in {{b.UNSEEN.trapped.C_DICT.deploy_collapse|pct}}.
Per-dataset values: `outputs/study_b/study-b-per-dataset.csv`.

### 17.3 Adversarial variants (T1 anonymized, T3 incomplete, T4 misleading)

| variant | condition | n | core accuracy | … same datasets, trapped | all traps blocked | … same datasets, trapped | deployment collapse |
|---|---|---|---|---|---|---|---|
| T1 anonymized | A_RAW | {{b.UNSEEN.anonymized.A_RAW.n_runs}} | {{b.UNSEEN.anonymized.A_RAW.core_semantic_accuracy|pct}} | {{bx.matched.UNSEEN.anonymized.A_RAW.core_semantic_accuracy|pct}} | {{b.UNSEEN.anonymized.A_RAW.all_traps_blocked|pct}} | {{bx.matched.UNSEEN.anonymized.A_RAW.all_traps_blocked|pct}} | {{b.UNSEEN.anonymized.A_RAW.deploy_collapse|pct}} |
| T1 anonymized | C_DICT | {{b.UNSEEN.anonymized.C_DICT.n_runs}} | {{b.UNSEEN.anonymized.C_DICT.core_semantic_accuracy|pct}} | {{bx.matched.UNSEEN.anonymized.C_DICT.core_semantic_accuracy|pct}} | {{b.UNSEEN.anonymized.C_DICT.all_traps_blocked|pct}} | {{bx.matched.UNSEEN.anonymized.C_DICT.all_traps_blocked|pct}} | {{b.UNSEEN.anonymized.C_DICT.deploy_collapse|pct}} |
| T1 anonymized | E_FULL | {{b.UNSEEN.anonymized.E_FULL.n_runs}} | {{b.UNSEEN.anonymized.E_FULL.core_semantic_accuracy|pct}} | {{bx.matched.UNSEEN.anonymized.E_FULL.core_semantic_accuracy|pct}} | {{b.UNSEEN.anonymized.E_FULL.all_traps_blocked|pct}} | {{bx.matched.UNSEEN.anonymized.E_FULL.all_traps_blocked|pct}} | {{b.UNSEEN.anonymized.E_FULL.deploy_collapse|pct}} |
| T3 incomplete | C_DICT | {{b.UNSEEN.incomplete.C_DICT.n_runs}} | {{b.UNSEEN.incomplete.C_DICT.core_semantic_accuracy|pct}} | {{bx.matched.UNSEEN.incomplete.C_DICT.core_semantic_accuracy|pct}} | {{b.UNSEEN.incomplete.C_DICT.all_traps_blocked|pct}} | {{bx.matched.UNSEEN.incomplete.C_DICT.all_traps_blocked|pct}} | {{b.UNSEEN.incomplete.C_DICT.deploy_collapse|pct}} |
| T3 incomplete | D_RULES | {{b.UNSEEN.incomplete.D_RULES.n_runs}} | {{b.UNSEEN.incomplete.D_RULES.core_semantic_accuracy|pct}} | {{bx.matched.UNSEEN.incomplete.D_RULES.core_semantic_accuracy|pct}} | {{b.UNSEEN.incomplete.D_RULES.all_traps_blocked|pct}} | {{bx.matched.UNSEEN.incomplete.D_RULES.all_traps_blocked|pct}} | {{b.UNSEEN.incomplete.D_RULES.deploy_collapse|pct}} |
| T3 incomplete | E_FULL | {{b.UNSEEN.incomplete.E_FULL.n_runs}} | {{b.UNSEEN.incomplete.E_FULL.core_semantic_accuracy|pct}} | {{bx.matched.UNSEEN.incomplete.E_FULL.core_semantic_accuracy|pct}} | {{b.UNSEEN.incomplete.E_FULL.all_traps_blocked|pct}} | {{bx.matched.UNSEEN.incomplete.E_FULL.all_traps_blocked|pct}} | {{b.UNSEEN.incomplete.E_FULL.deploy_collapse|pct}} |
| T4 misleading | C_DICT | {{b.UNSEEN.misleading.C_DICT.n_runs}} | {{b.UNSEEN.misleading.C_DICT.core_semantic_accuracy|pct}} | {{bx.matched.UNSEEN.misleading.C_DICT.core_semantic_accuracy|pct}} | {{b.UNSEEN.misleading.C_DICT.all_traps_blocked|pct}} | {{bx.matched.UNSEEN.misleading.C_DICT.all_traps_blocked|pct}} | {{b.UNSEEN.misleading.C_DICT.deploy_collapse|pct}} |
| T4 misleading | D_RULES | {{b.UNSEEN.misleading.D_RULES.n_runs}} | {{b.UNSEEN.misleading.D_RULES.core_semantic_accuracy|pct}} | {{bx.matched.UNSEEN.misleading.D_RULES.core_semantic_accuracy|pct}} | {{b.UNSEEN.misleading.D_RULES.all_traps_blocked|pct}} | {{bx.matched.UNSEEN.misleading.D_RULES.all_traps_blocked|pct}} | {{b.UNSEEN.misleading.D_RULES.deploy_collapse|pct}} |
| T4 misleading | E_FULL | {{b.UNSEEN.misleading.E_FULL.n_runs}} | {{b.UNSEEN.misleading.E_FULL.core_semantic_accuracy|pct}} | {{bx.matched.UNSEEN.misleading.E_FULL.core_semantic_accuracy|pct}} | {{b.UNSEEN.misleading.E_FULL.all_traps_blocked|pct}} | {{bx.matched.UNSEEN.misleading.E_FULL.all_traps_blocked|pct}} | {{b.UNSEEN.misleading.E_FULL.deploy_collapse|pct}} |

Table B3. Adversarial variants, UNSEEN, 2 datasets × 2 seeds each (descriptive; n is too small for tests). The "same
datasets, trapped" columns are the main-grid result of the same condition on the same two datasets, the like-for-like
reference (T1: taiwan_default, iranian_churn; T3: taiwan_default, diabetes_readmission; T4: taiwan_default,
card_fraud_synth).

**T1 (anonymized names, H10).** With names replaced by `f01…fNN`, A_RAW's core accuracy fell from
{{bx.matched.UNSEEN.anonymized.A_RAW.core_semantic_accuracy|pct}} (same datasets, real names) to
{{b.UNSEEN.anonymized.A_RAW.core_semantic_accuracy|pct}}, and it blocked all traps in none of
{{b.UNSEEN.anonymized.A_RAW.n_runs}} runs. With the (correct) dictionary, C_DICT scored
{{b.UNSEEN.anonymized.C_DICT.core_semantic_accuracy|pct}} anonymized and {{bx.matched.UNSEEN.anonymized.C_DICT.core_semantic_accuracy|pct}}
with real names: the dictionary carried what the names had carried. Consistent with H10, on 4 runs per cell.

**T3 (incomplete dictionary).** No condition reported a single one of the removed definitions as missing
(missing-semantics recall {{b.UNSEEN.incomplete.E_FULL.missing_semantics_recall|pct}} in E_FULL, the same in C and D). E_FULL
nevertheless blocked all traps in {{b.UNSEEN.incomplete.E_FULL.all_traps_blocked|pct}} of its runs (same datasets,
complete dictionary: {{bx.matched.UNSEEN.incomplete.E_FULL.all_traps_blocked|pct}}); D_RULES fell from
{{bx.matched.UNSEEN.incomplete.D_RULES.all_traps_blocked|pct}} to {{b.UNSEEN.incomplete.D_RULES.all_traps_blocked|pct}}.
The incomplete variant also drops the business rules, so D_RULES under T3 has less context than C_DICT in the main
grid. Whatever E caught, it caught from the profile, not from noticing a gap.

**T4 (misleading dictionary, H9).** Each misleading dictionary contains two swapped meanings and one post-outcome leak
described innocently. E_FULL's verification stage marked {{bx.t4.UNSEEN.E_FULL.swapped.verify_contradicted}} of
{{bx.t4.UNSEEN.E_FULL.swapped.n}} swapped entries as contradicted, but only {{bx.t4.UNSEEN.E_FULL.hidden_leak.verify_contradicted}}
of {{bx.t4.UNSEEN.E_FULL.hidden_leak.n}} hidden leaks; C_DICT and D_RULES, which have no verification stage, listed
{{bx.t4.UNSEEN.C_DICT.swapped.analysis_flagged}} and {{bx.t4.UNSEEN.D_RULES.swapped.analysis_flagged}} of
{{bx.t4.UNSEEN.C_DICT.swapped.n}} swapped entries as contradictions. So E challenges metadata that conflicts with the
profile (a "credit limit" whose values look like ages), and does not challenge an innocent-sounding description of a
leak. The leak itself was still blocked as post-outcome in {{bx.t4.UNSEEN.C_DICT.hidden_leak.blocked}}/{{bx.t4.UNSEEN.C_DICT.hidden_leak.n}}
(C), {{bx.t4.UNSEEN.D_RULES.hidden_leak.blocked}}/{{bx.t4.UNSEEN.D_RULES.hidden_leak.n}} (D) and
{{bx.t4.UNSEEN.E_FULL.hidden_leak.blocked}}/{{bx.t4.UNSEEN.E_FULL.hidden_leak.n}} (E) runs; this benchmark cannot say which
signal did it (the column names `chargeback_filed` and `collections_referral_oct` remain readable). E also raised
{{b.UNSEEN.misleading.E_FULL.false_contradictions|1}} false contradictions per run against correct entries, and under the
misleading dictionary it blocked all traps in {{b.UNSEEN.misleading.E_FULL.all_traps_blocked|pct}} of runs against
{{bx.matched.UNSEEN.misleading.E_FULL.all_traps_blocked|pct}} on the same datasets with the truthful dictionary. Per-entry
verdicts: `outputs/study_b/t4-falsified-entries.csv`.

### 17.4 Stability across seeds

Agreement of the two seeds per dataset (trapped grid): the business problem, split strategy, primary metric, model family
and HPO depth agreed in every dataset and condition. The set of blocked columns agreed in
{{b.stab.UNSEEN.trapped.A_RAW.agree_blocked|pct}} (A_RAW), {{b.stab.UNSEEN.trapped.C_DICT.agree_blocked|pct}} (C_DICT),
{{b.stab.UNSEEN.trapped.D_RULES.agree_blocked|pct}} (D_RULES) and {{b.stab.UNSEEN.trapped.E_FULL.agree_blocked|pct}} (E_FULL)
of datasets. Source: `outputs/study_b/study-b-stability.csv`.

### 17.5 Confidence versus correctness

| | A_RAW | B_SELF | C_DICT | D_RULES | E_FULL |
|---|---|---|---|---|---|
| mean confidence | {{b.conf.UNSEEN.A_RAW.confidence_mean|2}} | {{b.conf.UNSEEN.B_SELF.confidence_mean|2}} | {{b.conf.UNSEEN.C_DICT.confidence_mean|2}} | {{b.conf.UNSEEN.D_RULES.confidence_mean|2}} | {{b.conf.UNSEEN.E_FULL.confidence_mean|2}} |
| mean core accuracy | {{b.conf.UNSEEN.A_RAW.core_accuracy_mean|2}} | {{b.conf.UNSEEN.B_SELF.core_accuracy_mean|2}} | {{b.conf.UNSEEN.C_DICT.core_accuracy_mean|2}} | {{b.conf.UNSEEN.D_RULES.core_accuracy_mean|2}} | {{b.conf.UNSEEN.E_FULL.core_accuracy_mean|2}} |
| overconfidence | {{b.conf.UNSEEN.A_RAW.overconfidence|pp}} pp | {{b.conf.UNSEEN.B_SELF.overconfidence|pp}} pp | {{b.conf.UNSEEN.C_DICT.overconfidence|pp}} pp | {{b.conf.UNSEEN.D_RULES.overconfidence|pp}} pp | {{b.conf.UNSEEN.E_FULL.overconfidence|pp}} pp |
| Spearman(confidence, accuracy) | {{b.conf.UNSEEN.A_RAW.spearman_conf_vs_core|2}} | {{b.conf.UNSEEN.B_SELF.spearman_conf_vs_core|2}} | {{b.conf.UNSEEN.C_DICT.spearman_conf_vs_core|2}} | {{b.conf.UNSEEN.D_RULES.spearman_conf_vs_core|2}} | {{b.conf.UNSEEN.E_FULL.spearman_conf_vs_core|2}} |

Table B4. All UNSEEN runs of each condition (all variants). Source: `outputs/study_b/study-b-confidence.csv`.

## 18. Study B statistics

Confirmatory family (pre-registered, `outputs/study_b/study-b-design.md`): UNSEEN, trapped grid, each condition vs A_RAW,
pairs = (dataset, seed), n = {{b.paired.UNSEEN.trapped.core_semantic_accuracy.E_FULL.n_pairs}} pairs. Wilcoxon signed-rank
(raw p), exact sign test, Holm across the 4 contrasts within each metric (corrected p); difference = condition − A_RAW with a
95 % dataset-cluster bootstrap interval.

| metric | condition | diff | 95 % CI | better / worse pairs | sign p | Wilcoxon p | Holm p |
|---|---|---|---|---|---|---|---|
| core semantic accuracy (H5) | C_DICT | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.C_DICT.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.core_semantic_accuracy.C_DICT.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.core_semantic_accuracy.C_DICT.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.C_DICT.n_better}} / {{b.paired.UNSEEN.trapped.core_semantic_accuracy.C_DICT.n_worse}} | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.C_DICT.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.C_DICT.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.C_DICT.holm_p|p}} |
| | D_RULES | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.D_RULES.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.core_semantic_accuracy.D_RULES.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.core_semantic_accuracy.D_RULES.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.D_RULES.n_better}} / {{b.paired.UNSEEN.trapped.core_semantic_accuracy.D_RULES.n_worse}} | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.D_RULES.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.D_RULES.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.D_RULES.holm_p|p}} |
| | E_FULL | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.E_FULL.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.core_semantic_accuracy.E_FULL.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.core_semantic_accuracy.E_FULL.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.E_FULL.n_better}} / {{b.paired.UNSEEN.trapped.core_semantic_accuracy.E_FULL.n_worse}} | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.E_FULL.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.E_FULL.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.E_FULL.holm_p|p}} |
| | B_SELF | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.B_SELF.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.core_semantic_accuracy.B_SELF.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.core_semantic_accuracy.B_SELF.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.B_SELF.n_better}} / {{b.paired.UNSEEN.trapped.core_semantic_accuracy.B_SELF.n_worse}} | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.B_SELF.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.B_SELF.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.core_semantic_accuracy.B_SELF.holm_p|p}} |
| all traps blocked (H6) | C_DICT | {{b.paired.UNSEEN.trapped.all_traps_blocked.C_DICT.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.all_traps_blocked.C_DICT.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.all_traps_blocked.C_DICT.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.all_traps_blocked.C_DICT.n_better}} / {{b.paired.UNSEEN.trapped.all_traps_blocked.C_DICT.n_worse}} | {{b.paired.UNSEEN.trapped.all_traps_blocked.C_DICT.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.all_traps_blocked.C_DICT.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.all_traps_blocked.C_DICT.holm_p|p}} |
| | D_RULES | {{b.paired.UNSEEN.trapped.all_traps_blocked.D_RULES.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.all_traps_blocked.D_RULES.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.all_traps_blocked.D_RULES.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.all_traps_blocked.D_RULES.n_better}} / {{b.paired.UNSEEN.trapped.all_traps_blocked.D_RULES.n_worse}} | {{b.paired.UNSEEN.trapped.all_traps_blocked.D_RULES.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.all_traps_blocked.D_RULES.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.all_traps_blocked.D_RULES.holm_p|p}} |
| | E_FULL | {{b.paired.UNSEEN.trapped.all_traps_blocked.E_FULL.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.all_traps_blocked.E_FULL.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.all_traps_blocked.E_FULL.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.all_traps_blocked.E_FULL.n_better}} / {{b.paired.UNSEEN.trapped.all_traps_blocked.E_FULL.n_worse}} | {{b.paired.UNSEEN.trapped.all_traps_blocked.E_FULL.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.all_traps_blocked.E_FULL.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.all_traps_blocked.E_FULL.holm_p|p}} |
| | B_SELF | {{b.paired.UNSEEN.trapped.all_traps_blocked.B_SELF.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.all_traps_blocked.B_SELF.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.all_traps_blocked.B_SELF.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.all_traps_blocked.B_SELF.n_better}} / {{b.paired.UNSEEN.trapped.all_traps_blocked.B_SELF.n_worse}} | {{b.paired.UNSEEN.trapped.all_traps_blocked.B_SELF.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.all_traps_blocked.B_SELF.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.all_traps_blocked.B_SELF.holm_p|p}} |
| leak recall (H6) | C_DICT | {{b.paired.UNSEEN.trapped.leak_recall.C_DICT.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.leak_recall.C_DICT.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.leak_recall.C_DICT.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.leak_recall.C_DICT.n_better}} / {{b.paired.UNSEEN.trapped.leak_recall.C_DICT.n_worse}} | {{b.paired.UNSEEN.trapped.leak_recall.C_DICT.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.leak_recall.C_DICT.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.leak_recall.C_DICT.holm_p|p}} |
| | D_RULES | {{b.paired.UNSEEN.trapped.leak_recall.D_RULES.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.leak_recall.D_RULES.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.leak_recall.D_RULES.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.leak_recall.D_RULES.n_better}} / {{b.paired.UNSEEN.trapped.leak_recall.D_RULES.n_worse}} | {{b.paired.UNSEEN.trapped.leak_recall.D_RULES.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.leak_recall.D_RULES.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.leak_recall.D_RULES.holm_p|p}} |
| | E_FULL | {{b.paired.UNSEEN.trapped.leak_recall.E_FULL.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.leak_recall.E_FULL.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.leak_recall.E_FULL.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.leak_recall.E_FULL.n_better}} / {{b.paired.UNSEEN.trapped.leak_recall.E_FULL.n_worse}} | {{b.paired.UNSEEN.trapped.leak_recall.E_FULL.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.leak_recall.E_FULL.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.leak_recall.E_FULL.holm_p|p}} |
| | B_SELF | {{b.paired.UNSEEN.trapped.leak_recall.B_SELF.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.leak_recall.B_SELF.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.leak_recall.B_SELF.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.leak_recall.B_SELF.n_better}} / {{b.paired.UNSEEN.trapped.leak_recall.B_SELF.n_worse}} | {{b.paired.UNSEEN.trapped.leak_recall.B_SELF.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.leak_recall.B_SELF.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.leak_recall.B_SELF.holm_p|p}} |
| candidate accuracy (H7) | C_DICT | {{b.paired.UNSEEN.trapped.candidate_accuracy.C_DICT.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.candidate_accuracy.C_DICT.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.candidate_accuracy.C_DICT.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.candidate_accuracy.C_DICT.n_better}} / {{b.paired.UNSEEN.trapped.candidate_accuracy.C_DICT.n_worse}} | {{b.paired.UNSEEN.trapped.candidate_accuracy.C_DICT.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.candidate_accuracy.C_DICT.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.candidate_accuracy.C_DICT.holm_p|p}} |
| | D_RULES | {{b.paired.UNSEEN.trapped.candidate_accuracy.D_RULES.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.candidate_accuracy.D_RULES.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.candidate_accuracy.D_RULES.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.candidate_accuracy.D_RULES.n_better}} / {{b.paired.UNSEEN.trapped.candidate_accuracy.D_RULES.n_worse}} | {{b.paired.UNSEEN.trapped.candidate_accuracy.D_RULES.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.candidate_accuracy.D_RULES.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.candidate_accuracy.D_RULES.holm_p|p}} |
| | E_FULL | {{b.paired.UNSEEN.trapped.candidate_accuracy.E_FULL.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.candidate_accuracy.E_FULL.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.candidate_accuracy.E_FULL.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.candidate_accuracy.E_FULL.n_better}} / {{b.paired.UNSEEN.trapped.candidate_accuracy.E_FULL.n_worse}} | {{b.paired.UNSEEN.trapped.candidate_accuracy.E_FULL.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.candidate_accuracy.E_FULL.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.candidate_accuracy.E_FULL.holm_p|p}} |
| valid & leak-free proposal share (H7) | C_DICT | {{b.paired.UNSEEN.trapped.feature_valid_share.C_DICT.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.feature_valid_share.C_DICT.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.feature_valid_share.C_DICT.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.feature_valid_share.C_DICT.n_better}} / {{b.paired.UNSEEN.trapped.feature_valid_share.C_DICT.n_worse}} | {{b.paired.UNSEEN.trapped.feature_valid_share.C_DICT.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.feature_valid_share.C_DICT.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.feature_valid_share.C_DICT.holm_p|p}} |
| | D_RULES | {{b.paired.UNSEEN.trapped.feature_valid_share.D_RULES.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.feature_valid_share.D_RULES.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.feature_valid_share.D_RULES.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.feature_valid_share.D_RULES.n_better}} / {{b.paired.UNSEEN.trapped.feature_valid_share.D_RULES.n_worse}} | {{b.paired.UNSEEN.trapped.feature_valid_share.D_RULES.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.feature_valid_share.D_RULES.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.feature_valid_share.D_RULES.holm_p|p}} |
| | E_FULL | {{b.paired.UNSEEN.trapped.feature_valid_share.E_FULL.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.feature_valid_share.E_FULL.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.feature_valid_share.E_FULL.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.feature_valid_share.E_FULL.n_better}} / {{b.paired.UNSEEN.trapped.feature_valid_share.E_FULL.n_worse}} | {{b.paired.UNSEEN.trapped.feature_valid_share.E_FULL.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.feature_valid_share.E_FULL.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.feature_valid_share.E_FULL.holm_p|p}} |
| deployment collapse (H8) | C_DICT | {{b.paired.UNSEEN.trapped.deploy_collapse.C_DICT.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.deploy_collapse.C_DICT.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.deploy_collapse.C_DICT.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.deploy_collapse.C_DICT.n_worse}} / {{b.paired.UNSEEN.trapped.deploy_collapse.C_DICT.n_better}} | {{b.paired.UNSEEN.trapped.deploy_collapse.C_DICT.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.deploy_collapse.C_DICT.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.deploy_collapse.C_DICT.holm_p|p}} |
| | D_RULES | {{b.paired.UNSEEN.trapped.deploy_collapse.D_RULES.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.deploy_collapse.D_RULES.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.deploy_collapse.D_RULES.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.deploy_collapse.D_RULES.n_worse}} / {{b.paired.UNSEEN.trapped.deploy_collapse.D_RULES.n_better}} | {{b.paired.UNSEEN.trapped.deploy_collapse.D_RULES.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.deploy_collapse.D_RULES.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.deploy_collapse.D_RULES.holm_p|p}} |
| | E_FULL | {{b.paired.UNSEEN.trapped.deploy_collapse.E_FULL.diff|pp}} pp | [{{b.paired.UNSEEN.trapped.deploy_collapse.E_FULL.ci_lo|pp}}, {{b.paired.UNSEEN.trapped.deploy_collapse.E_FULL.ci_hi|pp}}] | {{b.paired.UNSEEN.trapped.deploy_collapse.E_FULL.n_worse}} / {{b.paired.UNSEEN.trapped.deploy_collapse.E_FULL.n_better}} | {{b.paired.UNSEEN.trapped.deploy_collapse.E_FULL.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.deploy_collapse.E_FULL.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.deploy_collapse.E_FULL.holm_p|p}} |
| gap to truth-clean model (H8) | C_DICT | {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.C_DICT.diff|3}} | [{{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.C_DICT.ci_lo|3}}, {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.C_DICT.ci_hi|3}}] | {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.C_DICT.n_worse}} / {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.C_DICT.n_better}} | {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.C_DICT.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.C_DICT.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.C_DICT.holm_p|p}} |
| | D_RULES | {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.D_RULES.diff|3}} | [{{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.D_RULES.ci_lo|3}}, {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.D_RULES.ci_hi|3}}] | {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.D_RULES.n_worse}} / {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.D_RULES.n_better}} | {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.D_RULES.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.D_RULES.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.D_RULES.holm_p|p}} |
| | E_FULL | {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.E_FULL.diff|3}} | [{{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.E_FULL.ci_lo|3}}, {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.E_FULL.ci_hi|3}}] | {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.E_FULL.n_worse}} / {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.E_FULL.n_better}} | {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.E_FULL.sign_test_p|p}} | {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.E_FULL.wilcoxon_p|p}} | {{b.paired.UNSEEN.trapped.deploy_gap_to_oracle.E_FULL.holm_p|p}} |

Table B5. Confirmatory tests. "Better / worse pairs" counts pairs where the condition is better / worse than A_RAW (for
collapse and gap, lower is better). B_SELF rows for H7/H8 are in `study-b-paired-tests.csv`. Source:
`outputs/study_b/study-b-paired-tests.csv`.

**Verdicts at Holm 0.05.**

* H5 core semantic accuracy: supported for E_FULL only (Holm p {{b.paired.UNSEEN.trapped.core_semantic_accuracy.E_FULL.holm_p|4}});
  D_RULES's interval excludes zero but its Holm p is {{b.paired.UNSEEN.trapped.core_semantic_accuracy.D_RULES.holm_p|p}}.
* H6 leakage: supported for D_RULES on all traps blocked (Holm p {{b.paired.UNSEEN.trapped.all_traps_blocked.D_RULES.holm_p|p}})
  not on leak recall, where Holm p is {{b.paired.UNSEEN.trapped.leak_recall.D_RULES.holm_p|4}}, just above the threshold. B_SELF and C_DICT
  have raw p below 0.05 and Holm p above it. **E_FULL is not distinguishable from A_RAW** on either leakage metric.
* H7 candidate judgements and valid proposals: we did not detect a statistically distinguishable difference.
* H8 deployment collapse: C_DICT and D_RULES collapsed in fewer pairs ({{b.paired.UNSEEN.trapped.deploy_collapse.C_DICT.n_worse}}
  fewer vs {{b.paired.UNSEEN.trapped.deploy_collapse.C_DICT.n_better}} more), raw Wilcoxon p {{b.paired.UNSEEN.trapped.deploy_collapse.C_DICT.wilcoxon_p|p}},
  Holm p {{b.paired.UNSEEN.trapped.deploy_collapse.C_DICT.holm_p|p}}: not significant after correction. Median gap to the
  truth-clean model: no detectable difference.

**Fragility (exploratory sensitivity, post-freeze; section 24).** Excluding `coil_caravan`, where two UNSEEN calls hit
their token caps, changes no sign. It changes three Holm verdicts: E_FULL core accuracy
({{b.sens.core_semantic_accuracy.E_FULL.holm_p_primary|4}} → {{b.sens.core_semantic_accuracy.E_FULL.holm_p_excl|p}}),
D_RULES leak recall ({{b.sens.leak_recall.D_RULES.holm_p_primary|4}} → {{b.sens.leak_recall.D_RULES.holm_p_excl|p}}) and
D_RULES deployment collapse ({{b.sens.deploy_collapse.D_RULES.holm_p_primary|p}} → {{b.sens.deploy_collapse.D_RULES.holm_p_excl|p}}).
The directions are stable; which individual contrasts clear 0.05 is not, at {{b.paired.UNSEEN.trapped.core_semantic_accuracy.E_FULL.n_pairs}}
pairs from {{design.B.UNSEEN.datasets}} datasets. Source: `outputs/study_b/study-b-sensitivity.csv`.

## 19. Study B feature-engineering results

UNSEEN, trapped grid: {{bx.UNSEEN.features_proposed}} proposals and {{bx.UNSEEN.candidate_judgements}} candidate judgements.

| | A_RAW | B_SELF | C_DICT | D_RULES | E_FULL |
|---|---|---|---|---|---|
| proposals | {{bx.UNSEEN.A_RAW.features_proposed}} | {{bx.UNSEEN.B_SELF.features_proposed}} | {{bx.UNSEEN.C_DICT.features_proposed}} | {{bx.UNSEEN.D_RULES.features_proposed}} | {{bx.UNSEEN.E_FULL.features_proposed}} |
| computable | {{bx.UNSEEN.A_RAW.features_computable}} | {{bx.UNSEEN.B_SELF.features_computable}} | {{bx.UNSEEN.C_DICT.features_computable}} | {{bx.UNSEEN.D_RULES.features_computable}} | {{bx.UNSEEN.E_FULL.features_computable}} |
| leaky proposals (truth) | {{bx.UNSEEN.A_RAW.leaky_proposed}} | {{bx.UNSEEN.B_SELF.leaky_proposed}} | {{bx.UNSEEN.C_DICT.leaky_proposed}} | {{bx.UNSEEN.D_RULES.leaky_proposed}} | {{bx.UNSEEN.E_FULL.leaky_proposed}} |
| … of which the model itself called leakage "likely" | {{bx.UNSEEN.A_RAW.leaky_self_flagged_likely|pct}} | {{bx.UNSEEN.B_SELF.leaky_self_flagged_likely|pct}} | {{bx.UNSEEN.C_DICT.leaky_self_flagged_likely|pct}} | {{bx.UNSEEN.D_RULES.leaky_self_flagged_likely|pct}} | {{bx.UNSEEN.E_FULL.leaky_self_flagged_likely|pct}} |
| statistically strong but invalid | {{bx.UNSEEN.A_RAW.strong_but_invalid}} | {{bx.UNSEEN.B_SELF.strong_but_invalid}} | {{bx.UNSEEN.C_DICT.strong_but_invalid}} | {{bx.UNSEEN.D_RULES.strong_but_invalid}} | {{bx.UNSEEN.E_FULL.strong_but_invalid}} |
| retained by the validator | {{bx.UNSEEN.A_RAW.retained}} | {{bx.UNSEEN.B_SELF.retained}} | {{bx.UNSEEN.C_DICT.retained}} | {{bx.UNSEEN.D_RULES.retained}} | {{bx.UNSEEN.E_FULL.retained}} |
| … valid and leak-free | {{bx.UNSEEN.A_RAW.retained_valid}} | {{bx.UNSEEN.B_SELF.retained_valid}} | {{bx.UNSEEN.C_DICT.retained_valid}} | {{bx.UNSEEN.D_RULES.retained_valid}} | {{bx.UNSEEN.E_FULL.retained_valid}} |
| … leaky | {{bx.UNSEEN.A_RAW.retained_leaky}} | {{bx.UNSEEN.B_SELF.retained_leaky}} | {{bx.UNSEEN.C_DICT.retained_leaky}} | {{bx.UNSEEN.D_RULES.retained_leaky}} | {{bx.UNSEEN.E_FULL.retained_leaky}} |
| invalid offered candidates rejected | {{bx.UNSEEN.A_RAW.invalid_candidate_rejection|pct}} | {{bx.UNSEEN.B_SELF.invalid_candidate_rejection|pct}} | {{bx.UNSEEN.C_DICT.invalid_candidate_rejection|pct}} | {{bx.UNSEEN.D_RULES.invalid_candidate_rejection|pct}} | {{bx.UNSEEN.E_FULL.invalid_candidate_rejection|pct}} |
| valid offered candidates accepted | {{bx.UNSEEN.A_RAW.valid_candidate_acceptance|pct}} | {{bx.UNSEEN.B_SELF.valid_candidate_acceptance|pct}} | {{bx.UNSEEN.C_DICT.valid_candidate_acceptance|pct}} | {{bx.UNSEEN.D_RULES.valid_candidate_acceptance|pct}} | {{bx.UNSEEN.E_FULL.valid_candidate_acceptance|pct}} |
| accepted: identifier transform | {{bx.UNSEEN.A_RAW.accept_rate.identifier|pct}} | {{bx.UNSEEN.B_SELF.accept_rate.identifier|pct}} | {{bx.UNSEEN.C_DICT.accept_rate.identifier|pct}} | {{bx.UNSEEN.D_RULES.accept_rate.identifier|pct}} | {{bx.UNSEEN.E_FULL.accept_rate.identifier|pct}} |
| accepted: post-outcome flag | {{bx.UNSEEN.A_RAW.accept_rate.post_outcome|pct}} | {{bx.UNSEEN.B_SELF.accept_rate.post_outcome|pct}} | {{bx.UNSEEN.C_DICT.accept_rate.post_outcome|pct}} | {{bx.UNSEEN.D_RULES.accept_rate.post_outcome|pct}} | {{bx.UNSEEN.E_FULL.accept_rate.post_outcome|pct}} |
| accepted: Friday load flag | {{bx.UNSEEN.A_RAW.accept_rate.artifact|pct}} | {{bx.UNSEEN.B_SELF.accept_rate.artifact|pct}} | {{bx.UNSEEN.C_DICT.accept_rate.artifact|pct}} | {{bx.UNSEEN.D_RULES.accept_rate.artifact|pct}} | {{bx.UNSEEN.E_FULL.accept_rate.artifact|pct}} |
| accepted: full-table target mean | {{bx.UNSEEN.A_RAW.accept_rate.target_leak|pct}} | {{bx.UNSEEN.B_SELF.accept_rate.target_leak|pct}} | {{bx.UNSEEN.C_DICT.accept_rate.target_leak|pct}} | {{bx.UNSEEN.D_RULES.accept_rate.target_leak|pct}} | {{bx.UNSEEN.E_FULL.accept_rate.target_leak|pct}} |

Table B6. Feature engineering, UNSEEN trapped grid. Sources: `outputs/study_b/generated-features.csv` (one row per
proposal with operation, inputs, semantic and statistical rationale, self-reported vs scored leakage, validity, stability,
CV gain, deployment-masked test gain, retained / rejected and reason) and `outputs/study_b/candidate-judgements.csv`.

**Proposals are mostly copies.** {{bx.UNSEEN.proposals_copying_candidates|pct}} of proposals reproduce one of the six
offered candidates (same operation and inputs). Feature engineering in this benchmark is therefore mostly *judging* what
was offered, not inventing.

**The Friday flag is the hardest trap.** The warehouse-load artifact was accepted in
{{bx.UNSEEN.A_RAW.accept_rate.artifact|pct}} of A_RAW and {{bx.UNSEEN.E_FULL.accept_rate.artifact|pct}} of E_FULL runs; the
lowest acceptance, C_DICT's, was {{bx.UNSEEN.C_DICT.accept_rate.artifact|pct}}. Its univariate AUC is modest
({{ex.artifact_accepted.univariate_auc|3}} on `{{ex.artifact_accepted.dataset_id}}`); one acceptance reason read
"{{ex.artifact_accepted.reason}}"

**Context also made things worse in one place.** C_DICT accepted the full-table target-mean encoding in
{{bx.UNSEEN.C_DICT.accept_rate.target_leak|pct}} of runs, against {{bx.UNSEEN.A_RAW.accept_rate.target_leak|pct}} for A_RAW;
the acceptance reasons cite what the grouping column means
(`{{ex.target_encoding_accepted.dataset_id}}`: "{{ex.target_encoding_accepted.reason}}").

**Statistically attractive, semantically invalid, shipped.** The validator retained one leaky proposal in each of A_RAW,
B_SELF and E_FULL. The clearest: on `{{ex.strong_invalid_retained.dataset_id}}` ({{ex.strong_invalid_retained.condition}},
seed {{ex.strong_invalid_retained.seed}}) the model proposed `{{ex.strong_invalid_retained.op}}({{ex.strong_invalid_retained.inputs}})`,
where `spend` is recorded only after a conversion, rated its own leakage risk "{{ex.strong_invalid_retained.model_leakage_assessment}}",
and wrote: "{{ex.strong_invalid_retained.statistical_rationale}}". CV gain {{ex.strong_invalid_retained.statistical_value_cv_gain|3}};
gain on the deployment-masked test split {{ex.strong_invalid_retained.generalization_test_gain|4}}. Because the validator is
truth-free it can only refuse what the run itself flagged; this feature passed every rule it has.

**A valid feature that helped.** On `{{ex.legit_feature_best.dataset_id}}` ({{ex.legit_feature_best.condition}}) the
retained `{{ex.legit_feature_best.op}}({{ex.legit_feature_best.inputs}})` ("{{ex.legit_feature_best.business_interpretation}}")
gained {{ex.legit_feature_best.statistical_value_cv_gain|4}} in CV and {{ex.legit_feature_best.generalization_test_gain|4}} on
the deployment-masked test, stable in {{ex.legit_feature_best.stability|pct}} of folds. The best legitimate CV gain is a small
fraction of the best leaky one; a selection rule based on CV gain alone would prefer the leak.

## 20. Study B failures

* **Leak-blind acceptance.** Post-outcome flags with univariate AUC {{ex.post_outcome_accepted.univariate_auc|3}} were accepted
  ({{ex.post_outcome_accepted.dataset_id}}, {{ex.post_outcome_accepted.condition}}: "{{ex.post_outcome_accepted.reason}}").
  Identifier transforms with AUC {{ex.id_trap_accepted.univariate_auc|3}} were accepted ({{ex.id_trap_accepted.dataset_id}},
  {{ex.id_trap_accepted.condition}}: "{{ex.id_trap_accepted.reason}}").
* **Verification without challenge (E_FULL).** E's verification stage rated {{bx.t4.UNSEEN.E_FULL.hidden_leak.n}} hidden-leak entries and
  contradicted {{bx.t4.UNSEEN.E_FULL.hidden_leak.verify_contradicted}} (the others: "plausible"), raised false contradictions, and E blocked all traps less often than D_RULES with identical context. Its
  blocked-column set was the least stable across seeds ({{b.stab.UNSEEN.trapped.E_FULL.agree_blocked|pct}} agreement).
* **No gap detection.** Under the incomplete dictionary no condition reported a removed definition as missing.
* **Lever choice.** An actionable intervention lever was named in at most {{b.UNSEEN.trapped.C_DICT.lever_actionable|pct}}
  of runs in any condition (A_RAW {{b.UNSEEN.trapped.A_RAW.lever_actionable|pct}}).
* **Self-assessment.** Mean self-reported confidence was between {{b.conf.UNSEEN.E_FULL.confidence_mean|2}} and {{b.conf.UNSEEN.D_RULES.confidence_mean|2}}
  in every condition and was overconfident by {{b.conf.UNSEEN.E_FULL.overconfidence|pp}} to {{b.conf.UNSEEN.A_RAW.overconfidence|pp}} pp.
* **Cap failures (harness).** {{design.B.UNSEEN.truncated_calls}} UNSEEN calls hit their token cap on the 86-column
  `coil_caravan` (section 24); both runs are scored as failures, as pre-registered.
