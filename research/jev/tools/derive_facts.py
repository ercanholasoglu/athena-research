"""JEV article facts, derived from the evidence files in `../evidence/`.

    python research/jev/tools/derive_facts.py            # writes ../results/facts.json
    python research/jev/tools/derive_facts.py --check    # fails if the derivation differs from the committed facts

The four functions below are cut verbatim (Python `ast`, unmodified) from the article build script, which also
renders the article and its figures and is not part of this repository. Source script SHA-256:
aac071be85044f86969849420477d843097c88fec874cec8696c9dadc47242ff.
"""
from __future__ import annotations

import collections  # noqa: F401  (used by build_facts)
import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parents[1] / "evidence"
RESULT = Path(__file__).resolve().parents[1] / "results" / "facts.json"


def load(name):
    path = EVIDENCE / name
    if name.endswith(".jsonl"):
        return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    return json.loads(path.read_text())


def rnd(x, digits=1):
    """Round half away from zero, as the experiment reports do (−6.25 → −6.3)."""
    q = Decimal(1).scaleb(-digits)
    return float(Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP))


def pct(x):
    return rnd(100 * x)


def build_facts():
    a = load("jev-ablation-2026-10-21.json")
    b = load("jev-semantics-ablation-2026-10-21.json")
    cde = load("jev-generalization-cde-2026-10-21.json")
    manifest = load("decision-corpus-v2-manifest.json")
    cases = load("jev-generalization-cde-cases-2026-10-21.jsonl")
    an = cde["analysis"]
    fh = an["final_holdout"]

    f = {}
    # ---- A/B on decision-corpus-v1
    for t, key in (("EXPLANATION_MODE", "expl"), ("HPO_DEPTH", "hpo"), ("RETRY_FALLBACK", "retry")):
        comp = b["comparison_vs_experiment_a"][t]
        arms = b["results"][t]["arms"]
        f[f"ab.{key}.a"] = pct(comp["accuracy_raw"]["A"])
        f[f"ab.{key}.b"] = pct(comp["accuracy_raw"]["B"])
        f[f"ab.{key}.delta_pp"] = comp["accuracy_raw"]["delta_pp"]
        f[f"ab.{key}.ratio"] = round(comp["accuracy_raw"]["B"] / comp["accuracy_raw"]["A"], 2)
        f[f"ab.{key}.wilson_a"] = [pct(v) for v in comp["accuracy_raw"]["wilson95_A"]]
        f[f"ab.{key}.wilson_b"] = [pct(v) for v in comp["accuracy_raw"]["wilson95_B"]]
        f[f"ab.{key}.overlap"] = comp["accuracy_raw"]["intervals_overlap"]
        f[f"ab.{key}.n"] = comp["n"]
        f[f"ab.{key}.local"] = pct(arms["local_bounded"]["accuracy_raw"])
        f[f"ab.{key}.rules"] = pct(arms["deterministic"]["accuracy_raw"])
        f[f"ab.{key}.tokens_a"] = comp["input_tokens_per_call"]["A"]
        f[f"ab.{key}.tokens_b"] = comp["input_tokens_per_call"]["B"]
        f[f"ab.{key}.tokens_ratio"] = comp["input_tokens_per_call"]["ratio_B_over_A"]
        f[f"ab.{key}.ece_a"] = comp["ece"]["A"]
        f[f"ab.{key}.ece_b"] = comp["ece"]["B"]
        # The same rules/local numbers were re-run inside experiment A.
        assert a["results"][t]["arms"]["local_bounded"]["accuracy_raw"] == arms["local_bounded"]["accuracy_raw"]
    tok = b["token_accounting"]
    f["ab.tokens_a"] = tok["A"]["input_tokens_per_call"]
    f["ab.tokens_b"] = tok["B"]["input_tokens_per_call"]
    f["ab.tokens_ratio"] = tok["input_ratio_B_over_A"]
    f["ab.cases"] = tok["A"]["evaluated_calls"]
    f["a.calls"] = a["jev_calls"]
    f["b.calls"] = b["jev_calls"]
    f["a.hpo_mean_conf"] = round(a["results"]["HPO_DEPTH"]["arms"]["jev"]["mean_confidence"], 2)

    # ---- C/D/E on decision-corpus-v2
    f["v2.datasets"] = cde["benchmark"]["datasets"]
    f["v2.dev"] = len(cde["benchmark"]["development"])
    f["v2.holdout"] = len(cde["benchmark"]["final_holdout"])
    f["v2.holdout_names"] = cde["benchmark"]["final_holdout"]
    f["v2.calls"] = cde["calls"]["total"]
    f["v2.input_tokens"] = sum(cde["input_tokens"].values())
    f["v2.output_tokens"] = sum(cde["output_tokens"].values())
    f["v2.model"] = cde["model"]["resolved"][0]
    f["v2.bootstrap"] = an["pre_registered"]["bootstrap"]
    f["v2.tests"] = len(an["pre_registered"]["family"])
    f["v2.max_p_holm"] = max(v["p_holm"] for v in an["holm"].values())
    f["v2.min_p_holm"] = min(v["p_holm"] for v in an["holm"].values())
    f["v2.significant"] = sum(v["significant"] for v in an["holm"].values())
    rows = [d for d in manifest["datasets"]]
    f["v2.feat_min"] = min(d["raw_columns"] for d in rows)
    f["v2.feat_max"] = max(d["raw_columns"] for d in rows)
    f["v2.rows_min"] = min(d["rows"] for d in rows)
    f["v2.rows_max"] = max(d["rows"] for d in rows)
    tasks = collections.Counter(d["task"] for d in rows)
    f["v2.binary"], f["v2.multiclass"] = tasks["binary"], tasks["multiclass"]
    for t, key in (("EXPLANATION_MODE", "expl"), ("HPO_DEPTH", "hpo")):
        cc = cde["benchmark"]["case_counts"][t]
        f[f"v2.{key}.total"], f[f"v2.{key}.dev_cases"], f[f"v2.{key}.final_cases"] = cc["total"], cc["development"], cc["final_holdout"]
        acc = fh[t]["accuracy"]
        for m in ("rules", "local_bounded", "local_bounded_v2dev", "jev_B", "jev_C", "jev_D", "jev_E"):
            f[f"v2.{key}.{m}"] = pct(acc[m]["macro"])
            f[f"v2.{key}.{m}.ci"] = [pct(v) for v in acc[m]["macro_ci95"]]
            assert acc[m]["macro"] == acc[m]["micro"], "8 cases per dataset: macro == micro"
        for m in ("local_bounded", "local_bounded_v2dev", "jev_B", "jev_C", "jev_D", "jev_E"):
            cal = fh[t]["calibration"][m]
            f[f"v2.{key}.{m}.ece"] = round(cal["ece"], 3)
            f[f"v2.{key}.{m}.conf"] = round(cal["mean_confidence"], 2)
        for m in ("jev_B", "jev_C", "jev_D", "jev_E"):
            ops = fh[t]["operations"][m]
            f[f"v2.{key}.{m}.tokens"] = ops["input_tokens_per_case"]
            f[f"v2.{key}.{m}.out_tokens"] = ops["output_tokens_per_case"]
            f[f"v2.{key}.{m}.p50"] = ops["latency_ms_p50"]
            f[f"v2.{key}.{m}.calls"] = ops["provider_calls"]
            f[f"v2.{key}.{m}.mult"] = round(ops["input_tokens_per_case"] / fh[t]["operations"]["jev_B"]["input_tokens_per_case"], 2)
        for m in ("jev_C", "jev_D", "jev_E"):
            cls = fh[t]["classification"][m]["vs_B"]
            f[f"v2.{key}.{m}.vs_b"] = rnd(100 * cls["estimate"])
            f[f"v2.{key}.{m}.vs_b.ci"] = [rnd(100 * v) for v in cls["ci95"]]
        vs_local = fh[t]["classification"]["jev_B"]["vs_local"]
        f[f"v2.{key}.b_vs_local"] = rnd(100 * vs_local["estimate"])
        f[f"v2.{key}.b_vs_local.ci"] = [rnd(100 * v) for v in vs_local["ci95"]]
        f[f"v2.{key}.per_dataset"] = fh[t]["per_dataset"]
        f[f"v2.{key}.labels"] = fh[t]["label_distribution"]
        f[f"v2.{key}.mcnemar"] = fh[t]["mcnemar"]
        f[f"v2.{key}.lodo"] = fh[t]["lodo"]
    per_e, per_h = f["v2.expl.per_dataset"], f["v2.hpo.per_dataset"]
    f["v2.expl.v2dev.min"] = pct(min(per_e["local_bounded_v2dev"].values()))
    f["v2.expl.v2dev.n100"] = sum(v == 1.0 for v in per_e["local_bounded_v2dev"].values())
    f["v2.expl.v2dev.n_rest"] = len(per_e["local_bounded_v2dev"]) - f["v2.expl.v2dev.n100"]
    f["v2.expl.shipped.min"] = pct(min(per_e["local_bounded"].values()))
    f["v2.expl.shipped.max"] = pct(max(per_e["local_bounded"].values()))
    f["v2.hpo.v2dev.vehicle"] = pct(per_h["local_bounded_v2dev"]["vehicle"])
    f["v2.const.expl"] = pct(cde["reference_dev_majority"]["EXPLANATION_MODE"]["macro"])
    f["v2.const.hpo"] = pct(cde["reference_dev_majority"]["HPO_DEPTH"]["macro"])
    rep = an["reproducibility"]
    f["v2.repeat_same"] = round(sum(r["answer_agreement"] * r["cases"] for r in rep.values()))
    f["v2.repeat_total"] = sum(r["cases"] for r in rep.values())

    # ---- per-case facts (final holdout only)
    final = [c for c in cases if c["phase"] == "final"]
    expl = [c for c in final if c["decision_type"] == "EXPLANATION_MODE"]
    hpo = [c for c in final if c["decision_type"] == "HPO_DEPTH"]
    jev = ("jev_B", "jev_C", "jev_D", "jev_E")
    f["case.expl.skip_needed"] = sum(c["ground_truth"] == "SKIP" for c in expl)
    f["case.expl.skip_chosen"] = sum(c["methods"][m]["prediction"] == "SKIP" for c in expl for m in jev)
    correct = {m: frozenset(c["case_id"] for c in expl if c["methods"][m]["correct"]) for m in jev + ("rules",)}
    f["case.expl.same_correct_set"] = len({correct[m] for m in jev}) == 1
    f["case.expl.same_as_rules"] = correct["jev_B"] == correct["rules"]
    f["case.expl.correct"] = len(correct["jev_B"])
    f["case.expl.tree_shap_preds_B"] = sum(c["methods"]["jev_B"]["prediction"] == "TREE_SHAP_EXACT" for c in expl)
    linear = [c for c in expl if c["context"].get("model_family") == "linear"]
    f["case.expl.linear"] = len(linear)
    f["case.expl.linear_skip"] = sum(c["ground_truth"] == "SKIP" for c in linear)
    f["case.expl.linear_perm_B"] = sum(c["methods"]["jev_B"]["prediction"].startswith("PERMUTATION") for c in linear)
    f["case.hpo.E_light"] = sum(c["methods"]["jev_E"]["prediction"] == "LIGHT" for c in hpo)
    for m in jev:
        f[f"case.hpo.{m}.light"] = sum(c["methods"][m]["prediction"] == "LIGHT" for c in hpo)
    f["case.hpo.light_share"] = pct(sum(c["ground_truth"] == "LIGHT" for c in hpo) / len(hpo))
    f["case.v2dev.expl_skip_preds"] = sum(c["methods"]["local_bounded_v2dev"]["prediction"] == "SKIP" for c in expl)
    return f


def main() -> None:
    facts = build_facts()
    text = json.dumps(facts, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        if json.loads(RESULT.read_text()) != json.loads(text):
            sys.exit("JEV facts differ from results/facts.json")
        print("JEV facts OK", len(facts), "keys")
        return
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(text)
    print("wrote", RESULT.name, len(facts), "keys")


if __name__ == "__main__":
    main()
