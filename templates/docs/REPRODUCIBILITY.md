# Reproducibility

## What can be reproduced, and how far

| level | what it shows | needs |
|---|---|---|
| 1. statistics from evidence | every table, test, interval, figure and report regenerates from the committed run records | the environment; raw data for the analyses that re-evaluate features |
| 2. frozen inputs | the public datasets still yield the frozen frames, splits, truths and rendered prompts; the harness files are the frozen ones | the environment and the public datasets |
| 3. exact prompts | every exported prompt is the one that was sent, because its request hash is in the ledger | as 2 |
| 4. new samples | re-running a model produces new outputs to compare | Ollama with `qwen2.5:7b` at the recorded digest; your own API keys for hosted arms |

Levels 1–3 call no model. Every model call is in a committed ledger (`harness/rs2610/artifacts/**/ledger*.jsonl`),
keyed by a hash of the exact request. The runners look up that hash first, so re-running a frozen runner replays the
recorded output instead of sampling again. Level 4 is outside the scope of this release: hosted models cannot be
seeded and may change behind the same id.

## Setup

Python 3.12.12 exactly (the Study A and B freeze records hold the interpreter version, so another patch release
fails `freeze --verify` with drift in `python`) and the pinned environment:

```bash
uv venv --python 3.12.12 .venv && source .venv/bin/activate
uv pip install -r requirements-lock.txt
# without uv, from a Python 3.12.12 interpreter: python -m venv .venv && . .venv/bin/activate && pip install -r requirements-lock.txt
```

The harness runs from `harness/` as the package `rs2610` (`cd harness && python -m rs2610.<module>`); the tools in
`tools/` add `harness/` to the path themselves.

## Datasets

```bash
python tools/prepare_data.py          # download missing public files into ~/.cache/..., then verify
python tools/verify_data.py           # verify only
```

The frozen loaders read fixed cache paths: `~/.cache/athena-decision-corpus-v2/` and
`~/.cache/athena-research-ablation/raw/`. The paths are part of the frozen code and were not changed for release.
Verification recomputes, with the frozen functions, the rows, columns, loaded-frame SHA-256 and truth SHA-256 against
the Study A and B records. It also recomputes the holdout scheme, the development and test index hashes and, for B2,
the base frame, the truth and every rendered prompt hash against the A2/B2 record. Per-dataset status and the source
of each file: [DATASETS.md](DATASETS.md).

## Freeze verification

```bash
cd harness
python -m rs2610.freeze --verify A            # Study A: sources, prompts, model digest, datasets
python -m rs2610.freeze --verify B            # Study B
python -m rs2610.replication.freeze --verify  # A2/B2 against the governing amendment; also runs the two above
```

Each command compares a freshly built record with the frozen one. It excludes the git fields, the freeze time and
the notes, and fails on any other difference. The full replication verify needs all 15 datasets. The A and B
records also hold the Ollama digest of `qwen2.5:7b`, the Python version and nine package versions, so those verifies
pass only with a local Ollama serving that model and the pinned environment. Without Ollama they report
`FREEZE DRIFT: ['model']`; `tools/verify_data.py` checks the dataset part on its own.

Result at release (2026-10-29, macOS on Apple silicon, Ollama `qwen2.5:7b` at the recorded digest, all datasets
prepared from their public sources): all three verifies reported FREEZE OK, and `tools/verify_data.py` reported 14
MATCH and 1 GENERATED, with none SOURCE_CHANGED.

## Regenerate everything

```bash
bash tools/reproduce.sh
```

In order, the script:

1. prepares and verifies the data;
2. runs the three freeze verifications;
3. reruns every analysis (Study A, Study B, A2, B2, cross-study);
4. replays the prompt examples against the ledgers;
5. regenerates the facts, configs, code excerpts and reports, then the figures added for this release;
6. checks the JEV and council derivations, replays the council analysis, recomputes the council evidence map, and
   checks the traces and the rendered docs;
7. runs the release audit;
8. prints `git status` for the result files.

**Reproduced exactly** means step 8 prints nothing.

