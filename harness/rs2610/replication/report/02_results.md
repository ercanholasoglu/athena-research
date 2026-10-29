## 6. A2 results: reasoning topology on a hosted model

{{r.design.a2.instances}} unseen decision instances on {{r.design.a2.datasets}} datasets, 3 replicates: 192 runs per
topology and model. `gpt-6-luna` ran {{r.design.a2.LUNA.runs|int}} runs in {{r.design.a2.LUNA.calls|int}} calls for
${{r.cost.a2.LUNA.usd|2}}. The `qwen2.5:7b` rows are the frozen Study A runs on the same instances. No run failed or
was truncated. Brackets are 95 % instance-cluster bootstrap intervals.

### 6.1 Accuracy

| | DIRECT | COT | TOT | GOT |
|---|---|---|---|---|
| `qwen2.5:7b` | {{r.a2.QWEN.DIRECT.accuracy|pct}} [{{r.a2.QWEN.DIRECT.acc_ci_lo|pct}}, {{r.a2.QWEN.DIRECT.acc_ci_hi|pct}}] | {{r.a2.QWEN.COT.accuracy|pct}} [{{r.a2.QWEN.COT.acc_ci_lo|pct}}, {{r.a2.QWEN.COT.acc_ci_hi|pct}}] | {{r.a2.QWEN.TOT.accuracy|pct}} [{{r.a2.QWEN.TOT.acc_ci_lo|pct}}, {{r.a2.QWEN.TOT.acc_ci_hi|pct}}] | {{r.a2.QWEN.GOT.accuracy|pct}} [{{r.a2.QWEN.GOT.acc_ci_lo|pct}}, {{r.a2.QWEN.GOT.acc_ci_hi|pct}}] |
| `gpt-6-luna` | {{r.a2.LUNA.DIRECT.accuracy|pct}} [{{r.a2.LUNA.DIRECT.acc_ci_lo|pct}}, {{r.a2.LUNA.DIRECT.acc_ci_hi|pct}}] | {{r.a2.LUNA.COT.accuracy|pct}} [{{r.a2.LUNA.COT.acc_ci_lo|pct}}, {{r.a2.LUNA.COT.acc_ci_hi|pct}}] | {{r.a2.LUNA.TOT.accuracy|pct}} [{{r.a2.LUNA.TOT.acc_ci_lo|pct}}, {{r.a2.LUNA.TOT.acc_ci_hi|pct}}] | {{r.a2.LUNA.GOT.accuracy|pct}} [{{r.a2.LUNA.GOT.acc_ci_lo|pct}}, {{r.a2.LUNA.GOT.acc_ci_hi|pct}}] |

**A2-W, within model** (topology − DIRECT, pp, Holm across six contrasts):

| | COT − DIRECT | TOT − DIRECT | GOT − DIRECT |
|---|---|---|---|
| `qwen2.5:7b` | {{r.a2.w.QWEN.DIRECT.COT.effect_b_minus_a|pp}} [{{r.a2.w.QWEN.DIRECT.COT.ci_lo|pp}}, {{r.a2.w.QWEN.DIRECT.COT.ci_hi|pp}}], p = {{r.a2.w.QWEN.DIRECT.COT.p_holm|p}} | {{r.a2.w.QWEN.DIRECT.TOT.effect_b_minus_a|pp}} [{{r.a2.w.QWEN.DIRECT.TOT.ci_lo|pp}}, {{r.a2.w.QWEN.DIRECT.TOT.ci_hi|pp}}], p = {{r.a2.w.QWEN.DIRECT.TOT.p_holm|p}} | {{r.a2.w.QWEN.DIRECT.GOT.effect_b_minus_a|pp}} [{{r.a2.w.QWEN.DIRECT.GOT.ci_lo|pp}}, {{r.a2.w.QWEN.DIRECT.GOT.ci_hi|pp}}], p = {{r.a2.w.QWEN.DIRECT.GOT.p_holm|p}} |
| `gpt-6-luna` | {{r.a2.w.LUNA.DIRECT.COT.effect_b_minus_a|pp}} [{{r.a2.w.LUNA.DIRECT.COT.ci_lo|pp}}, {{r.a2.w.LUNA.DIRECT.COT.ci_hi|pp}}], p = {{r.a2.w.LUNA.DIRECT.COT.p_holm|p}} | {{r.a2.w.LUNA.DIRECT.TOT.effect_b_minus_a|pp}} [{{r.a2.w.LUNA.DIRECT.TOT.ci_lo|pp}}, {{r.a2.w.LUNA.DIRECT.TOT.ci_hi|pp}}], p = {{r.a2.w.LUNA.DIRECT.TOT.p_holm|p}} | {{r.a2.w.LUNA.DIRECT.GOT.effect_b_minus_a|pp}} [{{r.a2.w.LUNA.DIRECT.GOT.ci_lo|pp}}, {{r.a2.w.LUNA.DIRECT.GOT.ci_hi|pp}}], p = {{r.a2.w.LUNA.DIRECT.GOT.p_holm|p}} |

