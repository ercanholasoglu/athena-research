# rs2610 replication phase: Study A2 and Study B2 (pre-registration)

Status: **written before any frontier-model evaluation run**, frozen in `outputs/replication/FREEZE_RECORD_A2B2.json`
together with every source file, prompt hash, dataset hash and configuration it describes. The original Study A
(freeze `1b87f101`) and Study B (freeze `90af81fe`) are not modified, re-run or re-analysed. Their results stay the
historical record. A2/B2 are later evidence.

## 1. Question

The original studies used one local model, `qwen2.5:7b` at temperature 0.4. Each finding has a competing
explanation that this phase tests.

- **Study A** found no detectable accuracy benefit from CoT, ToT or GoT, at 3.9× to 12.1× the compute. The competing
  explanation is that a 7B model cannot exploit richer reasoning structure. **A2** asks whether topology matters more
  when the underlying model is substantially stronger.
- **Study B** found that dictionaries and rules helped leakage blocking and semantic accuracy. It could not show
  feature *invention*: 97.8 % of proposals copied an offered candidate. **B2** asks whether a stronger model uses data
  semantics to make better decisions and invent valid features, or only produces more plausible language.

## 2. Models

| Arm | Provider | Requested id | Reasoning | Sampling | Status at freeze |
|---|---|---|---|---|---|
| Baseline | local Ollama | `qwen2.5:7b` (digest `845dbda0…`) | none | temperature 0.4, seed = replicate | A2: frozen Study A runs reused; B2: new runs |
| Frontier 1 | OpenAI Responses API | `gpt-6.1-sol` | `reasoning.effort = medium` | temperature / top_p / seed NOT_CONFIGURABLE | available |
| Frontier 2 | Anthropic Messages API | `claude-opus-5-5` | `output_config.effort = medium` (thinking always on) | NOT_CONFIGURABLE | **blocked: the account has no API credit** (400 "credit balance is too low", 2026-10-29). Harness ready; the arm runs unchanged if credit is added. Otherwise it is reported INCOMPLETE. |

**Model choice.** The OpenAI flagship is `gpt-6-astra` and the most capable Claude is `claude-fable-5-1`, both at
$10 / $50 per MTok. Neither was chosen. `gpt-6.1-sol` ($2 / $10) and `claude-opus-5-5` ($4 / $20) are each
provider's newest main reasoning tier at comparable prices. The owner set a hard budget of $25 for the frontier arms.
A result from these models does not speak for the top price tier; the limitations section says so.

**Recording.** Every call records the provider-returned model id, request id, response id, input, output, reasoning
and cached tokens, client-side wall latency, stop reason and computed cost. See `replication/providers.py`.

## 3. Fairness

The following are identical across models:
- datasets and frozen splits;
- evidence packets and profiles (built by frozen code);
- task wording and system prompts (frozen code);
- output schemas;
- answer keys and scoring;
- topology execution;
- statistics.

Unavoidable provider differences are recorded per call.

1. **Sampling parameters.** Neither frontier API accepts temperature, top_p or seed. Replicate k is an independent sample.
2. **Reasoning.** Both frontier models reason before answering, and that reasoning is not visible. The baseline has no
   reasoning. A frontier "DIRECT" call is therefore a single call with hidden provider-side reasoning, not a
   no-reasoning call. The topologies still differ in what is executed: one call versus five, isolated branch
   evaluation, and a graph with deterministic propagation.
3. **Token caps.** Provider `max_tokens` bounds reasoning plus visible output. Each frozen visible cap is sent as
   `frozen_cap + 16000`.
4. **Structured output.** The frozen schemas are sent in strict JSON-schema mode after `strict_schema()`, which adds
   `additionalProperties: false` and nothing else.
5. **Latency.** Frontier latency is client-side wall time, including network and queueing. Baseline latency is the
   server's prefill and decode time. The two are never combined in one ratio.
6. **Cost.** Neither API returns cost. It is computed from the usage block and the published prices (table in
   `providers.py`). The baseline is `NOT_APPLICABLE_LOCAL` and is never written as 0.

## 4. Frozen subsets (chosen by coverage, before any frontier result)

