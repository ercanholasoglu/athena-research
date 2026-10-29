# rs2610 replication (A2/B2) journal

Times are Europe/Istanbul.

## 2026-10-29: setup, before the freeze

- **Owner decisions:** OpenAI + Anthropic frontier arms, a hard $250 cap later lowered by the owner to about $25, and
  medium reasoning effort. The original Study A/B code and results are not touched.
- **Article drafts:** the editorial rewrite of article A done earlier this session is parked in
  `~/Desktop/atropos/blog/5/editorial-parked/`. All article drafts were restored to their template state (parity
  PASS), per the A2/B2 brief.
- **Model discovery (provider model-list endpoints):**
  - OpenAI lists `gpt-6.1-sol`, `gpt-6.1-terra`, `gpt-6-astra` (flagship) and `gpt-6-luna`.
  - Anthropic lists `claude-opus-5-5`, `claude-fable-5-1` and `claude-sonnet-5-5`.
  - Prices were taken from developers.openai.com/api/docs/pricing (accessed 2026-10-29) and the Anthropic model table.
- **Chosen models:** `gpt-6.1-sol` and `claude-opus-5-5` (PREREGISTRATION §2).
- **OpenAI key:** the local environment-file value (NOT PUBLIC) was empty. With the owner's explicit approval, the key was
  copied from the owner's hosted environment file (NOT PUBLIC) into `~/.config/rs2610/openai.key` (mode 0600, outside every repository).
- **Anthropic: BLOCKED.** The shell's ANTHROPIC_API_KEY returns 400 "Your credit balance is too low"
  (`req_011CgWALM7zdQfLoSMerZMN8`). The owner decided to proceed with OpenAI only for now. The Anthropic arm is ready
  but not run.
- **Pre-freeze smoke (excluded from analysis, `artifacts/replication/smoke/`):**
  - A2: `gpt-6.1-sol` on one DEVELOPMENT governance instance (DIRECT, GOT), plumbing verified, $0.02.
  - B2: `telco_churn`, misleading × E_FULL + invention on `gpt-6.1-sol` ($0.07), and invention on qwen2.5:7b (52 s).
  - Both strict JSON-schema paths parse.
- **Validator fix before the freeze:** `count_positive` / `gt_threshold` / `eq_value` were first mapped onto frozen
  ops whose type rules reject ordinal inputs (for example a count of delayed months on Taiwan `PAY_*`). They are
  condition tests, so they are now valid unless an input is barred. Changed before any B2 evaluation run.
- **Budget split:** A2 $14, B2 $9, smoke < $0.2.

## 2026-10-29 ~11:05: after the freeze, first runs

- **Freeze and launch.** `FREEZE_RECORD_A2B2.json` was written at commit `3299b015`; the verify passed, and the
  original A and B freezes are OK. Launched A2 OpenAI (8 workers), B2 OpenAI (6 workers) and B2 local qwen2.5:7b. The
  host was on battery; the owner was asked to plug in.
- **OpenAI billing stop.** After about 3 minutes, every OpenAI call returned 429 "You have no credits remaining". The
  organisation behind the key ran out of prepaid credit after this phase had spent $0.85 in total (A2 $0.41, B2
  $0.35, smoke $0.10). This is a billing refusal, not a model outcome.
- **Response.** Both OpenAI runs were stopped at once. Run rows with any billing-refused call were **moved, not
  deleted**, to `runs_openai.billing_refused.jsonl` (A2: 19 rows, B2: 5 rows). Scoring them as wrong would record a
  billing event as a decision error.
- **Deviation note.** The pre-registered rule "a failed run counts as wrong" covers model-side failures (parse,
  truncation). Billing refusals are excluded and re-run when credit exists. The request cache holds only successful
  calls, so a re-run repeats only the refused calls.
- **Frozen harness.** Nothing in it was changed.
- **Local qwen B2 run.** It continues; it is unaffected.

## 2026-10-29 ~11:20: amendment 1, OpenAI arm moved to gpt-6-luna

- **Decision.** The owner chose `gpt-6-luna` for all A2/B2 frontier runs.
- **Credit check.** A 1-call check with `gpt-6-luna` also returned 429 "no credits remaining", so the runs wait for a
  credit top-up.
- **Superseded `gpt-6.1-sol` data.** Moved to `*.superseded_sol.jsonl`; nothing was deleted.
- **Pricing table.** `gpt-6-luna` was added to `providers.PRICES`.
- **Freeze.** The freeze is amended (`--amend`) before any Luna run; the original record is untouched.

## 2026-10-29 ~11:30: amendment 2, Anthropic arm = claude-sonnet-5-5, B2 only, 1 replicate

- **Credit.** The owner added $5 to the Anthropic account and $5.78 to the OpenAI organisation.
- **Waiter guard.** The waiter saw the OpenAI credit at 11:22 and refused to launch, because the freeze verify reported
  drift: the pending Sonnet price edit to `providers.py`. That is the guard working as intended.
