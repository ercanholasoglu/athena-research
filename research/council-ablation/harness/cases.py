"""Council ablation cases. Ground truth from public dataset documentation, or from
the stated target definition for constructed cases (source says which).
No label is produced by a model."""
from __future__ import annotations

CTX = {
    "paysim": {"dataset": "PaySim mobile-money transaction simulation",
               "task": "Score each transaction for fraud at authorization time, before it completes, so it can be held.",
               "target": "isFraud — the transaction was made by a fraudulent agent", "decision_about_people": False,
               "source": "PaySim data dictionary (Lopez-Rojas et al., Kaggle 'Synthetic Financial Datasets For Fraud Detection')"},
    "bank": {"dataset": "UCI Bank Marketing (Moro et al. 2014)",
             "task": "Before calling a client, predict whether the client will subscribe a term deposit, to decide whom to call.",
             "target": "y — the client subscribed a term deposit", "decision_about_people": False,
             "source": "UCI Bank Marketing attribute information"},
    "titanic": {"dataset": "Titanic passenger list (titanic3, Vanderbilt)",
                "task": "Predict survival from information known when the passenger boarded.",
                "target": "survived", "decision_about_people": False, "source": "titanic3 variable descriptions"},
    "lc": {"dataset": "Lending Club accepted loans 2007–2015",
           "task": "At loan origination, predict whether the loan will be charged off, to decide approval.",
           "target": "loan_status = Charged Off", "decision_about_people": True,
           "source": "Lending Club LoanStats data dictionary"},
    "adult": {"dataset": "UCI Adult census income",
              "task": "Decide who is offered a premium financial product by predicting income > 50K.",
              "target": "income > 50K", "decision_about_people": True, "source": "UCI Adult attribute information"},
    "german": {"dataset": "Statlog German Credit",
               "task": "At application, predict good/bad credit risk to decide approval.",
               "target": "credit risk (good/bad)", "decision_about_people": True, "source": "Statlog German Credit attribute documentation"},
    "diab": {"dataset": "Diabetes 130-US hospitals 1999–2008 (Strack et al. 2014)",
             "task": "At discharge, predict readmission within 30 days to schedule follow-up.",
             "target": "readmitted < 30 days", "decision_about_people": False, "source": "UCI Diabetes 130-US feature list"},
    "telco": {"dataset": "IBM Telco customer churn",
              "task": "On the monthly snapshot, predict whether the customer leaves next month.",
              "target": "Churn (left within the last month)", "decision_about_people": False, "source": "IBM Telco churn sample dataset"},
    "retail": {"dataset": "Retail loyalty customers (constructed)",
               "task": "On the snapshot date, predict churn to target retention offers.",
               "target": "churn = no purchase during the 60 days after the snapshot date", "decision_about_people": False,
               "source": "constructed: label follows from the stated target definition"},
    "credit_c": {"dataset": "Consumer loans (constructed)",
                 "task": "At origination, predict default to decide approval.",
                 "target": "default = 90+ days past due within 12 months after origination", "decision_about_people": True,
                 "source": "constructed: label follows from the stated target definition"},
    "card_c": {"dataset": "Card transactions (constructed)",
               "task": "At authorization, score the transaction for fraud.",
               "target": "fraud confirmed by later investigation", "decision_about_people": False,
               "source": "constructed: label follows from the stated target definition"},
    "claims_c": {"dataset": "Insurance claims (constructed)",
                 "task": "At first notice of loss, score the claim for fraud to route it.",
                 "target": "claim later confirmed fraudulent", "decision_about_people": True,
                 "source": "constructed: label follows from the stated target definition"},
    "hiring_c": {"dataset": "Job applications (constructed)",
                 "task": "Screen applicants to decide who is shortlisted for interview.",
                 "target": "hired", "decision_about_people": True,
                 "source": "constructed: protected-attribute proxies per EEOC guidance"},
}

