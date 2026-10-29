# Study B — adversarial semantic tests

All traps are described **truthfully** in the documentation unless the test is about wrong documentation (T4).
Whether the model *uses* the description is what the conditions measure.

| Test | Construction | Where | Conditions | Scored by |
|---|---|---|---|---|
| T1 anonymized columns | every column renamed `x1..xn` in a fixed random order (seed 20261038), target → `target`; dictionary, codes and rules rewritten to the new names | DEV telco, bank · UNSEEN taiwan, iranian | A, C, E | core semantic accuracy, all traps blocked, vs A on named columns |
| T2 names only | the A_RAW condition on the trapped main grid | all | A | same metrics |
| T3 incomplete dictionary | definitions of every id, post-outcome, artifact column and of the target removed; business rules and code dictionary removed | DEV telco, german · UNSEEN taiwan, diabetes | C, D, E | `missing_semantics_recall`; trap blocking without definitions |
| T4 misleading dictionary | 3 entries per dataset replaced with false claims that the profile contradicts (below) | DEV telco, bank · UNSEEN taiwan, fraud | C, D, E | `falsified_detected_recall` (analysis contradictions ∪ E verification), false contradictions, trap blocking |
| T5 identifier trap | `record_key`: unique, assigned in target order (target + N(0, 0.35) noise), univariate AUC ≈ 0.9 | every main-grid dataset | A-E | `id_trap_caught`, candidate "log of record_key" rejected |
| T6 post-outcome leakage | natural (bank duration, fraud chargeback_filed, bike casual/registered, Hillstrom visit/spend) or inserted (`INSERTED_POST` in `variants.py`) | every main-grid dataset | A-E | `post_event_recall`, candidate post-outcome flag rejected, deployment loss when used |
| T7 statistically attractive, semantically absurd | `load_weekday`: positives batch-loaded on Fridays (p = 0.55 vs 1/7); candidate "load_weekday == Fri" with its measured AUC | every main-grid dataset | A-E | `artifact_caught`, candidate rejected |
| T7b target-mean encoding | candidate "mean of the target per value of <categorical>, computed on the full table including evaluation rows" | every main-grid dataset | A-E | candidate rejected |
| T8 causal / predictive trap | `intervention_column` must be a truth-actionable lever; failure if it is the strongest non-actionable predictor in the profile | every main-grid dataset with actionable columns | A-E | `lever_actionable`, `lever_is_predictive_trap`; Hillstrom intent = causal and family = uplift |

## T4 false claims (verbatim)

* telco: tenure → "Customer age in years" (profile: 0-72, many 0/1); MonthlyCharges → "Number of support tickets opened last
  month" (non-integer 18-119); save_desk_outcome → "Preferred contact channel chosen at sign-up" (non-'none' almost only for churners).
* bank: balance → "Client age in years" (negative values, max > 100k); duration → "Seconds the client spent on the bank
  website before the campaign" (hides the post-call leak); pdays → "Number of products the client holds" (−1 dominant, up to 871).
* taiwan: LIMIT_BAL → "Client age in years" (10k-1M); AGE → "Credit limit in NT dollars" (21-79);
  collections_referral_oct → "1 if the client opted in to paperless statements" (hides the post-outcome leak).
* fraud: amount ↔ account_age_days descriptions swapped; chargeback_filed → "1 if the merchant supports contactless payment"
  (hides the post-outcome leak).

Two T4 claims per dataset are *range* contradictions (checkable from min/max/integer flags). One per dataset *hides a leak
behind an innocent description*. That one can only be caught from the association statistics or from the semantics of the
other columns.
