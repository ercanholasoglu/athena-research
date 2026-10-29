"""Study B2 feature-invention task: no candidate features are shown.

The model sees what the frozen Study B analysis call sees (development-split column profile, target summary, and the
documentation its condition allows) and nothing else: no candidate list, no example feature, no earlier model output.
It proposes up to 5 features, each with an executable specification in a small DSL that ``evaluate.compute`` executes.
The call is independent of the frozen analysis and FE calls of the same run (same seed / replicate, separate request).
"""
from __future__ import annotations

from typing import Any

from rs2610.study_b.conditions import SYSTEM, documentation, enum_legend
from rs2610.study_b.profile import render_profile, target_summary
from rs2610.study_b.variants import Variant

OPS = ("ratio", "diff", "product", "sum", "mean", "min", "max", "std", "count_positive", "log1p", "is_zero", "gt_threshold",
       "eq_value")
LIST = {"type": "array", "items": {"type": "string"}}

INVENT_SCHEMA = {"type": "object", "properties": {"features": {"type": "array", "maxItems": 5, "items": {
    "type": "object", "properties": {
        "feature_name": {"type": "string"}, "source_columns": LIST, "transformation": {"type": "string"},
        "spec": {"type": "object", "properties": {"op": {"type": "string", "enum": list(OPS)}, "inputs": LIST,
                                                  "threshold": {"type": "number"}, "value": {"type": "string"}},
                 "required": ["op", "inputs", "threshold", "value"]},
        "semantic_rationale": {"type": "string"}, "statistical_rationale": {"type": "string"},
        "business_interpretation": {"type": "string"},
        "leakage_assessment": {"type": "string", "enum": ["none", "possible", "likely"]},
        "expected_stability": {"type": "string", "enum": ["high", "medium", "low"]},
        "actionability": {"type": "string"}},
    "required": ["feature_name", "source_columns", "transformation", "spec", "semantic_rationale", "statistical_rationale",
                 "business_interpretation", "leakage_assessment", "expected_stability", "actionability"]}}},
    "required": ["features"]}

INVENT_TASK = (
    "TASK: invent up to 5 ORIGINAL engineered features that should improve prediction of the target. No candidate features are "
    "provided; design them yourself from the columns shown. Each feature must be executable with exactly one op:\n"
    "- ratio(a, b) = a / b; diff(a, b) = a - b; product(a, b, ...); sum(...); mean(...); min(...); max(...); std(...) across "
    "the inputs; count_positive(...) = number of inputs > 0\n"
    "- log1p(a); is_zero(a) = 1 if a == 0; gt_threshold(a) = 1 if a > threshold; eq_value(a) = 1 if a equals value\n"
    "For each feature give: feature_name; source_columns (identical to spec.inputs); transformation (one line); spec (op, inputs, "
    "threshold, value; set threshold 0 and value '' when the op does not use them); semantic_rationale; statistical_rationale; "
    "business_interpretation; leakage_assessment; expected_stability (across time and segments); actionability (how the business "
    "could act on it, or 'n/a').\n"
    "Every feature must be computable at prediction time. Do not use identifiers, columns known only after the outcome, "
    "data-collection artifacts, or anything derived from the target.")

LEVEL = {"A_RAW": "none", "B_SELF": "none", "C_DICT": "dict", "D_RULES": "rules", "E_FULL": "rules"}
MAX_TOKENS = 2200


def prompt(v: Variant, cond: str, prof_rows: list[dict], dev_idx: Any) -> str:
    base = f"DATASET PROFILE (development split)\n{render_profile(prof_rows, v)}\n{target_summary(v, dev_idx)}\n\n"
    return base + documentation(v, LEVEL[cond]) + INVENT_TASK + enum_legend(INVENT_SCHEMA)


def invent(llm: Any, v: Variant, cond: str, seed: int, prof_rows: list[dict], dev_idx: Any, tag: dict[str, Any]) -> dict[str, Any]:
    r = llm.call(system=SYSTEM, user=prompt(v, cond, prof_rows, dev_idx), schema=INVENT_SCHEMA, seed=seed, max_tokens=MAX_TOKENS,
                 tag={**tag, "stage": "feature_invention"})
    return {"call": {"stage": "feature_invention", "prompt_tokens": r.prompt_tokens, "output_tokens": r.output_tokens,
                     "latency_s": round(r.latency_s, 3),
                     "compute_s": round((r.prefill_s or 0) + (r.decode_s or 0), 3) if r.decode_s is not None else None,
                     "parse_ok": r.parse_ok, "cached": r.cached, "request_hash": r.request_hash, "error": r.error},
            "features": (r.content or {}).get("features") if r.parse_ok else None,
            "failure": None if r.parse_ok else {"error": r.error or "parse_failure", "raw_head": r.raw[:300]}}
