"""Dataset variants for Study B.

``trapped(ds)`` — every main-grid dataset carries three traps (B4 tests 5-7):

* ``record_key``         identifier assigned in target order during an extract (T5):
                         unique per row, strongly predictive, meaningless.
* a post-outcome column  inserted only where the dataset has no natural one (T6);
                         bank ``duration``, fraud ``chargeback_filed``, bike
                         ``casual``/``registered``, Hillstrom ``visit``/``spend`` are natural.
* ``load_weekday``       warehouse load weekday; positives were batch-loaded on
                         Fridays (T7): statistically attractive, semantically absurd.

Every trap is described *truthfully* in the dictionary — whether a model uses
that description is what the conditions measure.

``anonymized`` (T1), ``incomplete`` (T3) and ``misleading`` (T4) transform the
column names / dictionary on top of the trapped variant.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from rs2610.common.data import SEED, Dataset

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# inserted post-outcome column: name -> (generator(target, rng) , dictionary text)
INSERTED_POST = {
    "telco_churn": ("save_desk_outcome", "Outcome of the save-desk call made after the customer asked to cancel (none / accepted / declined)"),
    "german_credit": ("sent_to_collections", "1 if the loan was later handed to the collections department"),
    "adult_income": ("tax_bracket_filed", "Tax bracket on the return the person filed for the census year (low / middle / high)"),
    "iranian_churn": ("deactivation_reason", "Reason recorded when the line was deactivated (none / price / quality / moved)"),
    "taiwan_default": ("collections_referral_oct", "1 if the client was referred to a collection agency in October 2005"),
    "coil_caravan": ("caravan_claims_count", "Number of claims filed on caravan insurance policies"),
    "diabetes_readmission": ("readmission_ward_code", "Ward code of the next inpatient stay of this patient (0 = none)"),
    "online_shoppers": ("checkout_seconds", "Seconds spent on the checkout confirmation page"),
    "thyroid_sick": ("treatment_started", "1 if thyroid treatment was started after the clinic visit"),
}


@dataclass
class Variant:
    ds: Dataset
    name: str                      # trapped / anonymized / incomplete / misleading
    frame: pd.DataFrame
    target: str
    dictionary: dict[str, str]
    description: str
    rules: list[str]
    codes: dict[str, dict[str, str]]
    constraints: list[str]
    truth: dict[str, Any]
    rename: dict[str, str] = field(default_factory=dict)   # shown name -> original name
    removed_definitions: list[str] = field(default_factory=list)
    falsified: dict[str, str] = field(default_factory=dict)  # shown column -> false claim


def _post_values(did: str, y: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    n = len(y)
    pos = y == 1
    if did == "telco_churn":
        v = np.where(pos, rng.choice(["accepted", "declined"], n, p=[0.3, 0.7]), "none")
        return np.where(~pos & (rng.random(n) < 0.03), "declined", v)
    if did in ("german_credit", "taiwan_default", "thyroid_sick"):
        return np.where(pos, rng.binomial(1, 0.8, n), rng.binomial(1, 0.02, n))
    if did == "adult_income":
        return np.where(pos, rng.choice(["middle", "high"], n, p=[0.3, 0.7]), rng.choice(["low", "middle"], n, p=[0.8, 0.2]))
    if did == "iranian_churn":
        return np.where(pos, rng.choice(["price", "quality", "moved"], n), np.where(rng.random(n) < 0.02, "moved", "none"))
    if did == "coil_caravan":
        return np.where(pos, rng.poisson(0.8, n), 0)
    if did == "diabetes_readmission":
        return np.where(pos, rng.integers(1, 40, n), 0)
    if did == "online_shoppers":
        return np.where(pos, np.round(rng.gamma(2, 20, n), 1), 0.0)
    raise KeyError(did)


def trapped(ds: Dataset) -> Variant:
    df = ds.load().copy()
    rng = np.random.default_rng(SEED + 7)
    y = df[ds.target].to_numpy()
    yb = (y > np.median(y)).astype(int) if ds.task_type == "regression" else (y == 1).astype(int)
    order = np.argsort(yb + rng.normal(0, 0.35, len(df)), kind="stable")
    key = np.empty(len(df), dtype=np.int64)
    key[order] = 500000 + np.arange(len(df)) * 3 + rng.integers(0, 3, len(df))
    df.insert(0, "record_key", key)
    p_fri = np.where(yb == 1, 0.55, 1 / 7)
    wd = np.where(rng.random(len(df)) < p_fri, "Fri", rng.choice(WEEKDAYS, len(df)))
    df["load_weekday"] = wd
    sem = ds.semantics
    dictionary = dict(sem.get("dictionary", {}))
    dictionary["record_key"] = "Internal warehouse record key assigned when the extract was built"
    dictionary["load_weekday"] = "Weekday on which the row was loaded into the data warehouse"
    post = list(ds.truth.get("post_event", [])) + list(ds.truth.get("target_derived", []))
    if ds.dataset_id in INSERTED_POST:
        col, text = INSERTED_POST[ds.dataset_id]
        df[col] = _post_values(ds.dataset_id, yb, rng)
        dictionary[col] = text
        post.append(col)
    truth = dict(ds.truth)
    truth["ids_all"] = sorted(set(ds.truth.get("ids", [])) | {"record_key"})
    truth["post_outcome_all"] = sorted(set(post))
    truth["artifacts"] = ["load_weekday"]
    truth["leak_all"] = sorted(set(post) | {"load_weekday"})
    return Variant(ds, "trapped", df, ds.target, dictionary, sem.get("description", ""), list(sem.get("business_rules", [])),
                   dict(sem.get("code_dictionary", {})), list(sem.get("constraints", [])), truth)


def anonymized(v: Variant) -> Variant:
    cols = [c for c in v.frame.columns if c != v.target]
    rng = np.random.default_rng(SEED + 11)
    perm = rng.permutation(len(cols))
    new = {cols[i]: f"x{j + 1}" for j, i in enumerate(perm)}
    new[v.target] = "target"
    shown = {b: a for a, b in new.items()}
    frame = v.frame.rename(columns=new)[[f"x{j + 1}" for j in range(len(cols))] + ["target"]]
    dictionary = {new[c]: d for c, d in v.dictionary.items() if c in new}
    codes = {new[c]: m for c, m in v.codes.items() if c in new}
    rules = list(v.rules)
    for orig, s in sorted(new.items(), key=lambda kv: -len(kv[0])):
        rules = [r.replace(orig, s) for r in rules]
    return Variant(v.ds, "anonymized", frame, "target", dictionary, v.description, rules, codes, v.constraints, v.truth, shown)


def incomplete(v: Variant) -> Variant:
    """Remove the definitions that matter most: IDs, post-outcome/artifact columns, the target, and the rules."""
    drop = set(v.truth["ids_all"]) | set(v.truth["leak_all"]) | {v.target}
    dictionary = {c: d for c, d in v.dictionary.items() if c not in drop}
    return Variant(v.ds, "incomplete", v.frame, v.target, dictionary, v.description, [], {}, v.constraints, v.truth,
                   removed_definitions=sorted(drop & set(v.frame.columns)))


MISLEAD = {
    "telco_churn": {"tenure": "Customer age in years", "MonthlyCharges": "Number of support tickets opened last month",
                    "save_desk_outcome": "Preferred contact channel chosen at sign-up"},
    "bank_marketing": {"balance": "Client age in years", "duration": "Seconds the client spent on the bank website before the campaign",
                       "pdays": "Number of products the client holds"},
    "taiwan_default": {"LIMIT_BAL": "Client age in years", "AGE": "Credit limit in NT dollars",
                       "collections_referral_oct": "1 if the client opted in to paperless statements"},
    "card_fraud_synth": {"amount": "Account age in days", "account_age_days": "Transaction amount in EUR",
                         "chargeback_filed": "1 if the merchant supports contactless payment"},
}


def misleading(v: Variant) -> Variant:
    false = MISLEAD[v.ds.dataset_id]
    dictionary = {**v.dictionary, **false}
    return Variant(v.ds, "misleading", v.frame, v.target, dictionary, v.description, v.rules, v.codes, v.constraints, v.truth,
                   falsified=dict(false))
