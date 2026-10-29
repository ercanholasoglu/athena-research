# History: freezes, amendments and incidents

The full, time-stamped record is in the two journals, which are published as written except for five phrases, listed at
the end of this page: four named where a credential was stored or a private scratch path (each replaced in place with
"NOT PUBLIC"), and one named the tool behind an unrelated process on the same Ollama server:

- [`harness/rs2610/JOURNAL.md`](../harness/rs2610/JOURNAL.md): Studies A and B, 2026-10-27 to 2026-10-28
- [`harness/rs2610/replication/JOURNAL.md`](../harness/rs2610/replication/JOURNAL.md): A2 and B2, 2026-10-29

Commit ids in the freeze records refer to the private development repository in which the harness was written. That
history is not public. The harness files here are byte-identical to the frozen sources: the freeze records hold their
SHA-256s, and `python -m rs2610.replication.freeze --verify` (run from `harness/`) recomputes them.

## Protocol

Each study was developed on development datasets only, then frozen. The freeze record hashes the source files, every
rendered prompt, the model digest or id, every loaded dataset frame and split, and the configuration. Unseen
datasets were run once, after the freeze, with `freeze --verify` before and after. Changes after a freeze are either
recorded as amendments (before the amended arm ran) or reported as post-freeze findings; nothing was silently edited.

## Timeline

| when | event | before evaluation of the affected arm? |
|---|---|---|
| 2026-10-27 22:46 | Study B frozen (first record) | — |
| 2026-10-27 22:52 | Study B first freeze **superseded**: contract defect in the feature-engineering stage found on development data. Kept as [`superseded_v2/FREEZE_RECORD_B_v1.json`](../harness/rs2610/artifacts/study_b/superseded_v2/FREEZE_RECORD_B_v1.json) | yes: no unseen run had happened |
| 2026-10-27 23:26 | Study B frozen again ([`FREEZE_RECORD_B.json`](../harness/rs2610/outputs/FREEZE_RECORD_B.json), commit `90af81fe`) | — |
| 2026-10-28 ~12:34 | Study B unseen runs complete | — |
| 2026-10-28 12:41 | Study A frozen ([`FREEZE_RECORD_A.json`](../harness/rs2610/outputs/FREEZE_RECORD_A.json), commit `1b87f101`) | — |
| 2026-10-28 ~13:00 | Post-freeze finding, Study B: token caps bind on the widest unseen dataset. Reported, not fixed | after; reported as a limitation |
| 2026-10-28 ~13:20 | Post-freeze finding: host suspend leaked into server-side timers. Latency only | after; latency marked unreliable |
| 2026-10-28 22:29 | Study A unseen complete ({{design.A.UNSEEN.runs|int}} runs); freeze verified before and after | — |
| 2026-10-29 11:02 | A2/B2 frozen ([`FREEZE_RECORD_A2B2.json`](../harness/rs2610/outputs/replication/FREEZE_RECORD_A2B2.json); harness commit `8d9f0c7c5e`, record committed in `3299b015`) | — |
| 2026-10-29 ~11:05 | First `gpt-6.1-sol` pilot calls; the OpenAI account hit a **billing stop** after $0.85. Refused rows quarantined in `*.billing_refused.superseded_sol.jsonl`, pilot rows in `*.superseded_sol.jsonl`; both excluded from every result | — |
| 2026-10-29 11:13 | **Amendment 1**: OpenAI arm `gpt-6.1-sol` → `gpt-6-luna` ([record](../harness/rs2610/outputs/replication/FREEZE_RECORD_A2B2_AMENDMENT1.json)) | yes: before any `gpt-6-luna` run |
| 2026-10-29 11:23 | **Amendment 2**: Anthropic arm `claude-opus-5-5` → `claude-sonnet-5-5`, B2 only, 1 replicate; Anthropic schema bounds adapted ([record](../harness/rs2610/outputs/replication/FREEZE_RECORD_A2B2_AMENDMENT2.json), governing) | yes: before any Sonnet run |
| 2026-10-29 | A2 `gpt-6-luna` {{r.design.a2.LUNA.runs|int}}/{{r.design.a2.LUNA.runs|int}}, B2 `gpt-6-luna` {{r.design.b2.LUNA.runs|int}}/{{r.design.b2.LUNA.runs|int}}, B2 `claude-sonnet-5-5` {{r.design.b2.SONNET.runs|int}}/{{r.design.b2.SONNET.runs|int}} complete | — |
| 2026-10-29 ~12:50–15:10 | **Disk full and data-cache deletion** during the local `qwen2.5:7b` B2 run (below) | B2 qwen at 75/80 |
| 2026-10-29 ~16:00 | B2 `qwen2.5:7b` complete, {{r.design.b2.QWEN.runs|int}}/{{r.design.b2.QWEN.runs|int}} | — |
| 2026-10-29 evening | Analyses, cross-study comparison, reports | after all runs |

Why the amendments happened: the pre-registered hosted models could not be run. The OpenAI account stopped billing
during the `gpt-6.1-sol` pilot, and the Anthropic account did not have credit for the planned `claude-opus-5-5` arm.
Each amendment is a complete new freeze record that names the record it amends and its reason, and each was written
before the first call of the arm it changes. The original record was never rewritten. The cheaper replacement models
are a limitation: nothing here speaks to either provider's top tier.

