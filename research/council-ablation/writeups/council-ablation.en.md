---
title: "A pre-registered model-council experiment: the best single model won. What that does and does not mean."
result: REJECTED_ON_THIS_BENCHMARK
date_of_experiment: 2026-11-04
evidence: ../EVIDENCE_MAP.md · ../evidence/council/results.json · ../notebooks/03_council_judge_critic.ipynb
---

A multi-model "council" is an easy story to tell: ask several models, let them vote or argue, and the answer
gets better. Before that story was allowed near Athena's product claims, it was tested on the questions Athena
actually has to answer:
- Is this column leakage, a proxy for a protected attribute, or fine?
- Is this near-perfect score credible?
- Which model should be chosen under a stated policy?

The hypotheses, conditions, metrics and decision rules were written down and committed *before* the first model
call (`protocol/PREREGISTRATION.md`). Two problems with the plan came up. Both were recorded as amendments
before any result was read (`protocol/AMENDMENTS.md`):

1. Claude Haiku 5.5 and Sonnet 5.5 accept only `temperature = 1`.
2. The 300-token answer budget truncated 186 answers. Those calls were asked again with 1 024 tokens.

**How to read the numbers.**
- **MEASURED** numbers come from real provider calls, and cost is as the provider reported it.
- **ESTIMATED** numbers are derived from measured ones by a stated formula.
- **UNKNOWN** means the evidence does not say.

Every number below is listed in `EVIDENCE_MAP.md` with its source.

## Setup

* **110 closed-answer cases in nine families:** feature screening, target interpretation, policy conflict,
  validation interpretation, model selection, XAI interpretation, missing sources, feature-engineering
  suggestions and high-consequence decisions.
* **Ground truth** comes from public dataset documentation or from a rule stated inside the case, never from a
  model. No dataset rows are used.
* **Split:** 39 cases chose the baseline and the "diverse" council; 71 were held out for evaluation.
* **Conditions:**
  * **A** — a strong single model;
  * **B** — a same-provider council: role prompts (B1) or three samples of one model (B2);
  * **C** — a multi-provider council;
  * **D** — a council chosen for uncorrelated errors;
  * **E** — a judge that reads the three C answers and decides;
  * **F** — an adaptive router that escalates only on disagreement or high consequence.

## Result (MEASURED)

* **The strong single model** (Sonnet 5.5) answered **70 of 71** held-out cases correctly (0.986).
* **No council beat it:**
  * the multi-provider council (C) and the judge (E) **tied** at 70/71;
  * the role council, the sampling council, the "diverse" council and the router scored **69/71**
    (0.972; Δ −0.014, 95 % CI [−0.042, 0]).
* **Under the pre-registered rules**, every council condition is **REJECTED_ON_THIS_BENCHMARK**.
  - H0 (a council does not materially beat the best solo model) is not rejected.
  - H1 (the value sits in hard segments) is not supported.
  - H3 (adaptive routing gives a better frontier) is rejected.

## Cost and latency

| Condition | Accuracy | Calls / decision | Tokens / decision | Latency s / decision | Cost $ / decision |
|---|---|---|---|---|---|
| A strong solo (Sonnet) | 0.986 | 1 | 432 | 2.31 | 0.00199 |
| A cheap solo (Haiku) | 0.986 | 1 | 490 | 1.77 | 0.00013 |
| B1 roles | 0.972 | 3 | 1 786 | 2.43 | 0.00049 |
| B2 sampling | 0.972 | 3 | 1 459 | 2.10 | 0.00038 |
| C multi-provider | 0.986 | 3 | 1 187 | 2.71 | 0.00212 |
| D diverse | 0.972 | 3 | 1 344 | 2.72 | 0.00218 |
| E judge | 0.986 | 4 | 1 927 | 5.26 | 0.00490 |
| F router | 0.972 | 3.35 | 1 501 | 3.07 | 0.00203 |

* **Cost and per-call latency are MEASURED.** Cost is provider-reported, and the local Qwen calls cost 0.
* **Council latency is ESTIMATED.** It is the slowest member plus the judge, on the assumption that members run
  in parallel.
* **Judge (E):** 2.5× the cost (USD 0.004899 vs 0.001994) and 2.3× the latency (5.26 s vs 2.31 s) of the strong
  solo model, for the same accuracy.
* **Router (F):** sent **36 of 71** decisions to human review, because every high-consequence case was escalated
  by rule.
* **Cheapest equally accurate configuration:** a solo Haiku, at about 1/15 of the strong solo model's cost per
  decision.
* **Total provider-reported cost of the whole experiment:** USD 0.71 for 1 506 distinct recorded calls (1 396
  member calls including the 186 re-asked ones, plus 110 judge calls). An earlier internal figure of USD 1.04
  counted the archived 300-token pass twice; the archive's rows are the first 1 210 rows of the final cache.
* **UNKNOWN:**
  - latency on a production network path;
  - prompt-cache effects;
  - the cost of any provider that does not report one.

## Interpretation

