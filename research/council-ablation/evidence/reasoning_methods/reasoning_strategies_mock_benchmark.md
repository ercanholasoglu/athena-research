<!-- Excerpt of the frozen offline mock-harness report. Mock runner; no real provider call. -->
Benchmark (llm/reasoning_benchmark.py, 6 configurations × 5 representative tasks):  NOT_RUN for a real provider
Mock runner (offline, deterministic answers from the packet, persona disagreement injected):
  configuration        calls  tokens   grounded  unsupported  directional  coverage  agreement
  deterministic_only     0        0      5/5         0            0          1.0        —
  single_llm             5     3 540     5/5         0            0          1.0        —
  council_vote          15    10 646     5/5         0            0          1.0       0.667
  chain_aggregation     15    10 646     5/5         0            0          1.0       0.667
  tree_aggregation      15    10 646     5/5         0            0          1.0       0.667
  graph_consensus       15    10 646     5/5         0            0          1.0       0.667
Defect injection: wrong_direction → 3 directional violations, grounded 2/5; invented_number → 5 unsupported, grounded 0/5.
Calls: ×3 for every council configuration; Tokens: ×3.0; Latency: mock; Cost: $0 (mock); Groundedness/Unsupported: see above.
```

No quality improvement is claimed for any configuration — with a mock runner the quality columns only prove the checks catch the
defects the product must catch. `GET /api/engineering/reasoning-benchmark` reads persisted runs (BenchmarkStore kind=reasoning) and
reports `real_provider_benchmark: NOT_RUN`. CLI: `python -m athena.llm.reasoning_benchmark --real --persist` (mock if no credential).

