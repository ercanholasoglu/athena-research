# Study B2: semantic context with frontier models

Frozen on 2026-10-29. Amendment 1 moved the OpenAI arm to `gpt-6-luna`. Amendment 2 replaced `claude-opus-5-5` with
`claude-sonnet-5-5`, B2 only, 1 replicate. Both amendments were written before the amended arm ran. Full report:
[FRONTIER_REPLICATION_REPORT.md](../../../harness/rs2610/FRONTIER_REPLICATION_REPORT.md), sections 1–5 and 7–11.

## Design

- **Cells.** {{r.design.b2.datasets|int}} datasets × {{r.design.b2.cells|int}} cells, built by
  [`replication/b2/variants.py`](../../../harness/rs2610/replication/b2/variants.py) on the frozen Study B base:
  - trapped × A_RAW, B_SELF, C_DICT, D_RULES, E_FULL;
  - anonymized × A_RAW, C_DICT;
  - incomplete × D_RULES;
  - misleading × D_RULES, E_FULL.
- **Arms.**

  | arm | runs | calls | spend |
  |---|---|---|---|
  | `qwen2.5:7b` | {{r.design.b2.QWEN.runs|int}} | {{r.design.b2.QWEN.calls|int}} | local |
  | `gpt-6-luna` | {{r.design.b2.LUNA.runs|int}} | {{r.design.b2.LUNA.calls|int}} | ${{r.cost.b2.LUNA.usd|4}} |
  | `claude-sonnet-5-5` | {{r.design.b2.SONNET.runs|int}} | {{r.design.b2.SONNET.calls|int}} | ${{r.cost.b2.SONNET.usd|4}} |

- **Units.** One unit is a dataset × replicate: 8 per cell, 4 for Sonnet.
- **Prompts.** Each run's first call is byte-identical across models, and later calls share the system prompt, stage
  and token cap (`tools/export_prompts.py` checks it). The
  rendered analysis, invention and candidate hashes of every dataset × cell are in the freeze record, and
  `tools/verify_data.py` recomputes them.

### Feature invention

The schema and pipeline are in [feature-invention/](feature-invention/):

1. **Ask.** The model proposes up to 5 features with no candidate list shown. Each feature has an executable spec in
   a small DSL: one of 13 operations (`ratio`, `diff`, `log1p`, `gt_threshold`, …) over named input columns
   ([`invent_task.txt`](feature-invention/invent_task.txt), [`invent_schema.json`](feature-invention/invent_schema.json)).
2. **Validate.** The spec is checked deterministically: the operation, its inputs and whether they exist. It is then
   executed by `evaluate.compute`. A spec that fails here is NOT_EXECUTABLE.
3. **Check for leakage.** Inputs are checked against the evaluation-authority truth. A feature is leaky if it uses
   the target, a target-derived column, an identifier, an artifact or a post-outcome column. A separate rule-based
   semantic-validity check is also applied.
4. **Evaluate.** The feature is evaluated by cross-validation on the development split, and on the held-out split
   under deployment masking.
5. **Classify** ([`replication/b2/evaluate.py`](../../../harness/rs2610/replication/b2/evaluate.py)):
   - VALID_USEFUL: leak-free and semantically valid, CV gain > 0.001 and deployed held-out gain > 0;
   - VALID_NOT_USEFUL: otherwise valid;
   - INVALID_HIGH_APPARENT: leaky or invalid with CV gain > 0.005;
   - INVALID_LOW_GAIN: otherwise invalid;
   - NOT_EXECUTABLE: the spec could not be executed.

## Result

At A_RAW (no documentation), named columns:

