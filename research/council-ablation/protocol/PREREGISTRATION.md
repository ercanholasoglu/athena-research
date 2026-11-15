# Council ablation — pre-registration

Written and committed before any evaluation call. Hypotheses, conditions,
splits, metrics and decision rules are fixed here; anything added after the
results is labelled EXPLORATORY.

**Research question:** *When* does a Council add value over a strong solo model, and *why*?
Council superiority is not assumed.

## Hypotheses (as specified in the brief)

* **H0** — Council does not materially outperform the best solo model.
* **H1** — Council's main value appears in ambiguity, disagreement, missing-context and high-consequence failure segments rather than average-case performance.
* **H2** — Provider diversity alone is not sufficient; complementary model characteristics matter more.
* **H3** — Adaptive Council routing provides a better quality / cost / latency frontier than always-on Council.

## Tasks

Every case is a closed-answer Athena reasoning problem with one correct option.
Ground truth comes from public dataset documentation (PaySim, UCI Bank Marketing,
Titanic3, Lending Club, UCI Adult, Statlog German Credit, Diabetes 130-US, IBM
Telco) or, for constructed scenarios, from the rule stated inside the case
(target definition, policy text, numbers given). No label is produced by a model.

Families: `feature_screening` (leakage, proxy, semantic ambiguity, clean, decoys —
column-level), `target_interpretation`, `missing_source`, `policy_conflict`,
`model_selection`, `validation_interpretation`, `xai_interpretation`,
`fe_suggestion`, `high_consequence`.

Each case is tagged with a **difficulty** (`easy`, `adversarial`, `ambiguous`),
a **consequence** (`high` for decisions about people / deployment / policy,
else `normal`) and its **permissive** options (the answer that lets a risky
input or decision through). A case whose correct answer is not permissive is a
*protective* case.

## Split

Within each family, every third case (index % 3 == 0) is **calibration**; the
rest is **evaluation**. Calibration is used only to pick the strong solo
baseline and the characteristic-diverse council. All comparisons are reported
on evaluation.

## Members

Providers reachable from the research machine: Anthropic (Claude Haiku 5.5,
Sonnet 5.5) and local Ollama (Qwen 2.5 7B and 1.5B, Q4_K_M). OpenAI/Gemini keys
are not available — a ≥ 3-vendor comparison is **not** possible and is not
substituted. Members (one cached answer per case):

| member | model | T | perspective |
|---|---|---|---|
| sonnet | Sonnet 5.5 | 0 | neutral |
| haiku | Haiku 5.5 | 0 | neutral |
| haiku_repeat | Haiku 5.5 | 0 | neutral (reproducibility probe) |
| haiku_s1..s3 | Haiku 5.5 | 0.8 | neutral (sampled) |
| haiku_verifier | Haiku 5.5 | 0 | conservative verifier |
| haiku_domain | Haiku 5.5 | 0 | domain expert |
| haiku_critic | Haiku 5.5 | 0 | semantic critic |
| qwen7b | Qwen 2.5 7B | 0 | neutral |
| qwen1_5b | Qwen 2.5 1.5B | 0 | neutral |

## Conditions

* **A strong solo** — the t = 0 neutral member with the highest calibration accuracy. Every member's solo result is also reported.
* **B same-provider council** — B1: {haiku_verifier, haiku_domain, haiku_critic} (roles); B2: {haiku_s1, s2, s3} (sampling). Plurality.
* **C multi-provider council** — {sonnet, haiku, qwen7b}. Plurality.
* **D characteristic-diverse council** — among 3-member combinations of {sonnet, haiku, haiku_verifier, haiku_domain, haiku_critic, qwen7b, qwen1_5b} whose members each reach calibration accuracy ≥ 0.5, the one with the lowest mean pairwise error correlation (phi on error indicators; tie → lower double-fault rate) on calibration. Plurality.
* **E judge-only** — Sonnet 5.5 judges the three C answers (option, confidence, reason) and decides.
* **F adaptive routing** (fixed rule, not tuned):
  1. NORMAL → haiku's answer, when haiku and qwen7b agree and the case is not high-consequence;
  2. DISAGREEMENT → the E judge;
  3. PERSISTENT_AMBIGUITY → council D, when the judge's confidence is < 0.6;
  4. HIGH_CONSEQUENCE → council D, and the case is counted as *escalated to human review*.
  Tokens, calls and latency count only the calls the route actually needs.

Plurality ties: highest mean confidence among tied options. An unparseable
answer is an abstention (does not vote; wrong when solo).

## Metrics (evaluation split; 95 % bootstrap CIs, 2 000 paired case resamples)

* **Quality:** accuracy overall, per family, per difficulty, per consequence; macro-F1 on `feature_screening`.
* **Safety:** critical miss rate = protective case answered with a permissive option; false-alarm rate = permissive-truth case answered with a wrong protective option.
* **Council value (vs strong solo):** correction rate (solo wrong → condition right), new errors introduced (solo right → condition wrong), disagreement resolution rate (cases where members disagree → condition right), segments improved / degraded.
* **Economics:** calls, tokens, provider-reported cost (UNKNOWN when the provider does not report it — never estimated), latency (parallel members = slowest + judge), retries.
* **System quality:** format failures, reproducibility (haiku vs haiku_repeat agreement). Validator agreement and organization-context use are **not measured** here (the harness calls models directly, not through the Athena product path); stated, not substituted.
* **Characteristics per member (derived from behaviour, not labels):** permissiveness (critical misses) vs conservatism (false alarms), literal vs inferential (easy vs adversarial accuracy), leakage sensitivity, verifier strength (`validation_interpretation`), quantitative strength (`model_selection`), ambiguity handling (`ambiguous` accuracy), pairwise error correlation.

## Decision rules (persisted to roadmap item `council_ablation_research`)

Per condition, against the strong solo baseline:
* **SUPPORTED** — paired accuracy-gain CI excludes 0 on evaluation and critical miss rate is not higher.
* **CONDITIONAL_VALUE** — not SUPPORTED, but the gain CI excludes 0 on a pre-registered segment (ambiguous, adversarial or high-consequence), or (F only) quality within 0.03 of the best always-on council at ≤ 50 % of its tokens.
* **REJECTED** — upper CI bound of the overall gain < 0.02 and no segment gain supported.
* **INSUFFICIENT_EVIDENCE** — anything else.

Hypothesis readings: H0 rejected iff any always-on council is SUPPORTED. H1 supported iff segment gains are supported while the overall gain is not (or segment gains exceed the overall gain with segment CIs excluding 0). H2 is assessed by comparing C (provider diversity) with D (characteristic diversity) and by the association, over all 3-member combinations, of council gain with error correlation vs provider count. H3 supported iff F's quality is within the always-on councils' CIs at materially lower tokens/latency.

## Declared limitations

Case count is modest (CIs will be wide); two provider families; the harness
measures models on Athena's reasoning tasks, not the product's council endpoint;
local models are quantised; the case author is also the harness author.

## Freeze record

Committed before any evaluation call (2026-11-04). SHA-256 at freeze:

* `scripts/research/council/cases.py` — 7c488dd95fba79656e5999b9b637a0a1fc587840a165ae58e8e4f8af77f1f0ef
* `scripts/research/council/run.py` — 79a5967271b3cdcf7bb654f23db52cfb1c3715ac924934f39dc3c9abf484c28b

Any later change to either file is listed in `AMENDMENTS.md` with its reason, before results are read.
