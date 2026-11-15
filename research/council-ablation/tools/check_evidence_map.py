"""Verify every number the write-ups use against the evidence, then render EVIDENCE_MAP.md.

Each claim names its source file and a JSON path (or a computation over a published file) and the value
the write-ups print. A claim passes only when the evidence, rounded as stated, equals that value.
Exit code 1 when any claim fails; EVIDENCE_MAP.md then marks it FAIL.

    python tools/check_evidence_map.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "evidence"
#: Jev evidence is the JEV study's canonical (redacted) copy in this repository, not a second copy here.
JEV = ROOT.parent / "jev" / "evidence"
R = json.loads((EV / "council/results.json").read_text())
C = R["conditions"]


def jl(rel):
    return [json.loads(x) for x in (EV / rel).read_text().splitlines() if x.strip()]


def cost_total():
    rows = jl("council/member_calls.jsonl") + jl("council/judge_calls.jsonl")
    return round(sum(r["cost_usd"] or 0 for r in rows), 2), len(rows)


J = json.loads((JEV / "jev-semantics-ablation-2026-10-21.json").read_text())
JS = J["comparison_vs_experiment_a"]["EXECUTION_SCALE"]

#: (claim, value printed in the write-ups, source, function returning the evidence value)
CLAIMS = [
    ("Cases total / calibration / evaluation", "110 / 39 / 71", "council/results.json: n_cases, n_calibration, n_evaluation",
     lambda: f"{R['n_cases']} / {R['n_calibration']} / {R['n_evaluation']}", "MEASURED"),
    ("Strong solo chosen on calibration", "sonnet", "council/results.json: strong_solo", lambda: R["strong_solo"], "MEASURED"),
    ("Strong solo accuracy", "0.986", "conditions['A_solo:sonnet'].accuracy", lambda: f"{C['A_solo:sonnet']['accuracy']:.3f}", "MEASURED"),
    ("Haiku solo accuracy", "0.986", "conditions['A_solo:haiku'].accuracy", lambda: f"{C['A_solo:haiku']['accuracy']:.3f}", "MEASURED"),
    ("C and E accuracy (tie)", "0.986 / 0.986", "conditions C_multi_provider, E_judge",
     lambda: f"{C['C_multi_provider']['accuracy']:.3f} / {C['E_judge']['accuracy']:.3f}", "MEASURED"),
    ("B1, B2, D, F accuracy", "0.972", "conditions B1, B2, D, F",
     lambda: "0.972" if {round(C[k]['accuracy'], 3) for k in ("B1_same_provider_roles", "B2_same_provider_sampling",
                                                              "D_characteristic_diverse", "F_adaptive_routing")} == {0.972} else "mismatch",
     "MEASURED"),
    ("B1/B2/D/F delta vs solo and CI", "-0.014 [-0.042, 0]", "conditions[...].vs_strong_solo",
     lambda: "{:.3f} [{:.3f}, {:g}]".format(C["B1_same_provider_roles"]["vs_strong_solo"]["delta"],
                                            *C["B1_same_provider_roles"]["vs_strong_solo"]["ci95"]), "MEASURED"),
    ("All council decisions", "REJECTED x6", "decisions",
     lambda: "REJECTED x6" if set(R["decisions"].values()) == {"REJECTED"} and len(R["decisions"]) == 6 else "mismatch", "MEASURED"),
    ("H0 / H1", "NOT_REJECTED / NOT_SUPPORTED", "hypotheses", lambda: f"{R['hypotheses']['H0']} / {R['hypotheses']['H1']}", "MEASURED"),
    ("H3 (F decision)", "REJECTED", "hypotheses.H3.F_decision", lambda: R["hypotheses"]["H3"]["F_decision"], "MEASURED"),
    ("Sonnet cost per decision", "0.001994", "conditions['A_solo:sonnet'].cost_usd_per_decision",
     lambda: f"{C['A_solo:sonnet']['cost_usd_per_decision']:.6f}", "MEASURED"),
    ("Haiku cost per decision", "0.000129", "conditions['A_solo:haiku'].cost_usd_per_decision",
     lambda: f"{C['A_solo:haiku']['cost_usd_per_decision']:.6f}", "MEASURED"),
    ("Judge cost / latency / tokens per decision", "0.004899 / 5.26 / 1927", "conditions.E_judge",
     lambda: f"{C['E_judge']['cost_usd_per_decision']:.6f} / {C['E_judge']['latency_s_per_decision']:.2f} / {C['E_judge']['tokens_per_decision']:.0f}",
     "MEASURED cost; ESTIMATED latency"),
    ("Solo latency per decision", "2.31", "conditions['A_solo:sonnet'].latency_s_per_decision",
     lambda: f"{C['A_solo:sonnet']['latency_s_per_decision']:.2f}", "MEASURED"),
    ("Judge cost and latency multiples", "2.5x / 2.3x", "E_judge vs A_solo:sonnet",
     lambda: f"{C['E_judge']['cost_usd_per_decision'] / C['A_solo:sonnet']['cost_usd_per_decision']:.1f}x / "
             f"{C['E_judge']['latency_s_per_decision'] / C['A_solo:sonnet']['latency_s_per_decision']:.1f}x", "ESTIMATED (ratio)"),
    ("Haiku cost relative to Sonnet", "1/15", "A_solo:haiku vs A_solo:sonnet",
     lambda: f"1/{round(C['A_solo:sonnet']['cost_usd_per_decision'] / C['A_solo:haiku']['cost_usd_per_decision'])}", "ESTIMATED (ratio)"),
    ("F escalations to human review", "36 / 71", "conditions.F_adaptive_routing.escalated_to_human",
     lambda: C["F_adaptive_routing"]["escalated_to_human"], "MEASURED"),
    ("F calls per decision", "3.35", "conditions.F_adaptive_routing.calls_per_decision",
     lambda: f"{C['F_adaptive_routing']['calls_per_decision']:.2f}", "MEASURED"),
    ("Spearman gain vs double fault / provider count", "-0.83 / -0.18", "hypotheses.H2",
     lambda: f"{R['hypotheses']['H2']['spearman_gain_vs_double_fault']:.2f} / {R['hypotheses']['H2']['spearman_gain_vs_provider_count']:.2f}",
     "MEASURED (descriptive)"),
    ("Combinations examined", "35", "hypotheses.H2.combinations", lambda: str(R["hypotheses"]["H2"]["combinations"]), "MEASURED"),
    ("Sonnet~Haiku error phi", "1.0", "pairwise_error_phi_evaluation['sonnet~haiku']",
     lambda: f"{R['pairwise_error_phi_evaluation']['sonnet~haiku']:.1f}", "MEASURED"),
    ("Critic critical misses / verifier false alarms", "0.000 / 0.059", "member_characteristics",
     lambda: f"{R['member_characteristics']['haiku_critic']['permissiveness_critical_miss']:.3f} / "
             f"{R['member_characteristics']['haiku_verifier']['conservatism_false_alarm']:.3f}", "MEASURED"),
    ("Critic is the only Claude member with zero critical misses", "haiku_critic", "member_characteristics",
     lambda: ",".join(m for m, v in R["member_characteristics"].items()
                      if not m.startswith("qwen") and v["permissiveness_critical_miss"] == 0), "MEASURED"),
    ("Qwen 7B accuracy", "0.620", "member_characteristics.qwen7b.accuracy",
     lambda: f"{R['member_characteristics']['qwen7b']['accuracy']:.3f}", "MEASURED"),
    ("Reproducibility of re-sampled Haiku", "110 / 110", "system_quality",
     lambda: R["system_quality"]["reproducibility_haiku_T1_two_samples"].split(" identical")[0], "MEASURED"),
    ("Total provider-reported cost, distinct calls", "0.71 / 1506", "council/member_calls.jsonl + judge_calls.jsonl (sum of cost_usd)",
     lambda: "{} / {}".format(*cost_total()), "MEASURED"),
    ("Re-asked truncated calls", "186", "member_calls.jsonl rows beyond the archive",
     lambda: str(len(jl("council/member_calls.jsonl")) - len(jl("council/member_calls_budget300_archive.jsonl"))), "MEASURED"),
    ("Jev EXECUTION_SCALE raw accuracy A -> B", "0.578 -> 0.733", "research/jev/evidence/jev-semantics-ablation-2026-10-21.json: comparison_vs_experiment_a",
     lambda: f"{JS['accuracy_raw']['A']:.3f} -> {JS['accuracy_raw']['B']:.3f}", "MEASURED"),
    ("Jev intervals overlap", "True", "comparison_vs_experiment_a.EXECUTION_SCALE.accuracy_raw.intervals_overlap",
     lambda: str(JS["accuracy_raw"]["intervals_overlap"]), "MEASURED"),
    ("Jev cost", "UNKNOWN", "research/jev/evidence/jev-ablation-2026-10-21.json: cost.state",
     lambda: json.loads((JEV / "jev-ablation-2026-10-21.json").read_text())["cost"]["state"], "UNKNOWN"),
    ("Mean gain by provider count (1 / 2 providers)", "-0.004 / -0.056", "hypotheses.H2.mean_gain_by_provider_count",
     lambda: "{:.3f} / {:.3f}".format(R["hypotheses"]["H2"]["mean_gain_by_provider_count"]["1"]["mean_gain"],
                                      R["hypotheses"]["H2"]["mean_gain_by_provider_count"]["2"]["mean_gain"]), "MEASURED (descriptive)"),
    ("Critic~Sonnet error phi", "-0.014", "pairwise_error_phi_evaluation['sonnet~haiku_critic']",
     lambda: f"{R['pairwise_error_phi_evaluation']['sonnet~haiku_critic']:.3f}", "MEASURED"),
    ("Qwen 1.5B accuracy / false-alarm rate", "0.282 / 0.882", "member_characteristics.qwen1_5b",
     lambda: f"{R['member_characteristics']['qwen1_5b']['accuracy']:.3f} / {R['member_characteristics']['qwen1_5b']['conservatism_false_alarm']:.3f}",
     "MEASURED"),
    ("Truncated at 300 tokens without an answer (verifier / critic / sonnet / all)", "44 / 31 / 8 / 186",
     "council/member_calls_budget300_archive.jsonl (answer is null and tokens_out >= 300)", lambda: _truncated(), "MEASURED"),
    ("Single strong-solo error on evaluation", "feature_screening:29", "member_calls.jsonl (sonnet) vs cases.json",
     lambda: _solo_errors(), "MEASURED"),
    ("Claude 5.5 accepts only temperature 1", "provider-enforced", "protocol/AMENDMENTS.md, Amendment 1",
     lambda: "provider-enforced" if "accept only\n`temperature=1`" in (ROOT / "protocol/AMENDMENTS.md").read_text() else "missing", "MEASURED"),
    ("Critic right and outvoted", "feature_screening:29, feature_screening:34", "member_calls.jsonl (B1 members) vs cases.json",
     lambda: _outvoted(), "MEASURED (exploratory)"),
]


def _truncated():
    rows = jl("council/member_calls_budget300_archive.jsonl")
    cut = [r for r in rows if r["answer"] is None and (r["tokens_out"] or 0) >= 300]
    n = {m: sum(r["member"] == m for r in cut) for m in ("haiku_verifier", "haiku_critic", "sonnet")}
    return f"{n['haiku_verifier']} / {n['haiku_critic']} / {n['sonnet']} / {len(cut)}"


def _solo_errors():
    last = {}
    for r in jl("council/member_calls.jsonl"):
        last[(r["member"], r["case_id"])] = r["answer"]
    cases = json.loads((EV / "council/cases.json").read_text())["cases"]
    return ", ".join(sorted(c["case_id"] for c in cases if c["split"] == "evaluation" and last.get(("sonnet", c["case_id"])) != c["answer"]))


def _outvoted():
    last = {}
    for r in jl("council/member_calls.jsonl"):
        last[(r["member"], r["case_id"])] = r["answer"]
    truth = {c["case_id"]: c["answer"] for c in json.loads((EV / "council/cases.json").read_text())["cases"]}
    hits = [cid for cid, t in truth.items()
            if last.get(("haiku_critic", cid)) == t and last.get(("haiku_verifier", cid)) != t and last.get(("haiku_domain", cid)) != t]
    return ", ".join(sorted(hits))


def main() -> int:
    rows, failed = [], 0
    for i, (claim, value, source, fn, label) in enumerate(CLAIMS, 1):
        try:
            got = str(fn())
        except Exception as exc:  # reported, not hidden
            got = f"ERROR {type(exc).__name__}"
        ok = got == value
        failed += not ok
        rows.append((i, claim, value, got, label, source, "PASS" if ok else "FAIL"))
    lines = ["# Evidence map", "",
             "Every number in [`writeups/council-ablation.en.md`](writeups/council-ablation.en.md) and `.tr.md` is listed here, with its source in [`evidence/`](evidence/) "
             "(Jev rows: [`research/jev/evidence/`](../jev/evidence/)) and the value recomputed from that source by `research/council-ablation/tools/check_evidence_map.py`. A number that is not in this "
             "table must not appear in the write-ups.", "",
             f"**Check result: {'PASS' if not failed else 'FAIL'}** ({len(rows) - failed} / {len(rows)} claims match).", "",
             "| # | Claim | Value in write-ups | Recomputed | Label | Source | Check |", "|---|---|---|---|---|---|---|"]
    lines += [f"| {i} | {c} | {v} | {g} | {lab} | `{s}` | {r} |" for i, c, v, g, lab, s, r in rows]
    lines += ["", "**Must be said (and is):** pre-registration and amendments; ceiling effect; only two provider families, the "
              "second much weaker; the harness calls models directly (no product council path, no validator, no tenant "
              "context); the minority veto is untested; CoT/ToT/GoT in the product council are confidence/tie-break aggregation, not model reasoning (CoT/ToT/GoT as "
              "reasoning orchestration are measured separately, in Studies A and A2 of this repository).",
              "", "**Must not be said:** that councils never work; that Athena's council improves anything; any vendor "
              "ranking; any number not in this table; any significance claim beyond the reported CIs."]
    (ROOT / "EVIDENCE_MAP.md").write_text("\n".join(lines) + "\n")
    print(f"{len(rows) - failed}/{len(rows)} claims PASS")
    for r in rows:
        if r[-1] == "FAIL":
            print("FAIL", r)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
