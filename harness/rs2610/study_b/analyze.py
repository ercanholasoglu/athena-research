"""Study B analysis.

    python -m rs2610.study_b.analyze
"""
from __future__ import annotations

import itertools
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter
from scipy.stats import binomtest, wilcoxon

from rs2610.common.viz import INK, INK2, MARKERS, SERIES, SURFACE, bars, plt, save
from rs2610.study_b.conditions import CONDITIONS
from rs2610.study_b.evaluate import downstream, references, setup, validate_feature
from rs2610.study_b.profile import profile
from rs2610.study_b.score import score

ART = Path(__file__).resolve().parents[1] / "artifacts" / "study_b"
OUT = Path(__file__).resolve().parents[1] / "outputs" / "study_b"
FIG = OUT / "study-b-figures"
TAGS = ("dev", "unseen")
B = 2000
RNG = np.random.default_rng(11)
COND_LABEL = {"A_RAW": "A raw schema", "B_SELF": "B self-inference", "C_DICT": "C dictionary", "D_RULES": "D dict + rules",
              "E_FULL": "E full + verify"}


@lru_cache(maxsize=None)
def strongest_non_actionable(did: str) -> str | None:
    st = setup(did)
    v = st["v"]
    rows = profile(v, st["dev"])
    t = v.truth
    skip = set(t["ids_all"]) | set(t["leak_all"]) | set(t.get("actionable", []))
    cand = [r for r in rows if r["column"] not in skip and r["target_association"] is not None]
    return max(cand, key=lambda r: r["target_association"])["column"] if cand else None


def load() -> list[dict]:
    from rs2610.common.llm import backfill, ledger_compute
    table = ledger_compute(ART / "ledger.jsonl")
    rows = []
    for tag in TAGS:
        p = ART / f"runs_{tag}.jsonl"
        if p.exists():
            rows += [json.loads(line) for line in p.read_text().splitlines()]
    for r in rows:
        backfill(r["trace"]["calls"], table)
    return rows


def process(rows: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame]:
    dec, feats = [], []
    for r in rows:
        did = r["dataset_id"]
        st = setup(did)
        v = st["v"]
        s = score(r, v.truth, list(v.frame.columns), strongest_non_actionable(did))
        blocked = set(s.pop("_blocked"))
        lever = s.pop("_lever")
        fe = r["trace"].get("fe") or {}
        retained = []
        props = fe.get("proposed_features", []) or []
        n_valid, n_leaky_retained, n_invalid_retained = 0, 0, 0
        for f in props:
            val = validate_feature(did, f, r.get("rename") or {})
            ins = val["inputs"]
            reason = None
            if not val.get("computable"):
                reason = f"not computable ({val.get('failure')})"
            elif st["v"].target in ins:
                reason = "uses the target column"
            elif f.get("leakage_assessment") == "likely":
                reason = "own leakage assessment: likely"
            elif set(ins) & blocked:
                reason = "uses a column the run itself blocked"
            elif val.get("cv_gain", 0) <= 0:
                reason = "no CV gain"
            keep = reason is None
            if keep:
                retained.append({"op": f.get("op"), "inputs": ins})
                n_leaky_retained += val["leakage_risk"] == "HIGH"
                n_invalid_retained += val["semantic_validity"] == "invalid"
            n_valid += val["semantic_validity"] == "valid" and val["leakage_risk"] == "LOW"
            feats.append({"dataset_id": did, "split": r["split"], "variant": r["variant"], "condition": r["condition"], "seed": r["seed"],
                          "name": f.get("name"), "op": f.get("op"), "inputs": "|".join(ins), "semantic_rationale": f.get("semantic_rationale"),
                          "statistical_rationale": f.get("statistical_rationale"), "model_leakage_assessment": f.get("leakage_assessment"),
                          "business_interpretation": f.get("business_interpretation"),
                          "statistical_value_cv_gain": val.get("cv_gain"), "semantic_validity": val["semantic_validity"],
                          "leakage_risk": val["leakage_risk"], "stability": val.get("stability"), "interpretability": val.get("interpretability"),
                          "generalization_test_gain": val.get("test_gain_deploy"), "computable": val.get("computable"),
                          "retained": keep, "rejection_reason": reason,
                          "statistically_strong_semantically_invalid": bool((val.get("cv_gain") or 0) > 0.005 and
                                                                            (val["semantic_validity"] == "invalid" or val["leakage_risk"] == "HIGH"))})
        an = r["trace"].get("analysis") or {}
        down = downstream(did, sorted(blocked), retained, an.get("split_strategy"),
                          (r.get("rename") or {}).get(an.get("group_column"), an.get("group_column")))
        ref = references(did)
        s.update({"dataset_id": did, "split": r["split"], "variant": r["variant"], "condition": r["condition"], "seed": r["seed"],
                  "lever": lever, "blocked": "|".join(sorted(blocked)), "n_retained_features": len(retained),
                  "feature_valid_share": n_valid / len(props) if props else np.nan,
                  "retained_leaky": n_leaky_retained, "retained_invalid": n_invalid_retained,
                  "deploy_score": down["test_deploy"], "naive_score": down["test_naive"], "leak_inflation": down["leak_inflation"],
                  "estimate_error": down["estimate_error"], "cv_estimate": down["cv_estimate"],
                  "oracle_deploy": ref["oracle_clean"]["test_deploy"], "use_everything_deploy": ref["use_everything"]["test_deploy"],
                  "use_everything_naive": ref["use_everything"]["test_naive"],
                  "deploy_gap_to_oracle": ref["oracle_clean"]["test_deploy"] - down["test_deploy"],
                  "deploy_collapse": bool(down["leak_inflation"] > COLLAPSE)})
        dec.append(s)
    return pd.DataFrame(dec), pd.DataFrame(feats)