On the hosted model, every structured topology was *less* accurate than a direct answer, and all three differences
survive Holm. GoT lost the most: {{r.a2.w.LUNA.DIRECT.GOT.effect_b_minus_a|pp}} pp. The baseline reproduces the
Study A null: no contrast is distinguishable.

**A2-M, model effect** (`gpt-6-luna` − `qwen2.5:7b`, pp, Holm across four topologies): DIRECT
{{r.a2.m.LUNA.DIRECT.effect_b_minus_a|pp}} [{{r.a2.m.LUNA.DIRECT.ci_lo|pp}}, {{r.a2.m.LUNA.DIRECT.ci_hi|pp}}],
p = {{r.a2.m.LUNA.DIRECT.p_holm|p}}; COT {{r.a2.m.LUNA.COT.effect_b_minus_a|pp}}, p = {{r.a2.m.LUNA.COT.p_holm|p}};
TOT {{r.a2.m.LUNA.TOT.effect_b_minus_a|pp}}, p = {{r.a2.m.LUNA.TOT.p_holm|p}}; GOT
{{r.a2.m.LUNA.GOT.effect_b_minus_a|pp}}, p = {{r.a2.m.LUNA.GOT.p_holm|p}}. The capability gain is significant only
when the model answers directly. Each added layer of structure shrinks it, and under GoT the point estimate reverses.

**A2-I, model × topology** (difference in differences, pp, sign-flip permutation, Holm across three): COT
{{r.a2.i.LUNA.COT.did|pp}} [{{r.a2.i.LUNA.COT.ci_lo|pp}}, {{r.a2.i.LUNA.COT.ci_hi|pp}}], p = {{r.a2.i.LUNA.COT.p_holm|p}};
TOT {{r.a2.i.LUNA.TOT.did|pp}} [{{r.a2.i.LUNA.TOT.ci_lo|pp}}, {{r.a2.i.LUNA.TOT.ci_hi|pp}}], p = {{r.a2.i.LUNA.TOT.p_holm|p}};
GOT {{r.a2.i.LUNA.GOT.did|pp}} [{{r.a2.i.LUNA.GOT.ci_lo|pp}}, {{r.a2.i.LUNA.GOT.ci_hi|pp}}], p = {{r.a2.i.LUNA.GOT.p_holm|p}}.
The interaction is significant and **negative** for GoT: the stronger model loses more from the graph than the 7B
model does.

### 6.2 Where the GoT loss comes from

The frozen scoring counts an abstention as wrong whenever the reference names a decision. Split by error type:

