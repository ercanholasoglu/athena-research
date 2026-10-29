"""Datasets, canonical dictionaries and ground-truth semantic annotations.

Every dataset carries three layers that the studies keep strictly apart:

* ``frame``      — the data itself (target column included).
* ``semantics``  — what a *human analyst* would supply: dictionary, code
                   dictionary, business rules, known constraints.  This is what
                   Study B conditions C/D/E reveal to the model.
* ``truth``      — the evaluation authority: target meaning, grain, IDs,
                   post-outcome columns, actionability, split.  Never shown to
                   any model; used only for scoring.

The split (DEVELOPMENT vs UNSEEN) is fixed here and pre-registered in
``study-*-design.md`` before any UNSEEN dataset is run.
"""
from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd

UCI = Path.home() / ".cache" / "athena-decision-corpus-v2"
RAW = Path.home() / ".cache" / "athena-research-ablation" / "raw"
SEED = 20261027
MAX_ROWS = 15000  # ML evidence row cap; original row count is reported separately


@dataclass
class Dataset:
    dataset_id: str
    family: str            # churn / credit / cross_sell / medical / fraud / generic / uplift / demand
    task_type: str         # binary / multiclass / regression
    split: str             # DEVELOPMENT / UNSEEN
    target: str
    loader: Callable[[], pd.DataFrame]
    semantics: dict[str, Any] = field(default_factory=dict)
    truth: dict[str, Any] = field(default_factory=dict)
    studies: tuple[str, ...] = ("A", "B")
    note: str = ""
    cap: int | None = MAX_ROWS

    def load(self, cap: int | None | str = "default") -> pd.DataFrame:
        cap = self.cap if cap == "default" else cap
        df = self.loader()
        self.truth.setdefault("original_rows", int(len(df)))
        if cap and len(df) > cap:
            df = df.sample(cap, random_state=SEED).sort_index().reset_index(drop=True)
        return df


# ── loaders ─────────────────────────────────────────────────────────────────

def _zip_text(archive: Path, member: str) -> str:
    with zipfile.ZipFile(archive) as zf:
        return zf.read(member).decode("utf-8", errors="replace")


def _telco() -> pd.DataFrame:
    f = pd.read_csv(RAW / "telco" / "telco.csv")
    f["TotalCharges"] = pd.to_numeric(f["TotalCharges"], errors="coerce")
    f["Churn"] = (f["Churn"] == "Yes").astype(int)
    return f


def _german() -> pd.DataFrame:
    f = pd.read_csv(io.StringIO(_zip_text(UCI / "144.zip", "german.data")), sep=" ", header=None)
    f.columns = [f"A{i + 1}" for i in range(20)] + ["credit_risk"]
    f["credit_risk"] = (f["credit_risk"] == 2).astype(int)  # 1 = bad credit
    return f


def _bank() -> pd.DataFrame:
    with zipfile.ZipFile(UCI / "222.zip") as outer, zipfile.ZipFile(io.BytesIO(outer.read("bank.zip"))) as inner:
        f = pd.read_csv(io.StringIO(inner.read("bank-full.csv").decode()), sep=";")
    f["y"] = (f["y"] == "yes").astype(int)
    return f


def _adult() -> pd.DataFrame:
    names = ["age", "workclass", "fnlwgt", "education", "education_num", "marital_status", "occupation",
             "relationship", "race", "sex", "capital_gain", "capital_loss", "hours_per_week", "native_country", "income"]
    f = pd.read_csv(io.StringIO(_zip_text(UCI / "2.zip", "adult.data")), header=None, names=names,
                    na_values="?", skipinitialspace=True).dropna(subset=["income"])
    f["income"] = (f["income"].str.strip() == ">50K").astype(int)
    return f


def _bike() -> pd.DataFrame:
    return pd.read_csv(RAW / "bike" / "hour.csv")


def _vehicle() -> pd.DataFrame:
    with zipfile.ZipFile(UCI / "149.zip") as zf:
        members = sorted(n for n in zf.namelist() if n.endswith(".dat"))
        f = pd.concat([pd.read_csv(io.StringIO(zf.read(m).decode()), sep=r"\s+", header=None) for m in members],
                      ignore_index=True)
    f.columns = [f"f{i}" for i in range(f.shape[1] - 1)] + ["vehicle_class"]
    return f


def _segment() -> pd.DataFrame:
    frames = []
    for member in ("segmentation.data", "segmentation.test"):
        lines = [ln for ln in _zip_text(UCI / "50.zip", member).splitlines() if ln.strip()]
        header = next(i for i, ln in enumerate(lines) if ln.startswith("REGION-CENTROID-COL"))
        frames.append(pd.read_csv(io.StringIO("\n".join(["CLASS," + lines[header], *lines[header + 1:]]))))
    f = pd.concat(frames, ignore_index=True)
    f.columns = [c.lower().replace("-", "_") for c in f.columns]
    return f.rename(columns={"class": "region_class"})


