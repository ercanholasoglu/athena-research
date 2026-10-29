"""Derived facts, deterministic examples and cross-study figures (run after both study analyzers).

    python -m rs2610.analyze_extra

Writes outputs/derived-facts.json ({key: {value, source}}), outputs/examples.json and outputs/cross_study/*.png|csv.
Examples are chosen by fixed rules stated next to each one (e.g. "the accepted identifier-derived candidate with the
highest univariate AUC"), preferring UNSEEN rows, never by reading and picking.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

from rs2610.common.viz import INK2, MARKERS, SERIES, plt, save

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
A, Bd = OUT / "study_a", OUT / "study_b"
XS = OUT / "cross_study"
FACTS: dict[str, dict] = {}
ORDER = {"A": ["DIRECT", "COT", "TOT", "GOT"], "B": ["A_RAW", "B_SELF", "C_DICT", "D_RULES", "E_FULL"]}


def put(key: str, value, source: str) -> None:
    if isinstance(value, (np.floating, np.integer)):
        value = value.item()
    if isinstance(value, float) and np.isnan(value):
        value = None
    FACTS[key] = {"value": value, "source": source}


def splits(df: pd.DataFrame) -> list[str]:
    return [s for s in ("DEVELOPMENT", "UNSEEN") if s in set(df.split)]


# ----------------------------------------------------------------------------------------------- Study B features
def feature_facts() -> None:
    f = pd.read_csv(Bd / "generated-features.csv")
    c = pd.read_csv(Bd / "candidate-judgements.csv")
    src_f, src_c = "outputs/study_b/generated-features.csv", "outputs/study_b/candidate-judgements.csv"
    cand_names = c.groupby(["dataset_id", "split", "variant", "condition", "seed"]).candidate_id.apply(set).to_dict()
    f["copies_candidate"] = [str(r["name"]) in cand_names.get((r.dataset_id, r.split, r.variant, r.condition, r.seed), set())
                             for _, r in f.iterrows()]
    for split in splits(f):
        for cond, g in f[(f.split == split) & (f.variant == "trapped")].groupby("condition"):
            k = f"bx.{split}.{cond}"
            put(f"{k}.features_proposed", len(g), src_f)
            put(f"{k}.features_computable", int(g.computable.fillna(False).astype(bool).sum()), src_f)
            put(f"{k}.proposals_copying_candidates", float(g.copies_candidate.mean()) if len(g) else None, src_f)
            put(f"{k}.strong_but_invalid", int(g.statistically_strong_semantically_invalid.sum()), src_f)
            put(f"{k}.retained", int(g.retained.sum()), src_f)
            put(f"{k}.retained_leaky", int((g.retained & (g.leakage_risk == "HIGH")).sum()), src_f)
            put(f"{k}.retained_valid", int((g.retained & (g.semantic_validity == "valid") & (g.leakage_risk == "LOW")).sum()), src_f)
            hi = g[g.leakage_risk == "HIGH"]
            put(f"{k}.leaky_proposed", len(hi), src_f)
            put(f"{k}.leaky_self_flagged_likely", float((hi.model_leakage_assessment == "likely").mean()) if len(hi) else None, src_f)
        all_g = f[(f.split == split) & (f.variant == "trapped")]
        put(f"bx.{split}.features_proposed", len(all_g), src_f)
        put(f"bx.{split}.proposals_copying_candidates", float(all_g.copies_candidate.mean()) if len(all_g) else None, src_f)
        ranked = f[(f.split == split) & f.statistical_value_cv_gain.notna()].sort_values("statistical_value_cv_gain", ascending=False)
        lead = int((ranked.leakage_risk != "HIGH").to_numpy().argmax()) if (ranked.leakage_risk != "HIGH").any() else len(ranked)
        put(f"bx.{split}.cv_gain_ranked_n", len(ranked), src_f)  # every variant, every condition
        put(f"bx.{split}.cv_gain_top_all_leaky", lead, src_f)  # the top `lead` features by CV gain are all HIGH leakage
        for cond, g in c[(c.split == split) & (c.variant == "trapped")].groupby("condition"):
            k = f"bx.{split}.{cond}"
            bad = g[g.truth == "reject"]
            good = g[g.truth == "accept"]
            put(f"{k}.invalid_candidate_rejection", float((bad.decision == "reject").mean()), src_c)
            put(f"{k}.valid_candidate_acceptance", float((good.decision == "accept").mean()), src_c)
            put(f"{k}.judgements_missing", int((g.decision == "MISSING").sum()), src_c)
            for kind, h in g.groupby("kind"):
                put(f"{k}.accept_rate.{kind}", float((h.decision == "accept").mean()), src_c)
        put(f"bx.{split}.candidate_judgements", int(((c.split == split) & (c.variant == "trapped")).sum()), src_c)


def pick(df: pd.DataFrame, rule: str, sort: str, ascending: bool = False) -> dict | None:
    for split in ("UNSEEN", "DEVELOPMENT"):
        d = df[df.split == split]
        if len(d):
            r = d.sort_values([sort, "dataset_id", "condition", "seed"], ascending=[ascending, True, True, True]).iloc[0]
            return {"rule": rule, **{k: (v.item() if hasattr(v, "item") else v) for k, v in r.to_dict().items()}}
    return None


def examples() -> dict:
    c = pd.read_csv(Bd / "candidate-judgements.csv")
    f = pd.read_csv(Bd / "generated-features.csv")
    c, f = c[c.variant == "trapped"], f[f.variant == "trapped"]
    ex = {}
    for kind, label in (("identifier", "id_trap_accepted"), ("artifact", "artifact_accepted"), ("post_outcome", "post_outcome_accepted"),
                        ("target_leak", "target_encoding_accepted")):
        ex[label] = pick(c[(c.kind == kind) & (c.decision == "accept")],
                         f"accepted {kind} candidate with the highest univariate AUC (UNSEEN first)", "univariate_auc")
        ex[label.replace("accepted", "rejected")] = pick(c[(c.kind == kind) & (c.decision == "reject")],
                                                         f"rejected {kind} candidate with the highest univariate AUC (UNSEEN first)",
                                                         "univariate_auc")
    ok = f[f.computable.fillna(False).astype(bool)]
    ex["legit_feature_best"] = pick(ok[(ok.semantic_validity == "valid") & (ok.leakage_risk == "LOW") & ok.retained],
                                    "retained valid, leak-free proposal with the largest deployment-masked test gain", "generalization_test_gain")
    ex["strong_invalid_best"] = pick(ok[ok.statistically_strong_semantically_invalid],
                                     "statistically strong but invalid / leaky proposal with the largest CV gain", "statistical_value_cv_gain")
    ex["strong_invalid_retained"] = pick(ok[ok.statistically_strong_semantically_invalid & ok.retained],
                                         "strong-but-invalid proposal that the validator still retained, largest CV gain", "statistical_value_cv_gain")
    # T4: what E_FULL's verification said about each falsified entry (from the run traces)
    t4 = []
    for tag in ("unseen", "dev"):
        p = ROOT / "artifacts" / "study_b" / f"runs_{tag}.jsonl"
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            r = json.loads(line)
            if r["variant"] != "misleading":
                continue
            ver = {chk.get("column"): chk for chk in ((r["trace"].get("verification") or {}).get("checks") or []) if isinstance(chk, dict)}
            contra = {d.get("column") for d in ((r["trace"].get("analysis") or {}).get("dictionary_contradictions") or []) if isinstance(d, dict)}
            for col in r.get("falsified") or []:
                t4.append({"split": r["split"], "dataset_id": r["dataset_id"], "condition": r["condition"], "seed": r["seed"], "column": col,
                           "verification_verdict": (ver.get(col) or {}).get("verdict", "NOT_CHECKED" if r["condition"] == "E_FULL" else "NO_STAGE"),
                           "verification_evidence": (ver.get(col) or {}).get("evidence"), "analysis_flagged": col in contra})
    pd.DataFrame(t4).to_csv(Bd / "t4-falsified-entries.csv", index=False)
    ex["t4_rows"] = len(t4)
    return ex


def t4_facts() -> None:
    """T4 split by entry kind: a falsified entry either swaps two real meanings or hides a post-outcome leak behind an
    innocent description. Per condition: did verification contradict it, did the analysis list it as a contradiction,
    and (hidden leak only) did the analysis still block the column."""
    from rs2610.common.data import by_id
    from rs2610.study_b.variants import trapped
    src = "outputs/study_b/t4-falsified-entries.csv"
    t4 = pd.read_csv(Bd / "t4-falsified-entries.csv")
    runs = {}
    for tag in ("unseen", "dev"):
        p = ROOT / "artifacts" / "study_b" / f"runs_{tag}.jsonl"
        for line in (p.read_text().splitlines() if p.exists() else []):
            r = json.loads(line)
            if r["variant"] == "misleading":
                a = r["trace"].get("analysis") or {}
                runs[(r["split"], r["dataset_id"], r["condition"], r["seed"])] = set(
                    a.get("post_outcome_columns") or []) | set(a.get("artifact_or_leakage_columns") or []) | set(a.get("excluded_columns") or [])
    leaks = {d: set(trapped(by_id(d)).truth["leak_all"]) for d in t4.dataset_id.unique()}
    t4["kind"] = [("hidden_leak" if c in leaks[d] else "swapped") for d, c in zip(t4.dataset_id, t4.column)]
    t4["blocked"] = [c in runs.get((s, d, k, int(e)), set()) for s, d, k, e, c in zip(t4.split, t4.dataset_id, t4.condition, t4.seed, t4.column)]
    for (split, cond, kind), g in t4.groupby(["split", "condition", "kind"]):
        k = f"bx.t4.{split}.{cond}.{kind}"
        put(f"{k}.n", len(g), src)
        put(f"{k}.analysis_flagged", int(g.analysis_flagged.astype(bool).sum()), src)
        if kind == "hidden_leak":
            put(f"{k}.blocked", int(g.blocked.sum()), src)
        if cond == "E_FULL":
            put(f"{k}.verify_contradicted", int((g.verification_verdict == "contradicted").sum()), src)


def truncation_facts() -> None:
    """Ledger audit: calls that hit their max_tokens cap, per study and split (post-freeze finding, JOURNAL 2026-10-28)."""
    for study in ("a", "b"):
        led = ROOT / "artifacts" / f"study_{study}" / "ledger.jsonl"
        runs = {tag: ROOT / "artifacts" / f"study_{study}" / f"runs_{tag}.jsonl" for tag in ("dev", "unseen")}
        n = {"DEVELOPMENT": 0, "UNSEEN": 0}
        splits_of = {}
        for tag, p in runs.items():
            for line in (p.read_text().splitlines() if p.exists() else []):
                r = json.loads(line)
                splits_of[r.get("dataset_id")] = r["split"]
        for line in led.read_text().splitlines():
            x = json.loads(line)
            if x.get("truncated") and isinstance(x.get("tag"), dict):
                ds = x["tag"].get("dataset") or str(x["tag"].get("instance", "")).split("::")[0]
                if ds in splits_of:
                    n[splits_of[ds]] += 1
        for split, v in n.items():
            put(f"design.{study.upper()}.{split}.truncated_calls", v, f"artifacts/study_{study}/ledger.jsonl")


MIN_DECODE_TPS = 5.0  # < 1/5 of the median decode rate (23-25 tok/s) and below the 1st percentile in both studies


def latency_audit() -> None:
    """Server compute per run with host-suspend contamination removed (post-freeze finding, JOURNAL 2026-10-28).

    The machine slept ~10 h with both studies running; the server's own timers absorbed part of that (one Study B call
    decoded 782 tokens in 35,308 s). A call whose decode rate is below MIN_DECODE_TPS is HOST_SUSPEND_CONTAMINATED and
    its compute is UNKNOWN; a run's compute is known only if all its calls are clean. Means are over known runs, with n."""
    for study, key in (("a", "mode"), ("b", "condition")):
        led = {}
        for line in (ROOT / "artifacts" / f"study_{study}" / "ledger.jsonl").read_text().splitlines():
            x = json.loads(line)
            led[x["request_hash"]] = x
        rows = []
        for tag in ("dev", "unseen"):
            p = ROOT / "artifacts" / f"study_{study}" / f"runs_{tag}.jsonl"
            for line in (p.read_text().splitlines() if p.exists() else []):
                r = json.loads(line)
                if study == "b" and r["variant"] != "trapped":
                    continue
                calls = r["trace"]["calls"] if "trace" in r else (r.get("calls") or [])
                comp, bad, known = 0.0, 0, True
                for c in calls:
                    x = led.get(c.get("request_hash"))
                    if not x or x.get("decode_s") is None:
                        known = False
                        continue
                    if (x.get("output_tokens") or 0) > 5 and x["output_tokens"] / x["decode_s"] < MIN_DECODE_TPS:
                        bad += 1
                        known = False
                        continue
                    comp += (x.get("prefill_s") or 0) + x["decode_s"]
                rows.append({"split": r["split"], key: r[key], "compute_s": comp if known else None, "contaminated_calls": bad})
        df = pd.DataFrame(rows)
        out = (A if study == "a" else Bd) / "latency-audit.csv"
        agg = df.groupby(["split", key]).agg(n_runs=("compute_s", "size"), n_known=("compute_s", "count"),
                                             compute_mean=("compute_s", "mean"), compute_median=("compute_s", "median"),
                                             contaminated_calls=("contaminated_calls", "sum")).reset_index()
        agg["status"] = f"ACTUAL_SERVER_COMPUTE; calls < {MIN_DECODE_TPS} tok/s = HOST_SUSPEND_CONTAMINATED -> UNKNOWN"
        agg.to_csv(out, index=False)
        src = str(out.relative_to(ROOT))
        for _, g in agg.iterrows():
            for col in ("n_runs", "n_known", "compute_mean", "compute_median", "contaminated_calls"):
                put(f"lat.{study.upper()}.{g.split}.{g[key]}.{col}", g[col] if pd.notna(g[col]) else None, src)


