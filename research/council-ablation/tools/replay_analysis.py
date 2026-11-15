"""Replay the pre-registered analysis from the published, non-raw answers and compare with the frozen result.

Makes no model call. Copies the published answer files under the names the harness expects into a
temporary directory, runs ``harness/run.py analyze`` and checks that the produced ``results.json`` is
identical to ``evidence/council/results.json``.

    python tools/replay_analysis.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "evidence" / "council"


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        shutil.copy(EV / "member_calls.jsonl", out / "answers.jsonl")
        shutil.copy(EV / "judge_calls.jsonl", out / "judge.jsonl")
        subprocess.run([sys.executable, "-I", str(ROOT / "harness" / "run.py"), "analyze", str(out)],
                       check=True, capture_output=True, cwd=tmp)
        produced = json.loads((out / "results.json").read_text())
    frozen = json.loads((EV / "results.json").read_text())
    same = produced == frozen
    diff = [k for k in frozen if produced.get(k) != frozen.get(k)]
    record = {"replay": "harness/run.py analyze over evidence/council/member_calls.jsonl + judge_calls.jsonl",
              "identical_to_frozen_results": same, "differing_top_level_keys": diff, "bootstrap_seed": 11}
    (ROOT / "evidence" / "replay_check.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record, indent=1))
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
