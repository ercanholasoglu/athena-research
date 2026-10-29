# Research journal — reasoning topology & semantic intelligence (2026-10)

Append-only. Each entry: hypothesis / experiment / result / interpretation / unexpected / failed run / design change + reason.
Times are local (Europe/Istanbul); entries before 18:40 are approximate (reconstructed from the ledger).

## 2026-10-27 ≈17:45 — Orientation

- **Finding (pre-experiment):** Athena's shipped `council/{chain,tree,graph}_of_thoughts.py` are *post-hoc
  aggregations* of the same N persona answers. They do not change how the model is called: CoT splits
  the reasoning text into steps, ToT scores member answers as branches, GoT links member subgraphs.
  The execution is identical across modes. Benchmarking them would be the "prompt-label" comparison
  the brief forbids. **Design consequence:** Study A builds a research harness
  (`study_a/topologies.py`) in which each topology has different call structure, intermediate
  artifacts and selection mechanics. Production code is not modified.
- **Substrate decision (forced):** the Anthropic key in the shell returns
  `400 credit balance is too low`; `GEMINI_API_KEY` / `OPENAI_API_KEY` are empty in the local environment file (NOT PUBLIC).
  Only local inference is available: Ollama `qwen2.5:7b` (Q4_K_M, digest recorded per call).
  `qwen2.5:1.5b` was rejected after one probe because it switched to Chinese mid-answer.
  Consequence for external validity: results describe a 7B open-weight model, not a frontier model.
  The harness is provider-agnostic so a replication only needs a backend.
- **Throughput measured:** ~25 output tok/s, flat under concurrency (server is single-slot);
  a repeated prompt prefix is KV-cached (prefill 5.2 s → 0.05 s). The design therefore orders all
  calls of one task instance consecutively, with the evidence packet first in the prompt.
- **Temperature / seed:** temperature 0.4 for every mode, seed = repeat index. Locally this is
  reproducible. (On current Claude models non-default temperature is rejected, so a Claude replication
  would measure run-to-run variance without controlling it.)

## 2026-10-27 ≈18:00 — Failed run #1 (infrastructure)

- **What:** first evidence build for `german_credit` crashed in PCA (`n_features=7`).
- **Root cause:** pandas 3 loads text columns as `str` dtype, not `object`. `encode()` tested
  `dtype == object`, so every categorical column went through `to_numeric` and became all-NaN, and
  the imputer silently dropped it. Every mixed-type dataset would have lost its categoricals
  without any error.
- **Fix:** `pd.api.types.is_numeric_dtype`. Verified on all 15 datasets: 0 all-NaN columns.
- **Lesson for the article:** the most dangerous failure in the whole sprint so far was silent, and it
  was in plumbing, not in reasoning.

## 2026-10-27 ≈18:15 — Debug runs (DEVELOPMENT only), failed run #2

- Study A debug (german MODEL_FAMILY, two `data_quality_suspicious` instances): all four topologies run, and their
  structures differ as designed (CoT 4-step strict chain; ToT 3 branches / 6 leaves / 1 pruned; GoT 7 claims,
  3 claims reused by several candidates, 1 claim conflict, so a DAG and not a tree). **Unexpected:** GoT's final call chose
  `random_forest` while its own propagation ranked `catboost` first. Added metric: *topology fidelity*, i.e. whether the final
  decision follows the structure's own ranking.
- Study B debug (german, A_RAW and E_FULL): **failed run #2**. The E verification stage hit its 1400-token cap and
  returned truncated JSON (parse failure). CoIL (86 columns) would overflow self-inference the same way.
  **Design change:** terse per-column fields (<10 / <15 words) and caps of 3200 tokens for inference/verification,
  1500 for analysis, 1800 for FE. The caps are identical wherever a stage exists. Reason: an infrastructure limit, not
  tuning toward a result. Changed on DEVELOPMENT before any UNSEEN run.
- **First substantive observation (exploratory):** under A_RAW, with no dictionary, the model already
  flagged `record_key` (id), `sent_to_collections` (post-outcome) and `load_weekday` (artifact), because the names
  give them away. This is why T1 (anonymized columns) is needed to separate names from documentation. It also labelled german credit
  `business_problem = demand_forecast` in both conditions, with the dictionary present.
