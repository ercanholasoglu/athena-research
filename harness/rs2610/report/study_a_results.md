## 10. Study A results

All numbers in this section are UNSEEN unless labelled otherwise: {{design.A.UNSEEN.datasets}} datasets
({{design.A.UNSEEN.dataset_list}}), {{design.A.UNSEEN.instances}} decision instances ({{design.A.UNSEEN.adversarial_instances}}
adversarial) in {{design.A.UNSEEN.families}} families, seeds 1–3: {{design.A.UNSEEN.runs|int}} runs and
{{design.A.UNSEEN.calls|int}} model calls, {{design.A.UNSEEN.failed_calls}} failed call
({{design.A.UNSEEN.parse_failed_runs}} parse-failed run). Brackets are 95 % dataset-cluster bootstrap intervals.

### 10.1 Aggregate quality

| | DIRECT | COT | TOT | GOT |
|---|---|---|---|---|
| runs | {{a.UNSEEN.DIRECT.n_runs}} | {{a.UNSEEN.COT.n_runs}} | {{a.UNSEEN.TOT.n_runs}} | {{a.UNSEEN.GOT.n_runs}} |
| accuracy | {{a.UNSEEN.DIRECT.accuracy|pct}} | {{a.UNSEEN.COT.accuracy|pct}} | {{a.UNSEEN.TOT.accuracy|pct}} | {{a.UNSEEN.GOT.accuracy|pct}} |
| 95 % CI | [{{a.UNSEEN.DIRECT.accuracy_ci_lo|pct}}, {{a.UNSEEN.DIRECT.accuracy_ci_hi|pct}}] | [{{a.UNSEEN.COT.accuracy_ci_lo|pct}}, {{a.UNSEEN.COT.accuracy_ci_hi|pct}}] | [{{a.UNSEEN.TOT.accuracy_ci_lo|pct}}, {{a.UNSEEN.TOT.accuracy_ci_hi|pct}}] | [{{a.UNSEEN.GOT.accuracy_ci_lo|pct}}, {{a.UNSEEN.GOT.accuracy_ci_hi|pct}}] |
| accuracy, base instances | {{a.UNSEEN.DIRECT.accuracy_base|pct}} | {{a.UNSEEN.COT.accuracy_base|pct}} | {{a.UNSEEN.TOT.accuracy_base|pct}} | {{a.UNSEEN.GOT.accuracy_base|pct}} |
| accuracy, adversarial instances | {{a.UNSEEN.DIRECT.accuracy_adversarial|pct}} | {{a.UNSEEN.COT.accuracy_adversarial|pct}} | {{a.UNSEEN.TOT.accuracy_adversarial|pct}} | {{a.UNSEEN.GOT.accuracy_adversarial|pct}} |
| mean regret (measured outcomes) | {{a.UNSEEN.DIRECT.regret_mean|3}} | {{a.UNSEEN.COT.regret_mean|3}} | {{a.UNSEEN.TOT.regret_mean|3}} | {{a.UNSEEN.GOT.regret_mean|3}} |
| regret 95 % CI | [{{a.UNSEEN.DIRECT.regret_ci_lo|3}}, {{a.UNSEEN.DIRECT.regret_ci_hi|3}}] | [{{a.UNSEEN.COT.regret_ci_lo|3}}, {{a.UNSEEN.COT.regret_ci_hi|3}}] | [{{a.UNSEEN.TOT.regret_ci_lo|3}}, {{a.UNSEEN.TOT.regret_ci_hi|3}}] | [{{a.UNSEEN.GOT.regret_ci_lo|3}}, {{a.UNSEEN.GOT.regret_ci_hi|3}}] |
| runs with measured regret | {{a.UNSEEN.DIRECT.regret_n_measured}} | {{a.UNSEEN.COT.regret_n_measured}} | {{a.UNSEEN.TOT.regret_n_measured}} | {{a.UNSEEN.GOT.regret_n_measured}} |
| consistency across seeds | {{a.UNSEEN.DIRECT.consistency|pct}} | {{a.UNSEEN.COT.consistency|pct}} | {{a.UNSEEN.TOT.consistency|pct}} | {{a.UNSEEN.GOT.consistency|pct}} |
| mean stated confidence | {{a.UNSEEN.DIRECT.confidence_mean|pct}} | {{a.UNSEEN.COT.confidence_mean|pct}} | {{a.UNSEEN.TOT.confidence_mean|pct}} | {{a.UNSEEN.GOT.confidence_mean|pct}} |
| ECE | {{a.UNSEEN.DIRECT.ece|3}} | {{a.UNSEEN.COT.ece|3}} | {{a.UNSEEN.TOT.ece|3}} | {{a.UNSEEN.GOT.ece|3}} |
| Brier (confidence vs correct) | {{a.UNSEEN.DIRECT.brier_conf|3}} | {{a.UNSEEN.COT.brier_conf|3}} | {{a.UNSEEN.TOT.brier_conf|3}} | {{a.UNSEEN.GOT.brier_conf|3}} |
| AUROC (confidence separates right from wrong) | {{a.UNSEEN.DIRECT.auroc_conf|3}} | {{a.UNSEEN.COT.auroc_conf|3}} | {{a.UNSEEN.TOT.auroc_conf|3}} | {{a.UNSEEN.GOT.auroc_conf|3}} |
| wrong with confidence ≥ 0.9 | {{a.UNSEEN.DIRECT.overconfident_wrong_rate|pct}} | {{a.UNSEEN.COT.overconfident_wrong_rate|pct}} | {{a.UNSEEN.TOT.overconfident_wrong_rate|pct}} | {{a.UNSEEN.GOT.overconfident_wrong_rate|pct}} |
| abstained ("undetermined") | {{a.UNSEEN.DIRECT.abstention_rate|pct}} | {{a.UNSEEN.COT.abstention_rate|pct}} | {{a.UNSEEN.TOT.abstention_rate|pct}} | {{a.UNSEEN.GOT.abstention_rate|pct}} |
| uncertainty preserved where expected ({{a.UNSEEN.DIRECT.n_uncertainty_runs}} runs) | {{a.UNSEEN.DIRECT.uncertainty_preserved_rate|pct}} | {{a.UNSEEN.COT.uncertainty_preserved_rate|pct}} | {{a.UNSEEN.TOT.uncertainty_preserved_rate|pct}} | {{a.UNSEEN.GOT.uncertainty_preserved_rate|pct}} |
| conflicting evidence named | {{a.UNSEEN.DIRECT.contradiction_handled_rate|pct}} | {{a.UNSEEN.COT.contradiction_handled_rate|pct}} | {{a.UNSEEN.TOT.contradiction_handled_rate|pct}} | {{a.UNSEEN.GOT.contradiction_handled_rate|pct}} |
| key evidence cited | {{a.UNSEEN.DIRECT.evidence_utilization|pct}} | {{a.UNSEEN.COT.evidence_utilization|pct}} | {{a.UNSEEN.TOT.evidence_utilization|pct}} | {{a.UNSEEN.GOT.evidence_utilization|pct}} |
| correct but more complex than needed | {{a.UNSEEN.DIRECT.unnecessary_complexity_rate|pct}} | {{a.UNSEEN.COT.unnecessary_complexity_rate|pct}} | {{a.UNSEEN.TOT.unnecessary_complexity_rate|pct}} | {{a.UNSEEN.GOT.unnecessary_complexity_rate|pct}} |
| decision follows own structure (fidelity) | — | — | {{a.UNSEEN.TOT.fidelity_rate|pct}} | {{a.UNSEEN.GOT.fidelity_rate|pct}} |
| parse failures | {{a.UNSEEN.DIRECT.parse_failure_rate|pct}} | {{a.UNSEEN.COT.parse_failure_rate|pct}} | {{a.UNSEEN.TOT.parse_failure_rate|pct}} | {{a.UNSEEN.GOT.parse_failure_rate|pct}} |

