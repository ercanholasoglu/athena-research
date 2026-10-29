"""Freeze record: everything that must not change between the DEVELOPMENT freeze and the end of UNSEEN evaluation.

    python -m rs2610.freeze --write  A|B   # create outputs/FREEZE_RECORD_<study>.json once, at that study's freeze
    python -m rs2610.freeze --verify A|B   # recompute and compare; exits 1 on any drift (run before and after UNSEEN)

Each study is frozen separately (Study B's development finished first). Shared harness files (LLM client, datasets,
preprocessing) are hashed in both records, so a change to them after either freeze is detected by that study's verify.

Hashes are SHA-256. Source hashes cover the files that define prompts, topologies, task contracts, conditions, scoring,
evaluation and statistics. Rendered-prompt hashes cover the exact bytes every UNSEEN run sends before any model output
is appended (Study A: system + instance prefix per instance; Study B: system + analysis prompt per dataset x variant x
condition, without the B/E pre-stage output, which is model-generated). The dataset manifest hashes every loaded frame.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
SHARED = ("harness_llm", "datasets_and_truth")

SOURCES = {
    "harness_llm": ["common/llm.py"],
    "datasets_and_truth": ["common/data.py", "common/prep.py"],
    "study_a_evidence": ["study_a/evidence.py"],
    "study_a_task_contracts": ["study_a/tasks.py"],
    "study_a_topologies_and_prompts": ["study_a/topologies.py"],
    "study_a_scoring": ["study_a/scoring.py"],
    "study_a_runner": ["study_a/run.py"],
    "study_a_statistics": ["study_a/analyze.py"],
    "study_b_variants_and_traps": ["study_b/variants.py", "study_b/profile.py"],
    "study_b_conditions_prompts_enum_legend": ["study_b/conditions.py"],
    "study_b_scoring": ["study_b/score.py"],
    "study_b_fe_evaluation": ["study_b/evaluate.py"],
    "study_b_runner": ["study_b/run.py"],
    "study_b_statistics": ["study_b/analyze.py"],
}


def sha(b: bytes | str) -> str:
    return hashlib.sha256(b.encode() if isinstance(b, str) else b).hexdigest()


def source_hashes(study: str) -> dict:
    keep = [k for k in SOURCES if k in SHARED or k.startswith(f"study_{study.lower()}_")]
    return {k: {f: sha((ROOT / f).read_bytes()) for f in SOURCES[k]} for k in keep}


def dataset_manifest() -> list[dict]:
    from rs2610.common.data import DATASETS
    rows = []
    for ds in DATASETS:
        df = ds.load()
        rows.append({"dataset_id": ds.dataset_id, "split": ds.split, "family": ds.family, "task_type": ds.task_type,
                     "studies": "".join(ds.studies), "target": ds.target, "rows": int(len(df)), "columns": int(df.shape[1]),
                     "frame_sha256": sha(pd.util.hash_pandas_object(df, index=True).to_numpy().tobytes()),
                     "truth_sha256": sha(json.dumps(ds.truth, sort_keys=True, default=str))})
    return rows


def study_a_prompts() -> dict:
    from rs2610.study_a.tasks import build_all
    from rs2610.study_a.topologies import SYSTEM, render_prefix
    out = {"system": sha(SYSTEM), "instances": {}}
    for inst in build_all():
        out["instances"][inst["instance_id"]] = {"split": inst["split"], "prefix": sha(SYSTEM + render_prefix(inst)),
                                                 "contract": sha(json.dumps(inst["reference"], sort_keys=True, default=str))}
    return out


def study_b_prompts() -> dict:
    from rs2610.common.data import by_id
    from rs2610.common.prep import holdout_split
    from rs2610.study_b.conditions import ANALYSIS_SCHEMA, ANALYSIS_TASK, CONDITIONS, SYSTEM, documentation, enum_legend
    from rs2610.study_b.profile import candidate_features, profile, render_profile, target_summary
    from rs2610.study_b.run import MAKERS, plan
    from rs2610.study_b.variants import trapped
    level = {"A_RAW": "none", "B_SELF": "none", "C_DICT": "dict", "D_RULES": "rules", "E_FULL": "rules"}
    out = {"system": sha(SYSTEM), "analysis_task": sha(ANALYSIS_TASK), "analysis_enum_legend": sha(enum_legend(ANALYSIS_SCHEMA)),
           "analysis_schema": sha(json.dumps(ANALYSIS_SCHEMA, sort_keys=True)), "conditions": list(CONDITIONS), "rendered": {}}
    for split in ("DEVELOPMENT", "UNSEEN"):
        for did, kind, conds in plan(split, "all"):
            ds = by_id(did)
            base = trapped(ds)
            dev, _, _ = holdout_split(ds, base.frame)
            v = base if kind == "trapped" else MAKERS[kind](base)
            prof = f"DATASET PROFILE (development split)\n{render_profile(profile(v, dev), v)}\n{target_summary(v, dev)}\n\n"
            cands = sha(json.dumps(candidate_features(v, dev), sort_keys=True, default=str))
            for c in conds:
                out["rendered"][f"{did}::{kind}::{c}"] = {"split": split, "candidates": cands,
                                                          "analysis_prompt": sha(SYSTEM + prof + documentation(v, level[c]) + ANALYSIS_TASK + enum_legend(ANALYSIS_SCHEMA))}
    return out


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def build(study: str) -> dict:
    from rs2610.common.llm import DEFAULT_MODEL, LLM, TEMPERATURE
    digest = LLM(OUT / ".digest_probe.jsonl").digest
    (OUT / ".digest_probe.jsonl").unlink(missing_ok=True)
    rec = {
        "model": {"name": DEFAULT_MODEL, "digest": digest, "runtime": "ollama (local)", "temperature": TEMPERATURE,
                  "num_ctx": 12288, "structured_output": "JSON schema via Ollama `format`"},
        "seed_policy": {"llm_seed": "= repeat index", "data_seed": 20261027, **({
                        "study_a": {"DEVELOPMENT": [1], "UNSEEN": [1, 2, 3], "order": "seed-outer, Latin-square mode rotation"}}
                        if study == "A" else {
                        "study_b": {"DEVELOPMENT": [1], "UNSEEN": [1, 2], "grid": "all (trapped main grid + T1/T3/T4 variants)"}})},
        "study": study,
        "sources": source_hashes(study),
        "dataset_manifest": dataset_manifest(),
        f"study_{study.lower()}_prompts": study_a_prompts() if study == "A" else study_b_prompts(),
        "python": platform.python_version(),
        "packages": {p: __import__(p).__version__ for p in ("sklearn", "lightgbm", "xgboost", "catboost", "scipy", "pandas", "numpy",
                                                            "matplotlib", "statsmodels")},
    }
    rec["dataset_manifest_sha256"] = sha(json.dumps(rec["dataset_manifest"], sort_keys=True))
    return rec


def comparable(rec: dict) -> dict:
    return {k: v for k, v in rec.items() if k not in ("git", "frozen_at", "pre_freeze_excluded", "notes", "enum_legend")}


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--verify"
    study = sys.argv[2] if len(sys.argv) > 2 else sys.exit("usage: freeze --write|--verify A|B")
    RECORD = OUT / f"FREEZE_RECORD_{study}.json"
    rec = build(study)
    if mode == "--write":
        if RECORD.exists():
            sys.exit("freeze record exists; refusing to overwrite (delete it deliberately and journal why)")
        rec["git"] = {"branch": git("rev-parse", "--abbrev-ref", "HEAD"), "head": git("rev-parse", "HEAD"),
                      "dirty_paths": git("status", "--porcelain", "--", ".").splitlines()}
        rec["frozen_at"] = pd.Timestamp.now(tz="Europe/Istanbul").isoformat()
        rec["pre_freeze_excluded"] = (["artifacts/study_b/superseded_v1/ (10 Study B DEVELOPMENT runs with blind enums; harness "
                                       "defect discovered during development before experimental freeze)"] if study == "B" else []) + [
                                      f"artifacts/study_{study.lower()}/runs_debug.jsonl (smoke runs)"]
        rec["enum_legend"] = ("every Study B call appends ALLOWED VALUES for every enum in its schema (conditions.enum_legend)"
                              if study == "B" else "Study A prompts list every option id; topology enums are named in task text")
        RECORD.write_text(json.dumps(rec, indent=1, sort_keys=True))
        print("written", RECORD, "sources:", sha(json.dumps(rec["sources"], sort_keys=True))[:12])
        return
    frozen = json.loads(RECORD.read_text())
    a, b = comparable(frozen), comparable(rec)
    drift = []
    for k in sorted(set(a) | set(b)):
        if json.dumps(a.get(k), sort_keys=True) != json.dumps(b.get(k), sort_keys=True):
            drift.append(k)
    if drift:
        print("FREEZE DRIFT:", drift)
        for k in drift:
            if k == "sources":
                for g, fs in b["sources"].items():
                    for f, h in fs.items():
                        if a["sources"].get(g, {}).get(f) != h:
                            print("  changed source:", f)
        sys.exit(1)
    print("FREEZE OK", frozen["git"]["head"][:10], frozen["frozen_at"])


if __name__ == "__main__":
    main()