def _iranian() -> pd.DataFrame:
    f = pd.read_csv(RAW / "iranian_churn" / "Customer Churn.csv")
    f.columns = [" ".join(c.split()).replace(" ", "_") for c in f.columns]
    return f


def _taiwan() -> pd.DataFrame:
    f = pd.read_excel(RAW / "taiwan_default" / "default of credit card clients.xls", header=1)
    return f.rename(columns={"default payment next month": "default_next_month"})


def _coil() -> pd.DataFrame:
    names = [ln.split()[1] for ln in (RAW / "coil2000" / "dictionary.txt").read_text(encoding="latin-1").splitlines()
             if ln[:1].isdigit() and len(ln.split()) > 1][:86]
    f = pd.read_csv(RAW / "coil2000" / "ticdata2000.txt", sep="\t", header=None, names=names)
    return f


def _diabetes() -> pd.DataFrame:
    f = pd.read_csv(RAW / "diabetes130" / "diabetic_data.csv", na_values="?", low_memory=False)
    f["readmitted_30d"] = (f["readmitted"] == "<30").astype(int)
    return f.drop(columns=["readmitted"])


def _online() -> pd.DataFrame:
    f = pd.read_csv(io.StringIO(_zip_text(UCI / "468.zip", "online_shoppers_intention.csv")))
    f["Revenue"] = f["Revenue"].astype(int)
    f["Weekend"] = f["Weekend"].astype(int)
    return f


def _thyroid() -> pd.DataFrame:
    names = ["age", "sex", "on_thyroxine", "query_on_thyroxine", "on_antithyroid_medication", "sick", "pregnant",
             "thyroid_surgery", "I131_treatment", "query_hypothyroid", "query_hyperthyroid", "lithium", "goitre",
             "tumor", "hypopituitary", "psych", "TSH_measured", "TSH", "T3_measured", "T3", "TT4_measured", "TT4",
             "T4U_measured", "T4U", "FTI_measured", "FTI", "TBG_measured", "TBG", "referral_source", "class"]
    f = pd.read_csv(io.StringIO(_zip_text(UCI / "102.zip", "sick.data")), header=None, names=names, na_values="?")
    f["sick_diagnosis"] = (f["class"].str.split(".|", regex=False).str[0].str.strip(".") == "sick").astype(int)
    return f.drop(columns=["class", "TBG", "TBG_measured"])


def _hillstrom() -> pd.DataFrame:
    return pd.read_csv(RAW / "hillstrom" / "h.csv")


def _fraud() -> pd.DataFrame:
    """Synthetic card-transaction data with a *documented* generating process.

    Fraud probability rises with velocity, amount deviation from the account's
    own history, new device, IP-country mismatch and card-not-present; it is
    independent of the merchant category code once those are known.
    ``chargeback_filed`` is generated *after* the outcome (post-event leakage).
    """
    rng = np.random.default_rng(SEED)
    n, n_acc = 14000, 1800
    acc = rng.integers(0, n_acc, n)
    acc_mean = rng.lognormal(3.6, 0.6, n_acc)
    acc_age = rng.integers(5, 3650, n_acc)
    hours = np.sort(rng.uniform(0, 24 * 120, n))
    amount = np.round(acc_mean[acc] * rng.lognormal(0, 0.7, n), 2)
    velocity_1h = rng.poisson(0.6, n)
    velocity_24h = velocity_1h + rng.poisson(3, n)
    new_device = rng.binomial(1, 0.08, n)
    ip_mismatch = rng.binomial(1, 0.05, n)
    card_present = rng.binomial(1, 0.55, n)
    dist = np.round(rng.exponential(15, n), 1)
    mcc = rng.choice(["grocery", "fuel", "electronics", "travel", "restaurants", "online_services", "jewelry"], n,
                     p=[0.25, 0.15, 0.1, 0.08, 0.2, 0.17, 0.05])
    ratio = amount / acc_mean[acc]
    logit = (-3.9 + 0.55 * velocity_1h + 0.9 * np.log1p(ratio) * (ratio > 2) + 1.6 * new_device + 1.4 * ip_mismatch
             - 0.9 * card_present + 0.012 * dist - 0.0003 * acc_age[acc] + 0.002 * hours / 24)
    fraud = rng.binomial(1, 1 / (1 + np.exp(-logit)))
    chargeback = np.where(fraud == 1, rng.binomial(1, 0.85, n), rng.binomial(1, 0.004, n))
    return pd.DataFrame({
        "transaction_id": np.arange(100000, 100000 + n), "account_id": acc,
        "event_hour": np.round(hours, 2), "amount": amount, "merchant_category": mcc,
        "account_age_days": acc_age[acc], "txn_count_1h": velocity_1h, "txn_count_24h": velocity_24h,
        "account_avg_amount_90d": np.round(acc_mean[acc], 2), "new_device": new_device,
        "ip_country_mismatch": ip_mismatch, "card_present": card_present, "distance_from_home_km": dist,
        "chargeback_filed": chargeback, "is_fraud": fraud,
    })


