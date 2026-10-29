"""Study B2 dataset variants: the frozen Study B traps plus one new trap, and the B2 condition grid.

``b2_base(ds)`` = frozen ``study_b.variants.trapped(ds)`` (identifier ``record_key``, a post-outcome column, the
``load_weekday`` warehouse artifact) plus a **target-derived** column:

* ``segment_outcome_rate``  the positive-outcome share of the row's micro-segment (about 8 rows, assigned at random),
                            computed on the whole extract, the row's own label included. Its association with the target
                            is an artifact of that computation; at prediction time the value can only come from
                            historical rows, which carries no information about the row's own outcome. Described
                            truthfully in the dictionary, like every Study B trap.

``anonymized`` / ``incomplete`` / ``misleading`` are the frozen Study B transforms applied to that base. False
dictionary entries for the two datasets the frozen ``MISLEAD`` table does not cover are added here (B2_MISLEAD), written
before the B2 freeze in the frozen pattern: two entries the profile contradicts and one post-outcome column disguised as a
harmless attribute.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from rs2610.common.data import SEED, Dataset
from rs2610.study_b import variants as frozen
from rs2610.study_b.variants import Variant, anonymized, incomplete, trapped

B2_DATASETS = ("iranian_churn", "taiwan_default", "bank_marketing", "hillstrom_email")
B2_REPLICATES = (1, 2)
TD_COL = "segment_outcome_rate"
TD_TEXT = ("Outcome rate of the customer's micro-segment: share of rows in the same segment with a positive outcome, computed by "
           "the analytics team on this extract")
SEGMENT_SIZE = 8

# (variant, condition) cells, identical for every dataset and model
CELLS = (("trapped", "A_RAW"), ("trapped", "B_SELF"), ("trapped", "C_DICT"), ("trapped", "D_RULES"), ("trapped", "E_FULL"),
         ("anonymized", "A_RAW"), ("anonymized", "C_DICT"),
         ("incomplete", "D_RULES"),
         ("misleading", "D_RULES"), ("misleading", "E_FULL"))

B2_MISLEAD = {
    "iranian_churn": {"Seconds_of_Use": "Customer age in years", "Age": "Total seconds of calls in the 9-month window",
                      "deactivation_reason": "Preferred language for billing statements"},
    "hillstrom_email": {"history": "Customer age in years", "recency": "Dollars spent in the past year",
                        "visit": "1 if the customer holds a store loyalty card"},
}


def segments(n: int) -> np.ndarray:
    return np.random.default_rng(SEED + 23).integers(0, max(1, n // SEGMENT_SIZE), n)


def _binary_target(v: Variant) -> np.ndarray:
    y = v.frame[v.target].to_numpy()
    return (y > np.median(y)).astype(float) if v.ds.task_type == "regression" else (y == 1).astype(float)


def b2_base(ds: Dataset) -> Variant:
    v = trapped(ds)
    df = v.frame.copy()
    seg = segments(len(df))
    yb = _binary_target(v)
    rate = pd.Series(yb).groupby(seg).transform("mean").to_numpy()
    cols = list(df.columns)
    df.insert(cols.index(v.target), TD_COL, np.round(rate, 3))
    truth = dict(v.truth)
    truth["target_derived_b2"] = [TD_COL]
    truth["post_outcome_all"] = sorted(set(truth["post_outcome_all"]) | {TD_COL})
    truth["leak_all"] = sorted(set(truth["leak_all"]) | {TD_COL})
    dictionary = {**v.dictionary, TD_COL: TD_TEXT}
    return Variant(ds, "trapped", df, v.target, dictionary, v.description, v.rules, v.codes, v.constraints, truth)


def deploy_value(base: Variant, dev_idx: np.ndarray, test_idx: np.ndarray) -> np.ndarray:
    """What ``segment_outcome_rate`` would be for test rows in deployment: the segment rate over development rows only."""
    seg = segments(len(base.frame))
    yb = _binary_target(base)
    hist = pd.Series(yb[dev_idx]).groupby(seg[dev_idx]).mean()
    return pd.Series(seg[test_idx]).map(hist).to_numpy(dtype=float)


def misleading(v: Variant) -> Variant:
    false = frozen.MISLEAD.get(v.ds.dataset_id) or B2_MISLEAD[v.ds.dataset_id]
    dictionary = {**v.dictionary, **false}
    return Variant(v.ds, "misleading", v.frame, v.target, dictionary, v.description, v.rules, v.codes, v.constraints, v.truth,
                   falsified=dict(false))


MAKERS = {"trapped": lambda v: v, "anonymized": anonymized, "incomplete": incomplete, "misleading": misleading}
