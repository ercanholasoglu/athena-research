"""EXPLORATORY sensitivity analysis for Study B UNSEEN (added after the freeze; not part of FREEZE_RECORD_B).

Reason (JOURNAL 2026-10-28 ~13:00): on `coil_caravan` (86 columns) two UNSEEN calls hit their token caps — A_RAW s1 lost
its FE stage, E_FULL s2 lost its verification stage and degenerated into a D_RULES run. The confirmatory analysis keeps
them as pre-registered failures. This script reruns the *frozen* paired test (`analyze.paired_vs_raw`, unchanged) with
`coil_caravan` excluded and reports, per confirmatory metric x condition, whether the Holm-adjusted verdict at 0.05
changes.

    python -m rs2610.study_b.sensitivity    # reads outputs/study_b/semantic-decisions.csv, writes study-b-sensitivity.csv
"""
from __future__ import annotations

import pandas as pd

from rs2610.study_b.analyze import OUT, paired_vs_raw

EXCLUDE = ["coil_caravan"]
CONFIRMATORY = ["core_semantic_accuracy", "all_traps_blocked", "leak_recall", "candidate_accuracy", "feature_valid_share",
                "deploy_collapse", "deploy_gap_to_oracle"]


def main() -> None:
    dec = pd.read_csv(OUT / "semantic-decisions.csv")
    full = paired_vs_raw(dec, "UNSEEN")
    sens = paired_vs_raw(dec[~dec.dataset_id.isin(EXCLUDE)], "UNSEEN")
    key = ["metric", "condition"]
    m = full[key + ["n_pairs", "diff", "ci_lo", "ci_hi", "wilcoxon_p", "holm_p"]].merge(
        sens[key + ["n_pairs", "diff", "ci_lo", "ci_hi", "wilcoxon_p", "holm_p"]], on=key, suffixes=("_primary", "_excl"))
    m = m[m.metric.isin(CONFIRMATORY)].copy()
    m.insert(0, "excluded", ",".join(EXCLUDE))
    m["verdict_primary"] = m.holm_p_primary < 0.05
    m["verdict_excl"] = m.holm_p_excl < 0.05
    m["verdict_changes"] = m.verdict_primary != m.verdict_excl
    m["sign_changes"] = (m.diff_primary > 0) != (m.diff_excl > 0)
    m["status"] = "EXPLORATORY (post-freeze sensitivity)"
    m.to_csv(OUT / "study-b-sensitivity.csv", index=False)
    pd.set_option("display.width", 250)
    print(m[key + ["diff_primary", "holm_p_primary", "diff_excl", "holm_p_excl", "verdict_changes", "sign_changes"]].round(3).to_string())


if __name__ == "__main__":
    main()