Table A1. UNSEEN, all {{design.A.UNSEEN.instances}} instances × 3 seeds per mode. Source:
`outputs/study_a/study-a-results.csv`. Abstaining counts as wrong unless "undetermined" is in the instance's accept set.

The four modes are within {{a.h.UNSEEN.H1.DIRECT.GOT.effect_b_minus_a|pp}} pp of each other (GOT − DIRECT, the widest
gap). Every point estimate orders them DIRECT ≥ COT ≥ TOT ≥ GOT; none of these differences is distinguishable (section 11).
The modes differ in *behaviour*:
- GOT is the most cautious: lowest confidence, lowest ECE and overconfident-wrong rate, most abstentions.
- DIRECT is the most repeatable across seeds.
- ToT names conflicting evidence most often, and CoT cites key evidence most completely.
- GoT's final call departs from its own propagated ranking in about a third of runs (fidelity
  {{a.UNSEEN.GOT.fidelity_rate|pct}}).

These are descriptive.

### 10.2 Per family and per adversarial variant (exploratory)

| family | n runs | DIRECT | COT | TOT | GOT |
|---|---|---|---|---|---|
| MODEL_FAMILY | {{a.fam.UNSEEN.MODEL_FAMILY.DIRECT.n}} | {{a.fam.UNSEEN.MODEL_FAMILY.DIRECT.acc|pct}} | {{a.fam.UNSEEN.MODEL_FAMILY.COT.acc|pct}} | {{a.fam.UNSEEN.MODEL_FAMILY.TOT.acc|pct}} | {{a.fam.UNSEEN.MODEL_FAMILY.GOT.acc|pct}} |
| HPO_DEPTH | {{a.fam.UNSEEN.HPO_DEPTH.DIRECT.n}} | {{a.fam.UNSEEN.HPO_DEPTH.DIRECT.acc|pct}} | {{a.fam.UNSEEN.HPO_DEPTH.COT.acc|pct}} | {{a.fam.UNSEEN.HPO_DEPTH.TOT.acc|pct}} | {{a.fam.UNSEEN.HPO_DEPTH.GOT.acc|pct}} |
| FE_STRATEGY | {{a.fam.UNSEEN.FE_STRATEGY.DIRECT.n}} | {{a.fam.UNSEEN.FE_STRATEGY.DIRECT.acc|pct}} | {{a.fam.UNSEEN.FE_STRATEGY.COT.acc|pct}} | {{a.fam.UNSEEN.FE_STRATEGY.TOT.acc|pct}} | {{a.fam.UNSEEN.FE_STRATEGY.GOT.acc|pct}} |
| FS_STRATEGY | {{a.fam.UNSEEN.FS_STRATEGY.DIRECT.n}} | {{a.fam.UNSEEN.FS_STRATEGY.DIRECT.acc|pct}} | {{a.fam.UNSEEN.FS_STRATEGY.COT.acc|pct}} | {{a.fam.UNSEEN.FS_STRATEGY.TOT.acc|pct}} | {{a.fam.UNSEEN.FS_STRATEGY.GOT.acc|pct}} |
| IMBALANCE | {{a.fam.UNSEEN.IMBALANCE.DIRECT.n}} | {{a.fam.UNSEEN.IMBALANCE.DIRECT.acc|pct}} | {{a.fam.UNSEEN.IMBALANCE.COT.acc|pct}} | {{a.fam.UNSEEN.IMBALANCE.TOT.acc|pct}} | {{a.fam.UNSEEN.IMBALANCE.GOT.acc|pct}} |
| CALIBRATION | {{a.fam.UNSEEN.CALIBRATION.DIRECT.n}} | {{a.fam.UNSEEN.CALIBRATION.DIRECT.acc|pct}} | {{a.fam.UNSEEN.CALIBRATION.COT.acc|pct}} | {{a.fam.UNSEEN.CALIBRATION.TOT.acc|pct}} | {{a.fam.UNSEEN.CALIBRATION.GOT.acc|pct}} |
| VALIDATION | {{a.fam.UNSEEN.VALIDATION.DIRECT.n}} | {{a.fam.UNSEEN.VALIDATION.DIRECT.acc|pct}} | {{a.fam.UNSEEN.VALIDATION.COT.acc|pct}} | {{a.fam.UNSEEN.VALIDATION.TOT.acc|pct}} | {{a.fam.UNSEEN.VALIDATION.GOT.acc|pct}} |
| EXPLANATION | {{a.fam.UNSEEN.EXPLANATION.DIRECT.n}} | {{a.fam.UNSEEN.EXPLANATION.DIRECT.acc|pct}} | {{a.fam.UNSEEN.EXPLANATION.COT.acc|pct}} | {{a.fam.UNSEEN.EXPLANATION.TOT.acc|pct}} | {{a.fam.UNSEEN.EXPLANATION.GOT.acc|pct}} |
| CAUSAL_VS_PREDICTIVE (scripted) | {{a.fam.UNSEEN.CAUSAL_VS_PREDICTIVE.DIRECT.n}} | {{a.fam.UNSEEN.CAUSAL_VS_PREDICTIVE.DIRECT.acc|pct}} | {{a.fam.UNSEEN.CAUSAL_VS_PREDICTIVE.COT.acc|pct}} | {{a.fam.UNSEEN.CAUSAL_VS_PREDICTIVE.TOT.acc|pct}} | {{a.fam.UNSEEN.CAUSAL_VS_PREDICTIVE.GOT.acc|pct}} |
| TRUST_PLAN (scripted) | {{a.fam.UNSEEN.TRUST_PLAN.DIRECT.n}} | {{a.fam.UNSEEN.TRUST_PLAN.DIRECT.acc|pct}} | {{a.fam.UNSEEN.TRUST_PLAN.COT.acc|pct}} | {{a.fam.UNSEEN.TRUST_PLAN.TOT.acc|pct}} | {{a.fam.UNSEEN.TRUST_PLAN.GOT.acc|pct}} |