# ── semantic layers ─────────────────────────────────────────────────────────
# ``semantics`` = what a data owner hands over.  ``truth`` = evaluation authority.

GERMAN_DICT = {
    "A1": "Status of existing checking account", "A2": "Duration of the credit in months",
    "A3": "Credit history", "A4": "Purpose of the credit", "A5": "Credit amount (Deutsche Mark)",
    "A6": "Savings account / bonds balance band", "A7": "Present employment since (band)",
    "A8": "Installment rate in percentage of disposable income", "A9": "Personal status and sex",
    "A10": "Other debtors / guarantors", "A11": "Present residence since (years)", "A12": "Property",
    "A13": "Age in years", "A14": "Other installment plans", "A15": "Housing",
    "A16": "Number of existing credits at this bank", "A17": "Job", "A18": "Number of people liable to provide maintenance for",
    "A19": "Telephone registered", "A20": "Foreign worker", "credit_risk": "1 = bad credit risk (defaulted), 0 = good",
}
GERMAN_CODES = {
    "A1": {"A11": "< 0 DM", "A12": "0 <= ... < 200 DM", "A13": ">= 200 DM / salary assignment", "A14": "no checking account"},
    "A3": {"A30": "no credits taken / all paid back duly", "A31": "all credits at this bank paid back duly",
           "A32": "existing credits paid back duly till now", "A33": "delay in paying off in the past", "A34": "critical account / other credits elsewhere"},
    "A4": {"A40": "car (new)", "A41": "car (used)", "A42": "furniture/equipment", "A43": "radio/television", "A44": "domestic appliances",
           "A45": "repairs", "A46": "education", "A48": "retraining", "A49": "business", "A410": "others"},
    "A6": {"A61": "< 100 DM", "A62": "100-500 DM", "A63": "500-1000 DM", "A64": ">= 1000 DM", "A65": "unknown / no savings"},
    "A7": {"A71": "unemployed", "A72": "< 1 year", "A73": "1-4 years", "A74": "4-7 years", "A75": ">= 7 years"},
    "A9": {"A91": "male divorced/separated", "A92": "female divorced/separated/married", "A93": "male single", "A94": "male married/widowed"},
    "A15": {"A151": "rent", "A152": "own", "A153": "for free"},
    "A20": {"A201": "yes", "A202": "no"},
}

COIL_DICT_HEAD = {
    "MOSTYPE": "Customer subtype (L0 code)", "MAANTHUI": "Number of houses", "MGEMOMV": "Average household size",
    "MGEMLEEF": "Average age band (L1)", "MOSHOOFD": "Customer main type (L2)",
    "MINKGEM": "Average income band", "MKOOPKLA": "Purchasing power class",
    "PPERSAUT": "Contribution (premium band) car policies", "PBRAND": "Contribution fire policies",
    "APERSAUT": "Number of car policies", "ABRAND": "Number of fire policies", "AWAPART": "Number of private third party insurance",
    "CARAVAN": "Number of mobile home (caravan) policies held: 1 = owns, 0 = does not",
}


def _coil_full_dict() -> dict[str, str]:
    out: dict[str, str] = {}
    for ln in (RAW / "coil2000" / "dictionary.txt").read_text(encoding="latin-1").splitlines():
        parts = ln.split()
        if ln[:1].isdigit() and len(parts) > 2 and int(parts[0]) <= 86 and parts[1].isupper() and parts[1] not in out:
            out[parts[1]] = " ".join(w for w in parts[2:] if w != "see" and not re.fullmatch(r"L\d", w))
    for k in out:  # postal-code-area aggregates: the data owner states this explicitly
        if k.startswith("M") and k not in ("MOSTYPE", "MOSHOOFD"):
            out[k] = out[k] + " (share band of the customer's postal-code area, 0-9)"
    out.update(COIL_DICT_HEAD)
    return out


