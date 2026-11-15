"""Generate the eight analysis notebooks from frozen evidence.

The notebooks read ``evidence/`` only. They make no model, provider or network call, so
re-running them cannot change a result. Every status label is copied from the evidence or
from the reasoning-methods registry snapshot; nothing is inferred from a name.

    python tools/build_notebooks.py          # writes notebooks/*.ipynb (unexecuted)
    python tools/run_notebooks.py            # clean-kernel Restart + Run All of every notebook
"""
from __future__ import annotations

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks"

SETUP = '''\
import json
import platform
import random
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 11  # the pre-registered bootstrap seed; reused for every derived computation here
random.seed(SEED)
np.random.seed(SEED)
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "EVIDENCE_MAP.md").exists())  # research/council-ablation
EV = ROOT / "evidence"
JEV = ROOT.parent / "jev" / "evidence"  # the JEV study's canonical copy in this repository
pd.set_option("display.max_colwidth", 140)
pd.set_option("display.width", 220)


def load(rel):
    return json.loads((EV / rel).read_text())


def jsonl(rel):
    return [json.loads(x) for x in (EV / rel).read_text().splitlines() if x.strip()]


def final_calls(rel):
    """The harness cache is append-only: a re-asked call (Amendments 1 and 2) appends a new row and the
    last row per (member, case) is the one analysed. Earlier rows stay in the file as recorded calls."""
    return pd.DataFrame(jsonl(rel)).drop_duplicates(["member", "case_id"], keep="last").reset_index(drop=True)


R = load("council/results.json")
REG = {r["id"]: r for r in load("reasoning_methods/reasoning_methods_registry.json")}
print("python", platform.python_version(), "| pandas", pd.__version__, "| numpy", np.__version__, "| seed", SEED)
print("evidence files:", sorted(str(p.relative_to(ROOT)) for p in EV.rglob("*") if p.is_file()))
'''

STATUS_FN = '''\
#: Evaluation state per method, with the evidence that sets it. Explicit, not inferred from text.
EVALUATION = {
    "deterministic-baseline": "MEASURED",      # reference arm of the decision-methods ablation
    "single-strong-model": "MEASURED",         # condition A of the council benchmark
    "council": "MEASURED",                     # conditions B1-D, F (harness, not the product endpoint)
    "proposer-judge": "MEASURED",              # as condition E (judge over C) in the harness only
    "critic-veto": "NOT_RUN",
    "critic-selective-council": "NOT_RUN",
    "cot": "SIMULATED (mock runner)",
    "tot": "SIMULATED (mock runner)",
    "got": "SIMULATED (mock runner)",
    "self-consistency": "NOT_RUN",
    "react": "NOT_RUN",
    "reflexion": "NOT_RUN",
    "pot-evidence": "NOT_RUN",
    "mcts": "NOT_RUN",
    "jev": "MEASURED",                         # real provider calls on decision-corpus-v1
    "agentic-llm-decision": "MEASURED",        # decision-methods ablation, small local model
    "hermes-agent-patterns": "NOT_RUN",
}


def status_row(method_id):
    """Implementation / wiring / evaluation labels, derived from the registry snapshot only."""
    r = REG[method_id]
    implemented = "NOT_IMPLEMENTED" if r["wiring"] == "NOT_PRESENT" else "IMPLEMENTED"
    wired = "WIRED" if r["wiring"] in {"WIRED", "DECISION_AFFECTING", "OBSERVED", "EVALUATED"} else "NOT_WIRED"
    evaluation = EVALUATION[method_id]
    return {"method": r["name"], "implemented": implemented, "wired": wired, "authority": r["authority"],
            "evaluation": evaluation, "production": r["production"], "recommendation": r["recommendation"],
            "result": r["result"], "limitations": r["limitations"]}
'''


