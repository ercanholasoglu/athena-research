# Study A2, GOT on gpt-6-luna: iranian_churn::MODEL_FAMILY, replicate 1

The same frozen inputs as the Study A example: the first call is byte-identical (system, user, schema) and every later call has the same system prompt, stage and token cap; later calls embed this model's own earlier outputs. See `providers/` for the provider request shape.

Ledger: `harness/rs2610/artifacts/replication/a2/ledger_openai.jsonl`. Every request hash below is present in it; the output shown is the recorded `raw` field of that ledger row.

## Call 1: `extract_claims`

- request_hash: `f90615ed6c99af3a3a9a29476b37836fae8a6cfb385f57da8dc37cf8911822ab`
- seed / replicate: 1
- visible token cap: 900
- recorded `model`: `gpt-6-luna`
- recorded `resolved_model`: `gpt-6-luna`
- recorded `temperature`: `NOT_CONFIGURABLE`
- recorded `reasoning`: `{'effort': 'medium', 'thinking': 'always on (provider)', 'allowance': 16000}`
- recorded `max_tokens_sent`: `16900`
- recorded `structured_output`: `json_schema strict (strict_schema)`
- recorded `prompt_tokens`: `849`
- recorded `output_tokens`: `728`
- recorded `reasoning_tokens`: `382`
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
{"claims":[{"id":"C1","text":"The task is binary classification, and ROC AUC is the primary metric to maximize.","source":["E1"],"polarity":"fact"},{"id":"C2","text":"The development dataset has 2,362 rows and 13 encoded features, with no missing values reported.","source":["E1"],"polarity":"fact"},{"id":"C3","text":"The class distribution is imbalanced: the shares are 0.8429 and 0.1571.","source":["E1"],"polarity":"concern"},{"id":"C4","text":"The reported mean CV ROC AUC values range from 0.9390 to 0.9885 across the evaluated methods.","source":["E2","E3","E4","E5","E6"],"polarity":"fact"},{"id":"C5","text":"The three highest reported mean CV ROC AUC values are close together: 0.9857, 0.9883, and 0.9885.","source":["E3","E4","E5"],"polarity":"fact"},{"id":"C6","text":"The supplied evidence reports fold scores but does not provide results of paired-fold significance tests.","source":["E2","E3","E4","E5","E6"],"polarity":"concern"},{"id":"C7","text":"Reported out-of-fold ECE and Brier scores vary across methods, so calibration-related measures do not all rank them identically.","source":["E2","E3","E4","E5","E6"],"polarity":"fact"}]}
```

## Call 2: `candidates`

- request_hash: `019735754a82bc7cdba8b781739f41dc487b4a93595f81f63bd83d7b11c80fc1`
- seed / replicate: 1
- visible token cap: 300
- recorded `model`: `gpt-6-luna`
- recorded `resolved_model`: `gpt-6-luna`
- recorded `temperature`: `NOT_CONFIGURABLE`
- recorded `reasoning`: `{'effort': 'medium', 'thinking': 'always on (provider)', 'allowance': 16000}`
- recorded `max_tokens_sent`: `16300`
- recorded `structured_output`: `json_schema strict (strict_schema)`
- recorded `prompt_tokens`: `1063`
- recorded `output_tokens`: `185`
- recorded `reasoning_tokens`: `82`
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

CLAIM NODES:
C1 [fact; E1]: The task is binary classification, and ROC AUC is the primary metric to maximize.
C2 [fact; E1]: The development dataset has 2,362 rows and 13 encoded features, with no missing values reported.
C3 [concern; E1]: The class distribution is imbalanced: the shares are 0.8429 and 0.1571.
C4 [fact; E2,E3,E4,E5,E6]: The reported mean CV ROC AUC values range from 0.9390 to 0.9885 across the evaluated methods.
C5 [fact; E3,E4,E5]: The three highest reported mean CV ROC AUC values are close together: 0.9857, 0.9883, and 0.9885.
C6 [concern; E2,E3,E4,E5,E6]: The supplied evidence reports fold scores but does not provide results of paired-fold significance tests.
C7 [fact; E2,E3,E4,E5,E6]: Reported out-of-fold ECE and Brier scores vary across methods, so calibration-related measures do not all rank them identically.

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
{"candidates":[{"option":"random_forest","description":"Compare as one of the top-performing families, with mean CV ROC AUC 0.9857."},{"option":"lightgbm","description":"Compare as a top-performing family, with mean CV ROC AUC 0.9883."},{"option":"catboost","description":"Compare as a top-performing family, with the highest mean CV ROC AUC at 0.9885."}]}
```

