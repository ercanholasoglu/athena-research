## 10. Study A results

All numbers in this section are UNSEEN unless labelled otherwise: 9 datasets
(iranian_churn, taiwan_default, coil_caravan, diabetes_readmission, card_fraud_synth, online_shoppers, thyroid_sick, image_segment, hillstrom_email), 101 decision instances (24
adversarial) in 10 families, seeds 1–3: 1,212 runs and
3,633 model calls, 1 failed call
(1 parse-failed run). Brackets are 95 % dataset-cluster bootstrap intervals.

### 10.1 Aggregate quality

| | DIRECT | COT | TOT | GOT |
|---|---|---|---|---|
| runs | 303 | 303 | 303 | 303 |
| accuracy | 77.6% | 77.2% | 75.9% | 74.6% |
| 95 % CI | [68.6%, 86.8%] | [71.8%, 82.7%] | [70.5%, 81.3%] | [70.4%, 79.4%] |
| accuracy, base instances | 78.4% | 80.1% | 75.8% | 76.2% |
| accuracy, adversarial instances | 75.0% | 68.1% | 76.4% | 69.4% |
| mean regret (measured outcomes) | 0.107 | 0.130 | 0.132 | 0.142 |
| regret 95 % CI | [0.036, 0.188] | [0.071, 0.196] | [0.080, 0.181] | [0.074, 0.199] |
| runs with measured regret | 176 | 179 | 183 | 170 |
| consistency across seeds | 97.4% | 72.3% | 53.1% | 69.3% |
| mean stated confidence | 85.7% | 88.0% | 84.6% | 75.7% |
| ECE | 0.097 | 0.153 | 0.114 | 0.057 |
| Brier (confidence vs correct) | 0.183 | 0.204 | 0.196 | 0.177 |
| AUROC (confidence separates right from wrong) | 0.528 | 0.483 | 0.507 | 0.621 |
| wrong with confidence ≥ 0.9 | 11.2% | 17.5% | 11.6% | 3.3% |
| abstained ("undetermined") | 9.2% | 5.0% | 2.0% | 14.9% |
| uncertainty preserved where expected (27 runs) | 55.6% | 48.1% | 18.5% | 66.7% |
| conflicting evidence named | 25.0% | 2.8% | 38.9% | 16.7% |
| key evidence cited | 63.1% | 80.6% | 54.0% | 74.1% |
| correct but more complex than needed | 22.6% | 25.2% | 32.2% | 17.3% |
| decision follows own structure (fidelity) | — | — | 78.9% | 66.2% |
| parse failures | 0.0% | 0.0% | 0.0% | 0.3% |

Table A1. UNSEEN, all 101 instances × 3 seeds per mode. Source:
`outputs/study_a/study-a-results.csv`. Abstaining counts as wrong unless "undetermined" is in the instance's accept set.

The four modes are within −3.0 pp of each other (GOT − DIRECT, the widest
gap). Every point estimate orders them DIRECT ≥ COT ≥ TOT ≥ GOT; none of these differences is distinguishable (section 11).
The modes differ in *behaviour*:
- GOT is the most cautious: lowest confidence, lowest ECE and overconfident-wrong rate, most abstentions.
- DIRECT is the most repeatable across seeds.
- ToT names conflicting evidence most often, and CoT cites key evidence most completely.
- GoT's final call departs from its own propagated ranking in about a third of runs (fidelity
  66.2%).

These are descriptive.

### 10.2 Per family and per adversarial variant (exploratory)

| family | n runs | DIRECT | COT | TOT | GOT |
|---|---|---|---|---|---|
| MODEL_FAMILY | 87 | 75.9% | 75.9% | 82.8% | 72.4% |
| HPO_DEPTH | 24 | 62.5% | 62.5% | 62.5% | 50.0% |
| FE_STRATEGY | 24 | 75.0% | 79.2% | 91.7% | 79.2% |
| FS_STRATEGY | 24 | 100.0% | 95.8% | 91.7% | 100.0% |
| IMBALANCE | 21 | 100.0% | 90.5% | 95.2% | 90.5% |
| CALIBRATION | 21 | 100.0% | 95.2% | 95.2% | 90.5% |
| VALIDATION | 24 | 50.0% | 62.5% | 58.3% | 87.5% |
| EXPLANATION | 24 | 91.7% | 95.8% | 62.5% | 100.0% |
| CAUSAL_VS_PREDICTIVE (scripted) | 30 | 80.0% | 80.0% | 70.0% | 63.3% |
| TRUST_PLAN (scripted) | 24 | 50.0% | 41.7% | 37.5% | 25.0% |

