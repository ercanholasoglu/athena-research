## 18. Study B statistics

Confirmatory family (pre-registered, `outputs/study_b/study-b-design.md`): UNSEEN, trapped grid, each condition vs A_RAW,
pairs = (dataset, seed), n = 16 pairs. Wilcoxon signed-rank
(raw p), exact sign test, Holm across the 4 contrasts within each metric (corrected p); difference = condition − A_RAW with a
95 % dataset-cluster bootstrap interval.

| metric | condition | diff | 95 % CI | better / worse pairs | sign p | Wilcoxon p | Holm p |
|---|---|---|---|---|---|---|---|
| core semantic accuracy (H5) | C_DICT | +4.5 pp | [0.0, +9.8] | 8 / 3 | 0.227 | 0.297 | 0.335 |
| | D_RULES | +8.9 pp | [+1.8, +15.2] | 11 / 2 | 0.022 | 0.032 | 0.096 |
| | E_FULL | +10.7 pp | [+6.2, +15.2] | 13 / 2 | 0.007 | 0.012 | 0.050 |
| | B_SELF | +3.6 pp | [−2.7, +10.7] | 5 / 2 | 0.453 | 0.168 | 0.335 |
| all traps blocked (H6) | C_DICT | +37.5 pp | [+6.2, +68.8] | 7 / 1 | 0.070 | 0.034 | 0.102 |
| | D_RULES | +50.0 pp | [+12.5, +87.5] | 9 / 1 | 0.021 | 0.011 | 0.046 |
| | E_FULL | +12.5 pp | [−25.0, +56.2] | 5 / 3 | 0.727 | 0.480 | 0.480 |
| | B_SELF | +31.2 pp | [−6.2, +68.8] | 6 / 1 | 0.125 | 0.059 | 0.118 |
| leak recall (H6) | C_DICT | +22.9 pp | [+4.2, +40.6] | 8 / 1 | 0.039 | 0.021 | 0.057 |
| | D_RULES | +26.0 pp | [+4.2, +43.8] | 9 / 1 | 0.021 | 0.013 | 0.050 |
| | E_FULL | +9.4 pp | [−9.4, +28.1] | 6 / 3 | 0.508 | 0.289 | 0.289 |
| | B_SELF | +18.8 pp | [+6.2, +34.4] | 7 / 1 | 0.070 | 0.019 | 0.057 |
| candidate accuracy (H7) | C_DICT | +9.4 pp | [0.0, +19.8] | 6 / 2 | 0.289 | 0.139 | 0.556 |
| | D_RULES | +13.5 pp | [+4.2, +22.9] | 7 / 3 | 0.344 | 0.199 | 0.598 |
| | E_FULL | +5.7 pp | [−4.2, +16.7] | 6 / 5 | 1.000 | 0.472 | 0.598 |
| valid & leak-free proposal share (H7) | C_DICT | +3.2 pp | [−1.8, +8.3] | 5 / 2 | 0.453 | 0.306 | 1.000 |
| | D_RULES | −2.9 pp | [−10.5, +6.8] | 4 / 5 | 1.000 | 0.373 | 1.000 |
| | E_FULL | +4.3 pp | [−3.8, +12.2] | 6 / 2 | 0.289 | 0.260 | 1.000 |
| deployment collapse (H8) | C_DICT | −37.5 pp | [−75.0, 0.0] | 7 / 1 | 0.070 | 0.034 | 0.136 |
| | D_RULES | −37.5 pp | [−75.0, 0.0] | 7 / 1 | 0.070 | 0.034 | 0.136 |
| | E_FULL | −18.8 pp | [−56.2, +18.8] | 5 / 2 | 0.453 | 0.257 | 0.257 |
| gap to truth-clean model (H8) | C_DICT | -0.043 | [-0.125, 0.005] | 7 / 6 | 1.000 | 0.278 | 1.000 |
| | D_RULES | -0.032 | [-0.124, 0.029] | 7 / 8 | 1.000 | 0.495 | 1.000 |
| | E_FULL | -0.019 | [-0.064, 0.012] | 5 / 8 | 0.581 | 0.916 | 1.000 |

Table B5. Confirmatory tests. "Better / worse pairs" counts pairs where the condition is better / worse than A_RAW (for
collapse and gap, lower is better). B_SELF rows for H7/H8 are in `study-b-paired-tests.csv`. Source:
`outputs/study_b/study-b-paired-tests.csv`.

**Verdicts at Holm 0.05.**

* H5 core semantic accuracy: supported for E_FULL only (Holm p 0.0495);
  D_RULES's interval excludes zero but its Holm p is 0.096.
* H6 leakage: supported for D_RULES on all traps blocked (Holm p 0.046)
  not on leak recall, where Holm p is 0.0502, just above the threshold. B_SELF and C_DICT
  have raw p below 0.05 and Holm p above it. **E_FULL is not distinguishable from A_RAW** on either leakage metric.
* H7 candidate judgements and valid proposals: we did not detect a statistically distinguishable difference.
* H8 deployment collapse: C_DICT and D_RULES collapsed in fewer pairs (7
  fewer vs 1 more), raw Wilcoxon p 0.034,
  Holm p 0.136: not significant after correction. Median gap to the
  truth-clean model: no detectable difference.

**Fragility (exploratory sensitivity, post-freeze; section 24).** Excluding `coil_caravan`, where two UNSEEN calls hit
their token caps, changes no sign. It changes three Holm verdicts: E_FULL core accuracy
(0.0495 → 0.128),
D_RULES leak recall (0.0502 → 0.016) and
D_RULES deployment collapse (0.136 → 0.033).
The directions are stable; which individual contrasts clear 0.05 is not, at 16
pairs from 8 datasets. Source: `outputs/study_b/study-b-sensitivity.csv`.
