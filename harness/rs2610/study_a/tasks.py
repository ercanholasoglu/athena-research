"""Task instances for Study A, with pre-registered reference rules.

Reference contract (fixed before any reasoning-mode run):

* ``accept``   — options a reviewer would accept.  For measured families this is
  every option whose dev-split CV is not significantly worse than the best
  (paired t-test over the same folds, two-sided p >= 0.05).  For the HPO depth
  family it is every depth whose *test* score is within 0.005 of the best depth.
* ``parsimonious`` — the simplest member of ``accept`` (complexity order is
  declared per family).  Choosing an accepted but more complex option counts
  as *unnecessary complexity*, not as an error.
* ``utility``  — per-option score on the untouched test split (higher is
  better).  Regret = best utility − utility of the chosen option.  Families
  without a measured outcome have utility None and regret UNKNOWN.
* ``uncertainty_expected`` — the instance is built so that a single confident
  winner is not supported; scored by "preserved uncertainty" (UNDETERMINED or
  confidence <= 0.65).

Adversarial instances perturb real measured numbers; every perturbation is
listed in ``perturbation`` and reported in study-a-task-contracts.md.
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

from rs2610.common.data import by_id, datasets

EVID = Path(__file__).resolve().parents[1] / "artifacts" / "study_a" / "evidence"
UNDET = "UNDETERMINED"
ALPHA = 0.05
HPO_TOL = 0.005

FAMILY_LABEL = {"linear_model": "regularised linear model (logistic / ridge)", "random_forest": "random forest (300 trees)",
                "lightgbm": "LightGBM gradient boosting", "catboost": "CatBoost gradient boosting", "neural_net": "MLP neural network (64-32)"}
COMPLEXITY = {
    "MODEL_FAMILY": ["linear_model", "random_forest", "lightgbm", "catboost", "neural_net"],
    "HPO_DEPTH": ["none", "light", "moderate", "deep"],
    "FE_STRATEGY": ["minimal", "semantic", "dimensionality_reduction", "interaction_heavy"],
    "FS_STRATEGY": ["none", "filter_mutual_info", "embedded_importance", "l1_regularized"],
    "IMBALANCE": ["none", "threshold_moving", "class_weighting", "random_oversampling"],
    "CALIBRATION": ["none", "platt_sigmoid", "isotonic"],
}


def _opt(oid: str, label: str) -> dict[str, str]:
    return {"id": oid, "label": label}


def _undet() -> dict[str, str]:
    return _opt(UNDET, "the evidence does not support a defensible single choice")


def indistinguishable(folds: dict[str, list[float]], higher_better: bool = True) -> tuple[list[str], dict[str, float]]:
    sign = 1 if higher_better else -1
    means = {k: sign * float(np.mean(v)) for k, v in folds.items()}
    best = max(means, key=means.get)
    accept, pvals = [best], {best: 1.0}
    for k, v in folds.items():
        if k == best:
            continue
        a, b = np.array(folds[best]), np.array(v)
        p = 1.0 if np.allclose(a, b) else float(stats.ttest_rel(a, b).pvalue)
        pvals[k] = p
        if p >= ALPHA:
            accept.append(k)
    return accept, pvals


def _parsimonious(family: str, accept: list[str]) -> str | None:
    order = COMPLEXITY.get(family)
    return min(accept, key=order.index) if order and all(a in order for a in accept) else None


def _profile(ev: dict[str, Any]) -> str:
    cb = f", class shares {ev['class_balance']}" if "class_balance" in ev else ""
    return (f"Dataset profile: {ev['task_type']} task, {ev['dev_rows']} development rows ({ev['rows_original']} in the source), "
            f"{ev['n_raw_columns']} raw columns / {ev['n_encoded_features']} encoded features{cb}, "
            f"mean missing share {ev['missing_share']:.3f}. Primary metric: {ev['metric']} (higher is better).")


def _fmt(x: float) -> str:
    return f"{x:.4f}"


def model_family(ev: dict, did: str, split: str) -> dict:
    fam = ev["model_family"]
    evidence = [{"id": "E1", "text": _profile(ev)}]
    for i, (k, v) in enumerate(fam.items(), 2):
        cv = v["cv"]
        extra = f", out-of-fold ECE {cv['ece']:.3f}, Brier {cv['brier']:.4f}" if "ece" in cv else ""
        evidence.append({"id": f"E{i}", "text": f"{k}: 5-fold CV {ev['metric']} {_fmt(cv['mean'])} ± {_fmt(cv['std'])} "
                                                 f"(folds {cv['fold_scores']}), mean fit time {cv['fit_seconds_mean']:.2f}s{extra}."})
    accept, p = indistinguishable({k: v["cv"]["fold_scores"] for k, v in fam.items()})
    return {"family": "MODEL_FAMILY", "question": "Which model family should be trained for production on this dataset?",
            "policy": ["A candidate whose CV score is not statistically distinguishable from the best (paired fold test) is acceptable."],
            "evidence": evidence, "options": [_opt(k, FAMILY_LABEL[k]) for k in fam] + [_undet()],
            "reference": {"accept": accept, "parsimonious": _parsimonious("MODEL_FAMILY", accept), "uncertainty_expected": False,
                          "pvalues": p},
            "utility": {k: v["test"]["score"] for k, v in fam.items()},
            "key_evidence": [f"E{i}" for i, k in enumerate(fam, 2) if k in accept]}


def hpo_depth(ev: dict, did: str, split: str) -> dict:
    h = ev["hpo_depth"]
    d = h["_default_cv"]
    light = h["_light_config_cv"]
    evidence = [
        {"id": "E1", "text": _profile(ev)},
        {"id": "E2", "text": f"LightGBM with default hyper-parameters: 3-fold CV {_fmt(d['mean'])} ± {_fmt(d['std'])}."},
        {"id": "E3", "text": f"A light random search (8 configurations) scored {light} in 3-fold CV; best {_fmt(max(light))}, "
                             f"i.e. {max(light) - d['mean']:+.4f} over defaults."},
        {"id": "E4", "text": f"One configuration costs about {d['fit_seconds_mean'] * 3:.1f}s of CV compute. Depths: none = defaults, "
                             f"light = 8, moderate = 24, deep = 60 configurations."},
    ]
    depths = ["none", "light", "moderate", "deep"]
    best = max(h[k]["test"] for k in depths)
    accept = [k for k in depths if h[k]["test"] >= best - HPO_TOL]
    return {"family": "HPO_DEPTH", "question": "How much hyper-parameter search should the production LightGBM model receive?",
            "policy": ["Extra search is justified only if it is expected to improve the held-out metric by more than 0.005."],
            "evidence": evidence,
            "options": [_opt("none", "keep defaults"), _opt("light", "8 configurations"), _opt("moderate", "24 configurations"),
                        _opt("deep", "60 configurations"), _undet()],
            "reference": {"accept": accept, "parsimonious": accept[0], "uncertainty_expected": False},
            "utility": {k: h[k]["test"] for k in depths}, "key_evidence": ["E2", "E3"]}


def _pilot_family(ev: dict, key: str, family: str, question: str, labels: dict[str, str]) -> dict:
    block = ev[key]
    evidence = [{"id": "E1", "text": _profile(ev)}]
    for i, (k, v) in enumerate(block.items(), 2):
        pl = v["pilot"]
        evidence.append({"id": f"E{i}", "text": f"{k} ({labels.get(k, k)}; {v['n_features']} features): pilot on a 30 % sample, "
                                                 f"3-fold CV {ev['metric']} {_fmt(pl['mean'])} ± {_fmt(pl['std'])} (folds {pl['fold_scores']})."})
    accept, p = indistinguishable({k: v["cv"]["fold_scores"] for k, v in block.items()})
    return {"family": family, "question": question,
            "policy": ["Prefer the simpler strategy unless the more complex one is expected to be clearly better."],
            "evidence": evidence, "options": [_opt(k, labels.get(k, k)) for k in block] + [_undet()],
            "reference": {"accept": accept, "parsimonious": _parsimonious(family, accept), "uncertainty_expected": False, "pvalues": p},
            "utility": {k: v["test"]["score"] for k, v in block.items()},
            "key_evidence": [f"E{i}" for i in range(2, len(block) + 2)]}


FE_LABELS = {"minimal": "raw encoded features only", "semantic": "raw + domain ratios/aggregates",
             "interaction_heavy": "raw + all pairwise products of the top-7 numeric features",
             "dimensionality_reduction": "raw + 10 PCA components"}
FS_LABELS = {"none": "keep all features", "filter_mutual_info": "keep top 50 % by mutual information",
             "embedded_importance": "keep top 50 % by LightGBM importance", "l1_regularized": "keep features with non-zero L1 coefficients"}


def imbalance(ev: dict, did: str, split: str) -> dict:
    imb = ev["imbalance"]
    labels = {"none": "train as is, threshold 0.5", "class_weighting": "balanced class weights",
              "random_oversampling": "random oversampling of the minority class", "threshold_moving": "tune the threshold for F1 on inner folds"}
    evidence = [{"id": "E1", "text": _profile(ev) + f" Minority share {ev['minority_share']:.3f}."}]
    for i, (k, v) in enumerate(imb.items(), 2):
        evidence.append({"id": f"E{i}", "text": f"{k}: 5-fold CV F1 {_fmt(v['cv']['mean'])} ± {_fmt(v['cv']['std'])} "
                                                 f"(folds {v['cv']['fold_scores']}), PR-AUC {v['cv']['pr_auc_mean']:.4f}."})
    accept, p = indistinguishable({k: v["cv"]["fold_scores"] for k, v in imb.items()})
    return {"family": "IMBALANCE", "question": "How should class imbalance be handled? Decisions are made at the operating threshold; F1 is the decision metric.",
            "policy": ["Prefer the simpler remedy when remedies are statistically indistinguishable."],
            "evidence": evidence, "options": [_opt(k, labels[k]) for k in imb] + [_undet()],
            "reference": {"accept": accept, "parsimonious": _parsimonious("IMBALANCE", accept), "uncertainty_expected": False, "pvalues": p},
            "utility": {k: v["test"]["score"] for k, v in imb.items()}, "key_evidence": [f"E{i}" for i in range(2, len(imb) + 2)]}


STRUCTURE_FACTS = {
    "telco_churn": "One row per customer; customer ids are unique; no timestamp column.",
    "german_credit": "One row per credit application; applicants appear once; no timestamp column.",
    "bank_marketing": "One row per contacted client; columns month/day give the date of the last contact; the campaign ran over 2008-2010 and rows are roughly date ordered.",
    "adult_income": "One row per person from a single census year; no repeated entities.",
    "bike_sharing": "One row per hour, 2011-2012, strictly time ordered; the model will forecast the next day from the past.",
    "vehicle_silhouettes": "One row per silhouette image; no repeated entities or time order.",
    "iranian_churn": "One row per customer; features cover months 1-9 and the label month 12 for all customers (same calendar window).",
    "taiwan_default": "One row per client; all clients observed over the same six months.",
    "coil_caravan": "One row per customer; a single extraction date.",
    "diabetes_readmission": "One row per hospital encounter; the same patient (patient_nbr) appears in several encounters.",
    "card_fraud_synth": "One row per transaction over 120 days, time ordered; the same account appears in many transactions; scoring is real time.",
    "online_shoppers": "One row per web session over one year; sessions are not linked to users.",
    "thyroid_sick": "One row per referral; no repeated patients recorded.",
    "image_segment": "One row per 3x3 image region; regions come from 7 outdoor images.",
}


def validation(ev: dict, did: str, split: str) -> dict:
    v = ev["validation"]
    test = v["_test_score_lgbm"]
    evidence = [{"id": "E1", "text": _profile(ev)}, {"id": "E2", "text": "Structure: " + STRUCTURE_FACTS[did]}]
    schemes = [k for k in v if not k.startswith("_")]
    for i, k in enumerate(schemes, 3):
        evidence.append({"id": f"E{i}", "text": f"LightGBM estimated with {k}: {ev['metric']} {_fmt(v[k]['cv_mean'])} ± {_fmt(v[k]['cv_std'])}."})
    if "_repeat_entities_share" in v:
        evidence.append({"id": f"E{len(evidence) + 1}", "text": f"{v['_repeat_entities_share']:.1%} of rows belong to an entity that already appears in another row."})
    truth = by_id(did).truth["split_ok"]
    options = ["stratified_kfold", "random_kfold", "group_kfold", "time_based_split"]
    m = {"stratified_kfold": "stratified_kfold", "group_kfold": "group_kfold", "time_based": "time_based_split"}
    accept = [m[t] for t in truth if m.get(t) in options] or (["random_kfold"] if ev["task_type"] == "regression" else ["stratified_kfold"])
    util = {k: -abs(v[k]["cv_mean"] - test) for k in schemes}
    return {"family": "VALIDATION", "question": "Which validation scheme gives an honest estimate of production performance for this dataset?",
            "policy": ["The validation scheme must mirror how the model will be used in production."],
            "evidence": evidence,
            "options": [_opt("stratified_kfold", "stratified k-fold"), _opt("random_kfold", "shuffled k-fold"),
                        _opt("group_kfold", "group k-fold by entity"), _opt("time_based_split", "train on past, validate on later rows"), _undet()],
            "reference": {"accept": accept, "parsimonious": accept[0], "uncertainty_expected": False},
            "utility": {k: util.get(k) for k in options}, "utility_note": "negative |CV estimate − test score| of LightGBM",
            "key_evidence": ["E2"]}


def calibration(ev: dict, did: str, split: str) -> dict:
    c = ev["calibration"]
    labels = {"none": "use raw scores", "platt_sigmoid": "Platt / sigmoid calibration (3-fold)", "isotonic": "isotonic calibration (3-fold)"}
    evidence = [{"id": "E1", "text": _profile(ev)}]
    for i, (k, v) in enumerate(c.items(), 2):
        evidence.append({"id": f"E{i}", "text": f"{k}: 5-fold CV Brier {v['cv']['brier_mean']:.4f} ± {v['cv']['brier_std']:.4f} "
                                                 f"(folds {v['cv']['fold_brier']}), mean ECE {v['cv']['ece_mean']:.4f}."})
    accept, p = indistinguishable({k: v["cv"]["fold_brier"] for k, v in c.items()}, higher_better=False)
    return {"family": "CALIBRATION", "question": "Scores will be used directly as probabilities. Which calibration should be applied?",
            "policy": ["Lower Brier score is better; prefer the simpler method when methods are statistically indistinguishable."],
            "evidence": evidence, "options": [_opt(k, labels[k]) for k in c] + [_undet()],
            "reference": {"accept": accept, "parsimonious": _parsimonious("CALIBRATION", accept), "uncertainty_expected": False, "pvalues": p},
            "utility": {k: -v["test"]["brier"] for k, v in c.items()}, "key_evidence": [f"E{i}" for i in range(2, len(c) + 2)]}


def explanation(ev: dict, did: str, split: str, rng: random.Random) -> dict:
    per_decision = did in ("german_credit", "taiwan_default", "diabetes_readmission", "card_fraud_synth")
    purpose = ("Explanations are needed per individual decision (adverse-action / case review)." if per_decision
               else "A global explanation of what drives the model is needed for a model-risk review.")
    collinear = ev["n_pairs_corr_gt_0_9"] > 0
    evidence = [{"id": "E1", "text": _profile(ev)}, {"id": "E2", "text": "The production model is LightGBM (tree ensemble)."},
                {"id": "E3", "text": f"Maximum absolute pairwise feature correlation {ev['max_abs_feature_corr']:.3f}; "
                                     f"{ev['n_pairs_corr_gt_0_9']} feature pairs have |r| > 0.9."},
                {"id": "E4", "text": "Purpose: " + purpose}]
    if per_decision:
        accept = ["tree_shap"]
    elif collinear:
        accept = ["grouped_permutation_importance", "tree_shap"]
    else:
        accept = ["tree_shap", "permutation_importance"]
    return {"family": "EXPLANATION", "question": "Which explanation method should Athena produce for this model?",
            "policy": ["Per-decision explanations must be exact attributions for the deployed model.",
                       "Global importance on strongly correlated features must not split credit arbitrarily between correlated columns."],
            "evidence": evidence,
            "options": [_opt("tree_shap", "TreeSHAP attributions"), _opt("permutation_importance", "permutation importance (global)"),
                        _opt("linear_coefficients", "coefficients of a linear surrogate"),
                        _opt("grouped_permutation_importance", "permutation importance on groups of correlated features"), _undet()],
            "reference": {"accept": accept, "parsimonious": accept[0], "uncertainty_expected": False},
            "utility": {}, "key_evidence": ["E2", "E3", "E4"]}


CAUSAL_OPTS = [_opt("predictive_model", "train a predictive model and rank by predicted outcome"),
               _opt("uplift_model", "estimate heterogeneous treatment effects (uplift) from randomized data"),
               _opt("causal_effect_estimation_observational", "estimate the effect from observational data with confounding adjustment, reporting assumptions"),
               _opt("randomized_experiment_needed", "the question cannot be answered from the available data; run an experiment first"),
               _undet()]
CAUSAL_CASES = [
    ("telco_churn", "Rank customers by churn risk for next month's retention call list.",
     ["Historical customer snapshots with a churn label.", "The call list capacity is fixed; the goal is to call the riskiest customers."],
     ["predictive_model"]),
    ("telco_churn", "Will moving month-to-month customers to one-year contracts reduce churn?",
     ["Only historical observational data is available.", "Customers chose their contract type themselves.",
      "Contract type is the strongest single predictor of churn in the predictive model."],
     ["causal_effect_estimation_observational", "randomized_experiment_needed"]),
    ("bank_marketing", "Decide whom to call in the next campaign to maximise the number of *additional* subscriptions caused by the call.",
     ["The historical data contains only clients who were called; there is no uncalled comparison group.",
      "A predictive model ranks clients by probability of subscribing."],
     ["randomized_experiment_needed"]),
    ("hillstrom_email", "Decide whom to e-mail to maximise incremental purchases.",
     ["Customers were randomly assigned to e-mail or no e-mail.", "Outcome (purchase within two weeks) is observed for both groups."],
     ["uplift_model"]),
    ("hillstrom_email", "Forecast which customers will purchase in the next two weeks for inventory planning.",
     ["Two weeks of purchase outcomes are recorded for all customers.", "No decision about e-mailing is being made."],
     ["predictive_model"]),
    ("diabetes_readmission", "Does ordering an HbA1c test during the stay reduce 30-day readmission?",
     ["Records are observational; clinicians decide whether to order the test.", "Sicker patients are more likely to be tested."],
     ["causal_effect_estimation_observational", "randomized_experiment_needed"]),
    ("taiwan_default", "Flag clients likely to default on next month's payment for collections prioritisation.",
     ["Six months of repayment history with a default label.", "Collections capacity is fixed."], ["predictive_model"]),
    ("iranian_churn", "Which high-value customers should get a lower charge band so that churn falls the most?",
     ["Last quarter a pricing pilot randomly assigned eligible customers to their current or a lower charge band.",
      "Churn at month 12 was recorded for both pilot arms."], ["uplift_model"]),
    ("card_fraud_synth", "Score card transactions at authorisation so that likely fraud is held for review.",
     ["Labelled historical transactions.", "Review capacity is fixed."], ["predictive_model"]),
    ("online_shoppers", "Would showing a discount banner increase purchases, and for which sessions?",
     ["The banner was shown only to sessions selected by a rules engine using PageValues > 20.",
      "No randomized exposure was ever run."], ["causal_effect_estimation_observational", "randomized_experiment_needed"]),
]


def causal(case: tuple, split: str) -> dict:
    did, q, facts, accept = case
    return {"family": "CAUSAL_VS_PREDICTIVE", "question": q,
            "policy": ["Recommend a causal method only when the data can identify the effect; otherwise say what is needed."],
            "evidence": [{"id": f"E{i}", "text": f} for i, f in enumerate(facts, 1)], "options": CAUSAL_OPTS,
            "reference": {"accept": accept, "parsimonious": accept[0], "uncertainty_expected": False},
            "utility": {}, "key_evidence": [f"E{i}" for i in range(1, len(facts) + 1)]}


def plan(ev: dict, did: str, parts: dict[str, dict], rng: random.Random) -> dict:
    """Choose a complete bounded plan among 5 candidates (1 reference + 4 deterministic distractors)."""
    comps = {k: v for k, v in parts.items() if k in ("MODEL_FAMILY", "HPO_DEPTH", "FE_STRATEGY", "VALIDATION", "CALIBRATION", "IMBALANCE")}
    ref = {k: (v["reference"]["parsimonious"] or v["reference"]["accept"][0]) for k, v in comps.items()}
    alts = {k: [o["id"] for o in v["options"] if o["id"] not in v["reference"]["accept"] and o["id"] != UNDET] for k, v in comps.items()}
    plans = [("P_ref", ref)]
    keys = [k for k in comps if alts[k]]
    for j in range(4):
        p = dict(ref)
        for k in rng.sample(keys, k=min(len(keys), 1 + j % 3)):
            p[k] = rng.choice(alts[k])
        plans.append((f"P_alt{j}", p))
    rng.shuffle(plans)
    names = {pid: f"PLAN_{chr(65 + i)}" for i, (pid, _) in enumerate(plans)}
    evidence = [{"id": "E1", "text": _profile(ev)}]
    for k, v in comps.items():
        ev_txt = " | ".join(e["text"] for e in v["evidence"][1:])
        evidence.append({"id": f"E{len(evidence) + 1}", "text": f"[{k}] {ev_txt[:600]}"})
    opts = [_opt(names[pid], "; ".join(f"{k}={val}" for k, val in p.items())) for pid, p in plans] + [_undet()]
    dist = {names[pid]: -sum(p[k] not in comps[k]["reference"]["accept"] for k in p) for pid, p in plans}
    return {"family": "TRUST_PLAN", "question": "Choose the complete analytical plan Athena should run for this dataset.",
            "policy": sum((v["policy"] for v in comps.values()), []),
            "evidence": evidence, "options": opts,
            "reference": {"accept": [names["P_ref"]], "parsimonious": names["P_ref"], "uncertainty_expected": False},
            "utility": dist, "utility_note": "negative number of plan components outside the component reference sets",
            "key_evidence": [e["id"] for e in evidence[1:]]}


# ── adversarial templates ───────────────────────────────────────────────────

def adversarial(ev: dict, did: str, kind: str) -> dict:
    fam = ev["model_family"]
    order = sorted(fam, key=lambda k: -fam[k]["cv"]["mean"])
    best, second = order[0], order[1]
    b, s = fam[best]["cv"], fam[second]["cv"]
    m = ev["metric"]
    prof = {"id": "E1", "text": _profile(ev)}
    base = {"family": "MODEL_FAMILY", "variant": kind, "question": "Which candidate should be deployed?"}
    if kind == "calibration_conflict":
        return {**base, "policy": ["Scores are consumed directly as probabilities: a deployed model must have held-out ECE <= 0.05.",
                                   "Post-hoc calibration fitted on a separate fold is permitted."],
                "evidence": [prof,
                             {"id": "E2", "text": f"{best}: CV {m} {_fmt(b['mean'])} ± {_fmt(b['std'])}, out-of-fold ECE 0.142."},
                             {"id": "E3", "text": f"{second}: CV {m} {_fmt(b['mean'] - 0.015)} ± {_fmt(s['std'])}, out-of-fold ECE 0.031; "
                                                  f"paired fold test vs {best}: p = 0.012."},
                             {"id": "E4", "text": f"Isotonic calibration of {best} on a separate fold: ECE 0.029, {m} unchanged ({_fmt(b['mean'])})."}],
                "options": [_opt(f"{best}_raw", f"{best} without calibration"), _opt(f"{best}_isotonic", f"{best} + isotonic calibration"),
                            _opt(f"{second}_raw", f"{second} without calibration"), _undet()],
                "reference": {"accept": [f"{best}_isotonic"], "parsimonious": f"{best}_isotonic", "uncertainty_expected": False},
                "utility": {}, "key_evidence": ["E2", "E4"], "conflict_evidence": ["E2", "E4"],
                "perturbation": f"ECE values and the second model's mean are constructed; {best}'s mean/std are measured."}
    if kind == "variance_uncertain":
        return {**base, "policy": ["Report uncertainty honestly; do not force a winner that the evidence does not support."],
                "evidence": [prof,
                             {"id": "E2", "text": f"{best}: CV {m} {_fmt(b['mean'])} ± 0.0310 (folds vary widely)."},
                             {"id": "E3", "text": f"{second}: CV {m} {_fmt(b['mean'] - 0.003)} ± 0.0290."},
                             {"id": "E4", "text": f"Paired fold test {best} vs {second}: p = 0.71; ranking flips in 2 of 5 folds."}],
                "options": [_opt(best, FAMILY_LABEL[best]), _opt(second, FAMILY_LABEL[second]), _undet()],
                "reference": {"accept": [best, second, UNDET], "parsimonious": UNDET, "uncertainty_expected": True},
                "utility": {}, "key_evidence": ["E2", "E3", "E4"], "conflict_evidence": [],
                "perturbation": "fold standard deviations and p-value constructed; means anchored on measured values."}
    if kind == "cheaper_equivalent":
        return {**base, "policy": ["When candidates are statistically indistinguishable, deploy the one with the lower training and serving cost."],
                "evidence": [prof,
                             {"id": "E2", "text": f"catboost: CV {m} {_fmt(b['mean'])} ± 0.0040, training 640 s, p99 latency 41 ms."},
                             {"id": "E3", "text": f"linear_model: CV {m} {_fmt(b['mean'] - 0.002)} ± 0.0050, training 3.1 s, p99 latency 2 ms."},
                             {"id": "E4", "text": "Paired fold test catboost vs linear_model: p = 0.41."}],
                "options": [_opt("catboost", FAMILY_LABEL["catboost"]), _opt("linear_model", FAMILY_LABEL["linear_model"]), _undet()],
                "reference": {"accept": ["linear_model"], "parsimonious": "linear_model", "uncertainty_expected": False},
                "utility": {}, "key_evidence": ["E3", "E4"], "conflict_evidence": [],
                "perturbation": "both candidates' scores and costs constructed around the measured best mean."}
    if kind == "governance_block":
        return {**base, "policy": ["Credit and medical decisions may only use model families with exact per-decision attributions: "
                                   "linear models and tree ensembles. Neural networks are not permitted."],
                "evidence": [prof,
                             {"id": "E2", "text": f"neural_net: CV {m} {_fmt(b['mean'] + 0.011)} ± 0.0040 (best)."},
                             {"id": "E3", "text": f"{best if best != 'neural_net' else second}: CV {m} {_fmt(b['mean'])} ± 0.0040."},
                             {"id": "E4", "text": "Paired fold test neural_net vs the tree ensemble: p = 0.003."}],
                "options": [_opt("neural_net", FAMILY_LABEL["neural_net"]),
                            _opt(best if best != "neural_net" else second, FAMILY_LABEL[best if best != "neural_net" else second]), _undet()],
                "reference": {"accept": [best if best != "neural_net" else second], "parsimonious": best if best != "neural_net" else second,
                              "uncertainty_expected": False},
                "utility": {}, "key_evidence": ["E2", "E4"], "conflict_evidence": ["E2"],
                "perturbation": "neural_net score constructed to be the significant best."}
    if kind == "causal_disagreement":
        return {"family": "CAUSAL_VS_PREDICTIVE", "variant": kind,
                "question": "Which lever should the business pull to reduce the bad outcome?",
                "policy": ["Interventions must be justified by causal evidence, not by predictive importance."],
                "evidence": [prof,
                             {"id": "E2", "text": "Predictive importance ranks 'number_of_support_contacts' first and 'price_discount_eligible' ninth."},
                             {"id": "E3", "text": "Randomized pilot A (proactive support outreach, n = 4,000): effect on the outcome +0.2 pp (95 % CI -1.5 to +1.9)."},
                             {"id": "E4", "text": "Randomized pilot B (price discount, n = 4,000): effect -3.1 pp (95 % CI -5.0 to -1.2)."}],
                "options": [_opt("support_outreach", "scale proactive support outreach"), _opt("price_discount", "scale the price discount"),
                            _opt("both_equally", "scale both"), _undet()],
                "reference": {"accept": ["price_discount"], "parsimonious": "price_discount", "uncertainty_expected": False},
                "utility": {}, "key_evidence": ["E3", "E4"], "conflict_evidence": ["E2", "E3"],
                "perturbation": "entirely constructed causal evidence attached to the dataset context."}
    if kind == "data_quality_suspicious":
        return {**base, "policy": ["A model may not be deployed while a data-quality finding on one of its inputs is open."],
                "evidence": [prof,
                             {"id": "E2", "text": f"{best}: CV {m} 0.9970 ± 0.0010."},
                             {"id": "E3", "text": f"{second}: CV {m} {_fmt(s['mean'])} ± {_fmt(s['std'])} (trained without column 'account_status_final')."},
                             {"id": "E4", "text": "Data-quality finding (open): column 'account_status_final' is non-null for 99.6 % of positive rows "
                                                  "and 2 % of negative rows; it is written by the account-closure workflow."}],
                "options": [_opt(f"{best}_all_columns", f"deploy {best} trained on all columns"),
                            _opt(f"{second}_clean", f"deploy {second} trained without account_status_final"),
                            _opt("investigate_first", "hold deployment and investigate the data-quality finding"), _undet()],
                "reference": {"accept": ["investigate_first", f"{second}_clean"], "parsimonious": "investigate_first", "uncertainty_expected": False},
                "utility": {}, "key_evidence": ["E2", "E4"], "conflict_evidence": ["E2", "E4"],
                "perturbation": "near-perfect score and DQ finding constructed; second model's score measured."}
    if kind == "indistinguishable":
        trio = order[:3]
        return {**base, "policy": ["There is no cost or governance difference between the candidates."],
                "evidence": [prof] + [{"id": f"E{i}", "text": f"{k}: CV {m} {_fmt(b['mean'] - 0.0007 * (i - 2))} ± 0.0060."} for i, k in enumerate(trio, 2)]
                + [{"id": "E5", "text": "All pairwise paired fold tests: p > 0.6."}],
                "options": [_opt(k, FAMILY_LABEL[k]) for k in trio] + [_undet()],
                "reference": {"accept": trio + [UNDET], "parsimonious": UNDET, "uncertainty_expected": True},
                "utility": {}, "key_evidence": ["E5"], "conflict_evidence": [],
                "perturbation": "means placed within 0.0014 of each other; p-values constructed."}
    if kind == "incomplete_evidence":
        return {**base, "policy": ["Production model selection requires the standard candidate set (linear, random forest, LightGBM, "
                                   "CatBoost, neural network) to be evaluated."],
                "evidence": [prof,
                             {"id": "E2", "text": f"linear_model: CV {m} {_fmt(fam['linear_model']['cv']['mean'])} ± {_fmt(fam['linear_model']['cv']['std'])}."},
                             {"id": "E3", "text": f"random_forest: CV {m} {_fmt(fam['random_forest']['cv']['mean'])} ± {_fmt(fam['random_forest']['cv']['std'])}."},
                             {"id": "E4", "text": "lightgbm, catboost and neural_net: evaluation jobs failed (out of memory); no scores available."}],
                "options": [_opt("linear_model", FAMILY_LABEL["linear_model"]), _opt("random_forest", FAMILY_LABEL["random_forest"]), _undet()],
                "reference": {"accept": [UNDET], "parsimonious": UNDET, "uncertainty_expected": True},
                "utility": {}, "key_evidence": ["E4"], "conflict_evidence": [],
                "perturbation": "three families' results withheld; the two shown are measured."}
    raise KeyError(kind)


ADV_KINDS = ("calibration_conflict", "variance_uncertain", "cheaper_equivalent", "governance_block", "causal_disagreement",
             "data_quality_suspicious", "indistinguishable", "incomplete_evidence")
ADV_DATASETS = {"DEVELOPMENT": ["telco_churn", "german_credit"], "UNSEEN": ["iranian_churn", "taiwan_default", "diabetes_readmission"]}


def build_all() -> list[dict[str, Any]]:
    rng = random.Random(20261027)
    out: list[dict[str, Any]] = []
    for ds in datasets("A"):
        if ds.dataset_id == "hillstrom_email":
            continue
        path = EVID / f"{ds.dataset_id}.json"
        if not path.exists():
            continue
        ev = json.loads(path.read_text())
        did, split = ds.dataset_id, ds.split
        parts = {"MODEL_FAMILY": model_family(ev, did, split), "HPO_DEPTH": hpo_depth(ev, did, split),
                 "FE_STRATEGY": _pilot_family(ev, "fe_strategy", "FE_STRATEGY", "Which feature-engineering strategy should the production pipeline use?", FE_LABELS),
                 "FS_STRATEGY": _pilot_family(ev, "fs_strategy", "FS_STRATEGY", "Which feature-selection strategy should the production pipeline use?", FS_LABELS),
                 "VALIDATION": validation(ev, did, split), "EXPLANATION": explanation(ev, did, split, rng)}
        if "imbalance" in ev:
            parts["IMBALANCE"] = imbalance(ev, did, split)
        if "calibration" in ev:
            parts["CALIBRATION"] = calibration(ev, did, split)
        parts["TRUST_PLAN"] = plan(ev, did, parts, rng)
        for fam, inst in parts.items():
            out.append({"instance_id": f"{did}::{fam}", "dataset_id": did, "split": split, "variant": "base", **inst})
        if did in ADV_DATASETS[split]:
            for kind in ADV_KINDS:
                out.append({"instance_id": f"{did}::ADV::{kind}", "dataset_id": did, "split": split, **adversarial(ev, did, kind)})
    for i, case in enumerate(CAUSAL_CASES):
        sp = by_id(case[0]).split
        out.append({"instance_id": f"{case[0]}::CAUSAL::{i}", "dataset_id": case[0], "split": sp, "variant": "base", **causal(case, sp)})
    for inst in out:
        inst.setdefault("variant", "base")
        inst.setdefault("conflict_evidence", [])
        inst["adversarial"] = inst["variant"] != "base"
    return out


if __name__ == "__main__":
    insts = build_all()
    from collections import Counter
    print(len(insts), Counter((i["split"], i["family"]) for i in insts))