def cboot(df: pd.DataFrame, col: str) -> tuple[float, float, float]:
    d = df.dropna(subset=[col])
    if d.empty:
        return (np.nan, np.nan, np.nan)
    groups = [g[col].astype(float).to_numpy() for _, g in d.groupby("dataset_id")]
    est = float(d[col].astype(float).mean())
    bs = [np.mean(np.concatenate([groups[i] for i in RNG.integers(0, len(groups), len(groups))])) for _ in range(B)]
    return est, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


COLLAPSE = 0.05  # pre-registered: the shipped model loses > 0.05 AUC/R² when deployment hides post-outcome values


METRICS = ["deploy_collapse", "task_understanding", "target_semantic", "grain", "temporal", "id_recall", "id_trap_caught", "post_event_recall",
           "post_event_flagged_as_post", "leak_recall", "leak_precision", "artifact_caught", "all_traps_blocked", "over_exclusion",
           "actionability_precision", "lever_actionable", "lever_is_predictive_trap", "intent", "metric", "split_correct",
           "candidate_accuracy", "cand_semantic_correct", "cand_identifier_correct", "cand_post_outcome_correct", "cand_artifact_correct",
           "cand_target_leak_correct", "feature_valid_share", "retained_leaky", "retained_invalid", "n_retained_features",
           "deploy_score", "deploy_gap_to_oracle", "leak_inflation", "estimate_error", "semantic_confidence",
           "missing_semantics_recall", "falsified_detected_recall", "false_contradictions", "n_calls", "prompt_tokens", "output_tokens",
           "latency_s", "analysis_ok"]
CORE = ["task_understanding", "target_semantic", "grain", "temporal", "intent", "metric", "split_correct"]


def aggregate(dec: pd.DataFrame) -> pd.DataFrame:
    out = []
    for (split, variant, cond), g in dec.groupby(["split", "variant", "condition"]):
        row = {"split": split, "variant": variant, "condition": cond, "n_runs": len(g), "n_datasets": g.dataset_id.nunique(),
               "n_seeds": g.seed.nunique()}
        for m in METRICS:
            if m in g and g[m].notna().any():
                est, lo, hi = cboot(g.assign(**{m: g[m].astype(float)}), m)
                row[m], row[f"{m}_lo"], row[f"{m}_hi"] = est, lo, hi
        row["core_semantic_accuracy"] = g[CORE].astype(float).mean(axis=1).mean()
        row["deploy_gap_to_oracle_median"] = g.deploy_gap_to_oracle.median()
        row["tokens_status"] = "ACTUAL"
        row["cost_usd"] = None
        row["cost_status"] = "NOT_APPLICABLE_LOCAL (no provider bill; energy UNKNOWN)"
        out.append(row)
    return pd.DataFrame(out)


