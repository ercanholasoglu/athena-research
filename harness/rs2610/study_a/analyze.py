"""Study A analysis: run-level CSV, aggregates, paired statistics, figures.

    python -m rs2610.study_a.analyze
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter
from scipy.stats import binomtest

from rs2610.common.llm import backfill, ledger_compute
from rs2610.common.viz import INK2, MARKERS, SERIES, bars, plt, save
from rs2610.study_a.scoring import score_run
from rs2610.study_a.topologies import MODES

ART = Path(__file__).resolve().parents[1] / "artifacts" / "study_a"
OUT = Path(__file__).resolve().parents[1] / "outputs" / "study_a"
FIG = OUT / "study-a-figures"
TAGS = ("dev", "unseen")
TABLE: dict = {}
B = 2000
RNG = np.random.default_rng(7)


def claim_sources_from_ledger() -> dict[str, dict[str, list[str]]]:
    """request_hash of a GoT claims call -> {claim id: source evidence}; for runs written before traces stored it."""
    out = {}
    for line in (ART / "ledger.jsonl").read_text().splitlines():
        rec = json.loads(line)
        if (rec.get("tag") or {}).get("stage") == "extract_claims" and isinstance(rec.get("content"), dict):
            out[rec["request_hash"]] = {c["id"]: list(c.get("source", []) or []) for c in rec["content"].get("claims", [])
                                        if isinstance(c, dict) and c.get("id")}
    return out


def load() -> pd.DataFrame:
    """Every run is rescored with the current scoring code, so DEVELOPMENT and UNSEEN rows are scored identically."""
    global TABLE
    TABLE = ledger_compute(ART / "ledger.jsonl")
    cs = claim_sources_from_ledger()
    insts = {}
    for f in (ART / "instances").glob("*.json"):
        insts.update({i["instance_id"]: i for i in json.loads(f.read_text())})
    rows = []
    for tag in TAGS:
        p = ART / f"runs_{tag}.jsonl"
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            r = json.loads(line)
            t = r.pop("trace")
            st = t.get("structure")
            if r["mode"] == "GOT" and isinstance(st, dict) and "claim_sources" not in st:
                h = next((c["request_hash"] for c in t["calls"] if c["stage"] == "extract_claims"), None)
                st["claim_sources"] = cs.get(h, {})
            backfill(t["calls"], TABLE)  # compute_s from the ledger for rows written before it was recorded
            if r["instance_id"] in insts:
                r.update(score_run(insts[r["instance_id"]], t))
            if r.get("latency_s") is None or "latency_status" not in r:  # rows written before compute_s existed
                backfill(t["calls"], TABLE)
                cs = [c.get("compute_s") for c in t["calls"]]
                r["wall_latency_s"] = r.get("wall_latency_s", r.get("latency_s"))
                r["latency_s"] = sum(cs) if all(x is not None for x in cs) else None
                r["latency_status"] = "ACTUAL_SERVER_COMPUTE (prefill+decode)"
            topo = r.pop("topology", {}) or {}
            for k, v in topo.items():
                if isinstance(v, (int, float, bool)):
                    r[f"topo_{k}"] = v
            r["fidelity"] = fidelity(r["mode"], t, r["decision"])
            r["prefill_s"] = None
            r["run_tag"] = tag
            rows.append(r)
    return pd.DataFrame(rows)


def fidelity(mode: str, t: dict, decision: str | None) -> bool | None:
    """Does the final decision follow the topology's own ranking?"""
    st = t.get("structure")
    if mode == "TOT" and st:
        kept = [b for b in st if b["kept"]]
        return bool(kept) and decision == max(kept, key=lambda b: b["score"])["option"]
    if mode == "GOT" and isinstance(st, dict) and st.get("scores"):
        sc = st["scores"]
        top = max(sc, key=sc.get)
        return decision in (top, st.get("merged"))
    return None