- **First Anthropic smoke.** It returned 400 "For 'array' type, property 'maxItems' is not supported" on the FE and
  invention schemas. Fixed in `strict_schema()` for Anthropic only.
- **Second smoke.** All calls parse; a full B2 run costs about $0.07–0.09 on Sonnet, so 80 runs would exceed $5. The arm
  is therefore set to 1 replicate (owner chose Sonnet B2 only).
- **Freeze.** Amended before any Sonnet or Luna run.

## 2026-10-29 ~12:50–15:10: disk full (ENOSPC), raw-data cache deleted, partial restore

- **ENOSPC.** The host disk filled twice while the local qwen2.5:7b B2 run was going. The first time the run kept
  going. The second time, at 75/80 rows, `common/llm.py:append_line` raised `OSError: [Errno 28] No space left on
  device` while writing a **ledger** record, and the run stopped. Checked afterwards: 75 run rows, 75 unique keys, no
  partial lines in `runs_local.jsonl` or `ledger_local.jsonl` (229 records, all valid JSON). The call whose ledger write
  failed was never cached, so on resume that one call is sampled again rather than replayed; its run row was never
  written, so no scored row is affected. A2 (Luna), B2 Luna and B2 Sonnet were already complete and are unaffected.
- **Cache deletion.** While disk space was being freed on the host, the whole of `~/.cache` was removed, including
  `~/.cache/athena-research-ablation/raw/` and `~/.cache/athena-decision-corpus-v2/`. No copy was found in the Trash
  or via Spotlight, and the Time Machine disk was not mounted. The first resume stopped at import (`coil2000/dictionary.txt`
  missing) before any model call.
- **Restore (owner-approved: UCI 350, 222, 125 only).** Downloaded from the canonical UCI pages listed in
  `stage_public.py`; only the files the loaders read were put back:

  | dataset | source | archive SHA-256 | restored file | file SHA-256 |
  |---|---|---|---|---|
  | taiwan_default | https://archive.ics.uci.edu/dataset/350 (`/static/public/350/default+of+credit+card+clients.zip`) | `56c885f84457f6680f8438f02bfcdac9579323d8a94465ee5f26e32baa727602` | `raw/taiwan_default/default of credit card clients.xls` | `30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933` |
  | bank_marketing | https://archive.ics.uci.edu/dataset/222 (`/static/public/222/bank+marketing.zip`) | `e0bf5f5de5b846e2f18e9d90606637267d46dfa260e0f17bb12e605db5efbeb4` | `athena-decision-corpus-v2/222.zip` (archive as-is) | same |
  | coil_caravan | https://archive.ics.uci.edu/dataset/125 (`/static/public/125/insurance+company+benchmark+coil+2000.zip`) | `f5b5b1be439e0d8a058628d5a06e2851300dfa5be5fae968403907fb2e770720` | `raw/coil2000/dictionary.txt`, `raw/coil2000/ticdata2000.txt` | `0b971c07…2b1ef`, `5d5bdca1…43723` |

- **Freeze match.** The freeze records hold loaded-frame and split hashes, not raw-file hashes, so the raw SHA-256s
  above are recorded here for the first time. Verification recomputed the frozen quantities with the frozen functions
  (`replication.freeze.frame_sha`, `holdout_split`, `b2_base`, prompt renderers):
  - taiwan_default: 38/38 match against `FREEZE_RECORD_A2B2.json` (rows, columns, `frame_sha256` `74098e6f…a0f5`,
    holdout scheme, dev/test index, `b2_frame_sha256`, `b2_truth_sha256`, and analysis/invention/candidate hashes for
    all 10 cells). **PASS**
  - bank_marketing: 38/38 match (`frame_sha256` `4a1325e2…3099`). **PASS**
  - coil_caravan (not in A2/B2; loaded at import by `common/data.py`): rows, columns, `frame_sha256` `6f667453…cf25`
    and `truth_sha256` match both `FREEZE_RECORD_A.json` and `FREEZE_RECORD_B.json`. **PASS**
  - Amendment 1 and 2 records carry dataset entries identical to the base record. All 22 frozen source files match
    the amendment 2 record. Nothing in the frozen harness, prompts, splits, preparation or loaders was changed; the
    `coil2000` import-time load was left in place.
- **Second blocker.** The resume after the restore stopped again before any model call: the frozen runner prepares all
  four B2 datasets up front (`replication/b2/run.py:62-66`), and B2 evaluation loads each one too
  (`replication/b2/evaluate.py:48`), so `iranian_churn` (UCI 563) and `hillstrom_email` (MineThatData) are also
  required. They were outside the approved restore, so the run is paused at **75/80** pending the owner's decision.

## 2026-10-29 ~15:45: restore of the remaining two B2 datasets (owner-approved)