def paired_vs_raw(dec: pd.DataFrame, split: str, variant: str = "trapped", ref: str = "A_RAW") -> pd.DataFrame:
    d = dec[(dec.split == split) & (dec.variant == variant)].copy()
    d["core_semantic_accuracy"] = d[CORE].astype(float).mean(axis=1)
    rows = []
    for m in ["core_semantic_accuracy", "task_understanding", "leak_recall", "all_traps_blocked", "candidate_accuracy",
              "feature_valid_share", "deploy_score", "deploy_gap_to_oracle", "deploy_collapse", "estimate_error", "over_exclusion",
              "output_tokens"]:
        wide = d.pivot_table(index=["dataset_id", "seed"], columns="condition", values=m, aggfunc="mean")
        if ref not in wide:
            continue
        for cond in [c for c in CONDITIONS if c != ref and c in wide]:
            w = wide[[ref, cond]].dropna()
            diff = (w[cond] - w[ref])
            nz = diff[diff != 0]
            p_sign = binomtest(int((nz > 0).sum()), len(nz), 0.5).pvalue if len(nz) else 1.0
            try:
                p_w = wilcoxon(diff).pvalue if len(nz) >= 1 else 1.0
            except ValueError:
                p_w = 1.0
            ds = w.index.get_level_values(0)
            groups = [diff[ds == k].to_numpy() for k in ds.unique()]
            bs = [np.mean(np.concatenate([groups[i] for i in RNG.integers(0, len(groups), len(groups))])) for _ in range(B)]
            rows.append({"split": split, "variant": variant, "metric": m, "condition": cond, "vs": ref, "n_pairs": len(w),
                         "mean_ref": w[ref].mean(), "mean_cond": w[cond].mean(), "diff": diff.mean(),
                         "ci_lo": np.percentile(bs, 2.5), "ci_hi": np.percentile(bs, 97.5),
                         "n_better": int((nz > 0).sum()), "n_worse": int((nz < 0).sum()), "sign_test_p": p_sign, "wilcoxon_p": p_w})
    r = pd.DataFrame(rows)
    if len(r):  # Holm within each metric across the 4 condition contrasts
        r["holm_p"] = np.nan
        for m, g in r.groupby("metric"):
            ps = g.wilcoxon_p.to_numpy()
            order = np.argsort(ps)
            adj, run = np.empty(len(ps)), 0.0
            for k, i in enumerate(order):
                run = max(run, min(1.0, (len(ps) - k) * ps[i]))
                adj[i] = run
            r.loc[g.index, "holm_p"] = adj
    return r


def candidate_judgements(rows: list[dict]) -> pd.DataFrame:
    """One row per (run, offered candidate): what the run decided and why, next to the truth label and the measured AUC."""
    out = []
    for r in rows:
        fe = r["trace"].get("fe") or {}
        cj = fe.get("candidate_judgements") or {}
        judg = cj if isinstance(cj, dict) else {j.get("id"): j for j in cj if isinstance(j, dict)}
        for c in r["candidates"]:
            j = judg.get(c["id"], {})
            want = "accept" if c["truth_accept"] else "reject"
            out.append({"dataset_id": r["dataset_id"], "split": r["split"], "variant": r["variant"], "condition": r["condition"],
                        "seed": r["seed"], "candidate_id": c["id"], "kind": c["kind"], "description": c["description"],
                        "univariate_auc": c["univariate_auc"], "truth": want, "decision": j.get("decision", "MISSING"),
                        "correct": j.get("decision") == want, "reason": j.get("reason")})
    return pd.DataFrame(out)


