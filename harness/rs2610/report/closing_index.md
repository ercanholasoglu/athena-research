## 30. Artifact index

All paths are relative to `research/rs2610/`. Raw datasets are not committed. Their sources and frame hashes are in the freeze records.

| What | Where |
|---|---|
| Lab journal: every decision, defect and freeze, in time order | `JOURNAL.md` |
| Freeze records: source hashes, prompt hashes, model digest, dataset frame hashes, split | `outputs/FREEZE_RECORD_A.json`, `outputs/FREEZE_RECORD_B.json` |
| Pre-registered designs and hypotheses | `outputs/study_a/study-a-design.md`, `outputs/study_b/study-b-design.md` |
| Task and condition contracts | `outputs/study_a/study-a-task-contracts.md`, `outputs/study_b/semantic-condition-contracts.md` |
| Datasets and dictionaries | `outputs/study_a/study-a-datasets.md`, `outputs/study_b/datasets-and-dictionaries.md` |
| Run rows (one row per run) | `artifacts/study_{a,b}/runs_{dev,unseen}.jsonl` |
| Every model request and response, keyed by request hash | `artifacts/study_{a,b}/ledger.jsonl` |
| Superseded Study B runs: enum-legend defect and unmatchable candidate ids (kept, excluded) | `artifacts/study_b/superseded_v1/`, `artifacts/study_b/superseded_v2/` |
| Study A tables: aggregate results, confirmatory H1–H4, pairwise tests, regret, per family, adversarial, topology | `outputs/study_a/study-a-{results,confirmatory,paired-tests,paired-regret,per-family,paired-by-family,adversarial,topology-stats}.csv` |
| Study B tables: aggregate results, paired tests, per dataset, stability, confidence | `outputs/study_b/study-b-{results,paired-tests,per-dataset,stability,confidence}.csv` |
| Study B decision-level detail | `outputs/study_b/{semantic-decisions,candidate-judgements,generated-features,decision-changes,t4-falsified-entries}.csv` |
| Exploratory post-freeze sensitivity analysis (Study B, `coil_caravan` excluded) | `outputs/study_b/study-b-sensitivity.csv` (`study_b/sensitivity.py`) |
| Latency audit: host-suspend contamination, UNKNOWN never 0 | `outputs/study_{a,b}/latency-audit.csv` |
| Cross-study table | `outputs/cross_study/` |
| Fact store and its index (key → table, row, column) | `outputs/facts.json`, `outputs/facts-index.md`, `outputs/derived-facts.json` |
| Report figures | `outputs/study_a/study-a-figures/`, `outputs/study_b/study-b-figures/` |
| Report section templates, assembled by `make_report.py` | `report/*.md` |
| Blog articles, evidence copy (SHA256SUMS) and readiness notes | `~/Desktop/atropos/blog/{5,6}/` |

**Figures.**

- **Study A, frozen pipeline** (`outputs/study_a/study-a-figures/`, `*_unseen.png` and `*_dev.png`):
  - accuracy, adversarial, calibration, per-family, calls, tokens, quality-vs-tokens, topology complexity;
  - `dev_vs_unseen.png` and `sample_structures.png` (schematic of recorded structures).
- **Study B, frozen pipeline** (`outputs/study_b/study-b-figures/`): semantic accuracy, task understanding, leakage detection,
  feature quality, validity-vs-gain, model quality, decision changes, adversarial tests, `dev_vs_unseen.png`.
- **Cross-study** (`outputs/cross_study/`): `quality_gain_vs_cost_{dev,unseen}.png` and `dev_vs_unseen_gap.png`.

**Latency figures.** Three figures from the frozen pipeline plot the unaudited latency columns, which include the
host-sleep calls of §24.1:
- `latency_by_mode_unseen.png` and `quality_vs_latency_unseen.png` (Study A);
- `cost_by_condition_unseen.png` (Study B).

They are kept as produced by the frozen code and are **not used** for any latency statement. Their audited counterparts
read `latency-audit.csv` and are drawn by the article figure builder (`~/Desktop/atropos/scripts/rs2610_figures.py`):
- Study A: `fig2b-quality-vs-latency`, `fig6-cost`;
- Study B: `fig7-cost`.

All other figures carry no latency. The cross-study compute multiples are computed from the audited files.