Table A2. Accuracy per family (base and adversarial instances together). Source: `outputs/study_a/study-a-per-family.csv`;
pairwise exact McNemar per family with Holm within family in `study-a-paired-by-family.csv` (all EXPLORATORY). The
smallest family-level p was VALIDATION COT → GOT, {{a.famtest.UNSEEN.VALIDATION.COT.GOT.discordant_a_wrong_b_right|int}}
vs {{a.famtest.UNSEEN.VALIDATION.COT.GOT.discordant_a_right_b_wrong|int}} discordant instances, exact p
{{a.famtest.UNSEEN.VALIDATION.COT.GOT.mcnemar_exact_p|p}}, Holm {{a.famtest.UNSEEN.VALIDATION.COT.GOT.holm_p|p}}.

| adversarial variant | n runs | DIRECT | COT | TOT | GOT |
|---|---|---|---|---|---|
| governance_block (policy forbids the best scorer) | {{a.adv.UNSEEN.governance_block.DIRECT.n}} | {{a.adv.UNSEEN.governance_block.DIRECT.acc|pct}} | {{a.adv.UNSEEN.governance_block.COT.acc|pct}} | {{a.adv.UNSEEN.governance_block.TOT.acc|pct}} | {{a.adv.UNSEEN.governance_block.GOT.acc|pct}} |
| incomplete_evidence (right answer: undetermined) | {{a.adv.UNSEEN.incomplete_evidence.DIRECT.n}} | {{a.adv.UNSEEN.incomplete_evidence.DIRECT.acc|pct}} | {{a.adv.UNSEEN.incomplete_evidence.COT.acc|pct}} | {{a.adv.UNSEEN.incomplete_evidence.TOT.acc|pct}} | {{a.adv.UNSEEN.incomplete_evidence.GOT.acc|pct}} |
| causal_disagreement | {{a.adv.UNSEEN.causal_disagreement.DIRECT.n}} | {{a.adv.UNSEEN.causal_disagreement.DIRECT.acc|pct}} | {{a.adv.UNSEEN.causal_disagreement.COT.acc|pct}} | {{a.adv.UNSEEN.causal_disagreement.TOT.acc|pct}} | {{a.adv.UNSEEN.causal_disagreement.GOT.acc|pct}} |
| calibration_conflict | {{a.adv.UNSEEN.calibration_conflict.DIRECT.n}} | {{a.adv.UNSEEN.calibration_conflict.DIRECT.acc|pct}} | {{a.adv.UNSEEN.calibration_conflict.COT.acc|pct}} | {{a.adv.UNSEEN.calibration_conflict.TOT.acc|pct}} | {{a.adv.UNSEEN.calibration_conflict.GOT.acc|pct}} |
| cheaper_equivalent | {{a.adv.UNSEEN.cheaper_equivalent.DIRECT.n}} | {{a.adv.UNSEEN.cheaper_equivalent.DIRECT.acc|pct}} | {{a.adv.UNSEEN.cheaper_equivalent.COT.acc|pct}} | {{a.adv.UNSEEN.cheaper_equivalent.TOT.acc|pct}} | {{a.adv.UNSEEN.cheaper_equivalent.GOT.acc|pct}} |
| data_quality_suspicious | {{a.adv.UNSEEN.data_quality_suspicious.DIRECT.n}} | {{a.adv.UNSEEN.data_quality_suspicious.DIRECT.acc|pct}} | {{a.adv.UNSEEN.data_quality_suspicious.COT.acc|pct}} | {{a.adv.UNSEEN.data_quality_suspicious.TOT.acc|pct}} | {{a.adv.UNSEEN.data_quality_suspicious.GOT.acc|pct}} |
| indistinguishable | {{a.adv.UNSEEN.indistinguishable.DIRECT.n}} | {{a.adv.UNSEEN.indistinguishable.DIRECT.acc|pct}} | {{a.adv.UNSEEN.indistinguishable.COT.acc|pct}} | {{a.adv.UNSEEN.indistinguishable.TOT.acc|pct}} | {{a.adv.UNSEEN.indistinguishable.GOT.acc|pct}} |
| variance_uncertain | {{a.adv.UNSEEN.variance_uncertain.DIRECT.n}} | {{a.adv.UNSEEN.variance_uncertain.DIRECT.acc|pct}} | {{a.adv.UNSEEN.variance_uncertain.COT.acc|pct}} | {{a.adv.UNSEEN.variance_uncertain.TOT.acc|pct}} | {{a.adv.UNSEEN.variance_uncertain.GOT.acc|pct}} |

