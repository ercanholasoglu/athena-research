# JEV retrospective: a typed bounded-decision model for AutoML decisions

Experiments A–E, 2026-10-20 to 2026-10-21. This is a retrospective. The experiments ran inside the private Athena
product, so their harness is **not public**. What is public:

- the five evidence files the article was written from ([`evidence/`](evidence/), pinned in
  [`evidence/SHA256SUMS`](evidence/SHA256SUMS));
- the derivation of every article number from those files ([`research/jev/tools/derive_facts.py`](tools/derive_facts.py) →
  [`results/facts.json`](results/facts.json));
- a [TRACE](TRACE.md) from each cited key to its evidence file.

Missing details are marked NOT PUBLIC (exists, withheld) or NOT RECOVERABLE (not recorded).

## Motivation

An AutoML system makes many small decisions that are not model training itself. Examples: how deep a
hyper-parameter search should go, which explanation method fits a model and budget, whether a failed step should be
retried. Each has a typed input and a short, closed list of actions, and a governance policy has the final word. We
call these *bounded decisions*.

The question was whether TypeSafe's Jev, a general model built for this shape of problem (typed state in, one
declared option out, with confidence and per-option probabilities), makes them well enough to be useful.

## Setup

| item | value |
|---|---|
| model | `{{jev:v2.model}}`, resolved from alias `jev-latest` (recorded in every evidence file) |
| access | TypeSafe API `POST /v1/systemone`, the author's personal credential; not sponsored |
| request shape | one choice question; state = the decision description + typed declared features (row count, feature count, model family, time budget, …); disclosure classes SCHEMA and AGGREGATED_STATISTICS |
| never sent | labels, label frequencies, rule thresholds, labelling constants, evaluation results, raw rows, personal data, credentials (the `contract.forbidden_information` list in the B evidence file) |
| decision types | A, B: six types on `decision-corpus-v1` ({{jev:ab.cases}} evaluated cases): four policy-defined, plus the two measured types EXPLANATION_MODE and HPO_DEPTH, whose labels come from running every alternative. C–E: the two measured types on `decision-corpus-v2` |
| benchmark v2 | {{jev:v2.datasets}} public datasets: {{jev:v2.dev}} for development, {{jev:v2.holdout}} held out until the final run (manifest: [`decision-corpus-v2-manifest.json`](evidence/decision-corpus-v2-manifest.json)) |
| pre-registration | C/D/E definitions and corpus committed before any C/D/E call (`pre_registration` in the C/D/E evidence; commit ids refer to the private product repository: NOT PUBLIC) |
| calls | A {{jev:a.calls}}, B {{jev:b.calls}} (+ 30 in phase B1), C/D/E {{jev:v2.calls}} |
| tokens, C/D/E | {{jev:v2.input_tokens|int}} input, {{jev:v2.output_tokens|int}} output |
| cost | UNKNOWN: the API returns token usage but no price or balance |

## Variants

| variant | change | benchmark |
|---|---|---|
| A | action names only | v1 |
| B | + typed semantics (meaning and selection criteria of every decision and action; `decision-semantics-v1`, SHA-256 in the evidence) | v1, then v2 as the baseline |
| C | richer semantics (`decision-semantics-v2`) | v2 |
| D | C + structured decision state (`decision-state-v2`) | v2 |
| E | D + decomposition into steps | v2 |

- **Prompt and contract text.** The semantics catalogues, state definitions and decomposition design are NOT PUBLIC:
  they are files in the private product repository. Their SHA-256s are recorded in the evidence.
- **Per-call request bodies.** NOT RECOVERABLE: no request ledger was kept.

## Comparators (baselines)

- **Rules.** Hand-written logic; for policy-defined types the rule defines correct.
- **Local bounded model.** Standardised features with logistic regression, trained on labelled decision cases.
  Two versions: the shipped one, and one retrained on the v2 development datasets only.
- **Hybrid and agentic.** A small local language model, `ollama/qwen2.5:1.5b`. These are the recorded 2026-10-20
  baseline on the same split, not re-run.

## Metrics

- Accuracy against the decision label, with 95% intervals: Wilson for A/B, dataset-clustered bootstrap for C/D/E.
- ECE.
- Input and output tokens per decision, and p50 latency.
- Reproducibility on repeated calls.
- C/D/E: {{jev:v2.tests}} pre-registered paired tests, Holm-corrected.

## Results

Original benchmark (v1; {{jev:ab.expl.n}} cases per measured type, {{jev:ab.retry.n}} for RETRY_FALLBACK; no per-case
answers stored, so no paired test):