## The disk-full and data-cache incident (B2, `qwen2.5:7b`)

1. The host disk filled while the local B2 run was going. At 75 of 80 runs, a ledger write failed with
   `OSError: [Errno 28] No space left on device` and the run stopped. Afterwards: 75 run rows, 75 unique keys, no
   partial lines. The call whose ledger write failed was never cached, so on resume that one call was sampled again;
   its run row had never been written, so no scored row was affected. All hosted arms were already complete.
2. While space was being freed, the whole user cache directory was deleted, including the raw-data cache the frozen
   loaders read. No copy was found (Trash, Spotlight; the backup disk was not mounted).
3. With the author's explicit approval, only the datasets the B2 runner and evaluator read were downloaded again from
   their public sources: UCI 350 (`taiwan_default`), 222 (`bank_marketing`), 125 (`coil_caravan`, loaded at import),
   then UCI 563 (`iranian_churn`) and the MineThatData Hillstrom file. Each source URL and raw-file SHA-256 was
   written to the journal before verification.
4. **The restored datasets were verified against the frozen loaded-frame, split, truth and prompt hashes before
   the run continued.** The frozen functions recomputed, for every B2 dataset: rows, columns, frame hash, holdout
   scheme, development and test index hashes, the B2 frame and truth hashes, and the rendered analysis, invention and
   candidate hashes of all 10 cells (38 checks each), plus `coil_caravan` against the Study A and B records: 160 of
   160 matched. All 22 frozen source files matched the governing record. Nothing in the harness, prompts, splits,
   preparation or loaders was changed.
5. The run resumed for the 5 missing keys only and completed at 80/80. The post-run check passed again.
6. **Deviation.** The pre-registration requires the full `freeze --verify` before and after every run. It could not
   run for these resumes, because it also loads datasets that B2 does not use and that were not restored. The scoped
   check above was run instead. No A2 run took place after the deletion. In this public repository the full verify
   can be run again once every dataset is prepared (`tools/prepare_data.py`). **At release, after all runs, it was:**
   all 15 datasets were prepared from their public sources and verified (14 MATCH, 1 GENERATED, none
   SOURCE_CHANGED), and `freeze --verify A`, `--verify B` and `replication.freeze --verify` all reported FREEZE OK.
   This confirms the frozen inputs after the fact. It does not replace the missing verify-before-run, which stays a
   recorded deviation.

## Evaluation nondeterminism

Found while preparing this release, on 2026-10-29, after all runs and analyses.

1. **The first clean-clone test.** It recomputed every Study B and B2 feature and downstream evaluation from
   scratch, because the evaluation cache was not yet part of the repository. The regenerated tables differed from
   the published ones:
   - 261 of 9367 Study B fact values changed, and 73 of 7941 B2 values.
   - Continuous scores moved by about 0.001 (median); threshold- and sign-derived quantities moved by a step on
     small cells.
   - No Holm-adjusted p-value crossed 0.05.
   - Three article-cited values changed in the third decimal.
2. **Release stopped.** The release was not pushed.
3. **Cache published.** The evaluation records the published analyses actually read (957 of 1000; the 43 others are
   pre-freeze Study B development evaluations) were added to the repository as a documented reproducibility
   artifact with a per-record manifest. The published results were not overwritten by the recomputation.
4. **Check added.** `tools/trace_cache_reads.py --check` now proves, on every reproduction, that each evaluation is
   served from those records and none is recomputed.

Details and the exact drift: [REPRODUCIBILITY](REPRODUCIBILITY.md#evaluation-cache). The finding is also recorded
in the replication journal.

## Other recorded changes

- Development-phase fixes to Study A scoring, GoT token caps and the GoT claim-resolution stage were all made before
  the Study A freeze (journal, 2026-10-27 22:54 and 23:35).
- A record-keeping correction (2026-10-28 22:50): `superseded_v1` holds 16 runs, not 10. No measurement affected.
- The URL list used for the restore was originally kept in a private staging script. In this repository it is
  [`tools/datasets.py`](../tools/datasets.py), with the same URLs.

## Changes to published harness files

| file | original phrase (paraphrased) | published as |
|---|---|---|
| `JOURNAL.md` | API keys empty in the local environment file (named) | "the local environment file (NOT PUBLIC)" |
| `JOURNAL.md` | a temporary chaining script (path) | "a temporary chaining script, NOT PUBLIC" |
| `JOURNAL.md` | the tool behind an unrelated benchmark on the same Ollama server (named) | "another process" |
| `replication/JOURNAL.md` | the local environment file (path) whose key value was empty | "the local environment-file value (NOT PUBLIC)" |
| `replication/JOURNAL.md` | the hosted environment (host name) the key was copied from | "the owner's hosted environment file (NOT PUBLIC)" |
| `.gitignore` (harness) | ignored the whole evaluation cache | the two published cache folders are tracked |

No credential appeared in either journal. The original files' SHA-256s are listed in
[`REDACTIONS.json`](REDACTIONS.json).
