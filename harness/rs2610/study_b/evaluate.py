"""Execute generated features, validate them, and measure downstream deployment quality.

Deployment realism: at test time a column that is only known after the outcome is
unavailable (set to NaN), and identifier / load-artifact values carry no target
information (randomly permuted across test rows).  A model that leaned on a leak
therefore loses its inflated score exactly as it would in production; the
*naive* score (test rows as recorded) is reported next to it as the inflation.

Feature rubric (B7), each dimension scored separately:
  statistical_value  CV gain of LightGBM(base + feature) over base on dev (3 folds)
  semantic_validity  deterministic rule table over annotated semantic types
  leakage_risk       HIGH if any input is an id / post-outcome / artifact / target
  stability          share of folds with positive gain
  interpretability   1 for one op on <= 2 inputs, 0.5 otherwise
  generalization     gain on the deployment-masked test split
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, KFold, StratifiedKFold, TimeSeriesSplit

from rs2610.common.data import SEED, by_id
from rs2610.common.prep import encode, holdout_split, score
from rs2610.study_b.variants import trapped

CACHE = Path(__file__).resolve().parents[1] / "artifacts" / "cache" / "study_b_eval"
QUANT = {"amount", "count", "duration", "rate", "age", "lab", "distance", "time"}
OPS = {"ratio", "diff", "product", "sum", "mean", "log1p", "is_zero"}


@lru_cache(maxsize=None)
def setup(did: str) -> dict[str, Any]:
    ds = by_id(did)
    v = trapped(ds)
    dev, test, scheme = holdout_split(ds, v.frame)
    return {"ds": ds, "v": v, "dev": dev, "test": test, "scheme": scheme}


def _model(task: str, n: int = 300) -> Any:
    kw = dict(n_estimators=n, learning_rate=0.05, num_leaves=31, random_state=SEED, verbose=-1, n_jobs=4)
    return lgb.LGBMRegressor(**kw) if task == "regression" else lgb.LGBMClassifier(**kw)


def _pred(m: Any, X: pd.DataFrame, task: str) -> np.ndarray:
    return m.predict(X) if task == "regression" else m.predict_proba(X)[:, 1]


def deploy_mask(frame: pd.DataFrame, truth: dict[str, Any], rows: np.ndarray, target: str | None = None) -> pd.DataFrame:
    """The target itself is unknown at prediction time, like every post-outcome column."""
    f = frame.copy()
    rng = np.random.default_rng(SEED + 99)
    for c in list(truth["post_outcome_all"]) + ([target] if target else []):
        if c in f:
            f.loc[f.index[rows], c] = np.nan if pd.api.types.is_numeric_dtype(f[c]) else None
    for c in set(truth["ids_all"]) | set(truth["artifacts"]):
        if c in f:
            vals = f[c].to_numpy()[rows].copy()
            rng.shuffle(vals)
            f.loc[f.index[rows], c] = vals
    return f


def compute_feature(frame: pd.DataFrame, spec: dict[str, Any]) -> pd.Series | str:
    op, inputs = spec.get("op"), list(spec.get("inputs") or [])
    if op not in OPS or not inputs:
        return "invalid_op"
    if any(c not in frame.columns for c in inputs):
        return "unknown_column"
    if any(not pd.api.types.is_numeric_dtype(frame[c]) for c in inputs):
        return "non_numeric_input"
    X = [frame[c].astype(float) for c in inputs]
    with np.errstate(all="ignore"):
        if op == "ratio":
            if len(X) != 2:
                return "arity"
            out = X[0] / X[1].replace(0, np.nan)
        elif op == "diff":
            if len(X) != 2:
                return "arity"
            out = X[0] - X[1]
        elif op == "product":
            out = X[0].copy()
            for x in X[1:]:
                out = out * x
        elif op == "sum":
            out = sum(X)
        elif op == "mean":
            out = sum(X) / len(X)
        elif op == "log1p":
            out = np.sign(X[0]) * np.log1p(X[0].abs())
        else:
            out = (X[0] == 0).astype(float)
    out = out.replace([np.inf, -np.inf], np.nan)
    if out.notna().sum() == 0 or out.nunique() < 2:
        return "degenerate"
    return out


def semantic_validity(spec: dict[str, Any], truth: dict[str, Any], target: str) -> str:
    inputs = list(spec.get("inputs") or [])
    bad = set(truth["ids_all"]) | set(truth["leak_all"]) | {target} | set(truth.get("redundant", []))
    if any(c in bad for c in inputs):
        return "invalid"
    st = truth.get("semtypes", {})
    types = [st.get(c) for c in inputs]
    if any(t in ("weight", "ordinal") for t in types) and spec.get("op") in ("ratio", "product", "diff", "log1p"):
        return "invalid"
    if any(t is None for t in types):
        return "unknown"
    op = spec.get("op")
    if op in ("ratio", "product", "log1p", "is_zero"):
        return "valid" if all(t in QUANT for t in types) else "invalid"
    if op in ("diff", "sum", "mean"):
        return "valid" if len(set(types)) == 1 and types[0] in QUANT else "invalid"
    return "unknown"


def _matrix(frame: pd.DataFrame, cols: list[str], extra: dict[str, pd.Series]) -> pd.DataFrame:
    X = encode(frame, cols) if cols else pd.DataFrame(index=frame.index)
    for k, s in extra.items():
        X[f"fe_{k}"] = s.to_numpy()
    return X.reset_index(drop=True)


def _y(st: dict) -> np.ndarray:
    v = st["v"]
    y = v.frame[v.target].to_numpy()
    return y.astype(float) if st["ds"].task_type == "regression" else y.astype(int)


def _cv(X: pd.DataFrame, y: np.ndarray, task: str, idx: np.ndarray, folds: Any, groups: np.ndarray | None = None, n: int = 150) -> list[float]:
    Xd, yd = X.iloc[idx].reset_index(drop=True), y[idx]
    out = []
    for tr, va in folds.split(Xd, yd, groups):
        m = _model(task, n).fit(Xd.iloc[tr], yd[tr])
        out.append(score(task, yd[va], _pred(m, Xd.iloc[va], task)))
    return out


def clean_cols(st: dict) -> list[str]:
    t = st["v"].truth
    bad = set(t["ids_all"]) | set(t["leak_all"]) | {st["v"].target}
    if st["ds"].dataset_id == "bike_sharing":
        bad |= {"dteday"}
    if st["ds"].dataset_id == "hillstrom_email":
        bad |= {"conversion"}
    return [c for c in st["v"].frame.columns if c not in bad]


def _key(*parts: Any) -> Path:
    h = hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:24]
    CACHE.mkdir(parents=True, exist_ok=True)
    return CACHE / f"{h}.json"


def validate_feature(did: str, spec: dict[str, Any], rename: dict[str, str]) -> dict[str, Any]:
    spec = {**spec, "inputs": [rename.get(c, c) for c in (spec.get("inputs") or [])]}
    path = _key("feat", did, spec.get("op"), spec["inputs"])
    if path.exists():
        return json.loads(path.read_text())
    st = setup(did)
    v, task = st["v"], st["ds"].task_type
    truth = v.truth
    res: dict[str, Any] = {"op": spec.get("op"), "inputs": spec["inputs"],
                           "leakage_risk": "HIGH" if set(spec["inputs"]) & (set(truth["ids_all"]) | set(truth["leak_all"]) | {v.target}) else "LOW",
                           "semantic_validity": semantic_validity(spec, truth, v.target)}
    feat = compute_feature(v.frame, spec)
    if isinstance(feat, str):
        res.update({"computable": False, "failure": feat})
        path.write_text(json.dumps(res))
        return res
    y = _y(st)
    rng = np.random.default_rng(SEED)
    dev = st["dev"] if len(st["dev"]) <= 6000 else np.sort(rng.choice(st["dev"], 6000, replace=False))
    base = _matrix(v.frame, clean_cols(st), {})
    withf = base.copy()
    withf["fe_new"] = feat.to_numpy()
    folds = KFold(3, shuffle=True, random_state=SEED) if task == "regression" else StratifiedKFold(3, shuffle=True, random_state=SEED)
    b, w = _cv(base, y, task, dev, folds), _cv(withf, y, task, dev, folds)
    gains = np.array(w) - np.array(b)
    masked = deploy_mask(v.frame, truth, st["test"], v.target)
    feat_dep = compute_feature(masked, spec)
    withf_dep = base.copy()
    withf_dep["fe_new"] = feat_dep.to_numpy() if not isinstance(feat_dep, str) else np.nan
    mb = _model(task).fit(base.iloc[st["dev"]], y[st["dev"]])
    mw = _model(task).fit(withf.iloc[st["dev"]], y[st["dev"]])
    t_base = score(task, y[st["test"]], _pred(mb, base.iloc[st["test"]], task))
    t_with = score(task, y[st["test"]], _pred(mw, withf_dep.iloc[st["test"]], task))
    res.update({"computable": True, "cv_gain": float(gains.mean()), "stability": float((gains > 0).mean()),
                "test_gain_deploy": float(t_with - t_base),
                "interpretability": 1.0 if len(spec["inputs"]) <= 2 else 0.5})
    path.write_text(json.dumps(res))
    return res


def downstream(did: str, blocked: list[str], features: list[dict[str, Any]], split_strategy: str | None,
               group_col: str | None) -> dict[str, Any]:
    """Model the run would ship: all columns minus what it blocked, plus its retained features."""
    path = _key("down", did, sorted(blocked), [(f["op"], f["inputs"]) for f in features], split_strategy, group_col)
    if path.exists():
        return json.loads(path.read_text())
    st = setup(did)
    v, task = st["v"], st["ds"].task_type
    y = _y(st)
    cols = [c for c in v.frame.columns if c != v.target and c not in set(blocked) and c != "dteday"]
    if did == "hillstrom_email":
        cols = [c for c in cols if c != "conversion"]
    extra = {}
    extra_dep = {}
    masked = deploy_mask(v.frame, v.truth, st["test"], v.target)
    for i, f in enumerate(features):
        a, b = compute_feature(v.frame, f), compute_feature(masked, f)
        if not isinstance(a, str):
            extra[str(i)] = a
            extra_dep[str(i)] = b if not isinstance(b, str) else pd.Series(np.nan, index=v.frame.index)
    X = _matrix(v.frame, cols, extra)
    Xdep = _matrix(masked, cols, extra_dep)
    Xdep = Xdep.reindex(columns=X.columns)
    m = _model(task).fit(X.iloc[st["dev"]], y[st["dev"]])
    naive = score(task, y[st["test"]], _pred(m, X.iloc[st["test"]], task))
    dep = score(task, y[st["test"]], _pred(m, Xdep.iloc[st["test"]], task))
    # validation estimate under the run's own split choice
    dev = st["dev"]
    groups = None
    if split_strategy == "time_based":
        folds = TimeSeriesSplit(4)
    elif split_strategy == "group_kfold" and group_col in v.frame.columns:
        folds, groups = GroupKFold(4), v.frame[group_col].to_numpy()[dev]
    elif task == "regression" or split_strategy == "random_kfold":
        folds = KFold(4, shuffle=True, random_state=SEED)
    else:
        folds = StratifiedKFold(4, shuffle=True, random_state=SEED)
    cv = float(np.mean(_cv(X, y, task, dev, folds, groups, n=300)))
    res = {"n_inputs": len(cols), "n_engineered": len(extra), "test_naive": naive, "test_deploy": dep,
           "leak_inflation": naive - dep, "cv_estimate": cv, "estimate_error": abs(cv - dep)}
    path.write_text(json.dumps(res))
    return res


def references(did: str) -> dict[str, Any]:
    """Oracle-clean model and use-everything model, for the same split."""
    st = setup(did)
    v = st["v"]
    oracle = downstream(did, [c for c in v.frame.columns if c not in clean_cols(st) and c != v.target], [], None, None)
    naive = downstream(did, [], [], None, None)
    return {"oracle_clean": oracle, "use_everything": naive}