def matched_baselines() -> None:
    """Adversarial variants run on 2 datasets each; their honest baseline is the trapped grid on the *same* datasets and
    condition (not the 8-dataset trapped mean)."""
    from rs2610.study_b.run import ADV as VARIANT_PLAN
    src = "outputs/study_b/study-b-per-dataset.csv"
    pdx = pd.read_csv(Bd / "study-b-per-dataset.csv")
    for variant, (by_split, conds) in VARIANT_PLAN.items():
        for split, dsets in by_split.items():
            g = pdx[(pdx.split == split) & (pdx.variant == "trapped") & pdx.dataset_id.isin(dsets)]
            for cond, h in g.groupby("condition"):
                for m in ("core_semantic_accuracy", "all_traps_blocked"):
                    put(f"bx.matched.{split}.{variant}.{cond}.{m}", float(h[m].mean()), src)


# ----------------------------------------------------------------------------------------------- cross-study
def cross_study() -> None:
    XS.mkdir(parents=True, exist_ok=True)
    a = pd.read_csv(A / "study-a-results.csv")
    b = pd.read_csv(Bd / "study-b-results.csv")
    b = b[b.variant == "trapped"]
    # latency from the host-suspend audit (never the results tables' latency columns)
    la = pd.read_csv(A / "latency-audit.csv").set_index(["split", "mode"]).compute_mean
    lb = pd.read_csv(Bd / "latency-audit.csv").set_index(["split", "condition"]).compute_mean
    a = a.assign(latency_s_mean=[la.get((sp, m)) for sp, m in zip(a.split, a["mode"])])
    b = b.assign(latency_s=[lb.get((sp, c)) for sp, c in zip(b.split, b.condition)])
    rows = []
    for split in splits(a):
        s = a[a.split == split].set_index("mode")
        if "COT" not in s.index:
            continue
        ref = s.loc["COT"]
        for m, r in s.iterrows():
            rows.append({"study": "A", "split": split, "arm": m, "reference": "COT", "quality_metric": "decision accuracy",
                         "quality": r.accuracy, "quality_delta": r.accuracy - ref.accuracy,
                         "token_multiple": r.total_tokens_mean / ref.total_tokens_mean, "latency_multiple": r.latency_s_mean / ref.latency_s_mean,
                         "calls": r.calls_mean})
    b = b.assign(total_tokens=b.prompt_tokens + b.output_tokens)
    for split in splits(b):
        s = b[b.split == split].set_index("condition")
        if "A_RAW" not in s.index:
            continue
        ref = s.loc["A_RAW"]
        for cnd, r in s.iterrows():
            for qm in ("core_semantic_accuracy", "all_traps_blocked"):
                rows.append({"study": "B", "split": split, "arm": cnd, "reference": "A_RAW", "quality_metric": qm, "quality": r[qm],
                             "quality_delta": r[qm] - ref[qm], "token_multiple": r.total_tokens / ref.total_tokens,
                             "latency_multiple": r.latency_s / ref.latency_s, "calls": r.n_calls})
    x = pd.DataFrame(rows)
    x.to_csv(XS / "quality-vs-cost.csv", index=False)
    for _, r in x.iterrows():
        k = f"x.{r.study}.{r.split}.{r.arm}.{r.quality_metric.replace(' ', '_')}"
        for col in ("quality_delta", "token_multiple", "latency_multiple"):
            put(f"{k}.{col}", r[col], "outputs/cross_study/quality-vs-cost.csv")
    gap = []
    for (study, arm, qm), g in x.groupby(["study", "arm", "quality_metric"]):
        g = g.set_index("split")
        if {"DEVELOPMENT", "UNSEEN"} <= set(g.index):
            gap.append({"study": study, "arm": arm, "quality_metric": qm, "delta_dev": g.loc["DEVELOPMENT", "quality_delta"],
                        "delta_unseen": g.loc["UNSEEN", "quality_delta"], "quality_dev": g.loc["DEVELOPMENT", "quality"],
                        "quality_unseen": g.loc["UNSEEN", "quality"]})
    gp = pd.DataFrame(gap)
    gp.to_csv(XS / "dev-vs-unseen-gap.csv", index=False)
    for split in splits(x):
        fig, axs = plt.subplots(1, 2, figsize=(11, 4))
        for ax, (study, qm, title) in zip(axs, [("A", "decision accuracy", "Study A: topology vs CoT"),
                                                ("B", "core_semantic_accuracy", "Study B: context vs raw schema")]):
            d = x[(x.study == study) & (x.split == split) & (x.quality_metric == qm)]
            order = ORDER[study]  # colour follows the entity, in the same order as every other figure of that study
            for j, (_, r) in enumerate(d.set_index("arm").reindex(order).dropna(subset=["quality"]).reset_index().iterrows()):
                i = order.index(r.arm)
                ax.scatter(r.token_multiple, r.quality_delta, s=90, color=SERIES[i], marker=MARKERS[i], edgecolor="#fcfcfb",
                           linewidth=1.5, zorder=3)
                ax.annotate(r.arm, (r.token_multiple, r.quality_delta), xytext=(7, 4 if j % 2 == 0 else -12), textcoords="offset points",
                            fontsize=8.5)
            ax.axhline(0, color=INK2, lw=0.8)
            ax.set_xscale("log")
            ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}×"))
            ax.xaxis.set_minor_formatter(FuncFormatter(lambda v, _: f"{v:g}×" if v in (2, 3, 5) else ""))
            ax.set_xlabel("total tokens per decision, relative to reference (log)")
            ax.set_ylabel(f"Δ {qm.replace('_', ' ')} vs reference")
            ax.set_title(f"{title} — {split.lower()}", fontsize=10)
        fig.text(0.01, -0.02, "Point estimates of the difference; uncertainty and tests are in the paired-test tables.", fontsize=8,
                 color=INK2)
        save(fig, XS / f"quality_gain_vs_cost_{'dev' if split == 'DEVELOPMENT' else 'unseen'}.png")
    if len(gp):
        fig, ax = plt.subplots(figsize=(8, 4))
        lab = [f"{r.study}·{r.arm}" + ("" if r.quality_metric in ("decision accuracy", "core_semantic_accuracy") else " (traps)")
               for _, r in gp.iterrows()]
        y = np.arange(len(gp))
        ax.scatter(gp.delta_dev, y, s=60, color=SERIES[0], marker="o", label="development", zorder=3)
        ax.scatter(gp.delta_unseen, y, s=60, color=SERIES[1], marker="s", label="unseen", zorder=3)
        for i, (_, r) in enumerate(gp.iterrows()):
            ax.plot([r.delta_dev, r.delta_unseen], [i, i], color=INK2, lw=1)
        ax.axvline(0, color=INK2, lw=0.8)
        ax.set_yticks(y, lab, fontsize=8)
        ax.set_xlabel("quality difference vs reference arm (CoT / A_RAW)")
        ax.legend(loc="lower right", fontsize=8)
        ax.set_title("Does the development difference survive on unseen datasets?", fontsize=10)
        save(fig, XS / "dev_vs_unseen_gap.png")