- Contention: while the CPU-bound evidence build runs, decode speed drops from ~25 to ~8-15 tok/s. Latency
  measured in these debug runs is not representative; main runs start after the evidence build finishes.

## 2026-10-27 ≈18:35 — Failed run #3 + an external contention source

- **Failed run #3 (evidence build):** `MLPRegressor((64, 32), …)` passed the tuple as the first positional parameter, which is
  `loss`, not the hidden layers. It crashed on the first regression dataset (bike). The classifier happened to work. Fixed with
  keyword arguments for both; the build resumed (telco/german/bank/adult kept; their classifier MLPs were correct).
  The background job reported exit 0 because the pipe's exit code was `grep`'s. Logs now use `--line-buffered` and I check them
  directly.
- **External contention:** another process (a different project, `tools/llm_benchmark.py`) is benchmarking a
  *different* model on the same Ollama server. `ollama ps` showed our model `Stopping...` with a foreign context size.
  Every switch forces a model swap, so wall-clock latency includes time spent waiting for someone else's work. Not my process,
  so I did not stop it.
  **Design change:** latency is now the server-reported compute time (prefill + decode), ACTUAL from Ollama. Queueing and model
  loads are excluded by construction. Wall time is kept as `wall_latency_s` and marked as contaminated. Rows written earlier
  are backfilled from the ledger by request hash.

## ~18:50 — failed run #4 and #5 (infrastructure)
* Evidence build died on `vehicle_silhouettes` (first multiclass dataset): L1 feature selection used `liblinear`, which is
  binary-only in sklearn 1.9. Fix: one-vs-rest wrapper, feature kept if any class coefficient is non-zero. Binary datasets
  are unaffected (same code path); their evidence files are not rebuilt.
* Study B DEV grid died after 10/43 runs with `PermissionError` on its own ledger (the traceback also could not read source
  lines, so the whole worktree was briefly unreadable to the background process — an environment event, not a code bug;
  the file is writable afterwards). Runs resume from `runs_dev.jsonl` and the LLM cache, so no completed run is redone.

## ~19:10 — design defect found in DEVELOPMENT: blind enums (Study B) — fixed before freeze
* Symptom (exploratory dev analysis of 10 runs): `business_problem = demand_forecast` in 8/10 runs although the free-text
  `target_meaning` was correct in every one ("the customer has churned", "high credit risk", "subscribed a term deposit").
* Cause: the JSON schema constrains enum fields (business_problem, prediction_unit, temporal_structure, primary_metric,
  split_strategy, model_family, hpo_depth, B_SELF column role, FE leakage_assessment), but the prompt never listed the allowed
  values. Grammar-constrained decoding then forces the model onto whichever allowed string its tokens drift into. This measured
  the harness, not the model. B_SELF scored better partly because its inference stage restated the meaning in prose first.
* Probe (4 calls, ledger kept in `artifacts/study_b/superseded_v1/enum_probe_ledger.jsonl`): with the allowed values shown,
  telco and german under A_RAW and C_DICT all give the correct problem, unit, split and metric.
* Fix: `conditions.enum_legend(schema)` appends "ALLOWED VALUES" for every enum in the schema of every call, identically in
  every condition. Study A already lists every option id in its prompt; GoT's relation/polarity enums are named in the task text.
* The 10 superseded runs are kept (`superseded_v1/`), excluded from every analysis. Study B DEV restarts from zero.
* Also found by the dev analysis: the scored metric `split` collided with the column `split` (DEVELOPMENT/UNSEEN) and was
  overwritten; renamed `split_correct`.

## ~20:00 — state at session pause (usage limit)
* Study B DEVELOPMENT (corrected harness): 42/43 runs written; the chain then starts Study A DEVELOPMENT automatically
  (a temporary chaining script, NOT PUBLIC). Evidence build continues for the remaining UNSEEN datasets (10/14 done).
* Added before freeze (no UNSEEN data exists yet): `freeze.py` (--write / --verify; source, prompt, contract, dataset hashes);
  Study A analyzer: per-family paired tests (EXPLORATORY, Holm), topology-complexity figure, token totals; Study B analyzer:
  candidate-judgements.csv, stability, semantic-confidence reliability, per-dataset table, input tokens + calls in cost figure.