def cluster_boot(df: pd.DataFrame, col: str, stat=np.mean) -> tuple[float, float, float]:
    """Point estimate + 95 % CI resampling datasets (clusters) with replacement."""
    d = df.dropna(subset=[col])
    if d.empty:
        return (np.nan, np.nan, np.nan)
    groups = [g[col].astype(float).to_numpy() for _, g in d.groupby("dataset_id")]
    est = float(stat(d[col].astype(float)))
    boots = []
    for _ in range(B):
        pick = RNG.integers(0, len(groups), len(groups))
        boots.append(stat(np.concatenate([groups[i] for i in pick])))
    return est, float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def ece(conf: np.ndarray, correct: np.ndarray, bins: int = 10) -> float:
    m = ~np.isnan(conf)
    conf, correct = conf[m], correct[m]
    idx = np.clip((conf * bins).astype(int), 0, bins - 1)
    return float(sum((idx == b).mean() * abs(correct[idx == b].mean() - conf[idx == b].mean()) for b in range(bins) if (idx == b).any()))


def auroc(conf: np.ndarray, correct: np.ndarray) -> float | None:
    from sklearn.metrics import roc_auc_score
    m = ~np.isnan(conf)
    if len(set(correct[m])) < 2:
        return None
    return float(roc_auc_score(correct[m], conf[m]))


def consistency(df: pd.DataFrame) -> float:
    vals = []
    for _, g in df.groupby("instance_id"):
        d = g["decision"].fillna("<FAIL>").tolist()
        if len(d) < 2:
            continue
        pairs = list(itertools.combinations(d, 2))
        vals.append(np.mean([a == b for a, b in pairs]))
    return float(np.mean(vals)) if vals else np.nan


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for (split, mode), g in df.groupby(["split", "mode"]):
        acc = cluster_boot(g, "correct")
        reg = cluster_boot(g[g.regret_status == "MEASURED"], "regret")
        conf = g["confidence"].astype(float).to_numpy()
        cor = g["correct"].astype(float).to_numpy()
        unc = g[g.uncertainty_expected]
        con = g[g.contradiction_handled.notna()]
        out.append({
            "split": split, "mode": mode, "n_runs": len(g), "n_instances": g.instance_id.nunique(), "n_seeds": g.seed.nunique(),
            "accuracy": acc[0], "accuracy_ci_lo": acc[1], "accuracy_ci_hi": acc[2],
            "accuracy_base": g[~g.adversarial].correct.mean(), "accuracy_adversarial": g[g.adversarial].correct.mean(),
            "regret_mean": reg[0], "regret_ci_lo": reg[1], "regret_ci_hi": reg[2],
            "regret_n_measured": int((g.regret_status == "MEASURED").sum()),
            "abstention_rate": g.abstained.mean(), "parse_failure_rate": g.parse_failed.mean(),
            "unnecessary_complexity_rate": g[g.correct].unnecessary_complexity.mean(),
            "uncertainty_preserved_rate": unc.uncertainty_preserved.mean() if len(unc) else np.nan, "n_uncertainty_runs": len(unc),
            "contradiction_handled_rate": con.contradiction_handled.astype(float).mean() if len(con) else np.nan,
            "evidence_utilization": g.evidence_utilization.mean(),
            "confidence_mean": np.nanmean(conf), "ece": ece(conf, cor), "brier_conf": float(np.nanmean((conf - cor) ** 2)),
            "auroc_conf": auroc(conf, cor), "overconfident_wrong_rate": float(((conf >= 0.9) & (cor == 0)).mean()),
            "consistency": consistency(g) if g.seed.nunique() > 1 else np.nan,
            "calls_mean": g.n_calls.mean(), "prompt_tokens_mean": g.prompt_tokens.mean(), "output_tokens_mean": g.output_tokens.mean(),
            "total_tokens_mean": (g.prompt_tokens + g.output_tokens).mean(), "prompt_tokens_sum": int(g.prompt_tokens.sum()),
            "output_tokens_sum": int(g.output_tokens.sum()), "latency_s_sum": g.latency_s.sum(min_count=len(g)),
            "latency_s_mean": g.latency_s.mean(), "fidelity_rate": g.fidelity.dropna().astype(float).mean() if g.fidelity.notna().any() else np.nan,
            "tokens_status": "ACTUAL" if (g.tokens_status == "ACTUAL").all() else "PARTIAL_UNKNOWN",
            "cost_usd": None, "cost_status": "NOT_APPLICABLE_LOCAL (no provider bill; energy UNKNOWN)",
        })
    a = pd.DataFrame(out)
    a["accuracy_per_1k_output_tokens"] = a.accuracy / (a.output_tokens_mean / 1000)
    a["accuracy_per_minute"] = a.accuracy / (a.latency_s_mean / 60)
    return a


