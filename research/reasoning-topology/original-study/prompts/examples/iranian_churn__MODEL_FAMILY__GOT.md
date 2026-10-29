# Study A, GOT: iranian_churn::MODEL_FAMILY, seed 1

Every call the GOT topology made for this instance, replayed through `harness/rs2610/study_a/topologies.py` against the Study A ledger.

Ledger: `harness/rs2610/artifacts/study_a/ledger.jsonl`. Every request hash below is present in it; the output shown is the recorded `raw` field of that ledger row.

## Call 1: `extract_claims`

- request_hash: `b881adee1ae32008d1dd43603f7b6bf1ebde1ff5dbd00502eb8fde1d547b9757`
- seed / replicate: 1
- visible token cap: 900
- recorded `model`: `qwen2.5:7b`
- recorded `model_digest`: `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`
- recorded `temperature`: `0.4`
- recorded `prompt_tokens`: `915`
- recorded `output_tokens`: `534`
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

MODE: graph reasoning, stage 1/4 (claim nodes). Decompose the evidence and policy into 4-10 atomic claims that matter for this decision. Give each an id C1, C2, ..., the evidence ids it rests on, and polarity: 'fact' or 'concern'. Do not decide and do not mention options yet.
```

### Output schema

```json
{
 "type": "object",
 "properties": {
  "claims": {
   "type": "array",
   "minItems": 4,
   "maxItems": 10,
   "items": {
    "type": "object",
    "properties": {
     "id": {
      "type": "string"
     },
     "text": {
      "type": "string"
     },
     "source": {
      "type": "array",
      "items": {
       "type": "string"
      }
     },
     "polarity": {
      "type": "string",
      "enum": [
       "fact",
       "concern"
      ]
     }
    },
    "required": [
     "id",
     "text",
     "source",
     "polarity"
    ]
   }
  }
 },
 "required": [
  "claims"
 ]
}
```

### Recorded output

```
{
  "claims": [
    {
      "id": "C1",
      "text": "The linear_model has a CV score of 0.9390 ± 0.0086.",
      "source": ["E2"],
      "polarity": "fact"
    },
    {
      "id": "C2",
      "text": "The random_forest has a CV score of 0.9857 ± 0.0048.",
      "source": ["E3"],
      "polarity": "fact"
    },
    {
      "id": "C3",
      "text": "The lightgbm has a CV score of 0.9883 ± 0.0047.",
      "source": ["E4"],
      "polarity": "fact"
    },
    {
      "id": "C4",
      "text": "The catboost has a CV score of 0.9885 ± 0.0025.",
      "source": ["E5"],
      "polarity": "fact"
    },
    {
      "id": "C5",
      "text": "The neural_net has a CV score of 0.9484 ± 0.0050.",
      "source": ["E6"],
      "polarity": "fact"
    },
    {
      "id": "C6",
      "text": "The CV score of the linear_model is not statistically distinguishable from the best (lightgbm).",
      "source": ["E2", "E4"],
      "polarity": "concern"
    },
    {
      "id": "C7",
      "text": "The CV score of the random_forest is not statistically distinguishable from the best (lightgbm).",
      "source": ["E3", "E4"],
      "polarity": "concern"
    },
    {
      "id": "C8",
      "text": "The CV score of the catboost is not statistically distinguishable from the best (lightgbm).",
      "source": ["E5", "E4"],
      "polarity": "concern"
    },
    {
      "id": "C9",
      "text": "The CV score of the neural_net is not statistically distinguishable from the best (lightgbm).",
      "source": ["E6", "E4"],
      "polarity": "concern"
    }
  ]
}
```

## Call 2: `candidates`

- request_hash: `bb8c01dda28667b0f6ca2ab797e273a28c5d0713bf6c7d17ac560ef466ea53fe`
- seed / replicate: 1
- visible token cap: 300
- recorded `model`: `qwen2.5:7b`
- recorded `model_digest`: `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`
- recorded `temperature`: `0.4`
- recorded `prompt_tokens`: `1168`
- recorded `output_tokens`: `126`
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

CLAIM NODES:
C1 [fact; E2]: The linear_model has a CV score of 0.9390 ± 0.0086.
C2 [fact; E3]: The random_forest has a CV score of 0.9857 ± 0.0048.
C3 [fact; E4]: The lightgbm has a CV score of 0.9883 ± 0.0047.
C4 [fact; E5]: The catboost has a CV score of 0.9885 ± 0.0025.
C5 [fact; E6]: The neural_net has a CV score of 0.9484 ± 0.0050.
C6 [concern; E2,E4]: The CV score of the linear_model is not statistically distinguishable from the best (lightgbm).
C7 [concern; E3,E4]: The CV score of the random_forest is not statistically distinguishable from the best (lightgbm).
C8 [concern; E5,E4]: The CV score of the catboost is not statistically distinguishable from the best (lightgbm).
C9 [concern; E6,E4]: The CV score of the neural_net is not statistically distinguishable from the best (lightgbm).

MODE: graph reasoning, stage 2/4 (candidate nodes). Name exactly 3 DIFFERENT candidate options from OPTIONS worth comparing, each with a one-line description.
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
     "description": {
      "type": "string"
     }
    },
    "required": [
     "option",
     "description"
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
{"candidates": [{"option": "random_forest", "description": "Random forest with a CV score of 0.9857 ± 0.0048."}, {"option": "lightgbm", "description": "LightGBM with a CV score of 0.9883 ± 0.0047, the best performing model."}, {"option": "catboost", "description": "CatBoost with a CV score of 0.9885 ± 0.0025, nearly as good as LightGBM."}]}
```