**A2: 4 UNSEEN Study A datasets, 64 decision instances.**
- `iranian_churn`, `taiwan_default` and `diabetes_readmission` carry all ten decision families. They also carry
  **all eight adversarial variants**: governance/policy block, calibration conflict, causal-vs-predictive
  disagreement, incomplete evidence, indistinguishable options, cheaper equivalent, variance uncertainty and suspicious
  data quality.
- Together these three datasets hold all 24 adversarial instances of the original study.
- `online_shoppers` adds a fourth domain (e-commerce) with base instances only.
- Coverage:
  - model-family selection;
  - validation strategy;
  - calibration and thresholding;
  - conflicting CV/holdout evidence (`variance_uncertain`, `calibration_conflict`);
  - a governance constraint;
  - ambiguous evidence (`indistinguishable`, `incomplete_evidence`);
  - causal-vs-predictive conflict.
- Excluded:
  - `coil_caravan`, because its token caps bound in Study B and it has no adversarial variants;
  - `card_fraud_synth`, because it is synthetic;
  - `thyroid_sick` and `image_segment`, which have few families;
  - `hillstrom_email`, which has one instance.
- Composition: 40 base + 24 adversarial instances. Governance block has 3 instances, so it is still not testable
  alone; see §6.
- Replicates: 1, 2 and 3 for the frontier models. The baseline is the frozen Study A UNSEEN runs, seeds 1, 2 and 3,
  on the same instances.

**B2: 4 datasets × 10 cells × 2 replicates.**
- `iranian_churn`: churn (Study B UNSEEN).
- `taiwan_default`: credit/default (Study B UNSEEN).
- `bank_marketing`: bank marketing / cross-sell, with the natural post-call leak `duration`. This dataset was a Study B
  **DEVELOPMENT** dataset, so the Study B harness was developed on it. That favours none of the B2 models, which are all
  new to it, but it is disclosed.
- `hillstrom_email`: randomized e-mail experiment; causal/actionability (Study B UNSEEN).

Every dataset carries the frozen Study B traps:
- the identifier `record_key`;
- a post-outcome column;
- the warehouse artifact `load_weekday`.

It also carries one new trap, the **target-derived** `segment_outcome_rate`. This is a micro-segment outcome rate
computed on the whole extract, including the row's own label (`replication/b2/variants.py`).

Cells, identical for all datasets and models:

| # | Variant | Condition | Tests |
|---|---|---|---|
| 1 | trapped | A_RAW | meaningful column names, no dictionary |
| 2 | trapped | B_SELF | self-inference stage |
| 3 | trapped | C_DICT | correct dictionary |
| 4 | trapped | D_RULES | dictionary + rules |
| 5 | trapped | E_FULL | rules + verification stage |
| 6 | anonymized | A_RAW | anonymized columns, no dictionary (floor) |
| 7 | anonymized | C_DICT | anonymized columns, correct dictionary |
| 8 | incomplete | D_RULES | definitions of ids, leaks and target removed |
| 9 | misleading | D_RULES | 3 false entries |
| 10 | misleading | E_FULL | 3 false entries, verification stage |

The identifier, post-outcome, artifact and target-derived traps are present in every cell. The
predictive-vs-causal lever (`intervention_column`) is scored in every cell.

False entries come from the frozen `MISLEAD` table (taiwan, bank) and from `B2_MISLEAD` (iranian, hillstrom), which
was written now in the frozen pattern: two entries the profile contradicts and one post-outcome column disguised as a
harmless attribute.

**Per run:** the frozen Study B pipeline (pre-stage where the condition has one, analysis, FE with candidate
judgements). Then **one independent feature-invention call**. It shows no candidate features, no examples and no
earlier output; only the profile, the target summary, the condition's documentation and the task
(`replication/b2/invention.py`).

## 5. Data safety (B2/A2 content sent to external APIs)

Only public research datasets are used:
- UCI 563 (Iranian churn), UCI 350 (Taiwan default), UCI 296 (Diabetes 130-US hospitals, a de-identified public
  release), UCI 468 (online shoppers), UCI 222 (bank marketing): UCI ML Repository, CC BY 4.0;
- MineThatData e-mail test (Hillstrom): published for public analysis.

What is sent:
- column names;
- aggregate statistics (min/median/max, category labels with shares, univariate association);
- data-dictionary text written for the studies;
- evidence packets of aggregated CV results.