Table A3. Accuracy per adversarial variant (3 instances × 3 seeds each). Source: `outputs/study_a/study-a-adversarial.csv`.
The governance_block row is the largest descriptive contrast in Study A (TOT {{a.adv.UNSEEN.governance_block.TOT.acc|pct}}
against {{a.adv.UNSEEN.governance_block.COT.acc|pct}} for DIRECT and COT). With 3 instances the smallest attainable exact
two-sided McNemar p is 0.25, so it cannot be a finding; it is recorded as a hypothesis (section 28).

### 10.3 Development vs unseen

| | DIRECT | COT | TOT | GOT |
|---|---|---|---|---|
| DEVELOPMENT accuracy ({{design.A.DEVELOPMENT.instances}} instances, 1 seed) | {{a.DEVELOPMENT.DIRECT.accuracy|pct}} | {{a.DEVELOPMENT.COT.accuracy|pct}} | {{a.DEVELOPMENT.TOT.accuracy|pct}} | {{a.DEVELOPMENT.GOT.accuracy|pct}} |
| UNSEEN accuracy | {{a.UNSEEN.DIRECT.accuracy|pct}} | {{a.UNSEEN.COT.accuracy|pct}} | {{a.UNSEEN.TOT.accuracy|pct}} | {{a.UNSEEN.GOT.accuracy|pct}} |

The exploratory DEVELOPMENT ordering (DIRECT = TOT > GOT > COT, journaled before the freeze) did not replicate: COT rose and
the others fell. See section 21 for the same pattern in Study B.

## 11. Study A statistics

Confirmatory tests are exactly those pre-registered in `outputs/study_a/study-a-design.md`, computed by the frozen
`study_a/analyze.py` (`confirmatory`), with Holm correction within each hypothesis family. Source:
`outputs/study_a/study-a-confirmatory.csv`. Effects are second minus first. Intervals are paired dataset-cluster bootstrap
(B = 2000). The unit for H1–H3 is the instance, scored by majority over its seeds.