| | wrong | of which abstained | wrong option | accuracy if abstentions were neutral |
|---|---|---|---|---|
| `gpt-6-luna` DIRECT | {{r.a2.err.LUNA.DIRECT.wrong|int}} | {{r.a2.err.LUNA.DIRECT.wrong_abstained|int}} | {{r.a2.err.LUNA.DIRECT.wrong_option|int}} | {{r.a2.err.LUNA.DIRECT.accuracy_if_abstentions_were_neutral|pct}} |
| `gpt-6-luna` GOT | {{r.a2.err.LUNA.GOT.wrong|int}} | {{r.a2.err.LUNA.GOT.wrong_abstained|int}} | {{r.a2.err.LUNA.GOT.wrong_option|int}} | {{r.a2.err.LUNA.GOT.accuracy_if_abstentions_were_neutral|pct}} |
| `qwen2.5:7b` DIRECT | {{r.a2.err.QWEN.DIRECT.wrong|int}} | {{r.a2.err.QWEN.DIRECT.wrong_abstained|int}} | {{r.a2.err.QWEN.DIRECT.wrong_option|int}} | {{r.a2.err.QWEN.DIRECT.accuracy_if_abstentions_were_neutral|pct}} |
| `qwen2.5:7b` GOT | {{r.a2.err.QWEN.GOT.wrong|int}} | {{r.a2.err.QWEN.GOT.wrong_abstained|int}} | {{r.a2.err.QWEN.GOT.wrong_option|int}} | {{r.a2.err.QWEN.GOT.accuracy_if_abstentions_were_neutral|pct}} |

{{r.a2.err.LUNA.GOT.wrong_abstained|int}} of `gpt-6-luna`'s {{r.a2.err.LUNA.GOT.wrong|int}} GoT errors are
abstentions; it picked a wrong option fewer times under GoT than under DIRECT. The graph made the model decline to
decide, not decide badly. The "neutral" column is a descriptive re-reading, not the pre-registered metric, and the
pre-registered result stands: under the frozen contract, declining a decidable instance is an error. The
graphs themselves were richer, not poorer: `gpt-6-luna` GoT graphs held {{r.a2.topo.LUNA.GOT.topo_claim_nodes|1}}
claim nodes and {{r.a2.topo.LUNA.GOT.topo_reused_claims|1}} reused claims per run, but
{{r.a2.topo.LUNA.GOT.topo_claim_conflict_edges|1}} claim-conflict edges (baseline
{{r.a2.topo.QWEN.GOT.topo_claim_conflict_edges|1}}).

**H6, fidelity** (final decision = graph or tree top option; exploratory Fisher): GOT {{r.a2.fid.LUNA.GOT.frontier_rate|pct}}
vs baseline {{r.a2.fid.LUNA.GOT.baseline_rate|pct}}, p = {{r.a2.fid.LUNA.GOT.p_fisher_exploratory|p}}; TOT
{{r.a2.fid.LUNA.TOT.frontier_rate|pct}} vs {{r.a2.fid.LUNA.TOT.baseline_rate|pct}}, p = {{r.a2.fid.LUNA.TOT.p_fisher_exploratory|p}}.
Capability did not make the final call follow the structure any more often.

### 6.3 Adversarial instances and governance (H4, H5)

On the 24 adversarial instances (72 pairs per contrast, exploratory, Holm across three), no topology beat DIRECT for
either model: `gpt-6-luna` GOT − DIRECT {{r.a2.advt.LUNA.DIRECT.GOT.effect_b_minus_a|pp}} pp, p =
{{r.a2.advt.LUNA.DIRECT.GOT.p_holm|p}}; `qwen2.5:7b` TOT − DIRECT {{r.a2.advt.QWEN.DIRECT.TOT.effect_b_minus_a|pp}} pp,
p = {{r.a2.advt.QWEN.DIRECT.TOT.p_holm|p}}. H4 is not supported.

Governance block (3 instances × 3 replicates per cell, descriptive): `gpt-6-luna` DIRECT chose the forbidden option in
{{r.a2.adv.LUNA.governance_block.DIRECT.chose_forbidden|pct}} of runs, COT and TOT in
{{r.a2.adv.LUNA.governance_block.COT.chose_forbidden|pct}} and {{r.a2.adv.LUNA.governance_block.TOT.chose_forbidden|pct}},
but mostly by abstaining (abstention {{r.a2.adv.LUNA.governance_block.TOT.abstention_rate|pct}} under TOT). Structure
moved compliance and abstention together. With 9 runs per cell this is a direction to test, not a finding.