def stability(dec: pd.DataFrame) -> pd.DataFrame:
    """Seed-to-seed agreement of each structured decision (same dataset, variant, condition; seeds differ)."""
    fields = ["business_problem", "split_strategy", "primary_metric", "model_family", "hpo_depth",
              "calibration_needed", "lever", "blocked"]
    rows = []
    for (split, variant, cond), g in dec.groupby(["split", "variant", "condition"]):
        per = []
        for _, h in g.groupby("dataset_id"):
            if h.seed.nunique() < 2:
                continue
            per.append({f: float(np.mean([a == b for a, b in itertools.combinations(h[f].astype(str).tolist(), 2)])) for f in fields})
        if per:
            rows.append({"split": split, "variant": variant, "condition": cond, "n_datasets": len(per),
                         **{f"agree_{f}": np.mean([p[f] for p in per]) for f in fields},
                         "agree_mean": np.mean([np.mean(list(p.values())) for p in per])})
    return pd.DataFrame(rows)


def confidence_reliability(dec: pd.DataFrame) -> pd.DataFrame:
    """Is self-reported semantic_confidence informative about core semantic accuracy?"""
    from scipy.stats import spearmanr
    d = dec.copy()
    d["core"] = d[CORE].astype(float).mean(axis=1)
    rows = []
    for (split, cond), g in d.dropna(subset=["semantic_confidence"]).groupby(["split", "condition"]):
        rho = spearmanr(g.semantic_confidence, g.core).statistic if g.semantic_confidence.nunique() > 1 and g.core.nunique() > 1 else np.nan
        rows.append({"split": split, "condition": cond, "n": len(g), "confidence_mean": g.semantic_confidence.mean(),
                     "core_accuracy_mean": g.core.mean(), "overconfidence": g.semantic_confidence.mean() - g.core.mean(),
                     "mean_abs_gap": (g.semantic_confidence - g.core).abs().mean(), "spearman_conf_vs_core": rho,
                     "all_traps_blocked_when_conf_ge_0_9": g[g.semantic_confidence >= 0.9].all_traps_blocked.astype(float).mean()})
    return pd.DataFrame(rows)


def decision_changes(dec: pd.DataFrame) -> pd.DataFrame:
    d = dec[dec.variant == "trapped"]
    fields = ["business_problem", "split_strategy", "model_family", "hpo_depth", "calibration_needed", "primary_metric", "lever", "blocked"]
    rows = []
    for (split, did, seed), g in d.groupby(["split", "dataset_id", "seed"]):
        base = g[g.condition == "A_RAW"]
        if base.empty:
            continue
        b = base.iloc[0]
        for _, r in g[g.condition != "A_RAW"].iterrows():
            rows.append({"split": split, "dataset_id": did, "seed": seed, "condition": r.condition,
                         **{f"changed_{f}": r[f] != b[f] for f in fields}})
    return pd.DataFrame(rows)


