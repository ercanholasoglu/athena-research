"""Feature matrices, splits and metrics shared by both studies."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, f1_score, r2_score, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit, train_test_split

from rs2610.common.data import SEED, Dataset

LOW_CARD = 15


def clean_columns(ds: Dataset, df: pd.DataFrame, *, keep: tuple[str, ...] = ()) -> list[str]:
    """Feature columns after removing target, IDs, post-event and target-derived columns."""
    t = ds.truth
    drop = {ds.target, *t.get("ids", []), *t.get("post_event", []), *t.get("target_derived", [])}
    if ds.dataset_id == "bike_sharing":
        drop |= {"dteday"}
    if ds.dataset_id == "hillstrom_email":
        drop |= {"visit", "spend", "conversion"}
    return [c for c in df.columns if c not in drop or c in keep]


def encode(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Numeric matrix: low-cardinality categoricals one-hot, others frequency-encoded."""
    out = []
    for c in cols:
        s = df[c]
        if not pd.api.types.is_numeric_dtype(s) or pd.api.types.is_bool_dtype(s):
            s = s.astype(str)
            if s.nunique() <= LOW_CARD:
                out.append(pd.get_dummies(s, prefix=c, dtype=float))
            else:
                out.append(s.map(s.value_counts(normalize=True)).rename(c).astype(float).to_frame())
        else:
            out.append(pd.to_numeric(s, errors="coerce").astype(float).to_frame())
    X = pd.concat(out, axis=1)
    X.columns = [str(c).replace("[", "(").replace("]", ")").replace("<", "lt").replace(",", "_").replace(":", "_")
                 for c in X.columns]
    return X


def target(ds: Dataset, df: pd.DataFrame) -> np.ndarray:
    y = df[ds.target]
    if ds.task_type == "multiclass":
        return pd.Categorical(y).codes.astype(int)
    return y.to_numpy(dtype=float if ds.task_type == "regression" else int)


def holdout_split(ds: Dataset, df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, str]:
    """Return (dev_idx, test_idx, scheme). The scheme mirrors the semantically correct split."""
    n = len(df)
    idx = np.arange(n)
    if ds.dataset_id in ("bike_sharing", "card_fraud_synth"):
        order = np.argsort(df["instant" if ds.dataset_id == "bike_sharing" else "event_hour"].to_numpy(), kind="stable")
        cut = int(n * 0.75)
        return np.sort(order[:cut]), np.sort(order[cut:]), "time_based"
    if ds.truth.get("group_col"):
        gss = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=SEED)
        dev, test = next(gss.split(idx, groups=df[ds.truth["group_col"]]))
        return dev, test, "group"
    strat = target(ds, df) if ds.task_type != "regression" else None
    dev, test = train_test_split(idx, test_size=0.25, random_state=SEED, stratify=strat)
    return np.sort(dev), np.sort(test), "stratified"


def score(task_type: str, y: np.ndarray, p: np.ndarray) -> float:
    """Primary metric, higher is better: ROC-AUC (binary), macro OVR AUC (multiclass), R² (regression)."""
    if task_type == "binary":
        return float(roc_auc_score(y, p))
    if task_type == "multiclass":
        return float(roc_auc_score(y, p, multi_class="ovr", average="macro"))
    return float(r2_score(y, p))


def metric_name(task_type: str) -> str:
    return {"binary": "roc_auc", "multiclass": "macro_ovr_auc", "regression": "r2"}[task_type]


def ece(y: np.ndarray, p: np.ndarray, bins: int = 10) -> float:
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(p, edges) - 1, 0, bins - 1)
    tot = 0.0
    for b in range(bins):
        m = idx == b
        if m.any():
            tot += m.mean() * abs(y[m].mean() - p[m].mean())
    return float(tot)


def extra_binary(y: np.ndarray, p: np.ndarray, thr: float = 0.5) -> dict[str, float]:
    return {"pr_auc": float(average_precision_score(y, p)), "f1": float(f1_score(y, p >= thr, zero_division=0)),
            "brier": float(np.mean((p - y) ** 2)), "ece": ece(y, p)}


def jsonable(o: Any) -> Any:
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    return o
