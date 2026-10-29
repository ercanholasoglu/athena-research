# Study A, TOT: iranian_churn::MODEL_FAMILY, seed 1

Every call the TOT topology made for this instance, replayed through `harness/rs2610/study_a/topologies.py` against the Study A ledger.

Ledger: `harness/rs2610/artifacts/study_a/ledger.jsonl`. Every request hash below is present in it; the output shown is the recorded `raw` field of that ledger row.

## Call 1: `propose`

- request_hash: `eef64ea25a457e84fcacfdf389ac81f159156fa4727c26127551bbd7d6bb7fd4`
- seed / replicate: 1
- visible token cap: 450
- recorded `model`: `qwen2.5:7b`
- recorded `model_digest`: `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`
- recorded `temperature`: `0.4`
- recorded `prompt_tokens`: `900`
- recorded `output_tokens`: `131`
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
{
  "candidates": [
    {
      "option": "lightgbm",
      "initial_case": "Best CV roc_auc, balanced performance.",
      "evidence_refs": ["E4"]
    },
    {
      "option": "catboost",
      "initial_case": "Second-best CV roc_auc, very low ECE and Brier.",
      "evidence_refs": ["E5"]
    },
    {
      "option": "random_forest",
      "initial_case": "High CV roc_auc, simple and interpretable.",
      "evidence_refs": ["E3"]
    }
  ]
}
```

## Call 2: `evaluate_0`

- request_hash: `775f1eb0045920953898d13bf02caf6005af318aaaeb36b60a4f00c186406fd7`
- seed / replicate: 1
- visible token cap: 450
- recorded `model`: `qwen2.5:7b`
- recorded `model_digest`: `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`
- recorded `temperature`: `0.4`
- recorded `prompt_tokens`: `956`
- recorded `output_tokens`: `129`
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

MODE: tree search, stage 2/3 (evaluate ONE branch in isolation). Branch under evaluation: option 'lightgbm' — initial case: Best CV roc_auc, balanced performance.
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
{
  "refinements": [
    {
      "variant": "lightgbm with early stopping",
      "supports": ["E2", "E4"],
      "risks": ["E6"],
      "score": 8
    },
    {
      "variant": "lightgbm with feature importance thresholding",
      "supports": ["E2", "E4"],
      "risks": ["E6"],
      "score": 7
    }
  ],
  "branch_score": 8,
  "fatal_flaw": false,
  "fatal_reason": ""
}
```

## Call 3: `evaluate_1`

- request_hash: `b4f29281634d02f5df403a63383f3858a910ea99dc3a4aac0c65edf731ea0421`
- seed / replicate: 1
- visible token cap: 450
- recorded `model`: `qwen2.5:7b`
- recorded `model_digest`: `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`
- recorded `temperature`: `0.4`
- recorded `prompt_tokens`: `961`
- recorded `output_tokens`: `134`
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

MODE: tree search, stage 2/3 (evaluate ONE branch in isolation). Branch under evaluation: option 'catboost' — initial case: Second-best CV roc_auc, very low ECE and Brier.
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
{
  "refinements": [
    {
      "variant": "catboost: LightGBM gradient boosting",
      "supports": ["E3", "E4"],
      "risks": ["E5"],
      "score": 8
    },
    {
      "variant": "catboost: ECE < 0.02",
      "supports": ["E5"],
      "risks": ["E3", "E4"],
      "score": 7
    }
  ],
  "branch_score": 8,
  "fatal_flaw": false,
  "fatal_reason": ""
}
```

## Call 4: `evaluate_2`

- request_hash: `e7372b2884157c1d7bda370092befe9c8ba58d558998a8eba3cd8ab24ef488d7`
- seed / replicate: 1
- visible token cap: 450
- recorded `model`: `qwen2.5:7b`
- recorded `model_digest`: `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`
- recorded `temperature`: `0.4`
- recorded `prompt_tokens`: `958`
- recorded `output_tokens`: `132`
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

MODE: tree search, stage 2/3 (evaluate ONE branch in isolation). Branch under evaluation: option 'random_forest' — initial case: High CV roc_auc, simple and interpretable.
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
{
  "refinements": [
    {
      "variant": "random_forest: 200 trees",
      "supports": ["E3"],
      "risks": ["E6"],
      "score": 8
    },
    {
      "variant": "random_forest: ECE < 0.03",
      "supports": ["E3"],
      "risks": ["E4", "E5"],
      "score": 7
    }
  ],
  "branch_score": 7,
  "fatal_flaw": false,
  "fatal_reason": ""
}
```

## Call 5: `select`

- request_hash: `537c2e6ff05e0238273d62d8de7401a77b20a3f28542d07b5c4fa29f62c7f75d`
- seed / replicate: 1
- visible token cap: 300
- recorded `model`: `qwen2.5:7b`
- recorded `model_digest`: `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`
- recorded `temperature`: `0.4`
- recorded `prompt_tokens`: `1076`
- recorded `output_tokens`: `61`
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
- branch 'lightgbm' score 8/10; refinements: lightgbm with early stopping (score 8, supports ['E2', 'E4'], risks ['E6']); lightgbm with feature importance thresholding (score 7, supports ['E2', 'E4'], risks ['E6'])
- branch 'catboost' score 8/10; refinements: catboost: LightGBM gradient boosting (score 8, supports ['E3', 'E4'], risks ['E5']); catboost: ECE < 0.02 (score 7, supports ['E5'], risks ['E3', 'E4'])
Pruned branches: ['random_forest'].
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
    "lightgbm",
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
{"decision": "lightgbm", "confidence": 0.9, "evidence_refs": ["E2", "E4"], "contradictions": [], "rationale_summary": "LightGBM has the highest CV roc_auc and competitive fit time compared to other models."}
```