### 6.4 Calibration, consistency and cost

| `gpt-6-luna` | DIRECT | COT | TOT | GOT |
|---|---|---|---|---|
| ECE | {{r.a2.LUNA.DIRECT.ece|3}} | {{r.a2.LUNA.COT.ece|3}} | {{r.a2.LUNA.TOT.ece|3}} | {{r.a2.LUNA.GOT.ece|3}} |
| consistency (3 replicates agree) | {{r.a2.LUNA.DIRECT.consistency|pct}} | {{r.a2.LUNA.COT.consistency|pct}} | {{r.a2.LUNA.TOT.consistency|pct}} | {{r.a2.LUNA.GOT.consistency|pct}} |
| abstention | {{r.a2.LUNA.DIRECT.abstention_rate|pct}} | {{r.a2.LUNA.COT.abstention_rate|pct}} | {{r.a2.LUNA.TOT.abstention_rate|pct}} | {{r.a2.LUNA.GOT.abstention_rate|pct}} |
| output tokens per decision (reasoning incl.) | {{r.a2.LUNA.DIRECT.output_tokens_mean|int}} | {{r.a2.LUNA.COT.output_tokens_mean|int}} | {{r.a2.LUNA.TOT.output_tokens_mean|int}} | {{r.a2.LUNA.GOT.output_tokens_mean|int}} |
| client wall time per decision (s) | {{r.a2.LUNA.DIRECT.client_wall_s_mean|1}} | {{r.a2.LUNA.COT.client_wall_s_mean|1}} | {{r.a2.LUNA.TOT.client_wall_s_mean|1}} | {{r.a2.LUNA.GOT.client_wall_s_mean|1}} |
| correct decisions per US$ | {{r.a2.LUNA.DIRECT.correct_per_usd|int}} | {{r.a2.LUNA.COT.correct_per_usd|int}} | {{r.a2.LUNA.TOT.correct_per_usd|int}} | {{r.a2.LUNA.GOT.correct_per_usd|int}} |

GoT was the worst-calibrated mode on the hosted model (baseline GOT ECE {{r.a2.QWEN.GOT.ece|3}}). DIRECT gave
{{r.a2.LUNA.DIRECT.correct_per_usd|int}} correct decisions per dollar, GoT {{r.a2.LUNA.GOT.correct_per_usd|int}}.

### 6.5 Verdict on the A2 hypotheses

| | Verdict |
|---|---|
| H1: topology does not help at either level | **Supported**, more strongly than planned: on `gpt-6-luna` structure is significantly harmful |
| H2: stronger models exploit ToT/GoT | **Not supported**; the GoT interaction is significant in the opposite direction |
| H3: capability raises accuracy, topology adds little | **Supported** at DIRECT; topology removes most of the gain |
| H4: topology helps only on adversarial decisions | **Not supported** (exploratory) |
| H5: structure improves compliance, not accuracy | Untestable by design (n = 9 per cell); descriptively, compliance rose with abstention |
| H6: richer graph, final call ignores it | Fidelity unchanged by capability; graphs had no conflict edges on the hosted model |

## 7. B2 results: semantic context on hosted models

Units are (dataset, replicate): 8 per cell for `qwen2.5:7b` ({{r.design.b2.QWEN.runs|int}} runs) and `gpt-6-luna`
({{r.design.b2.LUNA.runs|int}} runs, ${{r.cost.b2.LUNA.usd|2}}), **4** for `claude-sonnet-5-5`
({{r.design.b2.SONNET.runs|int}} runs, ${{r.cost.b2.SONNET.usd|2}}). With 4 units the smallest attainable two-sided
sign-test p is 0.125, so **no Sonnet contrast can reach significance**; its numbers are descriptive.

### 7.1 Semantic decisions and leakage