* NOT YET DONE: dev analyses of both studies; `make_docs`; `freeze --write`; pre-registration commit; UNSEEN runs (A seeds 1-3,
  B seeds 1-2 grid all), each preceded and followed by `freeze --verify`; report, figures, blog (site source located at
  ~/Desktop/atropos: blog/N/{en,tr}/*.md + scripts/build_jev_bounded_decisions.py pattern + scripts/check_blog.sh).

## ~22:05 — failed run #6 (infrastructure) and robustness fix
* Study A DEVELOPMENT stopped after 40 runs with the same transient `PermissionError` on its ledger (third occurrence;
  each coincided with the controlling session being suspended). Fix: `common/llm.append_line` retries a JSONL append with
  backoff for up to 30 min; both runners use it for run rows; jobs run under a restart wrapper (runners resume from disk
  and the LLM cache, so a restart never duplicates or alters a completed run). No prompt, scoring or topology change.
* Study B DEVELOPMENT complete: 43/43 runs. Evidence build complete: 14/14 datasets.

## ~22:30 — Study B DEVELOPMENT analysis (exploratory): two evaluation defects fixed before freeze
* Validator gap: on bike_sharing, C_DICT proposed `mean(season, cnt)` (a feature built from the target) and the Athena
  validator retained it: it only checked blocked columns, own leakage assessment and CV gain, and the target is never in
  the blocked set. Deployment R² fell to −1.33. A truth-free gate can and should refuse any feature reading the target, so
  the rule "uses the target column → reject" was added. The proposal itself is still recorded and counted as a
  target-derived proposal (an embarrassing model behaviour, kept as evidence).
* Aggregation defect: the mean deployment score averaged AUCs with an unbounded R² (bike, −1.33), so one collapsed
  regression run dominated each condition mean (A 0.83 vs C/D/E ≈ 0.38). Headline downstream metrics are now
  `deploy_collapse` (leak inflation > 0.05, i.e. the shipped model loses > 0.05 when deployment hides post-outcome values)
  with cluster-bootstrap CI and the per-run median of `deploy_gap_to_oracle`; per-dataset scores are reported unaggregated;
  paired tests (Wilcoxon, rank-based) also run on the gap and on collapse.
* Genuine dev observation kept as is: D_RULES and E_FULL on bike blocked `instant` but not the post-outcome `casual` /
  `registered`, although both are documented; A_RAW and B_SELF blocked them.

## ~22:46 — Study B FROZEN (commit 90af81fe)
* `outputs/FREEZE_RECORD_B.json` written (sources, rendered prompts for 101 dataset × variant × condition jobs, candidate
  lists, dataset manifest, model digest 845dbda0…, seeds); `freeze --verify B` = OK. The record's `git.head` is the parent
  (f5a2becf) because the record is written before the commit that contains it; the record itself is in 90af81fe.
* Freeze is split per study: Study A's development is still running and is frozen separately after its analysis.
* From here on no Study B prompt, scoring, validator, evaluation or statistics code may change. UNSEEN starts automatically
  when Study A DEVELOPMENT ends (single model slot; sequential keeps server-compute latency uncontaminated).

## ~22:52 — Study B freeze v1 SUPERSEDED before any UNSEEN run (contract defect in the FE stage)
* Found while building derived facts from the DEVELOPMENT analysis, after the v1 freeze (90af81fe) but **before any UNSEEN
  run** (the queued UNSEEN chain was stopped; `runs_unseen.jsonl` never existed). No unseen evidence was seen.
* Defect: `candidate_judgements` was a list with a free-string `id`. The model renamed candidates (`cand_target_mean_A1`,
  `cand_amount_per_month_A2_A13`) or judged only a subset; 47/258 DEVELOPMENT judgements could not be matched to their
  candidate and were scored as wrong. Same class as the blind-enum defect: the contract, not the model, was measured.
* Fix: `conditions.fe_schema(cands)` builds each run's FE schema with one required judgement per offered candidate, keyed
  by its exact id; the prompt says so. Probe (german, A_RAW): 6/6 judged under exact ids.
* Kept as genuine model behaviour (not a defect): the FE stage's own proposals largely copy the offered candidates, including
  ones it rejects in the same response (probe: proposes `cand_key_log`, judges it "reject"). Measured as proposal novelty.
* Superseded v1 freeze record and the 43 DEVELOPMENT runs with the list-shaped contract moved to
  `artifacts/study_b/superseded_v2/` (kept, excluded). Study B DEVELOPMENT is rerun; analysis and pre-stage calls are
  byte-identical and served from the LLM cache, only the FE stage is new. Study A DEVELOPMENT is running concurrently, so
  Study A dev latency in this window is contaminated by contention (dev is exploratory; latency is not used from dev).

## ~22:54 — Study A scoring fix (DEVELOPMENT, before Study A freeze): GoT claim references
* 27/384 final `evidence_refs` in DEVELOPMENT were not evidence ids, all from GoT: its decision stage cites its own claim
  nodes (C4, C6), which rest on evidence. Evidence utilization and contradiction handling counted only `E*` ids, so GoT
  was penalised for referencing its graph. Fix: `scoring.evidence_ids` resolves a cited claim id to the evidence it rests
  on; GoT traces now store `claim_sources`; for runs written earlier they are rebuilt exactly from the ledger (the claims
  call's content, by request hash). The analyzer now rescores every run with the current scorer, so DEVELOPMENT and UNSEEN
  rows are scored by identical code. Effect on DEVELOPMENT (exploratory): GoT evidence utilization 0.72 (CoT 0.77).
* No prompt or topology change. Study A is not frozen yet.

## ~23:30 — Study B DEVELOPMENT rerun complete (keyed FE contract); Study B FROZEN v2
* 43/43 runs, 0 failed calls; 258/258 candidate judgements matched to their candidate (0 missing; v1 had 47 unmatched).
* Exploratory dev observations kept for the record (not hypotheses): bike_sharing post-outcome columns `casual`/`registered`
  not blocked by D_RULES and E_FULL (deployment collapse); B_SELF reaches core semantic accuracy 1.00 on 5 dev datasets.
* `outputs/FREEZE_RECORD_B.json` rewritten (v2). From here no Study B prompt/scoring/validator/evaluation/statistics change.
* Ollama serves requests one at a time (decode 20-24 tok/s unchanged under two clients; wall ≫ compute), so Study B UNSEEN
  can run while Study A DEVELOPMENT finishes without contaminating server-compute latency.

## ~23:35 — Study A DEVELOPMENT: GoT token caps raised; claim-resolution stage-name bug (before Study A freeze)
* 1/41 DEVELOPMENT GoT `edges` calls truncated at its 700-token cap (parse failure → scored wrong); `extract_claims` peaked
  at 609/650. A cap that binds measures the harness, not the topology. Caps raised to 1200 (edges) and 900 (claims). No
  other stage came within 50 % of its cap (CoT max 403/900, ToT evaluate max 244/450, DIRECT max 84/260).
* Bug in the ~22:54 fix: the GoT claims stage is tagged `extract_claims`, not `claims`, so claim sources were never rebuilt
  for earlier runs. Fixed in `analyze.py`. Study B truncation re-checked: 0 in analysis / FE / self-inference; the single
  truncated verify call is failed run #2 (1400 cap, already journaled, cap since 3200).
* Study A DEVELOPMENT process restarted (resumes from disk) so its remaining runs exercise the new caps.

## 2026-10-28 ~12:34 — Study B UNSEEN complete (results not yet read)
116/116 runs (9 UNSEEN datasets x trapped grid + T1/T3/T4 variants x 2 seeds), 0 failed calls. `freeze --verify B` passed
before and after (`FREEZE OK 90af81fe4c`). The machine slept ~10 h overnight (ledger gap 23:4x → 09:5x); the runs paused
and resumed, server-compute latency is unaffected, wall time for that window is not meaningful. Idle sleep now blocked
with `caffeinate -w` on the run processes. **Study B UNSEEN results are deliberately not analysed until Study A is frozen**,
so that nothing seen in Study B's unseen outcomes can inform the Study A freeze.

## 2026-10-28 ~12:40 — Study A DEVELOPMENT complete; exploratory read; Study A freeze
276/276 runs (69 instances x 4 modes, seed 1). 1 failed run: `telco_churn::TRUST_PLAN` GOT, whose `edges` call truncated
at the old 700-token cap before the caps were raised (~23:35); the resumed runner kept that row. It is the only truncated
call in the Study A ledger; UNSEEN uses the raised caps throughout.

Exploratory (DEVELOPMENT, n = 69 instances, seed 1, not confirmatory): accuracy DIRECT 0.841, TOT 0.841, GOT 0.812,
COT 0.754; no pairwise McNemar p below 0.17 before correction. Output tokens per decision ~61 / 297 / 654 / 886
(DIRECT / COT / TOT / GOT); server compute ~3.5 / 14.7 / 31.2 / 45.6 s. GoT abstains most (0.116), TOT never.
These numbers are recorded here **before** any UNSEEN run so they cannot be re-read afterwards; no prompt, topology,
scoring or statistics change follows from them. Hypotheses H1-H4 and their corrections are as in study-a-design.md.
Study B UNSEEN results had not been read at this point.
Study A FROZEN at `1b87f101` (record `outputs/FREEZE_RECORD_A.json`, sources `de92d412c55f`, 170 instance prompts, clean
tree). `freeze --verify B` still OK after the Study A commits (shared harness unchanged). Study A UNSEEN launched:
101 instances x 4 modes x seeds 1-3, verify before and after.

## 2026-10-28 ~13:00 — POST-FREEZE FINDING (Study B UNSEEN): token caps bind on the widest unseen dataset
Found while reading the first Study B UNSEEN analysis (a non-zero `judgements_missing` for A_RAW). Ledger audit of all
Study B UNSEEN calls: exactly 2 truncated calls, both on `coil_caravan` (86 columns, the widest dataset in either split;
widest DEVELOPMENT dataset was narrower), both legitimate long outputs, not repetition loops:
* `coil_caravan / trapped / A_RAW / s1`, stage `feature_engineering`, 1800/1800 tokens: the model listed all 85
  feature columns as `inputs` of each proposed feature. FE stage parse-failed → 0 proposals, 0 of 6 candidate judgements.
* `coil_caravan / trapped / E_FULL / s2`, stage `verify`, 3200/3200: one verdict per documented column (~87) ran out near
  the last column. With no parsed verification, E's analysis prompt is byte-identical to D_RULES s2 and the ledger served
  the same responses — that E run is operationally a D_RULES run. (E_FULL s1 on the same dataset used 3102/3200.)

Decision (made before computing any condition-level comparison that would show which way it cuts):
1. **Not patched.** Raising caps and rerunning these runs would change the frozen harness after seeing UNSEEN outputs.
2. **UNSEEN not invalidated.** The frozen protocol pre-registers parse failures as failures (never as UNKNOWN→0 or
   dropped), and caps are identical across conditions. A rerun of everything would no longer be unseen.
3. Primary (confirmatory) analysis = the frozen analysis, unchanged. An **exploratory sensitivity analysis** excluding
   `coil_caravan` (both seeds, all conditions) is added in a new file (`study_b/sensitivity.py`, not part of the freeze)
   and reported next to the primary result; any conclusion that flips is reported as fragile.
4. Study A UNSEEN (running) gets the same ledger truncation audit; the same rule applies.
This is a limitation of the cap sizing (sized from DEVELOPMENT widths), recorded in the report's harness-defect section.
Sensitivity result (exploratory, `outputs/study_b/study-b-sensitivity.csv`): excluding `coil_caravan` changes the sign of
no confirmatory contrast. Three Holm verdicts at 0.05 flip: E_FULL core accuracy (sig → not), D_RULES leak recall and
D_RULES deploy collapse (not/borderline → sig). Reading: directions are robust, significance at n = 16 pairs is fragile;
the report states the primary result and marks these three as fragile.

## 2026-10-28 ~13:20 — POST-FREEZE FINDING (latency only): host suspend leaked into server timers
While reading the Study B UNSEEN aggregates: A_RAW mean server compute 2,274 s/run, impossible. Ledger scan of every call's
decode rate (median 25.2 tok/s Study A, 23.1 Study B; 1st percentile 17.1 / 9.5): one Study B UNSEEN call
(`iranian_churn / trapped / A_RAW / s2 / feature_engineering`) decoded 782 tokens in 35,308 s — the overnight sleep was
absorbed by the server's eval timer. Seven more calls ran at 3-4.5 tok/s around the suspend/resume (4 Study A
DEVELOPMENT on bank_marketing, 3 more Study B UNSEEN on iranian_churn). Decisions, outputs and tokens are unaffected
(tokens are counted, not timed); only compute time is wrong for these calls.
Handling (reporting layer, `analyze_extra.latency_audit`, outside the freeze; frozen tables untouched): a call with decode
rate < 5 tok/s is HOST_SUSPEND_CONTAMINATED and its compute is **UNKNOWN** (never 0); a run's compute is known only if all
its calls are clean. Reported latency = mean / median over known runs, with n_known
(`outputs/study_*/latency-audit.csv`). The latency columns of `study-b-results.csv` / `study-a-results.csv` are not quoted
anywhere. Wall time was never used as a measurement.

## 2026-10-28 22:29 — Study A UNSEEN complete (1212/1212 runs), freeze verified before and after
`freeze --verify A` printed `FREEZE OK 1b87f101b4` before the run and again after it (`artifacts/study_a/unseen_run.log`).
Analysis = the frozen `study_a.analyze`, unchanged; reporting layer (`analyze_extra`, `make_facts`) rerun.

Ledger audits (same rules as Study B, decided before the run):
* **Truncation:** 1 truncated call in 1212 runs — `card_fraud_synth::TRUST_PLAN / GOT / s1`, stage `edges`, 1200/1200
  tokens. The run is a parse failure and counts as wrong, as pre-registered (the only failed-call run in UNSEEN). One run in
  303 cannot move any Holm verdict (every H1 Holm p is 1.0), so no sensitivity analysis is added.
* **Latency:** 39 calls in 14 runs decode below 5 tok/s → compute UNKNOWN for those runs (n_known 299–300 of 303 per
  mode). Cause, from `pmset -g log` and the ledger timestamps: the battery ran down to 1 % (charger unplugged), the host
  throttled from ~15:58 and was put to sleep by macOS at 16:26 ("Low Power Sleep", 70 min), and resumed at 17:35 on AC;
  the slow calls are 15:58–16:26 and 17:36–17:42. Decisions and token counts are unaffected. `caffeinate -i` cannot
  prevent a critical-battery sleep. The audit's label (HOST_SUSPEND_CONTAMINATED) covers this throttling case too.

Primary result (CONFIRMATORY, `outputs/study_a/study-a-confirmatory.csv`): H1 — no pair of {DIRECT, COT, TOT, GOT} has a
statistically distinguishable accuracy difference (all 6 Holm p = 1.0; accuracies 0.776 / 0.772 / 0.759 / 0.746). H2 and
H3 — not detected (Holm p ≥ 0.91). Their cluster-bootstrap intervals exclude 0 for some contrasts while the pre-registered
exact McNemar tests are far from significant (e.g. H3 COT vs TOT: 0 vs 2 discordant instances, n = 9). This is the
few-cluster anti-conservatism already listed as a threat to validity; the pre-registered test decides. H4 — DIRECT and COT
deliver more accuracy per 1k output tokens than TOT and GOT, all 4 contrasts p < 1/2000 (bootstrap, B = 2000).
DEVELOPMENT → UNSEEN, the exploratory DEVELOPMENT ordering (DIRECT = TOT > GOT > COT) did not replicate.

## 2026-10-28 ~22:50 — Correction (record keeping, no measurement affected): superseded_v1 holds 16 runs, not 10
The ~19:10 entry and the `pre_freeze_excluded` note in FREEZE_RECORD_B (frozen, left unchanged) say "10 superseded
runs". The blind-enum diagnosis was made on the first 10 runs (telco, german × 5 conditions), but the background job kept
going after a restart until it was stopped: `artifacts/study_b/superseded_v1/runs_dev.jsonl` holds 16 runs (plus bank ×
5, adult A_RAW). All 16 ran with blind enums, all are superseded and excluded from every analysis, none is deleted. The
report and articles quote the count from the file (`design.B.superseded_v1_runs` = 16).
