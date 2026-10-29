# Study A, DIRECT: iranian_churn::MODEL_FAMILY, seed 1

Every call the DIRECT topology made for this instance, replayed through `harness/rs2610/study_a/topologies.py` against the Study A ledger.

Ledger: `harness/rs2610/artifacts/study_a/ledger.jsonl`. Every request hash below is present in it; the output shown is the recorded `raw` field of that ledger row.

## Call 1: `direct`

- request_hash: `c7d216b9125b6adef4bd8237310a38de90e0ec1b70aecb7d375ce80af50fdae9`
- seed / replicate: 1
- visible token cap: 260
- recorded `model`: `qwen2.5:7b`
- recorded `model_digest`: `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`
- recorded `temperature`: `0.4`
- recorded `prompt_tokens`: `900`
- recorded `output_tokens`: `55`
- recorded `truncated`: `False`
- recorded `parse_ok`: `True`

### System

```
You are the analytical decision engine of an AutoML platform. You make one bounded decision from the evidence packet you are given. Use only the evidence and the policy shown; never invent numbers. Evidence ids look like E1, E2. If the evidence does not support a defensible single choice, choose UNDETERMINED. confidence is your probability (0-1) that your decision is the defensible one. Answer in JSON only.
```

### User

```
TASK (MODEL_FAMILY): Which model family should be trained for production on this dataset?

POLICY:
- A candidate whose CV score is not statistically distinguishable from the best (paired fold test) is acceptable.

EVIDENCE:
E1: Dataset profile: binary task, 2362 development rows (3150 in the source), 13 raw columns / 13 encoded features, class shares [0.8429, 0.1571], mean missing share 0.000. Primary metric: roc_auc (higher is better).
E2: linear_model: 5-fold CV roc_auc 0.9390 ± 0.0086 (folds [0.94351, 0.93256, 0.95145, 0.93739, 0.93031]), mean fit time 0.01s, out-of-fold ECE 0.018, Brier 0.0667.
E3: random_forest: 5-fold CV roc_auc 0.9857 ± 0.0048 (folds [0.97888, 0.98958, 0.98231, 0.98944, 0.98807]), mean fit time 0.39s, out-of-fold ECE 0.034, Brier 0.0345.
E4: lightgbm: 5-fold CV roc_auc 0.9883 ± 0.0047 (folds [0.98481, 0.99317, 0.98207, 0.99002, 0.99166]), mean fit time 1.34s, out-of-fold ECE 0.026, Brier 0.0307.
E5: catboost: 5-fold CV roc_auc 0.9885 ± 0.0025 (folds [0.98471, 0.98985, 0.98713, 0.99043, 0.99034]), mean fit time 0.49s, out-of-fold ECE 0.017, Brier 0.0298.
E6: neural_net: 5-fold CV roc_auc 0.9484 ± 0.0050 (folds [0.95396, 0.94955, 0.94095, 0.95151, 0.94627]), mean fit time 0.08s, out-of-fold ECE 0.020, Brier 0.0636.

OPTIONS:
- linear_model: regularised linear model (logistic / ridge)
- random_forest: random forest (300 trees)
- lightgbm: LightGBM gradient boosting
- catboost: CatBoost gradient boosting
- neural_net: MLP neural network (64-32)
- UNDETERMINED: the evidence does not support a defensible single choice

MODE: answer directly. Do not write reasoning steps. Return decision, confidence, evidence_refs (ids you relied on), contradictions (each naming the conflicting evidence ids, e.g. 'E2 vs E5'; empty if none) and rationale_summary (at most 40 words).
```

### Output schema

```json
{
 "type": "object",
 "properties": {
  "decision": {
   "type": "string",
   "enum": [
    "linear_model",
    "random_forest",
    "lightgbm",
    "catboost",
    "neural_net",
    "UNDETERMINED"
   ]
  },
  "confidence": {
   "type": "number"
  },
  "evidence_refs": {
   "type": "array",
   "items": {
    "type": "string"
   }
  },
  "contradictions": {
   "type": "array",
   "items": {
    "type": "string"
   }
  },
  "rationale_summary": {
   "type": "string"
  }
 },
 "required": [
  "decision",
  "confidence",
  "evidence_refs",
  "contradictions",
  "rationale_summary"
 ]
}
```

### Recorded output

```
{
  "decision": "catboost",
  "confidence": 0.95,
  "evidence_refs": ["E5"],
  "contradictions": [],
  "rationale_summary": "CatBoost has the highest CV roc_auc score."
}
```