- **Sources and raw SHA-256** (recorded before verification):

  | dataset | source | archive SHA-256 | restored file | file SHA-256 |
  |---|---|---|---|---|
  | iranian_churn | https://archive.ics.uci.edu/dataset/563 (`/static/public/563/iranian+churn+dataset.zip`) | `696c3a1812267980751f30d19193a1b430ac4ad76172bb089e664c96813ead66` | `raw/iranian_churn/Customer Churn.csv` | `90d5fb6bd1630cd4de4b4d28fcf8b4cb92a8f6ab7484605b0799d47386f7dbe1` |
  | hillstrom_email | https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html → `http://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv` | (plain CSV) | `raw/hillstrom/h.csv` | `0e5893329d8b93cefecc571777672028290ab69865718020c78c7284f291aece` |
- **Freeze match.** Recomputed with the frozen functions against `FREEZE_RECORD_A2B2.json`, for all four B2 datasets
  together: iranian_churn 38/38 (`frame_sha256` `9a9dce53…93ea`), taiwan_default 38/38, bank_marketing 38/38,
  hillstrom_email 38/38 (`frame_sha256` `e8f021c5…6baf`), covering rows, columns, frame, holdout scheme, dev/test
  index, B2 frame, B2 truth and the analysis/invention/candidate hashes of every cell; coil_caravan 4/4 against the
  Study A and B records. **PASS** (160/160). Scratchpad downloads deleted after verification; only the loader inputs
  remain in `~/.cache`. The qwen B2 run resumes for the 5 missing keys only.

## 2026-10-29 ~15:45–16:00: qwen B2 complete (80/80)

- **Resume.** The run added only the 5 missing keys (taiwan_default misleading D_RULES/E_FULL r2; bank_marketing
  trapped A_RAW/B_SELF/C_DICT r2), `exit 0`, "done". The runner only appends, so the 75 existing rows were left
  as they were. Final: 80 rows, 80 unique keys, 0 invention failures (2 analysis-trace failures, both in rows written
  before the disk-full event), ledger 240 records.
- **Post-run check.** All four B2 datasets 38/38 and coil 4/4 against the freeze records, and all 22 frozen source
  files match the amendment 2 record: PASS.
- **Deviation (§9 "verify before and after every run").** The full `python -m rs2610.replication.freeze --verify` could
  not be run for these resumes: it also loads the A2-only datasets (`diabetes_readmission`, `online_shoppers`) and,
  through the original A and B verifies, all 14 Study A/B datasets, most of which were deleted with `~/.cache` and
  were not restored (the owner approved restoring only what B2 needs). The scoped check above uses the same frozen
  functions and covers every input the B2 runner and evaluator read, plus every frozen source file. It does not
  cover the A2-only datasets, but no A2 run happened after the deletion.
- **Other arms.** A2 gpt-6-luna 768/768, B2 gpt-6-luna 80/80 and B2 claude-sonnet-5-5 40/40 were complete before the
  event and were not re-run.

## 2026-10-29 evening: analysis, report, articles

- **B2 analysis.** The first run stopped after 22 min on a transient `PermissionError` writing `artifacts/cache/b2_eval`
  (the same host file-access revocation documented in `common/llm.py`). No output was written. A re-run reusing the
  cached evaluations completed and regenerated all seven `b2-*.csv`. The A2 tables were already newer than the last A2
  run and the last `a2/analyze.py` change, so they were not regenerated.
- **Cross-study (§8).** Added `replication/cross.py` → `outputs/replication/cross-study.csv` and registered it in
  `make_facts` as `r.x.*`.
- **Report.** `replication/make_report.py` assembles `FRONTIER_REPLICATION_REPORT.md` from `replication/report/`, and an
  unknown key fails the build. The three original-study numbers in §1 are now fact keys, not typed text.
- **Articles.** Blog 5 and 6, EN and TR, were updated and remain drafts. Parity PASS; trace PASS (157 and 152 keys).
  Nothing was committed, pushed, published or deployed.

## 2026-10-29 ~17:40: public release build, full freeze verification after the fact

- **Data.** For the public research repository all 15 datasets were prepared from their public sources with
  `tools/prepare_data.py` (the 10 not restored earlier were downloaded; the 5 restored ones were kept). The
  frozen-function check (`tools/verify_data.py`) reported MATCH for all 14 file-based datasets and GENERATED (hash
  checked) for `card_fraud_synth`. No dataset had SOURCE_CHANGED.
- **Full verify.** On the public copy of the harness (byte-identical to the frozen sources), `freeze --verify A`,
  `freeze --verify B` and `replication.freeze --verify` all reported FREEZE OK, with the local Ollama `qwen2.5:7b` at the
  recorded digest. This is the full verification that §9 required and the 15:45–16:00 resumes could not run. Run after
  all runs, it confirms that the inputs of every frozen study are still reproduced exactly. It does not replace the
  missing verify-before-run, which stays recorded as a deviation.
- **Prompt identity, corrected wording.** Replaying the ledgers showed that only the first call of a ToT, GoT, B_SELF
  or E_FULL run is byte-identical across models. Later calls embed each model's own earlier outputs, and ToT
  selection also embeds the enum of surviving branches. The system prompt, stage and token cap are identical. The
  public docs state it this way.
