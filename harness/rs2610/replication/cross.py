"""Cross-study question (PREREGISTRATION.md section 8): capability, structure and semantics effects side by side.

    python -m rs2610.replication.cross    # -> outputs/replication/cross-study.csv

Written after the freeze, from the A2/B2 result tables:
* capability: frontier - baseline. A2 DIRECT accuracy (row of a2-model-effect.csv); B2 trapped:A_RAW core semantic
  accuracy and all traps blocked, units (dataset, replicate) matched as in b2.analyze.model_effect;
* structure: best non-DIRECT topology - DIRECT within each model, A2 (row of a2-within-model.csv), "best" by accuracy;
* semantics: trapped:D_RULES - trapped:A_RAW within each model, B2, units matched as in b2.analyze.semantic_effect.
B2 CIs are a paired bootstrap over units (10,000 resamples). The scales differ, so the comparison is ordinal only.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from rs2610.replication.b2.analyze import BASELINE, sign_p

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "replication"
RNG = np.random.default_rng(20261029)
B2_METRICS = ("core_semantic_accuracy", "all_traps_blocked")


def paired(dec: pd.DataFrame, a: tuple[str, str], b: tuple[str, str], k: str) -> dict:
    """b - a over matched (dataset_id, seed) units; a and b are (model, cell)."""
    sa = dec[(dec.model == a[0]) & (dec.cell == a[1])].set_index(["dataset_id", "seed"])[k]
    sb = dec[(dec.model == b[0]) & (dec.cell == b[1])].set_index(["dataset_id", "seed"])[k]
    j = pd.concat([sa.rename("a"), sb.rename("b")], axis=1, join="inner").dropna().astype(float)
    d = (j.b - j.a).to_numpy()
    boot = d[RNG.integers(0, len(d), size=(10000, len(d)))].mean(axis=1)
    return {"n_units": len(d), "effect": float(d.mean()), "ci_lo": float(np.quantile(boot, 0.025)),
            "ci_hi": float(np.quantile(boot, 0.975)), "p": sign_p(d), "p_kind": "exact sign, unadjusted"}


def main() -> None:
    rows = []
    me = pd.read_csv(OUT / "a2" / "a2-model-effect.csv")
    for _, r in me[me["mode"] == "DIRECT"].iterrows():
        rows.append({"axis": "capability", "study": "A2", "model": r.frontier, "metric": "accuracy", "contrast": "frontier - baseline, DIRECT",
                     "n_units": int(r.n_pairs), "effect": r.effect_b_minus_a, "ci_lo": r.ci_lo, "ci_hi": r.ci_hi, "p": r.p_holm,
                     "p_kind": "McNemar, Holm across 4 topologies"})
    wm = pd.read_csv(OUT / "a2" / "a2-within-model.csv")
    for m, g in wm[wm.a == "DIRECT"].groupby("model"):
        r = g.sort_values(["acc_b", "b"], ascending=[False, True]).iloc[0]
        rows.append({"axis": "structure", "study": "A2", "model": m, "metric": "accuracy", "contrast": f"{r.b} - DIRECT (best non-DIRECT)",
                     "n_units": int(r.n_pairs), "effect": r.effect_b_minus_a, "ci_lo": r.ci_lo, "ci_hi": r.ci_hi, "p": r.p_holm,
                     "p_kind": "McNemar, Holm across 6 contrasts"})
    dec = pd.read_csv(OUT / "b2" / "b2-run-level.csv")
    for m in sorted(set(dec.model) - {BASELINE}):
        for k in B2_METRICS:
            rows.append({"axis": "capability", "study": "B2", "model": m, "metric": k, "contrast": "frontier - baseline, trapped:A_RAW",
                         **paired(dec, (BASELINE, "trapped:A_RAW"), (m, "trapped:A_RAW"), k)})
    for m in sorted(set(dec.model)):
        for k in B2_METRICS:
            rows.append({"axis": "semantics", "study": "B2", "model": m, "metric": k, "contrast": "trapped:D_RULES - trapped:A_RAW",
                         **paired(dec, (m, "trapped:A_RAW"), (m, "trapped:D_RULES"), k)})
    pd.DataFrame(rows).to_csv(OUT / "cross-study.csv", index=False)
    print(pd.DataFrame(rows).round(3).to_string())


if __name__ == "__main__":
    main()
