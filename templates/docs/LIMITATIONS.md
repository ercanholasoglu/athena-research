# Limitations

What these experiments do not show. Each study README repeats the limits specific to it. The reports carry the
complete lists:

- [FINAL_RESEARCH_REPORT.md](../harness/rs2610/FINAL_RESEARCH_REPORT.md)
- [FRONTIER_REPLICATION_REPORT.md](../harness/rs2610/FRONTIER_REPLICATION_REPORT.md), sections 9–10

## Scope

- **Models.**
  - One local model, `qwen2.5:7b`.
  - Two hosted models from the cheaper tiers, `gpt-6-luna` and `claude-sonnet-5-5`. Sonnet ran in B2 only, with
    1 replicate.
  - Nothing here speaks to either provider's top tier: the pre-registered `gpt-6.1-sol` and `claude-opus-5-5` arms
    could not be run ([HISTORY](HISTORY.md)).
- **Decisions.** Bounded AutoML decisions with closed option sets and rule-defined correct answers (A, A2). Semantic
  judgements against a hand-built truth (B, B2). Results need not transfer to open-ended tasks.
- **Orchestrations.** One implementation each of CoT, ToT and GoT, with one wording and one set of caps. Other
  designs could behave differently. "Topology never helps" is not claimed.
- **Datasets.** Public tabular datasets: 9 unseen in Study A, 8 in Study B, 4 in A2 and B2. `bank_marketing` was a
  Study B development dataset. Per-dataset effects are not claimed.

## Statistics

- **Small B2 samples.** B2 has 8 units per cell, or 4 for Sonnet, and Holm across 10 cells is strict. Most large B2
  differences are therefore descriptive. With 4 units, no Sonnet effect can reach significance, and a degenerate
  interval such as [{{r.x.capability.B2.SONNET.all_traps_blocked.ci_lo|pp}}, {{r.x.capability.B2.SONNET.all_traps_blocked.ci_hi|pp}}] reflects 4 identical unit differences, not certainty.
- **Non-significance is not equivalence.** No test here supports a claim that two arms are equal.
- **Cross-study comparison is ordinal.** Its effect sizes use different metrics and scales.

## Measurement

- **Hidden reasoning.** Hosted DIRECT calls include provider-side reasoning the caller cannot see. A2 compares
  orchestration, not reasoning against no reasoning.
- **Hosted sampling.** It cannot be seeded, so replicates are independent samples. A provider can change a model
  behind the same id; the resolved id is recorded per call, but no digest is exposed.
- **Costs.** They come from published prices applied to ledger token counts, not from invoices. JEV cost is UNKNOWN.
- **Latency.** Study A/B latency was affected by host suspend (post-freeze finding). Latency figures are indicative
  only.
- **Token caps.** Study B's caps bound on the widest unseen dataset (post-freeze finding, reported, not fixed).
- **"Understanding".** The tests measure behaviour consistent with semantic understanding. They do not show that any
  model understands the data.

## Reproduction

- **Raw data is not redistributed.** If a public source changes, the frozen frame hash will not match. The
  verification reports this as SOURCE_CHANGED rather than hiding it; see [DATASETS.md](DATASETS.md) for the status at
  release time.
- **Private development history.** Commit ids in the freeze records point into a private development history. File
  identity is established by the SHA-256s in the records, not by those commits.
- **JEV is not reproducible end to end.** Its harness ran inside the private product and is not published. Its
  evidence files, their derivation into the article facts, and the per-case rows for C/D/E are public; per-call
  requests are not ([research/jev](../research/jev/README.md#what-is-not-public)).
- **The B2 data-cache incident** forced a scoped freeze verification for the last 5 local B2 runs
  ([HISTORY](HISTORY.md#the-disk-full-and-data-cache-incident-b2-qwen257b)).
