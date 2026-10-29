## 1. Executive summary

This program asked two questions about LLM-assisted AutoML decisions, using one local model (`qwen2.5:7b`). Each study was
developed on DEVELOPMENT datasets, frozen (prompts, scoring, topologies, conditions and analysis hashed), and then evaluated
once on datasets it had never seen.

**Study A: does reasoning topology improve bounded AutoML decisions?** We compared DIRECT, COT, TOT and GOT on
{{design.A.UNSEEN.instances}} decisions over {{design.A.UNSEEN.datasets}} unseen datasets, with 3 seeds each
({{design.A.UNSEEN.runs|int}} runs). The topologies differ in execution, not prompt labels.

| | DIRECT | COT | TOT | GOT |
|---|---|---|---|---|
| decision accuracy | {{a.UNSEEN.DIRECT.accuracy|pct}} | {{a.UNSEEN.COT.accuracy|pct}} | {{a.UNSEEN.TOT.accuracy|pct}} | {{a.UNSEEN.GOT.accuracy|pct}} |
| server compute per decision, s | {{lat.A.UNSEEN.DIRECT.compute_mean|1}} | {{lat.A.UNSEEN.COT.compute_mean|1}} | {{lat.A.UNSEEN.TOT.compute_mean|1}} | {{lat.A.UNSEEN.GOT.compute_mean|1}} |

- **Accuracy.** We did not detect a statistically distinguishable difference between any pair (exact McNemar, Holm; all
  six Holm p = {{a.h.UNSEEN.H1.DIRECT.TOT.p_holm|2}}). Against DIRECT, the 95 % upper bounds on the benefit are
  {{a.h.UNSEEN.H1.DIRECT.TOT.ci_hi|pp}} pp for TOT and {{a.h.UNSEEN.H1.DIRECT.GOT.ci_hi|pp}} pp for GOT.
- **Adversarial evidence and uncertainty.** The predicted advantages (H2, H3) were not detected.
- **Efficiency.** DIRECT and COT deliver more accuracy per output token than TOT and GOT (H4, all four contrasts p < 0.001).
  TOT and GOT cost {{ax.UNSEEN.TOT.compute_vs_direct|1}}× and {{ax.UNSEEN.GOT.compute_vs_direct|1}}× the compute of DIRECT.
- **Behaviour (descriptive).** GOT was the most cautious and best calibrated (ECE {{a.UNSEEN.GOT.ece|3}}). DIRECT was the
  most repeatable across seeds ({{a.UNSEEN.DIRECT.consistency|pct}}). TOT named conflicting evidence most often.
- **Exploratory hypothesis.** TOT respected a policy that forbade the best scorer in
  {{a.adv.UNSEEN.governance_block.TOT.acc|pct}} of runs, against {{a.adv.UNSEEN.governance_block.COT.acc|pct}} for DIRECT
  and COT. This is 3 instances, so it is untestable here.

**Study B: does semantic context make AutoML decisions more correct and safer?** Five conditions, from the raw schema
(A_RAW) to dictionary + rules + a verification stage (E_FULL), were run on {{design.B.UNSEEN.datasets}} trapped unseen
datasets × 2 seeds. Each dataset had a planted target-ordered identifier, a post-outcome column and a warehouse artifact.

| | A_RAW | B_SELF | C_DICT | D_RULES | E_FULL |
|---|---|---|---|---|---|
| all traps blocked | {{b.UNSEEN.trapped.A_RAW.all_traps_blocked|pct}} | {{b.UNSEEN.trapped.B_SELF.all_traps_blocked|pct}} | {{b.UNSEEN.trapped.C_DICT.all_traps_blocked|pct}} | {{b.UNSEEN.trapped.D_RULES.all_traps_blocked|pct}} | {{b.UNSEEN.trapped.E_FULL.all_traps_blocked|pct}} |
| core semantic accuracy | {{b.UNSEEN.trapped.A_RAW.core_semantic_accuracy|pct}} | {{b.UNSEEN.trapped.B_SELF.core_semantic_accuracy|pct}} | {{b.UNSEEN.trapped.C_DICT.core_semantic_accuracy|pct}} | {{b.UNSEEN.trapped.D_RULES.core_semantic_accuracy|pct}} | {{b.UNSEEN.trapped.E_FULL.core_semantic_accuracy|pct}} |
| shipped model collapses in deployment | {{b.UNSEEN.trapped.A_RAW.deploy_collapse|pct}} | {{b.UNSEEN.trapped.B_SELF.deploy_collapse|pct}} | {{b.UNSEEN.trapped.C_DICT.deploy_collapse|pct}} | {{b.UNSEEN.trapped.D_RULES.deploy_collapse|pct}} | {{b.UNSEEN.trapped.E_FULL.deploy_collapse|pct}} |

- **Significant contrasts.** Two contrasts against A_RAW clear Holm at 0.05:
  - D_RULES on all traps blocked: {{b.paired.UNSEEN.trapped.all_traps_blocked.D_RULES.diff|pp}} pp, Holm p
    {{b.paired.UNSEEN.trapped.all_traps_blocked.D_RULES.holm_p|4}}.
  - E_FULL on core semantic accuracy: {{b.paired.UNSEEN.trapped.core_semantic_accuracy.E_FULL.diff|pp}} pp, Holm p
    {{b.paired.UNSEEN.trapped.core_semantic_accuracy.E_FULL.holm_p|4}}.
- **Fragility.** These verdicts are fragile. Excluding the one dataset whose calls hit token caps flips three Holm verdicts
  (exploratory sensitivity analysis), and changes no signs.
- **Verification stage.** It added cost ({{x.B.UNSEEN.E_FULL.all_traps_blocked.token_multiple|2}}× tokens) and no
  measurable leakage protection.
- **Missing definitions.** No condition noticed a missing dictionary definition.
- **Feature selection.** CV gain was the wrong signal: on UNSEEN, the {{bx.UNSEEN.cv_gain_top_all_leaky}} largest CV gains
  among {{bx.UNSEEN.cv_gain_ranked_n}} computable features were all leaky.

**Across both studies:**
- Adding model calls (topologies, verification, self-inference) did not buy measurable quality.
- Adding the data owner's information (dictionary, rules) did, at almost no cost.
- DEVELOPMENT rankings did not predict UNSEEN rankings in either study.

**Integrity.** Harness defects found during development are documented and the affected runs kept (section 24). Two issues
after the freeze were documented and not patched (section 24.1):
- token caps binding on the widest dataset;
- host sleep contaminating server timers, handled as UNKNOWN latency.

Nothing in Athena's production behaviour changed. Section 27 lists proposals only.