| H | metric | first → second | n | effect | 95 % CI | second better | first better | raw p | Holm p |
|---|---|---|---|---|---|---|---|---|---|
| H1 | accuracy | DIRECT → COT | {{a.h.UNSEEN.H1.DIRECT.COT.n_instances}} | {{a.h.UNSEEN.H1.DIRECT.COT.effect_b_minus_a|pp}} pp | [{{a.h.UNSEEN.H1.DIRECT.COT.ci_lo|pp}}, {{a.h.UNSEEN.H1.DIRECT.COT.ci_hi|pp}}] | {{a.h.UNSEEN.H1.DIRECT.COT.discordant_b_better|int}} | {{a.h.UNSEEN.H1.DIRECT.COT.discordant_a_better|int}} | {{a.h.UNSEEN.H1.DIRECT.COT.p_raw|p}} | {{a.h.UNSEEN.H1.DIRECT.COT.p_holm|p}} |
| H1 | accuracy | DIRECT → TOT | {{a.h.UNSEEN.H1.DIRECT.TOT.n_instances}} | {{a.h.UNSEEN.H1.DIRECT.TOT.effect_b_minus_a|pp}} pp | [{{a.h.UNSEEN.H1.DIRECT.TOT.ci_lo|pp}}, {{a.h.UNSEEN.H1.DIRECT.TOT.ci_hi|pp}}] | {{a.h.UNSEEN.H1.DIRECT.TOT.discordant_b_better|int}} | {{a.h.UNSEEN.H1.DIRECT.TOT.discordant_a_better|int}} | {{a.h.UNSEEN.H1.DIRECT.TOT.p_raw|p}} | {{a.h.UNSEEN.H1.DIRECT.TOT.p_holm|p}} |
| H1 | accuracy | DIRECT → GOT | {{a.h.UNSEEN.H1.DIRECT.GOT.n_instances}} | {{a.h.UNSEEN.H1.DIRECT.GOT.effect_b_minus_a|pp}} pp | [{{a.h.UNSEEN.H1.DIRECT.GOT.ci_lo|pp}}, {{a.h.UNSEEN.H1.DIRECT.GOT.ci_hi|pp}}] | {{a.h.UNSEEN.H1.DIRECT.GOT.discordant_b_better|int}} | {{a.h.UNSEEN.H1.DIRECT.GOT.discordant_a_better|int}} | {{a.h.UNSEEN.H1.DIRECT.GOT.p_raw|p}} | {{a.h.UNSEEN.H1.DIRECT.GOT.p_holm|p}} |
| H1 | accuracy | COT → TOT | {{a.h.UNSEEN.H1.COT.TOT.n_instances}} | {{a.h.UNSEEN.H1.COT.TOT.effect_b_minus_a|pp}} pp | [{{a.h.UNSEEN.H1.COT.TOT.ci_lo|pp}}, {{a.h.UNSEEN.H1.COT.TOT.ci_hi|pp}}] | {{a.h.UNSEEN.H1.COT.TOT.discordant_b_better|int}} | {{a.h.UNSEEN.H1.COT.TOT.discordant_a_better|int}} | {{a.h.UNSEEN.H1.COT.TOT.p_raw|p}} | {{a.h.UNSEEN.H1.COT.TOT.p_holm|p}} |
| H1 | accuracy | COT → GOT | {{a.h.UNSEEN.H1.COT.GOT.n_instances}} | {{a.h.UNSEEN.H1.COT.GOT.effect_b_minus_a|pp}} pp | [{{a.h.UNSEEN.H1.COT.GOT.ci_lo|pp}}, {{a.h.UNSEEN.H1.COT.GOT.ci_hi|pp}}] | {{a.h.UNSEEN.H1.COT.GOT.discordant_b_better|int}} | {{a.h.UNSEEN.H1.COT.GOT.discordant_a_better|int}} | {{a.h.UNSEEN.H1.COT.GOT.p_raw|p}} | {{a.h.UNSEEN.H1.COT.GOT.p_holm|p}} |
| H1 | accuracy | TOT → GOT | {{a.h.UNSEEN.H1.TOT.GOT.n_instances}} | {{a.h.UNSEEN.H1.TOT.GOT.effect_b_minus_a|pp}} pp | [{{a.h.UNSEEN.H1.TOT.GOT.ci_lo|pp}}, {{a.h.UNSEEN.H1.TOT.GOT.ci_hi|pp}}] | {{a.h.UNSEEN.H1.TOT.GOT.discordant_b_better|int}} | {{a.h.UNSEEN.H1.TOT.GOT.discordant_a_better|int}} | {{a.h.UNSEEN.H1.TOT.GOT.p_raw|p}} | {{a.h.UNSEEN.H1.TOT.GOT.p_holm|p}} |
| H2 | adversarial accuracy | COT → TOT | {{a.h.UNSEEN.H2.COT.TOT.n_instances}} | {{a.h.UNSEEN.H2.COT.TOT.effect_b_minus_a|pp}} pp | [{{a.h.UNSEEN.H2.COT.TOT.ci_lo|pp}}, {{a.h.UNSEEN.H2.COT.TOT.ci_hi|pp}}] | {{a.h.UNSEEN.H2.COT.TOT.discordant_b_better|int}} | {{a.h.UNSEEN.H2.COT.TOT.discordant_a_better|int}} | {{a.h.UNSEEN.H2.COT.TOT.p_raw|p}} | {{a.h.UNSEEN.H2.COT.TOT.p_holm|p}} |
| H2 | adversarial accuracy | COT → GOT | {{a.h.UNSEEN.H2.COT.GOT.n_instances}} | {{a.h.UNSEEN.H2.COT.GOT.effect_b_minus_a|pp}} pp | [{{a.h.UNSEEN.H2.COT.GOT.ci_lo|pp}}, {{a.h.UNSEEN.H2.COT.GOT.ci_hi|pp}}] | {{a.h.UNSEEN.H2.COT.GOT.discordant_b_better|int}} | {{a.h.UNSEEN.H2.COT.GOT.discordant_a_better|int}} | {{a.h.UNSEEN.H2.COT.GOT.p_raw|p}} | {{a.h.UNSEEN.H2.COT.GOT.p_holm|p}} |
| H3 | uncertainty preserved | COT → TOT | {{a.h.UNSEEN.H3.COT.TOT.n_instances}} | {{a.h.UNSEEN.H3.COT.TOT.effect_b_minus_a|pp}} pp | [{{a.h.UNSEEN.H3.COT.TOT.ci_lo|pp}}, {{a.h.UNSEEN.H3.COT.TOT.ci_hi|pp}}] | {{a.h.UNSEEN.H3.COT.TOT.discordant_b_better|int}} | {{a.h.UNSEEN.H3.COT.TOT.discordant_a_better|int}} | {{a.h.UNSEEN.H3.COT.TOT.p_raw|p}} | {{a.h.UNSEEN.H3.COT.TOT.p_holm|p}} |
| H3 | uncertainty preserved | COT → GOT | {{a.h.UNSEEN.H3.COT.GOT.n_instances}} | {{a.h.UNSEEN.H3.COT.GOT.effect_b_minus_a|pp}} pp | [{{a.h.UNSEEN.H3.COT.GOT.ci_lo|pp}}, {{a.h.UNSEEN.H3.COT.GOT.ci_hi|pp}}] | {{a.h.UNSEEN.H3.COT.GOT.discordant_b_better|int}} | {{a.h.UNSEEN.H3.COT.GOT.discordant_a_better|int}} | {{a.h.UNSEEN.H3.COT.GOT.p_raw|p}} | {{a.h.UNSEEN.H3.COT.GOT.p_holm|p}} |
| H3 | uncertainty preserved | DIRECT → TOT | {{a.h.UNSEEN.H3.DIRECT.TOT.n_instances}} | {{a.h.UNSEEN.H3.DIRECT.TOT.effect_b_minus_a|pp}} pp | [{{a.h.UNSEEN.H3.DIRECT.TOT.ci_lo|pp}}, {{a.h.UNSEEN.H3.DIRECT.TOT.ci_hi|pp}}] | {{a.h.UNSEEN.H3.DIRECT.TOT.discordant_b_better|int}} | {{a.h.UNSEEN.H3.DIRECT.TOT.discordant_a_better|int}} | {{a.h.UNSEEN.H3.DIRECT.TOT.p_raw|p}} | {{a.h.UNSEEN.H3.DIRECT.TOT.p_holm|p}} |
| H3 | uncertainty preserved | DIRECT → GOT | {{a.h.UNSEEN.H3.DIRECT.GOT.n_instances}} | {{a.h.UNSEEN.H3.DIRECT.GOT.effect_b_minus_a|pp}} pp | [{{a.h.UNSEEN.H3.DIRECT.GOT.ci_lo|pp}}, {{a.h.UNSEEN.H3.DIRECT.GOT.ci_hi|pp}}] | {{a.h.UNSEEN.H3.DIRECT.GOT.discordant_b_better|int}} | {{a.h.UNSEEN.H3.DIRECT.GOT.discordant_a_better|int}} | {{a.h.UNSEEN.H3.DIRECT.GOT.p_raw|p}} | {{a.h.UNSEEN.H3.DIRECT.GOT.p_holm|p}} |
| H4 | accuracy / 1k output tokens | DIRECT → TOT | {{a.h.UNSEEN.H4.DIRECT.TOT.n_instances}} | {{a.h.UNSEEN.H4.DIRECT.TOT.effect_b_minus_a|2}} | [{{a.h.UNSEEN.H4.DIRECT.TOT.ci_lo|2}}, {{a.h.UNSEEN.H4.DIRECT.TOT.ci_hi|2}}] | — | — | {{a.h.UNSEEN.H4.DIRECT.TOT.p_raw|p}} | {{a.h.UNSEEN.H4.DIRECT.TOT.p_holm|p}} |
| H4 | accuracy / 1k output tokens | DIRECT → GOT | {{a.h.UNSEEN.H4.DIRECT.GOT.n_instances}} | {{a.h.UNSEEN.H4.DIRECT.GOT.effect_b_minus_a|2}} | [{{a.h.UNSEEN.H4.DIRECT.GOT.ci_lo|2}}, {{a.h.UNSEEN.H4.DIRECT.GOT.ci_hi|2}}] | — | — | {{a.h.UNSEEN.H4.DIRECT.GOT.p_raw|p}} | {{a.h.UNSEEN.H4.DIRECT.GOT.p_holm|p}} |
| H4 | accuracy / 1k output tokens | COT → TOT | {{a.h.UNSEEN.H4.COT.TOT.n_instances}} | {{a.h.UNSEEN.H4.COT.TOT.effect_b_minus_a|2}} | [{{a.h.UNSEEN.H4.COT.TOT.ci_lo|2}}, {{a.h.UNSEEN.H4.COT.TOT.ci_hi|2}}] | — | — | {{a.h.UNSEEN.H4.COT.TOT.p_raw|p}} | {{a.h.UNSEEN.H4.COT.TOT.p_holm|p}} |
| H4 | accuracy / 1k output tokens | COT → GOT | {{a.h.UNSEEN.H4.COT.GOT.n_instances}} | {{a.h.UNSEEN.H4.COT.GOT.effect_b_minus_a|2}} | [{{a.h.UNSEEN.H4.COT.GOT.ci_lo|2}}, {{a.h.UNSEEN.H4.COT.GOT.ci_hi|2}}] | — | — | {{a.h.UNSEEN.H4.COT.GOT.p_raw|p}} | {{a.h.UNSEEN.H4.COT.GOT.p_holm|p}} |