Table A2. Accuracy per family (base and adversarial instances together). Source: `outputs/study_a/study-a-per-family.csv`;
pairwise exact McNemar per family with Holm within family in `study-a-paired-by-family.csv` (all EXPLORATORY). The
smallest family-level p was VALIDATION COT → GOT, 4
vs 0 discordant instances, exact p
0.125, Holm 1.000.

| adversarial variant | n runs | DIRECT | COT | TOT | GOT |
|---|---|---|---|---|---|
| governance_block (policy forbids the best scorer) | 9 | 0.0% | 0.0% | 77.8% | 11.1% |
| incomplete_evidence (right answer: undetermined) | 9 | 33.3% | 22.2% | 0.0% | 22.2% |
| causal_disagreement | 9 | 100.0% | 44.4% | 44.4% | 44.4% |
| calibration_conflict | 9 | 66.7% | 77.8% | 100.0% | 88.9% |
| cheaper_equivalent | 9 | 100.0% | 100.0% | 88.9% | 88.9% |
| data_quality_suspicious | 9 | 100.0% | 100.0% | 100.0% | 100.0% |
| indistinguishable | 9 | 100.0% | 100.0% | 100.0% | 100.0% |
| variance_uncertain | 9 | 100.0% | 100.0% | 100.0% | 100.0% |

Table A3. Accuracy per adversarial variant (3 instances × 3 seeds each). Source: `outputs/study_a/study-a-adversarial.csv`.
The governance_block row is the largest descriptive contrast in Study A (TOT 77.8%
against 0.0% for DIRECT and COT). With 3 instances the smallest attainable exact
two-sided McNemar p is 0.25, so it cannot be a finding; it is recorded as a hypothesis (section 28).

### 10.3 Development vs unseen

| | DIRECT | COT | TOT | GOT |
|---|---|---|---|---|
| DEVELOPMENT accuracy (69 instances, 1 seed) | 84.1% | 75.4% | 84.1% | 81.2% |
| UNSEEN accuracy | 77.6% | 77.2% | 75.9% | 74.6% |

The exploratory DEVELOPMENT ordering (DIRECT = TOT > GOT > COT, journaled before the freeze) did not replicate: COT rose and
the others fell. See section 21 for the same pattern in Study B.

## 12. Study A efficiency

| per decision | DIRECT | COT | TOT | GOT |
|---|---|---|---|---|
| model calls | 1.00 | 1.00 | 5.00 | 4.99 |
| prompt tokens | 668 | 730 | 3,690 | 4,351 |
| output tokens | 65 | 298 | 655 | 911 |
| total tokens | 733 | 1,028 | 4,345 | 5,262 |
| output tokens × DIRECT | 1.00 | 4.61 | 10.15 | 14.11 |
| server compute, s (audited mean) | 3.7 | 14.2 | 32.2 | 44.3 |
| server compute, s (audited median) | 3.2 | 13.8 | 31.6 | 43.3 |
| runs with known compute | 300 / 303 | 300 / 303 | 299 / 303 | 299 / 303 |
| compute × DIRECT | 1.00 | 3.88 | 8.81 | 12.10 |
| accuracy per 1k output tokens | 12.01 | 2.59 | 1.16 | 0.82 |
| cost | NOT_APPLICABLE_LOCAL | NOT_APPLICABLE_LOCAL | NOT_APPLICABLE_LOCAL | NOT_APPLICABLE_LOCAL |

Table A5. Sources: tokens and calls from `study-a-results.csv` (ACTUAL, server-counted); compute from
`outputs/study_a/latency-audit.csv` (server prefill + decode, runs with any contaminated call excluded, section 24.1). The
`latency_s_*` and `accuracy_per_minute` columns of `study-a-results.csv` include contaminated calls and are not quoted.
Energy is UNKNOWN. Total UNSEEN volume: 2,859,918 prompt and
584,342 output tokens, 9.63 h of server compute.

**Topology complexity actually built** (`study-a-topology-stats.csv`, mean per decision):
- **TOT:** 3.00 branches, 5.99 leaves,
  1.08 pruned, 0.00 duplicate proposals,
  depth 2.
- **GOT:** 10.84 nodes, of which 6.81 claims and
  3.00 candidates; 12.42 edges;
  1.58 claim-conflict edges; 2.79 reused
  claims; maximum claim fan-out 2.42; 0.03
  merged nodes.

The structures are real: GoT builds DAGs with shared claims and conflicts, not relabelled trees. The structure did not convert
into accuracy, and it was not always followed (fidelity TOT 78.9%, GOT
66.2%).
