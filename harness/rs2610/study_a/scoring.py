"""Per-run scoring against the pre-registered reference contract."""
from __future__ import annotations

import re
from typing import Any

from rs2610.study_a.tasks import COMPLEXITY, UNDET

EID = re.compile(r"\bE\d+\b")
CID = re.compile(r"\bC\d+\b")


def evidence_ids(text: str, claim_sources: dict[str, list[str]]) -> set[str]:
    """Evidence ids named directly, plus those behind any GoT claim id named (a claim rests on its source evidence)."""
    ids = set(EID.findall(text))
    for cid in CID.findall(text):
        for src in claim_sources.get(cid, []):
            ids |= set(EID.findall(str(src)))
    return ids


def score_run(inst: dict[str, Any], trace: dict[str, Any]) -> dict[str, Any]:
    final = trace.get("final") or {}
    ids = [o["id"] for o in inst["options"]]
    decision = final.get("decision") if final.get("decision") in ids else None
    conf = final.get("confidence")
    try:
        conf = float(conf)
        conf = conf / 100 if conf > 1.0 else conf  # a 0-100 scale is normalised, and counted below
        conf = min(max(conf, 0.0), 1.0)
    except (TypeError, ValueError):
        conf = None
    ref = inst["reference"]
    correct = decision in ref["accept"] if decision else False
    util = {k: v for k, v in inst.get("utility", {}).items() if v is not None}
    regret = None
    regret_status = "UNKNOWN_NO_OUTCOME"
    if util:
        if decision in util:
            regret = max(util.values()) - util[decision]
            regret_status = "MEASURED"
        elif decision == UNDET:
            regret_status = "ABSTAINED"
        else:
            regret_status = "FAILED_RUN" if decision is None else "UNKNOWN_NO_OUTCOME"
    order = COMPLEXITY.get(inst["family"])
    par = ref.get("parsimonious")
    unnecessary = bool(correct and order and par in (order or []) and decision in order and order.index(decision) > order.index(par))
    st = trace.get("structure")
    claim_sources = st.get("claim_sources", {}) if isinstance(st, dict) else {}
    refs = set()
    for r in final.get("evidence_refs", []) or []:
        refs |= evidence_ids(str(r), claim_sources)
    key = set(inst.get("key_evidence", []))
    util_ev = len(refs & key) / len(key) if key else None
    contra_txt = " ".join(map(str, final.get("contradictions", []) or []))
    conflict = set(inst.get("conflict_evidence", []))
    contra_handled = (len(evidence_ids(contra_txt, claim_sources) & conflict) > 0) if conflict else None
    calls = trace["calls"]
    pt = [c["prompt_tokens"] for c in calls]
    ot = [c["output_tokens"] for c in calls]
    return {
        "decision": decision, "parse_failed": decision is None, "correct": correct, "confidence": conf,
        "regret": regret, "regret_status": regret_status, "unnecessary_complexity": unnecessary,
        "uncertainty_expected": ref.get("uncertainty_expected", False),
        "uncertainty_preserved": (decision == UNDET or (conf is not None and conf <= 0.65)) if ref.get("uncertainty_expected") else None,
        "abstained": decision == UNDET,
        "evidence_utilization": util_ev, "n_refs": len(refs), "contradiction_handled": contra_handled,
        "n_contradictions_listed": len(final.get("contradictions", []) or []),
        "n_calls": len(calls), "n_failed_calls": len(trace["failures"]),
        "prompt_tokens": sum(p for p in pt if p is not None) if all(p is not None for p in pt) else None,
        "output_tokens": sum(o for o in ot if o is not None) if all(o is not None for o in ot) else None,
        "tokens_status": "ACTUAL" if all(p is not None for p in pt + ot) else "PARTIAL_UNKNOWN",
        "latency_s": round(sum(c["compute_s"] for c in calls), 3) if all(c.get("compute_s") is not None for c in calls) else None,
        "latency_status": "ACTUAL_SERVER_COMPUTE (prefill+decode)",
        "wall_latency_s": round(sum(c["latency_s"] for c in calls), 3), "wall_s": trace.get("wall_s"),
        "any_cached": any(c["cached"] for c in calls),
        "topology": trace.get("topology", {}),
    }