Table A4. Confirmatory tests, UNSEEN. H4's p is a two-sided bootstrap p with B = 2000: "< 0.001" means no bootstrap
replicate crossed zero (p < 1/2000).

**Verdicts.**
- **H1:** we did not detect a statistically distinguishable accuracy difference between any pair of the four modes.
- **H2 and H3:** we did not detect the predicted advantages.
- **H4:** supported. DIRECT and COT deliver more accuracy per thousand output tokens than TOT and GOT in all four contrasts.

**Cluster bootstrap vs exact test.** For H2 COT → TOT and two of the H3 contrasts (COT → TOT, COT → GOT), the dataset-cluster interval excludes
zero while the exact test is far from significant. Examples:
- H3 COT → TOT: {{a.h.UNSEEN.H3.COT.TOT.discordant_b_better|int}} vs {{a.h.UNSEEN.H3.COT.TOT.discordant_a_better|int}}
  discordant instances out of {{a.h.UNSEEN.H3.COT.TOT.n_instances}}.
- H2 COT → TOT: {{a.h.UNSEEN.H2.COT.TOT.discordant_b_better|int}} vs {{a.h.UNSEEN.H2.COT.TOT.discordant_a_better|int}}.

The uncertainty and adversarial subsets cover few instances per dataset, so the percentile bootstrap over
{{design.A.UNSEEN.datasets}} clusters is degenerate (many resamples contain the same handful of discordant pairs). The
pre-registered decision rule is the exact test; the intervals are reported but not used for verdicts. This was listed as a
threat before the run (section 23).