def paired(df: pd.DataFrame, split: str) -> pd.DataFrame:
    """Per-instance majority correctness → exact McNemar + dataset-cluster bootstrap of the difference; Holm across pairs."""
    d = df[df.split == split]
    inst = d.groupby(["instance_id", "mode"]).agg(c=("correct", "mean"), ds=("dataset_id", "first")).reset_index()
    wide = inst.pivot(index="instance_id", columns="mode", values="c")
    dsmap = inst.drop_duplicates("instance_id").set_index("instance_id")["ds"]
    rows = []
    for a, b in itertools.combinations(MODES, 2):
        if a not in wide or b not in wide:
            continue
        w = wide[[a, b]].dropna()
        ma, mb = (w[a] > 0.5).astype(int), (w[b] > 0.5).astype(int)
        n01, n10 = int(((ma == 0) & (mb == 1)).sum()), int(((ma == 1) & (mb == 0)).sum())
        p = binomtest(n01, n01 + n10, 0.5).pvalue if n01 + n10 else 1.0
        diff = (w[b] - w[a])
        groups = [diff[dsmap[diff.index] == ds].to_numpy() for ds in dsmap[diff.index].unique()]
        boots = [np.mean(np.concatenate([groups[i] for i in RNG.integers(0, len(groups), len(groups))])) for _ in range(B)]
        rows.append({"split": split, "a": a, "b": b, "n_instances": len(w), "acc_a": w[a].mean(), "acc_b": w[b].mean(),
                     "diff_b_minus_a": diff.mean(), "ci_lo": np.percentile(boots, 2.5), "ci_hi": np.percentile(boots, 97.5),
                     "discordant_a_wrong_b_right": n01, "discordant_a_right_b_wrong": n10, "mcnemar_exact_p": p})
    r = pd.DataFrame(rows)
    if len(r):
        order = np.argsort(r.mcnemar_exact_p.to_numpy())
        m = len(r)
        adj = np.empty(m)
        running = 0.0
        for rank, i in enumerate(order):
            running = max(running, min(1.0, (m - rank) * r.mcnemar_exact_p.iloc[i]))
            adj[i] = running
        r["holm_p"] = adj
    return r


def holm(p: np.ndarray) -> np.ndarray:
    order, m, adj, running = np.argsort(p), len(p), np.empty(len(p)), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * p[i]))
        adj[i] = running
    return adj


def paired_by_family(df: pd.DataFrame, split: str) -> pd.DataFrame:
    """Exploratory heterogeneity: each topology vs CoT inside each task family; exact McNemar on instance-majority
    correctness, Holm across every (family, contrast) test of the split."""
    d = df[df.split == split]
    rows = []
    for fam, g in d.groupby("family"):
        wide = g.groupby(["instance_id", "mode"]).correct.mean().unstack()
        for b in ("DIRECT", "TOT", "GOT"):
            if "COT" not in wide or b not in wide:
                continue
            w = wide[["COT", b]].dropna()
            ma, mb = (w["COT"] > 0.5).astype(int), (w[b] > 0.5).astype(int)
            n01, n10 = int(((ma == 0) & (mb == 1)).sum()), int(((ma == 1) & (mb == 0)).sum())
            rows.append({"split": split, "family": fam, "a": "COT", "b": b, "n_instances": len(w), "acc_a": w["COT"].mean(),
                         "acc_b": w[b].mean(), "diff_b_minus_a": (w[b] - w["COT"]).mean(), "discordant_a_wrong_b_right": n01,
                         "discordant_a_right_b_wrong": n10,
                         "mcnemar_exact_p": binomtest(n01, n01 + n10, 0.5).pvalue if n01 + n10 else 1.0})
    r = pd.DataFrame(rows)
    if len(r):
        r["holm_p"] = holm(r.mcnemar_exact_p.to_numpy())
        r["status"] = "EXPLORATORY"
    return r


