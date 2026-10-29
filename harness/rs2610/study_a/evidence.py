"""Measured evidence for Study A.

For each dataset: a 75 / 25 development / test split (semantically correct
scheme: time-based for temporal data, grouped for repeated entities).  Every
option of every measurable task family is actually executed:

* evidence the reasoning modes will see  = cross-validation on the dev split
  (or a small pilot for families where a pilot is the realistic evidence);
* oracle used only for regret            = score on the untouched test split.

    python -m rs2610.study_a.evidence [dataset_id ...]
"""
from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path
from typing import Any, Callable

import lightgbm as lgb
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier, CatBoostRegressor
from sklearn.calibration import CalibratedClassifierCV
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import GroupKFold, KFold, StratifiedKFold, TimeSeriesSplit
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from rs2610.common.data import SEED, Dataset, by_id, datasets
from rs2610.common.prep import clean_columns, encode, extra_binary, holdout_split, jsonable, metric_name, score, target

warnings.filterwarnings("ignore")
OUT = Path(__file__).resolve().parents[1] / "artifacts" / "study_a" / "evidence"
N_FOLDS = 5


def lgbm(task: str, **kw: Any) -> Any:
    base = dict(n_estimators=300, learning_rate=0.05, num_leaves=31, random_state=SEED, verbose=-1, n_jobs=4)
    base.update(kw)
    return lgb.LGBMRegressor(**base) if task == "regression" else lgb.LGBMClassifier(**base)


def families(task: str) -> dict[str, Callable[[], Any]]:
    imp = lambda: SimpleImputer(strategy="median")  # noqa: E731
    if task == "regression":
        return {
            "linear_model": lambda: make_pipeline(imp(), StandardScaler(), Ridge(alpha=1.0)),
            "random_forest": lambda: make_pipeline(imp(), RandomForestRegressor(300, min_samples_leaf=2, n_jobs=-1, random_state=SEED)),
            "lightgbm": lambda: lgbm(task),
            "catboost": lambda: CatBoostRegressor(iterations=400, verbose=0, random_seed=SEED, thread_count=4),
            "neural_net": lambda: make_pipeline(imp(), StandardScaler(), MLPRegressor(hidden_layer_sizes=(64, 32), early_stopping=True, max_iter=300, random_state=SEED)),
        }
    return {
        "linear_model": lambda: make_pipeline(imp(), StandardScaler(), LogisticRegression(max_iter=2000, C=1.0)),
        "random_forest": lambda: make_pipeline(imp(), RandomForestClassifier(300, min_samples_leaf=2, n_jobs=-1, random_state=SEED)),
        "lightgbm": lambda: lgbm(task),
        "catboost": lambda: CatBoostClassifier(iterations=400, verbose=0, random_seed=SEED, thread_count=4),
        "neural_net": lambda: make_pipeline(imp(), StandardScaler(), MLPClassifier(hidden_layer_sizes=(64, 32), early_stopping=True, max_iter=300, random_state=SEED)),
    }


def predict(model: Any, X: pd.DataFrame, task: str) -> np.ndarray:
    if task == "regression":
        return model.predict(X)
    p = model.predict_proba(X)
    return p[:, 1] if task == "binary" else p


def splitter(task: str, n_folds: int = N_FOLDS) -> Any:
    return KFold(n_folds, shuffle=True, random_state=SEED) if task == "regression" else StratifiedKFold(n_folds, shuffle=True, random_state=SEED)


def cv_eval(make: Callable[[], Any], X: pd.DataFrame, y: np.ndarray, task: str, *, folds: Any = None,
            groups: np.ndarray | None = None, fit_kw: Callable[[np.ndarray], dict] | None = None,
            transform: Callable[[pd.DataFrame, pd.DataFrame, np.ndarray], tuple[pd.DataFrame, pd.DataFrame]] | None = None,
            ) -> dict[str, Any]:
    folds = folds or splitter(task)
    scores, times = [], []
    oof = np.zeros((len(y),) if task != "multiclass" else (len(y), len(np.unique(y))))
    for tr, va in folds.split(X, y, groups):
        Xtr, Xva = X.iloc[tr], X.iloc[va]
        if transform:
            Xtr, Xva = transform(Xtr, Xva, y[tr])
        m = make()
        t0 = time.time()
        m.fit(Xtr, y[tr], **(fit_kw(y[tr]) if fit_kw else {}))
        times.append(time.time() - t0)
        p = predict(m, Xva, task)
        oof[va] = p
        scores.append(score(task, y[va], p))
    out = {"fold_scores": [round(s, 5) for s in scores], "mean": float(np.mean(scores)), "std": float(np.std(scores, ddof=1)),
           "fit_seconds_mean": float(np.mean(times))}
    if task == "binary":
        out.update({k: round(v, 5) for k, v in extra_binary(y, oof).items()})
    return out


