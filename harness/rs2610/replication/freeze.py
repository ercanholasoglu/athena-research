"""A2/B2 freeze record. Created once before any frontier evaluation run; verified before and after every run.

    python -m rs2610.replication.freeze --write
    python -m rs2610.replication.freeze --verify

Hashes (SHA-256): every replication source file and every frozen Study A/B source it imports; the A2 per-instance
prompt prefixes and answer keys; the B2 rendered analysis and invention prompts and candidate lists per dataset x cell;
dataset frames and split indices; schemas; the model / budget / replicate configuration. ``--verify`` also runs the
original Study A and Study B freeze verification, so a change to the canonical studies is caught here too.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from rs2610.freeze import git, sha

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "replication"
RECORD = OUT / "FREEZE_RECORD_A2B2.json"
# Amendments are made only before any run of the arm they change; each is a complete record and the latest one governs
# verification. The original record is never rewritten.
AMENDMENTS = sorted(OUT.glob("FREEZE_RECORD_A2B2_AMENDMENT*.json"))
OPENAI_MODEL = "gpt-6-luna"  # amendment 1 (2026-10-29): was gpt-6.1-sol; see JOURNAL.md
ANTHROPIC_MODEL = "claude-sonnet-5-5"  # amendment 2 (2026-10-29): was claude-opus-5-5, B2 only, 1 replicate
SOURCES = {
    "replication": ["replication/providers.py", "replication/a2/run.py", "replication/b2/variants.py", "replication/b2/invention.py",
                    "replication/b2/evaluate.py", "replication/b2/run.py", "replication/PREREGISTRATION.md", "replication/freeze.py"],
    "frozen_shared": ["common/llm.py", "common/data.py", "common/prep.py"],
    "frozen_study_a": ["study_a/evidence.py", "study_a/tasks.py", "study_a/topologies.py", "study_a/scoring.py", "study_a/analyze.py"],
    "frozen_study_b": ["study_b/variants.py", "study_b/profile.py", "study_b/conditions.py", "study_b/score.py", "study_b/evaluate.py",
                       "study_b/analyze.py"],
}


def frame_sha(df: pd.DataFrame) -> str:
    return sha(pd.util.hash_pandas_object(df, index=True).to_numpy().tobytes())


def build() -> dict:
    from rs2610.common.data import by_id
    from rs2610.common.prep import holdout_split
    from rs2610.replication import providers
    from rs2610.replication.a2.run import A2_BUDGET_USD, A2_DATASETS, A2_REPLICATES, instances
    from rs2610.replication.b2 import invention
    from rs2610.replication.b2.evaluate import HIGH_APPARENT_CV, USEFUL_CV
    from rs2610.replication.b2.run import B2_BUDGET_USD
    from rs2610.replication.b2.variants import B2_DATASETS, B2_MISLEAD, B2_REPLICATES, CELLS, MAKERS, TD_TEXT, b2_base
    from rs2610.study_a.topologies import SYSTEM as A_SYSTEM, render_prefix
    from rs2610.study_b.conditions import ANALYSIS_SCHEMA, ANALYSIS_TASK, SYSTEM as B_SYSTEM, documentation, enum_legend
    from rs2610.study_b.profile import candidate_features, profile, render_profile, target_summary

    rec: dict = {"sources": {g: {f: sha((ROOT / f).read_bytes()) for f in fs} for g, fs in SOURCES.items()}}
    a2 = {"system": sha(A_SYSTEM), "instances": {}}
    for i in instances():
        a2["instances"][i["instance_id"]] = {"prefix": sha(A_SYSTEM + render_prefix(i)),
                                             "contract": sha(json.dumps(i["reference"], sort_keys=True, default=str)),
                                             "variant": i["variant"], "family": i["family"]}
    rec["a2_prompts"] = a2
    level = {"A_RAW": "none", "B_SELF": "none", "C_DICT": "dict", "D_RULES": "rules", "E_FULL": "rules"}
    b2: dict = {"system": sha(B_SYSTEM), "analysis_task": sha(ANALYSIS_TASK), "invent_task": sha(invention.INVENT_TASK),
                "invent_schema": sha(json.dumps(invention.INVENT_SCHEMA, sort_keys=True)),
                "analysis_schema": sha(json.dumps(ANALYSIS_SCHEMA, sort_keys=True)), "td_text": sha(TD_TEXT),
                "b2_mislead": sha(json.dumps(B2_MISLEAD, sort_keys=True)), "rendered": {}}
    data: list[dict] = []
    for did in sorted(set(A2_DATASETS) | set(B2_DATASETS)):
        ds = by_id(did)
        df = ds.load()
        dev, test, scheme = holdout_split(ds, df)
        row = {"dataset_id": did, "split": ds.split, "rows": int(len(df)), "columns": int(df.shape[1]), "frame_sha256": frame_sha(df),
               "holdout_scheme": scheme, "dev_idx_sha256": sha(np.asarray(dev).tobytes()), "test_idx_sha256": sha(np.asarray(test).tobytes()),
               "in_a2": did in A2_DATASETS, "in_b2": did in B2_DATASETS}
        if did in B2_DATASETS:
            base = b2_base(ds)
            row["b2_frame_sha256"] = frame_sha(base.frame)
            row["b2_truth_sha256"] = sha(json.dumps(base.truth, sort_keys=True, default=str))
            for kind, cond in CELLS:
                v = MAKERS[kind](base)
                pr = profile(v, dev)
                prof = f"DATASET PROFILE (development split)\n{render_profile(pr, v)}\n{target_summary(v, dev)}\n\n"
                b2["rendered"][f"{did}::{kind}::{cond}"] = {
                    "analysis_prompt": sha(B_SYSTEM + prof + documentation(v, level[cond]) + ANALYSIS_TASK + enum_legend(ANALYSIS_SCHEMA)),
                    "invention_prompt": sha(B_SYSTEM + invention.prompt(v, cond, pr, dev)),
                    "candidates": sha(json.dumps(candidate_features(v, dev), sort_keys=True, default=str))}
        data.append(row)
    rec["b2_prompts"] = b2
    rec["datasets"] = data
    rec["config"] = {
        "models": {"baseline": {"provider": "local", "model": "qwen2.5:7b", "temperature": 0.4},
                   "openai": {"model": OPENAI_MODEL}, "anthropic": {"model": ANTHROPIC_MODEL, "studies": ["B2"], "b2_replicates": [1]}},
        "reasoning_effort": providers.REASONING_EFFORT, "reasoning_allowance": providers.REASONING_ALLOWANCE,
        "prices": providers.PRICES, "a2": {"datasets": list(A2_DATASETS), "replicates": list(A2_REPLICATES), "budget_usd": A2_BUDGET_USD,
                                           "n_instances": len(a2["instances"])},
        "b2": {"datasets": list(B2_DATASETS), "replicates": list(B2_REPLICATES), "cells": [list(c) for c in CELLS],
               "budget_usd": B2_BUDGET_USD, "invent_max_tokens": invention.MAX_TOKENS, "useful_cv": USEFUL_CV,
               "high_apparent_cv": HIGH_APPARENT_CV},
    }
    return rec


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--verify"
    rec = build()
    if mode == "--amend":
        path = OUT / f"FREEZE_RECORD_A2B2_AMENDMENT{len(AMENDMENTS) + 1}.json"
        rec["git"] = {"branch": git("rev-parse", "--abbrev-ref", "HEAD"), "head": git("rev-parse", "HEAD")}
        rec["frozen_at"] = pd.Timestamp.now(tz="Europe/Istanbul").isoformat()
        rec["amends"] = (AMENDMENTS[-1] if AMENDMENTS else RECORD).name
        rec["reason"] = sys.argv[2] if len(sys.argv) > 2 else sys.exit("--amend needs a reason")
        path.write_text(json.dumps(rec, indent=1, sort_keys=True))
        print("written", path)
        return
    if mode == "--write":
        if RECORD.exists():
            sys.exit("freeze record exists; refusing to overwrite")
        OUT.mkdir(parents=True, exist_ok=True)
        rec["git"] = {"branch": git("rev-parse", "--abbrev-ref", "HEAD"), "head": git("rev-parse", "HEAD")}
        rec["frozen_at"] = pd.Timestamp.now(tz="Europe/Istanbul").isoformat()
        RECORD.write_text(json.dumps(rec, indent=1, sort_keys=True))
        print("written", RECORD)
        return
    frozen = json.loads((AMENDMENTS[-1] if AMENDMENTS else RECORD).read_text())
    drift = [k for k in rec if k not in ("amends", "reason") and json.dumps(rec[k], sort_keys=True) != json.dumps(frozen.get(k), sort_keys=True)]
    for k in drift:
        if k == "sources":
            for g, fs in rec["sources"].items():
                for f, h in fs.items():
                    if frozen["sources"].get(g, {}).get(f) != h:
                        print("  changed source:", f)
    orig = [subprocess.run([sys.executable, "-m", "rs2610.freeze", "--verify", s], cwd=ROOT.parent, capture_output=True, text=True)
            for s in ("A", "B")]
    for s, r in zip("AB", orig):
        print(f"original Study {s}:", (r.stdout.strip() or r.stderr.strip()).splitlines()[-1])
    if drift or any(r.returncode for r in orig):
        print("A2/B2 FREEZE DRIFT:", drift)
        sys.exit(1)
    print("A2/B2 FREEZE OK", frozen["git"]["head"][:10], frozen["frozen_at"])


if __name__ == "__main__":
    main()