def design_facts() -> None:
    """Counts the report states about the design, from the manifests and the run tables (never typed by hand)."""
    from rs2610.common.data import DATASETS
    for study in ("A", "B"):
        for split in ("DEVELOPMENT", "UNSEEN"):
            ds = [d.dataset_id for d in DATASETS if study in d.studies and d.split == split]
            put(f"design.{study}.{split}.datasets", len(ds), "common/data.py DATASETS")
            put(f"design.{study}.{split}.dataset_list", ", ".join(ds), "common/data.py DATASETS")
    for split in ("DEVELOPMENT", "UNSEEN"):
        p = ROOT / "artifacts" / "study_a" / "instances" / f"{split}.json"
        if p.exists():
            insts = json.loads(p.read_text())
            put(f"design.A.{split}.instances", len(insts), str(p.relative_to(ROOT)))
            put(f"design.A.{split}.adversarial_instances", sum(i["variant"] != "base" for i in insts), str(p.relative_to(ROOT)))
            put(f"design.A.{split}.families", len({i["family"] for i in insts}), str(p.relative_to(ROOT)))
    ra = pd.read_csv(A / "study-a-run-level-results.csv")
    rb = pd.read_csv(Bd / "run-level-results.csv")
    for split in splits(ra):
        g = ra[ra.split == split]
        put(f"design.A.{split}.runs", len(g), "outputs/study_a/study-a-run-level-results.csv")
        put(f"design.A.{split}.calls", int(g.n_calls.sum()), "outputs/study_a/study-a-run-level-results.csv")
        put(f"design.A.{split}.prompt_tokens", int(g.prompt_tokens.sum()), "outputs/study_a/study-a-run-level-results.csv")
        put(f"design.A.{split}.output_tokens", int(g.output_tokens.sum()), "outputs/study_a/study-a-run-level-results.csv")
        put(f"design.A.{split}.compute_hours", float(g.latency_s.sum() / 3600), "outputs/study_a/study-a-run-level-results.csv")
        put(f"design.A.{split}.parse_failed_runs", int(g.parse_failed.sum()), "outputs/study_a/study-a-run-level-results.csv")
        put(f"design.A.{split}.failed_calls", int(g.n_failed_calls.sum()), "outputs/study_a/study-a-run-level-results.csv")
    for split in splits(rb):
        g = rb[rb.split == split]
        put(f"design.B.{split}.runs", len(g), "outputs/study_b/run-level-results.csv")
        put(f"design.B.{split}.calls", int(g.n_calls.sum()), "outputs/study_b/run-level-results.csv")
        put(f"design.B.{split}.prompt_tokens", int(g.prompt_tokens.sum()), "outputs/study_b/run-level-results.csv")
        put(f"design.B.{split}.output_tokens", int(g.output_tokens.sum()), "outputs/study_b/run-level-results.csv")
        put(f"design.B.{split}.compute_hours", float(g.latency_s.sum() / 3600), "outputs/study_b/run-level-results.csv")
        put(f"design.B.{split}.failed_calls", int(g.n_failed_calls.sum()), "outputs/study_b/run-level-results.csv")
        put(f"design.B.{split}.analysis_failed_runs", int((~g.analysis_ok.astype(bool)).sum()), "outputs/study_b/run-level-results.csv")
    for rec in ("A", "B"):  # loaded frame sizes, as hashed in the freeze record
        fr = OUT / f"FREEZE_RECORD_{rec}.json"
        if fr.exists():
            for d in json.loads(fr.read_text())["dataset_manifest"]:
                put(f"design.ds.{d['dataset_id']}.rows", d["rows"], str(fr.relative_to(ROOT)))
                put(f"design.ds.{d['dataset_id']}.columns", d["columns"], str(fr.relative_to(ROOT)))
    for p, k in ((ROOT / "artifacts/study_b/superseded_v1/runs_dev.jsonl", "design.B.superseded_v1_runs"),
                 (ROOT / "artifacts/study_b/superseded_v2/runs_dev.jsonl", "design.B.superseded_v2_runs")):
        put(k, len(p.read_text().splitlines()) if p.exists() else 0, str(p.relative_to(ROOT)))


