# Experiments

Six experiments, in the order they ran. Each section says what was varied, what was held fixed, how it was scored and
where the full material is. Numbers are point estimates on held-out data; intervals and tests are in the study READMEs
and the two reports.

## JEV (2026-10-20 to 2026-10-21): a typed bounded-decision model

- **Question.** Can TypeSafe's Jev, a general bounded-decision model (typed state in, one declared option out), make
  narrow AutoML decisions well enough to be useful?
- **Decisions.** EXPLANATION_MODE and HPO_DEPTH (labels *measured* by running every alternative), plus policy-defined
  types in experiments A and B.
- **Variants.** A: action names only. B: typed semantics for every decision and action. C: richer semantics.
  D: structured state. E: decomposition into steps.
- **Benchmarks.** A and B ran on `decision-corpus-v1`. B to E ran on `decision-corpus-v2`: 16 datasets, 10 for
  development and 6 held out until the final run.
- **Comparators.** Rules, a local bounded classifier (shipped, and one retrained on the v2 development datasets), and
  hybrid and agentic methods on a small local model.
- **Result.** B raised EXPLANATION_MODE accuracy from {{jev:ab.expl.a|1}}% to {{jev:ab.expl.b|1}}% on v1. On the six
  unseen v2 datasets, C, D and E added nothing. On EXPLANATION_MODE every variant was right on exactly the same cases
  as the rules, at the accuracy of a constant predictor ({{jev:v2.const.expl|1}}%). 0 of {{jev:v2.tests}}
  pre-registered tests were significant after Holm.
- **Material.** [research/jev/](../research/jev/). The evidence files are public. The JEV harness is not, because it
  ran inside the private product.

## Study B (frozen 2026-10-27): semantic context, `qwen2.5:7b`

- **Question.** Does documentation (a data dictionary, business rules, a verification pass) make a model's semantic
  decisions about a table safer and more correct?
- **Conditions.**
  - A_RAW: profile only.
  - B_SELF: the model first infers every column's meaning and role.
  - C_DICT: + the owner's dictionary.
  - D_RULES: + business rules, a code dictionary and constraints.
  - E_FULL: D plus a verification pass that checks each documented column against the profile.
- **Held fixed.** Every condition gets byte-identical profile, task text, schema and candidate list.
- **Traps.** Every dataset carries the same traps:
  - an identifier assigned in target order;
  - a post-outcome column;
  - a warehouse-artifact column: positives were batch-loaded on Fridays;
  - a candidate list containing an identifier transform, a post-outcome flag, the Friday flag and a full-table
    target encoding;
  - a causal/predictive distinction: the intervention column must be an actionable lever.
- **Adversarial variants.** Anonymized names, an incomplete dictionary, and a misleading dictionary with three false
  entries per dataset.
- **Scoring.** Against an evaluation-authority truth the model never sees. Proposed features are executed and
  evaluated on held-out data.
- **Data.** 8 unseen datasets, {{design.B.UNSEEN.runs|int}} runs, {{design.B.UNSEEN.calls|int}} calls.
- **Result.** Share of runs that blocked every trap: A_RAW {{b.UNSEEN.trapped.A_RAW.all_traps_blocked|pct}},
  C_DICT {{b.UNSEEN.trapped.C_DICT.all_traps_blocked|pct}}, D_RULES {{b.UNSEEN.trapped.D_RULES.all_traps_blocked|pct}}
  (Holm p {{b.paired.UNSEEN.trapped.all_traps_blocked.D_RULES.holm_p|3}}), E_FULL
  {{b.UNSEEN.trapped.E_FULL.all_traps_blocked|pct}}.
- **Material.** [research/semantic-context/original-study/](../research/semantic-context/original-study/).

## Study A (frozen 2026-10-28): reasoning topology, `qwen2.5:7b`

- **Question.** With the same task and evidence, do CoT, ToT and GoT differ from a direct answer?
- **Topologies.** The four topologies differ in *execution*, not only in prompt wording:
  - DIRECT: 1 call.
  - CoT: 1 call with schema-enforced ordered steps.
  - ToT: 5 calls. Three branches, isolated calls per branch, a deterministic prune, then selection.
  - GoT: 5 calls. Shared claim nodes, typed support, contradiction and conflict edges, deterministic weighted
    propagation, then aggregation.
- **Decisions.** 10 families of bounded AutoML decisions (calibration, causal vs predictive, explanation, feature-engineering strategy, feature-selection strategy, HPO depth, imbalance, model family, trust plan, validation). Options are closed and the correct answer is defined by rule from measured evidence. Adversarial
  instances are included.
- **Data.** {{design.A.UNSEEN.instances|int}} unseen instances from {{design.A.UNSEEN.datasets|int}} datasets,
  3 seeds, {{design.A.UNSEEN.runs|int}} runs, {{design.A.UNSEEN.calls|int}} calls.
- **Result.** Accuracy: DIRECT {{a.UNSEEN.DIRECT.accuracy|pct}}, CoT {{a.UNSEEN.COT.accuracy|pct}}, ToT
  {{a.UNSEEN.TOT.accuracy|pct}}, GoT {{a.UNSEEN.GOT.accuracy|pct}}. No topology beat DIRECT. ToT and GoT used
  {{ax.UNSEEN.TOT.compute_vs_direct|1}}× and {{ax.UNSEEN.GOT.compute_vs_direct|1}}× DIRECT's compute.
- **Material.** [research/reasoning-topology/original-study/](../research/reasoning-topology/original-study/).

## Study A2 (frozen 2026-10-29): topology with a frontier model

- **Design.** The frozen Study A topologies, prompts and contracts, run on {{r.design.a2.instances|int}} unseen
  instances from {{r.design.a2.datasets|int}} datasets with 3 replicates.