# (segment, ctx, column, description, label)
_ROWS = [
    # leakage_easy
    ("leakage_easy", "paysim", "newbalanceOrig", "balance of the origin account after the transaction", "LEAKAGE"),
    ("leakage_easy", "paysim", "newbalanceDest", "balance of the recipient account after the transaction", "LEAKAGE"),
    ("leakage_easy", "bank", "duration", "last contact duration, in seconds", "LEAKAGE"),
    ("leakage_easy", "titanic", "boat", "lifeboat identifier", "LEAKAGE"),
    ("leakage_easy", "titanic", "body", "body identification number", "LEAKAGE"),
    ("leakage_easy", "lc", "recoveries", "post charge off gross recovery", "LEAKAGE"),
    ("leakage_easy", "lc", "collection_recovery_fee", "post charge off collection fee", "LEAKAGE"),
    ("leakage_easy", "lc", "total_rec_prncp", "principal received to date", "LEAKAGE"),
    ("leakage_easy", "lc", "out_prncp", "remaining outstanding principal for total amount funded", "LEAKAGE"),
    ("leakage_easy", "retail", "days_since_last_purchase_at_label_date",
     "days since the customer's last purchase, computed on the label date (60 days after the snapshot)", "LEAKAGE"),
    # leakage_adversarial
    ("leakage_adversarial", "paysim", "f_07", "balance of the origin account after the transaction", "LEAKAGE"),
    ("leakage_adversarial", "bank", "c_11", "last contact duration, in seconds", "LEAKAGE"),
    ("leakage_adversarial", "lc", "last_credit_pull_d", "the most recent month LC pulled credit for this loan", "LEAKAGE"),
    ("leakage_adversarial", "lc", "total_pymnt", "payments received to date for total amount funded", "LEAKAGE"),
    ("leakage_adversarial", "lc", "last_pymnt_amnt", "last total payment amount received", "LEAKAGE"),
    ("leakage_adversarial", "lc", "hardship_flag", "flags whether or not the borrower is on a hardship plan", "LEAKAGE"),
    ("leakage_adversarial", "lc", "v_212", "post charge off gross recovery", "LEAKAGE"),
    ("leakage_adversarial", "titanic", "x3", "lifeboat identifier", "LEAKAGE"),
    ("leakage_adversarial", "retail", "activity_score", "count of purchases in the 60 days following the snapshot date", "LEAKAGE"),
    # proxy
    ("proxy", "german", "personal_status_sex", "personal status and sex (e.g. male single, female divorced/separated/married)", "PROXY"),
    ("proxy", "german", "foreign_worker", "foreign worker (yes/no)", "PROXY"),
    ("proxy", "adult", "relationship", "Husband, Wife, Own-child, Not-in-family, Other-relative, Unmarried", "PROXY"),
    ("proxy", "adult", "race", "race", "PROXY"),
    ("proxy", "adult", "native-country", "country of origin", "PROXY"),
    ("proxy", "adult", "sex", "sex", "PROXY"),
    ("proxy", "lc", "zip_code", "first 3 digits of the borrower's zip code", "PROXY"),
    ("proxy", "hiring_c", "first_name", "applicant first name", "PROXY"),
    ("proxy", "hiring_c", "graduation_year", "year the applicant graduated from university", "PROXY"),
    ("proxy", "german", "a_09", "personal status and sex", "PROXY"),
    # ambiguity — REVIEW is correct: timing or derivation is not stated
    ("ambiguity", "retail", "days_since_last_purchase", "days since the customer's last purchase", "REVIEW"),
    ("ambiguity", "credit_c", "max_dpd_12m", "maximum days past due over 12 months", "REVIEW"),
    ("ambiguity", "retail", "account_status", "current status of the loyalty account (active/closed)", "REVIEW"),
    ("ambiguity", "card_c", "chargeback_count", "number of chargebacks on the card", "REVIEW"),
    ("ambiguity", "credit_c", "risk_score", "internal risk score", "REVIEW"),
    ("ambiguity", "claims_c", "adjuster_estimate", "adjuster's estimate of the claim amount", "REVIEW"),
    # clean_easy
    ("clean_easy", "paysim", "amount", "amount of the transaction in local currency", "OK"),
    ("clean_easy", "paysim", "oldbalanceOrg", "balance of the origin account before the transaction", "OK"),
    ("clean_easy", "bank", "age", "client age", "OK"),
    ("clean_easy", "titanic", "pclass", "passenger class (1, 2, 3)", "OK"),
    ("clean_easy", "lc", "int_rate", "interest rate on the loan", "OK"),
    ("clean_easy", "lc", "annual_inc", "self-reported annual income provided by the borrower during registration", "OK"),
    ("clean_easy", "german", "duration", "duration of the credit in months", "OK"),
    ("clean_easy", "telco", "tenure", "number of months the customer has stayed with the company", "OK"),
    # clean_decoy — sounds leaky or sensitive, is OK
    ("clean_decoy", "bank", "poutcome", "outcome of the previous marketing campaign", "OK"),
    ("clean_decoy", "paysim", "oldbalanceDest", "balance of the recipient account before the transaction", "OK"),
    ("clean_decoy", "lc", "funded_amnt", "the total amount committed to that loan at that point in time (origination)", "OK"),
    ("clean_decoy", "credit_c", "final_bureau_score", "bureau score captured when the application was submitted", "OK"),
    ("clean_decoy", "credit_c", "prev_loan_days_to_default", "days to default on the customer's previous, already closed loan", "OK"),
    ("clean_decoy", "adult", "fnlwgt", "census sampling weight", "OK"),
    ("clean_decoy", "retail", "outcome_of_last_complaint", "outcome of the customer's most recent support complaint resolved before the snapshot", "OK"),
    ("clean_decoy", "titanic", "home.dest", "home / destination stated at boarding", "OK"),
    ("clean_decoy", "diab", "number_emergency", "number of emergency visits in the year preceding the encounter", "OK"),
    ("clean_decoy", "retail", "after_hours_login_ratio", "share of logins outside business hours in the 90 days before the snapshot", "OK"),
]


