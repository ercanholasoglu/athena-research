# Experiments

Five experiments, in the order they ran. Each section says what was varied, what was held fixed, how it was scored and
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
- **Result.** B raised EXPLANATION_MODE accuracy from 22.6% to 58.1% on v1. On the six
  unseen v2 datasets, C, D and E added nothing. On EXPLANATION_MODE every variant was right on exactly the same cases
  as the rules, at the accuracy of a constant predictor (58.3%). 0 of 14
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
- **Data.** 8 unseen datasets, 116 runs, 276 calls.
- **Result.** Share of runs that blocked every trap: A_RAW 43.8%,
  C_DICT 81.2%, D_RULES 93.8%
  (Holm p 0.046), E_FULL
  56.2%.
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
- **Data.** 101 unseen instances from 9 datasets,
  3 seeds, 1,212 runs, 3,633 calls.
- **Result.** Accuracy: DIRECT 77.6%, CoT 77.2%, ToT
  75.9%, GoT 74.6%. No topology beat DIRECT. ToT and GoT used
  8.8× and 12.1× DIRECT's compute.
- **Material.** [research/reasoning-topology/original-study/](../research/reasoning-topology/original-study/).

## Study A2 (frozen 2026-10-29): topology with a frontier model

- **Design.** The frozen Study A topologies, prompts and contracts, run on 64 unseen
  instances from 4 datasets with 3 replicates.
- **Arms.** `gpt-6-luna` (new runs) against `qwen2.5:7b` (the frozen Study A unseen runs for the same instances).
- **Held fixed.** The frozen prompts. A run's first call is byte-identical across models; later calls embed each
  model's own earlier outputs. `tools/export_prompts.py` checks this.
- **Result.**
  - `gpt-6-luna` accuracy: DIRECT 86.5%, CoT 82.3%, ToT
    81.2%, GoT 64.6%. Every topology was significantly worse than
    DIRECT, and GoT lost −21.9 pp.
  - 58 of GoT's 68 errors were abstentions.
  - At DIRECT, `gpt-6-luna` beat `qwen2.5:7b` by +12.5 pp.
- **Material.** [research/reasoning-topology/frontier-replication/](../research/reasoning-topology/frontier-replication/).

## Study B2 (frozen 2026-10-29): semantic context with frontier models

- **Design.** Study B's frozen conditions and traps in 10 cells:
  - the 5 conditions on the trapped variant;
  - anonymized names under A_RAW and C_DICT;
  - an incomplete dictionary under D_RULES;
  - a misleading dictionary under D_RULES and E_FULL.
- **Data.** 4 datasets.
- **Feature invention.** A new call asks each model to invent features as expressions in a restricted grammar. Each
  feature is validated deterministically, checked for leakage, executed and evaluated on held-out data. It is then
  classed as VALID_USEFUL, VALID_NOT_USEFUL, INVALID_LOW_GAIN, INVALID_HIGH_APPARENT or NOT_EXECUTABLE.
- **Arms.**
  - `qwen2.5:7b`: 80 runs.
  - `gpt-6-luna`: 80 runs.
  - `claude-sonnet-5-5`: 40 runs, 1 replicate.
- **Result.**
  - **Capability plus meaningful column names recovered much of the documentation benefit.** At A_RAW, the share of
    runs blocking every trap was 12.5% for `qwen2.5:7b`,
    62.5% for `gpt-6-luna` and 100.0% for
    `claude-sonnet-5-5`.
  - **The dictionary still mattered once the columns were anonymized.** For `gpt-6-luna` it took that share from
    0.0% to 100.0% (Holm p
    0.031).
  - **Falsified dictionary entries.** `gpt-6-luna` detected 91.7%
    of them, against 0.0% for `qwen2.5:7b` (Holm p
    0.016).
  - **Missing definitions.** Detection was 21.7%,
    29.2% and
    37.5% for `qwen2.5:7b`, `gpt-6-luna` and
    `claude-sonnet-5-5`.
  - **Invented features were safer, not more useful.** Hosted models' features were executable and rarely leaky, but
    no more useful than the 7B model's.
- **Material.** [research/semantic-context/frontier-replication/](../research/semantic-context/frontier-replication/).