DATASETS: list[Dataset] = [
    # ─────────────────────── DEVELOPMENT ───────────────────────
    Dataset(
        "telco_churn", "churn", "binary", "DEVELOPMENT", "Churn", _telco,
        semantics={
            "description": "Telecom subscription customers; one row per customer snapshot.",
            "dictionary": {
                "customerID": "Customer identifier", "gender": "Customer gender", "SeniorCitizen": "1 if customer is 65+",
                "Partner": "Has a partner", "Dependents": "Has dependents", "tenure": "Months the customer has been with the company",
                "PhoneService": "Has phone service", "MultipleLines": "Has multiple lines", "InternetService": "DSL / Fiber optic / No",
                "OnlineSecurity": "Has online security add-on", "OnlineBackup": "Has online backup add-on",
                "DeviceProtection": "Has device protection add-on", "TechSupport": "Has tech support add-on",
                "StreamingTV": "Streams TV", "StreamingMovies": "Streams movies", "Contract": "Month-to-month / One year / Two year",
                "PaperlessBilling": "Uses paperless billing", "PaymentMethod": "Payment method",
                "MonthlyCharges": "Current monthly charge (USD)", "TotalCharges": "Total amount charged over tenure (USD)",
                "Churn": "1 if the customer left within the last month",
            },
            "business_rules": ["Retention offers can change Contract type and add-on bundles; demographics cannot be targeted for pricing.",
                               "TotalCharges is approximately tenure x MonthlyCharges."],
            "constraints": ["Churn rate about 26 %."],
        },
        truth={
            "business_problem": "churn", "prediction_unit": "customer", "ids": ["customerID"], "group_col": None,
            "post_event": [], "target_derived": [], "ambiguous": [],
            "time_cols": [], "temporal": False, "split_ok": ["stratified_kfold"],
            "actionable": ["Contract", "OnlineSecurity", "TechSupport", "OnlineBackup", "DeviceProtection", "PaperlessBilling",
                           "PaymentMethod", "MonthlyCharges", "InternetService"],
            "protected": ["gender", "SeniorCitizen"], "intent": "predictive",
            "metrics_ok": ["roc_auc", "pr_auc", "f1", "log_loss", "brier"],
            "semtypes": {"tenure": "duration", "MonthlyCharges": "amount", "TotalCharges": "amount", "SeniorCitizen": "flag"},
        },
    ),
    Dataset(
        "german_credit", "credit", "binary", "DEVELOPMENT", "credit_risk", _german,
        semantics={"description": "Consumer credit applications from a German bank; one row per applicant.",
                   "dictionary": GERMAN_DICT, "code_dictionary": GERMAN_CODES,
                   "business_rules": ["Misclassifying a bad applicant as good costs 5x more than the reverse.",
                                      "Personal status/sex and foreign-worker status may not be used for decisions (fair lending)."],
                   "constraints": ["30 % of applicants are bad risks."]},
        truth={"business_problem": "credit_default", "prediction_unit": "applicant", "ids": [], "group_col": None,
               "post_event": [], "target_derived": [], "ambiguous": [], "time_cols": [], "temporal": False,
               "split_ok": ["stratified_kfold"], "actionable": ["A2", "A5", "A8"], "protected": ["A9", "A20", "A13"],
               "intent": "predictive", "metrics_ok": ["roc_auc", "expected_cost", "pr_auc", "brier", "log_loss"],
               "semtypes": {"A2": "duration", "A5": "amount", "A8": "rate", "A13": "age", "A16": "count", "A18": "count", "A11": "duration"}},
    ),
    Dataset(
        "bank_marketing", "cross_sell", "binary", "DEVELOPMENT", "y", _bank,
        semantics={"description": "Direct phone marketing of term deposits to existing bank clients; one row per client contacted in the campaign.",
                   "dictionary": {"age": "Client age", "job": "Type of job", "marital": "Marital status", "education": "Education level",
                                  "default": "Has credit in default", "balance": "Average yearly balance (EUR)", "housing": "Has housing loan",
                                  "loan": "Has personal loan", "contact": "Contact communication type", "day": "Last contact day of month",
                                  "month": "Last contact month", "duration": "Last contact duration in seconds",
                                  "campaign": "Number of contacts performed during this campaign for this client",
                                  "pdays": "Days since client was last contacted in a previous campaign (-1 = never)",
                                  "previous": "Number of contacts before this campaign", "poutcome": "Outcome of the previous campaign",
                                  "y": "1 if the client subscribed a term deposit"},
                   "business_rules": ["The model is used to decide whom to call BEFORE the call is made.",
                                      "Call duration is only known after the call ends."],
                   "constraints": ["About 12 % subscribe."]},
        truth={"business_problem": "cross_sell", "prediction_unit": "customer", "ids": [], "group_col": None,
               "post_event": ["duration"], "target_derived": [], "ambiguous": ["campaign"], "time_cols": ["month", "day"],
               "temporal": True, "split_ok": ["stratified_kfold", "time_based"], "actionable": ["contact", "month", "day", "campaign"],
               "protected": ["age", "marital"], "intent": "predictive", "metrics_ok": ["pr_auc", "roc_auc", "lift", "f1"],
               "semtypes": {"balance": "amount", "duration": "duration", "campaign": "count", "pdays": "duration", "previous": "count", "age": "age"}},
    ),
    Dataset(
        "adult_income", "generic", "binary", "DEVELOPMENT", "income", _adult,
        semantics={"description": "1994 US census extract; one row per person.",
                   "dictionary": {"age": "Age", "workclass": "Employer type", "fnlwgt": "Census sampling weight (number of people the row represents)",
                                  "education": "Highest education", "education_num": "Education as an ordinal number (same information as education)",
                                  "marital_status": "Marital status", "occupation": "Occupation", "relationship": "Role in household",
                                  "race": "Race", "sex": "Sex", "capital_gain": "Capital gains (USD)", "capital_loss": "Capital losses (USD)",
                                  "hours_per_week": "Hours worked per week", "native_country": "Country of origin", "income": "1 if income > 50K USD"},
                   "business_rules": ["Race and sex must not drive individual decisions."], "constraints": ["About 24 % positive."]},
        truth={"business_problem": "income_classification", "prediction_unit": "person", "ids": [], "group_col": None,
               "post_event": [], "target_derived": [], "ambiguous": ["fnlwgt"], "time_cols": [], "temporal": False,
               "split_ok": ["stratified_kfold"], "actionable": [], "protected": ["race", "sex", "native_country"],
               "intent": "predictive", "metrics_ok": ["roc_auc", "pr_auc", "f1", "log_loss", "accuracy"],
               "semtypes": {"capital_gain": "amount", "capital_loss": "amount", "hours_per_week": "count", "age": "age", "fnlwgt": "weight"}},
    ),
    Dataset(
        "bike_sharing", "demand", "regression", "DEVELOPMENT", "cnt", _bike,
        semantics={"description": "Hourly bike rental counts of a city bike-share system, 2011-2012.",
                   "dictionary": {"instant": "Record index", "dteday": "Date", "season": "Season (1-4)", "yr": "Year (0 = 2011, 1 = 2012)",
                                  "mnth": "Month", "hr": "Hour", "holiday": "Public holiday", "weekday": "Day of week", "workingday": "Working day",
                                  "weathersit": "Weather category (1 clear .. 4 heavy rain)", "temp": "Normalized temperature",
                                  "atemp": "Normalized feels-like temperature", "hum": "Normalized humidity", "windspeed": "Normalized wind speed",
                                  "casual": "Rentals by casual users in that hour", "registered": "Rentals by registered users in that hour",
                                  "cnt": "Total rentals in that hour"},
                   "business_rules": ["Forecasts are produced one day ahead.", "cnt = casual + registered."], "constraints": []},
        truth={"business_problem": "demand_forecast", "prediction_unit": "time_period", "ids": ["instant"], "group_col": None,
               "post_event": [], "target_derived": ["casual", "registered"], "ambiguous": [], "time_cols": ["dteday", "instant", "yr", "mnth", "hr"],
               "temporal": True, "split_ok": ["time_based"], "actionable": [], "protected": [], "intent": "predictive",
               "metrics_ok": ["rmse", "mae", "mape", "r2", "rmsle"],
               "semtypes": {"temp": "rate", "atemp": "rate", "hum": "rate", "windspeed": "rate", "casual": "count", "registered": "count"}},
    ),
    Dataset("vehicle_silhouettes", "generic", "multiclass", "DEVELOPMENT", "vehicle_class", _vehicle, studies=("A",),
            truth={"business_problem": "other", "split_ok": ["stratified_kfold"]}),
    # ─────────────────────── UNSEEN ───────────────────────
    Dataset(
        "iranian_churn", "churn", "binary", "UNSEEN", "Churn", _iranian,
        semantics={"description": "Iranian telecom subscribers; one row per customer, features aggregated over the first 9 months, churn observed at month 12.",
                   "dictionary": {"Call_Failure": "Number of call failures", "Complains": "1 if the customer complained",
                                  "Subscription_Length": "Total months of subscription", "Charge_Amount": "Charge band (0 lowest .. 9 highest)",
                                  "Seconds_of_Use": "Total seconds of calls", "Frequency_of_use": "Total number of calls",
                                  "Frequency_of_SMS": "Total number of text messages", "Distinct_Called_Numbers": "Number of distinct phone numbers called",
                                  "Age_Group": "Age band (1 youngest .. 5 oldest)", "Tariff_Plan": "1 = pay as you go, 2 = contractual",
                                  "Status": "1 = active, 2 = non-active (during the 9-month window)", "Age": "Customer age",
                                  "Customer_Value": "Calculated value of the customer", "Churn": "1 = churned by month 12"},
                   "business_rules": ["Features describe months 1-9; churn is measured at month 12 (3-month horizon)."],
                   "constraints": ["About 16 % churn."]},
        truth={"business_problem": "churn", "prediction_unit": "customer", "ids": [], "group_col": None, "post_event": [],
               "target_derived": [], "ambiguous": ["Status"], "time_cols": [], "temporal": False, "split_ok": ["stratified_kfold"],
               "actionable": ["Tariff_Plan", "Charge_Amount"], "protected": ["Age", "Age_Group"], "intent": "predictive",
               "metrics_ok": ["roc_auc", "pr_auc", "f1", "log_loss", "brier"],
               "semtypes": {"Call_Failure": "count", "Seconds_of_Use": "duration", "Frequency_of_use": "count", "Frequency_of_SMS": "count",
                            "Distinct_Called_Numbers": "count", "Subscription_Length": "duration", "Customer_Value": "amount", "Age": "age"}},
    ),
    Dataset(
        "taiwan_default", "credit", "binary", "UNSEEN", "default_next_month", _taiwan,
        semantics={"description": "Taiwanese credit-card clients, April-September 2005; one row per client.",
                   "dictionary": {"ID": "Client identifier", "LIMIT_BAL": "Credit limit (NT dollar)", "SEX": "1 male, 2 female",
                                  "EDUCATION": "1 grad school, 2 university, 3 high school, 4 others", "MARRIAGE": "1 married, 2 single, 3 others",
                                  "AGE": "Age in years",
                                  **{f"PAY_{m}": f"Repayment status {lbl} (-1 paid duly, 1..9 months of delay)" for m, lbl in
                                     [("0", "September 2005"), ("2", "August 2005"), ("3", "July 2005"), ("4", "June 2005"), ("5", "May 2005"), ("6", "April 2005")]},
                                  **{f"BILL_AMT{i}": f"Bill statement amount, {m} 2005" for i, m in enumerate(["September", "August", "July", "June", "May", "April"], 1)},
                                  **{f"PAY_AMT{i}": f"Amount paid, {m} 2005" for i, m in enumerate(["September", "August", "July", "June", "May", "April"], 1)},
                                  "default_next_month": "1 = default on the October 2005 payment"},
                   "business_rules": ["Sex, education and marriage may not be used for credit decisions."], "constraints": ["About 22 % default."]},
        truth={"business_problem": "credit_default", "prediction_unit": "customer", "ids": ["ID"], "group_col": None, "post_event": [],
               "target_derived": [], "ambiguous": [], "time_cols": [], "temporal": False, "split_ok": ["stratified_kfold"],
               "actionable": ["LIMIT_BAL"], "protected": ["SEX", "EDUCATION", "MARRIAGE", "AGE"], "intent": "predictive",
               "metrics_ok": ["roc_auc", "pr_auc", "expected_cost", "brier", "log_loss", "ks"],
               "semtypes": {"LIMIT_BAL": "amount", "AGE": "age", **{f"BILL_AMT{i}": "amount" for i in range(1, 7)},
                            **{f"PAY_AMT{i}": "amount" for i in range(1, 7)}, **{f"PAY_{m}": "ordinal" for m in ["0", "2", "3", "4", "5", "6"]}}},
    ),
    Dataset(
        "coil_caravan", "cross_sell", "binary", "UNSEEN", "CARAVAN", _coil,
        semantics={"description": "Insurance company customers (CoIL 2000); one row per customer. Variables starting with M are socio-demographics of the customer's postal-code area; P* are premium bands and A* are counts of policies held.",
                   "dictionary": {}, "business_rules": ["Goal: find customers to mail a caravan-insurance offer to (top 20 % of the list)."],
                   "constraints": ["About 6 % own a caravan policy."]},
        truth={"business_problem": "cross_sell", "prediction_unit": "customer", "ids": [], "group_col": None, "post_event": [],
               "target_derived": [], "ambiguous": [], "time_cols": [], "temporal": False, "split_ok": ["stratified_kfold"],
               "actionable": [], "protected": [], "intent": "predictive", "metrics_ok": ["pr_auc", "lift", "roc_auc", "top_k_precision"],
               "semtypes": {}},
    ),
    Dataset(
        "diabetes_readmission", "medical", "binary", "UNSEEN", "readmitted_30d", _diabetes,
        semantics={"description": "Inpatient diabetes encounters from 130 US hospitals, 1999-2008; one row per hospital encounter. A patient can have several encounters.",
                   "dictionary": {"encounter_id": "Encounter identifier", "patient_nbr": "Patient identifier", "race": "Race", "gender": "Gender",
                                  "age": "Age band (10-year)", "weight": "Weight band", "admission_type_id": "Admission type code",
                                  "discharge_disposition_id": "Discharge disposition code (e.g. 1 home, 11 expired, 13/14 hospice)",
                                  "admission_source_id": "Admission source code", "time_in_hospital": "Length of stay (days)",
                                  "payer_code": "Payer code", "medical_specialty": "Specialty of admitting physician",
                                  "num_lab_procedures": "Number of lab tests in the encounter", "num_procedures": "Number of non-lab procedures",
                                  "num_medications": "Number of distinct medications administered", "number_outpatient": "Outpatient visits in the year before",
                                  "number_emergency": "Emergency visits in the year before", "number_inpatient": "Inpatient visits in the year before",
                                  "diag_1": "Primary diagnosis (ICD9)", "diag_2": "Secondary diagnosis", "diag_3": "Additional diagnosis",
                                  "number_diagnoses": "Number of diagnoses", "max_glu_serum": "Glucose serum test result",
                                  "A1Cresult": "HbA1c test result", "change": "Diabetes medication changed", "diabetesMed": "Any diabetes medication prescribed",
                                  "readmitted_30d": "1 = readmitted within 30 days of discharge"},
                   "business_rules": ["Predictions are made at discharge.", "Encounters ending in death or hospice cannot be readmitted and should be excluded from the population."],
                   "constraints": ["About 11 % readmitted within 30 days."]},
        truth={"business_problem": "readmission", "prediction_unit": "encounter", "ids": ["encounter_id", "patient_nbr"], "group_col": "patient_nbr",
               "post_event": [], "target_derived": [], "ambiguous": ["discharge_disposition_id"], "time_cols": ["encounter_id"], "temporal": False,
               "split_ok": ["group_kfold"], "actionable": ["A1Cresult", "change", "diabetesMed", "num_medications"],
               "protected": ["race", "gender"], "intent": "predictive", "metrics_ok": ["roc_auc", "pr_auc", "brier", "log_loss", "recall"],
               "semtypes": {"time_in_hospital": "duration", "num_lab_procedures": "count", "num_procedures": "count", "num_medications": "count",
                            "number_outpatient": "count", "number_emergency": "count", "number_inpatient": "count", "number_diagnoses": "count"}},
        note="15k-row sample of 101,766 encounters",
    ),
    Dataset(
        "card_fraud_synth", "fraud", "binary", "UNSEEN", "is_fraud", _fraud,
        semantics={"description": "Card transactions over 120 days (synthetic, documented generator); one row per transaction.",
                   "dictionary": {"transaction_id": "Transaction identifier (assigned in time order)", "account_id": "Card account identifier",
                                  "event_hour": "Hours since start of the observation period", "amount": "Transaction amount (EUR)",
                                  "merchant_category": "Merchant category", "account_age_days": "Days since account opening",
                                  "txn_count_1h": "Transactions on the account in the previous hour", "txn_count_24h": "Transactions on the account in the previous 24 hours",
                                  "account_avg_amount_90d": "Account's average transaction amount over the previous 90 days",
                                  "new_device": "1 if the device was never seen for this account", "ip_country_mismatch": "1 if IP country differs from card country",
                                  "card_present": "1 if card physically present", "distance_from_home_km": "Distance between merchant and home address",
                                  "chargeback_filed": "1 if the cardholder later filed a chargeback for this transaction", "is_fraud": "1 = confirmed fraud"},
                   "business_rules": ["Scoring happens in real time at authorisation.", "Chargebacks arrive 10-60 days after the transaction."],
                   "constraints": ["About 3-4 % fraud."]},
        truth={"business_problem": "fraud", "prediction_unit": "transaction", "ids": ["transaction_id", "account_id"], "group_col": "account_id",
               "post_event": ["chargeback_filed"], "target_derived": [], "ambiguous": [], "time_cols": ["event_hour", "transaction_id"], "temporal": True,
               "split_ok": ["time_based", "group_kfold"], "actionable": [], "protected": [], "intent": "predictive",
               "metrics_ok": ["pr_auc", "recall", "roc_auc", "precision", "expected_cost"],
               "semtypes": {"amount": "amount", "account_avg_amount_90d": "amount", "txn_count_1h": "count", "txn_count_24h": "count",
                            "account_age_days": "duration", "distance_from_home_km": "distance", "event_hour": "time"}},
    ),
    Dataset(
        "online_shoppers", "generic", "binary", "UNSEEN", "Revenue", _online,
        semantics={"description": "E-commerce web sessions over one year; one row per session.",
                   "dictionary": {"Administrative": "Administrative pages visited", "Administrative_Duration": "Seconds on administrative pages",
                                  "Informational": "Informational pages visited", "Informational_Duration": "Seconds on informational pages",
                                  "ProductRelated": "Product pages visited", "ProductRelated_Duration": "Seconds on product pages",
                                  "BounceRates": "Average bounce rate of visited pages", "ExitRates": "Average exit rate of visited pages",
                                  "PageValues": "Average value of the pages visited (analytics metric derived from pages that preceded completed transactions)",
                                  "SpecialDay": "Closeness to a special day", "Month": "Month", "OperatingSystems": "OS code", "Browser": "Browser code",
                                  "Region": "Region code", "TrafficType": "Traffic source code", "VisitorType": "Returning / New / Other",
                                  "Weekend": "1 if weekend", "Revenue": "1 if the session ended with a purchase"},
                   "business_rules": ["Used to trigger an in-session offer."], "constraints": ["About 15 % of sessions purchase."]},
        truth={"business_problem": "purchase_intent", "prediction_unit": "session", "ids": [], "group_col": None, "post_event": [],
               "target_derived": [], "ambiguous": ["PageValues", "ExitRates", "ProductRelated_Duration"], "time_cols": ["Month"], "temporal": False,
               "split_ok": ["stratified_kfold", "time_based"], "actionable": ["SpecialDay"], "protected": [], "intent": "predictive",
               "metrics_ok": ["pr_auc", "roc_auc", "f1", "recall"],
               "semtypes": {f"{p}{s}": t for p in ("Administrative", "Informational", "ProductRelated") for s, t in (("", "count"), ("_Duration", "duration"))}
               | {"BounceRates": "rate", "ExitRates": "rate", "PageValues": "amount"}},
    ),
    Dataset(
        "thyroid_sick", "medical", "binary", "UNSEEN", "sick_diagnosis", _thyroid,
        semantics={"description": "Thyroid clinic referrals (Garvan Institute); one row per patient referral with lab results.",
                   "dictionary": {"age": "Age", "sex": "Sex", "on_thyroxine": "On thyroxine", "query_on_thyroxine": "Query on thyroxine",
                                  "on_antithyroid_medication": "On antithyroid medication", "sick": "Patient reports being sick",
                                  "pregnant": "Pregnant", "thyroid_surgery": "Had thyroid surgery", "I131_treatment": "Had I131 treatment",
                                  "query_hypothyroid": "Referring doctor queries hypothyroid", "query_hyperthyroid": "Referring doctor queries hyperthyroid",
                                  "lithium": "On lithium", "goitre": "Goitre", "tumor": "Tumor", "hypopituitary": "Hypopituitary", "psych": "Psychiatric",
                                  "TSH_measured": "TSH was measured", "TSH": "TSH level", "T3_measured": "T3 was measured", "T3": "T3 level",
                                  "TT4_measured": "TT4 measured", "TT4": "Total T4", "T4U_measured": "T4U measured", "T4U": "T4 uptake",
                                  "FTI_measured": "FTI measured", "FTI": "Free thyroxine index", "referral_source": "Referral source",
                                  "sick_diagnosis": "1 = diagnosed 'sick euthyroid'"},
                   "business_rules": ["FTI is computed from TT4 and T4U."], "constraints": ["About 6 % positive."]},
        truth={"business_problem": "medical_diagnosis", "prediction_unit": "patient", "ids": [], "group_col": None, "post_event": [],
               "target_derived": [], "ambiguous": ["sick", "TSH_measured", "T3_measured", "TT4_measured", "T4U_measured", "FTI_measured"],
               "time_cols": [], "temporal": False, "split_ok": ["stratified_kfold"], "actionable": [], "protected": ["sex"],
               "intent": "predictive", "metrics_ok": ["recall", "pr_auc", "roc_auc", "f1", "brier"],
               "semtypes": {"TSH": "lab", "T3": "lab", "TT4": "lab", "T4U": "lab", "FTI": "lab", "age": "age"}},
    ),
    Dataset("image_segment", "generic", "multiclass", "UNSEEN", "region_class", _segment, studies=("A",),
            truth={"business_problem": "other", "split_ok": ["stratified_kfold"]}),
    Dataset(
        "hillstrom_email", "uplift", "binary", "UNSEEN", "conversion", _hillstrom,
        semantics={"description": "Retailer e-mail experiment: customers randomly assigned to a men's e-mail, a women's e-mail or no e-mail; outcomes tracked for 2 weeks.",
                   "dictionary": {"recency": "Months since last purchase", "history_segment": "Band of spend in the past year",
                                  "history": "Dollars spent in the past year", "mens": "Bought men's merchandise in the past year",
                                  "womens": "Bought women's merchandise in the past year", "zip_code": "Urban / Suburban / Rural",
                                  "newbie": "New customer in the past 12 months", "channel": "Purchase channels used in the past year",
                                  "segment": "Randomly assigned e-mail campaign (treatment)", "visit": "Visited the website within 2 weeks",
                                  "conversion": "Purchased within 2 weeks", "spend": "Dollars spent within 2 weeks"},
                   "business_rules": ["Goal: decide whom to e-mail so that incremental purchases are maximised.", "Assignment to segment was randomised."],
                   "constraints": []},
        truth={"business_problem": "uplift", "prediction_unit": "customer", "ids": [], "group_col": None, "post_event": ["visit", "spend"],
               "target_derived": ["history_segment"], "ambiguous": [], "time_cols": [], "temporal": False,
               "split_ok": ["stratified_kfold"], "actionable": ["segment"], "protected": [], "intent": "causal", "treatment_col": "segment",
               "metrics_ok": ["qini", "uplift_auc", "auuc"],
               "semtypes": {"recency": "duration", "history": "amount", "spend": "amount"}},
        cap=None,
        note="history_segment is a binned copy of history, not of the target; listed in target_derived only for redundancy scoring",
    ),
]

# history_segment is redundancy, not target derivation — keep the truth honest.
for _d in DATASETS:
    if _d.dataset_id == "hillstrom_email":
        _d.truth["target_derived"] = []
        _d.truth["redundant"] = ["history_segment"]
    if _d.dataset_id == "coil_caravan":
        _d.semantics["dictionary"] = _coil_full_dict()


def by_id(dataset_id: str) -> Dataset:
    return next(d for d in DATASETS if d.dataset_id == dataset_id)


def datasets(study: str, split: str | None = None) -> list[Dataset]:
    return [d for d in DATASETS if study in d.studies and (split is None or d.split == split)]
