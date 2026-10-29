# Study A2, COT on gpt-6-luna: iranian_churn::MODEL_FAMILY, replicate 1

The same frozen inputs as the Study A example: the first call is byte-identical (system, user, schema) and every later call has the same system prompt, stage and token cap; later calls embed this model's own earlier outputs. See `providers/` for the provider request shape.

Ledger: `harness/rs2610/artifacts/replication/a2/ledger_openai.jsonl`. Every request hash below is present in it; the output shown is the recorded `raw` field of that ledger row.

## Call 1: `chain`

- request_hash: `df914d3dc431c74a3f4087a8a55c31edb8b948af58708e784cefaef56822981b`
- seed / replicate: 1
- visible token cap: 900
- recorded `model`: `gpt-6-luna`
- recorded `resolved_model`: `gpt-6-luna`
- recorded `temperature`: `NOT_CONFIGURABLE`
- recorded `reasoning`: `{'effort': 'medium', 'thinking': 'always on (provider)', 'allowance': 16000}`
- recorded `max_tokens_sent`: `16900`
- recorded `structured_output`: `json_schema strict (strict_schema)`
- recorded `prompt_tokens`: `970`
- recorded `output_tokens`: `594`
- recorded `reasoning_tokens`: `297`
- recorded `stop_reason`: `completed`
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

MODE: reason in a single sequential chain. Write 3-6 steps; step k must build on step k-1 (depends_on_step = k-1, the first step uses 0) and cite the evidence ids it uses. Consider one line of reasoning only; do not enumerate and compare alternatives in parallel. After the last step give the decision. Return decision, confidence, evidence_refs (ids you relied on), contradictions (each naming the conflicting evidence ids, e.g. 'E2 vs E5'; empty if none) and rationale_summary (at most 40 words).
```

### Output schema

```json
{
 "type": "object",
 "properties": {
  "steps": {
   "type": "array",
   "minItems": 3,
   "maxItems": 6,
   "items": {
    "type": "object",
    "properties": {
     "step": {
      "type": "integer"
     },
     "depends_on_step": {
      "type": "integer"
     },
     "uses_evidence": {
      "type": "array",
      "items": {
       "type": "string"
      }
     },
     "claim": {
      "type": "string"
     }
    },
    "required": [
     "step",
     "depends_on_step",
     "uses_evidence",
     "claim"
    ]
   }
  },
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
  "steps",
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
  "steps": [
    {
      "step": 1,
      "depends_on_step": 0,
      "uses_evidence": ["E1"],
      "claim": "The production choice should prioritize ROC AUC for this binary classification task."
    },
    {
      "step": 2,
      "depends_on_step": 1,
      "uses_evidence": ["E4", "E5"],
      "claim": "CatBoost has the highest reported mean ROC AUC, narrowly ahead of LightGBM; their paired fold results are close enough that the policy accepts CatBoost if the scores are not distinguishable."
    },
    {
      "step": 3,
      "depends_on_step": 2,
      "uses_evidence": ["E5"],
      "claim": "CatBoost also has favorable calibration and Brier score, and its mean fit time is lower than LightGBM's, supporting it as the production choice."
    }
  ],
  "decision": "catboost",
  "confidence": 0.82,
  "evidence_refs": ["E1", "E4", "E5"],
  "contradictions": [],
  "rationale_summary": "CatBoost has the highest mean ROC AUC, close to LightGBM under the policy's acceptability rule, and also offers favorable calibration, Brier score, and fit time."
}
```
