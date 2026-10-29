"""Study B2 deterministic feature validation and downstream check (never shown to any model).

Every feature (invented, or proposed in the frozen FE call) is executed and judged on separate axes:

SOURCE VALIDITY   inputs exist (shown names mapped back to original names), op known, executable, not degenerate
LEAKAGE           input is an identifier / post-outcome / warehouse artifact / target-derived column / the target
SEMANTIC VALIDITY frozen Study B rule table (``study_b.evaluate.semantic_validity``) for its ops; the added ops follow the
                  closest frozen op (min/max/std like sum); count_positive, gt_threshold and eq_value only test a
                  condition, so they are valid for any column type unless an input is barred
STATISTICS        3-fold LightGBM CV gain over the clean base on development rows (6000-row subsample), stability (share
                  of folds with positive gain), held-out gain on the deployment-masked test split, missingness, redundancy
                  (max |Spearman| with any clean numeric column)
GENERALIZATION    CV gain versus held-out deployed gain

Pre-registered classes (thresholds fixed before the B2 freeze):
  VALID_USEFUL             valid, leak-free, CV gain > 0.001 and deployed held-out gain > 0
  VALID_NOT_USEFUL         valid, leak-free, otherwise
  INVALID_HIGH_APPARENT    leaky or semantically invalid, CV gain > 0.005
  INVALID_LOW_GAIN         leaky or semantically invalid, otherwise
  NOT_EXECUTABLE           source-invalid (reported separately)
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

from rs2610.common.data import SEED, by_id
from rs2610.common.prep import holdout_split, score
from rs2610.replication.b2.variants import TD_COL, b2_base, deploy_value
from rs2610.study_b.evaluate import _cv, _matrix, _model, _pred, compute_feature, deploy_mask, semantic_validity

CACHE = Path(__file__).resolve().parents[2] / "artifacts" / "cache" / "b2_eval"
BASE_OPS = {"ratio", "diff", "product", "sum", "mean", "log1p", "is_zero"}
AS_FROZEN = {"min": "sum", "max": "sum", "std": "sum"}
CONDITION_OPS = {"count_positive", "gt_threshold", "eq_value"}
USEFUL_CV, HIGH_APPARENT_CV = 0.001, 0.005


@lru_cache(maxsize=None)
def setup(did: str) -> dict[str, Any]:
    ds = by_id(did)
    v = b2_base(ds)
    dev, test, scheme = holdout_split(ds, v.frame)
    masked = deploy_mask(v.frame, v.truth, test, v.target)
    masked[TD_COL] = masked[TD_COL].astype(float)
    masked.loc[masked.index[test], TD_COL] = deploy_value(v, dev, test)  # historical segment rate: available, not leaky
    y = v.frame[v.target].to_numpy().astype(int)
    bad = set(v.truth["ids_all"]) | set(v.truth["leak_all"]) | {v.target} | ({"conversion"} if did == "hillstrom_email" else set())
    clean = [c for c in v.frame.columns if c not in bad]
    rng = np.random.default_rng(SEED)
    sub = dev if len(dev) <= 6000 else np.sort(rng.choice(dev, 6000, replace=False))
    return {"ds": ds, "v": v, "dev": dev, "test": test, "masked": masked, "y": y, "clean": clean, "sub": sub}


def compute(frame: pd.DataFrame, spec: dict[str, Any]) -> pd.Series | str:
    op, inputs = spec.get("op"), list(spec.get("inputs") or [])
    if op in BASE_OPS:
        return compute_feature(frame, {"op": op, "inputs": inputs})
    if not inputs:
        return "invalid_op"
    if any(c not in frame.columns for c in inputs):
        return "unknown_column"
    if op == "eq_value":
        if len(inputs) != 1:
            return "arity"
        out = (frame[inputs[0]].astype(str) == str(spec.get("value"))).astype(float)
    else:
        if any(not pd.api.types.is_numeric_dtype(frame[c]) for c in inputs):
            return "non_numeric_input"
        X = pd.concat([frame[c].astype(float) for c in inputs], axis=1)
        if op == "min":
            out = X.min(axis=1)
        elif op == "max":
            out = X.max(axis=1)
        elif op == "std":
            if len(inputs) < 2:
                return "arity"
            out = X.std(axis=1)
        elif op == "count_positive":
            out = (X > 0).sum(axis=1).astype(float)
        elif op == "gt_threshold":
            if len(inputs) != 1:
                return "arity"
            try:
                thr = float(spec.get("threshold"))
            except (TypeError, ValueError):
                return "bad_threshold"
            out = (X.iloc[:, 0] > thr).astype(float)
        else:
            return "invalid_op"
    out = out.replace([np.inf, -np.inf], np.nan)
    if out.notna().sum() == 0 or out.nunique() < 2:
        return "degenerate"
    return out


def leakage(inputs: list[str], truth: dict[str, Any], target: str) -> list[str]:
    kinds = []
    for c in inputs:
        if c == target:
            kinds.append("target")
        elif c in truth.get("target_derived_b2", []):
            kinds.append("target_derived")
        elif c in truth["ids_all"]:
            kinds.append("identifier")
        elif c in truth["artifacts"]:
            kinds.append("artifact")
        elif c in truth["post_outcome_all"]:
            kinds.append("post_outcome")
    return sorted(set(kinds))


def _semantic(spec: dict[str, Any], truth: dict[str, Any], target: str) -> str:
    op = spec.get("op")
    if op in CONDITION_OPS:
        bad = set(truth["ids_all"]) | set(truth["leak_all"]) | {target} | set(truth.get("redundant", []))
        return "invalid" if set(spec["inputs"]) & bad else "valid"
    return semantic_validity({"op": AS_FROZEN.get(op, op), "inputs": spec["inputs"]}, truth, target)


def validate(did: str, spec: dict[str, Any], rename: dict[str, str]) -> dict[str, Any]:
    spec = {"op": spec.get("op"), "inputs": [rename.get(str(c), str(c)) for c in (spec.get("inputs") or [])],
            "threshold": spec.get("threshold"), "value": spec.get("value")}
    key = hashlib.sha256(json.dumps(["b2feat", did, spec], sort_keys=True, default=str).encode()).hexdigest()[:24]
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text())
    st = setup(did)
    v, task = st["v"], st["ds"].task_type
    res: dict[str, Any] = {**spec, "leakage": leakage(spec["inputs"], v.truth, v.target),
                           "semantic_validity": _semantic(spec, v.truth, v.target)}
    feat = compute(v.frame, spec)
    if isinstance(feat, str):
        res.update({"executable": False, "failure": feat, "class": "NOT_EXECUTABLE"})
        path.write_text(json.dumps(res))
        return res
    y = st["y"]
    base = _matrix(v.frame, st["clean"], {})
    withf = base.copy()
    withf["fe_new"] = feat.to_numpy()
    folds = StratifiedKFold(3, shuffle=True, random_state=SEED)
    gains = np.array(_cv(withf, y, task, st["sub"], folds)) - np.array(_cv(base, y, task, st["sub"], folds))
    fdep = compute(st["masked"], spec)
    withf_dep = base.copy()
    withf_dep["fe_new"] = fdep.to_numpy() if not isinstance(fdep, str) else np.nan
    mb = _model(task).fit(base.iloc[st["dev"]], y[st["dev"]])
    mw = _model(task).fit(withf.iloc[st["dev"]], y[st["dev"]])
    t_base = score(task, y[st["test"]], _pred(mb, base.iloc[st["test"]], task))
    t_dep = score(task, y[st["test"]], _pred(mw, withf_dep.iloc[st["test"]], task))
    num = [c for c in st["clean"] if pd.api.types.is_numeric_dtype(v.frame[c]) and c not in spec["inputs"]]
    fs = feat.iloc[st["sub"]]
    red = max((abs(fs.corr(v.frame[c].iloc[st["sub"]], method="spearman")) for c in num), default=0.0)
    res.update({"executable": True, "cv_gain": float(gains.mean()), "stability": float((gains > 0).mean()),
                "test_gain_deploy": float(t_dep - t_base), "missing_share": float(feat.isna().mean()),
                "redundancy_max_spearman": float(0.0 if pd.isna(red) else red)})
    valid = not res["leakage"] and res["semantic_validity"] != "invalid"
    if valid:
        res["class"] = "VALID_USEFUL" if res["cv_gain"] > USEFUL_CV and res["test_gain_deploy"] > 0 else "VALID_NOT_USEFUL"
    else:
        res["class"] = "INVALID_HIGH_APPARENT" if res["cv_gain"] > HIGH_APPARENT_CV else "INVALID_LOW_GAIN"
    path.write_text(json.dumps(res))
    return res


def downstream(did: str, blocked: list[str], features: list[dict[str, Any]]) -> dict[str, Any]:
    """Model the run would ship: all columns minus what it blocked, plus its invented features that are executable and not
    self-assessed 'likely' leaky. Scored on the deployment-masked test split (deployed) and as recorded (naive)."""
    key = hashlib.sha256(json.dumps(["b2down", did, sorted(blocked), features], sort_keys=True, default=str).encode()).hexdigest()[:24]
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text())
    st = setup(did)
    v, task, y = st["v"], st["ds"].task_type, st["y"]
    cols = [c for c in v.frame.columns if c != v.target and c not in set(blocked) and not (did == "hillstrom_email" and c == "conversion")]
    extra, extra_dep = {}, {}
    for i, f in enumerate(features):
        a, b = compute(v.frame, f), compute(st["masked"], f)
        if not isinstance(a, str):
            extra[str(i)] = a
            extra_dep[str(i)] = b if not isinstance(b, str) else pd.Series(np.nan, index=v.frame.index)
    X, Xd = _matrix(v.frame, cols, extra), _matrix(st["masked"], cols, extra_dep)
    Xd = Xd.reindex(columns=X.columns)
    m = _model(task).fit(X.iloc[st["dev"]], y[st["dev"]])
    naive = score(task, y[st["test"]], _pred(m, X.iloc[st["test"]], task))
    dep = score(task, y[st["test"]], _pred(m, Xd.iloc[st["test"]], task))
    res = {"test_naive": naive, "test_deploy": dep, "leak_inflation": naive - dep, "deploy_collapse": bool(naive - dep > 0.05),
           "n_inputs": len(cols), "n_engineered": len(extra)}
    path.write_text(json.dumps(res))
    return res


def oracle(did: str) -> float:
    st = setup(did)
    blocked = [c for c in st["v"].frame.columns if c not in st["clean"]]
    return downstream(did, blocked, [])["test_deploy"]
