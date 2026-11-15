"""Render METHODOLOGY.md from the pre-registration summary and evidence/reasoning_methods/research_plans.json."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HEAD = """# Methodology

## Completed study: council ablation (2026-11-04)

* **Pre-registration.** Hypotheses H0–H3, conditions A–F, the calibration/evaluation split (every third case per
  family is calibration), metrics and decision rules were committed before the first model call:
  [`protocol/PREREGISTRATION.md`](protocol/PREREGISTRATION.md). The two amendments were recorded before any result was read:
  [`protocol/AMENDMENTS.md`](protocol/AMENDMENTS.md).
* **Cases.** 110 closed-answer cases in nine families ([`evidence/council/cases.json`](evidence/council/cases.json)). Ground truth comes from
  public dataset documentation or from a rule stated in the case; no label is produced by a model.
* **Members.** Claude Sonnet 5.5 and Haiku 5.5 (temperature 1, provider-enforced), local Qwen 2.5 7B and 1.5B
  (temperature 0, Q4_K_M). One cached answer per member and case; the last cached row is the analysed one.
* **Aggregation.** Plurality, ties broken by mean confidence. An unparseable answer is an abstention.
* **Statistics.** 95 % paired bootstrap CIs, 2 000 resamples, seed 11, on the 71 evaluation cases.
* **Decision rules.** SUPPORTED / CONDITIONAL_VALUE / REJECTED / INSUFFICIENT_EVIDENCE, as pre-registered.
* **Exploratory, labelled as such.** The critic-outvoted observation (notebook 03) and the calibration table
  (notebook 06) were not pre-registered.

## Labels

* **MEASURED** — produced by a real provider call or a real run.
* **ESTIMATED** — derived from measured data by a stated formula (for example council latency = slowest
  member + judge).
* **SIMULATED** — produced by a mock runner; never a quality result.
* **NOT_RUN** — no result exists.
* **UNKNOWN** — the evidence does not say.

Implementation and wiring are reported separately from evaluation: code that exists is not a measured capability.

## Planned research (`RESEARCH_PLANNED`)

None of the methods below is an Athena capability or production feature. No performance claim is made for a
method that has not been run. Paid calls start only after the budget is approved.

**Prior evidence in this repository.** "Not run" below means not run on the council case set or in the product. Two
of the methods have measured results on a different task family elsewhere in this repository:
* CoT, ToT and GoT as reasoning orchestration were measured on bounded AutoML decisions in
  [Study A](../reasoning-topology/original-study/) and [Study A2](../reasoning-topology/frontier-replication/). No
  topology beat a direct answer.
* Bounded-decision routing to a typed model was measured in the [JEV retrospective](../jev/).

Those results do not transfer to the council governance cases by assumption. Each plan below states its own baseline
and gate.

"""


def main() -> None:
    plans = json.loads((ROOT / "evidence/reasoning_methods/research_plans.json").read_text())
    parts = [HEAD]
    for p in plans["plans"]:
        parts.append(f"### {p['method']} — `{p['id']}`\n\n"
                     + "\n".join(f"* **{label}.** {p[key]}" for label, key in (
                         ("Purpose", "purpose"), ("Hypothesis", "hypothesis"), ("Baseline", "baseline"),
                         ("Dataset / task family", "dataset_task_family"), ("Metric", "metric"),
                         ("Budget", "budget"), ("Stopping rule", "stopping_rule"),
                         ("Production admission gate", "production_admission_gate"),
                         ("Current status", "current_status")))
                     + "\n")
    (ROOT / "METHODOLOGY.md").write_text("\n".join(parts))
    print("wrote METHODOLOGY.md with", len(plans["plans"]), "plans")


if __name__ == "__main__":
    main()