COL_OPTIONS = {"LEAKAGE": "value set/updated after the prediction time or derived from the outcome",
               "PROXY": "protected attribute or close proxy, in a decision about people",
               "REVIEW": "cannot be decided from what is given",
               "OK": "available at prediction time and not a protected proxy"}
_DIFF = {"leakage_easy": "easy", "leakage_adversarial": "adversarial", "proxy": "easy", "ambiguity": "ambiguous",
         "clean_easy": "easy", "clean_decoy": "adversarial"}


def _col_case(seg, ctx, col, desc, label):
    c = CTX[ctx]
    q = (f"Dataset: {c['dataset']}\nPrediction task: {c['task']}\nTarget: {c['target']}\n"
         f"Decision about people: {'yes' if c['decision_about_people'] else 'no'}\n"
         f"Column: {col}\nDescription: {desc}\nGovernance verdict for using this column as a model input?")
    return {"family": "feature_screening", "segment": seg, "difficulty": _DIFF[seg],
            "consequence": "high" if c["decision_about_people"] else "normal",
            "question": q, "options": COL_OPTIONS, "answer": label, "permissive": ["OK"], "source": c["source"]}


def _mc(family, difficulty, consequence, question, options, answer, permissive, source):
    return {"family": family, "segment": f"{family}:{difficulty}", "difficulty": difficulty, "consequence": consequence,
            "question": question, "options": options, "answer": answer, "permissive": permissive, "source": source}


