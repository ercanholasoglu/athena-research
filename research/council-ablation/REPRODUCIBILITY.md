# Reproducibility — council ablation

No model is called by any step below. The answers, judge calls and analysis results are committed under
[`evidence/`](evidence/), and every step reads them.

## Environment

* The repository environment: Python 3.12.12 and [`requirements-lock.txt`](../../requirements-lock.txt), as described in
  [docs/REPRODUCIBILITY.md](../../docs/REPRODUCIBILITY.md).
* The notebooks also need a Jupyter kernel and runner, pinned in
  [`requirements-notebooks.txt`](requirements-notebooks.txt).
* Fixed seed: 11. This is the pre-registered bootstrap seed, and every derived computation reuses it.

```bash
uv venv --python 3.12.12 .venv && source .venv/bin/activate
uv pip install -r requirements-lock.txt -r research/council-ablation/requirements-notebooks.txt
```

## Checks run by `tools/reproduce.sh`

```bash
python research/council-ablation/tools/derive_facts.py --check      # results/facts.json from evidence/
python research/council-ablation/tools/replay_analysis.py           # pre-registered analysis re-run; writes evidence/replay_check.json
python research/council-ablation/tools/check_evidence_map.py        # every write-up number recomputed; writes EVIDENCE_MAP.md
python research/council-ablation/tools/render_methodology.py        # METHODOLOGY.md from the research plans
python research/council-ablation/tools/scan_publication.py          # study-level scan; writes evidence/publication_scan.json
```

What the replay does:
1. It copies `evidence/council/member_calls.jsonl` and `judge_calls.jsonl` under the names the study harness
   expects.
2. It runs the harness's `analyze` step (`research/council-ablation/harness/run.py`).
3. It checks that the produced `results.json` is identical to `evidence/council/results.json`.

The published answers carry no raw completions, and the analysis does not need them.

## Notebooks (clean kernel, Restart + Run All)

```bash
python research/council-ablation/tools/build_notebooks.py   # regenerates notebooks/*.ipynb from the evidence (optional)
python research/council-ablation/tools/run_notebooks.py     # fresh kernel per notebook; writes outputs and evidence/notebook_runs.json
```

A notebook passes only if every cell executes without an error. `evidence/notebook_runs.json` records the result,
duration and environment of each run. Durations differ between runs, so this step is not part of the exact-diff check
of `tools/reproduce.sh`.

## Re-collect the answers (paid, not needed for any result here)

The harness's `collect` and `judge` steps call the providers again. They need an Anthropic API key and a local
Ollama with `qwen2.5:7b` and `qwen2.5:1.5b`. At the provider-enforced temperature of 1, a re-collection gives new
samples, not the same answers. The frozen evidence remains the only basis of the published result. A new collection
is a new experiment and needs its own pre-registration.

## Source integrity

`evidence/SOURCE_MANIFEST.json` lists the SHA-256 of every source file this study folder was built from. Notebook 00
checks the copied protocol, harness and results against it. Two evidence files differ from their private originals,
because product source paths are redacted; both are listed in [docs/REDACTIONS.json](../../docs/REDACTIONS.json).
The Jev evidence is not copied: the notebooks and the evidence map read the JEV study's files in
[`research/jev/evidence/`](../jev/evidence/).
