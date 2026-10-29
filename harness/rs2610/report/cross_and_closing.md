## 21. Cross-study analysis

**Quality gain against cost.** Each arm is compared with its study's baseline: COT for Study A, as pre-registered in the
cross-study table, and A_RAW for Study B. The gain is in the study's headline quality metric. The multiples are total tokens
and audited server compute relative to the baseline. Source: `outputs/cross_study/quality-vs-cost.csv`, figures
`quality_gain_vs_cost_{dev,unseen}.png`.

| study | arm | quality metric | gain vs baseline (UNSEEN) | token multiple | compute multiple |
|---|---|---|---|---|---|
| A | DIRECT | decision accuracy | {{x.A.UNSEEN.DIRECT.decision_accuracy.quality_delta|pp}} pp | {{x.A.UNSEEN.DIRECT.decision_accuracy.token_multiple|2}} | {{x.A.UNSEEN.DIRECT.decision_accuracy.latency_multiple|2}} |
| A | TOT | decision accuracy | {{x.A.UNSEEN.TOT.decision_accuracy.quality_delta|pp}} pp | {{x.A.UNSEEN.TOT.decision_accuracy.token_multiple|2}} | {{x.A.UNSEEN.TOT.decision_accuracy.latency_multiple|2}} |
| A | GOT | decision accuracy | {{x.A.UNSEEN.GOT.decision_accuracy.quality_delta|pp}} pp | {{x.A.UNSEEN.GOT.decision_accuracy.token_multiple|2}} | {{x.A.UNSEEN.GOT.decision_accuracy.latency_multiple|2}} |
| B | B_SELF | all traps blocked | {{x.B.UNSEEN.B_SELF.all_traps_blocked.quality_delta|pp}} pp | {{x.B.UNSEEN.B_SELF.all_traps_blocked.token_multiple|2}} | {{x.B.UNSEEN.B_SELF.all_traps_blocked.latency_multiple|2}} |
| B | C_DICT | all traps blocked | {{x.B.UNSEEN.C_DICT.all_traps_blocked.quality_delta|pp}} pp | {{x.B.UNSEEN.C_DICT.all_traps_blocked.token_multiple|2}} | {{x.B.UNSEEN.C_DICT.all_traps_blocked.latency_multiple|2}} |
| B | D_RULES | all traps blocked | {{x.B.UNSEEN.D_RULES.all_traps_blocked.quality_delta|pp}} pp | {{x.B.UNSEEN.D_RULES.all_traps_blocked.token_multiple|2}} | {{x.B.UNSEEN.D_RULES.all_traps_blocked.latency_multiple|2}} |
| B | E_FULL | all traps blocked | {{x.B.UNSEEN.E_FULL.all_traps_blocked.quality_delta|pp}} pp | {{x.B.UNSEEN.E_FULL.all_traps_blocked.token_multiple|2}} | {{x.B.UNSEEN.E_FULL.all_traps_blocked.latency_multiple|2}} |

Table X1. Cost multiples above 1 mean the arm is more expensive than its baseline.

The two studies point the same way. **Adding model calls bought nothing measurable.** This covers ToT and GoT in Study A,
and B_SELF and E_FULL in Study B, which add a self-inference or verification stage. **Adding information bought the
improvements.** C_DICT and D_RULES add the owner's dictionary and rules for about {{x.B.UNSEEN.D_RULES.all_traps_blocked.token_multiple|2}}×
the tokens and no extra compute. In both studies the most expensive arm was not the best one:
- Study A: GOT at {{x.A.UNSEEN.GOT.decision_accuracy.latency_multiple|2}}× CoT's compute.
- Study B: E_FULL at {{x.B.UNSEEN.E_FULL.all_traps_blocked.latency_multiple|2}}× A_RAW's compute.

**Development vs unseen.** Source: `outputs/cross_study/dev-vs-unseen-gap.csv`, figure `dev_vs_unseen_gap.png`. In both
studies the DEVELOPMENT ranking failed to predict the UNSEEN ranking:
- Study A's DEVELOPMENT gains over CoT (DIRECT and TOT both {{a.DEVELOPMENT.DIRECT.accuracy|pct}} against CoT's
  {{a.DEVELOPMENT.COT.accuracy|pct}}) vanished on UNSEEN.
- Study B's DEVELOPMENT showed C_DICT and E_FULL *below* A_RAW on all traps blocked
  ({{x.B.DEVELOPMENT.C_DICT.all_traps_blocked.quality_delta|pp}} pp each). On UNSEEN, C_DICT was
  {{x.B.UNSEEN.C_DICT.all_traps_blocked.quality_delta|pp}} pp above.

With 5–6 development datasets and one seed, development was fit for debugging the harness and not for estimating effects.
That is why no conclusion in this report rests on DEVELOPMENT numbers.

## 22. Cost analysis

No provider was billed: every call ran on local Ollama. Cost in money is `NOT_APPLICABLE_LOCAL`, and energy is UNKNOWN (no
meter); neither is ever converted to zero. Cost is reported as calls, server-counted tokens and audited server compute.

