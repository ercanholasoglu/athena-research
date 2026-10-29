## 11. Study A statistics

Confirmatory tests are exactly those pre-registered in `outputs/study_a/study-a-design.md`, computed by the frozen
`study_a/analyze.py` (`confirmatory`), with Holm correction within each hypothesis family. Source:
`outputs/study_a/study-a-confirmatory.csv`. Effects are second minus first. Intervals are paired dataset-cluster bootstrap
(B = 2000). The unit for H1–H3 is the instance, scored by majority over its seeds.

| H | metric | first → second | n | effect | 95 % CI | second better | first better | raw p | Holm p |
|---|---|---|---|---|---|---|---|---|---|
| H1 | accuracy | DIRECT → COT | 101 | −0.3 pp | [−5.0, +3.6] | 5 | 5 | 1.000 | 1.000 |
| H1 | accuracy | DIRECT → TOT | 101 | −1.7 pp | [−8.7, +5.6] | 9 | 12 | 0.664 | 1.000 |
| H1 | accuracy | DIRECT → GOT | 101 | −3.0 pp | [−9.1, +2.6] | 6 | 9 | 0.607 | 1.000 |
| H1 | accuracy | COT → TOT | 101 | −1.3 pp | [−6.8, +4.0] | 9 | 12 | 0.664 | 1.000 |
| H1 | accuracy | COT → GOT | 101 | −2.6 pp | [−6.1, 0.0] | 9 | 12 | 0.664 | 1.000 |
| H1 | accuracy | TOT → GOT | 101 | −1.3 pp | [−5.8, +3.0] | 11 | 11 | 1.000 | 1.000 |
| H2 | adversarial accuracy | COT → TOT | 24 | +8.3 pp | [+4.2, +12.5] | 5 | 2 | 0.453 | 0.906 |
| H2 | adversarial accuracy | COT → GOT | 24 | +1.4 pp | [0.0, +4.2] | 2 | 1 | 1.000 | 1.000 |
| H3 | uncertainty preserved | COT → TOT | 9 | −29.6 pp | [−44.4, −11.1] | 0 | 2 | 0.500 | 1.000 |
| H3 | uncertainty preserved | COT → GOT | 9 | +18.5 pp | [+11.1, +22.2] | 3 | 0 | 0.250 | 1.000 |
| H3 | uncertainty preserved | DIRECT → TOT | 9 | −37.0 pp | [−77.8, +22.2] | 1 | 4 | 0.375 | 1.000 |
| H3 | uncertainty preserved | DIRECT → GOT | 9 | +11.1 pp | [−22.2, +55.6] | 2 | 0 | 0.500 | 1.000 |
| H4 | accuracy / 1k output tokens | DIRECT → TOT | 101 | -10.85 | [-12.27, -9.61] | — | — | < 0.001 | < 0.001 |
| H4 | accuracy / 1k output tokens | DIRECT → GOT | 101 | -11.20 | [-12.65, -9.90] | — | — | < 0.001 | < 0.001 |
| H4 | accuracy / 1k output tokens | COT → TOT | 101 | -1.43 | [-1.59, -1.27] | — | — | < 0.001 | < 0.001 |
| H4 | accuracy / 1k output tokens | COT → GOT | 101 | -1.77 | [-1.92, -1.63] | — | — | < 0.001 | < 0.001 |

Table A4. Confirmatory tests, UNSEEN. H4's p is a two-sided bootstrap p with B = 2000: "< 0.001" means no bootstrap
replicate crossed zero (p < 1/2000).

**Verdicts.**
- **H1:** we did not detect a statistically distinguishable accuracy difference between any pair of the four modes.
- **H2 and H3:** we did not detect the predicted advantages.
- **H4:** supported. DIRECT and COT deliver more accuracy per thousand output tokens than TOT and GOT in all four contrasts.

**Cluster bootstrap vs exact test.** For H2 COT → TOT and two of the H3 contrasts (COT → TOT, COT → GOT), the dataset-cluster interval excludes
zero while the exact test is far from significant. Examples:
- H3 COT → TOT: 0 vs 2
  discordant instances out of 9.
- H2 COT → TOT: 5 vs 2.

The uncertainty and adversarial subsets cover few instances per dataset, so the percentile bootstrap over
9 clusters is degenerate (many resamples contain the same handful of discordant pairs). The
pre-registered decision rule is the exact test; the intervals are reported but not used for verdicts. This was listed as a
threat before the run (section 23).

**Regret (exploratory, not pre-registered).** Paired regret differences on instances with a measured outcome
(`study-a-paired-regret.csv`):
- GOT − DIRECT: 0.041, CI [0.001,
  0.096], n = 59. This interval just excludes zero.
- TOT − DIRECT: 0.030, CI [-0.020,
  0.091].
- COT − DIRECT: 0.025, CI [-0.008,
  0.070].

No regret contrast favours a structured mode.