**Regret (exploratory, not pre-registered).** Paired regret differences on instances with a measured outcome
(`study-a-paired-regret.csv`):
- GOT − DIRECT: {{a.regret.UNSEEN.DIRECT.GOT.diff_b_minus_a|3}}, CI [{{a.regret.UNSEEN.DIRECT.GOT.ci_lo|3}},
  {{a.regret.UNSEEN.DIRECT.GOT.ci_hi|3}}], n = {{a.regret.UNSEEN.DIRECT.GOT.n_instances}}. This interval just excludes zero.
- TOT − DIRECT: {{a.regret.UNSEEN.DIRECT.TOT.diff_b_minus_a|3}}, CI [{{a.regret.UNSEEN.DIRECT.TOT.ci_lo|3}},
  {{a.regret.UNSEEN.DIRECT.TOT.ci_hi|3}}].
- COT − DIRECT: {{a.regret.UNSEEN.DIRECT.COT.diff_b_minus_a|3}}, CI [{{a.regret.UNSEEN.DIRECT.COT.ci_lo|3}},
  {{a.regret.UNSEEN.DIRECT.COT.ci_hi|3}}].

No regret contrast favours a structured mode.

## 12. Study A efficiency

| per decision | DIRECT | COT | TOT | GOT |
|---|---|---|---|---|
| model calls | {{a.UNSEEN.DIRECT.calls_mean|2}} | {{a.UNSEEN.COT.calls_mean|2}} | {{a.UNSEEN.TOT.calls_mean|2}} | {{a.UNSEEN.GOT.calls_mean|2}} |
| prompt tokens | {{a.UNSEEN.DIRECT.prompt_tokens_mean|int}} | {{a.UNSEEN.COT.prompt_tokens_mean|int}} | {{a.UNSEEN.TOT.prompt_tokens_mean|int}} | {{a.UNSEEN.GOT.prompt_tokens_mean|int}} |
| output tokens | {{a.UNSEEN.DIRECT.output_tokens_mean|int}} | {{a.UNSEEN.COT.output_tokens_mean|int}} | {{a.UNSEEN.TOT.output_tokens_mean|int}} | {{a.UNSEEN.GOT.output_tokens_mean|int}} |
| total tokens | {{a.UNSEEN.DIRECT.total_tokens_mean|int}} | {{a.UNSEEN.COT.total_tokens_mean|int}} | {{a.UNSEEN.TOT.total_tokens_mean|int}} | {{a.UNSEEN.GOT.total_tokens_mean|int}} |
| output tokens × DIRECT | {{ax.UNSEEN.DIRECT.output_tokens_mean_vs_direct|2}} | {{ax.UNSEEN.COT.output_tokens_mean_vs_direct|2}} | {{ax.UNSEEN.TOT.output_tokens_mean_vs_direct|2}} | {{ax.UNSEEN.GOT.output_tokens_mean_vs_direct|2}} |
| server compute, s (audited mean) | {{lat.A.UNSEEN.DIRECT.compute_mean|1}} | {{lat.A.UNSEEN.COT.compute_mean|1}} | {{lat.A.UNSEEN.TOT.compute_mean|1}} | {{lat.A.UNSEEN.GOT.compute_mean|1}} |
| server compute, s (audited median) | {{lat.A.UNSEEN.DIRECT.compute_median|1}} | {{lat.A.UNSEEN.COT.compute_median|1}} | {{lat.A.UNSEEN.TOT.compute_median|1}} | {{lat.A.UNSEEN.GOT.compute_median|1}} |
| runs with known compute | {{lat.A.UNSEEN.DIRECT.n_known}} / {{lat.A.UNSEEN.DIRECT.n_runs}} | {{lat.A.UNSEEN.COT.n_known}} / {{lat.A.UNSEEN.COT.n_runs}} | {{lat.A.UNSEEN.TOT.n_known}} / {{lat.A.UNSEEN.TOT.n_runs}} | {{lat.A.UNSEEN.GOT.n_known}} / {{lat.A.UNSEEN.GOT.n_runs}} |
| compute × DIRECT | {{ax.UNSEEN.DIRECT.compute_vs_direct|2}} | {{ax.UNSEEN.COT.compute_vs_direct|2}} | {{ax.UNSEEN.TOT.compute_vs_direct|2}} | {{ax.UNSEEN.GOT.compute_vs_direct|2}} |
| accuracy per 1k output tokens | {{a.UNSEEN.DIRECT.accuracy_per_1k_output_tokens|2}} | {{a.UNSEEN.COT.accuracy_per_1k_output_tokens|2}} | {{a.UNSEEN.TOT.accuracy_per_1k_output_tokens|2}} | {{a.UNSEEN.GOT.accuracy_per_1k_output_tokens|2}} |
| cost | NOT_APPLICABLE_LOCAL | NOT_APPLICABLE_LOCAL | NOT_APPLICABLE_LOCAL | NOT_APPLICABLE_LOCAL |