def _mcnemar(wide: pd.DataFrame, a: str, b: str, dsmap: pd.Series) -> dict:
    w = wide[[a, b]].dropna()
    ma, mb = (w[a] > 0.5).astype(int), (w[b] > 0.5).astype(int)
    n01, n10 = int(((ma == 0) & (mb == 1)).sum()), int(((ma == 1) & (mb == 0)).sum())
    diff = w[b] - w[a]
    ds = dsmap[diff.index]
    groups = [diff[ds == k].to_numpy() for k in ds.unique()]
    boots = [np.mean(np.concatenate([groups[i] for i in RNG.integers(0, len(groups), len(groups))])) for _ in range(B)] if groups else [np.nan]
    return {"n_instances": len(w), "mean_a": w[a].mean(), "mean_b": w[b].mean(), "effect_b_minus_a": diff.mean(),
            "ci_lo": np.nanpercentile(boots, 2.5), "ci_hi": np.nanpercentile(boots, 97.5), "discordant_b_better": n01,
            "discordant_a_better": n10, "p_raw": binomtest(n01, n01 + n10, 0.5).pvalue if n01 + n10 else 1.0, "test": "exact McNemar"}


def confirmatory(df: pd.DataFrame, split: str = "UNSEEN") -> pd.DataFrame:
    """H1-H4 exactly as pre-registered (study-a-design.md); Holm within each hypothesis family."""
    d = df[df.split == split]
    if d.empty:
        return pd.DataFrame()
    dsmap = d.drop_duplicates("instance_id").set_index("instance_id")["dataset_id"]
    out = []
    acc = d.groupby(["instance_id", "mode"]).correct.mean().unstack()
    for a, b in itertools.combinations(MODES, 2):  # H1
        out.append({"hypothesis": "H1", "metric": "accuracy", "a": a, "b": b, **_mcnemar(acc, a, b, dsmap)})
    adv = d[d.adversarial].groupby(["instance_id", "mode"]).correct.mean().unstack()
    for b in ("TOT", "GOT"):  # H2
        out.append({"hypothesis": "H2", "metric": "adversarial accuracy", "a": "COT", "b": b, **_mcnemar(adv, "COT", b, dsmap)})
    unc = d[d.uncertainty_expected].assign(u=lambda x: x.uncertainty_preserved.astype(float))
    unc = unc.groupby(["instance_id", "mode"]).u.mean().unstack()
    for a in ("COT", "DIRECT"):  # H3
        for b in ("TOT", "GOT"):
            out.append({"hypothesis": "H3", "metric": "uncertainty preserved", "a": a, "b": b, **_mcnemar(unc, a, b, dsmap)})
    # H4: accuracy per 1k output tokens; paired dataset-cluster bootstrap of the difference of ratios
    per_ds = d.groupby(["dataset_id", "mode"]).agg(c=("correct", "sum"), t=("output_tokens", "sum")).unstack()
    dss = per_ds.index.to_numpy()

    def eff(idx, m):
        sub = per_ds.loc[idx]
        return sub[("c", m)].sum() / (sub[("t", m)].sum() / 1000)
    for a in ("DIRECT", "COT"):
        for b in ("TOT", "GOT"):
            est = eff(dss, a) - eff(dss, b)
            boots = []
            for _ in range(B):
                idx = dss[RNG.integers(0, len(dss), len(dss))]  # same resampled datasets for both arms (paired)
                boots.append(eff(idx, a) - eff(idx, b))
            boots = np.array(boots)
            p = min(1.0, 2 * min((boots <= 0).mean(), (boots >= 0).mean()))
            out.append({"hypothesis": "H4", "metric": "accuracy per 1k output tokens", "a": a, "b": b, "n_instances": d.instance_id.nunique(),
                        "mean_a": eff(dss, a), "mean_b": eff(dss, b), "effect_b_minus_a": -est,
                        "ci_lo": float(np.percentile(-boots, 2.5)), "ci_hi": float(np.percentile(-boots, 97.5)),
                        "p_raw": p, "test": "paired dataset-cluster bootstrap (two-sided)"})
    r = pd.DataFrame(out)
    r["p_holm"] = np.nan
    for h, g in r.groupby("hypothesis"):
        r.loc[g.index, "p_holm"] = holm(g.p_raw.to_numpy())
    r["split"] = split
    r["status"] = "CONFIRMATORY (pre-registered)"
    return r


