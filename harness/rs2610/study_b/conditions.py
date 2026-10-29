"""Study B semantic conditions, prompts and schemas.

A  RAW_SCHEMA          profile only                                   → analysis, FE                (2 calls)
B  SELF_INFERENCE      profile; an explicit column-role inference stage → inference, analysis, FE  (3 calls)
C  DICTIONARY          profile + description + data dictionary        → analysis, FE                (2 calls)
D  DICT_RULES          C + business rules + code dictionary + constraints → analysis, FE           (2 calls)
E  FULL_VERIFIED       D + a verification stage that checks every documented claim against the
                       profile before it may be used                  → verify, analysis, FE        (3 calls)

The profile, task wording, schemas, model, temperature and seeds are identical;
only the semantic context and the presence of an inference/verification stage
differ.  Column names in outputs are mapped back to original names for scoring.
"""
from __future__ import annotations

import json
from typing import Any

from rs2610.common.llm import LLM
from rs2610.study_b.profile import render_profile, target_summary
from rs2610.study_b.variants import Variant

CONDITIONS = ("A_RAW", "B_SELF", "C_DICT", "D_RULES", "E_FULL")

SYSTEM = ("You are the semantic-understanding layer of an AutoML platform. Before any model is trained you must understand what a "
          "dataset represents: the business problem, what the target means, what one row is, which columns are identifiers, which "
          "are only known after the outcome, which are artifacts, which a business can act on, and how the model must be validated. "
          "Use only what you are shown. Column names may be uninformative; documentation may be incomplete or wrong. "
          "Answer in JSON only.")

ENUMS = {
    "business_problem": ["churn", "fraud", "credit_default", "cross_sell", "readmission", "medical_diagnosis", "income_classification",
                         "demand_forecast", "purchase_intent", "uplift", "other"],
    "prediction_unit": ["customer", "applicant", "person", "transaction", "account", "encounter", "patient", "session", "time_period",
                        "household", "other"],
    "temporal_structure": ["none", "time_ordered_rows", "observation_window_then_outcome", "repeated_entities", "unknown"],
    "analysis_intent": ["predictive", "causal", "both"],
    "primary_metric": ["roc_auc", "pr_auc", "f1", "recall", "precision", "log_loss", "brier", "accuracy", "expected_cost", "lift",
                       "top_k_precision", "rmse", "mae", "mape", "r2", "rmsle", "qini", "uplift_auc", "ks"],
    "split_strategy": ["stratified_kfold", "random_kfold", "group_kfold", "time_based"],
    "model_family": ["gradient_boosting", "random_forest", "linear", "neural_net", "uplift_meta_learner"],
    "hpo_depth": ["none", "light", "moderate", "deep"],
}
LIST = {"type": "array", "items": {"type": "string"}}

ANALYSIS_SCHEMA = {"type": "object", "properties": {
    "business_problem": {"type": "string", "enum": ENUMS["business_problem"]},
    "target_meaning": {"type": "string"},
    "prediction_unit": {"type": "string", "enum": ENUMS["prediction_unit"]},
    "temporal_structure": {"type": "string", "enum": ENUMS["temporal_structure"]},
    "time_columns": LIST, "id_columns": LIST, "post_outcome_columns": LIST, "artifact_or_leakage_columns": LIST,
    "actionable_columns": LIST, "intervention_column": {"type": "string"},
    "analysis_intent": {"type": "string", "enum": ENUMS["analysis_intent"]},
    "primary_metric": {"type": "string", "enum": ENUMS["primary_metric"]},
    "split_strategy": {"type": "string", "enum": ENUMS["split_strategy"]},
    "group_column": {"type": "string"},
    "model_family": {"type": "string", "enum": ENUMS["model_family"]},
    "hpo_depth": {"type": "string", "enum": ENUMS["hpo_depth"]},
    "calibration_needed": {"type": "boolean"},
    "excluded_columns": LIST, "missing_semantics": LIST,
    "dictionary_contradictions": {"type": "array", "items": {"type": "object", "properties": {
        "column": {"type": "string"}, "issue": {"type": "string"}}, "required": ["column", "issue"]}},
    "semantic_confidence": {"type": "number"}},
    "required": ["business_problem", "target_meaning", "prediction_unit", "temporal_structure", "time_columns", "id_columns",
                 "post_outcome_columns", "artifact_or_leakage_columns", "actionable_columns", "intervention_column", "analysis_intent",
                 "primary_metric", "split_strategy", "group_column", "model_family", "hpo_depth", "calibration_needed",
                 "excluded_columns", "missing_semantics", "dictionary_contradictions", "semantic_confidence"]}