def nb(title: str, intro: str, cells: list[tuple[str, str]]) -> nbformat.NotebookNode:
    book = new_notebook()
    book.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    book.metadata["language_info"] = {"name": "python"}
    book.cells = [new_markdown_cell(f"# {title}\n\n{intro}"), new_code_cell(SETUP), new_code_cell(STATUS_FN)]
    for kind, src in cells:
        book.cells.append(new_markdown_cell(src) if kind == "md" else new_code_cell(src))
    return book


LEGEND = ("Labels used in every notebook: **MEASURED** (a real provider or real run produced the number), "
          "**ESTIMATED** (derived here from measured data by a stated formula), **SIMULATED** (mock runner, no real "
          "model), **NOT_RUN**, **UNKNOWN** (the evidence does not say). Implementation and wiring are reported "
          "separately from evaluation: code that exists is not a measured capability.")

BOOKS: dict[str, nbformat.NotebookNode] = {}

BOOKS["00_protocol_and_datasets"] = nb(
    "00 — Protocol and datasets",
    "The pre-registered protocol, the case set and the provenance of every ground-truth label. " + LEGEND,
    [
        ("md", "## Protocol\n\nHypotheses H0–H3, conditions A–F, the calibration/evaluation split and the decision "
               "rules were committed before the first model call (`protocol/PREREGISTRATION.md`). Two amendments were "
               "recorded before any result was read (`protocol/AMENDMENTS.md`): the Claude 5.5 models accept only "
               "temperature 1, and a 300-token budget truncated 186 answers, which were re-asked with 1 024 tokens."),
        ("code", '''\
C = load("council/cases.json")
cases = pd.DataFrame(C["cases"])
print("cases:", len(cases), "| calibration:", (cases.split == "calibration").sum(), "| evaluation:", (cases.split == "evaluation").sum())
pd.crosstab(cases.family, cases.split, margins=True)'''),
        ("code", "pd.crosstab([cases.difficulty, cases.consequence], cases.split, margins=True)"),
        ("md", "## Ground-truth provenance\n\nEvery label comes from public dataset documentation or from a rule stated "
               "inside the case. No label is produced by a model. **No dataset rows are included in this package**: a "
               "case quotes a column name and its documented meaning only."),
        ("code", '''\
ctx = pd.DataFrame([{"context": k, **v} for k, v in C["contexts"].items()])
ctx[["context", "dataset", "target", "decision_about_people", "source"]]'''),
        ("code", '''\
cases.source.map(lambda s: "constructed (rule stated in case)" if str(s).startswith("constructed") else "public documentation").value_counts()'''),
        ("md", "## Integrity of the copied protocol and harness\n\nThe SHA-256 of each copied file is compared with the "
               "manifest written when the package was built from the source repository."),
        ("code", '''\
import hashlib
man = load("SOURCE_MANIFEST.json")
pairs = {"scripts/research/council/cases.py": "harness/cases.py", "scripts/research/council/run.py": "harness/run.py",
         "docs/research/council-ablation/PREREGISTRATION.md": "protocol/PREREGISTRATION.md",
         "docs/research/council-ablation/AMENDMENTS.md": "protocol/AMENDMENTS.md",
         "docs/research/council-ablation/evidence/results.json": "evidence/council/results.json"}
rows = [{"source": s, "package": p, "match": hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == man["sha256"][s]} for s, p in pairs.items()]
df = pd.DataFrame(rows); assert df.match.all(), df; df'''),
        ("code", '''\
fz = (ROOT / "protocol/PREREGISTRATION.md").read_text()
print(fz[fz.index("## Freeze record"):])'''),
    ],
)

