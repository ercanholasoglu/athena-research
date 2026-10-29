"""Study A2: the frozen Study A topologies on a frontier model, over the frozen A2 subset.

    python -m rs2610.replication.a2.run --provider openai --model gpt-6.1-sol [--replicates 1 2 3] [--workers 8]

Execution semantics, prompts, schemas, instances and scoring are the frozen Study A code (``study_a.topologies.Runner``,
``study_a.scoring.score_run``, ``study_a.tasks.build_all``), imported unchanged. Only the substrate differs
(``replication.providers.FrontierLLM``). The local qwen2.5:7b arm is not re-run: its frozen Study A UNSEEN runs on the same
instances and seeds are the baseline.
"""
from __future__ import annotations

import argparse
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from rs2610.common.llm import append_line
from rs2610.replication.providers import Budget, BudgetExceeded, FrontierLLM
from rs2610.study_a.scoring import score_run
from rs2610.study_a.tasks import build_all
from rs2610.study_a.topologies import MODES, Runner

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts" / "replication" / "a2"
# Frozen subset (SUBSET_RATIONALE.md): the three UNSEEN datasets that carry every adversarial variant, plus one base-only
# dataset from a different domain.
A2_DATASETS = ("iranian_churn", "taiwan_default", "diabetes_readmission", "online_shoppers")
A2_REPLICATES = (1, 2, 3)
A2_BUDGET_USD = {"openai": 14.0, "anthropic": 14.0}


def instances() -> list[dict]:
    return [i for i in build_all() if i["split"] == "UNSEEN" and i["dataset_id"] in A2_DATASETS]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", required=True, choices=["openai", "anthropic"])
    ap.add_argument("--model", required=True)
    ap.add_argument("--replicates", type=int, nargs="+", default=list(A2_REPLICATES))
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    insts = instances()[: a.limit] if a.limit else instances()
    ledger = ART / f"ledger_{a.provider}.jsonl"
    llm = FrontierLLM(ledger, a.provider, a.model, Budget(A2_BUDGET_USD[a.provider], [ledger]))
    runner = Runner(llm)
    out = ART / f"runs_{a.provider}.jsonl"
    done = set()
    if out.exists():
        for line in out.read_text().splitlines():
            r = json.loads(line)
            done.add((r["instance_id"], r["mode"], r["seed"]))
    stop = threading.Event()
    lock = threading.Lock()
    counter = {"n": 0}

    def job(seed: int, k: int, inst: dict) -> None:
        order = MODES[(k + seed) % 4:] + MODES[: (k + seed) % 4]  # same Latin-square rotation as the frozen runner
        for pos, mode in enumerate(order):
            if stop.is_set() or (inst["instance_id"], mode, seed) in done:
                continue
            try:
                trace = runner.run(inst, mode, seed)
            except BudgetExceeded as e:
                stop.set()
                print("BUDGET STOP:", e, flush=True)
                return
            costs = [llm._cache.get(c["request_hash"], {}).get("cost_usd") for c in trace["calls"]]
            rec = [llm._cache.get(c["request_hash"], {}) for c in trace["calls"]]
            row = {"instance_id": inst["instance_id"], "dataset_id": inst["dataset_id"], "split": inst["split"],
                   "family": inst["family"], "variant": inst["variant"], "adversarial": inst["adversarial"],
                   "mode": mode, "seed": seed, "order_position": pos, "provider": a.provider, "model": a.model,
                   "resolved_models": sorted({r.get("resolved_model") for r in rec if r.get("resolved_model")}),
                   "reasoning_tokens": sum(r.get("reasoning_tokens") or 0 for r in rec) if all(r.get("reasoning_tokens") is not None for r in rec) else None,
                   "cost_usd": round(sum(costs), 6) if costs and all(c is not None for c in costs) else None,
                   "cost_status": "CALCULATED_FROM_PUBLISHED_PRICES" if costs and all(c is not None for c in costs) else "UNKNOWN",
                   "truncated_calls": sum(bool(r.get("truncated")) for r in rec),
                   **score_run(inst, trace), "trace": trace}
            with lock:
                append_line(out, json.dumps(row))
                counter["n"] += 1
                print(f"[{counter['n']}] {inst['instance_id']:55s} {mode:6s} r{seed} -> {row['decision']!s:24s} ok={row['correct']} "
                      f"calls={row['n_calls']} out={row['output_tokens']} ${row['cost_usd']} spent=${llm.budget.spent:.2f}", flush=True)

    with ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(job, seed, k, inst) for seed in a.replicates for k, inst in enumerate(insts)]
        for f in futs:
            f.result()
    print("runs written:", counter["n"], "spent USD:", round(llm.budget.spent, 4), "STOPPED_BY_BUDGET" if stop.is_set() else "")


if __name__ == "__main__":
    main()
