"""Study B scoring: semantic decisions against the evaluation authority (never shown to the model)."""
from __future__ import annotations

import re
from typing import Any

# acceptable answers beyond the single truth value (pre-registered; see semantic-condition-contracts.md)
PROBLEM_OK = {"telco_churn": {"churn"}, "german_credit": {"credit_default"}, "bank_marketing": {"cross_sell", "purchase_intent"},
              "adult_income": {"income_classification"}, "bike_sharing": {"demand_forecast"}, "iranian_churn": {"churn"},
              "taiwan_default": {"credit_default"}, "coil_caravan": {"cross_sell", "purchase_intent"},
              "diabetes_readmission": {"readmission"}, "card_fraud_synth": {"fraud"}, "online_shoppers": {"purchase_intent"},
              "thyroid_sick": {"medical_diagnosis"}, "hillstrom_email": {"uplift"}}
UNIT_OK = {"telco_churn": {"customer", "account"}, "german_credit": {"applicant", "customer", "person"},
           "bank_marketing": {"customer", "person"}, "adult_income": {"person"}, "bike_sharing": {"time_period"},
           "iranian_churn": {"customer", "account"}, "taiwan_default": {"customer", "account", "person"},
           "coil_caravan": {"customer", "household"}, "diabetes_readmission": {"encounter"}, "card_fraud_synth": {"transaction"},
           "online_shoppers": {"session"}, "thyroid_sick": {"patient", "person"}, "hillstrom_email": {"customer"}}
TEMPORAL_OK = {"telco_churn": {"none"}, "german_credit": {"none"}, "bank_marketing": {"time_ordered_rows", "none"},
               "adult_income": {"none"}, "bike_sharing": {"time_ordered_rows"}, "iranian_churn": {"observation_window_then_outcome"},
               "taiwan_default": {"observation_window_then_outcome"}, "coil_caravan": {"none"},
               "diabetes_readmission": {"repeated_entities"}, "card_fraud_synth": {"time_ordered_rows", "repeated_entities"},
               "online_shoppers": {"none", "time_ordered_rows"}, "thyroid_sick": {"none"},
               "hillstrom_email": {"observation_window_then_outcome", "none"}}
TARGET_KW = {"telco_churn": ["churn", "leave", "left", "cancel"], "german_credit": ["bad", "default", "risk"],
             "bank_marketing": ["subscri", "deposit"], "adult_income": ["income", "50k", "50,000", "50 000"],
             "bike_sharing": ["rental", "count", "bike", "demand"], "iranian_churn": ["churn", "leave", "left", "cancel"],
             "taiwan_default": ["default"], "coil_caravan": ["caravan", "mobile home"], "diabetes_readmission": ["readmi"],
             "card_fraud_synth": ["fraud"], "online_shoppers": ["purchase", "revenue", "buy", "transaction"],
             "thyroid_sick": ["sick", "euthyroid", "thyroid"], "hillstrom_email": ["purchase", "conver", "buy"]}
SPLIT_MAP = {"time_based": "time_based", "group_kfold": "group_kfold", "stratified_kfold": "stratified_kfold"}


def _cols(names: Any, rename: dict[str, str], valid: set[str]) -> set[str]:
    out = set()
    for n in names or []:
        n = str(n).strip()
        n = rename.get(n, n)
        if n in valid:
            out.add(n)
    return out


def prf(pred: set[str], truth: set[str]) -> dict[str, float | None]:
    tp = len(pred & truth)
    p = tp / len(pred) if pred else None
    r = tp / len(truth) if truth else None
    f = (2 * p * r / (p + r) if p and r else 0.0) if p is not None and r is not None else None
    return {"precision": p, "recall": r, "f1": f}


def judgements(fe: dict) -> dict[str, str]:
    """candidate id -> decision; accepts the keyed contract and the superseded list shape."""
    cj = fe.get("candidate_judgements") or {}
    if isinstance(cj, dict):
        return {k: v.get("decision") for k, v in cj.items() if isinstance(v, dict)}
    return {j.get("id"): j.get("decision") for j in cj if isinstance(j, dict)}


