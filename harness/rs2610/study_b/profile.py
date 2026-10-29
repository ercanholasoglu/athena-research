"""Column profile shown in every condition, and the candidate-feature judgement list.

The profile is what an AutoML system always has, dictionary or not: dtype,
cardinality, missingness, range / top values, uniqueness, correlation with
row order, and univariate association with the target (folded ROC-AUC for
classification, |Spearman| for regression).  It is computed on the
development split only.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import KFold

from rs2610.study_b.variants import Variant


def _assoc(x: pd.Series, y: np.ndarray, regression: bool) -> float | None:
    if pd.api.types.is_numeric_dtype(x):
        v = pd.to_numeric(x, errors="coerce").to_numpy(dtype=float)
    else:  # out-of-fold target-mean encoding so a category cannot "memorise" its rows
        v = np.full(len(x), np.nan)
        xs = x.astype(str).to_numpy()
        for tr, va in KFold(2, shuffle=True, random_state=0).split(xs):
            means = pd.Series(y[tr]).groupby(xs[tr]).mean()
            v[va] = pd.Series(xs[va]).map(means).to_numpy(dtype=float)
    m = ~np.isnan(v)
    if m.sum() < 30 or np.nanstd(v[m]) == 0:
        return None
    if regression:
        return float(abs(spearmanr(v[m], y[m]).statistic))
    yy = y[m]
    if len(np.unique(yy)) < 2:
        return None
    a = roc_auc_score(yy, v[m])
    return float(max(a, 1 - a))


def profile(v: Variant, dev_idx: np.ndarray) -> list[dict[str, Any]]:
    f = v.frame.iloc[dev_idx]
    y = f[v.target].to_numpy()
    regression = v.ds.task_type == "regression"
    rows = []
    order = np.arange(len(f))
    for c in f.columns:
        if c == v.target:
            continue
        s = f[c]
        r: dict[str, Any] = {"column": c, "dtype": "numeric" if pd.api.types.is_numeric_dtype(s) else "text",
                             "n_unique": int(s.nunique()), "unique_ratio": round(s.nunique() / len(s), 4),
                             "missing": round(float(s.isna().mean()), 4)}
        if r["dtype"] == "numeric":
            q = pd.to_numeric(s, errors="coerce")
            r.update({"min": float(q.min()), "median": float(q.median()), "max": float(q.max()),
                      "integer_valued": bool(np.allclose(q.dropna() % 1, 0))})
            if q.notna().sum() > 30 and q.std() > 0:
                r["row_order_spearman"] = round(float(spearmanr(order[q.notna()], q.dropna()).statistic), 3)
        else:
            vc = s.astype(str).value_counts(normalize=True)
            r["top_values"] = {str(k): round(float(p), 3) for k, p in vc.head(4).items()}
        a = _assoc(s, y, regression)
        r["target_association"] = round(a, 3) if a is not None else None
        rows.append(r)
    return rows


def render_profile(rows: list[dict[str, Any]], v: Variant) -> str:
    kind = "|Spearman|" if v.ds.task_type == "regression" else "folded AUC"
    head = (f"{len(rows)} feature columns + target '{v.target}' ({v.ds.task_type}). Univariate target association = {kind} "
            "(0.5 = none for AUC). row_order = Spearman correlation with row position.")
    lines = [head]
    for r in rows:
        if r["dtype"] == "numeric":
            desc = f"numeric{' int' if r.get('integer_valued') else ''} min {r['min']:.4g} median {r['median']:.4g} max {r['max']:.4g}"
            if "row_order_spearman" in r:
                desc += f", row_order {r['row_order_spearman']}"
        else:
            desc = "text top " + ", ".join(f"{k}:{p}" for k, p in r["top_values"].items())
        lines.append(f"- {r['column']}: {desc}; unique {r['n_unique']} (ratio {r['unique_ratio']}); missing {r['missing']}; "
                     f"assoc {r['target_association']}")
    return "\n".join(lines)


def target_summary(v: Variant, dev_idx: np.ndarray) -> str:
    y = v.frame.iloc[dev_idx][v.target]
    if v.ds.task_type == "regression":
        return f"Target '{v.target}': numeric, min {y.min():.4g}, median {y.median():.4g}, max {y.max():.4g}."
    vc = y.value_counts(normalize=True).round(3).to_dict()
    return f"Target '{v.target}': classes {vc}."


# ── candidate features to accept or reject (T5/T6/T7 + target-encoding leak) ─────

def candidate_features(v: Variant, dev_idx: np.ndarray) -> list[dict[str, Any]]:
    """Each candidate is computed on the development split; truth says accept/reject."""
    from rs2610.study_a.evidence import SEMANTIC_FE

    f = v.frame
    inv = {orig: shown for shown, orig in v.rename.items()} if v.rename else {}
    nm = lambda c: inv.get(c, c)  # noqa: E731 — original -> shown name
    y_all = f[v.target].to_numpy()
    yb = (y_all > np.median(y_all)).astype(int) if v.ds.task_type == "regression" else y_all
    orig = f.rename(columns=v.rename) if v.rename else f
    cands: list[tuple[str, str, pd.Series, bool, str]] = []
    sem = SEMANTIC_FE.get(v.ds.dataset_id)
    if sem is not None:
        sdf = sem(orig).replace([np.inf, -np.inf], np.nan)
        for col in list(sdf.columns)[:2]:
            cands.append((f"cand_{col}", f"{col} (domain recipe over existing columns)", sdf[col], True, "semantic"))
    cands.append(("cand_key_log", f"log of {nm('record_key')}", np.log(orig["record_key"].astype(float)), False, "identifier"))
    post = v.truth["post_outcome_all"][0]
    p = orig[post]
    pv = (p.astype(str) != "none").astype(float) if not pd.api.types.is_numeric_dtype(p) else (pd.to_numeric(p) > 0).astype(float)
    cands.append(("cand_post_flag", f"indicator that {nm(post)} is set / positive", pv, False, "post_outcome"))
    cands.append(("cand_friday", f"{nm('load_weekday')} == Fri", (orig["load_weekday"] == "Fri").astype(float), False, "artifact"))
    cat = next((c for c in orig.columns if c not in (v.ds.target, "load_weekday", post, "record_key")
                and not pd.api.types.is_numeric_dtype(orig[c]) and 3 <= orig[c].nunique() <= 60), None)
    if cat is None:
        cat = next(c for c in orig.columns if c not in (v.ds.target, "record_key") and 3 <= orig[c].nunique() <= 60)
    te = orig[cat].astype(str).map(pd.Series(yb).groupby(orig[cat].astype(str).to_numpy()).mean())
    cands.append(("cand_target_mean", f"mean of the target per value of {nm(cat)}, computed on the full table including evaluation rows",
                  te.astype(float), False, "target_leak"))
    out = []
    ydev = yb[dev_idx]
    for cid, desc, series, ok, kind in cands:
        x = pd.Series(series).to_numpy(dtype=float)[dev_idx]
        m = ~np.isnan(x)
        auc = roc_auc_score(ydev[m], x[m]) if len(np.unique(ydev[m])) > 1 and np.nanstd(x[m]) > 0 else 0.5
        out.append({"id": cid, "description": desc, "univariate_auc": round(float(max(auc, 1 - auc)), 3), "truth_accept": ok, "kind": kind})
    return out