BOOKS["01_routing_and_jev"] = nb(
    "01 — Routing and Jev",
    "Adaptive routing (council condition F) and the Jev bounded-decision provider. Two different benchmarks: "
    "routing was measured on the 71 council evaluation cases; Jev on the decision corpus `decision-corpus-v1`. "
    "The two are not compared with each other. " + LEGEND,
    [
        ("code", 'pd.DataFrame([status_row(m) for m in ("single-strong-model", "jev", "agentic-llm-decision", "hermes-agent-patterns")]).T'),
        ("md", "## Adaptive routing (condition F) — MEASURED\n\nFixed rule, not tuned: agreement of two cheap members "
               "→ answer; disagreement → judge; judge confidence < 0.6 or a high-consequence case → council D and human review."),
        ("code", '''\
F = R["conditions"]["F_adaptive_routing"]
pd.Series({k: F[k] for k in ("accuracy", "critical_miss_rate", "calls_per_decision", "tokens_per_decision",
                              "latency_s_per_decision", "cost_usd_per_decision")} | {"delta_vs_strong_solo": F["vs_strong_solo"]["delta"],
                              "ci95": F["vs_strong_solo"]["ci95"], "decision": R["decisions"]["F_adaptive_routing"]}, name="F").to_frame()'''),
        ("code", 'pd.Series(R["hypotheses"]["H3"], name="H3").to_frame()'),
        ("md", "**RESULT.** F scored 0.972 (69/71) against 0.986 for the strong solo model and used more tokens than the "
               "multi-provider council, because every high-consequence case was routed to council D. H3 is rejected on "
               "this benchmark. The routing rule of the Athena *Hermes* persona is not part of this measurement: "
               "routing quality for that persona is `NOT_RUN`. The registry row `Hermes Agent patterns (Nous "
               "Research)` above is a different thing: an external agent runtime whose patterns were reviewed; it is "
               "not embedded in Athena and is not the Athena Hermes persona."),
        ("md", "## Jev bounded decisions — MEASURED (real provider calls)\n\nJev was asked the same typed, closed-set "
               "question as every other decision method; Athena's policy resolver had the final say. Provider cost is "
               "`UNKNOWN`: the API reports tokens but no price."),
        ("code", '''\
A = json.loads((JEV / "jev-ablation-2026-10-21.json").read_text())
rows = []
for dtype, res in A["results"].items():
    for arm, m in res["arms"].items():
        rows.append({"decision_type": dtype, "arm": arm, "n": m.get("cases_evaluated"), "accuracy_raw": m.get("accuracy_raw"),
                     "accuracy_final": m.get("accuracy_after_resolver_with_fallback"), "brier": m.get("brier"), "ece": m.get("ece")})
jev = pd.DataFrame(rows)
jev.pivot_table(index="decision_type", columns="arm", values="accuracy_raw").round(3)'''),
        ("code", '''\
print("calls:", A["jev_calls"], "| cost:", A["cost"]["state"], "-", A["cost"]["reason"])
for line in A["limitations"]:
    print("-", line)'''),
        ("md", "## Jev with Athena semantic context — MEASURED, one decision family"),
        ("code", '''\
S = json.loads((JEV / "jev-semantics-ablation-2026-10-21.json").read_text())
cmp = S["comparison_vs_experiment_a"]["EXECUTION_SCALE"]
pd.DataFrame({k: v for k, v in cmp.items() if isinstance(v, dict) and "A" in v}).T[["A", "B", "delta_B_minus_A"]]'''),
        ("code", 'pd.Series(S["token_accounting"]["A"]).to_frame("A").join(pd.Series(S["token_accounting"]["B"]).to_frame("B"))'),
        ("md", "**RESULT.** On `EXECUTION_SCALE` (n = 90), typed semantics raised Jev's raw accuracy from 0.578 to 0.733 "
               "and lowered Brier from 0.576 to 0.364, at 1.78× input tokens per call on that family (1.60× over all 279 evaluated calls of the six families). The 95 % Wilson intervals "
               "overlap, so the gain is not established. Deterministic rules remain more accurate on policy-labelled "
               "decisions by construction (the policy *is* the label).\n\n**Not measured:** Jev latency on a comparable "
               "network path, Jev on the council case set, shadow-mode comparison against the router."),
    ],
)