| | runs | model calls | prompt tokens | output tokens | server compute (h) |
|---|---|---|---|---|---|
| Study A DEVELOPMENT | {{design.A.DEVELOPMENT.runs|int}} | {{design.A.DEVELOPMENT.calls|int}} | {{design.A.DEVELOPMENT.prompt_tokens|int}} | {{design.A.DEVELOPMENT.output_tokens|int}} | {{design.A.DEVELOPMENT.compute_hours|2}} |
| Study A UNSEEN | {{design.A.UNSEEN.runs|int}} | {{design.A.UNSEEN.calls|int}} | {{design.A.UNSEEN.prompt_tokens|int}} | {{design.A.UNSEEN.output_tokens|int}} | {{design.A.UNSEEN.compute_hours|2}} |
| Study B DEVELOPMENT | {{design.B.DEVELOPMENT.runs|int}} | {{design.B.DEVELOPMENT.calls|int}} | {{design.B.DEVELOPMENT.prompt_tokens|int}} | {{design.B.DEVELOPMENT.output_tokens|int}} | {{design.B.DEVELOPMENT.compute_hours|2}} |
| Study B UNSEEN | {{design.B.UNSEEN.runs|int}} | {{design.B.UNSEEN.calls|int}} | {{design.B.UNSEEN.prompt_tokens|int}} | {{design.B.UNSEEN.output_tokens|int}} | {{design.B.UNSEEN.compute_hours|2}} |

Table X2. Totals from the ledgers (`analyze_extra.design_facts`). Compute hours are summed from the server's own
prefill/decode timers and include the contaminated calls described in section 24.1. They are therefore an upper bound
for the work done, and are used only for this table. Per-run means elsewhere come from the audited latency files.

Per-arm cost is in section 12 (Study A, Table A5) and section 17 (Study B). In Study A the price of structure is fixed and
large:
- TOT costs {{ax.UNSEEN.TOT.compute_vs_direct|2}}× and GOT {{ax.UNSEEN.GOT.compute_vs_direct|2}}× the compute of DIRECT.
- They use {{ax.UNSEEN.TOT.output_tokens_mean_vs_direct|2}}× and {{ax.UNSEEN.GOT.output_tokens_mean_vs_direct|2}}× its
  output tokens.

In Study B the useful context is nearly free: D_RULES used {{x.B.UNSEEN.D_RULES.all_traps_blocked.token_multiple|2}}× A_RAW's
tokens at {{x.B.UNSEEN.D_RULES.all_traps_blocked.latency_multiple|2}}× its compute. The verification stage is what costs: E_FULL used
{{x.B.UNSEEN.E_FULL.all_traps_blocked.token_multiple|2}}× the tokens and {{x.B.UNSEEN.E_FULL.all_traps_blocked.latency_multiple|2}}× the compute.

## 25. Limitations

- **One model.** Everything is `qwen2.5:7b` (Q4_K_M) at temperature 0.4 on one local runtime. The substrate was forced: no
  credited provider key was available. No claim here transfers to larger or hosted models without a new run.
- **Few unseen datasets.**
  - Study A has {{design.A.UNSEEN.datasets}} and Study B {{design.B.UNSEEN.datasets}}.
  - Dataset-cluster intervals are coarse and, for small subsets, degenerate (section 11). Verdicts rest on the pre-registered
    exact or rank tests.
  - In Study B, three Holm verdicts flip when one dataset is removed (section 18).
- **Seeds.** 3 (Study A) and 2 (Study B) on UNSEEN. Seed variance is reported, not modelled.
- **Constructed benchmark.** The same authors wrote Study A's evidence packets and adversarial variants, Study B's traps, and
  the harness. The traps are strong and documented truthfully; real leaks are subtler.
- **Lenient Study A references.** A five-fold paired test sets the accept sets, which admits several options when
  differences are small. Two families are scripted, and their regret is UNKNOWN by design.
- **Small adversarial cells.** Study A has 3 instances per variant. Study B has 2 datasets × 2 seeds per adversarial
  variant. These cells are descriptive only.
- **Token caps sized on DEVELOPMENT.** Two Study B UNSEEN calls and one Study A UNSEEN call hit their caps (section 24.1).
  They are counted as failures, as pre-registered, and are not patched.
- **Latency.** The host slept twice during the UNSEEN runs: overnight during Study B, and a critical-battery sleep during
  Study A. The affected runs' compute is UNKNOWN, so per-run compute is a mean over known runs. Decisions and tokens are
  complete.
- **Feature engineering was mostly judgement.** Most Study B proposals copied an offered candidate
  ({{bx.UNSEEN.proposals_copying_candidates|pct}}), so Study B says little about feature *invention*.
- **Record keeping.** One count in the frozen Study B freeze record is wrong (superseded_v1 holds 16 runs, not 10). It is
  corrected in the journal and quoted from the file (section 24).

## 26. Negative and null results

Reported as found, without softening:

1. **Study A, H1.** We did not detect a statistically distinguishable accuracy difference between DIRECT, COT, TOT and GOT
   (all six Holm p = {{a.h.UNSEEN.H1.DIRECT.TOT.p_holm|2}}). Every point estimate favours the *less* structured mode.