ANALYSIS_TASK = (
    "TASK: produce the semantic analysis.\n"
    "- business_problem / target_meaning (one sentence: what a positive or high target means) / prediction_unit (what one row is).\n"
    "- temporal_structure and time_columns.\n"
    "- id_columns: identifiers or keys (never predictive in deployment, whatever their association).\n"
    "- post_outcome_columns: columns whose value is only known after the target outcome happened, or derived from the target.\n"
    "- artifact_or_leakage_columns: other columns whose association with the target is an artifact of data collection or that would leak.\n"
    "- actionable_columns: columns the business can change through an intervention; intervention_column: the single best lever "
    "(a column name, or 'none'). Strong predictors are not automatically levers.\n"
    "- analysis_intent, primary_metric, split_strategy (+ group_column or 'none'), model_family, hpo_depth, calibration_needed.\n"
    "- excluded_columns: every column that must not be a model input.\n"
    "- missing_semantics: columns whose meaning you cannot determine from what you were given.\n"
    "- dictionary_contradictions: documented claims contradicted by the profile (empty if no documentation or none found).\n"
    "- semantic_confidence: probability (0-1) that your reading of the dataset is right.")

FE_SCHEMA = {"type": "object", "properties": {
    "proposed_features": {"type": "array", "maxItems": 6, "items": {"type": "object", "properties": {
        "name": {"type": "string"}, "op": {"type": "string", "enum": ["ratio", "diff", "product", "sum", "mean", "log1p", "is_zero"]},
        "inputs": LIST, "semantic_rationale": {"type": "string"}, "statistical_rationale": {"type": "string"},
        "leakage_assessment": {"type": "string", "enum": ["none", "possible", "likely"]}, "business_interpretation": {"type": "string"}},
        "required": ["name", "op", "inputs", "semantic_rationale", "statistical_rationale", "leakage_assessment", "business_interpretation"]}},
    "candidate_judgements": {"type": "array", "items": {"type": "object", "properties": {
        "id": {"type": "string"}, "decision": {"type": "string", "enum": ["accept", "reject"]}, "reason": {"type": "string"}},
        "required": ["id", "decision", "reason"]}}},
    "required": ["proposed_features", "candidate_judgements"]}  # superseded_v2 shape (free-string ids); kept for the record


def fe_schema(cands: list[dict]) -> dict:
    """FE contract for one run: one required judgement per offered candidate, keyed by its exact id.

    The earlier free-string `id` let the model rename candidates (cand_target_mean_A1) or skip them, so a judgement could
    not be matched to its candidate: a contract defect, not model behaviour (JOURNAL ~22:52)."""
    judgement = {"type": "object", "properties": {"decision": {"type": "string", "enum": ["accept", "reject"]},
                                                  "reason": {"type": "string"}}, "required": ["decision", "reason"]}
    ids = [c["id"] for c in cands]
    return {"type": "object", "properties": {
        "proposed_features": FE_SCHEMA["properties"]["proposed_features"],
        "candidate_judgements": {"type": "object", "properties": {cid: judgement for cid in ids}, "required": ids}},
        "required": ["proposed_features", "candidate_judgements"]}

INFER_SCHEMA = {"type": "object", "properties": {
    "dataset_meaning": {"type": "string"}, "target_meaning": {"type": "string"}, "row_meaning": {"type": "string"},
    "column_roles": {"type": "array", "items": {"type": "object", "properties": {
        "column": {"type": "string"},
        "role": {"type": "string", "enum": ["identifier", "pre_outcome_feature", "post_outcome", "target_derived", "artifact", "time",
                                             "group_key", "treatment", "unknown"]},
        "meaning_guess": {"type": "string"}}, "required": ["column", "role", "meaning_guess"]}}},
    "required": ["dataset_meaning", "target_meaning", "row_meaning", "column_roles"]}

VERIFY_SCHEMA = {"type": "object", "properties": {
    "checks": {"type": "array", "items": {"type": "object", "properties": {
        "column": {"type": "string"}, "verdict": {"type": "string", "enum": ["plausible", "contradicted", "unverifiable"]},
        "evidence": {"type": "string"}}, "required": ["column", "verdict", "evidence"]}},
    "overall_trust": {"type": "string", "enum": ["high", "partial", "low"]}},
    "required": ["checks", "overall_trust"]}


def enum_legend(schema: dict) -> str:
    """List the allowed values of every enum in a schema, so the model never writes a constrained field blind."""
    found: dict[str, list[str]] = {}

    def walk(node: Any, name: str) -> None:
        if isinstance(node, dict):
            if "enum" in node:
                found.setdefault(name, node["enum"])
            for k, sub in node.get("properties", {}).items():
                walk(sub, k)
            if "items" in node:
                walk(node["items"], name)
    walk(schema, "")
    return "\nALLOWED VALUES:\n" + "\n".join(f"- {k}: {', '.join(v)}" for k, v in found.items()) if found else ""


