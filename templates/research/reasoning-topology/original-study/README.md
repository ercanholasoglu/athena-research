# Study A: reasoning topology with `qwen2.5:7b`

Pre-registered, frozen on 2026-10-28 and evaluated once on unseen data. Full report: sections on Study A in
[FINAL_RESEARCH_REPORT.md](../../../harness/rs2610/FINAL_RESEARCH_REPORT.md).
Design and hypotheses: [study-a-design.md](../../../harness/rs2610/outputs/study_a/study-a-design.md).

## What was compared

Four topologies whose **execution** differs, on the same task text, evidence packet and decision schema:

| mode | calls | execution |
|---|---|---|
| DIRECT | 1 | decision fields only |
| CoT | 1 | the schema forces 3–6 ordered steps; each step depends on the previous one and cites evidence ids; the decision comes after the steps |
| ToT | 5 | propose 3 branches → one isolated call per branch (2 scored refinement leaves, a fatal-flaw flag) → deterministic prune to the top 2 → select among the survivors |
| GoT | 5 | atomic claim nodes shared by all candidates → candidate nodes → typed edges (supports / contradicts / conflicts) → deterministic weighted propagation → aggregation call |

- **Topology code.** The implementation is [`study_a/topologies.py`](../../../harness/rs2610/study_a/topologies.py)
  (frozen; [topologies/](topologies/) lists it with its hash).
- **Excerpts.** Verbatim excerpts with line ranges are in
  [CODE_EXCERPTS.md](../../../harness/rs2610/outputs/replication/CODE_EXCERPTS.md).
- **Held fixed.** Model `qwen2.5:7b` (digest in the freeze record), temperature 0.4, `num_ctx` 12288, seed equal to
  the replicate index.
- **Decisions.** 10 decision families with closed options and rule-defined correct answers from measured evidence.
- **Data.** {{design.A.UNSEEN.instances|int}} unseen instances from {{design.A.UNSEEN.datasets|int}} datasets
  ({{design.A.UNSEEN.adversarial_instances|int}} adversarial), 3 seeds: {{design.A.UNSEEN.runs|int}} runs,
  {{design.A.UNSEEN.calls|int}} calls.

## Result (unseen split)

| mode | accuracy |
|---|---|
| DIRECT | {{a.UNSEEN.DIRECT.accuracy|pct}} |
| CoT | {{a.UNSEEN.COT.accuracy|pct}} |
| ToT | {{a.UNSEEN.TOT.accuracy|pct}} |
| GoT | {{a.UNSEEN.GOT.accuracy|pct}} |

- **H1 (topology vs DIRECT).** No topology was better than DIRECT. ToT − DIRECT = {{a.h.UNSEEN.H1.DIRECT.TOT.effect_b_minus_a|pp}}
  pp (Holm p {{a.h.UNSEEN.H1.DIRECT.TOT.p_holm|3}}), GoT − DIRECT = {{a.h.UNSEEN.H1.DIRECT.GOT.effect_b_minus_a|pp}} pp
  (Holm p {{a.h.UNSEEN.H1.DIRECT.GOT.p_holm|3}}). Non-significance is not shown equivalence.
- **Compute.** ToT used {{ax.UNSEEN.TOT.compute_vs_direct|1}}× and GoT {{ax.UNSEEN.GOT.compute_vs_direct|1}}× DIRECT's
  compute.
- **Material.** Every test, interval and correction is in
  [study-a-statistics.md](../../../harness/rs2610/outputs/study_a/study-a-statistics.md).

## Folders

| folder | contents |
|---|---|
| [configs/](configs/) | freeze record, pre-registered design |
| [topologies/](topologies/) | the four topology implementations |
| [contracts/](contracts/) | decision contracts, evidence packets, the instances as presented |
| [prompts/examples/](prompts/examples/) | the exact prompts and outputs of one instance in all four modes, replayed from the ledger (`tools/export_prompts.py`) |
| [evaluation/](evaluation/) | scoring and runner |
| [statistics/](statistics/) | tests, intervals, corrections |
| [results/](results/) | aggregate and run-level tables, run records, request ledger |
| [figures/](figures/) | figures |
| [TRACE.md](TRACE.md) | every article number → table, row, run, ledger, prompt, model, dataset hash |

## Limitations

- One local 7B model, one implementation per topology and one wording.
- Latency was affected by host suspend (post-freeze finding); compute is reported in tokens and calls.
- More: [docs/LIMITATIONS.md](../../../docs/LIMITATIONS.md).