| cell | core semantic accuracy: qwen / luna / sonnet | all traps blocked: qwen / luna / sonnet | deploy collapse: qwen / luna / sonnet |
|---|---|---|---|
| trapped A_RAW | {{r.b2.QWEN.A_RAW.core_semantic_accuracy|pct}} / {{r.b2.LUNA.A_RAW.core_semantic_accuracy|pct}} / {{r.b2.SONNET.A_RAW.core_semantic_accuracy|pct}} | {{r.b2.QWEN.A_RAW.all_traps_blocked|pct}} / {{r.b2.LUNA.A_RAW.all_traps_blocked|pct}} / {{r.b2.SONNET.A_RAW.all_traps_blocked|pct}} | {{r.b2.QWEN.A_RAW.deploy_collapse|pct}} / {{r.b2.LUNA.A_RAW.deploy_collapse|pct}} / {{r.b2.SONNET.A_RAW.deploy_collapse|pct}} |
| trapped C_DICT | {{r.b2.QWEN.C_DICT.core_semantic_accuracy|pct}} / {{r.b2.LUNA.C_DICT.core_semantic_accuracy|pct}} / {{r.b2.SONNET.C_DICT.core_semantic_accuracy|pct}} | {{r.b2.QWEN.C_DICT.all_traps_blocked|pct}} / {{r.b2.LUNA.C_DICT.all_traps_blocked|pct}} / {{r.b2.SONNET.C_DICT.all_traps_blocked|pct}} | {{r.b2.QWEN.C_DICT.deploy_collapse|pct}} / {{r.b2.LUNA.C_DICT.deploy_collapse|pct}} / {{r.b2.SONNET.C_DICT.deploy_collapse|pct}} |
| trapped D_RULES | {{r.b2.QWEN.D_RULES.core_semantic_accuracy|pct}} / {{r.b2.LUNA.D_RULES.core_semantic_accuracy|pct}} / {{r.b2.SONNET.D_RULES.core_semantic_accuracy|pct}} | {{r.b2.QWEN.D_RULES.all_traps_blocked|pct}} / {{r.b2.LUNA.D_RULES.all_traps_blocked|pct}} / {{r.b2.SONNET.D_RULES.all_traps_blocked|pct}} | {{r.b2.QWEN.D_RULES.deploy_collapse|pct}} / {{r.b2.LUNA.D_RULES.deploy_collapse|pct}} / {{r.b2.SONNET.D_RULES.deploy_collapse|pct}} |
| anonymized A_RAW | {{r.b2.QWEN.anon_A_RAW.core_semantic_accuracy|pct}} / {{r.b2.LUNA.anon_A_RAW.core_semantic_accuracy|pct}} / {{r.b2.SONNET.anon_A_RAW.core_semantic_accuracy|pct}} | {{r.b2.QWEN.anon_A_RAW.all_traps_blocked|pct}} / {{r.b2.LUNA.anon_A_RAW.all_traps_blocked|pct}} / {{r.b2.SONNET.anon_A_RAW.all_traps_blocked|pct}} | {{r.b2.QWEN.anon_A_RAW.deploy_collapse|pct}} / {{r.b2.LUNA.anon_A_RAW.deploy_collapse|pct}} / {{r.b2.SONNET.anon_A_RAW.deploy_collapse|pct}} |
| anonymized C_DICT | {{r.b2.QWEN.anon_C_DICT.core_semantic_accuracy|pct}} / {{r.b2.LUNA.anon_C_DICT.core_semantic_accuracy|pct}} / {{r.b2.SONNET.anon_C_DICT.core_semantic_accuracy|pct}} | {{r.b2.QWEN.anon_C_DICT.all_traps_blocked|pct}} / {{r.b2.LUNA.anon_C_DICT.all_traps_blocked|pct}} / {{r.b2.SONNET.anon_C_DICT.all_traps_blocked|pct}} | {{r.b2.QWEN.anon_C_DICT.deploy_collapse|pct}} / {{r.b2.LUNA.anon_C_DICT.deploy_collapse|pct}} / {{r.b2.SONNET.anon_C_DICT.deploy_collapse|pct}} |
| misleading D_RULES | {{r.b2.QWEN.mislead_D_RULES.core_semantic_accuracy|pct}} / {{r.b2.LUNA.mislead_D_RULES.core_semantic_accuracy|pct}} / {{r.b2.SONNET.mislead_D_RULES.core_semantic_accuracy|pct}} | {{r.b2.QWEN.mislead_D_RULES.all_traps_blocked|pct}} / {{r.b2.LUNA.mislead_D_RULES.all_traps_blocked|pct}} / {{r.b2.SONNET.mislead_D_RULES.all_traps_blocked|pct}} | {{r.b2.QWEN.mislead_D_RULES.deploy_collapse|pct}} / {{r.b2.LUNA.mislead_D_RULES.deploy_collapse|pct}} / {{r.b2.SONNET.mislead_D_RULES.deploy_collapse|pct}} |