def topology_figure(df: pd.DataFrame, split: str, tag: str) -> None:
    d = df[df.split == split]
    tot, got = d[d["mode"] == "TOT"], d[d["mode"] == "GOT"]
    if tot.empty or got.empty:
        return
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.6))
    tcols = [("topo_branches", "branches proposed"), ("topo_pruned", "branches pruned"), ("topo_leaves", "refinement leaves"),
             ("topo_duplicate_proposals", "duplicate proposals")]
    tcols = [(c, l) for c, l in tcols if c in tot]
    bars(axs[0], [l for _, l in tcols], [tot[c].mean() for c, _ in tcols], fmt="{:.2f}", colors=[SERIES[2]] * len(tcols),
         ylabel="mean per ToT decision")
    axs[0].set_title(f"ToT structure — {split.lower()} (n = {len(tot)} runs)", fontsize=10)
    gcols = [("topo_claim_nodes", "claim nodes"), ("topo_candidate_nodes", "candidate nodes"), ("topo_edges", "edges"),
             ("topo_reused_claims", "claims reused\nby ≥ 2 candidates"), ("topo_claim_conflict_edges", "claim conflicts"),
             ("topo_merged_nodes", "merged path\n(share)")]
    gcols = [(c, l) for c, l in gcols if c in got]
    bars(axs[1], [l for _, l in gcols], [got[c].mean() for c, _ in gcols], fmt="{:.2f}", colors=[SERIES[3]] * len(gcols),
         ylabel="mean per GoT decision")
    axs[1].set_title(f"GoT structure — {split.lower()} (n = {len(got)} runs; "
                     f"{got.topo_is_dag_beyond_tree.astype(float).mean():.0%} non-tree)", fontsize=10)
    for ax in axs:
        ax.tick_params(axis="x", labelsize=7.5)
    save(fig, FIG / f"topology_complexity_{tag}.png")


def paired_regret(df: pd.DataFrame, split: str) -> pd.DataFrame:
    d = df[(df.split == split) & (df.regret_status == "MEASURED")]
    inst = d.groupby(["instance_id", "mode"]).regret.mean().unstack()
    rows = []
    for a, b in itertools.combinations(MODES, 2):
        if a in inst and b in inst:
            w = inst[[a, b]].dropna()
            diff = (w[b] - w[a]).to_numpy()
            boots = [np.mean(RNG.choice(diff, len(diff))) for _ in range(B)] if len(diff) else [np.nan]
            rows.append({"split": split, "a": a, "b": b, "n_instances": len(w), "regret_a": w[a].mean(), "regret_b": w[b].mean(),
                         "diff_b_minus_a": diff.mean() if len(diff) else np.nan,
                         "ci_lo": np.percentile(boots, 2.5), "ci_hi": np.percentile(boots, 97.5)})
    return pd.DataFrame(rows)