Study B and B2 read their scored evaluations from the committed [evaluation cache](#evaluation-cache).
`tools/trace_cache_reads.py --check` runs both analyses with every cache read and write traced. It fails if:

- a record differs from its manifest entry;
- an evaluation had to be recomputed;
- a published record is never read.

Bootstrap and permutation procedures use fixed seeds.

## Evaluation cache

[`harness/rs2610/artifacts/cache/study_b_eval/`](../harness/rs2610/artifacts/cache/study_b_eval/) and
[`b2_eval/`](../harness/rs2610/artifacts/cache/b2_eval/) hold one JSON record per evaluation. Each record is one of:

- a proposed or invented feature evaluation: leakage and validity checks, cross-validated gain, stability, held-out
  deployed gain and, for B2, its class;
- a feature that could not be executed, with the failure;
- a downstream model fitted on a run's accepted features: CV estimate, held-out naive and deployed score, leak
  inflation.

**What these records are:**

- **Not model output.** What the models proposed is in the run records and ledgers. These records are what the
  frozen evaluators ([`study_b/evaluate.py`](../harness/rs2610/study_b/evaluate.py),
  [`replication/b2/evaluate.py`](../harness/rs2610/replication/b2/evaluate.py)) computed from those proposals and
  the data. Each record is keyed by a hash of its inputs.
- **The published authority.** The published Study B and B2 statistics were generated from exactly these records.
  The last record was written seconds before the result tables: Study B on 2026-10-28, B2 on 2026-10-29.
  [`data/evaluation-cache-manifest.json`](../data/evaluation-cache-manifest.json) lists every record with its path,
  SHA-256, size, study, record type, purpose, write time, and the frozen evaluator that produced it (with that file's
  SHA-256 from the freeze record). Library versions are in `requirements-lock.txt`.
- **Selected by use.** The private cache held 1000 records. Tracing the published analyses showed 957 of them read.
  The other 43 are Study B development evaluations written on 2026-10-27, before the Study B freeze, and no
  published analysis reads them. They are not published; their SHA-256s and write times are listed under
  `excluded_records` in the manifest, and the trace is in
  [`data/evaluation-cache-selection.json`](../data/evaluation-cache-selection.json).

**Recomputing without the cache.** Delete the two folders and run the analyses: every evaluation is recomputed. The
first public clean-clone test did this and did **not** reproduce the published tables exactly ([HISTORY](HISTORY.md#evaluation-nondeterminism)):

- **Continuous scores** (gains, deployed scores, leak inflation) moved by a median of about 0.001 (Study B) and 0.0004
  (B2), at most 0.0022 in B2.
- **Threshold- or sign-based quantities** derived from those scores can change by a whole step on small cells. For
  example, a deployment-collapse rate on a two-unit development cell moved from 0.0 to 0.5, and some sign-test
  counts shifted by one.
- **Tests.** No Holm-adjusted p-value crossed 0.05, and no reported conclusion changed. Three values cited in the
  articles moved in the third decimal, for example C_DICT leak inflation 0.008 → 0.009.

The likely source is run-to-run nondeterminism in the boosted-model fits: the evaluators fit LightGBM with
`n_jobs=4`. This was observed, not isolated by a controlled experiment. The published numbers stay those computed
from the cache; a clean recomputation is a robustness check of them, not a replacement.

## Traceability

Every number in an article or report follows one chain:

```
ARTICLE claim
 → \{\{key\}\}                       fact key in the article draft (research/*/article-keys.json lists them)
 → value                         harness/rs2610/outputs/facts.json, .../replication/facts-replication.json, research/jev/results/facts.json
 → TABLE / FIGURE, ROW, COLUMN   facts-index.md, facts-replication-index.md: canonical CSV, row filter, column
 → RUN                           artifacts/**/runs_*.jsonl: one row per run (dataset, condition or mode, seed or replicate),
                                 with the request_hash of every call it made
 → REQUEST / LEDGER              artifacts/**/ledger_*.jsonl: request_hash, raw output, tokens, latency, provider model id,
                                 request id, cost
 → PROMPT                        tools/export_prompts.py replays the run through the frozen runner and prints the exact
                                 system and user text and schema for that request_hash (refuses if the hash is absent)
 → MODEL                         model id, digest or resolved id in the ledger row and the freeze record (docs/MODELS.md)
 → DATASET / SPLIT               dataset_id in the run row; frame, split and truth hashes in the freeze record
 → HASH                          tools/verify_data.py recomputes those hashes from the public source
```

The per-article chains are generated as TRACE files. Each lists every key the article cites, its value, and a link
to its canonical file:

- [reasoning-topology/original-study/TRACE.md](../research/reasoning-topology/original-study/TRACE.md)
- [reasoning-topology/frontier-replication/TRACE.md](../research/reasoning-topology/frontier-replication/TRACE.md)
- [semantic-context/original-study/TRACE.md](../research/semantic-context/original-study/TRACE.md)
- [semantic-context/frontier-replication/TRACE.md](../research/semantic-context/frontier-replication/TRACE.md)
- [jev/TRACE.md](../research/jev/TRACE.md): coarser, because JEV has per-case rows but no public request ledger
- [council-ablation/TRACE.md](../research/council-ablation/TRACE.md): fact keys to per-call parsed answers; the
  write-up numbers are recomputed claim by claim in [EVIDENCE_MAP.md](../research/council-ablation/EVIDENCE_MAP.md)

`python tools/make_trace.py --check` fails if a TRACE file is stale or a cited key has no canonical source.

## Environment

- Python 3.12.12; the packages are pinned in [`requirements-lock.txt`](../requirements-lock.txt) (50 packages, no
  editable or private installs).
- The runs were made on one Apple-silicon laptop (macOS) with Ollama serving `qwen2.5:7b` locally.
- Hosted SDKs: `openai` 3.41.0, `anthropic` 2.3.0.
- JEV experiments A and B ran under Python 3.12.7 and 3.12.15 respectively, as recorded in their evidence files.
- The council-ablation notebooks run in this environment plus a pinned Jupyter runner
  ([`research/council-ablation/requirements-notebooks.txt`](../research/council-ablation/requirements-notebooks.txt)).
  Their Restart + Run All results are in
  [`research/council-ablation/evidence/notebook_runs.json`](../research/council-ablation/evidence/notebook_runs.json).

## Release checks

`python tools/check_repo.py` runs before every push and fails on any finding. It checks:

- credentials and tokens;
- personal identifiers, home and temporary paths;
- private infrastructure names and IP addresses;
- product code;
- forbidden files and files over 10 MB;
- every relative Markdown link and every backticked repository path.