## Call 3: `edges`

- request_hash: `747f26955e9af23a41de1466ef587843afed525e9ea4291e0a39db2270d3f732`
- seed / replicate: 1
- visible token cap: 1200
- recorded `model`: `qwen2.5:7b`
- recorded `model_digest`: `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`
- recorded `temperature`: `0.4`
- recorded `prompt_tokens`: `1213`
- recorded `output_tokens`: `1046`
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

CLAIM NODES:
C1 [fact; E2]: The linear_model has a CV score of 0.9390 ± 0.0086.
C2 [fact; E3]: The random_forest has a CV score of 0.9857 ± 0.0048.
C3 [fact; E4]: The lightgbm has a CV score of 0.9883 ± 0.0047.
C4 [fact; E5]: The catboost has a CV score of 0.9885 ± 0.0025.
C5 [fact; E6]: The neural_net has a CV score of 0.9484 ± 0.0050.
C6 [concern; E2,E4]: The CV score of the linear_model is not statistically distinguishable from the best (lightgbm).
C7 [concern; E3,E4]: The CV score of the random_forest is not statistically distinguishable from the best (lightgbm).
C8 [concern; E5,E4]: The CV score of the catboost is not statistically distinguishable from the best (lightgbm).
C9 [concern; E6,E4]: The CV score of the neural_net is not statistically distinguishable from the best (lightgbm).

