"""Run the Study B and B2 analyses and record which evaluation-cache records they read and whether any was missing.

    python tools/trace_cache_reads.py                 # writes data/evaluation-cache-reads.json
    python tools/trace_cache_reads.py --check         # fails if a record differs from data/evaluation-cache-manifest.json,
                                                      # is missing (an evaluation was recomputed) or is never read

The analyses look up each feature and downstream evaluation by a hash key in `harness/rs2610/artifacts/cache/`
(`study_b/evaluate.py`, `replication/b2/evaluate.py`); a missing key is computed afresh and written. This script wraps
file opening for the run, so it observes every cache read and every cache write. A write means a recomputation, which
is exactly what the committed cache is there to prevent.
"""
from __future__ import annotations

import builtins
import io
import json
import os
import runpy
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HARNESS = REPO / "harness"
CACHE = HARNESS / "rs2610" / "artifacts" / "cache"
DIRS = ("study_b_eval", "b2_eval")


def main() -> None:
    check = "--check" in sys.argv[1:]
    reads, writes = set(), set()
    real_open = io.open

    def traced(file, mode="r", *a, **k):
        p = Path(os.fspath(file)) if isinstance(file, (str, os.PathLike)) else None
        if p is not None:
            try:
                rel = p.resolve().relative_to(CACHE).as_posix()
            except ValueError:
                rel = None
            if rel and rel.split("/")[0] in DIRS:
                (writes if any(c in mode for c in "wax+") else reads).add(rel)
        return real_open(file, mode, *a, **k)

    before = {f.relative_to(CACHE).as_posix() for d in DIRS for f in (CACHE / d).glob("*.json")}
    man = REPO / "data" / "evaluation-cache-manifest.json"
    if check and man.exists():  # every committed record is the one listed, byte for byte
        import hashlib
        listed = {f["path"]: f["sha256"] for f in json.loads(man.read_text())["files"]}
        got = {f"harness/rs2610/artifacts/cache/{r}": hashlib.sha256((CACHE / r).read_bytes()).hexdigest() for r in before}
        if listed != got:
            sys.exit(f"evaluation cache differs from data/evaluation-cache-manifest.json: "
                     f"{sorted(set(listed.items()) ^ set(got.items()))[:5]}")
        print(f"manifest OK: {len(listed)} records, SHA-256 match")
    io.open = builtins.open = traced
    sys.path.insert(0, str(HARNESS))
    os.chdir(HARNESS)
    try:
        for mod in ("rs2610.study_b.analyze", "rs2610.replication.b2.analyze"):
            sys.argv = [mod]
            runpy.run_module(mod, run_name="__main__")
    finally:
        io.open = builtins.open = real_open
    after = {f.relative_to(CACHE).as_posix() for d in DIRS for f in (CACHE / d).glob("*.json")}
    rec = {"committed_records": len(before), "read": sorted(reads), "written": sorted(writes),
           "new_records": sorted(after - before), "unread_committed": sorted(before - reads)}
    print(f"cache records committed {len(before)}, read {len(reads)}, written {len(writes)}, "
          f"new {len(after - before)}, unread {len(before - reads)}")
    if check:
        if writes or after - before or before - reads:
            sys.exit("evaluation cache incomplete or unused records present")
        print("CACHE OK: every evaluation served from the committed records; every record was read")
        return
    (REPO / "data").mkdir(exist_ok=True)
    (REPO / "data" / "evaluation-cache-reads.json").write_text(json.dumps(rec, indent=1) + "\n")


if __name__ == "__main__":
    main()
