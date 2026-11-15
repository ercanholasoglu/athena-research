# Council ablation — results (2026-11-04)

Pre-registration: `PREREGISTRATION.md` (commit `b70ccd264`, pushed before any call).
Amendments: `AMENDMENTS.md` (1: Claude 5.5 accepts only T = 1; 2: 186 answers truncated
at 300 tokens re-asked with 1 024). Raw data: `evidence/answers.jsonl` (1 210 member calls),
`evidence/judge.jsonl` (110 judge calls), `evidence/results.json` (all numbers below).
Harness: `scripts/research/council/run.py`; cases: `scripts/research/council/cases.py`.

## Decision (pre-registered rules, evaluation split n = 71)

| Condition | Members | Accuracy | Δ vs strong solo [95 % CI] | Critical miss | Calls | Tokens / decision | Latency s | Cost $ / decision | Decision |
|---|---|---|---|---|---|---|---|---|---|
| A strong solo | sonnet | 0.986 | — | 0.019 | 1 | 432 | 2.31 | 0.00199 | baseline |
| A (cheap solo) | haiku | 0.986 | +0.000 [0, 0] | 0.019 | 1 | 490 | 1.77 | 0.00013 | — |
| B1 same provider, roles | verifier, domain, critic | 0.972 | −0.014 [−0.042, 0] | 0.019 | 3 | 1 786 | 2.43 | 0.00049 | **REJECTED** |
| B2 same provider, sampling | haiku ×3 (T = 1) | 0.972 | −0.014 [−0.042, 0] | 0.019 | 3 | 1 459 | 2.10 | 0.00038 | **REJECTED** |
| C multi-provider | sonnet, haiku, qwen7b | 0.986 | +0.000 [0, 0] | 0.019 | 3 | 1 187 | 2.71 | 0.00212 | **REJECTED** |
| D characteristic-diverse | sonnet, haiku_verifier, qwen7b | 0.972 | −0.014 [−0.042, 0] | 0.019 | 3 | 1 344 | 2.72 | 0.00218 | **REJECTED** |
| E judge-only | Sonnet judges C | 0.986 | +0.000 [0, 0] | 0.019 | 4 | 1 927 | 5.26 | 0.00490 | **REJECTED** |
| F adaptive routing | route | 0.972 | −0.014 [−0.042, 0] | 0.019 | 3.35 | 1 501 | 3.07 | 0.00203 | **REJECTED** |

Cost is the provider-reported cost (litellm); local Qwen calls are 0. Latency for a council
is the slowest member plus the judge where used.

**Hypotheses.** H0 (council does not materially outperform the best solo) — **not rejected**.
H1 (value concentrates in ambiguity / high-consequence segments) — **not supported**: no
segment gain; on the 9 ambiguous cases B1, D and F lose 1 case (−0.111). H2 — **descriptively
supported, confounded** (below). H3 (adaptive routing gives a better frontier) — **rejected**:
F is less accurate than C and uses more tokens, because every high-consequence case is
sent to council D; 36 / 71 decisions were escalated to human review.

**Persisted decision for `council_ablation_research`: REJECTED — on this benchmark.**

## What the result does and does not say

* **Ceiling effect — the main limitation.** The strong solo answers 70 / 71 evaluation cases
  correctly. The largest gain any council could show is +0.014, so the REJECTED rule
  ("upper CI bound of the gain < 0.02") is met by construction. The experiment shows that
  *on single-answer governance questions that a frontier model already answers, a council
  adds cost and no accuracy*; it cannot show whether a council helps on problems a frontier
  solo gets wrong. That needs a harder case set with measured solo headroom (≥ 15 % solo
  error) before any new claim. Recorded as a research gap, not hidden.
* **The single solo error is a debatable item.** `feature_screening:29`
  (`days_since_last_purchase`, churn on a snapshot date) — reference answer REVIEW (the
  reference date is unstated), constructed by the case author. Every member answered OK
  except `haiku_critic` and `qwen1_5b` (which answers REVIEW on almost every case: false-alarm rate 0.88). A reader may reasonably disagree with the reference.
* **Validator agreement and organization-context use were not measured.** The harness calls
  models directly; it does not go through Athena's council endpoint, Validator or tenant
  context. The result is about model ensembles on Athena-shaped questions, not about the
  product's council feature end to end.

## Behavioural characteristics (main analysis: failure characteristics, not provider names)

| Member | Acc. | Critical miss (permissive) | False alarm (conservative) | Ambiguous acc. | Truncated at 300 tok (verbosity) | Format failures |
|---|---|---|---|---|---|---|
| sonnet | 0.986 | 0.019 | 0.000 | 0.89 | 8 | 0 |
| haiku | 0.986 | 0.019 | 0.000 | 0.89 | 20 | 0 |
| haiku_verifier | 0.958 | 0.019 | **0.059** | 0.78 | **44** | 0 |
| haiku_domain | 0.972 | 0.019 | 0.000 | 0.78 | 21 | 0 |
| haiku_critic | 0.986 | **0.000** | 0.000 | **1.00** | 31 | 0 |
| qwen7b | 0.620 | 0.315 | 0.235 | 0.56 | 0 | 2 |
| qwen1_5b | 0.282 | 0.111 | **0.882** | 0.78 | 0 | 0 |

* **Role prompts change failure characteristics, not just accuracy.** The verifier role is the
  most conservative (only member with false alarms among Claude members) and the most
  verbose; the semantic-critic role is the only member with zero critical misses and the only
  *discriminating* member that answered the ambiguous `days_since_last_purchase` case as REVIEW
  (qwen1_5b did too, but it flags almost everything).
* **Error correlation.** sonnet and haiku have identical error vectors (phi = 1.0); the
  critic's errors are uncorrelated with both (phi ≈ −0.01). The verifier and domain roles
  are highly correlated with each other (0.81).
* **H2 (descriptive, 35 three-member combinations).** Council gain over the best member
  correlates strongly with the double-fault rate (Spearman −0.83) and weakly with provider
  count (−0.18) or mean error phi (+0.07). Two-provider combinations average −0.056 vs
  −0.004 for one-provider ones — but the only second provider available here (local Qwen)
  is far weaker, so provider count is confounded with member strength. Read as: *adding a
  different provider is not a substitute for adding a member who is right where the others
  are wrong*; not as evidence about any specific vendor.
* **Mechanism finding (EXPLORATORY, not pre-registered).** The one discriminating member that
  avoids the critical miss (the critic, in B1) is outvoted two to one by plurality. On this data the aggregation rule, not membership,
  discards the useful dissent. A "protective minority veto" (any calibrated critic voting
  REVIEW/LEAKAGE/PROXY forces review) is a hypothesis for the next pre-registration — it
  is untested here and not claimed.
* **Reproducibility.** haiku vs haiku_repeat (two independent samples at the enforced T = 1):
  110 / 110 identical answers.

## Economics summary

Relative to the strong solo, always-on councils cost 3–4 calls, 2.7–4.5× tokens, up to 2.3×
latency (judge) and up to 2.5× provider cost for no accuracy gain on this set. The cheapest
equally accurate configuration is a solo Haiku (0.986 at $0.00013 / decision, 15× cheaper
than Sonnet).

## Next step (recorded on the roadmap, not started)

A follow-up pre-registration with (1) a case set chosen for measured frontier-solo headroom,
(2) the product's council endpoint so Validator agreement and tenant context are measured,
(3) a third provider family if keys become available, and (4) the protective-minority-veto
aggregation as an explicit condition.