def figures(df: pd.DataFrame, agg: pd.DataFrame) -> None:
    labels = list(MODES)
    for split in ("DEVELOPMENT", "UNSEEN"):
        a = agg[agg.split == split].set_index("mode").reindex(labels)
        if a.accuracy.isna().all():
            continue
        tag = "dev" if split == "DEVELOPMENT" else "unseen"
        fig, ax = plt.subplots(figsize=(6, 3.6))
        bars(ax, labels, a.accuracy.tolist(), list(zip(a.accuracy_ci_lo, a.accuracy_ci_hi)), ylabel="decision accuracy", ylim=(0, 1.05))
        ax.set_title(f"Decision accuracy by reasoning mode — {split.lower()} ({int(a.n_instances.max())} instances, "
                     f"{int(a.n_seeds.max())} seed{'s' if a.n_seeds.max() > 1 else ''})")
        ax.text(0, -0.2, "95 % CI: dataset-cluster bootstrap", transform=ax.transAxes, fontsize=8, color=INK2)
        save(fig, FIG / f"accuracy_by_mode_{tag}.png")
        topology_figure(df, split, tag)
        for col, yl, fname, fmt in [("output_tokens_mean", "output tokens per decision (ACTUAL)", "tokens", "{:.0f}"),
                                    ("latency_s_mean", "seconds per decision (ACTUAL, local 7B)", "latency", "{:.1f}"),
                                    ("calls_mean", "model calls per decision", "calls", "{:.1f}")]:
            fig, ax = plt.subplots(figsize=(6, 3.4))
            bars(ax, labels, a[col].tolist(), fmt=fmt, ylabel=yl)
            ax.set_title(f"{yl.split(' (')[0].capitalize()} — {split.lower()}")
            save(fig, FIG / f"{fname}_by_mode_{tag}.png")
        for xcol, xl, fname in [("output_tokens_mean", "output tokens per decision", "quality_vs_tokens"),
                                ("latency_s_mean", "seconds per decision", "quality_vs_latency")]:
            fig, ax = plt.subplots(figsize=(6, 3.8))
            for i, m in enumerate(labels):
                r = a.loc[m]
                ax.errorbar(r[xcol], r.accuracy, yerr=[[r.accuracy - r.accuracy_ci_lo], [r.accuracy_ci_hi - r.accuracy]], fmt=MARKERS[i],
                            color=SERIES[i], ms=9, ecolor=SERIES[i], elinewidth=1.2, capsize=3, mec="#fcfcfb", mew=2)
                ax.annotate(m, (r[xcol], r.accuracy), xytext=(8, 4), textcoords="offset points", fontsize=9, color="#0b0b0b")
            ax.set_xscale("log")
            ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
            ax.xaxis.set_minor_formatter(FuncFormatter(lambda v, _: ""))
            ax.set_xlabel(xl + " (log scale)")
            ax.set_ylabel("decision accuracy")
            ax.set_title(f"Quality vs {'tokens' if 'tokens' in xcol else 'latency'} — {split.lower()}")
            save(fig, FIG / f"{fname}_{tag}.png")
        # calibration: reliability small multiples
        d = df[df.split == split]
        fig, axs = plt.subplots(1, 4, figsize=(11, 3.1), sharey=True)
        for i, m in enumerate(labels):
            g = d[d["mode"] == m].dropna(subset=["confidence"])
            ax = axs[i]
            ax.plot([0, 1], [0, 1], color=INK2, lw=1, ls="--")
            edges = np.array([0, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0001])
            idx = np.digitize(g.confidence, edges) - 1
            xs, ys, ns = [], [], []
            for b in range(len(edges) - 1):
                s = g[idx == b]
                if len(s):
                    xs.append(s.confidence.mean()), ys.append(s.correct.mean()), ns.append(len(s))
            ax.plot(xs, ys, color=SERIES[i], lw=2, marker=MARKERS[i], ms=8, mec="#fcfcfb", mew=2)
            for x, y, n in zip(xs, ys, ns):
                ax.annotate(str(n), (x, y), xytext=(0, -13), textcoords="offset points", fontsize=7, ha="center", color=INK2)
            r = agg[(agg.split == split) & (agg["mode"] == m)].iloc[0]
            ax.set_title(f"{m}  ECE {r.ece:.2f}", fontsize=10)
            ax.set_xlim(0, 1.02), ax.set_ylim(0, 1.05)
            ax.set_xlabel("stated confidence")
        axs[0].set_ylabel("observed accuracy")
        fig.suptitle(f"Confidence calibration — {split.lower()} (labels = runs per bin)", x=0.01, ha="left", fontsize=11, fontweight="bold")
        save(fig, FIG / f"calibration_{tag}.png")
        # per-family small multiples
        fam = d.groupby(["family", "mode"]).correct.mean().unstack().reindex(columns=labels)
        fams = fam.index.tolist()
        fig, ax = plt.subplots(figsize=(10, 3.8))
        w = 0.2
        for i, m in enumerate(labels):
            ax.bar(np.arange(len(fams)) + (i - 1.5) * w, fam[m], width=w, color=SERIES[i], edgecolor="#fcfcfb", linewidth=1.5, label=m)
        ax.set_xticks(np.arange(len(fams)), [f.replace("_", "\n") for f in fams], fontsize=7)
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("decision accuracy")
        ax.legend(ncol=4, loc="upper left", bbox_to_anchor=(0, 1.15))
        ax.grid(axis="x", visible=False)
        ax.set_title(f"Accuracy per task family — {split.lower()}", pad=24)
        save(fig, FIG / f"per_family_{tag}.png")
        # adversarial behaviours
        adv = d[d.adversarial]
        if len(adv):
            kinds = sorted(adv.variant.unique())
            t = adv.groupby(["variant", "mode"]).correct.mean().unstack().reindex(columns=labels)
            fig, ax = plt.subplots(figsize=(10, 3.6))
            for i, m in enumerate(labels):
                ax.bar(np.arange(len(kinds)) + (i - 1.5) * w, t.loc[kinds, m], width=w, color=SERIES[i], edgecolor="#fcfcfb", linewidth=1.5, label=m)
            ax.set_xticks(np.arange(len(kinds)), [k.replace("_", "\n") for k in kinds], fontsize=7)
            ax.set_ylim(0, 1.05)
            ax.set_ylabel("decision accuracy")
            ax.legend(ncol=4, loc="upper left", bbox_to_anchor=(0, 1.15))
            ax.grid(axis="x", visible=False)
            ax.set_title(f"Adversarial cases — {split.lower()}", pad=24)
            save(fig, FIG / f"adversarial_{tag}.png")
    # generalization: dev vs unseen side by side
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    w = 0.36
    for j, (split, hatch) in enumerate([("DEVELOPMENT", ""), ("UNSEEN", "")]):
        a = agg[agg.split == split].set_index("mode").reindex(labels)
        if a.accuracy.isna().all():
            continue
        xs = np.arange(4) + (j - 0.5) * w
        ax.bar(xs, a.accuracy, width=w, color=SERIES[:4], alpha=0.45 if j == 0 else 1.0, edgecolor="#fcfcfb", linewidth=2,
               yerr=[a.accuracy - a.accuracy_ci_lo, a.accuracy_ci_hi - a.accuracy], error_kw={"ecolor": INK2, "elinewidth": 1, "capsize": 3})
        for x, v in zip(xs, a.accuracy):
            ax.text(x, 0.02, f"{v:.2f}", ha="center", fontsize=7, color="#0b0b0b", rotation=90)
    ax.set_xticks(range(4), labels)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("decision accuracy")
    ax.grid(axis="x", visible=False)
    ax.set_title("Development (pale, left) vs unseen (solid, right)")
    save(fig, FIG / "dev_vs_unseen.png")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = load()
    keep = [c for c in df.columns if c not in ("prefill_s",)]
    df[keep].to_csv(OUT / "study-a-run-level-results.csv", index=False)
    agg = aggregate(df)
    agg.to_csv(OUT / "study-a-results.csv", index=False)
    pr = pd.concat([paired(df, s) for s in df.split.unique()], ignore_index=True)
    pr.to_csv(OUT / "study-a-paired-tests.csv", index=False)
    rg = pd.concat([paired_regret(df, s) for s in df.split.unique()], ignore_index=True)
    rg.to_csv(OUT / "study-a-paired-regret.csv", index=False)
    confirmatory(df).to_csv(OUT / "study-a-confirmatory.csv", index=False)
    pf = pd.concat([paired_by_family(df, s) for s in df.split.unique()], ignore_index=True)
    pf.to_csv(OUT / "study-a-paired-by-family.csv", index=False)
    fam = df.groupby(["split", "family", "mode"]).agg(acc=("correct", "mean"), n=("correct", "size"),
                                                       regret=("regret", "mean")).reset_index()
    fam.to_csv(OUT / "study-a-per-family.csv", index=False)
    adv = df[df.adversarial].groupby(["split", "variant", "mode"]).agg(
        acc=("correct", "mean"), uncertainty_preserved=("uncertainty_preserved", "mean"),
        contradiction_handled=("contradiction_handled", lambda s: s.dropna().astype(float).mean() if s.notna().any() else np.nan),
        conf=("confidence", "mean"), n=("correct", "size")).reset_index()
    adv.to_csv(OUT / "study-a-adversarial.csv", index=False)
    topo = df.groupby(["split", "mode"])[[c for c in df.columns if c.startswith("topo_")]].mean(numeric_only=True).reset_index()
    topo.to_csv(OUT / "study-a-topology-stats.csv", index=False)
    figures(df, agg)
    pd.set_option("display.width", 250)
    print(agg[["split", "mode", "n_runs", "accuracy", "accuracy_ci_lo", "accuracy_ci_hi", "regret_mean", "abstention_rate",
               "ece", "consistency", "output_tokens_mean", "latency_s_mean", "fidelity_rate"]].round(3).to_string())
    print(pr.round(4).to_string())


if __name__ == "__main__":
    main()
