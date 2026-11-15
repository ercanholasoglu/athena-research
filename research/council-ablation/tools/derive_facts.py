"""Council ablation facts, derived from the evidence in `../evidence/`.

    python research/council-ablation/tools/derive_facts.py            # writes ../results/facts.json
    python research/council-ablation/tools/derive_facts.py --check    # fails if the derivation differs from the committed facts

Every number in the rendered READMEs and docs that concerns this study is a `{{council:key}}` reference to this file's
output. Accuracies and deltas are fractions (render them with `|pct` or `|pp`); costs are US dollars.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parents[1]
EV = STUDY / "evidence"
RESULT = STUDY / "results" / "facts.json"

#: Short keys for the six council conditions, in the order of the pre-registration.
CONDITIONS = {
    "B1": "B1_same_provider_roles",
    "B2": "B2_same_provider_sampling",
    "C": "C_multi_provider",
    "D": "D_characteristic_diverse",
    "E": "E_judge",
    "F": "F_adaptive_routing",
}


def jl(rel: str) -> list[dict]:
    return [json.loads(x) for x in (EV / rel).read_text().splitlines() if x.strip()]


def build_facts() -> dict:
    r = json.loads((EV / "council" / "results.json").read_text())
    c = r["conditions"]
    n_eval = r["n_evaluation"]
    members = jl("council/member_calls.jsonl")
    judge = jl("council/judge_calls.jsonl")
    archive = jl("council/member_calls_budget300_archive.jsonl")
    model_of = {m["member"]: m["model"] for m in members}
    solo = c[f"A_solo:{r['strong_solo']}"]

    f: dict = {
        "cases.total": r["n_cases"],
        "cases.calibration": r["n_calibration"],
        "cases.evaluation": n_eval,
        "solo.member": r["strong_solo"],
        "solo.model": model_of[r["strong_solo"]].split("/", 1)[1],
        "solo.accuracy": solo["accuracy"],
        "solo.correct": round(solo["accuracy"] * n_eval),
        "solo.cost_per_decision": solo["cost_usd_per_decision"],
        "solo.cost_per_1k": round(1000 * solo["cost_usd_per_decision"], 3),
        "solo.latency_s": solo["latency_s_per_decision"],
        "haiku.model": model_of["haiku"].split("/", 1)[1],
        "haiku.accuracy": c["A_solo:haiku"]["accuracy"],
        "haiku.cost_per_decision": c["A_solo:haiku"]["cost_usd_per_decision"],
        "haiku.cost_per_1k": round(1000 * c["A_solo:haiku"]["cost_usd_per_decision"], 3),
        "haiku.correct": round(c["A_solo:haiku"]["accuracy"] * n_eval),
        "haiku.delta": c["A_solo:haiku"]["vs_strong_solo"]["delta"],
        "haiku.latency_s": c["A_solo:haiku"]["latency_s_per_decision"],
        "qwen7b.accuracy": c["A_solo:qwen7b"]["accuracy"],
        "qwen1_5b.accuracy": c["A_solo:qwen1_5b"]["accuracy"],
        "conditions.count": len(CONDITIONS),
        "conditions.rejected": sum(r["decisions"][v] == "REJECTED" for v in CONDITIONS.values()),
        "hypotheses.H0": r["hypotheses"]["H0"],
        "hypotheses.H1": r["hypotheses"]["H1"],
    }
    assert set(r["decisions"]) == set(CONDITIONS.values()), "condition set changed"
    for short, key in CONDITIONS.items():
        row = c[key]
        f[f"{short}.accuracy"] = row["accuracy"]
        f[f"{short}.correct"] = round(row["accuracy"] * n_eval)
        f[f"{short}.delta"] = row["vs_strong_solo"]["delta"]
        f[f"{short}.ci_low"], f[f"{short}.ci_high"] = row["vs_strong_solo"]["ci95"]
        f[f"{short}.cost_per_decision"] = row["cost_usd_per_decision"]
        f[f"{short}.cost_per_1k"] = round(1000 * row["cost_usd_per_decision"], 3)
        f[f"{short}.latency_s"] = row["latency_s_per_decision"]
        f[f"{short}.decision"] = r["decisions"][key]
    f["conditions.tied"] = sum(f[f"{s}.correct"] == f["solo.correct"] for s in CONDITIONS)
    f["conditions.below"] = sum(f[f"{s}.correct"] < f["solo.correct"] for s in CONDITIONS)
    f["conditions.above"] = sum(f[f"{s}.correct"] > f["solo.correct"] for s in CONDITIONS)
    below = {f[f"{s}.correct"] for s in CONDITIONS if f[f"{s}.correct"] < f["solo.correct"]}
    assert len(below) == 1, "the conditions below the single model no longer share one score"
    f["conditions.below_correct"] = below.pop()
    equal = [k for k, v in c.items() if v["accuracy"] >= solo["accuracy"]]
    cheapest = min(equal, key=lambda k: c[k]["cost_usd_per_decision"])
    # The cheapest equally accurate row is a Haiku sample (the re-samples haiku_repeat / haiku_s* share one configuration).
    assert cheapest.startswith("A_solo:") and model_of[cheapest.split(":", 1)[1]] == model_of["haiku"], cheapest
    assert all(c[k]["cost_usd_per_decision"] > c["A_solo:haiku"]["cost_usd_per_decision"] for k in CONDITIONS.values()), \
        "a council is no longer more expensive than the cheapest equally accurate single model"
    f["E.cost_ratio"] = round(c["E_judge"]["cost_usd_per_decision"] / solo["cost_usd_per_decision"], 1)
    f["E.latency_ratio"] = round(c["E_judge"]["latency_s_per_decision"] / solo["latency_s_per_decision"], 1)
    f["F.escalated"] = int(str(c["F_adaptive_routing"]["escalated_to_human"]).split("/")[0].strip())
    f["F.calls_per_decision"] = c["F_adaptive_routing"]["calls_per_decision"]
    h2 = r["hypotheses"]["H2"]
    f["H2.combinations"] = h2["combinations"]
    f["H2.spearman_double_fault"] = h2["spearman_gain_vs_double_fault"]
    f["H2.spearman_provider_count"] = h2["spearman_gain_vs_provider_count"]

    # Cost: distinct calls only. The archived 300-token pass is the first rows of member_calls.jsonl, so adding it
    # again double-counts (the figure first reported, corrected in the write-ups).
    assert archive == members[: len(archive)], "archive is no longer a prefix of member_calls.jsonl"
    distinct = members + judge
    f["cost.calls"] = len(distinct)
    f["cost.total_usd"] = round(sum(x["cost_usd"] or 0 for x in distinct), 2)
    f["cost.double_counted_usd"] = round(sum(x["cost_usd"] or 0 for x in distinct + archive), 2)
    f["cost.reasked"] = len(members) - len(archive)

    runs = json.loads((EV / "notebook_runs.json").read_text())
    nbs = runs["runs"]
    f["notebooks.count"] = len(nbs)
    f["notebooks.pass"] = sum(n["result"] == "PASS" for n in nbs)
    plans = json.loads((EV / "reasoning_methods" / "research_plans.json").read_text())
    f["plans.count"] = len(plans["plans"])
    return f


def main() -> None:
    facts = build_facts()
    text = json.dumps(facts, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        if not RESULT.exists() or RESULT.read_text() != text:
            sys.exit("council facts differ from the committed results/facts.json")
        print("COUNCIL FACTS OK", len(facts), "keys")
        return
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(text)
    print("wrote", RESULT.relative_to(STUDY.parents[1]), len(facts), "keys")


if __name__ == "__main__":
    main()
