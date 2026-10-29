"""Verify the locally prepared datasets against the frozen hashes, using the frozen functions.

    python tools/verify_data.py            # all datasets
    python tools/verify_data.py --only bank_marketing --json

Per dataset:
* Study A/B manifest (`FREEZE_RECORD_A.json`, `FREEZE_RECORD_B.json`): rows, columns, loaded-frame SHA-256, truth SHA-256;
* A2/B2 record (`FREEZE_RECORD_A2B2.json`): rows, columns, frame, holdout scheme, dev/test split index hashes and, for
  B2 datasets, the B2 frame, the B2 truth and every rendered analysis / invention / candidate prompt hash of all 10 cells.

Status: MATCH (every check equal), SOURCE_CHANGED (the data loads but a frozen hash differs: the current public source
no longer reproduces the frozen frame), MISSING (raw files absent), GENERATED (synthetic, still hash-checked).
Exit code 1 if any dataset is SOURCE_CHANGED or MISSING.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "harness"))

import numpy as np  # noqa: E402

from rs2610.common.data import by_id  # noqa: E402
from rs2610.common.prep import holdout_split  # noqa: E402
from rs2610.replication.freeze import frame_sha, sha  # noqa: E402

OUT = REPO / "harness" / "rs2610" / "outputs"
LEVEL = {"A_RAW": "none", "B_SELF": "none", "C_DICT": "dict", "D_RULES": "rules", "E_FULL": "rules"}


def b2_checks(did: str, frozen: dict, prompts: dict) -> dict[str, bool]:
    from rs2610.replication.b2 import invention
    from rs2610.replication.b2.variants import CELLS, MAKERS, b2_base
    from rs2610.study_b.conditions import ANALYSIS_SCHEMA, ANALYSIS_TASK, SYSTEM, documentation, enum_legend
    from rs2610.study_b.profile import candidate_features, profile, render_profile, target_summary

    ds = by_id(did)
    df = ds.load()
    dev, test, scheme = holdout_split(ds, df)
    got = {"rows": int(len(df)), "columns": int(df.shape[1]), "frame_sha256": frame_sha(df), "holdout_scheme": scheme,
           "dev_idx_sha256": sha(np.asarray(dev).tobytes()), "test_idx_sha256": sha(np.asarray(test).tobytes())}
    checks = {f"a2b2.{k}": got[k] == frozen[k] for k in got}
    if frozen.get("in_b2"):
        base = b2_base(ds)
        checks["a2b2.b2_frame_sha256"] = frame_sha(base.frame) == frozen["b2_frame_sha256"]
        checks["a2b2.b2_truth_sha256"] = sha(json.dumps(base.truth, sort_keys=True, default=str)) == frozen["b2_truth_sha256"]
        for kind, cond in CELLS:
            v = MAKERS[kind](base)
            pr = profile(v, dev)
            prof = f"DATASET PROFILE (development split)\n{render_profile(pr, v)}\n{target_summary(v, dev)}\n\n"
            ref = prompts[f"{did}::{kind}::{cond}"]
            checks[f"b2.{kind}.{cond}.analysis_prompt"] = sha(SYSTEM + prof + documentation(v, LEVEL[cond]) + ANALYSIS_TASK
                                                                + enum_legend(ANALYSIS_SCHEMA)) == ref["analysis_prompt"]
            checks[f"b2.{kind}.{cond}.invention_prompt"] = sha(SYSTEM + invention.prompt(v, cond, pr, dev)) == ref["invention_prompt"]
            checks[f"b2.{kind}.{cond}.candidates"] = sha(json.dumps(candidate_features(v, dev), sort_keys=True, default=str)) == ref["candidates"]
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    manifest: dict[str, dict] = {}
    for rec in ("FREEZE_RECORD_A.json", "FREEZE_RECORD_B.json"):
        for m in json.loads((OUT / rec).read_text())["dataset_manifest"]:
            manifest.setdefault(m["dataset_id"], {}).update({"ab": m})
    a2b2 = json.loads((OUT / "replication" / "FREEZE_RECORD_A2B2.json").read_text())
    for m in a2b2["datasets"]:
        manifest.setdefault(m["dataset_id"], {})["a2b2"] = m
    report, bad = [], 0
    for did in sorted(manifest):
        if a.only and did not in a.only:
            continue
        entry = manifest[did]
        row = {"dataset_id": did, "checks": 0, "mismatches": []}
        try:
            ds = by_id(did)
            df = ds.load()
            if "ab" in entry:
                m = entry["ab"]
                got = {"rows": int(len(df)), "columns": int(df.shape[1]), "frame_sha256": frame_sha(df),
                       "truth_sha256": sha(json.dumps(ds.truth, sort_keys=True, default=str))}
                c = {f"ab.{k}": got[k] == m[k] for k in got}
                row["frame_sha256"] = got["frame_sha256"]
            else:
                c = {}
            if "a2b2" in entry:
                c.update(b2_checks(did, entry["a2b2"], a2b2["b2_prompts"]["rendered"]))
            row["checks"] = len(c)
            row["mismatches"] = [k for k, ok in c.items() if not ok]
            row["status"] = "SOURCE_CHANGED" if row["mismatches"] else ("GENERATED" if did == "card_fraud_synth" else "MATCH")
        except FileNotFoundError as e:
            row["status"], row["error"] = "MISSING", str(e).replace(str(Path.home()), "~")
        bad += row["status"] in ("SOURCE_CHANGED", "MISSING")
        report.append(row)
        if not a.json:
            mm = f"  mismatches: {row['mismatches']}" if row["mismatches"] else ""
            print(f"{did:22s} {row['status']:15s} {row['checks']:3d} checks{mm}")
    if a.json:
        print(json.dumps(report, indent=1))
    else:
        print("ALL MATCH" if not bad else f"{bad} dataset(s) not verified")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