## Call 3: `edges`

- request_hash: `4f5b09dce80badfb8f786658d325f9edc1844dae9687fe11115315eecc902540`
- seed / replicate: 1
- visible token cap: 1200
- recorded `model`: `gpt-6-luna`
- recorded `resolved_model`: `gpt-6-luna`
- recorded `temperature`: `NOT_CONFIGURABLE`
- recorded `reasoning`: `{'effort': 'medium', 'thinking': 'always on (provider)', 'allowance': 16000}`
- recorded `max_tokens_sent`: `17200`
- recorded `structured_output`: `json_schema strict (strict_schema)`
- recorded `prompt_tokens`: `1149`
- recorded `output_tokens`: `1281`
- recorded `reasoning_tokens`: `1080`
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

CLAIM NODES:
C1 [fact; E1]: The task is binary classification, and ROC AUC is the primary metric to maximize.
C2 [fact; E1]: The development dataset has 2,362 rows and 13 encoded features, with no missing values reported.
C3 [concern; E1]: The class distribution is imbalanced: the shares are 0.8429 and 0.1571.
C4 [fact; E2,E3,E4,E5,E6]: The reported mean CV ROC AUC values range from 0.9390 to 0.9885 across the evaluated methods.
C5 [fact; E3,E4,E5]: The three highest reported mean CV ROC AUC values are close together: 0.9857, 0.9883, and 0.9885.
C6 [concern; E2,E3,E4,E5,E6]: The supplied evidence reports fold scores but does not provide results of paired-fold significance tests.
C7 [fact; E2,E3,E4,E5,E6]: Reported out-of-fold ECE and Brier scores vary across methods, so calibration-related measures do not all rank them identically.

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
{"edges":[{"claim":"C1","candidate":"random_forest","relation":"supports"},{"claim":"C1","candidate":"lightgbm","relation":"supports"},{"claim":"C1","candidate":"catboost","relation":"supports"},{"claim":"C4","candidate":"random_forest","relation":"supports"},{"claim":"C4","candidate":"lightgbm","relation":"supports"},{"claim":"C4","candidate":"catboost","relation":"supports"},{"claim":"C5","candidate":"random_forest","relation":"supports"},{"claim":"C5","candidate":"lightgbm","relation":"supports"},{"claim":"C5","candidate":"catboost","relation":"supports"},{"claim":"C6","candidate":"random_forest","relation":"contradicts"},{"claim":"C6","candidate":"lightgbm","relation":"contradicts"},{"claim":"C6","candidate":"catboost","relation":"contradicts"}],"claim_conflicts":[]}
```

## Call 4: `aggregate`

- request_hash: `d45730eb3fc75de9da3295f50d721572b9f640ed27b6aaa05012a73f110796d5`
- seed / replicate: 1
- visible token cap: 250
- recorded `model`: `gpt-6-luna`
- recorded `resolved_model`: `gpt-6-luna`
- recorded `temperature`: `NOT_CONFIGURABLE`
- recorded `reasoning`: `{'effort': 'medium', 'thinking': 'always on (provider)', 'allowance': 16000}`
- recorded `max_tokens_sent`: `16250`
- recorded `structured_output`: `json_schema strict (strict_schema)`
- recorded `prompt_tokens`: `1152`
- recorded `output_tokens`: `202`
- recorded `reasoning_tokens`: `153`
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

CLAIM NODES:
C1 [fact; E1]: The task is binary classification, and ROC AUC is the primary metric to maximize.
C2 [fact; E1]: The development dataset has 2,362 rows and 13 encoded features, with no missing values reported.
C3 [concern; E1]: The class distribution is imbalanced: the shares are 0.8429 and 0.1571.
C4 [fact; E2,E3,E4,E5,E6]: The reported mean CV ROC AUC values range from 0.9390 to 0.9885 across the evaluated methods.
C5 [fact; E3,E4,E5]: The three highest reported mean CV ROC AUC values are close together: 0.9857, 0.9883, and 0.9885.
C6 [concern; E2,E3,E4,E5,E6]: The supplied evidence reports fold scores but does not provide results of paired-fold significance tests.
C7 [fact; E2,E3,E4,E5,E6]: Reported out-of-fold ECE and Brier scores vary across methods, so calibration-related measures do not all rank them identically.

GRAPH: candidate scores after propagation {'random_forest': 1.5, 'lightgbm': 1.5, 'catboost': 1.5}; claims shared by the top two candidates ['C1', 'C4', 'C5', 'C6']; claim conflicts [].
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
{"merge_possible":false,"merged_option":"NONE","unresolved_conflicts":["Paired-fold significance tests are not provided, so it is unclear whether the top candidates are statistically distinguishable."]}
```

