"""Write the navigation READMEs of every `research/<study>/<part>/<folder>/`, `docs/DATASETS.md` and `data/manifest.json`.

    python tools/make_index.py           # write
    python tools/make_index.py --check   # fail if any generated file is stale

The research folders do not duplicate code or results. Each folder README links the canonical file under
`harness/rs2610/` (the code that ran, byte-identical to the frozen sources) with its SHA-256 and size, so a reader can
verify that the linked file is the frozen one.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
H = REPO / "harness" / "rs2610"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from datasets import SOURCES, download_url, page  # noqa: E402


def caps() -> tuple[dict[str, int | None], int]:
    """Row cap per dataset and the sampling seed, read from the frozen loader's source (importing it needs the raw data)."""
    import ast
    tree = ast.parse((H / "common" / "data.py").read_text())
    const = {t.id: n.value.value for n in tree.body if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant)
             for t in n.targets if isinstance(t, ast.Name)}
    out = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "Dataset" and n.args and isinstance(n.args[0], ast.Constant):
            kw = {k.arg: k.value for k in n.keywords}
            out[n.args[0].value] = kw["cap"].value if "cap" in kw else const["MAX_ROWS"]
    return out, const["SEED"]

FOLDERS: dict[str, tuple[str, list[tuple[str, str]]]] = {
    # ---------------------------------------------------------------- Study A
    "reasoning-topology/original-study/configs": ("Frozen configuration of Study A", [
        ("outputs/FREEZE_RECORD_A.json", "freeze record: source hashes, model digest, temperature, num_ctx, every rendered prompt hash, dataset manifest"),
        ("outputs/study_a/study-a-design.md", "pre-registered design: hypotheses H1–H4, splits, metrics, tests")]),
    "reasoning-topology/original-study/topologies": ("DIRECT, CoT, ToT, GoT: the implementation that ran", [
        ("study_a/topologies.py", "all four topologies, their prompts, the branch scoring, pruning and graph propagation (frozen)"),
        ("outputs/replication/CODE_EXCERPTS.md", "verbatim excerpts with line ranges and file SHA-256 (no paraphrase)"),
        ("study_a/structure_fig.py", "renders sample ToT / GoT structures from recorded runs")]),
    "reasoning-topology/original-study/contracts": ("Decision contracts and evidence packets", [
        ("study_a/tasks.py", "the 10 decision families: options, evidence fields, correct-answer rules, adversarial variants (frozen)"),
        ("outputs/study_a/study-a-task-contracts.md", "the contracts as a document (generated from `tasks.py`)"),
        ("study_a/evidence.py", "measured evidence per dataset (cross-validated models, timings) that the contracts quote (frozen)"),
        ("artifacts/study_a/instances/UNSEEN.json", "the 101 unseen decision instances exactly as presented"),
        ("artifacts/study_a/instances/DEVELOPMENT.json", "development instances")]),
    "reasoning-topology/original-study/evaluation": ("Scoring", [
        ("study_a/scoring.py", "correctness, abstention, governance violations, calibration (frozen)"),
        ("study_a/run.py", "runner: instance × mode × seed, call budget, ledger (frozen)")]),
    "reasoning-topology/original-study/statistics": ("Statistics", [
        ("study_a/analyze.py", "exact McNemar, dataset-cluster bootstrap, Holm within each hypothesis family (frozen)"),
        ("outputs/study_a/study-a-statistics.md", "every test with effect, CI and adjusted p"),
        ("outputs/study_a/study-a-confirmatory.csv", "H1–H4 confirmatory tests"),
        ("outputs/study_a/study-a-paired-tests.csv", "all paired mode contrasts")]),
    "reasoning-topology/original-study/results": ("Results (aggregate and run level)", [
        ("outputs/study_a/study-a-summary.md", "summary"),
        ("outputs/study_a/study-a-results.csv", "per split × mode: accuracy with CI, abstention, calibration, tokens, latency"),
        ("outputs/study_a/study-a-per-family.csv", "per decision family"),
        ("outputs/study_a/study-a-adversarial.csv", "adversarial instances"),
        ("outputs/study_a/study-a-topology-stats.csv", "branch / node / edge statistics of ToT and GoT"),
        ("outputs/study_a/latency-audit.csv", "compute and latency relative to DIRECT"),
        ("outputs/study_a/study-a-failures.md", "failure catalogue"),
        ("outputs/study_a/study-a-run-level-results.csv", "one row per run"),
        ("artifacts/study_a/runs_unseen.jsonl", "run records with per-call request hashes"),
        ("artifacts/study_a/ledger.jsonl", "request ledger: request hash, raw output, tokens, latency, model digest")]),
    "reasoning-topology/original-study/figures": ("Figures", [
        ("outputs/study_a/study-a-figures/accuracy_by_mode_unseen.png", "accuracy by mode, unseen split"),
        ("outputs/study_a/study-a-figures/per_family_unseen.png", "per family"),
        ("outputs/study_a/study-a-figures/quality_vs_tokens_unseen.png", "accuracy against output tokens"),
        ("outputs/study_a/study-a-figures/sample_structures.png", "sample ToT / GoT structures"),
        ("outputs/study_a/study-a-figures/dev_vs_unseen.png", "development against unseen")]),
    # ---------------------------------------------------------------- A2
    "reasoning-topology/frontier-replication/configs": ("Frozen configuration of A2", [
        ("outputs/replication/FREEZE_RECORD_A2B2.json", "original A2/B2 freeze record"),
        ("outputs/replication/FREEZE_RECORD_A2B2_AMENDMENT1.json", "amendment 1: OpenAI arm gpt-6.1-sol → gpt-6-luna, before any Luna run"),
        ("outputs/replication/FREEZE_RECORD_A2B2_AMENDMENT2.json", "amendment 2 (governing): Anthropic arm, B2 only"),
        ("replication/PREREGISTRATION.md", "pre-registration (hashed into the freeze record)"),
        ("outputs/replication/a2/EXPERIMENT_CONFIG.md", "model ids, resolved ids, reasoning setting, token caps, prices, usage per arm"),
        ("outputs/replication/a2/experiment-config.json", "the same, machine-readable")]),
    "reasoning-topology/frontier-replication/providers": ("Provider substrate", [
        ("replication/providers.py", "OpenAI Responses and Anthropic Messages clients: request shape, reasoning effort, strict schema, caching by request hash, cost (frozen)"),
        ("replication/a2/run.py", "A2 runner: the 64 unseen instances, 3 replicates, the frozen Study A topologies (frozen)")]),
    "reasoning-topology/frontier-replication/statistics": ("Statistics", [
        ("replication/a2/analyze.py", "A2 analysis: within-model, model effect, interaction, error decomposition"),
        ("outputs/replication/a2/a2-within-model.csv", "topology vs DIRECT within each model (Holm)"),
        ("outputs/replication/a2/a2-model-effect.csv", "gpt-6-luna vs qwen2.5:7b per topology"),
        ("outputs/replication/a2/a2-interaction.csv", "model × topology interaction"),
        ("outputs/replication/a2/a2-adversarial-tests.csv", "adversarial instances")]),
    "reasoning-topology/frontier-replication/results": ("Results", [
        ("outputs/replication/a2/a2-results.csv", "per model × mode: accuracy with CI, abstention, calibration, tokens, latency, cost"),
        ("outputs/replication/a2/a2-error-decomposition.csv", "wrong option vs abstention (descriptive)"),
        ("outputs/replication/a2/a2-topology-structure.csv", "graph statistics (descriptive)"),
        ("outputs/replication/a2/a2-fidelity.csv", "topology fidelity"),
        ("outputs/replication/a2/a2-adversarial.csv", "adversarial instances"),
        ("outputs/replication/a2/a2-run-level.csv", "one row per run"),
        ("artifacts/replication/a2/runs_openai.jsonl", "run records"),
        ("artifacts/replication/a2/ledger_openai.jsonl", "request ledger with provider-returned model id and usage"),
        ("artifacts/replication/a2/runs_openai.superseded_sol.jsonl", "superseded gpt-6.1-sol pilot (excluded)"),
        ("artifacts/replication/a2/runs_openai.billing_refused.superseded_sol.jsonl", "billing-refused pilot rows (quarantined, excluded)")]),
    # ---------------------------------------------------------------- Study B
    "semantic-context/original-study/configs": ("Frozen configuration of Study B", [
        ("outputs/FREEZE_RECORD_B.json", "freeze record: sources, model, prompts, condition hashes, dataset manifest"),
        ("outputs/study_b/study-b-design.md", "pre-registered design"),
        ("artifacts/study_b/superseded_v2/FREEZE_RECORD_B_v1.json", "superseded first freeze (kept; see docs/HISTORY.md)")]),
    "semantic-context/original-study/conditions": ("A_RAW, B_SELF, C_DICT, D_RULES, E_FULL", [
        ("study_b/conditions.py", "the five conditions: prompt builder, dictionary / rules injection, self-description, verification pass (frozen)"),
        ("outputs/study_b/semantic-condition-contracts.md", "what each condition shows the model"),
        ("study_b/profile.py", "development-split profile and candidate features shown to every condition (frozen)")]),
    "semantic-context/original-study/traps": ("Traps and dictionary variants", [
        ("study_b/variants.py", "trapped variant: leakage, identifier, post-outcome, warehouse-artifact and causal/predictive traps; ground truth (frozen)"),
        ("outputs/study_b/datasets-and-dictionaries.md", "every dataset, dictionary entry, rule and inserted trap column"),
        ("outputs/study_b/adversarial-cases.md", "adversarial cases"),
        ("outputs/study_b/t4-falsified-entries.csv", "falsified dictionary entries")]),
    "semantic-context/original-study/evaluation": ("Scoring and feature evaluation", [
        ("study_b/score.py", "semantic decisions scored against the evaluation-authority truth (frozen)"),
        ("study_b/evaluate.py", "proposed features executed and evaluated on held-out data (frozen)"),
        ("study_b/run.py", "runner (frozen)")]),
    "semantic-context/original-study/statistics": ("Statistics", [
        ("study_b/analyze.py", "paired tests over (dataset, seed) units, Holm (frozen)"),
        ("study_b/sensitivity.py", "sensitivity analyses"),
        ("outputs/study_b/study-b-statistics.md", "every test"),
        ("outputs/study_b/study-b-paired-tests.csv", "paired condition contrasts")]),
    "semantic-context/original-study/results": ("Results", [
        ("outputs/study_b/study-b-summary.md", "summary"),
        ("outputs/study_b/study-b-results.csv", "per split × variant × condition"),
        ("outputs/study_b/study-b-per-dataset.csv", "per dataset"),
        ("outputs/study_b/semantic-decisions.csv", "every semantic decision"),
        ("outputs/study_b/generated-features.csv", "every proposed feature and its evaluation"),
        ("outputs/study_b/candidate-judgements.csv", "candidate judgements"),
        ("outputs/study_b/study-b-failures.md", "failure catalogue"),
        ("outputs/study_b/run-level-results.csv", "one row per run"),
        ("artifacts/study_b/runs_unseen.jsonl", "run records"),
        ("artifacts/study_b/ledger.jsonl", "request ledger")]),
    "semantic-context/original-study/figures": ("Figures", [
        ("outputs/study_b/study-b-figures/semantic_accuracy_by_condition_unseen.png", "semantic accuracy by condition"),
        ("outputs/study_b/study-b-figures/leakage_detection_by_condition_unseen.png", "leakage detection"),
        ("outputs/study_b/study-b-figures/validity_vs_gain_unseen.png", "feature validity against gain"),
        ("outputs/study_b/study-b-figures/dev_vs_unseen.png", "development against unseen")]),
    # ---------------------------------------------------------------- B2
    "semantic-context/frontier-replication/configs": ("Frozen configuration of B2", [
        ("outputs/replication/FREEZE_RECORD_A2B2_AMENDMENT2.json", "governing freeze record (amends 1, which amends the original)"),
        ("replication/PREREGISTRATION.md", "pre-registration"),
        ("outputs/replication/b2/EXPERIMENT_CONFIG.md", "model ids, reasoning setting, token caps, prices, usage per arm"),
        ("outputs/replication/b2/experiment-config.json", "the same, machine-readable")]),
    "semantic-context/frontier-replication/variants": ("The 10 B2 cells", [
        ("replication/b2/variants.py", "trapped, anonymized, incomplete and misleading dictionary variants on the frozen Study B base (frozen)"),
        ("replication/b2/run.py", "B2 runner: 4 datasets × 10 cells × replicates per arm (frozen)")]),
    "semantic-context/frontier-replication/feature-invention": ("Feature invention: schema, validation, evaluation, classes", [
        ("replication/b2/invention.py", "invention prompt, schema, deterministic expression validation, leakage checks (frozen)"),
        ("replication/b2/evaluate.py", "execution and held-out evaluation; VALID_USEFUL / VALID_NOT_USEFUL / INVALID_LOW_GAIN / INVALID_HIGH_APPARENT / NOT_EXECUTABLE (frozen)"),
        ("outputs/replication/b2/b2-features.csv", "every invented feature with its class and held-out gain"),
        ("outputs/replication/b2/b2-feature-classes.csv", "class counts per model and source")]),
    "semantic-context/frontier-replication/statistics": ("Statistics", [
        ("replication/b2/analyze.py", "B2 analysis: model effect, semantic effect, interaction (exact sign tests, Holm across cells)"),
        ("outputs/replication/b2/b2-model-effect.csv", "hosted model vs qwen2.5:7b per cell"),
        ("outputs/replication/b2/b2-semantic-effect.csv", "documentation effect within each model"),
        ("outputs/replication/b2/b2-interaction.csv", "model × documentation")]),
    "semantic-context/frontier-replication/results": ("Results", [
        ("outputs/replication/b2/b2-results.csv", "per model × cell, with bootstrap intervals"),
        ("outputs/replication/b2/b2-run-level.csv", "one row per run"),
        ("artifacts/replication/b2/runs_local.jsonl", "qwen2.5:7b runs"),
        ("artifacts/replication/b2/runs_openai.jsonl", "gpt-6-luna runs"),
        ("artifacts/replication/b2/runs_anthropic.jsonl", "claude-sonnet-5-5 runs"),
        ("artifacts/replication/b2/ledger_local.jsonl", "local ledger"),
        ("artifacts/replication/b2/ledger_openai.jsonl", "OpenAI ledger"),
        ("artifacts/replication/b2/ledger_anthropic.jsonl", "Anthropic ledger")]),
    # ---------------------------------------------------------------- cross-study
    "cross-study/analysis": ("Cross-study analysis", [
        ("replication/cross.py", "capability, structure and semantics effects side by side (pre-registration section 8)"),
        ("outputs/replication/cross-study.csv", "the effects table (copied to `../cross-study.csv`, checked identical)"),
        ("replication/PREREGISTRATION.md", "section 8 defines the comparison")]),
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def size(p: Path) -> str:
    n = p.stat().st_size
    return f"{n / 1e6:.1f} MB" if n >= 1e6 else f"{n / 1e3:.0f} kB"


def folder_readme(folder: str, title: str, items: list[tuple[str, str]]) -> str:
    dest = REPO / "research" / folder / "README.md"
    lines = [f"# {title}", "", "Generated by `python tools/make_index.py`. Links point at the canonical files in `harness/rs2610/`; "
             "nothing here is a copy. Files marked *frozen* are byte-identical to the freeze record's source hashes "
             "(`python -m rs2610.replication.freeze --verify`).", "", "| file | what it is | size | sha256 |", "|---|---|---|---|"]
    for rel, what in items:
        p = H / rel
        if not p.exists():
            sys.exit(f"{folder}: missing {rel}")
        link = os.path.relpath(p, dest.parent).replace(os.sep, "/")
        lines.append(f"| [`{rel}`]({link}) | {what} | {size(p)} | `{sha(p)[:16]}…` |")
    extra = sorted(q for q in (REPO / "research" / folder).glob("*") if q.name != "README.md")
    if extra:
        lines += ["", "Generated in this folder:", ""] + [f"- [`{q.name}`]({q.name}{'/' if q.is_dir() else ''})" for q in extra]
    return "\n".join(lines) + "\n"


def manifest() -> tuple[str, str]:
    out = H / "outputs"
    ab: dict[str, dict] = {}
    for rec in ("FREEZE_RECORD_A.json", "FREEZE_RECORD_B.json"):
        for m in json.loads((out / rec).read_text())["dataset_manifest"]:
            ab.setdefault(m["dataset_id"], {}).update(m)
    a2b2 = {m["dataset_id"]: m for m in json.loads((out / "replication" / "FREEZE_RECORD_A2B2.json").read_text())["datasets"]}
    rows, (cap, seed) = [], caps()
    for did, s in SOURCES.items():
        m, r = ab.get(did, {}), a2b2.get(did, {})
        rows.append({
            "dataset_id": did, "name": s["name"], "licence": s["licence"], "page": page(did),
            "download": None if s["kind"] == "generated" else download_url(did),
            "studies": sorted(set(m.get("studies", [])) | ({"A2"} if r.get("in_a2") else set()) | ({"B2"} if r.get("in_b2") else set())),
            "split_role": m.get("split"), "family": m.get("family"), "task": m.get("task_type"), "target": m.get("target"),
            "rows": m.get("rows"), "columns": m.get("columns"), "row_cap": cap[did], "cap_rule": f"seeded sample (random_state={seed}) when rows exceed the cap",
            "frame_sha256": m.get("frame_sha256"), "truth_sha256": m.get("truth_sha256"),
            "holdout_scheme": r.get("holdout_scheme"), "dev_idx_sha256": r.get("dev_idx_sha256"), "test_idx_sha256": r.get("test_idx_sha256"),
            "b2_frame_sha256": r.get("b2_frame_sha256"), "b2_truth_sha256": r.get("b2_truth_sha256"),
        })
    md = ["# Datasets", "", "Generated by `python tools/make_index.py` from `tools/datasets.py` and the freeze records. Raw data is **not** "
          "redistributed: `python tools/prepare_data.py` downloads each file from its public source into the cache layout the frozen "
          "loaders read (`~/.cache/athena-decision-corpus-v2/`, `~/.cache/athena-research-ablation/raw/`) and then runs "
          "`tools/verify_data.py`, which recomputes every frozen hash with the frozen functions.", "",
          "Status per dataset is MATCH, SOURCE_CHANGED (the current source no longer reproduces the frozen frame; reported, never "
          "hidden), MISSING or GENERATED (synthetic, built by `common/data.py` from a fixed seed). Preparation, capping and the "
          "split rule are code, not prose: `harness/rs2610/common/data.py` (loading, target, row cap, column selection) and "
          "`harness/rs2610/common/prep.py` (`holdout_split`: 75/25, time-based for `bike_sharing` and `card_fraud_synth`, "
          "group-based where the truth names a group column, stratified otherwise; fixed seed). Rows above the cap are reduced by "
          "a seeded random sample before anything else; `rows` below is the frame after capping, which is what the frame hash covers.", "",
          "| dataset_id | public source | licence | studies | role | task | target | rows × cols used | row cap |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        src = f"[{r['name']}]({r['page']})" if (r["page"] or "").startswith("http") else r["name"]
        md.append(f"| `{r['dataset_id']}` | {src} | {r['licence']} | {', '.join(r['studies'])} | {r['split_role'] or '—'} | "
                  f"{r['task'] or '—'} | `{r['target']}` | {r['rows']} × {r['columns']} | {r['row_cap'] or 'none'} |")
    md += ["", "## Frozen hashes", "", "| dataset_id | frame sha256 | truth sha256 | holdout | dev idx sha256 | test idx sha256 |",
           "|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| `{r['dataset_id']}` | `{r['frame_sha256']}` | `{r['truth_sha256']}` | {r['holdout_scheme'] or '—'} | "
                  f"`{r['dev_idx_sha256'] or '—'}` | `{r['test_idx_sha256'] or '—'}` |")
    md += ["", "Split index hashes were first frozen in the A2/B2 record, so they are listed for the A2/B2 datasets only. For the "
           "other datasets the split is a deterministic function of the frozen frame (`holdout_split`, fixed seed), so the "
           "frame hash also fixes the split. Study A's evidence packets (`artifacts/study_a/evidence/`) record the measured "
           "quantities the contracts quote.", "", "B2 additionally freezes the B2 base frame and truth (`b2_frame_sha256`, `b2_truth_sha256` in "
           "[`data/manifest.json`](../data/manifest.json)) and the SHA-256 of every rendered analysis prompt, invention prompt and "
           "candidate list for all 10 cells (`b2_prompts.rendered` in the freeze record).", ""]
    return "\n".join(md), json.dumps({"datasets": rows}, indent=1) + "\n"


def main() -> None:
    plan = {REPO / "research" / f / "README.md": folder_readme(f, t, items) for f, (t, items) in FOLDERS.items()}
    md, js = manifest()
    plan[REPO / "docs" / "DATASETS.md"] = md + "\n"
    plan[REPO / "data" / "manifest.json"] = js
    plan[REPO / "research" / "cross-study" / "cross-study.csv"] = (H / "outputs" / "replication" / "cross-study.csv").read_text()
    stale = []
    for p, text in plan.items():
        if "--check" in sys.argv:
            if not p.exists() or p.read_text() != text:
                stale.append(str(p.relative_to(REPO)))
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
    if stale:
        sys.exit(f"stale generated files: {stale}")
    print("INDEX OK" if "--check" in sys.argv else f"wrote {len(plan)} files")


if __name__ == "__main__":
    main()