Table A5. Sources: tokens and calls from `study-a-results.csv` (ACTUAL, server-counted); compute from
`outputs/study_a/latency-audit.csv` (server prefill + decode, runs with any contaminated call excluded, section 24.1). The
`latency_s_*` and `accuracy_per_minute` columns of `study-a-results.csv` include contaminated calls and are not quoted.
Energy is UNKNOWN. Total UNSEEN volume: {{design.A.UNSEEN.prompt_tokens|int}} prompt and
{{design.A.UNSEEN.output_tokens|int}} output tokens, {{design.A.UNSEEN.compute_hours|2}} h of server compute.

**Topology complexity actually built** (`study-a-topology-stats.csv`, mean per decision):
- **TOT:** {{a.topo.UNSEEN.TOT.topo_branches|2}} branches, {{a.topo.UNSEEN.TOT.topo_leaves|2}} leaves,
  {{a.topo.UNSEEN.TOT.topo_pruned|2}} pruned, {{a.topo.UNSEEN.TOT.topo_duplicate_proposals|2}} duplicate proposals,
  depth {{a.topo.UNSEEN.TOT.topo_depth|0}}.
- **GOT:** {{a.topo.UNSEEN.GOT.topo_nodes|2}} nodes, of which {{a.topo.UNSEEN.GOT.topo_claim_nodes|2}} claims and
  {{a.topo.UNSEEN.GOT.topo_candidate_nodes|2}} candidates; {{a.topo.UNSEEN.GOT.topo_edges|2}} edges;
  {{a.topo.UNSEEN.GOT.topo_claim_conflict_edges|2}} claim-conflict edges; {{a.topo.UNSEEN.GOT.topo_reused_claims|2}} reused
  claims; maximum claim fan-out {{a.topo.UNSEEN.GOT.topo_max_claim_fanout|2}}; {{a.topo.UNSEEN.GOT.topo_merged_nodes|2}}
  merged nodes.

The structures are real: GoT builds DAGs with shared claims and conflicts, not relabelled trees. The structure did not convert
into accuracy, and it was not always followed (fidelity TOT {{a.UNSEEN.TOT.fidelity_rate|pct}}, GOT
{{a.UNSEEN.GOT.fidelity_rate|pct}}).

## 13. Study A failures

- **Parse failures:** {{design.A.UNSEEN.parse_failed_runs}} UNSEEN run, the single truncated call (GOT edges,
  `card_fraud_synth::TRUST_PLAN`, seed 1, 1200/1200 tokens). Counted as wrong, as pre-registered.
- **Hard families for every mode:** TRUST_PLAN ({{a.fam.UNSEEN.TRUST_PLAN.GOT.acc|pct}}–{{a.fam.UNSEEN.TRUST_PLAN.DIRECT.acc|pct}})
  and HPO_DEPTH ({{a.fam.UNSEEN.HPO_DEPTH.GOT.acc|pct}}–{{a.fam.UNSEEN.HPO_DEPTH.TOT.acc|pct}}).
- **Incomplete evidence:** the right answer was "undetermined". No mode exceeded
  {{a.adv.UNSEEN.incomplete_evidence.DIRECT.acc|pct}}, and TOT reached {{a.adv.UNSEEN.incomplete_evidence.TOT.acc|pct}}.
- **Policy override:** with a policy forbidding the best scorer, DIRECT and COT were wrong in every run.
- **Causal vs predictive conflict:** DIRECT chose the lever backed by the randomized pilot in
  {{a.adv.UNSEEN.causal_disagreement.DIRECT.acc|pct}} of runs; COT, TOT and GOT in {{a.adv.UNSEEN.causal_disagreement.COT.acc|pct}},
  {{a.adv.UNSEEN.causal_disagreement.TOT.acc|pct}} and {{a.adv.UNSEEN.causal_disagreement.GOT.acc|pct}}. This is descriptive, 3 instances.
- **Structure not followed:** GOT's final call overrode its own propagated ranking in about a third of runs.
- **Seed instability:** TOT's decisions agreed across seeds only {{a.UNSEEN.TOT.consistency|pct}} of the time.