BOOKS["02_cot_tot_got"] = nb(
    "02 — Chain-, Tree- and Graph-of-Thoughts",
    "What CoT, ToT and GoT actually do in Athena, and what was (and was not) measured. " + LEGEND,
    [
        ("code", 'pd.DataFrame([status_row(m) for m in ("cot", "tot", "got", "self-consistency")]).T'),
        ("md", "## What the wiring is\n\nIn Athena, *CoT / ToT / GoT* are **post-hoc aggregations over council member "
               "answers**, not reasoning performed by a model. Each member is called once; the chain, tree or graph is "
               "built from the returned text and makes **zero** model calls of its own. Its only effect is a "
               "confidence boost (×1.15) for the member it prefers. Under the default `vote` strategy that boost only "
               "breaks ties; under `confidence`, `consensus` and `debate` it can change the winner. These methods are "
               "therefore **confidence / tie-break behaviour**, not evidence of chain-of-thought, tree search or "
               "graph reasoning by a language model."),
        ("code", 'print(REG["cot"]["affects_final"])\nprint()\nprint(REG["cot"]["limitations"])'),
        ("md", "## The only frozen evidence — SIMULATED\n\nA reasoning-strategies harness exists and was run with a "
               "**mock runner** (6 configurations × 5 tasks). A mock cannot measure reasoning quality; it measures "
               "call and token overhead of the prompting variants and that the defect-injection checks fire."),
        ("code", 'print((EV / "reasoning_methods/reasoning_strategies_mock_benchmark.md").read_text())'),
        ("md", "**RESULT.** `NOT_RUN` with a real provider. No accuracy, cost or latency claim about CoT, ToT or GoT is "
               "made. Self-consistency (k samples, majority) is `NOT_IMPLEMENTED`; the council's vote over different "
               "personas is a different method. The research plan for a real measurement is in `METHODOLOGY.md` "
               "(roadmap state `RESEARCH_PLANNED`)."),
    ],
)