| decision | A | B | rules | local bounded |
|---|---|---|---|---|
| EXPLANATION_MODE | {{jev:ab.expl.a|1}}% | {{jev:ab.expl.b|1}}% | {{jev:ab.expl.rules|1}}% | {{jev:ab.expl.local|1}}% |
| HPO_DEPTH | {{jev:ab.hpo.a|1}}% | {{jev:ab.hpo.b|1}}% | {{jev:ab.hpo.rules|1}}% | {{jev:ab.hpo.local|1}}% |
| RETRY_FALLBACK | {{jev:ab.retry.a|1}}% | {{jev:ab.retry.b|1}}% | {{jev:ab.retry.rules|1}}% | {{jev:ab.retry.local|1}}% |

B used {{jev:ab.tokens_ratio|2}}× A's input tokens.

Six unseen datasets (v2):

| decision | B | C | D | E | rules | local, shipped | local, retrained on v2 dev | constant |
|---|---|---|---|---|---|---|---|---|
| EXPLANATION_MODE | {{jev:v2.expl.jev_B|1}}% | {{jev:v2.expl.jev_C|1}}% | {{jev:v2.expl.jev_D|1}}% | {{jev:v2.expl.jev_E|1}}% | {{jev:v2.expl.rules|1}}% | {{jev:v2.expl.local_bounded|1}}% | {{jev:v2.expl.local_bounded_v2dev|1}}% | {{jev:v2.const.expl|1}}% |
| HPO_DEPTH | {{jev:v2.hpo.jev_B|1}}% | {{jev:v2.hpo.jev_C|1}}% | {{jev:v2.hpo.jev_D|1}}% | {{jev:v2.hpo.jev_E|1}}% | {{jev:v2.hpo.rules|1}}% | {{jev:v2.hpo.local_bounded|1}}% | {{jev:v2.hpo.local_bounded_v2dev|1}}% | {{jev:v2.const.hpo|1}}% |

- **Tests.** None of the {{jev:v2.tests}} pre-registered tests was significant after Holm; every adjusted p was
  {{jev:v2.min_p_holm|1}}. That does not show the variants are equal: the intervals over six datasets are wide.
- **EXPLANATION_MODE.** Jev never chose SKIP. B, C, D and E were right on exactly the same cases as the rules, at
  the accuracy of a constant predictor.
- **Cost of decomposition.** E used about {{jev:v2.hpo.jev_E.mult|1}}× B's input tokens on HPO_DEPTH with no accuracy
  gain.
- **Reproducibility.** Answers were identical on {{jev:v2.repeat_same}} of {{jev:v2.repeat_total}} repeated calls.
- **Exploratory.** The retrained local model's {{jev:v2.expl.local_bounded_v2dev|1}}% on EXPLANATION_MODE was not a
  pre-registered hypothesis. The same recipe scored {{jev:v2.hpo.local_bounded_v2dev|1}}% on HPO_DEPTH.

## Why Jev stayed experimental and opt-in

Jev was evaluated only as an experimental external method. It was never a default routing choice, and nothing in
the product changed because of these experiments. The evidence gave no reason to change that status:

- On unseen data no variant beat the rules or a constant predictor on EXPLANATION_MODE.
- On HPO_DEPTH, B was not distinguishable from the shipped local model.
- Cost could not be measured.

Jev remains an opt-in provider behind each user's own credential, and the governance policy remains the final
authority over every method's answer.

## Limitations

- **Holdout size.** Six holdout datasets give coarse intervals; non-inferiority could not be shown in either
  direction.
- **Labels and decision types.** Labels came from one machine. Only two decision types were rebuilt for v2, and the
  explanation holdout contains only two of the four labels.
- **Designs and version.** One wording per variant, one decomposition design, one model version.
- **A and B.** They were small and stored no per-case answers.
- **Cost.** Unknown.

## What is not public

| item | status |
|---|---|
| JEV harness: runner, prompt builders, semantics catalogues, state and decomposition definitions | NOT PUBLIC (private product code) |
| product code version (`athena_sha` in the evidence) | NOT PUBLIC; field replaced in the published evidence |
| where experiment B and C/D/E calls ran from | generalized to "the product's hosted backend environment (NOT PUBLIC)"; see [docs/REDACTIONS.json](../../docs/REDACTIONS.json) |
| per-call requests and raw responses | NOT RECOVERABLE (no request ledger was kept; C/D/E per-case answers are in [`evidence/jev-generalization-cde-cases-2026-10-21.jsonl`](evidence/jev-generalization-cde-cases-2026-10-21.jsonl)) |
| v1 constant baseline (48.4%) | quoted in the article from the private C/D/E report; not in the evidence files |
| the article's figures and page build | not part of this repository; [`research/jev/tools/derive_facts.py`](tools/derive_facts.py) is cut verbatim from that build |

Three evidence files differ from the originals only in the redacted fields. The published
[`SHA256SUMS`](evidence/SHA256SUMS) pins the published files, and [docs/REDACTIONS.json](../../docs/REDACTIONS.json)
lists each original SHA-256, the published SHA-256 and the fields changed.
`python research/jev/tools/derive_facts.py --check` reproduces every article fact from the published files.
