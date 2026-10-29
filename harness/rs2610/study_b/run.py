"""Execute Study B: (dataset variant × condition × seed) → JSONL of raw traces.

    python -m rs2610.study_b.run --split DEVELOPMENT --seeds 1 [--only telco] [--grid main|adversarial|all]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from rs2610.common.data import by_id, datasets
from rs2610.common.llm import LLM, append_line
from rs2610.common.prep import holdout_split
from rs2610.study_b.conditions import CONDITIONS, run_condition
from rs2610.study_b.profile import candidate_features, profile
from rs2610.study_b.variants import anonymized, incomplete, misleading, trapped

ART = Path(__file__).resolve().parents[1] / "artifacts" / "study_b"
ADV = {
    "anonymized": ({"DEVELOPMENT": ["telco_churn", "bank_marketing"], "UNSEEN": ["taiwan_default", "iranian_churn"]}, ("A_RAW", "C_DICT", "E_FULL")),
    "incomplete": ({"DEVELOPMENT": ["telco_churn", "german_credit"], "UNSEEN": ["taiwan_default", "diabetes_readmission"]}, ("C_DICT", "D_RULES", "E_FULL")),
    "misleading": ({"DEVELOPMENT": ["telco_churn", "bank_marketing"], "UNSEEN": ["taiwan_default", "card_fraud_synth"]}, ("C_DICT", "D_RULES", "E_FULL")),
}
MAKERS = {"anonymized": anonymized, "incomplete": incomplete, "misleading": misleading}


def plan(split: str, grid: str) -> list[tuple[str, str, tuple[str, ...]]]:
    jobs = []
    if grid in ("main", "all"):
        jobs += [(d.dataset_id, "trapped", CONDITIONS) for d in datasets("B", split)]
    if grid in ("adversarial", "all"):
        for kind, (ids, conds) in ADV.items():
            jobs += [(did, kind, conds) for did in ids[split]]
    return jobs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1])
    ap.add_argument("--grid", default="all")
    ap.add_argument("--only")
    ap.add_argument("--conditions", nargs="+")
    ap.add_argument("--tag", default="main")
    a = ap.parse_args()
    llm = LLM(ART / "ledger.jsonl")
    out = ART / f"runs_{a.tag}.jsonl"
    ART.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        for line in out.read_text().splitlines():
            r = json.loads(line)
            done.add((r["dataset_id"], r["variant"], r["condition"], r["seed"]))
    for did, kind, conds in plan(a.split, a.grid):
        if a.only and a.only not in did:
            continue
        ds = by_id(did)
        base = trapped(ds)
        dev, test, scheme = holdout_split(ds, base.frame)
        v = base if kind == "trapped" else MAKERS[kind](base)
        prof = profile(v, dev)
        cands = candidate_features(v, dev)
        for seed in a.seeds:
            for cond in conds:
                if a.conditions and cond not in a.conditions:
                    continue
                if (did, kind, cond, seed) in done:
                    continue
                tr = run_condition(llm, v, cond, seed, prof, dev, cands, {"study": "B", "dataset": did, "variant": kind, "condition": cond, "seed": seed})
                row = {"dataset_id": did, "split": ds.split, "variant": kind, "condition": cond, "seed": seed, "model": llm.model,
                       "model_digest": llm.digest, "rename": v.rename, "removed_definitions": v.removed_definitions,
                       "falsified": v.falsified, "candidates": cands, "holdout_scheme": scheme, "trace": tr}
                append_line(out, json.dumps(row))
                an = tr.get("analysis") or {}
                print(f"{did:22s} {kind:10s} {cond:8s} s{seed} bp={an.get('business_problem')} ids={an.get('id_columns')} "
                      f"post={an.get('post_outcome_columns')} split={an.get('split_strategy')} calls={len(tr['calls'])} "
                      f"out_tok={sum((c['output_tokens'] or 0) for c in tr['calls'])} fail={len(tr['failures'])}", flush=True)


if __name__ == "__main__":
    main()