BOOKS["03_council_judge_critic"] = nb(
    "03 — Council, judge and critic",
    "Pre-registered council ablation, conditions A–F, evaluation split n = 71. " + LEGEND,
    [
        ("code", 'pd.DataFrame([status_row(m) for m in ("council", "proposer-judge", "critic-veto", "critic-selective-council")]).T'),
        ("code", '''\
order = ["A_solo:sonnet", "A_solo:haiku", "B1_same_provider_roles", "B2_same_provider_sampling", "C_multi_provider",
         "D_characteristic_diverse", "E_judge", "F_adaptive_routing"]
rows = []
for k in order:
    v = R["conditions"][k]
    rows.append({"condition": k, "members": ", ".join(v["members"]), "accuracy": v["accuracy"],
                 "delta_vs_solo": (v.get("vs_strong_solo") or {}).get("delta"), "ci95": (v.get("vs_strong_solo") or {}).get("ci95"),
                 "critical_miss": v["critical_miss_rate"], "false_alarm": v["false_alarm_rate"],
                 "decision": R["decisions"].get(k, "baseline" if k == "A_solo:sonnet" else "—")})
pd.DataFrame(rows).set_index("condition")'''),
        ("code", 'pd.Series({k: v for k, v in R["hypotheses"].items() if k in ("H0", "H1")}, name="hypothesis").to_frame()'),
        ("md", "**RESULT (MEASURED).** The strong solo model answered 70 of 71 evaluation cases. C and E tied it; B1, B2, "
               "D and F scored 69/71. Every council condition is `REJECTED_ON_THIS_BENCHMARK`. H0 is not rejected; H1 is "
               "not supported.\n\n**Scope.** With 70/71 for the solo model, the largest possible council gain is +0.014, "
               "so the rejection rule is met by construction. The result says nothing about questions a frontier solo "
               "model gets wrong. It does **not** show that councils never work."),
        ("md", "## Member characteristics (behaviour, not provider names)"),
        ("code", '''\
mc = pd.DataFrame(R["member_characteristics"]).T
mc[["model", "role", "accuracy", "permissiveness_critical_miss", "conservatism_false_alarm", "ambiguity_handling", "format_failures"]]'''),
        ("code", '''\
phi = pd.Series(R["pairwise_error_phi_evaluation"], name="error_phi").sort_values()
phi.to_frame()'''),
        ("md", "## Diversity (H2) — descriptive only"),
        ("code", '''\
H2 = R["hypotheses"]["H2"]
pd.Series({k: v for k, v in H2.items() if not isinstance(v, (list, dict))}).to_frame("H2")'''),
        ("code", 'pd.DataFrame(H2["mean_gain_by_provider_count"]).T'),
        ("md", "**INTERPRETATION.** Gain tracks how often members fail on the *same* case (Spearman −0.83 with the "
               "double-fault rate) far more than provider count (−0.18). The second provider available was a much "
               "weaker local model, so provider count is confounded with member strength. The 35 combinations overlap "
               "and are not independent samples."),
        ("md", "## The critic was right and outvoted (EXPLORATORY)"),
        ("code", '''\
calls = final_calls("council/member_calls.jsonl")
truth = pd.DataFrame(load("council/cases.json")["cases"]).set_index("case_id")
b1 = calls[calls.member.isin(["haiku_verifier", "haiku_domain", "haiku_critic"])].pivot(index="case_id", columns="member", values="answer")
b1["truth"] = truth.answer
b1["split"] = truth.split
crit_right = b1[(b1.haiku_critic == b1.truth) & ((b1.haiku_verifier != b1.truth) & (b1.haiku_domain != b1.truth))]
crit_right'''),
        ("md", "On these cases plurality voting discarded the one correct dissent. A *protective-minority veto* is a "
               "hypothesis for a new pre-registration; it is `NOT_IMPLEMENTED` and `NOT_RUN`."),
        ("code", 'print("reproducibility:", R["system_quality"]["reproducibility_haiku_T1_two_samples"])\nprint("validator agreement:", R["system_quality"]["validator_agreement"])\nprint("organization context:", R["system_quality"]["organization_context_use"])'),
    ],
)

BOOKS["04_react_reflexion_pot"] = nb(
    "04 — ReAct, Reflexion and Program-of-Thought",
    "Status of three agentic patterns. None of them has a frozen benchmark result. " + LEGEND,
    [
        ("code", 'pd.DataFrame([status_row(m) for m in ("react", "reflexion", "pot-evidence")]).T'),
        ("code", '''\
for m in ("react", "reflexion", "pot-evidence"):
    r = REG[m]
    print(f"{r['name']}\\n  definition: {r['definition']}\\n  runtime: {r['runtime']}\\n  next step: {r['next_step']}\\n")'''),
        ("md", "**RESULT.**\n\n* **ReAct** — `NOT_IMPLEMENTED`. Natural-language orchestration in Athena is a deterministic "
               "intent planner; there is no reason-act tool loop. `NOT_RUN`.\n* **Reflexion** — one diagnose-and-retry "
               "step is wired (advisory, API only). It is not iterative Reflexion and has never been evaluated: "
               "`NOT_RUN`.\n* **Program-of-Thought / evidence enforcement** — wired: numbers in validated reports come "
               "from canonical computation, and the model only explains them. Coverage is partial (some narrative "
               "surfaces are not checked number by number). No ablation measures its effect: `NOT_RUN`.\n\nNo accuracy, "
               "cost or latency figure is claimed for any of the three."),
    ],
)

