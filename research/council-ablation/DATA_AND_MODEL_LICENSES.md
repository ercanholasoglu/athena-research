# Data and model terms

## Datasets

**No dataset rows are included in this repository.** Each case quotes a column name, its documented meaning and
a task statement. The ground truth follows from the public documentation listed below, or from a rule stated
inside the case (marked *constructed*).

The licence column records the terms as listed by each source when this package was prepared. Before reusing
any dataset itself, the terms should be checked at the source. "Not stated" means the source page lists no
licence.

| Context | Dataset / documentation | Licence of the dataset (as listed by the source) |
|---|---|---|
| paysim | PaySim, "Synthetic Financial Datasets For Fraud Detection" (Lopez-Rojas et al., Kaggle) | CC BY-SA 4.0 |
| bank | UCI Bank Marketing (Moro et al. 2014) | CC BY 4.0 |
| titanic | titanic3 variable descriptions (Vanderbilt Biostatistics) | Not stated |
| lc | Lending Club LoanStats data dictionary | Not stated |
| adult | UCI Adult | CC BY 4.0 |
| german | Statlog (German Credit Data), UCI | CC BY 4.0 |
| diab | Diabetes 130-US hospitals 1999–2008 (Strack et al. 2014), UCI | CC BY 4.0 |
| telco | IBM Telco customer churn sample | Not stated |
| retail, credit_c, card_c, claims_c, hiring_c | Constructed by the case author | Same as this repository |

## Models

| Member | Model | Terms that apply to outputs |
|---|---|---|
| sonnet, judge | Claude Sonnet 5.5 (Anthropic API) | Anthropic commercial terms |
| haiku and role/sampling variants | Claude Haiku 5.5 (Anthropic API) | Anthropic commercial terms |
| qwen7b, qwen1_5b | Qwen 2.5 7B / 1.5B Instruct, local, Q4_K_M | Apache 2.0 |
| Jev arm (decision corpus) | TypeSafe Jev API, model `jev-1.13.0` | Provider terms; only aggregate metrics are published |

Only parsed answers (option id and confidence) and call telemetry are published. Raw completions and free-text
reasons are not.

## Third-party names

Names of models, providers and datasets identify what was measured. They are not endorsements, and no ranking
of vendors is claimed.
