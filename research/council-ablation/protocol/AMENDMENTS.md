# Amendments to the pre-registration

## Amendment 1 — 2026-11-04, before any result was read

**Trigger.** The first collection run (10 rows, discarded) returned
`UnsupportedParamsError`: Claude Haiku 5.5 and Sonnet 5.5 accept only
`temperature=1`; 0.0 and 0.8 are rejected by the provider. Verified by a probe
of both models at T ∈ {0.0, 0.8, 1.0}.

**Change.**
1. Every Claude member and the judge run at T = 1 (`CLAUDE_T`). Qwen members keep T = 0.
2. Consequences, stated up front:
   * `haiku`, `haiku_repeat` and `haiku_s1..s3` now share one configuration; they are
     five independent samples of Haiku at T = 1. B2 (sampling council) is unchanged
     in meaning; the "deterministic vs sampled" contrast in the pre-registration no
     longer exists and is not reported.
   * The reproducibility metric (haiku vs haiku_repeat) now measures sampling
     agreement at the provider-enforced temperature, not run-to-run determinism.
   * The strong solo baseline and all councils with Claude members carry sampling
     noise; this widens the CIs and is reported as a limitation.
3. Harness robustness: a provider/transport error is re-asked on the next run instead
   of being cached as final. Scoring is unchanged — an unparseable completed answer is
   still an abstention.

No case, condition, metric, split or decision rule changed. The 10 discarded rows were
not analysed.

## Amendment 2 — 2026-11-04, after collection, before any accuracy was computed

**Trigger.** A format audit of the 1 210 collected answers (no scoring) found 189
without a parseable answer. 186 had exactly 300 output tokens: the members reasoned
in prose before emitting the JSON, and the harness budget (`max_tokens=300`) cut them
off. By member: haiku_verifier 44, haiku_critic 31, haiku_domain 21, haiku 20,
haiku_repeat 18, haiku_s1 16, haiku_s2 14, haiku_s3 14, sonnet 8. That is a harness
budget artefact, not a model's inability to answer.

**Change.**
1. `MAX_TOKENS = 1024` for every call (members and judge).
2. Only calls that produced no parsed answer **and** used the full 300-token budget are
   re-asked (186 rows). Every other row ended naturally under 300 tokens, so a larger
   budget would not have changed it.
3. The parser is unchanged (strict). The 3 non-truncated failures (qwen7b: option text
   instead of the key; two JSON blocks after a self-correction) remain abstentions.
4. The pre-amendment file is kept as `evidence/answers_budget300_archive.jsonl`. The
   truncation rate at 300 tokens is reported per member as a *verbosity* characteristic.

Because Claude runs at T = 1 (Amendment 1), each re-asked row is a fresh sample.