- **Arms.** `gpt-6-luna` (new runs) against `qwen2.5:7b` (the frozen Study A unseen runs for the same instances).
- **Held fixed.** The frozen prompts. A run's first call is byte-identical across models; later calls embed each
  model's own earlier outputs. `tools/export_prompts.py` checks this.
- **Result.**
  - `gpt-6-luna` accuracy: DIRECT {{r.a2.LUNA.DIRECT.accuracy|pct}}, CoT {{r.a2.LUNA.COT.accuracy|pct}}, ToT
    {{r.a2.LUNA.TOT.accuracy|pct}}, GoT {{r.a2.LUNA.GOT.accuracy|pct}}. Every topology was significantly worse than
    DIRECT, and GoT lost {{r.a2.w.LUNA.DIRECT.GOT.effect_b_minus_a|pp}} pp.
  - {{r.a2.err.LUNA.GOT.wrong_abstained|int}} of GoT's {{r.a2.err.LUNA.GOT.wrong|int}} errors were abstentions.
  - At DIRECT, `gpt-6-luna` beat `qwen2.5:7b` by {{r.a2.m.LUNA.DIRECT.effect_b_minus_a|pp}} pp.
- **Material.** [research/reasoning-topology/frontier-replication/](../research/reasoning-topology/frontier-replication/).

## Study B2 (frozen 2026-10-29): semantic context with frontier models

- **Design.** Study B's frozen conditions and traps in 10 cells:
  - the 5 conditions on the trapped variant;
  - anonymized names under A_RAW and C_DICT;
  - an incomplete dictionary under D_RULES;
  - a misleading dictionary under D_RULES and E_FULL.
- **Data.** {{r.design.b2.datasets|int}} datasets.
- **Feature invention.** A new call asks each model to invent features as expressions in a restricted grammar. Each
  feature is validated deterministically, checked for leakage, executed and evaluated on held-out data. It is then
  classed as VALID_USEFUL, VALID_NOT_USEFUL, INVALID_LOW_GAIN, INVALID_HIGH_APPARENT or NOT_EXECUTABLE.
- **Arms.**
  - `qwen2.5:7b`: {{r.design.b2.QWEN.runs|int}} runs.
  - `gpt-6-luna`: {{r.design.b2.LUNA.runs|int}} runs.
  - `claude-sonnet-5-5`: {{r.design.b2.SONNET.runs|int}} runs, 1 replicate.
- **Result.**
  - **Capability plus meaningful column names recovered much of the documentation benefit.** At A_RAW, the share of
    runs blocking every trap was {{r.b2.QWEN.A_RAW.all_traps_blocked|pct}} for `qwen2.5:7b`,
    {{r.b2.LUNA.A_RAW.all_traps_blocked|pct}} for `gpt-6-luna` and {{r.b2.SONNET.A_RAW.all_traps_blocked|pct}} for
    `claude-sonnet-5-5`.
  - **The dictionary still mattered once the columns were anonymized.** For `gpt-6-luna` it took that share from
    {{r.b2.LUNA.anon_A_RAW.all_traps_blocked|pct}} to {{r.b2.LUNA.anon_C_DICT.all_traps_blocked|pct}} (Holm p
    {{r.b2.s.LUNA.all_traps_blocked.anon_C_DICT_vs_anon_A_RAW.p_holm_sign|p}}).
  - **Falsified dictionary entries.** `gpt-6-luna` detected {{r.b2.LUNA.mislead_D_RULES.falsified_detected_recall|pct}}
    of them, against {{r.b2.QWEN.mislead_D_RULES.falsified_detected_recall|pct}} for `qwen2.5:7b` (Holm p
    {{r.b2.m.LUNA.falsified_detected_recall.mislead_D_RULES.p_holm|p}}).
  - **Missing definitions.** Detection was {{r.b2.QWEN.incompl_D_RULES.missing_semantics_recall|pct}},
    {{r.b2.LUNA.incompl_D_RULES.missing_semantics_recall|pct}} and
    {{r.b2.SONNET.incompl_D_RULES.missing_semantics_recall|pct}} for `qwen2.5:7b`, `gpt-6-luna` and
    `claude-sonnet-5-5`.
  - **Invented features were safer, not more useful.** Hosted models' features were executable and rarely leaky, but
    no more useful than the 7B model's.
- **Material.** [research/semantic-context/frontier-replication/](../research/semantic-context/frontier-replication/).

## Council ablation (frozen 2026-11-04): model councils on ML-governance questions

- **Question.** Does a council of models beat one strong model on closed-answer ML-governance questions, and does
  measured error diversity predict when it does?
- **Cases.** {{council:cases.total}} cases in nine families, {{council:cases.calibration}} for calibration and
  {{council:cases.evaluation}} held out. Ground truth comes from public dataset documentation or a stated rule.
- **Conditions.** A single model; B1 same-provider roles; B2 same-provider sampling; C multi-provider;
  D characteristic-diverse; E judge; F adaptive routing.
- **Result.** The single model (`{{council:solo.model}}`) answered {{council:solo.correct}} of
  {{council:cases.evaluation}}. {{council:conditions.tied}} councils tied it, {{council:conditions.below}} scored
  {{council:conditions.below_correct}}, and none beat it. All {{council:conditions.rejected}} council conditions are
  `REJECTED_ON_THIS_BENCHMARK`. The judge cost {{council:E.cost_ratio|1}}× the single model per decision.
- **Scope.** A ceiling-bounded negative result. It does not show that councils never help.
- **Material.** [research/council-ablation/](../research/council-ablation/): write-ups (EN, TR), evidence map,
  notebooks, and the research plans for the methods not yet measured.
