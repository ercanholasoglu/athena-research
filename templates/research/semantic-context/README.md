# Semantic context

Does documentation of a table (a data dictionary, business rules, a verification pass) make a model's semantic
decisions safer and more correct? Do stronger models need it less, resist wrong documentation, and invent better
features?

| part | model(s) | folder |
|---|---|---|
| Study B, original | `qwen2.5:7b` | [original-study/](original-study/) |
| Study B2, frontier replication | `qwen2.5:7b`, `gpt-6-luna`, `claude-sonnet-5-5` | [frontier-replication/](frontier-replication/) |

Both use the same frozen profile, conditions, prompts, traps and scoring:
[`harness/rs2610/study_b/`](../../harness/rs2610/study_b/). B2 adds dictionary variants, a feature-invention call
and its validator: [`harness/rs2610/replication/b2/`](../../harness/rs2610/replication/b2/).

[`article-keys.json`](article-keys.json) lists the fact keys the article draft cites; the two TRACE files resolve
each of them to its table, row and run.