| | `qwen2.5:7b` | `gpt-6-luna` | `claude-sonnet-5-5` |
|---|---|---|---|
| all traps blocked | {{r.b2.QWEN.A_RAW.all_traps_blocked|pct}} | {{r.b2.LUNA.A_RAW.all_traps_blocked|pct}} | {{r.b2.SONNET.A_RAW.all_traps_blocked|pct}} |
| core semantic accuracy | {{r.b2.QWEN.A_RAW.core_semantic_accuracy|pct}} | {{r.b2.LUNA.A_RAW.core_semantic_accuracy|pct}} | {{r.b2.SONNET.A_RAW.core_semantic_accuracy|pct}} |
| invented features executable | {{r.b2.QWEN.A_RAW.inv_executable_share|pct}} | {{r.b2.LUNA.A_RAW.inv_executable_share|pct}} | {{r.b2.SONNET.A_RAW.inv_executable_share|pct}} |
| invented features leaky | {{r.b2.QWEN.A_RAW.inv_leaky_share|pct}} | {{r.b2.LUNA.A_RAW.inv_leaky_share|pct}} | {{r.b2.SONNET.A_RAW.inv_leaky_share|pct}} |
| invented features valid and useful | {{r.b2.QWEN.A_RAW.inv_valid_useful_share|pct}} | {{r.b2.LUNA.A_RAW.inv_valid_useful_share|pct}} | {{r.b2.SONNET.A_RAW.inv_valid_useful_share|pct}} |
| best held-out gain of an invented feature (ROC-AUC) | {{r.b2.QWEN.A_RAW.inv_best_test_gain|3}} | {{r.b2.LUNA.A_RAW.inv_best_test_gain|3}} | {{r.b2.SONNET.A_RAW.inv_best_test_gain|3}} |

- **Capability plus meaningful names recovered much of the documentation benefit.** With named columns the hosted
  models blocked most traps without documentation.
- **The dictionary still mattered once the columns were anonymized.** For `gpt-6-luna`, all traps blocked went from
  {{r.b2.LUNA.anon_A_RAW.all_traps_blocked|pct}} (anonymized, A_RAW) to
  {{r.b2.LUNA.anon_C_DICT.all_traps_blocked|pct}} (anonymized, C_DICT), Holm p
  {{r.b2.s.LUNA.all_traps_blocked.anon_C_DICT_vs_anon_A_RAW.p_holm_sign|p}}.
- **Wrong documentation.**
  - Falsified entries detected (misleading, D_RULES): `qwen2.5:7b`
    {{r.b2.QWEN.mislead_D_RULES.falsified_detected_recall|pct}}, `gpt-6-luna`
    {{r.b2.LUNA.mislead_D_RULES.falsified_detected_recall|pct}} (Holm p
    {{r.b2.m.LUNA.falsified_detected_recall.mislead_D_RULES.p_holm|p}}), `claude-sonnet-5-5`
    {{r.b2.SONNET.mislead_D_RULES.falsified_detected_recall|pct}}.
  - Missing definitions detected (incomplete, D_RULES): {{r.b2.QWEN.incompl_D_RULES.missing_semantics_recall|pct}},
    {{r.b2.LUNA.incompl_D_RULES.missing_semantics_recall|pct}} and
    {{r.b2.SONNET.incompl_D_RULES.missing_semantics_recall|pct}}.
- **Invented features were safer but not more useful.** The hosted models' inventions were executable and rarely
  leaky. The highest valid-and-useful share in any model × cell was
  {{r.b2.QWEN.mislead_D_RULES.inv_valid_useful_share|pct}} (`qwen2.5:7b`, misleading D_RULES), and documentation did
  not change that.

## Folders

| folder | contents |
|---|---|
| [configs/](configs/) | governing freeze record, pre-registration, per-arm configuration |
| [variants/](variants/) | the 10 cells, runner |
| [feature-invention/](feature-invention/) | invention schema and task, validator, evaluation, feature classes |
| [prompts/examples/](prompts/examples/) | one dataset in all 10 cells on the baseline, replayed from the ledger; hosted identity is checked for every cell |
| [statistics/](statistics/) | model, documentation and interaction tests |
| [results/](results/) | aggregate and run-level tables, run records and ledgers for all three arms |
| [figures/](figures/) | all traps blocked, core semantic accuracy, invention classes (generated by `tools/replication_figures.py`) |
| [TRACE.md](TRACE.md) | article numbers → table, row, run, ledger, prompt, model, dataset hash |

## Limitations

- **Small samples.** 8 units per cell (4 for Sonnet), with Holm across 10 cells, so most large differences are
  descriptive. No Sonnet effect can reach significance with 4 units.
- **Development data.** `bank_marketing` was a Study B development dataset.
- **Data-cache incident.** The last 5 `qwen2.5:7b` runs were verified with a scoped freeze check
  ([HISTORY](../../../docs/HISTORY.md#the-disk-full-and-data-cache-incident-b2-qwen257b)).
- More: [docs/LIMITATIONS.md](../../../docs/LIMITATIONS.md).
