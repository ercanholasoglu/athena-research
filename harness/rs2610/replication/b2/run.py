"""Study B2: the frozen Study B conditions plus the feature-invention task, on the B2 grid, for one model.

    python -m rs2610.replication.b2.run --provider local                          # qwen2.5:7b baseline (frozen substrate)
    python -m rs2610.replication.b2.run --provider openai --model gpt-6.1-sol [--workers 6]

Per (dataset, cell, replicate): the frozen ``study_b.conditions.run_condition`` (analysis, FE with candidate judgements,
plus the B_SELF / E_FULL pre-stage), then the independent invention call (``invention.invent``). All prompts, profiles
and candidate lists are built by frozen Study B code from the B2 variants.
"""
from __future__ import annotations

import argparse
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from rs2610.common.data import by_id
from rs2610.common.llm import LLM, append_line
from rs2610.common.prep import holdout_split
from rs2610.replication.b2.invention import invent
from rs2610.replication.b2.variants import B2_DATASETS, B2_REPLICATES, CELLS, MAKERS, b2_base
from rs2610.replication.providers import Budget, BudgetExceeded, FrontierLLM
from rs2610.study_b.conditions import run_condition
from rs2610.study_b.profile import candidate_features, profile

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts" / "replication" / "b2"
B2_BUDGET_USD = {"openai": 9.0, "anthropic": 4.5}
# amendment 2: the Anthropic account holds $5, so its arm runs one replicate
B2_REPLICATES_BY_PROVIDER = {"anthropic": (1,)}


def jobs() -> list[tuple[str, str, str]]:
    return [(did, kind, cond) for did in B2_DATASETS for kind, cond in CELLS]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", required=True, choices=["local", "openai", "anthropic"])
    ap.add_argument("--model", default="qwen2.5:7b")
    ap.add_argument("--replicates", type=int, nargs="+")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--only")
    a = ap.parse_args()
    a.replicates = a.replicates or list(B2_REPLICATES_BY_PROVIDER.get(a.provider, B2_REPLICATES))
    ART.mkdir(parents=True, exist_ok=True)
    ledger = ART / f"ledger_{a.provider}.jsonl"
    if a.provider == "local":
        llm = LLM(ledger)
        workers = 1
    else:
        llm = FrontierLLM(ledger, a.provider, a.model, Budget(B2_BUDGET_USD[a.provider], [ledger]))
        workers = a.workers
    out = ART / f"runs_{a.provider}.jsonl"
    done = set()
    if out.exists():
        for line in out.read_text().splitlines():
            r = json.loads(line)
            done.add((r["dataset_id"], r["variant"], r["condition"], r["seed"]))
    prepared: dict[str, tuple] = {}
    for did in B2_DATASETS:
        ds = by_id(did)
        base = b2_base(ds)
        dev, _, scheme = holdout_split(ds, base.frame)
        prepared[did] = (ds, base, dev, scheme)
    stop = threading.Event()
    lock = threading.Lock()

    def job(did: str, kind: str, cond: str, seed: int) -> None:
        if stop.is_set() or (did, kind, cond, seed) in done or (a.only and a.only not in did):
            return
        ds, base, dev, scheme = prepared[did]
        v = MAKERS[kind](base)
        prof = profile(v, dev)
        cands = candidate_features(v, dev)
        tag = {"study": "B2", "dataset": did, "variant": kind, "condition": cond, "seed": seed}
        try:
            tr = run_condition(llm, v, cond, seed, prof, dev, cands, tag)
            inv = invent(llm, v, cond, seed, prof, dev, tag)
        except BudgetExceeded as e:
            stop.set()
            print("BUDGET STOP:", e, flush=True)
            return
        hashes = [c["request_hash"] for c in tr["calls"]] + [inv["call"]["request_hash"]]
        if a.provider == "local":
            model_info = {"provider": "local", "model": llm.model, "model_digest": llm.digest, "cost_usd": None,
                          "cost_status": "NOT_APPLICABLE_LOCAL"}
        else:
            recs = [llm._cache.get(h, {}) for h in hashes]
            costs = [r.get("cost_usd") for r in recs]
            known = bool(costs) and all(c is not None for c in costs)
            model_info = {"provider": a.provider, "model": a.model,
                          "resolved_models": sorted({r.get("resolved_model") for r in recs if r.get("resolved_model")}),
                          "cost_usd": round(sum(costs), 6) if known else None,
                          "cost_status": "CALCULATED_FROM_PUBLISHED_PRICES" if known else "UNKNOWN",
                          "reasoning_tokens": sum(r.get("reasoning_tokens") or 0 for r in recs),
                          "truncated_calls": sum(bool(r.get("truncated")) for r in recs)}
        row = {"dataset_id": did, "split": ds.split, "variant": kind, "condition": cond, "seed": seed, **model_info,
               "rename": v.rename, "removed_definitions": v.removed_definitions, "falsified": v.falsified,
               "candidates": cands, "holdout_scheme": scheme, "trace": tr, "invention": inv}
        with lock:
            append_line(out, json.dumps(row))
            an = tr.get("analysis") or {}
            print(f"{did:20s} {kind:10s} {cond:8s} r{seed} bp={an.get('business_problem')} post={an.get('post_outcome_columns')} "
                  f"inv={len(inv['features'] or [])} fail={len(tr['failures']) + (inv['failure'] is not None)} "
                  f"${model_info.get('cost_usd')} spent={getattr(getattr(llm, 'budget', None), 'spent', 0):.2f}", flush=True)

    todo = [(did, kind, cond, seed) for seed in a.replicates for did, kind, cond in jobs()]
    with ThreadPoolExecutor(workers) as ex:
        for f in [ex.submit(job, *t) for t in todo]:
            f.result()
    print("done", "STOPPED_BY_BUDGET" if stop.is_set() else "")


if __name__ == "__main__":
    main()