**No raw rows are sent.** No customer data, proprietary data, production data, secrets or Athena credentials are
sent. The OpenAI key comes from the owner's account and is read from a local `0600` file at run time; it is never
logged. OpenAI calls use `store=false`.

## 6. Hypotheses and analysis (A2)

**Unit and metric.** The pair is (instance, replicate). Accuracy is the frozen `study_a.scoring.score_run` `correct`.
A truncated or failed run counts as wrong, as in Study A.

- **A2-W, within-model topology.** For each frontier model: the six pairwise accuracy contrasts, exact McNemar, Holm
  across the six. Effect with a 95 % CI from an instance-cluster bootstrap (10,000 resamples). Four datasets are too
  few clusters, so instances are resampled with their replicates.
- **A2-M, model effect.** Frontier vs baseline per topology. McNemar on pairs matched by instance and replicate index,
  Holm across the four topologies.
- **A2-I, model × topology interaction.** For T ∈ {COT, TOT, GOT}:
  DiD_T = (acc_T − acc_DIRECT)<sub>frontier</sub> − (acc_T − acc_DIRECT)<sub>baseline</sub>, on instance-level means.
  Test: sign-flip permutation over the 64 instances (100,000 draws). CI: instance bootstrap. Holm across the three.

Decision rules:

| Hypothesis | Supported when |
|---|---|
| H1: topology does not meaningfully help at either capability level | no A2-W contrast vs DIRECT significant in favour of structure, and no A2-I significant |
| H2: stronger models exploit ToT/GoT | A2-I significant and positive for TOT or GOT |
| H3: capability raises accuracy, topology adds little | A2-M significant and positive while H1 holds |
| H4: topology helps only on constrained/adversarial decisions | descriptive, plus exploratory McNemar on the 24 adversarial instances within each model; labelled exploratory |
| H5: complex reasoning improves policy compliance, not decision accuracy | descriptive. On governance_block, policy compliance (decision ≠ the forbidden `neural_net`) is reported separately from correctness. 3 instances × 3 replicates per cell, minimum attainable exact p 0.25, so untestable |
| H6: the GoT representation improves but the final call still ignores the graph | GoT fidelity (final decision = graph top-ranked option, frozen `analyze.fidelity`) frontier vs baseline, Fisher exact on runs (exploratory), plus graph metrics (claims, edges, conflicts, reused claims, merges) |

Never claimed:
- equality from a non-significant test (bounds are reported instead);
- per-dataset significance.

**Also reported:**
- calibration (ECE, mean confidence);
- consistency (share of instances whose three replicates agree);
- abstention;
- evidence utilization;
- contradiction handling;
- regret where measured;
- input, output, reasoning (OpenAI) and total tokens;
- calls;
- client wall latency;
- cost;
- accuracy per 1k output tokens (reasoning included; visible-only reported too where the provider reports reasoning
  tokens);
- accuracy per dollar.

## 7. Hypotheses and analysis (B2)

**Unit.** (dataset, replicate): 8 per cell per model.

**Metrics.** Frozen `study_b.score.score` against the B2 truth: core semantic accuracy (frozen `CORE`), id / leak /
artifact flags, `all_traps_blocked` (now including the target-derived column), lever actionable vs predictive trap,
`falsified_detected_recall` (cells 9–10), `missing_semantics_recall` (cell 8) and candidate-judgement accuracy. New B2
metrics:
- `target_derived_caught`: the column was blocked by any analysis field.
- Invention classes from `replication/b2/evaluate.py`: VALID_USEFUL / VALID_NOT_USEFUL / INVALID_HIGH_APPARENT /
  INVALID_LOW_GAIN / NOT_EXECUTABLE, as shares per run and counts.
- Novelty: the share of invented specs that differ from every frozen Study B candidate recipe.
- Self-assessment honesty: the share of features the model rated `leakage_assessment = none` that the validator found
  leaky.
- Downstream: the shipped model = all columns − blocked + executable invented features not self-rated "likely" leaky.
  `deploy_collapse` = leak inflation > 0.05 (frozen definition). Deployed-score gap to the oracle-clean model.