Two patterns are clear descriptively:
- With meaningful column names (trapped), both hosted models were near the ceiling on core semantic accuracy
  **without** documentation. Documentation mainly closed the remaining trap gaps.
- With anonymized names and no dictionary, every model failed to block all traps
  ({{r.b2.QWEN.anon_A_RAW.all_traps_blocked|pct}} / {{r.b2.LUNA.anon_A_RAW.all_traps_blocked|pct}} /
  {{r.b2.SONNET.anon_A_RAW.all_traps_blocked|pct}}). A correct dictionary restored it for the hosted models.

**B2-S, semantic effect within model** (Holm across four contrasts). For `gpt-6-luna`, anonymized C_DICT − A_RAW is
significant on all traps blocked ({{r.b2.s.LUNA.all_traps_blocked.anon_C_DICT_vs_anon_A_RAW.effect|pp}} pp, p =
{{r.b2.s.LUNA.all_traps_blocked.anon_C_DICT_vs_anon_A_RAW.p_holm_sign|p}}) and on leak inflation
({{r.b2.s.LUNA.leak_inflation.anon_C_DICT_vs_anon_A_RAW.effect|3}}, p =
{{r.b2.s.LUNA.leak_inflation.anon_C_DICT_vs_anon_A_RAW.p_holm_sign|p}}). On trapped data, D_RULES − A_RAW on all traps
blocked was {{r.b2.s.LUNA.all_traps_blocked.D_RULES_vs_A_RAW.effect|pp}} pp, p =
{{r.b2.s.LUNA.all_traps_blocked.D_RULES_vs_A_RAW.p_holm_sign|p}}. No `qwen2.5:7b` semantic contrast survives Holm at 8
units (its D_RULES − A_RAW on all traps blocked: {{r.b2.s.QWEN.all_traps_blocked.D_RULES_vs_A_RAW.effect|pp}} pp).

**B2-M, model effect.** `gpt-6-luna` − baseline is large and consistent in direction (for example core semantic
accuracy on trapped A_RAW {{r.b2.m.LUNA.core_semantic_accuracy.A_RAW.effect|pp}} pp, raw sign p =
{{r.b2.m.LUNA.core_semantic_accuracy.A_RAW.p_sign|p}}), but with 8 units and Holm across 10 cells only one metric
survives correction: detecting falsified dictionary entries, on misleading D_RULES
({{r.b2.m.LUNA.falsified_detected_recall.mislead_D_RULES.effect|pp}} pp, p =
{{r.b2.m.LUNA.falsified_detected_recall.mislead_D_RULES.p_holm|p}}) and misleading E_FULL
({{r.b2.m.LUNA.falsified_detected_recall.mislead_E_FULL.effect|pp}} pp, p =
{{r.b2.m.LUNA.falsified_detected_recall.mislead_E_FULL.p_holm|p}}).

**B2-X, model × semantics.** No interaction on a decision metric reached p < 0.05; the one raw hit is on the share of
multi-column invented features ({{r.b2.x.LUNA.inv_multi_column_share.D_RULES_vs_A_RAW.did|pp}} pp, p =
{{r.b2.x.LUNA.inv_multi_column_share.D_RULES_vs_A_RAW.p_perm|p}}, uncorrected, one of 96 tests across both hosted models).