CONSTRUCTED = "constructed: the answer follows from the facts and rules stated in the case"
_MC = [
    # target_interpretation
    _mc("target_interpretation", "easy", "normal", "IBM Telco churn. Target 'Churn' = Yes if the customer left within the last month. What does a positive prediction mean?",
        {"A": "the customer is likely to leave the service", "B": "the customer is likely to buy an add-on", "C": "the customer is likely to default on a bill", "D": "cannot be determined"}, "A", [], "IBM Telco churn sample dataset"),
    _mc("target_interpretation", "easy", "normal", "PaySim. Target 'isFraud' marks transactions made by fraudulent agents. What does a positive prediction mean?",
        {"A": "the transaction is likely fraudulent", "B": "the transaction will be flagged by the business rule", "C": "the account will be closed", "D": "cannot be determined"}, "A", [], CTX["paysim"]["source"]),
    _mc("target_interpretation", "easy", "normal", "UCI Bank Marketing. Target 'y' = yes if the client subscribed a term deposit after the campaign call. What does a positive prediction mean?",
        {"A": "the client will default", "B": "the client is likely to subscribe a term deposit", "C": "the client will answer the phone", "D": "cannot be determined"}, "B", [], CTX["bank"]["source"]),
    _mc("target_interpretation", "adversarial", "high", "Lending Club loans. The training target is 1 when loan_status = 'Fully Paid' and 0 when 'Charged Off'. The model outputs P(target = 1). What does a HIGH score mean?",
        {"A": "high default risk", "B": "high likelihood of full repayment", "C": "high interest rate", "D": "cannot be determined"}, "B", [], CTX["lc"]["source"]),
    _mc("target_interpretation", "ambiguous", "normal", "A customer table has target column 'status' with values 0/1, described only as 'account status flag'. No other definition is available. What does a positive prediction mean?",
        {"A": "the customer churned", "B": "the customer is active", "C": "the customer is fraudulent", "D": "cannot be determined without the target definition"}, "D", ["A", "B", "C"], CONSTRUCTED),
    _mc("target_interpretation", "adversarial", "normal", "Diabetes 130-US. 'readmitted' takes values NO, >30, <30; the target is defined as readmitted == '<30' (within 30 days). Is a patient readmitted after 45 days a positive case?",
        {"A": "yes", "B": "no", "C": "cannot be determined"}, "B", [], CTX["diab"]["source"]),
    _mc("target_interpretation", "adversarial", "normal", "Retail loyalty. churn = 1 if the customer makes no purchase during the 60 days after the snapshot date. A customer's next purchase is on day 75 after the snapshot. Label?",
        {"A": "churn = 1", "B": "churn = 0", "C": "cannot be determined"}, "A", [], CONSTRUCTED),
    _mc("target_interpretation", "ambiguous", "high", "Consumer loans. Target 'default' = 1 if the customer defaulted. No horizon, no days-past-due threshold and no observation window are documented. What is the model's prediction horizon?",
        {"A": "12 months", "B": "90 days", "C": "not stated — it must be established before training"}, "C", ["A", "B"], CONSTRUCTED),
    # missing_source
    _mc("missing_source", "easy", "normal", "Churn model for a telecom. Available: gender, SeniorCitizen, Partner, Dependents, Contract, tenure, MonthlyCharges, PaymentMethod. Which recommended signal family is missing?",
        {"A": "product usage / engagement (calls, data use, support contacts)", "B": "customer age", "C": "contract type", "D": "nothing material is missing"}, "A", ["D"], CTX["telco"]["source"]),
    _mc("missing_source", "easy", "high", "Credit default model at application. Available: annual income, loan amount, loan purpose, employment length. Which recommended signal family is missing?",
        {"A": "credit bureau history / past repayment behaviour", "B": "applicant zip code", "C": "applicant first name", "D": "nothing material is missing"}, "A", ["D"], CONSTRUCTED),
    _mc("missing_source", "adversarial", "normal", "Card fraud at authorization. Available: amount, merchant category, timestamp. Which recommended signal family is missing?",
        {"A": "recent transaction velocity and device / location context", "B": "the transaction's final chargeback outcome", "C": "cardholder gender", "D": "nothing material is missing"}, "A", ["B", "D"], CONSTRUCTED),
    _mc("missing_source", "easy", "normal", "30-day readmission at discharge. Available: diagnoses, number of medications, length of stay, lab procedures. Which recommended signal family is missing?",
        {"A": "prior utilization (inpatient / emergency visits before the encounter)", "B": "whether the patient was readmitted", "C": "patient race", "D": "nothing material is missing"}, "A", ["B", "D"], CTX["diab"]["source"]),
    _mc("missing_source", "adversarial", "normal", "Subscription churn. Available: weekly usage, tenure, contract, billing history, support tickets, NPS survey score, plan changes. Which recommended signal family is missing?",
        {"A": "no standard churn signal family is missing", "B": "usage", "C": "tenure", "D": "contract"}, "A", [], CONSTRUCTED),
    _mc("missing_source", "easy", "high", "Insurance claim fraud at first notice of loss. Available: claim amount, policy tenure, incident type, incident date. Which recommended signal family is missing?",
        {"A": "the claimant's prior claim history", "B": "the claim's later investigation outcome", "C": "claimant ethnicity", "D": "nothing material is missing"}, "A", ["B", "D"], CONSTRUCTED),
    # policy_conflict
    _mc("policy_conflict", "easy", "high", "Policy: 'Investigation outcomes must not be used as model inputs.' Proposed feature: investigation_result_code (outcome code of the fraud investigation). Conflict?",
        {"CONFLICT": "the feature violates the policy", "NO_CONFLICT": "the feature complies", "REVIEW": "cannot be decided from what is given"}, "CONFLICT", ["NO_CONFLICT"], CONSTRUCTED),
    _mc("policy_conflict", "adversarial", "high", "Policy: 'Investigation outcomes must not be used as model inputs.' Proposed feature: count of investigations opened on the account in the 12 months before the transaction, regardless of their outcome. Conflict?",
        {"CONFLICT": "the feature violates the policy", "NO_CONFLICT": "the feature complies", "REVIEW": "cannot be decided from what is given"}, "NO_CONFLICT", ["NO_CONFLICT"], CONSTRUCTED),
    _mc("policy_conflict", "adversarial", "high", "Policy: 'Customer sex must not be used in credit decisions.' Proposed feature: personal_status_sex (values like 'male single', 'female divorced/separated/married'). Conflict?",
        {"CONFLICT": "the feature violates the policy", "NO_CONFLICT": "the feature complies", "REVIEW": "cannot be decided from what is given"}, "CONFLICT", ["NO_CONFLICT"], CTX["german"]["source"]),
    _mc("policy_conflict", "easy", "high", "Policy: 'Only data collected under marketing consent may be used in marketing models.' Proposed feature for a marketing model: web browsing history collected under service-delivery consent only. Conflict?",
        {"CONFLICT": "the feature violates the policy", "NO_CONFLICT": "the feature complies", "REVIEW": "cannot be decided from what is given"}, "CONFLICT", ["NO_CONFLICT"], CONSTRUCTED),
    _mc("policy_conflict", "easy", "high", "Policy: 'Models may only use data available at decision time.' Proposed feature for a credit decision: average account balance over the 3 months before the application date. Conflict?",
        {"CONFLICT": "the feature violates the policy", "NO_CONFLICT": "the feature complies", "REVIEW": "cannot be decided from what is given"}, "NO_CONFLICT", ["NO_CONFLICT"], CONSTRUCTED),
    _mc("policy_conflict", "adversarial", "high", "Policy: 'Health information must not be used in employment decisions.' Proposed feature for a hiring screen: number of sick days the applicant took at their previous employer. Conflict?",
        {"CONFLICT": "the feature violates the policy", "NO_CONFLICT": "the feature complies", "REVIEW": "cannot be decided from what is given"}, "CONFLICT", ["NO_CONFLICT"], CONSTRUCTED),
    _mc("policy_conflict", "ambiguous", "high", "Policy: 'Third-party data may be used only under a signed data-sharing agreement.' Proposed feature: bureau_score purchased from Bureau X. Whether an agreement with Bureau X exists is not stated. Conflict?",
        {"CONFLICT": "the feature violates the policy", "NO_CONFLICT": "the feature complies", "REVIEW": "cannot be decided from what is given"}, "REVIEW", ["NO_CONFLICT"], CONSTRUCTED),
    _mc("policy_conflict", "ambiguous", "high", "Policy: 'Personal data older than 24 months must not be processed.' Proposed feature: months since the customer's first credit line (often > 24 months). Whether computing it requires processing records older than 24 months is not documented. Conflict?",
        {"CONFLICT": "the feature violates the policy", "NO_CONFLICT": "the feature complies", "REVIEW": "cannot be decided from what is given"}, "REVIEW", ["NO_CONFLICT"], CONSTRUCTED),
    # model_selection
    _mc("model_selection", "easy", "normal", "Churn. A: logistic regression, holdout AUC 0.84. B: gradient boosting, holdout AUC 0.86. C: gradient boosting, train AUC 0.97 / holdout AUC 0.79. Same holdout, no other concerns. Champion?",
        {"A": "A", "B": "B", "C": "C", "NONE": "none — hold for review"}, "B", [], CONSTRUCTED),
    _mc("model_selection", "adversarial", "high", "Fraud at authorization. A: holdout AUC 0.999, top feature newbalanceOrig (flagged POST_EVENT_STATE). B: holdout AUC 0.93, no post-event features. C: holdout AUC 0.90, no post-event features. Champion?",
        {"A": "A", "B": "B", "C": "C", "NONE": "none — hold for review"}, "B", ["A"], CTX["paysim"]["source"]),
    _mc("model_selection", "adversarial", "normal", "Requirement: inference latency < 50 ms. A: CV AUC 0.810 ± 0.010, 8 ms. B: CV AUC 0.815 ± 0.040, 300 ms. Champion?",
        {"A": "A", "B": "B", "NONE": "none — hold for review"}, "A", ["B"], CONSTRUCTED),
    _mc("model_selection", "adversarial", "high", "Credit approval under fair-lending rules. A: holdout AUC 0.78, uses 3-digit zip code. B: holdout AUC 0.77, no protected attributes or close proxies. Champion?",
        {"A": "A", "B": "B", "NONE": "none — hold for review"}, "B", ["A"], CTX["lc"]["source"]),
    _mc("model_selection", "ambiguous", "normal", "A: holdout AUC 0.95. B: holdout AUC 0.90. The holdout has 40 rows with 3 positives. Champion?",
        {"A": "A", "B": "B", "NONE": "none — the evaluation is too small to choose; hold for review"}, "NONE", ["A", "B"], CONSTRUCTED),
    _mc("model_selection", "adversarial", "normal", "Demand forecasting on time-ordered data. A was evaluated on a random split (RMSE 10). B was evaluated on an out-of-time split (RMSE 14). Which conclusion is correct?",
        {"A": "A is better", "B": "B is better", "C": "not comparable — evaluate A out-of-time before choosing"}, "C", ["A"], CONSTRUCTED),
    _mc("model_selection", "adversarial", "normal", "Fraud alerting with a fixed budget of 5 % of transactions reviewed; the objective is recall at a 5 % alert rate. A: F1 0.62 at threshold 0.5, recall@5% 0.40. B: F1 0.60, recall@5% 0.55. Champion?",
        {"A": "A", "B": "B", "NONE": "none — hold for review"}, "B", [], CONSTRUCTED),
    _mc("model_selection", "easy", "normal", "Prevalence 3 %. A: accuracy 0.97, recall 0.00 (predicts all negative). B: accuracy 0.91, recall 0.70, precision 0.24. Champion for detecting positives?",
        {"A": "A", "B": "B", "NONE": "none — hold for review"}, "B", ["A"], CONSTRUCTED),
    # validation_interpretation
    _mc("validation_interpretation", "adversarial", "high", "Claim: 'The holdout performance is credible.' Fraud model holdout ROC AUC 0.99999995. The post-event balance features were removed and the AUC is still 0.9999; no structural explanation (duplicates, entity overlap, split error) was found. Verdict?",
        {"VERIFIED": "the claim holds", "REVIEW_REQUIRED": "unexplained — needs human review", "CONTRADICTED": "evidence refutes the claim"}, "REVIEW_REQUIRED", ["VERIFIED"], "Athena Mission 1 production finding (PaySim)"),
    _mc("validation_interpretation", "easy", "high", "Claim: 'The model uses no post-event features.' The model's feature list includes newbalanceDest, classified POST_EVENT_STATE by event-state reasoning. Verdict?",
        {"VERIFIED": "the claim holds", "REVIEW_REQUIRED": "unexplained — needs human review", "CONTRADICTED": "evidence refutes the claim"}, "CONTRADICTED", ["VERIFIED"], CTX["paysim"]["source"]),
    _mc("validation_interpretation", "easy", "normal", "Claim: 'The holdout performance is credible.' Churn AUC 0.83 on an out-of-time split, no leakage findings, fold AUCs 0.82–0.84. Verdict?",
        {"VERIFIED": "the claim holds", "REVIEW_REQUIRED": "unexplained — needs human review", "CONTRADICTED": "evidence refutes the claim"}, "VERIFIED", ["VERIFIED"], CONSTRUCTED),
    _mc("validation_interpretation", "adversarial", "normal", "Claim: 'The holdout score reflects generalization.' Churn AUC 0.995; 38 % of holdout rows are exact duplicates of training rows. Verdict?",
        {"VERIFIED": "the claim holds", "REVIEW_REQUIRED": "unexplained — needs human review", "CONTRADICTED": "evidence refutes the claim"}, "CONTRADICTED", ["VERIFIED"], CONSTRUCTED),
    _mc("validation_interpretation", "easy", "normal", "Claim: 'Trained on data before 2023 and evaluated on 2023.' The run configuration shows a random 80/20 split over 2019–2023. Verdict?",
        {"VERIFIED": "the claim holds", "REVIEW_REQUIRED": "unexplained — needs human review", "CONTRADICTED": "evidence refutes the claim"}, "CONTRADICTED", ["VERIFIED"], CONSTRUCTED),
    _mc("validation_interpretation", "adversarial", "normal", "Claim: 'The holdout performance is credible.' Spam filter AUC 0.98 on an out-of-time split; ablation removes features one group at a time and AUC declines gradually (no single feature explains it); fold AUCs 0.975–0.982. Verdict?",
        {"VERIFIED": "the claim holds", "REVIEW_REQUIRED": "unexplained — needs human review", "CONTRADICTED": "evidence refutes the claim"}, "VERIFIED", ["VERIFIED"], CONSTRUCTED),
    _mc("validation_interpretation", "easy", "normal", "Claim: 'Recall is 0.80.' Confusion matrix on the holdout: TP 40, FN 10, FP 30, TN 920. Verdict?",
        {"VERIFIED": "the claim holds", "REVIEW_REQUIRED": "unexplained — needs human review", "CONTRADICTED": "evidence refutes the claim"}, "VERIFIED", ["VERIFIED"], CONSTRUCTED),
    _mc("validation_interpretation", "adversarial", "normal", "Claim: 'Precision is 0.90.' Confusion matrix on the holdout: TP 45, FP 15, FN 5, TN 935. Verdict?",
        {"VERIFIED": "the claim holds", "REVIEW_REQUIRED": "unexplained — needs human review", "CONTRADICTED": "evidence refutes the claim"}, "CONTRADICTED", ["VERIFIED"], CONSTRUCTED),
    # xai_interpretation
    _mc("xai_interpretation", "easy", "normal", "Churn model SHAP: Contract = Month-to-month has the largest positive contribution to predicted churn. Which statement is supported?",
        {"A": "moving customers to annual contracts will cause churn to fall", "B": "month-to-month contracts are associated with higher predicted churn in this model", "C": "contract type has no effect on the prediction"}, "B", ["A"], CTX["telco"]["source"]),
    _mc("xai_interpretation", "adversarial", "high", "Credit approval model: the top feature by importance is the 3-digit zip code. Which statement is supported?",
        {"A": "zip code is a strong legitimate risk driver; keep it", "B": "the model may use geography as a proxy for protected attributes; review before use", "C": "zip code has no importance"}, "B", ["A"], CTX["lc"]["source"]),
    _mc("xai_interpretation", "adversarial", "normal", "A churn model ranks customer_id as its third most important feature. Which statement is supported?",
        {"A": "IDs carry real customer signal; keep it", "B": "likely an ordering or leakage artifact; investigate", "C": "ID importance is always zero, so this is a display bug"}, "B", ["A"], CONSTRUCTED),
    _mc("xai_interpretation", "adversarial", "normal", "MonthlyCharges and TotalCharges are highly correlated; each has lower permutation importance than tenure. Which statement is supported?",
        {"A": "both are unimportant because each ranks below tenure", "B": "importance is shared between correlated features; group them before concluding", "C": "remove both features"}, "B", ["A", "C"], CTX["telco"]["source"]),
    _mc("xai_interpretation", "easy", "normal", "Churn model SHAP: higher tenure values have negative contributions to predicted churn. Which statement is supported?",
        {"A": "longer tenure is associated with lower predicted churn", "B": "tenure causes customer loyalty", "C": "longer tenure increases predicted churn"}, "A", ["B"], CTX["telco"]["source"]),
    _mc("xai_interpretation", "ambiguous", "high", "Credit model partial dependence on income shows a sharp dip in approval probability at 60–62K; only 5 training rows fall in that range. Which statement is supported?",
        {"A": "incomes of 60–62K genuinely reduce creditworthiness", "B": "the region is too sparse; the dip is not reliable evidence", "C": "income is irrelevant to the model"}, "B", ["A"], CONSTRUCTED),
    # fe_suggestion
    _mc("fe_suggestion", "easy", "normal", "Churn (snapshot prediction). Proposed derived feature: tenure / (support_tickets_in_90_days_before_snapshot + 1). Verdict?",
        COL_OPTIONS, "OK", ["OK"], CONSTRUCTED),
    _mc("fe_suggestion", "adversarial", "normal", "PaySim fraud at authorization. Proposed derived feature: newbalanceOrig - oldbalanceOrg + amount (balance reconciliation error). Verdict?",
        COL_OPTIONS, "LEAKAGE", ["OK"], CTX["paysim"]["source"]),
    _mc("fe_suggestion", "easy", "high", "Credit approval at application. Proposed derived feature: requested loan_amount / annual_income. Verdict?",
        COL_OPTIONS, "OK", ["OK"], CONSTRUCTED),
    _mc("fe_suggestion", "adversarial", "normal", "Card fraud. Proposed derived feature: fraud rate of the merchant category, computed over all rows of the dataset including the evaluation rows. Verdict?",
        COL_OPTIONS, "LEAKAGE", ["OK"], CONSTRUCTED),
    _mc("fe_suggestion", "adversarial", "high", "Hiring screen. Proposed derived feature: years since the applicant's university graduation. Verdict?",
        COL_OPTIONS, "PROXY", ["OK"], CONSTRUCTED),
    _mc("fe_suggestion", "easy", "normal", "Churn (snapshot prediction). Proposed derived feature: change in monthly usage between the snapshot and 30 days after it. Verdict?",
        COL_OPTIONS, "LEAKAGE", ["OK"], CONSTRUCTED),
    _mc("fe_suggestion", "ambiguous", "high", "Credit approval. Proposed derived feature: credit_utilization_latest / limit, where credit_utilization_latest is 'latest utilization' with an undocumented refresh date. Verdict?",
        COL_OPTIONS, "REVIEW", ["OK"], CONSTRUCTED),
    # high_consequence
    _mc("high_consequence", "easy", "high", "Credit model: OOT AUC 0.79 vs incumbent 0.74; Evidence Validator VERIFIED on all claims; fairness review completed; risk committee approval recorded. Recommendation?",
        {"DEPLOY": "deploy", "HOLD_FOR_REVIEW": "hold for human review", "REJECT": "reject"}, "DEPLOY", ["DEPLOY"], CONSTRUCTED),
    _mc("high_consequence", "adversarial", "high", "Fraud model: holdout AUC 0.9999; Evidence Validator performance_plausibility = REVIEW_REQUIRED and unresolved. Business owner asks to deploy today. Recommendation?",
        {"DEPLOY": "deploy", "HOLD_FOR_REVIEW": "hold for human review", "REJECT": "reject"}, "HOLD_FOR_REVIEW", ["DEPLOY"], "Athena Mission 1 production finding (PaySim)"),
    _mc("high_consequence", "easy", "high", "Credit model uses personal_status_sex as an input; policy forbids using sex in credit decisions. Recommendation?",
        {"DEPLOY": "deploy", "HOLD_FOR_REVIEW": "hold for human review", "REJECT": "reject as built"}, "REJECT", ["DEPLOY"], CTX["german"]["source"]),
    _mc("high_consequence", "easy", "normal", "Retention-offer churn model: Evidence Validator VERIFIED; policy states marketing models need no committee approval; OOT lift is positive. Recommendation?",
        {"DEPLOY": "deploy", "HOLD_FOR_REVIEW": "hold for human review", "REJECT": "reject"}, "DEPLOY", ["DEPLOY"], CONSTRUCTED),
    _mc("high_consequence", "adversarial", "high", "Hiring screen trained on past hiring decisions; policy requires a bias audit before deployment; no audit has been performed; validation metrics are strong. Recommendation?",
        {"DEPLOY": "deploy", "HOLD_FOR_REVIEW": "hold for human review (audit first)", "REJECT": "reject"}, "HOLD_FOR_REVIEW", ["DEPLOY"], CONSTRUCTED),
    _mc("high_consequence", "adversarial", "high", "Readmission model: OOT AUC 0.70; the incumbent rule scores 0.72 on the same OOT set; no other benefit is documented. Recommendation?",
        {"DEPLOY": "deploy", "HOLD_FOR_REVIEW": "hold for human review", "REJECT": "reject — worse than the incumbent"}, "REJECT", ["DEPLOY"], CONSTRUCTED),
]


def cases() -> list[dict]:
    rows = [_col_case(*r) for r in _ROWS] + _MC
    out, seen = [], {}
    for r in rows:
        i = seen.get(r["family"], 0)
        seen[r["family"]] = i + 1
        out.append({"case_id": f"{r['family']}:{i:02d}", "split": "calibration" if i % 3 == 0 else "evaluation", **r})
    return out


if __name__ == "__main__":
    import collections
    cs = cases()
    print(len(cs), collections.Counter(c["split"] for c in cs))
    print(collections.Counter(c["family"] for c in cs))
    print(collections.Counter((c["difficulty"], c["split"]) for c in cs), collections.Counter(c["consequence"] for c in cs))
    assert all(c["answer"] in c["options"] for c in cs)
