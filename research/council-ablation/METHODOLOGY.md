# Methodology

## Completed study: council ablation (2026-11-04)

* **Pre-registration.** Hypotheses H0–H3, conditions A–F, the calibration/evaluation split (every third case per
  family is calibration), metrics and decision rules were committed before the first model call:
  [`protocol/PREREGISTRATION.md`](protocol/PREREGISTRATION.md). The two amendments were recorded before any result was read:
  [`protocol/AMENDMENTS.md`](protocol/AMENDMENTS.md).
* **Cases.** 110 closed-answer cases in nine families ([`evidence/council/cases.json`](evidence/council/cases.json)). Ground truth comes from
  public dataset documentation or from a rule stated in the case; no label is produced by a model.
* **Members.** Claude Sonnet 5.5 and Haiku 5.5 (temperature 1, provider-enforced), local Qwen 2.5 7B and 1.5B
  (temperature 0, Q4_K_M). One cached answer per member and case; the last cached row is the analysed one.
* **Aggregation.** Plurality, ties broken by mean confidence. An unparseable answer is an abstention.
* **Statistics.** 95 % paired bootstrap CIs, 2 000 resamples, seed 11, on the 71 evaluation cases.
* **Decision rules.** SUPPORTED / CONDITIONAL_VALUE / REJECTED / INSUFFICIENT_EVIDENCE, as pre-registered.
* **Exploratory, labelled as such.** The critic-outvoted observation (notebook 03) and the calibration table
  (notebook 06) were not pre-registered.

## Labels

* **MEASURED** — produced by a real provider call or a real run.
* **ESTIMATED** — derived from measured data by a stated formula (for example council latency = slowest
  member + judge).
* **SIMULATED** — produced by a mock runner; never a quality result.
* **NOT_RUN** — no result exists.
* **UNKNOWN** — the evidence does not say.

Implementation and wiring are reported separately from evaluation: code that exists is not a measured capability.

## Planned research (`RESEARCH_PLANNED`)

None of the methods below is an Athena capability or production feature. No performance claim is made for a
method that has not been run. Paid calls start only after the budget is approved.

**Prior evidence in this repository.** "Not run" below means not run on the council case set or in the product. Two
of the methods have measured results on a different task family elsewhere in this repository:
* CoT, ToT and GoT as reasoning orchestration were measured on bounded AutoML decisions in
  [Study A](../reasoning-topology/original-study/) and [Study A2](../reasoning-topology/frontier-replication/). No
  topology beat a direct answer.
* Bounded-decision routing to a typed model was measured in the [JEV retrospective](../jev/).

Those results do not transfer to the council governance cases by assumption. Each plan below states its own baseline
and gate.


### Hermes persona routing (agent / model / tool route selection) — `research_hermes_routing`

* **Purpose.** Measure whether the right agent, model or tool route is chosen for a task given task type, cost, latency and evidence needs.
* **Hypothesis.** A route chosen from the task's declared type, consequence and evidence need matches the oracle-best route on at least 80 % of tasks at no more than 1.2x the cost of the cheapest adequate route.
* **Baseline.** Fixed default route (single strong model + deterministic checks); oracle-best route computed after the fact from all routes' measured outcomes.
* **Dataset / task family.** Athena task log families: bounded decisions (decision-corpus-v1), governance questions (council case set), report narration; synthetic and public-documentation tasks only.
* **Metric.** Route accuracy vs oracle; regret in cost and latency; critical-miss rate of the chosen route.
* **Budget.** USD 15 provider cost cap; local models count 0.
* **Stopping rule.** Stop at the cost cap, at > 5 % harness failures after one retry, or when collection completes. Stop before evaluation if no route differs from the default on calibration (no headroom).
* **Production admission gate.** Route accuracy CI lower bound >= 0.8 and critical-miss rate not higher than the default route on a held-out split; shadow mode next to the existing router before any authority.
* **Current status.** NOT_RUN. The routing rule of the Athena Hermes persona has not been measured. Unrelated to the Nous Research Hermes agent runtime, which is not embedded in Athena.

### Program of Thoughts (PoT) — `research_program_of_thoughts`