def score(row: dict[str, Any], truth: dict[str, Any], columns: list[str], strongest_non_actionable: str | None) -> dict[str, Any]:
    did = row["dataset_id"]
    an = row["trace"].get("analysis") or {}
    fe = row["trace"].get("fe") or {}
    rename = row.get("rename") or {}
    valid = set(columns)
    ok = bool(an)
    ids_t = set(truth["ids_all"])
    post_t = set(truth["post_outcome_all"])
    leak_t = set(truth["leak_all"])
    ids_p = _cols(an.get("id_columns"), rename, valid)
    post_p = _cols(an.get("post_outcome_columns"), rename, valid)
    art_p = _cols(an.get("artifact_or_leakage_columns"), rename, valid)
    excl_p = _cols(an.get("excluded_columns"), rename, valid)
    flagged_leak = post_p | art_p
    blocked = ids_p | post_p | art_p | excl_p
    act_p = _cols(an.get("actionable_columns"), rename, valid)
    act_t = set(truth.get("actionable", []))
    prot_t = set(truth.get("protected", []))
    lever = rename.get(str(an.get("intervention_column", "")).strip(), str(an.get("intervention_column", "")).strip())
    tm = str(an.get("target_meaning", "")).lower()
    s: dict[str, Any] = {
        "analysis_ok": ok,
        "task_understanding": an.get("business_problem") in PROBLEM_OK[did] if ok else False,
        "target_semantic": any(k in tm for k in TARGET_KW[did]) if ok else False,
        "grain": an.get("prediction_unit") in UNIT_OK[did] if ok else False,
        "temporal": an.get("temporal_structure") in TEMPORAL_OK[did] if ok else False,
        "id_recall": prf(ids_p, ids_t)["recall"], "id_precision": prf(ids_p, ids_t)["precision"],
        "id_trap_caught": "record_key" in blocked,
        "post_event_recall": prf(post_p | art_p | excl_p, post_t)["recall"],
        "post_event_flagged_as_post": prf(post_p, post_t)["recall"],
        "leak_recall": len((flagged_leak | excl_p) & leak_t) / len(leak_t) if leak_t else None,
        "leak_precision": (len(flagged_leak & (leak_t | ids_t)) / len(flagged_leak)) if flagged_leak else None,
        "artifact_caught": "load_weekday" in blocked,
        "all_traps_blocked": ids_t <= blocked and leak_t <= blocked,
        "over_exclusion": len(excl_p - ids_t - leak_t - set(truth.get("protected", [])) - set(truth.get("ambiguous", [])) - set(truth.get("redundant", []))),
        "actionability_precision": prf(act_p, act_t)["precision"] if act_t else None,
        "protected_called_actionable": len(act_p & prot_t),
        "lever_actionable": (lever in act_t) if act_t else None,
        "lever_is_predictive_trap": bool(strongest_non_actionable and lever == strongest_non_actionable),
        "intent": (an.get("analysis_intent") in ({"causal", "both"} if truth.get("intent") == "causal" else {"predictive", "both"})) if ok else False,
        "metric": an.get("primary_metric") in set(truth.get("metrics_ok", [])) if ok else False,
        "split_correct": SPLIT_MAP.get(an.get("split_strategy")) in set(truth.get("split_ok", [])) if ok else False,
        "model_family": an.get("model_family"), "hpo_depth": an.get("hpo_depth"), "calibration_needed": an.get("calibration_needed"),
        "split_strategy": an.get("split_strategy"), "primary_metric": an.get("primary_metric"), "business_problem": an.get("business_problem"),
        "semantic_confidence": an.get("semantic_confidence"),
        "n_excluded": len(excl_p),
    }
    if truth.get("intent") == "causal":
        s["model_family_ok"] = an.get("model_family") == "uplift_meta_learner"
    # T3: did it notice the missing definitions?
    removed = set(row.get("removed_definitions") or [])
    if removed:
        miss = _cols(an.get("missing_semantics"), rename, valid)
        s["missing_semantics_recall"] = len(miss & removed) / len(removed)
    # T4: did it detect falsified documentation?
    falsified = set(row.get("falsified") or {})
    if falsified:
        contra = _cols([c.get("column") for c in an.get("dictionary_contradictions", []) if isinstance(c, dict)], rename, valid)
        ver = (row["trace"].get("verification") or {}).get("checks", [])
        vcon = _cols([c.get("column") for c in ver if c.get("verdict") == "contradicted"], rename, valid)
        s["falsified_detected_recall"] = len((contra | vcon) & falsified) / len(falsified)
        s["false_contradictions"] = len((contra | vcon) - falsified)
    # candidate judgement
    cands = {c["id"]: c for c in row["candidates"]}
    judg = judgements(fe)
    correct = [judg.get(cid) == ("accept" if c["truth_accept"] else "reject") for cid, c in cands.items()]
    s["candidate_accuracy"] = sum(correct) / len(correct)
    s["candidate_missing_judgements"] = sum(cid not in judg for cid in cands)
    for kind in ("semantic", "identifier", "post_outcome", "artifact", "target_leak"):
        ids = [cid for cid, c in cands.items() if c["kind"] == kind]
        if ids:
            s[f"cand_{kind}_correct"] = sum(judg.get(cid) == ("accept" if kind == "semantic" else "reject") for cid in ids) / len(ids)
    s["n_proposed_features"] = len(fe.get("proposed_features", []) or [])
    calls = row["trace"]["calls"]
    s["n_calls"] = len(calls)
    s["n_failed_calls"] = len(row["trace"]["failures"])
    pt = [c["prompt_tokens"] for c in calls]
    ot = [c["output_tokens"] for c in calls]
    s["prompt_tokens"] = sum(pt) if all(x is not None for x in pt) else None
    s["output_tokens"] = sum(ot) if all(x is not None for x in ot) else None
    s["latency_s"] = round(sum(c["compute_s"] for c in calls), 2) if all(c.get("compute_s") is not None for c in calls) else None
    s["wall_latency_s"] = round(sum(c["latency_s"] for c in calls), 2)
    s["_blocked"] = sorted(blocked)
    s["_lever"] = lever
    return s


TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