BOOKS["05_mcts_feature_strategy"] = nb(
    "05 — MCTS for feature strategy",
    "Monte-Carlo Tree Search over feature/pipeline strategies. " + LEGEND,
    [
        ("code", 'pd.DataFrame([status_row("mcts")]).T'),
        ("code", 'print(REG["mcts"]["limitations"])\nprint(REG["mcts"]["next_step"])'),
        ("md", "**RESULT.** `NOT_IMPLEMENTED`, `NOT_RUN`. No implementation exists, and no result is claimed. "
               "Scope for any future study: a strategy-level comparison only (which feature families to try, in what "
               "order) against the existing deterministic search and the HPO engine as baselines. Re-implementing "
               "hyper-parameter optimisation is out of scope. The research plan is recorded in `METHODOLOGY.md` with "
               "roadmap state `RESEARCH_PLANNED`."),
    ],
)

BOOKS["06_cost_latency_calibration"] = nb(
    "06 — Cost, latency and calibration",
    "Economics of every council condition and confidence calibration of every member. Cost is the provider-reported "
    "cost per call (MEASURED); local models report 0. Latency of a council is the slowest member plus the judge where "
    "used (ESTIMATED from measured per-call latency: members are assumed to run in parallel). " + LEGEND,
    [
        ("code", '''\
order = ["A_solo:sonnet", "A_solo:haiku", "B1_same_provider_roles", "B2_same_provider_sampling", "C_multi_provider",
         "D_characteristic_diverse", "E_judge", "F_adaptive_routing"]
base = R["conditions"]["A_solo:sonnet"]
econ = pd.DataFrame([{"condition": k, "accuracy": R["conditions"][k]["accuracy"],
                      "calls": R["conditions"][k]["calls_per_decision"], "tokens": R["conditions"][k]["tokens_per_decision"],
                      "latency_s": R["conditions"][k]["latency_s_per_decision"], "cost_usd": R["conditions"][k]["cost_usd_per_decision"]}
                     for k in order]).set_index("condition")
econ["tokens_x_solo"] = (econ.tokens / base["tokens_per_decision"]).round(2)
econ["latency_x_solo"] = (econ.latency_s / base["latency_s_per_decision"]).round(2)
econ["cost_x_solo"] = (econ.cost_usd / base["cost_usd_per_decision"]).round(2)
econ.to_csv(EV.parent / "evidence" / "council" / "cost_latency_by_condition.csv")
econ'''),
        ("code", '''\
recorded = pd.concat([pd.DataFrame(jsonl("council/member_calls.jsonl")), pd.DataFrame(jsonl("council/judge_calls.jsonl"))])
calls = final_calls("council/member_calls.jsonl")
print("recorded calls (incl. re-asked):", len(recorded), "| analysed member answers:", len(calls))
allc = recorded
per_member = allc.groupby("member").agg(calls=("case_id", "size"), tokens_in=("tokens_in", "sum"), tokens_out=("tokens_out", "sum"),
                                        cost_usd=("cost_usd", "sum"), latency_p50=("latency_s", "median"),
                                        latency_p95=("latency_s", lambda s: s.quantile(0.95)), retries=("retries", "sum"))
arch = pd.DataFrame(jsonl("council/member_calls_budget300_archive.jsonl"))
# The archive is the pre-Amendment-2 file: its rows are the first rows of the final cache, not extra calls.
assert jsonl("council/member_calls_budget300_archive.jsonl") == jsonl("council/member_calls.jsonl")[:len(arch)]
print("distinct recorded calls:", len(allc), "| provider-reported cost of all of them (USD):",
      round(float(allc.cost_usd.fillna(0).sum()), 4))
print("note: adding the archive again would double-count", len(arch), "calls (USD",
      round(float(arch.cost_usd.fillna(0).sum()), 4), ")")
per_member.round(4)'''),
        ("md", "## Calibration (EXPLORATORY — not pre-registered)\n\nExpected calibration error over 10 equal-width "
               "confidence bins and Brier score of the stated confidence for the chosen option, on the evaluation split. "
               "Computed here from the frozen answers; an abstention counts as wrong with confidence 0."),
        ("code", '''\
truth = pd.DataFrame(load("council/cases.json")["cases"]).set_index("case_id")
ev = calls[calls.case_id.map(truth.split) == "evaluation"].copy()
ev["correct"] = (ev.answer == ev.case_id.map(truth.answer)).astype(float)
ev["conf"] = ev.confidence.fillna(0.0).clip(0, 1)


def ece(df, bins=10):
    idx = np.minimum((df.conf * bins).astype(int), bins - 1)
    return float(sum(abs(g.correct.mean() - g.conf.mean()) * len(g) for _, g in df.groupby(idx)) / len(df))


cal = pd.DataFrame([{"member": m, "n": len(g), "accuracy": g.correct.mean(), "mean_confidence": g.conf.mean(),
                     "ece": ece(g), "brier": float(((g.conf - g.correct) ** 2).mean())} for m, g in ev.groupby("member")]).set_index("member")
cal.to_csv(EV / "council" / "calibration_by_member.csv")
cal.round(3)'''),
        ("md", "**RESULT.** Always-on councils cost 3–4 calls, 2.7–4.5× tokens, up to 2.3× latency (judge) and up to 2.5× "
               "provider cost of the strong solo model for no accuracy gain on this set. A solo Haiku matched the strong "
               "solo accuracy at about 1/15 of its cost per decision. Calibration figures are exploratory and describe "
               "this case set only.\n\n**UNKNOWN:** cost of Jev calls (no price reported), latency on a production "
               "network path, prompt-cache effects (Hermes-style stable prefix — `NOT_RUN`)."),
    ],
)

