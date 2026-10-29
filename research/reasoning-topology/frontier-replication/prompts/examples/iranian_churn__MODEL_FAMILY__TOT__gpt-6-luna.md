# Study A2, TOT on gpt-6-luna: iranian_churn::MODEL_FAMILY, replicate 1

The same frozen inputs as the Study A example: the first call is byte-identical (system, user, schema) and every later call has the same system prompt, stage and token cap; later calls embed this model's own earlier outputs. See `providers/` for the provider request shape.

Ledger: `harness/rs2610/artifacts/replication/a2/ledger_openai.jsonl`. Every request hash below is present in it; the output shown is the recorded `raw` field of that ledger row.

## Call 1: `propose`

- request_hash: `791e53b1048e6498c4813286b673e5ad624ed1b2ee0a441bb7ca6767af891f9e`
- seed / replicate: 1
- visible token cap: 450
- recorded `model`: `gpt-6-luna`
- recorded `resolved_model`: `gpt-6-luna`
- recorded `temperature`: `NOT_CONFIGURABLE`
- recorded `reasoning`: `{'effort': 'medium', 'thinking': 'always on (provider)', 'allowance': 16000}`
- recorded `max_tokens_sent`: `16450`
- recorded `structured_output`: `json_schema strict (strict_schema)`
- recorded `prompt_tokens`: `848`
- recorded `output_tokens`: `209`
- recorded `reasoning_tokens`: `58`
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

