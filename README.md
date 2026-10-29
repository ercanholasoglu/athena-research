# Athena Research — Tabular AI Decision-Making

Controlled experiments on reasoning topology, semantic context, and model capability

This repository holds the evidence behind a set of articles on LLM-assisted decisions in tabular machine learning: the
designs, pre-registrations, freeze records, prompts, contracts, code that ran, run-level records, statistics and
figures. The articles interpret the results; this repository is what they rest on. Athena, the AutoML product these
questions came from, is not part of it: the research harness here is standalone and imports nothing from the product.

Result numbers in this README and in `docs/` are rendered from the committed fact files (`tools/render_docs.py`),
not typed by hand.

## Studies

| Study | Question | Models | Status |
|---|---|---|---|
| [JEV](research/jev/) | Can a typed bounded-decision model (TypeSafe Jev) make AutoML decisions such as explanation method or search depth? | `jev-1.13.0` | retrospective; evidence public, harness not public |
| [Study A](research/reasoning-topology/original-study/) | Do chain, tree or graph orchestration (CoT, ToT, GoT) improve bounded AutoML decisions over a direct answer? | `qwen2.5:7b` (local) | frozen 2026-10-28, evaluated once |
| [Study A2](research/reasoning-topology/frontier-replication/) | Does that change with a stronger hosted model? | `qwen2.5:7b`, `gpt-6-luna` | frozen 2026-10-29, 2 amendments before the amended arms ran |
| [Study B](research/semantic-context/original-study/) | Do data dictionaries, business rules and a verification pass make semantic decisions safer and more correct? | `qwen2.5:7b` | frozen 2026-10-27, evaluated once |
| [Study B2](research/semantic-context/frontier-replication/) | Do stronger models use semantics better, resist false or incomplete dictionaries, and invent valid features? | `qwen2.5:7b`, `gpt-6-luna`, `claude-sonnet-5-5` | frozen 2026-10-29, 2 amendments |
| [Cross-study](research/cross-study/) | Capability, structure or semantics: which moved decisions most, within these tests? | all of the above | analysis of the completed studies |

## Headline results

Point estimates on held-out (unseen) data, with the pre-registered test. Within these models, datasets and contracts
only; each study README gives the full table, intervals and what is not claimed.

| Study | Result | Test |
|---|---|---|
| A | Accuracy DIRECT 77.6%, CoT 77.2%, ToT 75.9%, GoT 74.6%; no topology beat DIRECT | H1, Holm p = 1.000 (GoT vs DIRECT) |
| A2 | `gpt-6-luna`: DIRECT 86.5%, CoT 82.3%, ToT 81.2%, GoT 64.6%; GoT vs DIRECT −21.9 pp [−30.7, −14.1]; 58 of 68 GoT errors were abstentions | Holm p < 0.001 |
| A2 | Capability at DIRECT: `gpt-6-luna` − `qwen2.5:7b` = +12.5 pp [+4.2, +21.9] | Holm p < 0.001 |
| B | Runs blocking every trap: A_RAW 43.8%, D_RULES 93.8% | Holm p 0.046 |
| B2 | Without documentation (A_RAW), runs blocking every trap: `qwen2.5:7b` 12.5%, `gpt-6-luna` 62.5%, `claude-sonnet-5-5` 100.0% | descriptive (4–8 units) |
| B2 | Anonymized columns, `gpt-6-luna`: dictionary raises all-traps-blocked from 0.0% to 100.0% | Holm p 0.031 |
| B2 | Falsified dictionary entries detected: `gpt-6-luna` 91.7% vs `qwen2.5:7b` 0.0% | Holm p 0.016 |
| B2 | Invented features: rarely leaky on hosted models, but no more useful; the highest valid-and-useful share in any model × cell was 17.5% (`qwen2.5:7b`) | descriptive |
| JEV | Semantic descriptions: EXPLANATION_MODE 22.6% → 58.1% on the original benchmark; on 6 unseen datasets richer semantics, structured state and decomposition added nothing | 0 of 14 tests significant after Holm |

Ordinal reading across studies (section 8 of the replication report): **capability > semantics > structure**. Different
metrics and scales; only the order is compared. See [cross-study](research/cross-study/).

## Layout

```
harness/rs2610/          the research harness that ran (byte-identical to the frozen sources), with its outputs/ and
                         artifacts/ (run records, request ledgers, freeze records, result tables, reports)
research/                one folder per study: README, configs, prompts, contracts, evaluation, statistics, results,
                         figures, TRACE.md. Folders link the canonical harness files; they do not copy them
docs/                    EXPERIMENTS, REPRODUCIBILITY, MODELS, DATASETS, LIMITATIONS, HISTORY
tools/                   data preparation and verification, prompt export, figures, traces, docs, release audit
data/manifest.json       dataset manifest: sources, licences, hashes (raw data is not redistributed)
templates/               sources of the rendered READMEs and docs
```

## Reproduce

```bash
uv venv --python 3.12.12 .venv && source .venv/bin/activate
uv pip install -r requirements-lock.txt
python tools/prepare_data.py        # download public datasets, verify every frozen hash
bash tools/reproduce.sh             # freeze verification, statistics, figures, reports, traces, audit
```

No API key is needed: every model call is in a committed ledger, and re-running replays it by request hash. Details,
expected run time and what each step checks: [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md).

## Read first

- [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md): the experiments in one page each
- [docs/LIMITATIONS.md](docs/LIMITATIONS.md): what these results do not show
- [docs/HISTORY.md](docs/HISTORY.md): freezes, amendments, the billing stop and the data-cache incident
- Full reports: [FINAL_RESEARCH_REPORT.md](harness/rs2610/FINAL_RESEARCH_REPORT.md) (Studies A, B) and
  [FRONTIER_REPLICATION_REPORT.md](harness/rs2610/FRONTIER_REPLICATION_REPORT.md) (A2, B2)

## Licence and citation

Code: Apache-2.0 ([LICENSE](LICENSE)). Text, result tables and figures: CC BY 4.0 ([LICENSE-CC-BY-4.0.md](LICENSE-CC-BY-4.0.md)).
Datasets keep their own licences and are not redistributed ([docs/DATASETS.md](docs/DATASETS.md)). Citation metadata:
[CITATION.cff](CITATION.cff). No DOI has been minted.