### 7.2 Feature invention: quality versus explanation

Invented features over all cells, by validator class:

| | VALID_USEFUL | VALID_NOT_USEFUL | INVALID_HIGH_APPARENT | INVALID_LOW_GAIN | NOT_EXECUTABLE |
|---|---|---|---|---|---|
| `qwen2.5:7b` | {{r.b2.fc.QWEN.invention.VALID_USEFUL|int}} | {{r.b2.fc.QWEN.invention.VALID_NOT_USEFUL|int}} | {{r.b2.fc.QWEN.invention.INVALID_HIGH_APPARENT|int}} | {{r.b2.fc.QWEN.invention.INVALID_LOW_GAIN|int}} | {{r.b2.fc.QWEN.invention.NOT_EXECUTABLE|int}} |
| `gpt-6-luna` | {{r.b2.fc.LUNA.invention.VALID_USEFUL|int}} | {{r.b2.fc.LUNA.invention.VALID_NOT_USEFUL|int}} | {{r.b2.fc.LUNA.invention.INVALID_HIGH_APPARENT|int}} | {{r.b2.fc.LUNA.invention.INVALID_LOW_GAIN|int}} | {{r.b2.fc.LUNA.invention.NOT_EXECUTABLE|int}} |
| `claude-sonnet-5-5` | {{r.b2.fc.SONNET.invention.VALID_USEFUL|int}} | {{r.b2.fc.SONNET.invention.VALID_NOT_USEFUL|int}} | {{r.b2.fc.SONNET.invention.INVALID_HIGH_APPARENT|int}} | {{r.b2.fc.SONNET.invention.INVALID_LOW_GAIN|int}} | {{r.b2.fc.SONNET.invention.NOT_EXECUTABLE|int}} |

- **Capability changed safety and validity.** On trapped A_RAW, the share of executable inventions was
  {{r.b2.QWEN.A_RAW.inv_executable_share|pct}} / {{r.b2.LUNA.A_RAW.inv_executable_share|pct}} /
  {{r.b2.SONNET.A_RAW.inv_executable_share|pct}} (qwen / luna / sonnet) and the leaky share
  {{r.b2.QWEN.A_RAW.inv_leaky_share|pct}} / {{r.b2.LUNA.A_RAW.inv_leaky_share|pct}} / {{r.b2.SONNET.A_RAW.inv_leaky_share|pct}}.
- **Capability did not change usefulness.** The best held-out gain (test-split ROC-AUC) from any invented feature
  stayed tiny for every model (trapped A_RAW: {{r.b2.QWEN.A_RAW.inv_best_test_gain|3}} / {{r.b2.LUNA.A_RAW.inv_best_test_gain|3}} /
  {{r.b2.SONNET.A_RAW.inv_best_test_gain|3}}). The VALID_USEFUL share never exceeded
  {{r.b2.QWEN.mislead_D_RULES.inv_valid_useful_share|pct}} in any cell for the baseline or
  {{r.b2.SONNET.B_SELF.inv_valid_useful_share|pct}} for the hosted models.
- **Self-assessment.** The baseline rated as leakage-free {{r.b2.QWEN.anon_A_RAW.inv_selfassess_missed_leak_share|pct}} of
  its anonymized A_RAW inventions that the validator found leaky. On trapped A_RAW the hosted models had no leaky
  feature to misjudge ({{r.b2.LUNA.A_RAW.inv_selfassess_missed_leak_share|pct}} /
  {{r.b2.SONNET.A_RAW.inv_selfassess_missed_leak_share|pct}}).
- **Semantics did not raise invention quality** for any model: no semantic contrast on a validator-class metric
  survives Holm.

By the pre-registered rule (section 7 of the plan), the supported statement is narrower than "semantics improved
explanation but not quality": documentation did not improve invention quality, and capability improved its safety
and validity but not its usefulness.