MODE: tree search, stage 1/3 (propose). Propose exactly 3 DIFFERENT candidate options from OPTIONS as root branches. For each give the initial case for it (at most 30 words) and the evidence ids behind it. Do not decide yet.
```

### Output schema

```json
{
 "type": "object",
 "properties": {
  "candidates": {
   "type": "array",
   "minItems": 3,
   "maxItems": 3,
   "items": {
    "type": "object",
    "properties": {
     "option": {
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
     "initial_case": {
      "type": "string"
     },
     "evidence_refs": {
      "type": "array",
      "items": {
       "type": "string"
      }
     }
    },
    "required": [
     "option",
     "initial_case",
     "evidence_refs"
    ]
   }
  }
 },
 "required": [
  "candidates"
 ]
}
```

### Recorded output

```
{"candidates":[{"option":"random_forest","initial_case":"Strong performance with 0.9857 ROC AUC, low fit time, and a Brier score substantially better than the linear model.","evidence_refs":["E1","E3","E2"]},{"option":"lightgbm","initial_case":"Near-top ROC AUC of 0.9883 and the lowest Brier score, supporting strong ranking and probability performance.","evidence_refs":["E1","E4"]},{"option":"catboost","initial_case":"Highest reported ROC AUC, lowest variability, and best ECE and Brier scores among the candidates.","evidence_refs":["E1","E5"]}]}
```

## Call 2: `evaluate_0`

- request_hash: `a2ea16eacc522768f8065b5eabd0a38c6e9d1f56f83f2e2a65ed46f635186f55`
- seed / replicate: 1
- visible token cap: 450
- recorded `model`: `gpt-6-luna`
- recorded `resolved_model`: `gpt-6-luna`
- recorded `temperature`: `NOT_CONFIGURABLE`
- recorded `reasoning`: `{'effort': 'medium', 'thinking': 'always on (provider)', 'allowance': 16000}`
- recorded `max_tokens_sent`: `16450`
- recorded `structured_output`: `json_schema strict (strict_schema)`
- recorded `prompt_tokens`: `934`
- recorded `output_tokens`: `576`
- recorded `reasoning_tokens`: `445`
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

MODE: tree search, stage 2/3 (evaluate ONE branch in isolation). Branch under evaluation: option 'random_forest' — initial case: Strong performance with 0.9857 ROC AUC, low fit time, and a Brier score substantially better than the linear model.
Expand it into exactly 2 refinements (each a concrete variant or condition of this option), list for each the supporting and the risk evidence ids and score it 1-10. Then give branch_score 1-10 for the branch as a whole and state whether it has a fatal flaw (policy violation, unsupported by evidence, or contradicted by evidence).
```

### Output schema

```json
{
 "type": "object",
 "properties": {
  "refinements": {
   "type": "array",
   "minItems": 2,
   "maxItems": 2,
   "items": {
    "type": "object",
    "properties": {
     "variant": {
      "type": "string"
     },
     "supports": {
      "type": "array",
      "items": {
       "type": "string"
      }
     },
     "risks": {
      "type": "array",
      "items": {
       "type": "string"
      }
     },
     "score": {
      "type": "integer"
     }
    },
    "required": [
     "variant",
     "supports",
     "risks",
     "score"
    ]
   }
  },
  "branch_score": {
   "type": "integer"
  },
  "fatal_flaw": {
   "type": "boolean"
  },
  "fatal_reason": {
   "type": "string"
  }
 },
 "required": [
  "refinements",
  "branch_score",
  "fatal_flaw",
  "fatal_reason"
 ]
}
```

### Recorded output

```
{"refinements":[{"variant":"Train the standard 300-tree random forest for production, subject to the policy’s paired-fold acceptability criterion.","supports":["E3"],"risks":["E4","E5"],"score":7},{"variant":"Prefer the random forest when its paired-fold CV comparison with the best candidate is not statistically distinguishable and its lower fit time is useful.","supports":["E3","E4","E5"],"risks":["E4","E5"],"score":7}],"branch_score":7,"fatal_flaw":false,"fatal_reason":""}
```

## Call 3: `evaluate_1`

- request_hash: `fdcf2e4a599ba1bcc24315a028f2928d34c58b68a85d4fdd301f9cb212578574`
- seed / replicate: 1
- visible token cap: 450
- recorded `model`: `gpt-6-luna`
- recorded `resolved_model`: `gpt-6-luna`
- recorded `temperature`: `NOT_CONFIGURABLE`
- recorded `reasoning`: `{'effort': 'medium', 'thinking': 'always on (provider)', 'allowance': 16000}`
- recorded `max_tokens_sent`: `16450`
- recorded `structured_output`: `json_schema strict (strict_schema)`
- recorded `prompt_tokens`: `931`
- recorded `output_tokens`: `1123`
- recorded `reasoning_tokens`: `912`
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

MODE: tree search, stage 2/3 (evaluate ONE branch in isolation). Branch under evaluation: option 'lightgbm' — initial case: Near-top ROC AUC of 0.9883 and the lowest Brier score, supporting strong ranking and probability performance.
Expand it into exactly 2 refinements (each a concrete variant or condition of this option), list for each the supporting and the risk evidence ids and score it 1-10. Then give branch_score 1-10 for the branch as a whole and state whether it has a fatal flaw (policy violation, unsupported by evidence, or contradicted by evidence).
```

### Output schema

```json
{
 "type": "object",
 "properties": {
  "refinements": {
   "type": "array",
   "minItems": 2,
   "maxItems": 2,
   "items": {
    "type": "object",
    "properties": {
     "variant": {
      "type": "string"
     },
     "supports": {
      "type": "array",
      "items": {
       "type": "string"
      }
     },
     "risks": {
      "type": "array",
      "items": {
       "type": "string"
      }
     },
     "score": {
      "type": "integer"
     }
    },
    "required": [
     "variant",
     "supports",
     "risks",
     "score"
    ]
   }
  },
  "branch_score": {
   "type": "integer"
  },
  "fatal_flaw": {
   "type": "boolean"
  },
  "fatal_reason": {
   "type": "string"
  }
 },
 "required": [
  "refinements",
  "branch_score",
  "fatal_flaw",
  "fatal_reason"
 ]
}
```

### Recorded output

```
{"refinements":[{"variant":"Use the reported LightGBM configuration if a paired-fold comparison with CatBoost does not distinguish their ROC AUC scores.","supports":["E4","E5"],"risks":["E5"],"score":8},{"variant":"Use the reported LightGBM configuration when its near-top ROC AUC and Brier score are acceptable and the 1.34s mean fit time is tolerable.","supports":["E1","E4"],"risks":["E5"],"score":6}],"branch_score":7,"fatal_flaw":false,"fatal_reason":"The claim that LightGBM has the lowest Brier score is contradicted by E5 (CatBoost: 0.0298; LightGBM: 0.0307). That weakens the rationale but does not disqualify the branch: LightGBM has near-top ROC AUC, and its paired fold differences from CatBoost are small and not statistically distinguishable."}
```

## Call 4: `evaluate_2`

- request_hash: `c3d4e6090766e01e58f98c7b371fe618bbe5aa32b829d7d2302b18abbed1ae15`
- seed / replicate: 1
- visible token cap: 450
- recorded `model`: `gpt-6-luna`
- recorded `resolved_model`: `gpt-6-luna`
- recorded `temperature`: `NOT_CONFIGURABLE`
- recorded `reasoning`: `{'effort': 'medium', 'thinking': 'always on (provider)', 'allowance': 16000}`
- recorded `max_tokens_sent`: `16450`
- recorded `structured_output`: `json_schema strict (strict_schema)`
- recorded `prompt_tokens`: `926`
- recorded `output_tokens`: `724`
- recorded `reasoning_tokens`: `572`
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

MODE: tree search, stage 2/3 (evaluate ONE branch in isolation). Branch under evaluation: option 'catboost' — initial case: Highest reported ROC AUC, lowest variability, and best ECE and Brier scores among the candidates.
Expand it into exactly 2 refinements (each a concrete variant or condition of this option), list for each the supporting and the risk evidence ids and score it 1-10. Then give branch_score 1-10 for the branch as a whole and state whether it has a fatal flaw (policy violation, unsupported by evidence, or contradicted by evidence).
```

### Output schema

```json
{
 "type": "object",
 "properties": {
  "refinements": {
   "type": "array",
   "minItems": 2,
   "maxItems": 2,
   "items": {
    "type": "object",
    "properties": {
     "variant": {
      "type": "string"
     },
     "supports": {
      "type": "array",
      "items": {
       "type": "string"
      }
     },
     "risks": {
      "type": "array",
      "items": {
       "type": "string"
      }
     },
     "score": {
      "type": "integer"
     }
    },
    "required": [
     "variant",
     "supports",
     "risks",
     "score"
    ]
   }
  },
  "branch_score": {
   "type": "integer"
  },
  "fatal_flaw": {
   "type": "boolean"
  },
  "fatal_reason": {
   "type": "string"
  }
 },
 "required": [
  "refinements",
  "branch_score",
  "fatal_flaw",
  "fatal_reason"
 ]
}
```

### Recorded output

```
{"refinements":[{"variant":"Use CatBoost in the evaluated configuration, prioritizing ROC AUC.","supports":["E5"],"risks":["E4"],"score":9},{"variant":"Select CatBoost if a paired-fold test finds it not statistically distinguishable from the best candidate, as permitted by policy.","supports":["E5"],"risks":["E4"],"score":8}],"branch_score":8,"fatal_flaw":false,"fatal_reason":"No policy violation or contradiction is shown. CatBoost has the highest reported ROC AUC and strongest reported calibration metrics, though its AUC is very close to LightGBM's and the paired-fold test result is not provided."}
```

## Call 5: `select`

- request_hash: `73b11441f964e2e5d838cebb571d582fa51bf572c8b811c1fb4adb27200b11ad`
- seed / replicate: 1
- visible token cap: 300
- recorded `model`: `gpt-6-luna`
- recorded `resolved_model`: `gpt-6-luna`
- recorded `temperature`: `NOT_CONFIGURABLE`
- recorded `reasoning`: `{'effort': 'medium', 'thinking': 'always on (provider)', 'allowance': 16000}`
- recorded `max_tokens_sent`: `16300`
- recorded `structured_output`: `json_schema strict (strict_schema)`
- recorded `prompt_tokens`: `1043`
- recorded `output_tokens`: `693`
- recorded `reasoning_tokens`: `581`
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

MODE: tree search, stage 3/3 (select). After evaluation and pruning, these branches survive:
- branch 'catboost' score 8/10; refinements: Use CatBoost in the evaluated configuration, prioritizing ROC AUC. (score 9, supports ['E5'], risks ['E4']); Select CatBoost if a paired-fold test finds it not statistically distinguishable (score 8, supports ['E5'], risks ['E4'])
- branch 'random_forest' score 7/10; refinements: Train the standard 300-tree random forest for production, subject to the policy’ (score 7, supports ['E3'], risks ['E4', 'E5']); Prefer the random forest when its paired-fold CV comparison with the best candid (score 7, supports ['E3', 'E4', 'E5'], risks ['E4', 'E5'])
Pruned branches: ['lightgbm'].
Choose among the surviving branches (or UNDETERMINED). Return decision, confidence, evidence_refs (ids you relied on), contradictions (each naming the conflicting evidence ids, e.g. 'E2 vs E5'; empty if none) and rationale_summary (at most 40 words).
```

### Output schema

```json
{
 "type": "object",
 "properties": {
  "decision": {
   "type": "string",
   "enum": [
    "random_forest",
    "catboost",
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
{"decision":"catboost","confidence":0.78,"evidence_refs":["E3","E5"],"contradictions":["E3 vs E5: random forest and CatBoost have different CV means, though the paired-fold difference is not statistically significant."],"rationale_summary":"CatBoost has the highest CV ROC AUC and better ECE and Brier scores than random forest. Their paired-fold difference is not statistically significant, so the policy accepts CatBoost; the surviving branch also favors it."}
```