**Contrasts.**
- **B2-M, model effect per cell.** Exact sign test over the 8 units, Holm across the 10 cells within each metric.
- **B2-S, semantic effect within model.** C_DICT, D_RULES and E_FULL vs A_RAW on trapped, and anonymized C_DICT vs
  anonymized A_RAW. Wilcoxon signed-rank and exact sign test, Holm across the 4 within each metric.
- **B2-X, model × semantics.** DiD (D_RULES − A_RAW) and (C_DICT − A_RAW), frontier − baseline. Sign-flip
  permutation over units.

**Feature QUALITY vs EXPLANATION.**
- Quality = validator classes and the downstream result.
- Explanation = rationale completeness and self-assessed leakage, compared with the validator.

"Semantics improved explanation but not quality" is stated only when the quality metrics show no detected
improvement while the explanation metrics do.

**Wording.** Behavioural only. The strongest permitted phrasing is "behaved consistently with semantic understanding
under these tests". "Understands" is never used.

## 8. Cross-study question

What makes an AI system better at tabular decisions: model capability, reasoning structure or semantic context?

Three effect sizes are reported side by side, with their CIs:
- **Capability:** frontier − baseline. A2, DIRECT, accuracy. B2, A_RAW, core semantic accuracy and all traps blocked.
- **Structure:** best non-DIRECT topology − DIRECT, within each model, A2.
- **Semantics:** D_RULES − A_RAW within each model, B2.

The scales differ (decision accuracy vs semantic-decision accuracy). The comparison is ordinal and stated as such.

## 9. Integrity rules

- Freeze before any frontier evaluation run. `python -m rs2610.replication.freeze --verify` is run before and after
  every run.
- A defect found after the freeze is documented in `replication/JOURNAL.md` and not patched.
- The budget guard refuses any call that could exceed the cap. A run stopped this way is reported INCOMPLETE.
- Pre-freeze smoke calls are in `artifacts/replication/smoke/` and excluded from analysis:
  - A2: one DEVELOPMENT instance;
  - B2: `telco_churn`, which is not a B2 dataset.
- Analysis code is written after the freeze, to this plan. Any deviation from the plan is listed in the report as a
  deviation.

## Amendment 1 (2026-10-29, before any run of the amended arm)

**Change.** The OpenAI frontier arm changes from `gpt-6.1-sol` to **`gpt-6-luna`**: Responses API, `reasoning.effort =
medium`, $0.10 / $0.50 per MTok (published price, accessed 2026-10-29). This is the owner's decision after the
organisation's prepaid credit ran out partway through the `gpt-6.1-sol` runs.

**Superseded data.** The partial `gpt-6.1-sol` runs (A2: 20 complete rows, B2: 6) and their ledgers are kept as
`*.superseded_sol.jsonl`. They are excluded from every analysis and listed in the report as a superseded pilot.

**Consequence for the question.** `gpt-6-luna` is OpenAI's lowest-cost tier, not its strongest model. A2/B2 with this
arm therefore test a current low-cost reasoning model against a 2024 7B open model. They do not test the provider's top
capability, and every conclusion is worded that way.

**Unchanged.** Everything else in this document: datasets, cells, prompts, schemas, scoring, statistics and budget
caps.

## Amendment 2 (2026-10-29, before any run of the amended arm)

**Anthropic arm.** It runs **`claude-sonnet-5-5`**, `output_config.effort = medium`, $2 / $10 per MTok. Scope is
**B2 only, replicate 1** (40 runs), with a hard cap of $4.50. The owner added $5 of credit; Opus 5.5 would need about
$27 for A2+B2.

**A2 Anthropic arm.** Not run; reported INCOMPLETE.

**Schema adaptation.** Anthropic's JSON-schema mode rejects array `minItems` / `maxItems`, so `strict_schema()`
drops them for that provider only. The prompts still state the bounds, and the analysis keeps at most the frozen
`maxItems` items (first k) for every model.

**Analysis.** The Sonnet B2 arm has 4 units per cell (one per dataset). Its contrasts are reported as descriptive
effects with dataset-level detail. No Holm verdicts are claimed for it.

**Pre-run smoke.** `telco_churn` (not a B2 dataset), misleading × E_FULL + invention: all calls parse, $0.09
(`artifacts/replication/smoke/ledger_b_anthropic.jsonl`).

**OpenAI arm.** The owner added credit ($5.78 balance). Amendment 1 (`gpt-6-luna`) stands.