CANDIDATE NODES: ['random_forest', 'lightgbm', 'catboost']
MODE: graph reasoning, stage 3/4 (edges). Link claims to candidates: for every claim that bears on a candidate add an edge with relation 'supports' or 'contradicts'. One claim may link to several candidates. Also list pairs of claims that conflict with each other.
```

### Output schema

```json
{
 "type": "object",
 "properties": {
  "edges": {
   "type": "array",
   "items": {
    "type": "object",
    "properties": {
     "claim": {
      "type": "string"
     },
     "candidate": {
      "type": "string",
      "enum": [
       "random_forest",
       "lightgbm",
       "catboost"
      ]
     },
     "relation": {
      "type": "string",
      "enum": [
       "supports",
       "contradicts"
      ]
     }
    },
    "required": [
     "claim",
     "candidate",
     "relation"
    ]
   }
  },
  "claim_conflicts": {
   "type": "array",
   "items": {
    "type": "object",
    "properties": {
     "a": {
      "type": "string"
     },
     "b": {
      "type": "string"
     },
     "why": {
      "type": "string"
     }
    },
    "required": [
     "a",
     "b",
     "why"
    ]
   }
  }
 },
 "required": [
  "edges",
  "claim_conflicts"
 ]
}
```

### Recorded output

```
{
  "edges": [
    {"claim": "C6", "candidate": "lightgbm", "relation": "supports"},
    {"claim": "C7", "candidate": "lightgbm", "relation": "supports"},
    {"claim": "C8", "candidate": "lightgbm", "relation": "supports"},
    {"claim": "C9", "candidate": "lightgbm", "relation": "supports"}
  ],
  "claim_conflicts": [
    {"a": "C1", "b": "C2", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C1", "b": "C3", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C1", "b": "C4", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C1", "b": "C5", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C1", "b": "C6", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C2", "b": "C3", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C2", "b": "C4", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C2", "b": "C5", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C2", "b": "C7", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C3", "b": "C4", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C3", "b": "C5", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C3", "b": "C8", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C4", "b": "C5", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C4", "b": "C6", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C4", "b": "C9", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C5", "b": "C6", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C5", "b": "C7", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C5", "b": "C8", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C6", "b": "C7", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C6", "b": "C8", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C6", "b": "C9", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C7", "b": "C8", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C7", "b": "C9", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."},
    {"a": "C8", "b": "C9", "why": "Both models have similar CV scores, but the task policy allows for non-distinguishable scores."}
  ]
}
```

## Call 4: `aggregate`

- request_hash: `e785ac3d69669d6843fe04a4d461ec51857a8a09e3f6504b16d625f753912831`
- seed / replicate: 1
- visible token cap: 250
- recorded `model`: `qwen2.5:7b`
- recorded `model_digest`: `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`
- recorded `temperature`: `0.4`
- recorded `prompt_tokens`: `1429`
- recorded `output_tokens`: `196`
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

CLAIM NODES:
C1 [fact; E2]: The linear_model has a CV score of 0.9390 ± 0.0086.
C2 [fact; E3]: The random_forest has a CV score of 0.9857 ± 0.0048.
C3 [fact; E4]: The lightgbm has a CV score of 0.9883 ± 0.0047.
C4 [fact; E5]: The catboost has a CV score of 0.9885 ± 0.0025.
C5 [fact; E6]: The neural_net has a CV score of 0.9484 ± 0.0050.
C6 [concern; E2,E4]: The CV score of the linear_model is not statistically distinguishable from the best (lightgbm).
C7 [concern; E3,E4]: The CV score of the random_forest is not statistically distinguishable from the best (lightgbm).
C8 [concern; E5,E4]: The CV score of the catboost is not statistically distinguishable from the best (lightgbm).
C9 [concern; E6,E4]: The CV score of the neural_net is not statistically distinguishable from the best (lightgbm).

GRAPH: candidate scores after propagation {'lightgbm': 2.0, 'random_forest': 0.0, 'catboost': 0.0}; claims shared by the top two candidates []; claim conflicts [('C1', 'C2'), ('C1', 'C3'), ('C1', 'C4'), ('C1', 'C5'), ('C1', 'C6'), ('C2', 'C3'), ('C2', 'C4'), ('C2', 'C5'), ('C2', 'C7'), ('C3', 'C4'), ('C3', 'C5'), ('C3', 'C8'), ('C4', 'C5'), ('C4', 'C6'), ('C4', 'C9'), ('C5', 'C6'), ('C5', 'C7'), ('C5', 'C8'), ('C6', 'C7'), ('C6', 'C8'), ('C6', 'C9'), ('C7', 'C8'), ('C7', 'C9'), ('C8', 'C9')].
MODE: graph reasoning, stage 4a (aggregation). Can the top two candidates be recombined into one option from OPTIONS that keeps the strengths of both (for example a model plus a remedy)? If yes give merged_option, else 'NONE'. List the conflicts that remain unresolved.
```

### Output schema

```json
{
 "type": "object",
 "properties": {
  "merge_possible": {
   "type": "boolean"
  },
  "merged_option": {
   "type": "string",
   "enum": [
    "linear_model",
    "random_forest",
    "lightgbm",
    "catboost",
    "neural_net",
    "UNDETERMINED",
    "NONE"
   ]
  },
  "unresolved_conflicts": {
   "type": "array",
   "items": {
    "type": "string"
   }
  }
 },
 "required": [
  "merge_possible",
  "merged_option",
  "unresolved_conflicts"
 ]
}
```

### Recorded output

```
{
  "merge_possible": false,
  "merged_option": "NONE",
  "unresolved_conflicts": [
    "C1 C2",
    "C1 C3",
    "C1 C4",
    "C1 C5",
    "C1 C6",
    "C2 C3",
    "C2 C4",
    "C2 C5",
    "C2 C7",
    "C3 C4",
    "C3 C5",
    "C3 C8",
    "C4 C5",
    "C4 C6",
    "C4 C9",
    "C5 C6",
    "C5 C7",
    "C5 C8",
    "C6 C7",
    "C6 C8",
    "C6 C9",
    "C7 C8",
    "C7 C9",
    "C8 C9"
  ]
}
```

## Call 5: `decide`

- request_hash: `21ebd827ef7c9d4540d382f4c99625de3eb96cafae7fcfcf0f891ae7875c0eaa`
- seed / replicate: 1
- visible token cap: 300
- recorded `model`: `qwen2.5:7b`
- recorded `model_digest`: `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`
- recorded `temperature`: `0.4`
- recorded `prompt_tokens`: `2087`
- recorded `output_tokens`: `74`
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

CLAIM NODES:
C1 [fact; E2]: The linear_model has a CV score of 0.9390 ± 0.0086.
C2 [fact; E3]: The random_forest has a CV score of 0.9857 ± 0.0048.
C3 [fact; E4]: The lightgbm has a CV score of 0.9883 ± 0.0047.
C4 [fact; E5]: The catboost has a CV score of 0.9885 ± 0.0025.
C5 [fact; E6]: The neural_net has a CV score of 0.9484 ± 0.0050.
C6 [concern; E2,E4]: The CV score of the linear_model is not statistically distinguishable from the best (lightgbm).
C7 [concern; E3,E4]: The CV score of the random_forest is not statistically distinguishable from the best (lightgbm).
C8 [concern; E5,E4]: The CV score of the catboost is not statistically distinguishable from the best (lightgbm).
C9 [concern; E6,E4]: The CV score of the neural_net is not statistically distinguishable from the best (lightgbm).

GRAPH SUMMARY:
Candidate scores (support minus contradiction, conflicted claims down-weighted): {'lightgbm': 2.0, 'random_forest': 0.0, 'catboost': 0.0}.
Reused claims (linked to 2+ candidates): [].
Claim conflicts: [('C1', 'C2', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C1', 'C3', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C1', 'C4', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C1', 'C5', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C1', 'C6', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C2', 'C3', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C2', 'C4', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C2', 'C5', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C2', 'C7', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C3', 'C4', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C3', 'C5', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C3', 'C8', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C4', 'C5', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C4', 'C6', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C4', 'C9', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C5', 'C6', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C5', 'C7', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C5', 'C8', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C6', 'C7', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C6', 'C8', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C6', 'C9', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C7', 'C8', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C7', 'C9', 'Both models have similar CV scores, but the task policy allows for non-distingui'), ('C8', 'C9', 'Both models have similar CV scores, but the task policy allows for non-distingui')].
Aggregation node: none. Unresolved conflicts: ['C1 C2', 'C1 C3', 'C1 C4', 'C1 C5', 'C1 C6', 'C2 C3', 'C2 C4', 'C2 C5', 'C2 C7', 'C3 C4', 'C3 C5', 'C3 C8', 'C4 C5', 'C4 C6', 'C4 C9', 'C5 C6', 'C5 C7', 'C5 C8', 'C6 C7', 'C6 C8', 'C6 C9', 'C7 C8', 'C7 C9', 'C8 C9'].

MODE: graph reasoning, stage 4b (decide over the graph). Choose the option best supported by the graph, or UNDETERMINED if unresolved conflicts make a single choice indefensible. Return decision, confidence, evidence_refs (ids you relied on), contradictions (each naming the conflicting evidence ids, e.g. 'E2 vs E5'; empty if none) and rationale_summary (at most 40 words).
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
{"decision": "lightgbm", "confidence": 1.0, "evidence_refs": ["E2", "E3", "E4", "E5", "E6"], "contradictions": [], "rationale_summary": "LightGBM has the highest CV score and is not statistically distinguishable from other top models."}
```
