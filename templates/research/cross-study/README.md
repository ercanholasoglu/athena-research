# WHAT ACTUALLY IMPROVES TABULAR AI DECISIONS?

This page compares three levers, within the experiments in this repository: a more **capable model**, more
**reasoning structure** (topology), and more **semantic context** (documentation). It adds no new analysis. Every
entry below is a result reported in a study README or report, and the order of the levers comes from the
pre-registered comparison in section 8 of the replication report.

## Compact matrix

| lever | Study A / A2 (bounded AutoML decisions) | Study B / B2 (semantic decisions, traps) | JEV (typed bounded-decision model) |
|---|---|---|---|
| **capability** | `gpt-6-luna` − `qwen2.5:7b` at DIRECT: {{r.x.capability.A2.LUNA.accuracy.effect|pp}} pp accuracy [{{r.x.capability.A2.LUNA.accuracy.ci_lo|pp}}, {{r.x.capability.A2.LUNA.accuracy.ci_hi|pp}}], Holm p {{r.a2.m.LUNA.DIRECT.p_holm|p}} | at A_RAW, all traps blocked {{r.b2.QWEN.A_RAW.all_traps_blocked|pct}} → {{r.b2.LUNA.A_RAW.all_traps_blocked|pct}} (`gpt-6-luna`) / {{r.b2.SONNET.A_RAW.all_traps_blocked|pct}} (`claude-sonnet-5-5`), descriptive | not tested (one model version) |
| **structure** | no gain on `qwen2.5:7b` (Study A and A2); on `gpt-6-luna` every topology worse than DIRECT, GoT {{r.a2.w.LUNA.DIRECT.GOT.effect_b_minus_a|pp}} pp, Holm p {{r.a2.w.LUNA.DIRECT.GOT.p_holm|p}} | — | decomposition (E) added nothing on unseen data |
| **semantics** | — | Study B (`qwen2.5:7b`): all traps blocked {{b.UNSEEN.trapped.A_RAW.all_traps_blocked|pct}} → {{b.UNSEEN.trapped.D_RULES.all_traps_blocked|pct}} with rules, Holm p {{b.paired.UNSEEN.trapped.all_traps_blocked.D_RULES.holm_p|3}}; B2: decisive with anonymized names (`gpt-6-luna` {{r.b2.LUNA.anon_A_RAW.all_traps_blocked|pct}} → {{r.b2.LUNA.anon_C_DICT.all_traps_blocked|pct}}, Holm p {{r.b2.s.LUNA.all_traps_blocked.anon_C_DICT_vs_anon_A_RAW.p_holm_sign|p}}), small with meaningful names on capable models | v1: EXPLANATION_MODE {{jev:ab.expl.a|1}}% → {{jev:ab.expl.b|1}}% (A → B); on 6 unseen datasets richer semantics (C) and structured state (D) added nothing over B (0 of {{jev:v2.tests}} tests significant) |

## Pre-registered comparison (A2, B2)

[`cross-study.csv`](cross-study.csv) (canonical copy:
[`outputs/replication/cross-study.csv`](../../harness/rs2610/outputs/replication/cross-study.csv); code:
[`replication/cross.py`](../../harness/rs2610/replication/cross.py)). A2 intervals are instance-cluster bootstraps
with Holm-adjusted McNemar p. B2 intervals are paired bootstraps over (dataset, replicate) units with an unadjusted
exact sign p.