A single model at 70/71 leaves a council at most one case to win, and the decision rule cannot tell "no value"
from "no room". The defensible reading is narrow: *on governance questions a frontier model already answers
correctly, a council added no accuracy and cost more than the cheapest equally accurate single model.* Against
the strong solo model, the Haiku-only councils B1 and B2 were cheaper per decision, and less accurate.

This does **not** show that councils never work. There is no evidence either way about the questions a
frontier model gets wrong, which is where a council would have to earn its keep.

What the data do show is how members fail:

* **Same model, same errors.** Sonnet and Haiku made the *same* single mistake (error correlation 1.0), so
  stacking them adds nothing.
* **A role prompt changes how a model fails.**
  * The "conservative verifier" role produced the only false alarms among the Claude members (0.059).
  * The "semantic critic" role was the only Claude member with zero critical misses.
* **Majority vote discarded the useful signal.** On `feature_screening:29` and `:34` the critic gave the
  correct answer. In both cases the other two role members outvoted it.
* **Gain tracked shared failure, not vendor count.** Across all 35 three-member councils, gain tracked how often
  members failed *on the same case* (rank correlation −0.83). Its link to the number of providers was far weaker
  (−0.18). This is descriptive: the combinations overlap, and the only second provider was a much weaker local
  model.

## What the other reasoning methods are, and what was not measured

| Method | Implemented | Wired | Evaluation |
|---|---|---|---|
| Council (vote) | yes | yes, advisory | MEASURED (this study) |
| Proposer / judge | yes | yes, off by default | MEASURED as condition E only |
| Critic with protective-minority veto | no | no | NOT_RUN |
| CoT / ToT / GoT | yes, as aggregation | yes, confidence only | SIMULATED (mock runner) |
| Self-consistency | no | no | NOT_RUN |
| ReAct | no | no | NOT_RUN |
| Reflexion (one diagnose-and-retry step) | yes | yes, API only | NOT_RUN |
| Program-of-Thought / evidence enforcement | yes, partial | yes | NOT_RUN |
| MCTS (feature strategy) | no | no | NOT_RUN |
| Jev bounded decisions | yes | yes, off by default | MEASURED on a different benchmark |

* **CoT / ToT / GoT in Athena are not language-model reasoning.** They are post-hoc aggregations over the council
  members' answers. The chain, tree or graph is built from the returned text and makes no model call of its own.
  Its only effect is a ×1.15 confidence boost, which under the default vote strategy only breaks ties. They are
  therefore labelled confidence / tie-break behaviour. No accuracy claim is made for them.
  CoT, ToT and GoT as orchestration of model calls are a different thing. They were measured on bounded AutoML
  decisions in Studies A and A2 of this repository ([reasoning topology](../../reasoning-topology/)), not on this case set.
* **Jev** was measured on a separate decision corpus (`notebooks/01_routing_and_jev.ipynb`). On one decision
  family, typed semantics raised its accuracy from 0.578 to 0.733, but the 95 % intervals overlap, so the gain is
  not established. Its cost is UNKNOWN because the provider reports no price.

## Limitations

* **Ceiling.** With 70/71 for the solo model, the benchmark cannot show improvement.
* **Providers.** Only two provider families were reachable. The second, a local 7B model, scored far lower
  (0.620), so adding it mostly added errors.
* **Harness, not product.** The harness called the models directly. Athena's council endpoint, its evidence
  validator and tenant context were not used, so validator agreement and organization-context use are
  `NOT_MEASURED`.
* **Description, not inference.** The 35 combinations overlap and are not independent samples.
* **One configuration.** One temperature (forced by the provider) and one prompt family.
* **Authorship.** The case author is also the harness author. The single solo error (`feature_screening:29`) has
  a debatable reference answer.

## Next hypotheses (not findings)

1. **Headroom first.** On cases chosen *because* a frontier single model gets them wrong, a council may help.
   The next study must first show at least 15 % solo error on calibration. Otherwise it stops as
   `NOT_RUN — CEILING`.
2. **Protective-minority veto.** A veto rule (escalate when a calibrated member flags a critical risk) may keep
   the dissent that majority vote discarded. It is untested and will be pre-registered first.
3. **Characteristic diversity is not proven.** It may matter only when members' errors are measurably
   uncorrelated on the target task *and* the strongest member is below ceiling.

Each of these, and each untested method in the table above, is recorded as `RESEARCH_PLANNED`. Every plan has a
hypothesis, baseline, task family, metric, budget, stopping rule and production admission gate
(`METHODOLOGY.md`). None is presented as a product capability.

## What Athena does today

On the default path Athena uses a single strong model, deterministic checks and its evidence validator. When
something looks wrong, such as leakage or an implausible score, Athena **warns** and asks for review instead of
deciding silently. A council is not a product claim.

*The pre-registration, amendments, parsed model answers (without raw completions), judge log, analysis harness
and eight notebooks that re-read the frozen evidence are in this repository. The analysis reproduces
`evidence/council/results.json` exactly from the published, non-raw answers (`REPRODUCIBILITY.md`).*