## Call 5: `decide`

- request_hash: `9ee7ea21128e4183099542b0518e7efcaa6cb7ff66ea4b4462982734ed2ace47`
- seed / replicate: 1
- visible token cap: 300
- recorded `model`: `gpt-6-luna`
- recorded `resolved_model`: `gpt-6-luna`
- recorded `temperature`: `NOT_CONFIGURABLE`
- recorded `reasoning`: `{'effort': 'medium', 'thinking': 'always on (provider)', 'allowance': 16000}`
- recorded `max_tokens_sent`: `16300`
- recorded `structured_output`: `json_schema strict (strict_schema)`
- recorded `prompt_tokens`: `1252`
- recorded `output_tokens`: `448`
- recorded `reasoning_tokens`: `354`
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

CLAIM NODES:
C1 [fact; E1]: The task is binary classification, and ROC AUC is the primary metric to maximize.
C2 [fact; E1]: The development dataset has 2,362 rows and 13 encoded features, with no missing values reported.
C3 [concern; E1]: The class distribution is imbalanced: the shares are 0.8429 and 0.1571.
C4 [fact; E2,E3,E4,E5,E6]: The reported mean CV ROC AUC values range from 0.9390 to 0.9885 across the evaluated methods.
C5 [fact; E3,E4,E5]: The three highest reported mean CV ROC AUC values are close together: 0.9857, 0.9883, and 0.9885.
C6 [concern; E2,E3,E4,E5,E6]: The supplied evidence reports fold scores but does not provide results of paired-fold significance tests.
C7 [fact; E2,E3,E4,E5,E6]: Reported out-of-fold ECE and Brier scores vary across methods, so calibration-related measures do not all rank them identically.

GRAPH SUMMARY:
Candidate scores (support minus contradiction, conflicted claims down-weighted): {'random_forest': 1.5, 'lightgbm': 1.5, 'catboost': 1.5}.
Reused claims (linked to 2+ candidates): ['C1', 'C4', 'C5', 'C6'].
Claim conflicts: [].
Aggregation node: none. Unresolved conflicts: ['Paired-fold significance tests are not provided, so it is unclear whether the top candidates are statistically distinguishable.'].

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
{"decision":"UNDETERMINED","confidence":0.88,"evidence_refs":["E3","E4","E5"],"contradictions":[],"rationale_summary":"CatBoost has the highest mean ROC AUC, but its lead over LightGBM and random forest is small. Paired-fold significance results are absent, so the evidence cannot establish a defensible single production choice under the policy."}
```
