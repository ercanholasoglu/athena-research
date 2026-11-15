# Limitations and benchmark scope

* **Ceiling effect — the main limitation.**
  - The strong single model answered 70 of 71 evaluation cases.
  - The largest gain any council could show was therefore +0.014, so the pre-registered REJECTED rule (upper CI
    bound of the gain < 0.02) is met by construction.
  - The result covers only governance questions that a frontier model already answers. Questions a frontier
    model gets wrong are out of scope.
* **Two provider families.**
  - The study had Anthropic (Sonnet 5.5, Haiku 5.5) and local Qwen 2.5 (7B, 1.5B, quantised).
  - The second family is much weaker, so provider count is confounded with member strength.
  - No three-vendor comparison was possible, and none is substituted.
* **Harness, not product.**
  - The harness called the models directly. It did not go through Athena's council endpoint, its evidence
    validator or tenant context.
  - Validator agreement and organization-context use are `NOT_MEASURED`.
* **One configuration.**
  - Claude models accept only temperature 1, so all Claude members carry sampling noise.
  - One prompt family was used.
* **Small segments.** For example, the ambiguous segment has n = 9. Segment CIs are wide.
* **Descriptive diversity analysis.** The 35 three-member combinations overlap and are not independent samples.
* **Authorship.**
  - The case author is also the harness author.
  - The single solo error (`feature_screening:29`) has a debatable reference answer, because the reference date
    is unstated.
* **Exploratory analyses are labelled.** Two analyses were not pre-registered:
  - the outvoted-critic observation;
  - the calibration table.
* **Other methods.**
  - **CoT / ToT / GoT in the product council:** these labels are aggregation steps, and only mock-runner evidence
    exists for them. CoT, ToT and GoT as reasoning orchestration are measured in Studies A and A2 of this
    repository, on bounded AutoML decisions, not on this case set.
  - **ReAct, Reflexion, Program-of-Thought, MCTS, self-consistency and the critic veto:** no result exists.
  - **Jev:** measured on a different corpus ([JEV retrospective](../jev/)). Those numbers are not comparable
    with the council numbers.
* **Cost.**
  - Cost is provider-reported; local models cost 0.
  - Jev cost is `UNKNOWN`, because the provider reports no price.
  - Council latency is ESTIMATED (slowest member plus judge).
  - Latency on a production network path is not measured.
* **Correction.** An earlier internal total of USD 1.04 counted the archived 300-token pass twice. The archive's
  rows are the first 1 210 rows of the final cache. The correct total for the 1 506 distinct calls is USD 0.71
  (notebook 06).