def test_eval(make: Callable[[], Any], Xd: pd.DataFrame, yd: np.ndarray, Xt: pd.DataFrame, yt: np.ndarray, task: str,
              fit_kw: dict | None = None, transform: Callable | None = None, thr: float = 0.5) -> dict[str, Any]:
    if transform:
        Xd, Xt = transform(Xd, Xt, yd)
    m = make()
    t0 = time.time()
    m.fit(Xd, yd, **(fit_kw or {}))
    fit_s = time.time() - t0
    p = predict(m, Xt, task)
    out = {"score": score(task, yt, p), "fit_seconds": fit_s}
    if task == "binary":
        out.update(extra_binary(yt, p, thr))
    return out


# ── semantic feature recipes (the "semantic" FE option) ──────────────────────

def _yes(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    return sum((df[c] == "Yes").astype(float) for c in cols)


SEMANTIC_FE: dict[str, Callable[[pd.DataFrame], pd.DataFrame]] = {
    "telco_churn": lambda d: pd.DataFrame({"charges_per_month_of_tenure": d.TotalCharges / (d.tenure + 1),
                                           "price_increase_ratio": d.MonthlyCharges / (d.TotalCharges / (d.tenure + 1) + 1),
                                           "n_addons": _yes(d, ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"])}),
    "german_credit": lambda d: pd.DataFrame({"amount_per_month": d.A5 / d.A2, "burden": d.A8 * d.A5 / d.A2, "amount_per_age": d.A5 / d.A13}),
    "bank_marketing": lambda d: pd.DataFrame({"previously_contacted": (d.pdays != -1).astype(float), "balance_per_age": d.balance / d.age,
                                              "contacts_ratio": d.campaign / (d.previous + 1)}),
    "adult_income": lambda d: pd.DataFrame({"capital_net": d.capital_gain - d.capital_loss, "hours_x_edu": d.hours_per_week * d.education_num,
                                            "has_capital": ((d.capital_gain + d.capital_loss) > 0).astype(float)}),
    "bike_sharing": lambda d: pd.DataFrame({"hr_sin": np.sin(2 * np.pi * d.hr / 24), "hr_cos": np.cos(2 * np.pi * d.hr / 24),
                                            "rush_hour": (d.hr.isin([7, 8, 17, 18]) & (d.workingday == 1)).astype(float),
                                            "temp_x_working": d.temp * d.workingday}),
    "iranian_churn": lambda d: pd.DataFrame({"seconds_per_call": d.Seconds_of_Use / (d.Frequency_of_use + 1),
                                             "failure_rate": d.Call_Failure / (d.Frequency_of_use + 1),
                                             "sms_share": d.Frequency_of_SMS / (d.Frequency_of_SMS + d.Frequency_of_use + 1)}),
    "taiwan_default": lambda d: pd.DataFrame({"utilization": d.BILL_AMT1 / d.LIMIT_BAL.clip(lower=1),
                                              "pay_ratio": d.PAY_AMT1 / d.BILL_AMT1.clip(lower=1),
                                              "months_delinquent": sum((d[c] > 0).astype(float) for c in ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]),
                                              "bill_trend": (d.BILL_AMT1 - d.BILL_AMT6) / d.LIMIT_BAL.clip(lower=1)}),
    "coil_caravan": lambda d: pd.DataFrame({"n_policies": d[[c for c in d.columns if c.startswith("A")]].sum(axis=1),
                                            "premium_bands": d[[c for c in d.columns if c.startswith("P")]].sum(axis=1),
                                            "car_x_fire": d.PPERSAUT * d.PBRAND}),
    "diabetes_readmission": lambda d: pd.DataFrame({"prior_visits": d.number_outpatient + d.number_emergency + d.number_inpatient,
                                                    "meds_per_day": d.num_medications / d.time_in_hospital,
                                                    "labs_per_day": d.num_lab_procedures / d.time_in_hospital}),
    "card_fraud_synth": lambda d: pd.DataFrame({"amount_vs_history": d.amount / d.account_avg_amount_90d,
                                                "burst_share": d.txn_count_1h / (d.txn_count_24h + 1),
                                                "night": ((d.event_hour % 24) < 6).astype(float)}),
    "online_shoppers": lambda d: pd.DataFrame({"total_pages": d.Administrative + d.Informational + d.ProductRelated,
                                               "product_share": d.ProductRelated / (d.Administrative + d.Informational + d.ProductRelated + 1),
                                               "sec_per_product_page": d.ProductRelated_Duration / (d.ProductRelated + 1)}),
    "thyroid_sick": lambda d: pd.DataFrame({"t3_tt4_ratio": d.T3 / d.TT4, "log_tsh": np.log1p(d.TSH), "n_measured": sum(
        (d[c] == "t").astype(float) for c in ["TSH_measured", "T3_measured", "TT4_measured", "T4U_measured", "FTI_measured"])}),
}


def _interactions(cols: list[str]) -> Callable:
    def tf(Xtr: pd.DataFrame, Xva: pd.DataFrame, ytr: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
        add_tr, add_va = {}, {}
        for i, a in enumerate(cols):
            for b in cols[i + 1:]:
                add_tr[f"{a}*{b}"] = Xtr[a] * Xtr[b]
                add_va[f"{a}*{b}"] = Xva[a] * Xva[b]
        return pd.concat([Xtr, pd.DataFrame(add_tr, index=Xtr.index)], axis=1), pd.concat([Xva, pd.DataFrame(add_va, index=Xva.index)], axis=1)
    return tf


def _pca(k: int) -> Callable:
    def tf(Xtr: pd.DataFrame, Xva: pd.DataFrame, ytr: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
        pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), PCA(min(k, Xtr.shape[1] - 1), random_state=SEED))
        a = pipe.fit_transform(Xtr)
        b = pipe.transform(Xva)
        cols = [f"pc{i}" for i in range(a.shape[1])]
        return (pd.concat([Xtr, pd.DataFrame(a, index=Xtr.index, columns=cols)], axis=1),
                pd.concat([Xva, pd.DataFrame(b, index=Xva.index, columns=cols)], axis=1))
    return tf


def _select(kind: str, task: str) -> Callable:
    def tf(Xtr: pd.DataFrame, Xva: pd.DataFrame, ytr: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
        k = max(3, Xtr.shape[1] // 2)
        if kind == "filter_mutual_info":
            Xi = Xtr.fillna(Xtr.median())
            mi = (mutual_info_regression if task == "regression" else mutual_info_classif)(Xi, ytr, random_state=SEED)
            keep = Xtr.columns[np.argsort(-mi)[:k]]
        elif kind == "embedded_importance":
            m = lgbm(task, n_estimators=150).fit(Xtr, ytr)
            keep = Xtr.columns[np.argsort(-m.feature_importances_)[:k]]
        else:  # l1
            Xi = StandardScaler().fit_transform(Xtr.fillna(Xtr.median()))
            if task == "regression":
                from sklearn.linear_model import Lasso
                coef = Lasso(alpha=0.01 * np.std(ytr), max_iter=5000).fit(Xi, ytr).coef_
            else:
                l1 = LogisticRegression(penalty="l1", solver="liblinear", C=0.05, max_iter=3000)
                if len(np.unique(ytr)) > 2:  # liblinear is binary-only: one-vs-rest, max |coef| across classes
                    from sklearn.multiclass import OneVsRestClassifier
                    coef = np.abs(np.vstack([e.coef_ for e in OneVsRestClassifier(l1).fit(Xi, ytr).estimators_])).max(axis=0)
                else:
                    coef = l1.fit(Xi, ytr).coef_
            nz = np.flatnonzero(np.abs(np.ravel(coef)) > 1e-8)
            keep = Xtr.columns[nz] if len(nz) >= 3 else Xtr.columns[np.argsort(-np.abs(np.ravel(coef)))[:3]]
        return Xtr[keep], Xva[keep]
    return tf


HPO_SPACE_RNG = np.random.default_rng(SEED)
HPO_CONFIGS = [dict(n_estimators=int(HPO_SPACE_RNG.integers(100, 600)), learning_rate=float(10 ** HPO_SPACE_RNG.uniform(-2.3, -0.7)),
                    num_leaves=int(HPO_SPACE_RNG.integers(8, 128)), min_child_samples=int(HPO_SPACE_RNG.integers(5, 100)),
                    subsample=float(HPO_SPACE_RNG.uniform(0.5, 1.0)), subsample_freq=1, colsample_bytree=float(HPO_SPACE_RNG.uniform(0.4, 1.0)),
                    reg_lambda=float(10 ** HPO_SPACE_RNG.uniform(-3, 1))) for _ in range(60)]
HPO_DEPTHS = {"none": 0, "light": 8, "moderate": 24, "deep": 60}


def build(ds: Dataset) -> dict[str, Any]:
    t_start = time.time()
    df = ds.load()
    task = ds.task_type
    cols = clean_columns(ds, df)
    X = encode(df, cols)
    y = target(ds, df)
    dev, test, scheme = holdout_split(ds, df)
    Xd, yd, Xt, yt = X.iloc[dev].reset_index(drop=True), y[dev], X.iloc[test].reset_index(drop=True), y[test]
    ev: dict[str, Any] = {"dataset_id": ds.dataset_id, "task_type": task, "metric": metric_name(task), "split": ds.split,
                          "family": ds.family, "rows_original": ds.truth.get("original_rows"), "rows_used": len(df),
                          "dev_rows": len(dev), "test_rows": len(test), "holdout_scheme": scheme,
                          "n_raw_columns": len(cols), "n_encoded_features": X.shape[1]}
    if task != "regression":
        counts = np.bincount(yd)
        ev["class_balance"] = (counts / counts.sum()).round(4).tolist()
    ev["missing_share"] = float(X.isna().mean().mean())
    num = Xd.select_dtypes("number")
    corr = num.corr().abs().to_numpy().copy()
    np.fill_diagonal(corr, 0)
    ev["max_abs_feature_corr"] = float(np.nanmax(corr)) if corr.size else 0.0
    ev["n_pairs_corr_gt_0_9"] = int((np.triu(np.nan_to_num(corr)) > 0.9).sum())

    # 1. model family
    fam = {}
    for name, make in families(task).items():
        fam[name] = {"cv": cv_eval(make, Xd, yd, task), "test": test_eval(make, Xd, yd, Xt, yt, task)}
        print(f"  {ds.dataset_id} family {name} cv={fam[name]['cv']['mean']:.4f} test={fam[name]['test']['score']:.4f}", flush=True)
    ev["model_family"] = fam

    # 2. HPO depth (3-fold CV per config; nested sequences, so deeper always contains shallower)
    folds3 = splitter(task, 3)
    cfg_scores = []
    for cfg in HPO_CONFIGS[: max(HPO_DEPTHS.values())]:
        r = cv_eval(lambda c=cfg: lgbm(task, **c), Xd, yd, task, folds=folds3)
        cfg_scores.append((r["mean"], r["std"], r["fit_seconds_mean"]))
    default_cv = cv_eval(lambda: lgbm(task), Xd, yd, task, folds=folds3)
    hpo = {}
    for depth, n in HPO_DEPTHS.items():
        if n == 0:
            best_cfg, cvbest = {}, default_cv["mean"]
        else:
            i = int(np.argmax([s[0] for s in cfg_scores[:n]]))
            best_cfg, cvbest = HPO_CONFIGS[i], cfg_scores[i][0]
        te = test_eval(lambda c=best_cfg: lgbm(task, **c), Xd, yd, Xt, yt, task)
        hpo[depth] = {"n_configs": n, "cv_best": cvbest, "test": te["score"],
                      "search_seconds": float(sum(s[2] * 3 for s in cfg_scores[:n]))}
    hpo["_light_config_cv"] = [round(s[0], 5) for s in cfg_scores[:HPO_DEPTHS["light"]]]
    hpo["_default_cv"] = default_cv
    ev["hpo_depth"] = hpo

    # 3. feature engineering strategy — pilot (30 % of dev, 3 folds) is the shown evidence
    numeric_cols = [c for c in Xd.columns if Xd[c].nunique() > 2][:]
    top = list(pd.Series(lgbm(task, n_estimators=100).fit(Xd[numeric_cols], yd).feature_importances_, index=numeric_cols)
               .sort_values(ascending=False).index[:7]) if numeric_cols else []
    sem = SEMANTIC_FE.get(ds.dataset_id)
    sem_df = sem(df).replace([np.inf, -np.inf], np.nan) if sem else None
    strategies: dict[str, tuple[pd.DataFrame, Callable | None]] = {"minimal": (X, None)}
    if sem_df is not None:
        strategies["semantic"] = (pd.concat([X, sem_df.reset_index(drop=True)], axis=1), None)
    if len(top) >= 3:
        strategies["interaction_heavy"] = (X, _interactions(top))
    strategies["dimensionality_reduction"] = (X, _pca(10))
    rng = np.random.default_rng(SEED)
    pilot_idx = np.sort(rng.choice(len(dev), size=max(300, int(0.3 * len(dev))), replace=False))
    fe = {}
    for name, (XX, tf) in strategies.items():
        XXd, XXt = XX.iloc[dev].reset_index(drop=True), XX.iloc[test].reset_index(drop=True)
        fe[name] = {"n_features": int(XX.shape[1] + (len(top) * (len(top) - 1) // 2 if name == "interaction_heavy" else 0)
                                      + (10 if name == "dimensionality_reduction" else 0)),
                    "pilot": cv_eval(lambda: lgbm(task), XXd.iloc[pilot_idx].reset_index(drop=True), yd[pilot_idx], task, folds=folds3, transform=tf),
                    "cv": cv_eval(lambda: lgbm(task), XXd, yd, task, transform=tf),
                    "test": test_eval(lambda: lgbm(task), XXd, yd, XXt, yt, task, transform=tf)}
    ev["fe_strategy"] = fe

    # 4. feature selection
    fs = {}
    for name in ("none", "filter_mutual_info", "embedded_importance", "l1_regularized"):
        tf = None if name == "none" else _select(name, task)
        nfeat = Xd.shape[1] if tf is None else tf(Xd, Xd.iloc[:5], yd)[0].shape[1]
        fs[name] = {"n_features": int(nfeat),
                    "pilot": cv_eval(lambda: lgbm(task), Xd.iloc[pilot_idx].reset_index(drop=True), yd[pilot_idx], task, folds=folds3, transform=tf),
                    "cv": cv_eval(lambda: lgbm(task), Xd, yd, task, transform=tf),
                    "test": test_eval(lambda: lgbm(task), Xd, yd, Xt, yt, task, transform=tf)}
    ev["fs_strategy"] = fs

    if task == "binary" and min(ev["class_balance"]) < 0.35:
        # 5. imbalance handling (decision metric F1 at the operating threshold)
        pos = yd.mean()
        def oversample(Xtr: pd.DataFrame, Xva: pd.DataFrame, ytr: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
            return Xtr, Xva
        imb = {}
        variants = {
            "none": (lambda: lgbm(task), None),
            "class_weighting": (lambda: lgbm(task, class_weight="balanced"), None),
            "random_oversampling": ("oversample", None),
            "threshold_moving": ("threshold", None),
        }
        skf = splitter(task)
        for name, (make, _) in variants.items():
            f1s, prs = [], []
            for tr, va in skf.split(Xd, yd):
                Xtr, ytr = Xd.iloc[tr], yd[tr]
                m = lgbm(task)
                thr = 0.5
                if name == "class_weighting":
                    m = lgbm(task, class_weight="balanced")
                if name == "random_oversampling":
                    r2 = np.random.default_rng(SEED)
                    pos_i = np.flatnonzero(ytr == 1)
                    extra = r2.choice(pos_i, size=max(0, int((ytr == 0).sum() - len(pos_i))), replace=True)
                    Xtr, ytr = pd.concat([Xtr, Xtr.iloc[extra]]), np.concatenate([ytr, ytr[extra]])
                if name == "threshold_moving":
                    inner = splitter(task, 3)
                    oof = np.zeros(len(tr))
                    for a, b in inner.split(Xtr, ytr):
                        oof[b] = lgbm(task).fit(Xtr.iloc[a], ytr[a]).predict_proba(Xtr.iloc[b])[:, 1]
                    grid = np.linspace(0.05, 0.95, 37)
                    from sklearn.metrics import f1_score as _f1
                    thr = float(grid[np.argmax([_f1(ytr, oof >= g, zero_division=0) for g in grid])])
                m.fit(Xtr, ytr)
                p = m.predict_proba(Xd.iloc[va])[:, 1]
                e = extra_binary(yd[va], p, thr)
                f1s.append(e["f1"])
                prs.append(e["pr_auc"])
            imb[name] = {"cv": {"fold_scores": [round(v, 5) for v in f1s], "mean": float(np.mean(f1s)), "std": float(np.std(f1s, ddof=1)),
                                "pr_auc_mean": float(np.mean(prs))}}
        # test
        for name in imb:
            Xtr, ytr, thr = Xd, yd, 0.5
            m = lgbm(task, class_weight="balanced") if name == "class_weighting" else lgbm(task)
            if name == "random_oversampling":
                r2 = np.random.default_rng(SEED)
                pos_i = np.flatnonzero(ytr == 1)
                extra = r2.choice(pos_i, size=int((ytr == 0).sum() - len(pos_i)), replace=True)
                Xtr, ytr = pd.concat([Xtr, Xtr.iloc[extra]]), np.concatenate([ytr, ytr[extra]])
            if name == "threshold_moving":
                oof = np.zeros(len(yd))
                for a, b in splitter(task, 3).split(Xd, yd):
                    oof[b] = lgbm(task).fit(Xd.iloc[a], yd[a]).predict_proba(Xd.iloc[b])[:, 1]
                from sklearn.metrics import f1_score as _f1
                grid = np.linspace(0.05, 0.95, 37)
                thr = float(grid[np.argmax([_f1(yd, oof >= g, zero_division=0) for g in grid])])
                imb[name]["chosen_threshold"] = thr
            m.fit(Xtr, ytr)
            p = m.predict_proba(Xt)[:, 1]
            e = extra_binary(yt, p, thr)
            imb[name]["test"] = {"score": e["f1"], "pr_auc": e["pr_auc"]}
        ev["imbalance"] = imb
        ev["minority_share"] = float(min(pos, 1 - pos))

    # 6. validation strategy: optimism of naive random CV vs the scheme that matches deployment
    val: dict[str, Any] = {}
    naive = cv_eval(lambda: lgbm(task), Xd, yd, task, folds=KFold(N_FOLDS, shuffle=True, random_state=SEED))
    val["random_kfold"] = {"cv_mean": naive["mean"], "cv_std": naive["std"]}
    if task != "regression":
        strat = cv_eval(lambda: lgbm(task), Xd, yd, task)
        val["stratified_kfold"] = {"cv_mean": strat["mean"], "cv_std": strat["std"]}
    if ds.truth.get("group_col"):
        g = df[ds.truth["group_col"]].to_numpy()[dev]
        gk = cv_eval(lambda: lgbm(task), Xd, yd, task, folds=GroupKFold(N_FOLDS), groups=g)
        val["group_kfold"] = {"cv_mean": gk["mean"], "cv_std": gk["std"]}
        val["_repeat_entities_share"] = float(1 - pd.Series(g).nunique() / len(g))
    if ds.truth.get("temporal") or ds.dataset_id in ("bike_sharing", "card_fraud_synth"):
        ts = cv_eval(lambda: lgbm(task), Xd, yd, task, folds=TimeSeriesSplit(N_FOLDS))
        val["time_based_split"] = {"cv_mean": ts["mean"], "cv_std": ts["std"]}
    val["_test_score_lgbm"] = fam["lightgbm"]["test"]["score"]
    ev["validation"] = val

    # 7. calibration
    if task == "binary":
        cal = {}
        for name in ("none", "platt_sigmoid", "isotonic"):
            make = (lambda: lgbm(task)) if name == "none" else (
                lambda n=name: CalibratedClassifierCV(lgbm(task), method="sigmoid" if n == "platt_sigmoid" else "isotonic", cv=3))
            briers, eces = [], []
            for tr, va in splitter(task).split(Xd, yd):
                p = make().fit(Xd.iloc[tr], yd[tr]).predict_proba(Xd.iloc[va])[:, 1]
                e = extra_binary(yd[va], p)
                briers.append(e["brier"])
                eces.append(e["ece"])
            p = make().fit(Xd, yd).predict_proba(Xt)[:, 1]
            e = extra_binary(yt, p)
            cal[name] = {"cv": {"fold_brier": [round(b, 5) for b in briers], "brier_mean": float(np.mean(briers)),
                                "brier_std": float(np.std(briers, ddof=1)), "ece_mean": float(np.mean(eces))},
                         "test": {"brier": e["brier"], "ece": e["ece"]}}
        ev["calibration"] = cal
    ev["build_seconds"] = round(time.time() - t_start, 1)
    return ev


def main(ids: list[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    todo = [by_id(i) for i in ids] if ids else [d for d in datasets("A") if d.dataset_id != "hillstrom_email"]
    for ds in todo:
        path = OUT / f"{ds.dataset_id}.json"
        if path.exists():
            print("skip", ds.dataset_id)
            continue
        print("build", ds.dataset_id, flush=True)
        ev = build(ds)
        path.write_text(json.dumps(jsonable(ev), indent=1))
        print("done", ds.dataset_id, ev["build_seconds"], "s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
