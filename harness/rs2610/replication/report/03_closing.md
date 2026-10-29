## 8. Cross-study: capability, structure or semantics?

Effect sizes side by side (`outputs/replication/cross-study.csv`). A2 intervals are instance-cluster bootstraps with
Holm-adjusted McNemar p; B2 intervals are paired bootstraps over (dataset, replicate) units with unadjusted exact sign
p. The scales differ, so only the **order** is compared.

| axis | study, metric | `qwen2.5:7b` | `gpt-6-luna` | `claude-sonnet-5-5` |
|---|---|---|---|---|
| capability (frontier − baseline) | A2, DIRECT accuracy | (baseline) | {{r.x.capability.A2.LUNA.accuracy.effect|pp}} [{{r.x.capability.A2.LUNA.accuracy.ci_lo|pp}}, {{r.x.capability.A2.LUNA.accuracy.ci_hi|pp}}] | not run |
| capability | B2, A_RAW core semantic accuracy | (baseline) | {{r.x.capability.B2.LUNA.core_semantic_accuracy.effect|pp}} [{{r.x.capability.B2.LUNA.core_semantic_accuracy.ci_lo|pp}}, {{r.x.capability.B2.LUNA.core_semantic_accuracy.ci_hi|pp}}] | {{r.x.capability.B2.SONNET.core_semantic_accuracy.effect|pp}} [{{r.x.capability.B2.SONNET.core_semantic_accuracy.ci_lo|pp}}, {{r.x.capability.B2.SONNET.core_semantic_accuracy.ci_hi|pp}}] |
| capability | B2, A_RAW all traps blocked | (baseline) | {{r.x.capability.B2.LUNA.all_traps_blocked.effect|pp}} [{{r.x.capability.B2.LUNA.all_traps_blocked.ci_lo|pp}}, {{r.x.capability.B2.LUNA.all_traps_blocked.ci_hi|pp}}] | {{r.x.capability.B2.SONNET.all_traps_blocked.effect|pp}} [{{r.x.capability.B2.SONNET.all_traps_blocked.ci_lo|pp}}, {{r.x.capability.B2.SONNET.all_traps_blocked.ci_hi|pp}}] |
| structure (best non-DIRECT − DIRECT) | A2, accuracy | {{r.x.structure.A2.QWEN.accuracy.effect|pp}} [{{r.x.structure.A2.QWEN.accuracy.ci_lo|pp}}, {{r.x.structure.A2.QWEN.accuracy.ci_hi|pp}}] | {{r.x.structure.A2.LUNA.accuracy.effect|pp}} [{{r.x.structure.A2.LUNA.accuracy.ci_lo|pp}}, {{r.x.structure.A2.LUNA.accuracy.ci_hi|pp}}] | not run |
| semantics (D_RULES − A_RAW) | B2, core semantic accuracy | {{r.x.semantics.B2.QWEN.core_semantic_accuracy.effect|pp}} [{{r.x.semantics.B2.QWEN.core_semantic_accuracy.ci_lo|pp}}, {{r.x.semantics.B2.QWEN.core_semantic_accuracy.ci_hi|pp}}] | {{r.x.semantics.B2.LUNA.core_semantic_accuracy.effect|pp}} [{{r.x.semantics.B2.LUNA.core_semantic_accuracy.ci_lo|pp}}, {{r.x.semantics.B2.LUNA.core_semantic_accuracy.ci_hi|pp}}] | {{r.x.semantics.B2.SONNET.core_semantic_accuracy.effect|pp}} [{{r.x.semantics.B2.SONNET.core_semantic_accuracy.ci_lo|pp}}, {{r.x.semantics.B2.SONNET.core_semantic_accuracy.ci_hi|pp}}] |
| semantics | B2, all traps blocked | {{r.x.semantics.B2.QWEN.all_traps_blocked.effect|pp}} [{{r.x.semantics.B2.QWEN.all_traps_blocked.ci_lo|pp}}, {{r.x.semantics.B2.QWEN.all_traps_blocked.ci_hi|pp}}] | {{r.x.semantics.B2.LUNA.all_traps_blocked.effect|pp}} [{{r.x.semantics.B2.LUNA.all_traps_blocked.ci_lo|pp}}, {{r.x.semantics.B2.LUNA.all_traps_blocked.ci_hi|pp}}] | {{r.x.semantics.B2.SONNET.all_traps_blocked.effect|pp}} [{{r.x.semantics.B2.SONNET.all_traps_blocked.ci_lo|pp}}, {{r.x.semantics.B2.SONNET.all_traps_blocked.ci_hi|pp}}] |

**Ordinal answer, within these tests:** capability > semantics > structure.
- Capability gave the largest gains on both benchmarks.
- Semantic documentation mattered where names alone were not enough: trap blocking with weak names, and anonymized
  columns (section 7.1). Where the column names were meaningful, a capable model barely needed it for core accuracy.
