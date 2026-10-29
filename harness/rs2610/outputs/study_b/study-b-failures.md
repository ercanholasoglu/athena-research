## 20. Study B failures

* **Leak-blind acceptance.** Post-outcome flags with univariate AUC 1.000 were accepted
  (hillstrom_email, A_RAW: "The spend column is an artifact, but the flag is a valid feature that can provide insights into non-purchasing behavior.").
  Identifier transforms with AUC 0.981 were accepted (hillstrom_email,
  A_RAW: "The log of record_key has a strong univariate AUC and can provide valuable insights into the relationship between the record_key and the target.").
* **Verification without challenge (E_FULL).** E's verification stage rated 4 hidden-leak entries and
  contradicted 1 (the others: "plausible"), raised false contradictions, and E blocked all traps less often than D_RULES with identical context. Its
  blocked-column set was the least stable across seeds (25.0% agreement).
* **No gap detection.** Under the incomplete dictionary no condition reported a removed definition as missing.
* **Lever choice.** An actionable intervention lever was named in at most 40.0%
  of runs in any condition (A_RAW 0.0%).
* **Self-assessment.** Mean self-reported confidence was between 0.90 and 0.93
  in every condition and was overconfident by +2.9 to +16.0 pp.
* **Cap failures (harness).** 2 UNSEEN calls hit their token cap on the 86-column
  `coil_caravan` (section 24); both runs are scored as failures, as pre-registered.
