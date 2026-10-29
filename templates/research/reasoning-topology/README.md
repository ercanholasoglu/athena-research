# Reasoning topology

Does how a model's reasoning is orchestrated, as a direct answer, a chain, a tree or a graph of calls, change the
quality of bounded AutoML decisions?

| part | model(s) | folder |
|---|---|---|
| Study A, original | `qwen2.5:7b` | [original-study/](original-study/) |
| Study A2, frontier replication | `qwen2.5:7b`, `gpt-6-luna` | [frontier-replication/](frontier-replication/) |

Both use the same frozen topologies, prompts, decision contracts and scoring:
[`harness/rs2610/study_a/`](../../harness/rs2610/study_a/). A2 adds only a provider substrate and a runner.

[`article-keys.json`](article-keys.json) lists the fact keys the article draft cites; the two TRACE files resolve
each of them to its table, row and run.