BOOKS["07_results_and_recommendations"] = nb(
    "07 — Results and recommendations",
    "One table across every method, then what is and is not recommended. " + LEGEND,
    [
        ("code", '''\
ids = ["deterministic-baseline", "single-strong-model", "council", "proposer-judge", "critic-veto", "cot", "tot", "got",
       "self-consistency", "react", "reflexion", "pot-evidence", "mcts", "jev", "agentic-llm-decision", "hermes-agent-patterns"]
summary = pd.DataFrame([status_row(i) for i in ids]).set_index("method")
summary.to_csv(EV / "reasoning_methods" / "method_status_summary.csv")
summary[["implemented", "wired", "authority", "evaluation", "production", "recommendation"]]'''),
        ("code", 'pd.Series(R["decisions"], name="council decision (pre-registered rule)").to_frame()'),
        ("md", "## Recommendations\n\n1. **Default path:** a single strong model plus deterministic checks and the "
               "evidence validator. Measured: no council beat it on this set.\n2. **Council:** not a default. "
               "`REJECTED_ON_THIS_BENCHMARK`; the next study must first show solo headroom (≥ 15 % error on calibration) "
               "or stop as `NOT_RUN — CEILING`.\n3. **Critic veto:** the most promising hypothesis (the critic was right "
               "and outvoted); it needs its own pre-registration before any claim.\n4. **CoT / ToT / GoT:** confidence "
               "and tie-break behaviour only; no real-provider measurement. No capability claim.\n5. **ReAct, MCTS, "
               "self-consistency:** not implemented. **Reflexion, PoT:** wired, not evaluated.\n6. **Jev:** measured on "
               "one decision family; gain with semantics not established (intervals overlap); cost unknown.\n\nEvery "
               "untested method is recorded as `RESEARCH_PLANNED` with a hypothesis, baseline, metric, budget, "
               "stopping rule and production gate (`METHODOLOGY.md`). None is presented as a product capability."),
        ("md", "## Limitations\n\nCeiling effect (70/71); two provider families, the second much weaker; harness calls "
               "models directly (not the product path, no validator, no tenant context); one provider-enforced "
               "temperature; the case author is also the harness author. See `LIMITATIONS.md`."),
    ],
)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, book in BOOKS.items():
        nbformat.validate(book)
        nbformat.write(book, OUT / f"{name}.ipynb")
        print("wrote", f"notebooks/{name}.ipynb")


if __name__ == "__main__":
    main()
