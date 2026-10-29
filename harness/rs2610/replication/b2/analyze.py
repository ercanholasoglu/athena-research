"""Study B2 analysis, written after the freeze to PREREGISTRATION.md section 7 and amendment 2 (deviations listed in the
report).

    python -m rs2610.replication.b2.analyze

Semantic decisions are scored by the frozen ``study_b.score.score`` against the B2 truth (frozen traps + the target-
derived column). Invented features and the frozen-FE proposals go through ``replication.b2.evaluate.validate``.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest, wilcoxon

from rs2610.replication.b2 import evaluate as ev
from rs2610.replication.b2.invention import INVENT_SCHEMA
from rs2610.replication.b2.variants import CELLS, TD_COL
from rs2610.study_b.analyze import CORE
from rs2610.study_b.conditions import FE_SCHEMA
from rs2610.study_b.profile import profile
from rs2610.study_b.score import score

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts" / "replication" / "b2"
OUT = ROOT / "outputs" / "replication" / "b2"
RNG = np.random.default_rng(20261029)
B = 10000
BASELINE = "qwen2.5:7b"
INV_MAX = INVENT_SCHEMA["properties"]["features"]["maxItems"]
FE_MAX = FE_SCHEMA["properties"]["proposed_features"]["maxItems"]
CELL_NAME = {c: f"{c[0]}:{c[1]}" for c in CELLS}
KEY = ["core_semantic_accuracy", "all_traps_blocked", "frozen_traps_blocked", "target_derived_caught", "id_trap_caught",
       "artifact_caught", "post_event_recall", "lever_actionable", "lever_is_predictive_trap", "falsified_detected_recall",
       "false_contradictions", "missing_semantics_recall", "candidate_accuracy", "inv_n", "inv_executable_share",
       "inv_valid_useful_share", "inv_valid_share", "inv_invalid_high_apparent_share", "inv_leaky_share",
       "inv_selfassess_missed_leak_share", "inv_multi_column_share", "inv_spec_mismatch_share", "inv_best_test_gain",
       "fe_valid_useful_share", "deploy_collapse", "deploy_gap_to_oracle", "leak_inflation", "cost_usd", "output_tokens"]


def strongest_non_actionable(did: str) -> str | None:
    st = ev.setup(did)
    v = st["v"]
    t = v.truth
    skip = set(t["ids_all"]) | set(t["leak_all"]) | set(t.get("actionable", []))
    rows = [r for r in profile(v, st["dev"]) if r["column"] not in skip and r["target_association"] is not None]
    return max(rows, key=lambda r: r["target_association"])["column"] if rows else None


def load() -> list[dict]:
    rows = []
    for prov in ("local", "openai", "anthropic"):
        p = ART / f"runs_{prov}.jsonl"
        if p.exists():
            rows += [json.loads(line) for line in p.read_text().splitlines()]
    return rows


def process(rows: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame]:
    dec, feats = [], []
    for r in rows:
        did = r["dataset_id"]
        st = ev.setup(did)
        v = st["v"]
        rename = r.get("rename") or {}
        s = score(r, v.truth, list(v.frame.columns), strongest_non_actionable(did))
        blocked = set(s.pop("_blocked"))
        s.pop("_lever")
        frozen_leak = set(v.truth["leak_all"]) - {TD_COL}
        s["target_derived_caught"] = TD_COL in blocked
        s["frozen_traps_blocked"] = set(v.truth["ids_all"]) <= blocked and frozen_leak <= blocked
        s["core_semantic_accuracy"] = float(np.mean([float(s[c]) for c in CORE]))
        inv = (r.get("invention") or {}).get("features") or []
        inv = inv[:INV_MAX]
        cls, kept = [], []
        for k, f in enumerate(inv):
            spec = f.get("spec") or {}
            val = ev.validate(did, spec, rename)
            src = {rename.get(str(c), str(c)) for c in (f.get("source_columns") or [])}
            ins = set(val["inputs"])
            leaky = bool(val.get("leakage"))
            cls.append(val["class"])
            feats.append({"model": r["model"], "dataset_id": did, "variant": r["variant"], "condition": r["condition"], "seed": r["seed"],
                          "source": "invention", "k": k, "feature_name": f.get("feature_name"), "op": val["op"], "inputs": "|".join(val["inputs"]),
                          "class": val["class"], "leakage": "|".join(val.get("leakage", [])), "semantic_validity": val["semantic_validity"],
                          "cv_gain": val.get("cv_gain"), "test_gain_deploy": val.get("test_gain_deploy"), "stability": val.get("stability"),
                          "missing_share": val.get("missing_share"), "redundancy": val.get("redundancy_max_spearman"),
                          "model_leakage_assessment": f.get("leakage_assessment"), "expected_stability": f.get("expected_stability"),
                          "spec_mismatch": src != ins, "multi_column": len(ins) >= 2,
                          "selfassess_missed_leak": leaky and f.get("leakage_assessment") == "none",
                          "semantic_rationale": f.get("semantic_rationale"), "business_interpretation": f.get("business_interpretation"),
                          "actionability": f.get("actionability")})
            if val.get("executable") and f.get("leakage_assessment") != "likely":
                kept.append({k2: val[k2] for k2 in ("op", "inputs", "threshold", "value")})
        fe_cls = []
        for f in ((r["trace"].get("fe") or {}).get("proposed_features") or [])[:FE_MAX]:
            val = ev.validate(did, {"op": f.get("op"), "inputs": f.get("inputs")}, rename)
            fe_cls.append(val["class"])
            feats.append({"model": r["model"], "dataset_id": did, "variant": r["variant"], "condition": r["condition"], "seed": r["seed"],
                          "source": "frozen_fe", "feature_name": f.get("name"), "op": val["op"], "inputs": "|".join(val["inputs"]),
                          "class": val["class"], "leakage": "|".join(val.get("leakage", [])), "cv_gain": val.get("cv_gain"),
                          "test_gain_deploy": val.get("test_gain_deploy"), "model_leakage_assessment": f.get("leakage_assessment")})
        fi = [x for x in feats if x["source"] == "invention" and x["model"] == r["model"] and x["dataset_id"] == did
              and x["variant"] == r["variant"] and x["condition"] == r["condition"] and x["seed"] == r["seed"]]
        n = len(inv)
        share = lambda pred: (sum(pred(x) for x in fi) / n) if n else np.nan  # noqa: E731
        down = ev.downstream(did, sorted(blocked), kept)
        s.update({
            "model": r["model"], "provider": r.get("provider"), "dataset_id": did, "variant": r["variant"], "condition": r["condition"],
            "cell": f"{r['variant']}:{r['condition']}", "seed": r["seed"], "inv_n": n, "inv_failed": (r.get("invention") or {}).get("failure") is not None,
            "inv_executable_share": share(lambda x: x["class"] != "NOT_EXECUTABLE"),
            "inv_valid_useful_share": share(lambda x: x["class"] == "VALID_USEFUL"),
            "inv_valid_share": share(lambda x: x["class"] in ("VALID_USEFUL", "VALID_NOT_USEFUL")),
            "inv_invalid_high_apparent_share": share(lambda x: x["class"] == "INVALID_HIGH_APPARENT"),
            "inv_leaky_share": share(lambda x: bool(x["leakage"])),
            "inv_selfassess_missed_leak_share": share(lambda x: x["selfassess_missed_leak"]),
            "inv_multi_column_share": share(lambda x: x["multi_column"]),
            "inv_spec_mismatch_share": share(lambda x: x["spec_mismatch"]),
            "inv_best_test_gain": max((x["test_gain_deploy"] for x in fi if x["class"] in ("VALID_USEFUL", "VALID_NOT_USEFUL")
                                       and x["test_gain_deploy"] is not None), default=np.nan),
            "fe_valid_useful_share": (sum(c == "VALID_USEFUL" for c in fe_cls) / len(fe_cls)) if fe_cls else np.nan,
            "deploy_collapse": down["deploy_collapse"], "leak_inflation": down["leak_inflation"], "deploy_score": down["test_deploy"],
            "deploy_gap_to_oracle": ev.oracle(did) - down["test_deploy"],
            "cost_usd": r.get("cost_usd"), "cost_status": r.get("cost_status"), "reasoning_tokens": r.get("reasoning_tokens"),
            "output_tokens": (s.get("output_tokens") or 0) + ((r.get("invention") or {}).get("call", {}).get("output_tokens") or 0)
            if s.get("output_tokens") is not None else None})
        dec.append(s)
    return pd.DataFrame(dec), pd.DataFrame(feats)


def dboot(g: pd.DataFrame, col: str) -> tuple[float, float, float]:
    d = g.dropna(subset=[col])
    if d.empty:
        return (np.nan, np.nan, np.nan)
    groups = [x[col].astype(float).to_numpy() for _, x in d.groupby("dataset_id")]
    est = float(d[col].astype(float).mean())
    bs = [np.mean(np.concatenate([groups[i] for i in RNG.integers(0, len(groups), len(groups))])) for _ in range(B)]
    return est, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def holm(p: list[float]) -> list[float]:
    order = np.argsort(p)
    adj = np.empty(len(p))
    run = 0.0
    for k, i in enumerate(order):
        run = max(run, min(1.0, (len(p) - k) * p[i])) if not np.isnan(p[i]) else run
        adj[i] = run if not np.isnan(p[i]) else np.nan
    return adj.tolist()


def sign_p(d: np.ndarray) -> float:
    pos, neg = int((d > 0).sum()), int((d < 0).sum())
    return float(binomtest(pos, pos + neg, 0.5).pvalue) if pos + neg else 1.0


def aggregates(dec: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (m, cell), g in dec.groupby(["model", "cell"]):
        row = {"model": m, "cell": cell, "n_runs": len(g)}
        for k in KEY:
            if k in g and g[k].notna().any():
                e, lo, hi = dboot(g, k)
                row.update({k: e, f"{k}_lo": lo, f"{k}_hi": hi})
        rows.append(row)
    return pd.DataFrame(rows)


def model_effect(dec: pd.DataFrame, frontier: str) -> pd.DataFrame:
    """B2-M: frontier - baseline per cell, units (dataset, replicate) matched; Holm across the 10 cells per metric."""
    rows = []
    for k in KEY[:-2]:
        rr = []
        for cell in [CELL_NAME[c] for c in CELLS]:
            a = dec[(dec.model == BASELINE) & (dec.cell == cell)].set_index(["dataset_id", "seed"])[k]
            b = dec[(dec.model == frontier) & (dec.cell == cell)].set_index(["dataset_id", "seed"])[k]
            j = pd.concat([a.rename("a"), b.rename("b")], axis=1, join="inner").dropna().astype(float)
            if j.empty:
                continue
            d = (j.b - j.a).to_numpy()
            rr.append({"frontier": frontier, "metric": k, "cell": cell, "n_units": len(j), "baseline": float(j.a.mean()),
                       "frontier_value": float(j.b.mean()), "effect": float(d.mean()), "p_sign": sign_p(d)})
        for r, ph in zip(rr, holm([r["p_sign"] for r in rr])):
            r["p_holm"] = ph
        rows += rr
    return pd.DataFrame(rows)


def semantic_effect(dec: pd.DataFrame) -> pd.DataFrame:
    """B2-S: within model, documentation conditions vs no documentation; Holm across the 4 contrasts per metric."""
    contrasts = [("trapped:C_DICT", "trapped:A_RAW"), ("trapped:D_RULES", "trapped:A_RAW"), ("trapped:E_FULL", "trapped:A_RAW"),
                 ("anonymized:C_DICT", "anonymized:A_RAW")]
    rows = []
    for m in dec.model.unique():
        for k in KEY[:-2]:
            rr = []
            for hi, lo in contrasts:
                a = dec[(dec.model == m) & (dec.cell == lo)].set_index(["dataset_id", "seed"])[k]
                b = dec[(dec.model == m) & (dec.cell == hi)].set_index(["dataset_id", "seed"])[k]
                j = pd.concat([a.rename("a"), b.rename("b")], axis=1, join="inner").dropna().astype(float)
                if j.empty:
                    continue
                d = (j.b - j.a).to_numpy()
                try:
                    pw = float(wilcoxon(d).pvalue) if np.any(d != 0) else 1.0
                except ValueError:
                    pw = 1.0
                rr.append({"model": m, "metric": k, "contrast": f"{hi} - {lo}", "n_units": len(j), "effect": float(d.mean()),
                           "p_sign": sign_p(d), "p_wilcoxon": pw})
            for r, ph in zip(rr, holm([r["p_sign"] for r in rr])):
                r["p_holm_sign"] = ph
            rows += rr
    return pd.DataFrame(rows)


def interaction(dec: pd.DataFrame, frontier: str) -> pd.DataFrame:
    """B2-X: (doc - A_RAW)_frontier - (doc - A_RAW)_baseline, sign-flip permutation over matched units."""
    rows = []
    for k in KEY[:-2]:
        for hi in ("trapped:C_DICT", "trapped:D_RULES"):
            w = dec[dec.cell.isin([hi, "trapped:A_RAW"])].pivot_table(index=["dataset_id", "seed"], columns=["model", "cell"], values=k)
            need = [(frontier, hi), (frontier, "trapped:A_RAW"), (BASELINE, hi), (BASELINE, "trapped:A_RAW")]
            if not all(c in w.columns for c in need):
                continue
            d = ((w[need[0]] - w[need[1]]) - (w[need[2]] - w[need[3]])).dropna().to_numpy()
            if not len(d):
                continue
            perm = (RNG.choice([-1.0, 1.0], size=(100000, len(d))) * d).mean(axis=1)
            rows.append({"frontier": frontier, "metric": k, "contrast": f"({hi} - A_RAW) frontier - baseline", "n_units": len(d),
                         "did": float(d.mean()), "p_perm": float((np.abs(perm) >= abs(d.mean()) - 1e-12).mean())})
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    dec, feats = process(load())
    dec.to_csv(OUT / "b2-run-level.csv", index=False)
    feats.to_csv(OUT / "b2-features.csv", index=False)
    agg = aggregates(dec)
    agg.to_csv(OUT / "b2-results.csv", index=False)
    frontiers = [m for m in dec.model.unique() if m != BASELINE]
    pd.concat([model_effect(dec, f) for f in frontiers]).to_csv(OUT / "b2-model-effect.csv", index=False)
    semantic_effect(dec).to_csv(OUT / "b2-semantic-effect.csv", index=False)
    pd.concat([interaction(dec, f) for f in frontiers]).to_csv(OUT / "b2-interaction.csv", index=False)
    feats.groupby(["model", "source", "class"]).size().unstack(fill_value=0).to_csv(OUT / "b2-feature-classes.csv")
    print(agg[["model", "cell", "n_runs", "core_semantic_accuracy", "all_traps_blocked", "target_derived_caught",
               "inv_valid_useful_share", "inv_leaky_share"]].round(3).to_string())


if __name__ == "__main__":
    main()
