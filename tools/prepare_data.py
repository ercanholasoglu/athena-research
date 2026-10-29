"""Download every public dataset into the cache layout the frozen loaders read, then verify it.

    python tools/prepare_data.py              # download what is missing, then run verify_data.py
    python tools/prepare_data.py --only taiwan_default bank_marketing
    python tools/prepare_data.py --force      # re-download even when the files exist

Files already present are kept. Each written file's SHA-256 is printed and saved to `data/raw-sha256.observed.json`
(machine-local, git-ignored). Verification against the frozen hashes is done by `verify_data.py`, which this script calls at
the end; a dataset whose current public source no longer reproduces its frozen frame is reported as SOURCE_CHANGED.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from datasets import RECORDED_RAW_SHA256, SOURCES, download_url, label, targets  # noqa: E402

REPO = Path(__file__).resolve().parents[1]


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "athena-research-prepare/1.0"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def prepare(did: str, force: bool) -> dict:
    s, out = SOURCES[did], targets(did)
    if s["kind"] == "generated":
        return {"dataset_id": did, "status": "GENERATED"}
    if out and all(p.exists() for p in out) and not force:
        return {"dataset_id": did, "status": "PRESENT", "files": {label(p): sha(p.read_bytes()) for p in out}}
    url = download_url(did)
    blob = fetch(url)
    files: dict[str, bytes] = {}
    if s["kind"] == "uci_archive":
        files[str(out[0])] = blob
    elif s["kind"] == "file":
        files[str(out[0])] = blob
    else:
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            names = zf.namelist()
            for p in out:
                hit = [n for n in names if n.split("/")[-1] == p.name]
                if not hit:  # some UCI archives nest a second zip
                    for inner in [n for n in names if n.endswith(".zip")]:
                        with zipfile.ZipFile(io.BytesIO(zf.read(inner))) as z2:
                            h2 = [n for n in z2.namelist() if n.split("/")[-1] == p.name]
                            if h2:
                                files[str(p)] = z2.read(h2[0])
                                break
                    if str(p) not in files:
                        raise SystemExit(f"{did}: {p.name} not found in {url}")
                else:
                    files[str(p)] = zf.read(hit[0])
    rec = {"dataset_id": did, "status": "DOWNLOADED", "url": url, "archive_sha256": sha(blob), "files": {}}
    for path, data in files.items():
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        h = sha(data)
        rec["files"][label(p)] = h
        known = RECORDED_RAW_SHA256.get(label(p))
        if known and known != h:
            rec.setdefault("raw_differs_from_recorded", []).append(label(p))
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--no-verify", action="store_true")
    a = ap.parse_args()
    ids = a.only or list(SOURCES)
    report = []
    for did in ids:
        try:
            r = prepare(did, a.force)
        except Exception as e:  # noqa: BLE001 — report and continue; verification decides
            r = {"dataset_id": did, "status": "DOWNLOAD_FAILED", "error": f"{type(e).__name__}: {e}"}
        report.append(r)
        extra = f"  raw differs from recorded: {r['raw_differs_from_recorded']}" if r.get("raw_differs_from_recorded") else ""
        print(f"{did:22s} {r['status']}{extra}")
    out = REPO / "data" / "raw-sha256.observed.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=1))
    if not a.no_verify:
        sys.exit(subprocess.run([sys.executable, str(REPO / "tools" / "verify_data.py"), *(["--only", *a.only] if a.only else [])]).returncode)


if __name__ == "__main__":
    main()