- Reasoning structure added nothing on the 7B model and cost accuracy on the hosted model.

Bootstrap intervals over 4 or 8 units are coarse, and a degenerate interval such as Sonnet's
[{{r.x.capability.B2.SONNET.all_traps_blocked.ci_lo|pp}}, {{r.x.capability.B2.SONNET.all_traps_blocked.ci_hi|pp}}]
reflects 4 identical unit differences, not certainty.

## 9. Deviations from the pre-registration

1. **Models (amendments 1 and 2).** `gpt-6-luna` replaced `gpt-6.1-sol`, and `claude-sonnet-5-5` replaced
   `claude-opus-5-5` with B2 only and 1 replicate (section 3). Both were recorded before any run of the amended arm.
2. **Billing-refused rows.** Excluded from scoring and moved, not deleted (section 5).
3. **Freeze verify during the last qwen B2 resumes.** §9 of the plan requires `freeze --verify` before and after every
   run. After the raw-data cache was deleted, the full verify could not run: it also loads A2-only and original-study
   datasets that were not restored. A scoped check was run instead, before and after, with the frozen functions: every
   B2 dataset (frame, split, truth and all rendered prompts; 38/38 each), the import-time `coil_caravan` load (4/4
   against the Study A and B records) and all 22 frozen source files against the amendment 2 record. No A2 run took
   place after the deletion.
4. **One re-sampled baseline call.** The disk-full error hit while one qwen B2 call was being written to the ledger.
   That call was not cached and was sampled again on resume. No scored row was written from the lost call.
5. **Section 8 analysis code.** `replication/cross.py` was written after all runs, to the plan. "Best non-DIRECT"
   is chosen by accuracy within each model, as planned.
6. **Descriptive additions not in the plan:** the A2 error decomposition (abstention vs wrong option, with the
   "abstentions neutral" re-reading) and the A2 topology-structure metrics. They are labelled descriptive and change
   no pre-registered verdict.

## 10. What can and cannot be claimed

Supported, within these models, data and contracts:
- A stronger hosted model makes better bounded AutoML decisions when it answers directly.
- Chain, tree and graph orchestration did not improve those decisions at either capability level. On `gpt-6-luna`
  they made them worse, mostly by turning decisions into abstentions.
- With meaningful column names, the hosted models handled most semantic decisions without documentation. A correct
  dictionary was decisive once the names were anonymized.
- Hosted models invented features that were executable and rarely leaky, but these were no more *useful* than the 7B
  model's. Documentation did not change that.
- Behaviour was consistent with semantic understanding under these tests. The study does not show that any model
  "understands" the data.

Not claimed:
- that topology never helps: only these four orchestrations, decisions and models were tested;
- anything about either provider's top tier (section 3);
- equality from any non-significant test;
- any significant Sonnet effect: with 4 units none is attainable;
- per-dataset effects.

**Limitations.**
- There are few B2 units (8, or 4 for Sonnet), and Holm across 10 cells is strict, so most large B2 differences are
  descriptive.
- Hosted "DIRECT" calls include provider-side reasoning that is not visible (section 4), so A2 compares orchestration,
  not reasoning versus no reasoning.
- Hosted sampling cannot be seeded; replicates are independent samples.
- `bank_marketing` was a Study B development dataset.
- Costs come from published prices, not invoices.

## 11. Reproducibility

- **Freeze records:** `outputs/replication/FREEZE_RECORD_A2B2.json` plus amendments 1–2 (sources, prompts, datasets,
  config).
- **Runs and ledgers:** `artifacts/replication/{a2,b2}/runs_*.jsonl` and `ledger_*.jsonl`, with every call's request
  hash, provider model id and usage. Requests are cached by hash, so re-running replays rather than re-samples.
- **Analysis:**

  ```
  python -m rs2610.replication.a2.analyze
  python -m rs2610.replication.b2.analyze
  python -m rs2610.replication.cross
  python -m rs2610.replication.make_configs
  python -m rs2610.replication.make_facts
  python -m rs2610.replication.make_excerpts
  python -m rs2610.replication.make_report
  ```

- **Every number in this report** is a fact key rendered from `outputs/replication/facts-replication.json` (index:
  `facts-replication-index.md`), plus three original-study keys from `outputs/facts.json`. An unknown key fails the
  build.
- **Data:** public sources, listed with URLs and licences in the public research repository (`docs/DATASETS.md`,
  download and hash check: `tools/prepare_data.py`). Raw-file SHA-256s for the restored B2 datasets are in
  `replication/JOURNAL.md`, and loaded-frame hashes are in the freeze records.
- **Spend:** A2 `gpt-6-luna` ${{r.cost.a2.LUNA.usd|2}}, B2 `gpt-6-luna` ${{r.cost.b2.LUNA.usd|2}} and B2
  `claude-sonnet-5-5` ${{r.cost.b2.SONNET.usd|2}}, excluding the superseded `gpt-6.1-sol` pilot.