def figures(dec: pd.DataFrame, feats: pd.DataFrame, agg: pd.DataFrame, chg: pd.DataFrame) -> None:
    labels = [COND_LABEL[c] for c in CONDITIONS]
    short = list(CONDITIONS)
    for split in ("DEVELOPMENT", "UNSEEN"):
        a = agg[(agg.split == split) & (agg.variant == "trapped")].set_index("condition").reindex(short)
        if a.n_runs.isna().all():
            continue
        tag = "dev" if split == "DEVELOPMENT" else "unseen"
        sfx = f"— {split.lower()} ({int(a.n_datasets.max())} datasets × {int(a.n_seeds.max())} seed{'s' if a.n_seeds.max() > 1 else ''})"

        def grouped(metrics, names, fname, title, ylim=(0, 1.08), ylabel="share correct"):
            fig, ax = plt.subplots(figsize=(10, 3.8))
            w = 0.8 / len(short)
            for i, c in enumerate(short):
                vals = [a.loc[c, m] if m in a else np.nan for m in metrics]
                lo = [a.loc[c, f"{m}_lo"] if f"{m}_lo" in a else np.nan for m in metrics]
                hi = [a.loc[c, f"{m}_hi"] if f"{m}_hi" in a else np.nan for m in metrics]
                xs = np.arange(len(metrics)) + (i - (len(short) - 1) / 2) * w
                ax.bar(xs, vals, width=w, color=SERIES[i], edgecolor=SURFACE, linewidth=1.5, label=COND_LABEL[c],
                       yerr=[np.array(vals) - np.array(lo), np.array(hi) - np.array(vals)], error_kw={"ecolor": INK2, "elinewidth": 0.8, "capsize": 2})
            ax.set_xticks(range(len(metrics)), names, fontsize=8)
            ax.set_ylim(*ylim)
            ax.set_ylabel(ylabel)
            ax.grid(axis="x", visible=False)
            ax.legend(ncol=5, loc="upper left", bbox_to_anchor=(0, 1.16), fontsize=8)
            ax.set_title(f"{title} {sfx}", pad=26)
            ax.text(0, -0.17, "95 % CI: dataset-cluster bootstrap", transform=ax.transAxes, fontsize=8, color=INK2)
            save(fig, FIG / f"{fname}_{tag}.png")

        grouped(["task_understanding", "target_semantic", "grain", "temporal", "intent", "metric", "split_correct"],
                ["business\nproblem", "target\nmeaning", "row grain", "temporal\nstructure", "causal vs\npredictive", "metric", "split"],
                "semantic_accuracy_by_condition", "Semantic understanding by condition")
        grouped(["id_trap_caught", "post_event_recall", "artifact_caught", "all_traps_blocked", "leak_precision"],
                ["ID trap\nblocked", "post-outcome\nrecall", "load-artifact\nblocked", "all traps\nblocked", "leak flag\nprecision"],
                "leakage_detection_by_condition", "Leakage and trap detection by condition")
        grouped(["candidate_accuracy", "cand_semantic_correct", "cand_identifier_correct", "cand_post_outcome_correct",
                 "cand_artifact_correct", "cand_target_leak_correct", "feature_valid_share"],
                ["candidate\njudgement", "accept\nsemantic", "reject\nID-derived", "reject\npost-outcome", "reject\nartifact",
                 "reject\ntarget-enc.", "proposed: valid\n& no leak"], "feature_quality_by_condition", "Feature judgement and generation quality")
        grouped(["task_understanding"], ["business problem identified"], "task_understanding_by_condition", "Task understanding")
        # model quality
        fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
        bars(axs[0], short, a.deploy_collapse.tolist(), list(zip(a.deploy_collapse_lo, a.deploy_collapse_hi)), fmt="{:.2f}",
             ylabel="share of runs whose shipped model collapses", ylim=(0, 1.05))
        axs[0].set_title(f"Deployment collapse (loses > {COLLAPSE} when\npost-outcome values are unknown)", fontsize=10)
        bars(axs[1], short, a.deploy_gap_to_oracle_median.tolist(), fmt="{:.3f}", ylabel="median (oracle-clean − deployed score)")
        axs[1].set_title("Gap to the truth-clean model (median over runs)", fontsize=10)
        for ax in axs:
            ax.tick_params(axis="x", labelsize=8)
        fig.suptitle(f"Deployment-realistic model quality {sfx}", x=0.01, ha="left", fontsize=11, fontweight="bold")
        save(fig, FIG / f"model_quality_by_condition_{tag}.png")
        # tokens / latency
        fig, axs = plt.subplots(1, 3, figsize=(13, 3.4))
        bars(axs[0], short, a.prompt_tokens.tolist(), fmt="{:.0f}", ylabel="input tokens per run (ACTUAL)")
        bars(axs[1], short, a.output_tokens.tolist(), fmt="{:.0f}", ylabel="output tokens per run (ACTUAL)")
        bars(axs[2], short, a.latency_s.tolist(), fmt="{:.0f}", ylabel="seconds per run (server compute, local 7B)")
        axs[0].set_title("Input tokens  (calls per run: " + " / ".join(f"{c.split('_')[0]} {a.loc[c, 'n_calls']:.0f}" for c in short) + ")", fontsize=9)
        axs[1].set_title("Output tokens"), axs[2].set_title("Latency")
        for ax in axs:
            ax.tick_params(axis="x", labelsize=8)
        save(fig, FIG / f"cost_by_condition_{tag}.png")
        # semantic validity vs predictive gain
        f = feats[(feats.split == split) & (feats.variant == "trapped") & feats.computable.fillna(False).astype(bool)]
        if len(f):
            fig, ax = plt.subplots(figsize=(7, 4))
            cats = [("valid", "LOW", SERIES[0], "semantically valid, no leak"), ("unknown", "LOW", SERIES[3], "validity unknown, no leak"),
                    ("invalid", "LOW", SERIES[1], "semantically invalid"), (None, "HIGH", SERIES[4], "uses id / leak / target")]
            for j, (sv, lr, col, name) in enumerate(cats):
                s = f[(f.leakage_risk == lr) & ((f.semantic_validity == sv) if sv else True)]
                if len(s):
                    ax.scatter(s.statistical_value_cv_gain, s.generalization_test_gain, s=22, color=col, marker=MARKERS[j], alpha=0.75,
                               edgecolor=SURFACE, linewidth=0.6, label=f"{name} (n={len(s)})")
            ax.axhline(0, color=INK2, lw=0.8), ax.axvline(0, color=INK2, lw=0.8)
            ax.set_xlabel("CV gain on development rows (statistical value)")
            ax.set_ylabel("gain on deployment-masked test rows")
            ax.legend(fontsize=8, loc="lower right")
            ax.set_title(f"Semantic validity vs predictive gain — {split.lower()} ({len(f)} executed features)")
            save(fig, FIG / f"validity_vs_gain_{tag}.png")
        # decision changes
        c = chg[chg.split == split]
        if len(c):
            fields = [k for k in c.columns if k.startswith("changed_")]
            t = c.groupby("condition")[fields].mean().reindex(short[1:])
            fig, ax = plt.subplots(figsize=(10, 3.6))
            w = 0.2
            for i, cond in enumerate(short[1:]):
                ax.bar(np.arange(len(fields)) + (i - 1.5) * w, t.loc[cond], width=w, color=SERIES[i + 1], edgecolor=SURFACE, linewidth=1.5,
                       label=COND_LABEL[cond])
            ax.set_xticks(range(len(fields)), [k.replace("changed_", "").replace("_", "\n") for k in fields], fontsize=8)
            ax.set_ylim(0, 1.05)
            ax.set_ylabel("share of runs that differ from A")
            ax.legend(ncol=4, loc="upper left", bbox_to_anchor=(0, 1.16), fontsize=8)
            ax.grid(axis="x", visible=False)
            ax.set_title(f"Downstream decisions changed relative to raw schema {sfx}", pad=26)
            save(fig, FIG / f"decision_changes_{tag}.png")
    # dev vs unseen for core semantic accuracy and deployment
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.6))
    for k, (m, yl) in enumerate([("core_semantic_accuracy", "core semantic accuracy"), ("all_traps_blocked", "all traps blocked")]):
        ax = axs[k]
        for j, split in enumerate(["DEVELOPMENT", "UNSEEN"]):
            a = agg[(agg.split == split) & (agg.variant == "trapped")].set_index("condition").reindex(short)
            if a[m].isna().all():
                continue
            xs = np.arange(5) + (j - 0.5) * 0.36
            ax.bar(xs, a[m], width=0.36, color=SERIES[:5], alpha=0.45 if j == 0 else 1.0, edgecolor=SURFACE, linewidth=2)
            for x, v in zip(xs, a[m]):
                ax.text(x, 0.02, f"{v:.2f}", rotation=90, fontsize=7, ha="center")
        ax.set_xticks(range(5), short, fontsize=8)
        ax.set_ylim(0, 1.05)
        ax.set_ylabel(yl)
        ax.grid(axis="x", visible=False)
        ax.set_title(f"{yl.capitalize()}: development (pale) vs unseen (solid)")
    save(fig, FIG / "dev_vs_unseen.png")
    # adversarial tests
    for split in ("DEVELOPMENT", "UNSEEN"):
        tag = "dev" if split == "DEVELOPMENT" else "unseen"
        a = agg[(agg.split == split)]
        panels = [("anonymized", "core_semantic_accuracy", "T1 anonymized: core semantic accuracy"),
                  ("anonymized", "all_traps_blocked", "T1 anonymized: all traps blocked"),
                  ("incomplete", "missing_semantics_recall", "T3 incomplete: missing definitions noticed"),
                  ("misleading", "falsified_detected_recall", "T4 misleading: falsified entries detected")]
        if not any((a.variant == p[0]).any() for p in panels):
            continue
        fig, axs = plt.subplots(1, 4, figsize=(13, 3.3))
        for ax, (var, m, title) in zip(axs, panels):
            s = a[a.variant == var].set_index("condition")
            if var == "anonymized":
                t = agg[(agg.split == split) & (agg.variant == "trapped")].set_index("condition")
                s = pd.concat([t.loc[["A_RAW"]].assign(condition_label="A names"), s.assign(condition_label=[f"{c.split('_')[0]} anon" for c in s.index])])
            else:
                s = s.assign(condition_label=[c.split("_")[0] for c in s.index])
            if m not in s:
                continue
            bars(ax, s.condition_label.tolist(), s[m].tolist(), fmt="{:.2f}", ylim=(0, 1.1), colors=SERIES[: len(s)])
            ax.set_title(title, fontsize=9)
            ax.tick_params(axis="x", labelsize=8)
        save(fig, FIG / f"adversarial_tests_{tag}.png")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = load()
    dec, feats = process(rows)
    dec.to_csv(OUT / "semantic-decisions.csv", index=False)
    feats.to_csv(OUT / "generated-features.csv", index=False)
    run_level = dec[["dataset_id", "split", "variant", "condition", "seed", "n_calls", "n_failed_calls", "prompt_tokens", "output_tokens",
                     "latency_s", "analysis_ok", "deploy_score", "naive_score", "leak_inflation", "estimate_error", "oracle_deploy",
                     "use_everything_deploy", "deploy_gap_to_oracle", "n_retained_features", "retained_leaky", "retained_invalid"]].copy()
    run_level["tokens_status"] = "ACTUAL"
    run_level["cost_usd"] = None
    run_level["cost_status"] = "NOT_APPLICABLE_LOCAL"
    run_level.to_csv(OUT / "run-level-results.csv", index=False)
    agg = aggregate(dec)
    agg.to_csv(OUT / "study-b-results.csv", index=False)
    pr = pd.concat([paired_vs_raw(dec, s) for s in dec.split.unique()], ignore_index=True)
    pr.to_csv(OUT / "study-b-paired-tests.csv", index=False)
    chg = decision_changes(dec)
    chg.to_csv(OUT / "decision-changes.csv", index=False)
    candidate_judgements(rows).to_csv(OUT / "candidate-judgements.csv", index=False)
    stability(dec).to_csv(OUT / "study-b-stability.csv", index=False)
    confidence_reliability(dec).to_csv(OUT / "study-b-confidence.csv", index=False)
    d = dec.copy()
    d["core_semantic_accuracy"] = d[CORE].astype(float).mean(axis=1)
    d.groupby(["split", "variant", "dataset_id", "condition"])[
        ["core_semantic_accuracy", "task_understanding", "all_traps_blocked", "leak_recall", "id_trap_caught", "post_event_recall",
         "artifact_caught", "candidate_accuracy", "deploy_score", "leak_inflation", "over_exclusion", "output_tokens", "latency_s"]
    ].mean(numeric_only=True).reset_index().to_csv(OUT / "study-b-per-dataset.csv", index=False)
    figures(dec, feats, agg, chg)
    pd.set_option("display.width", 250)
    cols = ["split", "variant", "condition", "n_runs", "core_semantic_accuracy", "task_understanding", "all_traps_blocked", "leak_recall",
            "candidate_accuracy", "feature_valid_share", "deploy_score", "over_exclusion", "output_tokens"]
    print(agg[[c for c in cols if c in agg]].round(3).to_string())


if __name__ == "__main__":
    main()
