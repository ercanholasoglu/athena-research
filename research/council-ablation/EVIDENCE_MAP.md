# Evidence map

Every number in [`writeups/council-ablation.en.md`](writeups/council-ablation.en.md) and `.tr.md` is listed here, with its source in [`evidence/`](evidence/) (Jev rows: [`research/jev/evidence/`](../jev/evidence/)) and the value recomputed from that source by `research/council-ablation/tools/check_evidence_map.py`. A number that is not in this table must not appear in the write-ups.

**Check result: PASS** (37 / 37 claims match).

| # | Claim | Value in write-ups | Recomputed | Label | Source | Check |
|---|---|---|---|---|---|---|
| 1 | Cases total / calibration / evaluation | 110 / 39 / 71 | 110 / 39 / 71 | MEASURED | `council/results.json: n_cases, n_calibration, n_evaluation` | PASS |
| 2 | Strong solo chosen on calibration | sonnet | sonnet | MEASURED | `council/results.json: strong_solo` | PASS |
| 3 | Strong solo accuracy | 0.986 | 0.986 | MEASURED | `conditions['A_solo:sonnet'].accuracy` | PASS |
| 4 | Haiku solo accuracy | 0.986 | 0.986 | MEASURED | `conditions['A_solo:haiku'].accuracy` | PASS |
| 5 | C and E accuracy (tie) | 0.986 / 0.986 | 0.986 / 0.986 | MEASURED | `conditions C_multi_provider, E_judge` | PASS |
| 6 | B1, B2, D, F accuracy | 0.972 | 0.972 | MEASURED | `conditions B1, B2, D, F` | PASS |
| 7 | B1/B2/D/F delta vs solo and CI | -0.014 [-0.042, 0] | -0.014 [-0.042, 0] | MEASURED | `conditions[...].vs_strong_solo` | PASS |
| 8 | All council decisions | REJECTED x6 | REJECTED x6 | MEASURED | `decisions` | PASS |
| 9 | H0 / H1 | NOT_REJECTED / NOT_SUPPORTED | NOT_REJECTED / NOT_SUPPORTED | MEASURED | `hypotheses` | PASS |
| 10 | H3 (F decision) | REJECTED | REJECTED | MEASURED | `hypotheses.H3.F_decision` | PASS |
| 11 | Sonnet cost per decision | 0.001994 | 0.001994 | MEASURED | `conditions['A_solo:sonnet'].cost_usd_per_decision` | PASS |
| 12 | Haiku cost per decision | 0.000129 | 0.000129 | MEASURED | `conditions['A_solo:haiku'].cost_usd_per_decision` | PASS |
| 13 | Judge cost / latency / tokens per decision | 0.004899 / 5.26 / 1927 | 0.004899 / 5.26 / 1927 | MEASURED cost; ESTIMATED latency | `conditions.E_judge` | PASS |
| 14 | Solo latency per decision | 2.31 | 2.31 | MEASURED | `conditions['A_solo:sonnet'].latency_s_per_decision` | PASS |
| 15 | Judge cost and latency multiples | 2.5x / 2.3x | 2.5x / 2.3x | ESTIMATED (ratio) | `E_judge vs A_solo:sonnet` | PASS |
| 16 | Haiku cost relative to Sonnet | 1/15 | 1/15 | ESTIMATED (ratio) | `A_solo:haiku vs A_solo:sonnet` | PASS |
| 17 | F escalations to human review | 36 / 71 | 36 / 71 | MEASURED | `conditions.F_adaptive_routing.escalated_to_human` | PASS |
| 18 | F calls per decision | 3.35 | 3.35 | MEASURED | `conditions.F_adaptive_routing.calls_per_decision` | PASS |
| 19 | Spearman gain vs double fault / provider count | -0.83 / -0.18 | -0.83 / -0.18 | MEASURED (descriptive) | `hypotheses.H2` | PASS |
| 20 | Combinations examined | 35 | 35 | MEASURED | `hypotheses.H2.combinations` | PASS |
| 21 | Sonnet~Haiku error phi | 1.0 | 1.0 | MEASURED | `pairwise_error_phi_evaluation['sonnet~haiku']` | PASS |
| 22 | Critic critical misses / verifier false alarms | 0.000 / 0.059 | 0.000 / 0.059 | MEASURED | `member_characteristics` | PASS |
| 23 | Critic is the only Claude member with zero critical misses | haiku_critic | haiku_critic | MEASURED | `member_characteristics` | PASS |
| 24 | Qwen 7B accuracy | 0.620 | 0.620 | MEASURED | `member_characteristics.qwen7b.accuracy` | PASS |
| 25 | Reproducibility of re-sampled Haiku | 110 / 110 | 110 / 110 | MEASURED | `system_quality` | PASS |
| 26 | Total provider-reported cost, distinct calls | 0.71 / 1506 | 0.71 / 1506 | MEASURED | `council/member_calls.jsonl + judge_calls.jsonl (sum of cost_usd)` | PASS |
| 27 | Re-asked truncated calls | 186 | 186 | MEASURED | `member_calls.jsonl rows beyond the archive` | PASS |
| 28 | Jev EXECUTION_SCALE raw accuracy A -> B | 0.578 -> 0.733 | 0.578 -> 0.733 | MEASURED | `research/jev/evidence/jev-semantics-ablation-2026-10-21.json: comparison_vs_experiment_a` | PASS |
| 29 | Jev intervals overlap | True | True | MEASURED | `comparison_vs_experiment_a.EXECUTION_SCALE.accuracy_raw.intervals_overlap` | PASS |
| 30 | Jev cost | UNKNOWN | UNKNOWN | UNKNOWN | `research/jev/evidence/jev-ablation-2026-10-21.json: cost.state` | PASS |
| 31 | Mean gain by provider count (1 / 2 providers) | -0.004 / -0.056 | -0.004 / -0.056 | MEASURED (descriptive) | `hypotheses.H2.mean_gain_by_provider_count` | PASS |
| 32 | Critic~Sonnet error phi | -0.014 | -0.014 | MEASURED | `pairwise_error_phi_evaluation['sonnet~haiku_critic']` | PASS |
| 33 | Qwen 1.5B accuracy / false-alarm rate | 0.282 / 0.882 | 0.282 / 0.882 | MEASURED | `member_characteristics.qwen1_5b` | PASS |
| 34 | Truncated at 300 tokens without an answer (verifier / critic / sonnet / all) | 44 / 31 / 8 / 186 | 44 / 31 / 8 / 186 | MEASURED | `council/member_calls_budget300_archive.jsonl (answer is null and tokens_out >= 300)` | PASS |
| 35 | Single strong-solo error on evaluation | feature_screening:29 | feature_screening:29 | MEASURED | `member_calls.jsonl (sonnet) vs cases.json` | PASS |
| 36 | Claude 5.5 accepts only temperature 1 | provider-enforced | provider-enforced | MEASURED | `protocol/AMENDMENTS.md, Amendment 1` | PASS |
| 37 | Critic right and outvoted | feature_screening:29, feature_screening:34 | feature_screening:29, feature_screening:34 | MEASURED (exploratory) | `member_calls.jsonl (B1 members) vs cases.json` | PASS |

**Must be said (and is):** pre-registration and amendments; ceiling effect; only two provider families, the second much weaker; the harness calls models directly (no product council path, no validator, no tenant context); the minority veto is untested; CoT/ToT/GoT in the product council are confidence/tie-break aggregation, not model reasoning (CoT/ToT/GoT as reasoning orchestration are measured separately, in Studies A and A2 of this repository).

**Must not be said:** that councils never work; that Athena's council improves anything; any vendor ranking; any number not in this table; any significance claim beyond the reported CIs.