def topology_ratios() -> None:
    """Study A cost multiples relative to DIRECT (tokens from study-a-results.csv, compute from the audited
    latency-audit.csv), and the per-instance-majority adversarial counts the article quotes."""
    res = pd.read_csv(A / "study-a-results.csv")
    lat = pd.read_csv(A / "latency-audit.csv")
    for split in splits(res):
        r = res[res.split == split].set_index("mode")
        lt = lat[lat.split == split].set_index("mode")
        for m in r.index:
            for col in ("output_tokens_mean", "total_tokens_mean", "calls_mean"):
                put(f"ax.{split}.{m}.{col}_vs_direct", float(r.loc[m, col] / r.loc["DIRECT", col]), "outputs/study_a/study-a-results.csv")
            put(f"ax.{split}.{m}.accuracy_per_1k_vs_direct", float(r.loc["DIRECT", "accuracy_per_1k_output_tokens"]
                                                                  / r.loc[m, "accuracy_per_1k_output_tokens"]),
                "outputs/study_a/study-a-results.csv")
            if m in lt.index and pd.notna(lt.loc[m, "compute_mean"]):
                put(f"ax.{split}.{m}.compute_vs_direct", float(lt.loc[m, "compute_mean"] / lt.loc["DIRECT", "compute_mean"]),
                    "outputs/study_a/latency-audit.csv")


def main() -> None:
    design_facts()
    feature_facts()
    ex = examples()
    (OUT / "examples.json").write_text(json.dumps(ex, indent=1, default=str))
    for name, e in ex.items():  # deterministic examples as facts, so articles quote them from data
        for col, v in (e or {}).items() if isinstance(e, dict) else ():
            if isinstance(v, (int, float, str, bool)) and col not in ("rule",):
                put(f"ex.{name}.{col}", v, "outputs/examples.json")
    t4_facts()
    latency_audit()
    matched_baselines()
    truncation_facts()
    topology_ratios()
    cross_study()
    (OUT / "derived-facts.json").write_text(json.dumps(FACTS, indent=1, sort_keys=True, default=str))
    print(len(FACTS), "derived facts;", sum(v is not None for v in ex.values() if isinstance(v, dict) or v is None), "examples")


if __name__ == "__main__":
    main()