* **Purpose.** Measure whether executable computation, instead of natural-language reasoning, increases correctness on numeric calculation, metric verification, feature statistics and tabular analysis.
* **Hypothesis.** On numeric tabular questions, PoT (model writes code, sandbox executes it, model explains the result) answers at least 10 percentage points more questions correctly than direct natural-language answers.
* **Baseline.** Direct single-model answer; Athena's canonical deterministic computation as the ground truth.
* **Dataset / task family.** Metric recomputation, feature statistics, threshold arithmetic and split-validity checks on public datasets (UCI Adult, Bank Marketing, Telco).
* **Metric.** Exact-answer accuracy (numeric tolerance stated per task); execution failure rate; cost and latency per answer.
* **Budget.** USD 10 provider cost cap; sandbox execution only, no network.
* **Stopping rule.** Cost cap; > 5 % sandbox failures; or completion. Stop before evaluation if the direct baseline is >= 95 % correct on calibration.
* **Production admission gate.** Accuracy gain CI excludes 0; no sandbox escape in the security suite; every number in a narrative traceable to an executed computation.
* **Current status.** NOT_RUN as a method comparison. Evidence enforcement (numbers come from canonical computation, the model only explains them) is wired in part of the reporting path; that is not a measured PoT result.

### Chain-of-Thought prompting — `research_cot`

* **Purpose.** Measure the accuracy, calibration and cost difference of chain-of-thought prompting against a single-step answer.
* **Hypothesis.** CoT prompting improves accuracy on adversarial and ambiguous governance cases without worsening calibration (ECE) and at no more than 3x output tokens.
* **Baseline.** Single-step answer of the same model and temperature.
* **Dataset / task family.** Council case families with measured solo headroom (new case set, >= 15 % solo error on calibration).
* **Metric.** Accuracy, ECE, Brier, critical-miss rate, tokens, latency.
* **Budget.** USD 10 provider cost cap.
* **Stopping rule.** Headroom screen fails (solo error < 15 % on calibration) -> NOT_RUN — CEILING; cost cap; or completion.
* **Production admission gate.** Accuracy gain CI excludes 0 and ECE not worse; raw chain-of-thought is never stored or shown.
* **Current status.** NOT_RUN with a real provider. The existing 'chain aggregation' is a confidence multiplier over council answers (tie-break behaviour) and is not labelled as real CoT.

### Tree-of-Thoughts — `research_tot`

* **Purpose.** Measure whether exploring several candidate reasoning paths improves result quality on hard tabular and modelling decisions.
* **Hypothesis.** Model-scored tree search over candidate decisions improves accuracy on hard model-selection and validation-interpretation cases by at least 10 percentage points over a single path.
* **Baseline.** Single-path answer; CoT arm of research_cot.
* **Dataset / task family.** Model selection and validation interpretation cases with measured solo headroom.
* **Metric.** Accuracy, critical-miss rate, calls, tokens, latency.
* **Budget.** USD 15 provider cost cap.
* **Stopping rule.** Headroom screen; cost cap; completion.
* **Production admission gate.** Accuracy gain CI excludes 0 at an accepted cost multiple; deterministic re-check of the chosen decision.
* **Current status.** NOT_RUN with a real provider. The existing 'tree aggregation' scores branches from returned text and makes no model calls of its own.

### Graph-of-Thoughts — `research_got`

* **Purpose.** Measure whether graph-based reasoning improves interdependent decisions such as feature engineering, model selection and error analysis.
* **Hypothesis.** Reasoning over a dependency graph of related decisions reduces contradictory decisions across a run by at least half compared with independent per-decision answers.
* **Baseline.** Independent per-decision single-model answers; deterministic Athena pipeline.
* **Dataset / task family.** Multi-step runs on public datasets where feature, model and error-analysis decisions depend on each other.
* **Metric.** Cross-decision contradiction rate, final model quality on a locked test split, cost, latency.
* **Budget.** USD 20 provider cost cap.
* **Stopping rule.** Cost cap; > 5 % run failures; completion.
* **Production admission gate.** Contradiction reduction CI excludes 0 with no loss of locked-test quality.
* **Current status.** NOT_RUN with a real provider. The existing 'graph consensus' is an aggregation over council answers; the preprocessing 'GoT' graph is a decision trace built after the fact and changes nothing.

### Council / judge / critic — `research_council_judge_critic`