2. **Study A, H2 and H3.** We did not detect the predicted advantages of TOT/GOT on adversarial evidence (Holm p
   {{a.h.UNSEEN.H2.COT.TOT.p_holm|p}}, {{a.h.UNSEEN.H2.COT.GOT.p_holm|p}}) or on preserving uncertainty (all Holm p
   {{a.h.UNSEEN.H3.COT.TOT.p_holm|2}}).
3. **Study A, fidelity.** The structured modes did not reliably follow their own structure (GOT
   {{a.UNSEEN.GOT.fidelity_rate|pct}}).
4. **Study B, E_FULL.** Adding a verification stage to D_RULES did not improve leakage avoidance. All traps blocked:
   {{b.UNSEEN.trapped.E_FULL.all_traps_blocked|pct}} against {{b.UNSEEN.trapped.D_RULES.all_traps_blocked|pct}} for
   D_RULES, and not distinguishable from A_RAW (Holm p {{b.paired.UNSEEN.trapped.all_traps_blocked.E_FULL.holm_p|p}}).
   E_FULL nearly doubled the tokens.
5. **Study B, B_SELF.** Self-inference was not distinguishable from A_RAW on any confirmatory metric.
6. **Study B, T3.** No condition noticed a missing dictionary definition in any run.
7. **Study B, T4.** E's verification flagged hidden leaks in only {{bx.t4.UNSEEN.E_FULL.hidden_leak.verify_contradicted}} of
   {{bx.t4.UNSEEN.E_FULL.hidden_leak.n}} runs.
8. **Study B, downstream.** We did not detect a statistically distinguishable difference on deployment collapse (Holm p
   {{b.paired.UNSEEN.trapped.deploy_collapse.D_RULES.holm_p|p}} for C_DICT and D_RULES), on the gap to the truth-clean
   model, or on the valid-and-leak-free share of proposed features.
9. **Study B, confidence.** Self-reported semantic confidence did not track correctness in any condition.
10. **Both studies, DEVELOPMENT.** DEVELOPMENT rankings did not predict UNSEEN rankings (section 21).

## 27. Implications for Athena

These are proposals. No product behaviour changed during or because of this program. Each proposal needs its own evaluation
before it ships.

1. **Do not introduce executed ToT/GoT for bounded AutoML decisions.**
   - Athena's existing chain/tree/graph council modes are post-hoc aggregations with identical model calls (section 9).
   - This study found no accuracy benefit from executed topologies, against a {{ax.UNSEEN.TOT.compute_vs_direct|1}}–{{ax.UNSEEN.GOT.compute_vs_direct|1}}×
     compute cost.
   - Proposal: keep a single well-specified call as the default. Label the existing modes honestly as aggregation
     strategies, not reasoning topologies.
2. **Treat the data owner's dictionary and rules as first-class inputs.** In Study B they made a leak-free pipeline more
   likely at almost no cost. Proposal: make dictionary and rule capture part of dataset onboarding, and feed them as
   constraints rather than as notes.
3. **Do not ship a verification stage of the E_FULL design as a safety feature.** It cost {{x.B.UNSEEN.E_FULL.all_traps_blocked.token_multiple|2}}× the tokens and added no measurable
   leakage protection. It challenged metadata that conflicts with the data's shape (swapped entries), not metadata that
   innocently describes a leak.
4. **Never rank candidate features by CV gain alone when a leak flag exists.** On UNSEEN, the
   {{bx.UNSEEN.cv_gain_top_all_leaky}} largest CV gains among {{bx.UNSEEN.cv_gain_ranked_n}} computable features were all
   leaky. Proposal: treat semantic validity and the run's own leak judgement as hard constraints on feature selection.
5. **Do not use the model's self-reported confidence as a gate.** In Study B it did not track correctness. In Study A the AUROC of
   confidence for separating right from wrong was {{a.UNSEEN.COT.auroc_conf|3}}–{{a.UNSEEN.DIRECT.auroc_conf|3}} for DIRECT, COT and TOT and
   {{a.UNSEEN.GOT.auroc_conf|3}} for GOT (descriptive).

## 28. Future work

- **A pre-registered test of isolated option evaluation under policy constraints.** It would test the Study A
  governance_block pattern (TOT {{a.adv.UNSEEN.governance_block.TOT.acc|pct}} against {{a.adv.UNSEEN.governance_block.COT.acc|pct}})
  with enough instances to be testable: at least 30 policy-override decisions on unseen datasets.
- **The same protocol on one or more frontier models**, to separate "structure does not help" from "structure does not help
  a 7B model".
- **A verification design that checks leakage semantics**, for example by re-deriving each column's availability time
  against the target, not only shape consistency. It would be evaluated on the T3/T4 variants with more datasets.
- **Feature invention rather than candidate judgement**: withhold the candidate list and measure what the model proposes.
- **More unseen datasets and seeds** for Study B, sized so that the confirmatory contrasts are not fragile to removing one
  dataset.
- **Token caps sized from the widest dataset in the program**, not the widest development dataset (lesson from section 24.1).