def documentation(v: Variant, level: str) -> str:
    if level == "none":
        return ""
    parts = [f"DATA OWNER DOCUMENTATION\nDescription: {v.description}", "Dictionary:"]
    parts += [f"- {c}: {d}" for c, d in v.dictionary.items()]
    if level == "rules":
        if v.rules:
            parts.append("Business rules:\n" + "\n".join(f"- {r}" for r in v.rules))
        if v.codes:
            parts.append("Code dictionary:\n" + "\n".join(f"- {c}: " + "; ".join(f"{k} = {m}" for k, m in codes.items())
                                                         for c, codes in v.codes.items()))
        if v.constraints:
            parts.append("Known constraints:\n" + "\n".join(f"- {r}" for r in v.constraints))
    return "\n".join(parts) + "\n\n"


def run_condition(llm: LLM, v: Variant, cond: str, seed: int, prof_rows: list[dict], dev_idx: Any, cands: list[dict],
                  tag: dict[str, Any]) -> dict[str, Any]:
    prof = render_profile(prof_rows, v)
    base = f"DATASET PROFILE (development split)\n{prof}\n{target_summary(v, dev_idx)}\n\n"
    doc = documentation(v, {"A_RAW": "none", "B_SELF": "none", "C_DICT": "dict", "D_RULES": "rules", "E_FULL": "rules"}[cond])
    trace: dict[str, Any] = {"condition": cond, "calls": [], "failures": []}

    def call(stage: str, user: str, schema: dict, max_tokens: int) -> dict | None:
        r = llm.call(system=SYSTEM, user=user + enum_legend(schema), schema=schema, seed=seed, max_tokens=max_tokens, tag={**tag, "stage": stage})
        trace["calls"].append({"stage": stage, "prompt_tokens": r.prompt_tokens, "output_tokens": r.output_tokens,
                               "latency_s": round(r.latency_s, 3), "compute_s": round((r.prefill_s or 0) + (r.decode_s or 0), 3) if r.decode_s is not None else None, "load_s": r.load_s, "parse_ok": r.parse_ok, "cached": r.cached, "request_hash": r.request_hash})
        if not r.parse_ok:
            trace["failures"].append({"stage": stage, "error": r.error or "parse_failure", "raw_head": r.raw[:300]})
        return r.content if r.parse_ok else None

    pre = ""
    if cond == "B_SELF":
        inf = call("self_inference", base + "TASK: before any analysis, infer independently what this dataset is: its meaning, what the "
                   "target means, what one row is, and a role and meaning guess for EVERY column. Keep each meaning_guess under 10 words.", INFER_SCHEMA, 3200)
        trace["inference"] = inf
        if inf:
            pre = "YOUR EARLIER SELF-INFERENCE:\n" + json.dumps(inf)[:3500] + "\n\n"
    if cond == "E_FULL":
        ver = call("verify", base + doc + "TASK: do not trust the documentation blindly. For every documented column decide whether its "
                   "description is plausible given the profile (value ranges, types, cardinality, association with the target), "
                   "contradicted, or unverifiable, citing the profile evidence in under 15 words per column.", VERIFY_SCHEMA, 3200)
        trace["verification"] = ver
        if ver:
            pre = "YOUR VERIFICATION OF THE DOCUMENTATION:\n" + json.dumps(ver)[:3500] + "\n\n"
    analysis = call("analysis", base + doc + pre + ANALYSIS_TASK, ANALYSIS_SCHEMA, 1500)
    trace["analysis"] = analysis
    ctext = "\n".join(f"- {c['id']}: {c['description']} (univariate AUC on development rows {c['univariate_auc']})" for c in cands)
    fe = call("feature_engineering", base + doc + pre + "YOUR SEMANTIC ANALYSIS:\n" + json.dumps(analysis or {})[:2500] + "\n\n" +
              "TASK: (1) propose up to 6 new features built only from existing columns with the allowed ops (ratio, diff, product, sum, "
              "mean, log1p, is_zero); give semantic and statistical rationale, a leakage assessment and the business interpretation. "
              "Do not build features from identifiers, post-outcome or artifact columns. "
              "(2) Judge each CANDIDATE feature below: accept or reject, with the reason. A strong univariate AUC is not by itself a "
              "reason to accept. Return candidate_judgements keyed by the candidate id exactly as listed.\nCANDIDATES:\n" + ctext,
              fe_schema(cands), 1800)
    trace["fe"] = fe
    return trace