* **Purpose.** Identify the task classes where a council, judge or critic beats the single-model baseline, and the conditions under which the added cost and latency buy a benefit.
* **Hypothesis.** On cases with measured solo headroom, a role-diverse council with a protective-minority veto lowers the critical-miss rate versus the strong single model without raising the false-alarm rate by more than 5 percentage points.
* **Baseline.** Strong single model (condition A of the 2026-11-04 ablation).
* **Dataset / task family.** New governance case set (>= 60 calibration, >= 150 evaluation), admitted only when two human reviewers agree on the answer; run through the product council endpoint so validator agreement and tenant context are measured.
* **Metric.** Critical-miss rate, false-alarm rate, accuracy, cost, latency (paired bootstrap, 2 000 resamples, fixed seed).
* **Budget.** USD 25 hard cap (the full 2026-11-04 run cost USD 0.71 provider-reported over 1 506 distinct calls).
* **Stopping rule.** Strong model >= 85 % on calibration -> NOT_RUN — CEILING; cost cap -> STOPPED — COST_CAP; > 5 % call failures after one retry; completion.
* **Production admission gate.** Critical-miss reduction CI upper bound < 0, false-alarm increase <= 0.05, validator agreement measured; escalation only (never a default path, never global orchestration).
* **Current status.** MEASURED once: REJECTED_ON_THIS_BENCHMARK (ceiling, 70/71). This does not show that councils never work. Follow-up plan prepared, NOT_RUN.

### ReAct (reason + act tool loop) — `research_react`

* **Purpose.** Measure whether tool use reduces the error rate on data-validation and operational tasks compared with text-only reasoning.
* **Hypothesis.** A bounded ReAct loop over read-only tools halves the error rate on data-validation questions compared with text-only answers.
* **Baseline.** Text-only single-model answer; deterministic validator result as ground truth.
* **Dataset / task family.** Data-validation and operational questions answerable from read-only tools (schema, profile, metric, capability status) on synthetic tenants.
* **Metric.** Error rate, tool calls per task, loop-limit hits, cost, latency.
* **Budget.** USD 15 provider cost cap; read-only tools only.
* **Stopping rule.** Cost cap; any write attempt (fails the run); completion.
* **Production admission gate.** Error-rate reduction CI excludes 0; zero write side effects; per-tenant tool grants enforced; loop and budget limits enforced.
* **Current status.** NOT_IMPLEMENTED, NOT_RUN. Natural-language orchestration is a deterministic intent planner with no tool loop.

### Reflexion — `research_reflexion`

* **Purpose.** Measure whether a second attempt after validator feedback produces a measurable improvement over the first answer.
* **Hypothesis.** One reflection step driven by validator findings corrects at least 30 % of first-attempt validator failures without introducing new failures in more than 5 % of cases.
* **Baseline.** First attempt; a plain retry without feedback.
* **Dataset / task family.** Report narration and interpretation tasks where the evidence validator flags unsupported or contradicted claims.
* **Metric.** Correction rate, new-error rate, validator pass rate, cost and latency of the extra step.
* **Budget.** USD 10 provider cost cap.
* **Stopping rule.** Cost cap; completion; stop early if the first-attempt failure rate on calibration is < 10 % (no headroom).
* **Production admission gate.** Correction-rate CI excludes 0 and new-error rate <= 5 %; the validator, not the model, decides acceptance.
* **Current status.** NOT_RUN. One diagnose-and-retry step is wired (advisory, API only); it is not iterative Reflexion and has not been evaluated.

### Monte-Carlo Tree Search (feature / model strategy) — `research_mcts_feature_strategy`

* **Purpose.** Measure whether MCTS gives a cost-effective advantage over fixed HPO or heuristic search in wide feature and model strategy searches.
* **Hypothesis.** At equal compute budget, MCTS over strategy choices (feature families, encodings, model families) reaches a better locked-test score than the existing heuristic search in at least 2 of 3 public datasets.
* **Baseline.** Existing deterministic strategy search plus the HPO engine at the same compute budget; random search.
* **Dataset / task family.** Public tabular datasets (UCI Adult, Bank Marketing, Diabetes 130-US).
* **Metric.** Locked-test score, compute time, number of evaluated pipelines.
* **Budget.** Compute only (no provider cost); 8 CPU-hours cap.
* **Stopping rule.** Compute cap; completion.
* **Production admission gate.** Score gain CI excludes 0 at equal budget on at least 2 of 3 datasets; no re-implementation of HPO.
* **Current status.** NOT_IMPLEMENTED, NOT_RUN.