| axis | study, metric | `qwen2.5:7b` | `gpt-6-luna` | `claude-sonnet-5-5` |
|---|---|---|---|---|
| capability (frontier − baseline) | A2, DIRECT accuracy | (baseline) | {{r.x.capability.A2.LUNA.accuracy.effect|pp}} [{{r.x.capability.A2.LUNA.accuracy.ci_lo|pp}}, {{r.x.capability.A2.LUNA.accuracy.ci_hi|pp}}] | not run |
| capability | B2, A_RAW core semantic accuracy | (baseline) | {{r.x.capability.B2.LUNA.core_semantic_accuracy.effect|pp}} [{{r.x.capability.B2.LUNA.core_semantic_accuracy.ci_lo|pp}}, {{r.x.capability.B2.LUNA.core_semantic_accuracy.ci_hi|pp}}] | {{r.x.capability.B2.SONNET.core_semantic_accuracy.effect|pp}} [{{r.x.capability.B2.SONNET.core_semantic_accuracy.ci_lo|pp}}, {{r.x.capability.B2.SONNET.core_semantic_accuracy.ci_hi|pp}}] |
| capability | B2, A_RAW all traps blocked | (baseline) | {{r.x.capability.B2.LUNA.all_traps_blocked.effect|pp}} [{{r.x.capability.B2.LUNA.all_traps_blocked.ci_lo|pp}}, {{r.x.capability.B2.LUNA.all_traps_blocked.ci_hi|pp}}] | {{r.x.capability.B2.SONNET.all_traps_blocked.effect|pp}} [{{r.x.capability.B2.SONNET.all_traps_blocked.ci_lo|pp}}, {{r.x.capability.B2.SONNET.all_traps_blocked.ci_hi|pp}}] |
| structure (best non-DIRECT − DIRECT) | A2, accuracy | {{r.x.structure.A2.QWEN.accuracy.effect|pp}} [{{r.x.structure.A2.QWEN.accuracy.ci_lo|pp}}, {{r.x.structure.A2.QWEN.accuracy.ci_hi|pp}}] | {{r.x.structure.A2.LUNA.accuracy.effect|pp}} [{{r.x.structure.A2.LUNA.accuracy.ci_lo|pp}}, {{r.x.structure.A2.LUNA.accuracy.ci_hi|pp}}] | not run |
| semantics (D_RULES − A_RAW) | B2, core semantic accuracy | {{r.x.semantics.B2.QWEN.core_semantic_accuracy.effect|pp}} [{{r.x.semantics.B2.QWEN.core_semantic_accuracy.ci_lo|pp}}, {{r.x.semantics.B2.QWEN.core_semantic_accuracy.ci_hi|pp}}] | {{r.x.semantics.B2.LUNA.core_semantic_accuracy.effect|pp}} [{{r.x.semantics.B2.LUNA.core_semantic_accuracy.ci_lo|pp}}, {{r.x.semantics.B2.LUNA.core_semantic_accuracy.ci_hi|pp}}] | {{r.x.semantics.B2.SONNET.core_semantic_accuracy.effect|pp}} [{{r.x.semantics.B2.SONNET.core_semantic_accuracy.ci_lo|pp}}, {{r.x.semantics.B2.SONNET.core_semantic_accuracy.ci_hi|pp}}] |
| semantics | B2, all traps blocked | {{r.x.semantics.B2.QWEN.all_traps_blocked.effect|pp}} [{{r.x.semantics.B2.QWEN.all_traps_blocked.ci_lo|pp}}, {{r.x.semantics.B2.QWEN.all_traps_blocked.ci_hi|pp}}] | {{r.x.semantics.B2.LUNA.all_traps_blocked.effect|pp}} [{{r.x.semantics.B2.LUNA.all_traps_blocked.ci_lo|pp}}, {{r.x.semantics.B2.LUNA.all_traps_blocked.ci_hi|pp}}] | {{r.x.semantics.B2.SONNET.all_traps_blocked.effect|pp}} [{{r.x.semantics.B2.SONNET.all_traps_blocked.ci_lo|pp}}, {{r.x.semantics.B2.SONNET.all_traps_blocked.ci_hi|pp}}] |

![Effect sizes side by side](figures/cross-study-effects.png)

*Figure: the table above as dot-and-interval rows. Scales differ across rows; compare order only. Generated by
`tools/replication_figures.py`.*

## Reading, within these tests

**Ordinal answer: capability > semantics > structure.**

- **Capability** gave the largest gains on both benchmarks.
- **Semantic documentation** mattered where names alone were not enough: trap blocking with a weak model, and
  anonymized columns. Where the column names were meaningful, a capable model barely needed it for core accuracy.
  A false dictionary was caught by the hosted models far more often than by the 7B model.
- **Reasoning structure** added nothing on the 7B model and cost accuracy on the hosted model, mostly through
  abstentions.
- **JEV** is a different kind of model and is listed separately. On its original benchmark, typed semantics raised
  one decision type sharply. On six unseen datasets, richer semantics, structured state and decomposition added
  nothing over B. B itself was not re-tested against A there, so the JEV report does not claim that B's gain was
  dataset-specific.

## Not claimed

- That topology never helps. Only four orchestrations, these decisions and these models were tested.
- That documentation is unnecessary for capable models. It was decisive once names were anonymized, and B2 has
  4–8 units per cell.
- Anything about the providers' top tiers, or any equality from a non-significant test.
- That the three levers are independent or additive. No experiment varied all three together.

## Folders

- [analysis/](analysis/): code and canonical table
- [figures/](figures/): figure above
