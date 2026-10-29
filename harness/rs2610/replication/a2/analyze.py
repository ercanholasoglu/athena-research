"""Study A2 analysis, written after the freeze to PREREGISTRATION.md section 6 (deviations are listed in the report).

    python -m rs2610.replication.a2.analyze

Baseline rows are the frozen Study A UNSEEN runs on the A2 instances, rescored by the frozen ``study_a.analyze.load``.
Frontier rows are scored by the frozen ``score_run`` at run time; fidelity, ECE and consistency use the frozen functions.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest, fisher_exact

from rs2610.replication.a2.run import A2_DATASETS
from rs2610.study_a import analyze as frozen
from rs2610.study_a.topologies import MODES

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts" / "replication" / "a2"
OUT = ROOT / "outputs" / "replication" / "a2"
B = 10000
RNG = np.random.default_rng(20261029)
FORBIDDEN = "neural_net"  # the option the governance_block policy forbids (study_a.tasks)
PRETTY = {"qwen2.5:7b": "qwen2.5:7b", "gpt-6.1-sol": "gpt-6.1-sol", "claude-opus-5-5": "claude-opus-5-5"}


def holm(p: list[float]) -> list[float]:
    order = np.argsort(p)
    adj = np.empty(len(p))
    run = 0.0
    for k, i in enumerate(order):
        run = max(run, min(1.0, (len(p) - k) * p[i]))
        adj[i] = run
    return adj.tolist()


def load_baseline() -> pd.DataFrame:
    df = frozen.load()
    df = df[(df.split == "UNSEEN") & df.dataset_id.isin(A2_DATASETS)].copy()
    df["model"] = "qwen2.5:7b"
    df["provider"] = "local"
    df["cost_usd"] = np.nan
    return df


def load_frontier(provider: str) -> pd.DataFrame:
    p = ART / f"runs_{provider}.jsonl"
    if not p.exists():
        return pd.DataFrame()
    rows = []
    for line in p.read_text().splitlines():
        r = json.loads(line)
        t = r.pop("trace")
        topo = r.pop("topology", {}) or {}
        for k, v in topo.items():
            if isinstance(v, (int, float, bool)):
                r[f"topo_{k}"] = v
        r["fidelity"] = frozen.fidelity(r["mode"], t, r["decision"])
        r["n_calls"] = len(t["calls"])
        r["visible_output_tokens"] = (r["output_tokens"] - r["reasoning_tokens"]) if r.get("reasoning_tokens") is not None and r.get("output_tokens") is not None else None
        rows.append(r)
    return pd.DataFrame(rows)


def load_all() -> pd.DataFrame:
    parts = [load_baseline()] + [load_frontier(p) for p in ("openai", "anthropic")]
    df = pd.concat([p for p in parts if len(p)], ignore_index=True)
    df["correct"] = df["correct"].astype(bool)
    df["total_tokens"] = df["prompt_tokens"] + df["output_tokens"]
    gov = df.variant == "governance_block"
    df.loc[gov, "policy_compliant"] = (df.loc[gov, "decision"] != FORBIDDEN)
    return df


def inst_boot(fn, insts: list[str]) -> tuple[float, float]:
    vals = []
    arr = np.array(insts)
    for _ in range(B):
        vals.append(fn(arr[RNG.integers(0, len(arr), len(arr))]))
    return float(np.nanpercentile(vals, 2.5)), float(np.nanpercentile(vals, 97.5))


def paired(df: pd.DataFrame, key_a: dict, key_b: dict, match=("instance_id", "seed")) -> dict:
    a = df[np.logical_and.reduce([df[k] == v for k, v in key_a.items()])].set_index(list(match))["correct"]
    b = df[np.logical_and.reduce([df[k] == v for k, v in key_b.items()])].set_index(list(match))["correct"]
    j = pd.concat([a.rename("a"), b.rename("b")], axis=1, join="inner")
    b_better, a_better = int((~j.a & j.b).sum()), int((j.a & ~j.b).sum())
    p = binomtest(b_better, b_better + a_better, 0.5).pvalue if b_better + a_better else 1.0
    per_inst = j.groupby(level=0).mean()
    d = per_inst.b - per_inst.a
    lo, hi = inst_boot(lambda s: float(d.loc[s].mean()), list(per_inst.index))
    return {"n_pairs": len(j), "n_instances": len(per_inst), "acc_a": float(j.a.mean()), "acc_b": float(j.b.mean()),
            "effect_b_minus_a": float(j.b.mean() - j.a.mean()), "ci_lo": lo, "ci_hi": hi, "discordant_b_better": b_better,
            "discordant_a_better": a_better, "p_raw": float(p)}


def within_model(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for m in df.model.unique():
        rows = [{"model": m, "a": x, "b": y, **paired(df, {"model": m, "mode": x}, {"model": m, "mode": y})}
                for x, y in itertools.combinations(MODES, 2)]
        for r, ph in zip(rows, holm([r["p_raw"] for r in rows])):
            r["p_holm"] = ph
        out += rows
    return pd.DataFrame(out)


def model_effect(df: pd.DataFrame, frontier: str) -> pd.DataFrame:
    rows = [{"frontier": frontier, "mode": mode, **paired(df, {"model": "qwen2.5:7b", "mode": mode}, {"model": frontier, "mode": mode})}
            for mode in MODES]
    for r, ph in zip(rows, holm([r["p_raw"] for r in rows])):
        r["p_holm"] = ph
    return pd.DataFrame(rows)


def interaction(df: pd.DataFrame, frontier: str) -> pd.DataFrame:
    acc = df.groupby(["model", "mode", "instance_id"]).correct.mean().unstack(["model", "mode"])
    rows = []
    for t in ("COT", "TOT", "GOT"):
        d = ((acc[(frontier, t)] - acc[(frontier, "DIRECT")]) - (acc[("qwen2.5:7b", t)] - acc[("qwen2.5:7b", "DIRECT")])).dropna()
        obs = float(d.mean())
        flips = RNG.choice([-1.0, 1.0], size=(100000, len(d)))
        perm = (flips * d.to_numpy()).mean(axis=1)
        p = float((np.abs(perm) >= abs(obs) - 1e-12).mean())
        lo, hi = inst_boot(lambda s: float(d.loc[s].mean()), list(d.index))
        rows.append({"frontier": frontier, "topology": t, "n_instances": len(d),
                     "topology_effect_frontier": float((acc[(frontier, t)] - acc[(frontier, "DIRECT")]).mean()),
                     "topology_effect_baseline": float((acc[("qwen2.5:7b", t)] - acc[("qwen2.5:7b", "DIRECT")]).mean()),
                     "did": obs, "ci_lo": lo, "ci_hi": hi, "p_raw": p})
    for r, ph in zip(rows, holm([r["p_raw"] for r in rows])):
        r["p_holm"] = ph
    return pd.DataFrame(rows)


def aggregates(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for (m, mode), g in df.groupby(["model", "mode"]):
        insts = list(g.instance_id.unique())
        per = g.groupby("instance_id").correct.mean()
        lo, hi = inst_boot(lambda s: float(per.loc[s].mean()), insts)
        conf = g.confidence.astype(float).to_numpy()
        cor = g.correct.astype(float).to_numpy()
        cost_known = g.cost_usd.notna().all() and len(g)
        acc = float(g.correct.mean())
        out.append({
            "model": m, "mode": mode, "n_runs": len(g), "accuracy": acc, "acc_ci_lo": lo, "acc_ci_hi": hi,
            "accuracy_adversarial": float(g[g.adversarial].correct.mean()), "accuracy_base": float(g[~g.adversarial].correct.mean()),
            "regret_mean": float(g[g.regret_status == "MEASURED"].regret.mean()),
            "confidence_mean": float(np.nanmean(conf)), "ece": frozen.ece(conf, cor), "abstention_rate": float(g.abstained.mean()),
            "consistency": frozen.consistency(g), "evidence_utilization": float(g.evidence_utilization.dropna().astype(float).mean()),
            "contradiction_handled_rate": float(g.contradiction_handled.dropna().astype(float).mean()),
            "uncertainty_preserved_rate": float(g.uncertainty_preserved.dropna().astype(float).mean()),
            "fidelity_rate": float(g.fidelity.dropna().astype(float).mean()) if g.fidelity.notna().any() else np.nan,
            "calls_mean": float(g.n_calls.mean()), "prompt_tokens_mean": float(g.prompt_tokens.mean()),
            "output_tokens_mean": float(g.output_tokens.mean()), "total_tokens_mean": float(g.total_tokens.mean()),
            "reasoning_tokens_mean": float(g.reasoning_tokens.mean()) if "reasoning_tokens" in g and g.reasoning_tokens.notna().any() else np.nan,
            "accuracy_per_1k_output_tokens": acc / g.output_tokens.mean() * 1000,
            "server_compute_s_mean": float(g.latency_s.mean()) if m == "qwen2.5:7b" else np.nan,
            "client_wall_s_mean": float(g.wall_latency_s.mean()) if m != "qwen2.5:7b" else np.nan,
            "cost_usd_total": float(g.cost_usd.sum()) if cost_known else np.nan,
            "cost_usd_per_decision": float(g.cost_usd.mean()) if cost_known else np.nan,
            "correct_per_usd": float(g.correct.sum() / g.cost_usd.sum()) if cost_known else np.nan,
            "truncated_calls": int(g.truncated_calls.sum()) if "truncated_calls" in g and g.truncated_calls.notna().any() else np.nan,
            "failed_runs": int(g.parse_failed.sum()),
        })
    return pd.DataFrame(out)


def adversarial(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (m, var, mode), g in df[df.adversarial].groupby(["model", "variant", "mode"]):
        rows.append({"model": m, "variant": var, "mode": mode, "n": len(g), "accuracy": float(g.correct.mean()),
                     "abstention_rate": float(g.abstained.mean()),
                     "policy_compliance": float(g.policy_compliant.astype(float).mean()) if var == "governance_block" else np.nan,
                     "chose_forbidden": float((g.decision == FORBIDDEN).mean()) if var == "governance_block" else np.nan})
    return pd.DataFrame(rows)


def adversarial_tests(df: pd.DataFrame) -> pd.DataFrame:
    """Exploratory (H4): within-model McNemar vs DIRECT on the 24 adversarial instances."""
    d = df[df.adversarial]
    rows = []
    for m in d.model.unique():
        rr = [{"model": m, "a": "DIRECT", "b": t, **paired(d, {"model": m, "mode": "DIRECT"}, {"model": m, "mode": t})} for t in ("COT", "TOT", "GOT")]
        for r, ph in zip(rr, holm([r["p_raw"] for r in rr])):
            r["p_holm"] = ph
        rows += rr
    return pd.DataFrame(rows)


def fidelity_test(df: pd.DataFrame, frontier: str) -> pd.DataFrame:
    rows = []
    for mode in ("TOT", "GOT"):
        a = df[(df.model == "qwen2.5:7b") & (df["mode"] == mode)].fidelity.dropna().astype(bool)
        b = df[(df.model == frontier) & (df["mode"] == mode)].fidelity.dropna().astype(bool)
        if not len(b):
            continue
        _, p = fisher_exact([[int(a.sum()), int((~a).sum())], [int(b.sum()), int((~b).sum())]])
        rows.append({"frontier": frontier, "mode": mode, "baseline_rate": float(a.mean()), "frontier_rate": float(b.mean()),
                     "n_baseline": len(a), "n_frontier": len(b), "p_fisher_exploratory": float(p)})
    return pd.DataFrame(rows)


def error_decomposition(df: pd.DataFrame) -> pd.DataFrame:
    """Exploratory (not pre-registered): wrong runs split into abstentions where a decision was expected, wrong options
    and failed runs."""
    rows = []
    for (m, mode), g in df.groupby(["model", "mode"]):
        w = g[~g.correct]
        abst = w[w.abstained & ~w.uncertainty_expected.astype(bool)]
        rows.append({"model": m, "mode": mode, "n_runs": len(g), "wrong": len(w), "wrong_abstained": len(abst),
                     "wrong_option": int((~w.abstained & ~w.parse_failed).sum()), "failed": int(w.parse_failed.sum()),
                     "abstained_share_of_wrong": len(abst) / len(w) if len(w) else np.nan,
                     "accuracy_if_abstentions_were_neutral": float(g.correct.sum() / (len(g) - len(abst))) if len(g) > len(abst) else np.nan})
    return pd.DataFrame(rows)


def topology_structure(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in df.columns if c.startswith("topo_") and df[c].dtype != object]
    return df[df["mode"].isin(["COT", "TOT", "GOT"])].groupby(["model", "mode"])[cols].mean().reset_index()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = load_all()
    frontiers = [m for m in df.model.unique() if m != "qwen2.5:7b"]
    keep = [c for c in df.columns if not isinstance(df[c].dropna().iloc[0] if df[c].notna().any() else None, (dict, list))]
    df[keep].to_csv(OUT / "a2-run-level.csv", index=False)
    agg = aggregates(df)
    agg.to_csv(OUT / "a2-results.csv", index=False)
    within_model(df).to_csv(OUT / "a2-within-model.csv", index=False)
    pd.concat([model_effect(df, f) for f in frontiers]).to_csv(OUT / "a2-model-effect.csv", index=False)
    pd.concat([interaction(df, f) for f in frontiers]).to_csv(OUT / "a2-interaction.csv", index=False)
    adversarial(df).to_csv(OUT / "a2-adversarial.csv", index=False)
    adversarial_tests(df).to_csv(OUT / "a2-adversarial-tests.csv", index=False)
    pd.concat([fidelity_test(df, f) for f in frontiers]).to_csv(OUT / "a2-fidelity.csv", index=False)
    topology_structure(df).to_csv(OUT / "a2-topology-structure.csv", index=False)
    error_decomposition(df).to_csv(OUT / "a2-error-decomposition.csv", index=False)
    print(agg[["model", "mode", "n_runs", "accuracy", "acc_ci_lo", "acc_ci_hi", "fidelity_rate", "output_tokens_mean", "cost_usd_total"]].round(3).to_string())


if __name__ == "__main__":
    main()
