## 13. Study A failures

- **Parse failures:** 1 UNSEEN run, the single truncated call (GOT edges,
  `card_fraud_synth::TRUST_PLAN`, seed 1, 1200/1200 tokens). Counted as wrong, as pre-registered.
- **Hard families for every mode:** TRUST_PLAN (25.0%–50.0%)
  and HPO_DEPTH (50.0%–62.5%).
- **Incomplete evidence:** the right answer was "undetermined". No mode exceeded
  33.3%, and TOT reached 0.0%.
- **Policy override:** with a policy forbidding the best scorer, DIRECT and COT were wrong in every run.
- **Causal vs predictive conflict:** DIRECT chose the lever backed by the randomized pilot in
  100.0% of runs; COT, TOT and GOT in 44.4%,
  44.4% and 44.4%. This is descriptive, 3 instances.
- **Structure not followed:** GOT's final call overrode its own propagated ranking in about a third of runs.
- **Seed instability:** TOT's decisions agreed across seeds only 53.1% of the time.
