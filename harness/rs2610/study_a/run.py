"""Execute Study A: instances × modes × seeds, one JSONL row per run.

    python -m rs2610.study_a.run --split DEVELOPMENT --seeds 1 [--limit N] [--only substring]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from rs2610.common.llm import LLM, append_line
from rs2610.study_a.scoring import score_run
from rs2610.study_a.tasks import build_all
from rs2610.study_a.topologies import MODES, Runner

ART = Path(__file__).resolve().parents[1] / "artifacts" / "study_a"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--only")
    ap.add_argument("--tag", default="main")
    a = ap.parse_args()
    insts = [i for i in build_all() if i["split"] == a.split and (not a.only or a.only in i["instance_id"])]
    insts = insts[: a.limit] if a.limit else insts
    (ART / "instances").mkdir(parents=True, exist_ok=True)
    (ART / "instances" / f"{a.split}.json").write_text(json.dumps(insts, indent=1))
    llm = LLM(ART / "ledger.jsonl")
    runner = Runner(llm)
    out = ART / f"runs_{a.tag}.jsonl"
    done = set()
    if out.exists():
        for line in out.read_text().splitlines():
            r = json.loads(line)
            done.add((r["instance_id"], r["mode"], r["seed"]))
    n = 0
    for seed in a.seeds:  # seed-outer: every completed seed is a full replicate
        for k, inst in enumerate(insts):
            order = MODES[(k + seed) % 4:] + MODES[: (k + seed) % 4]  # rotate mode order: spreads prefix-cache advantage
            for pos, mode in enumerate(order):
                if (inst["instance_id"], mode, seed) in done:
                    continue
                trace = runner.run(inst, mode, seed)
                row = {"instance_id": inst["instance_id"], "dataset_id": inst["dataset_id"], "split": inst["split"],
                       "family": inst["family"], "variant": inst["variant"], "adversarial": inst["adversarial"],
                       "mode": mode, "seed": seed, "order_position": pos, "model": llm.model, "model_digest": llm.digest,
                       **score_run(inst, trace), "trace": trace}
                append_line(out, json.dumps(row))
                n += 1
                print(f"[{k + 1}/{len(insts)}] {inst['instance_id']:55s} {mode:6s} s{seed} -> {row['decision']!s:28s} "
                      f"ok={row['correct']} conf={row['confidence']} calls={row['n_calls']} out_tok={row['output_tokens']} {row['wall_s']:.0f}s",
                      flush=True)
    print("runs written:", n)


if __name__ == "__main__":
    main()
