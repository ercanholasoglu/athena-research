# Code excerpts (verbatim from the research harness)

Each block is cut by `replication/make_excerpts.py` from the file named, at the lines given. The file hash is the one recorded in the governing freeze record, so the excerpt is the code that ran. Nothing is simplified.

## DIRECT execution

`study_a/topologies.py` lines 92–96, file SHA-256 `6cda875f9c0a1176…`

```python
    def _direct(self, inst: dict, seed: int, trace: dict, tag: dict) -> dict | None:
        ids = [o["id"] for o in inst["options"]]
        user = render_prefix(inst) + "MODE: answer directly. Do not write reasoning steps. " + FINAL_TAIL
        trace["topology"] = {"nodes": 1, "edges": 0, "branches": 1}
        return self._call(trace, "direct", user, _decision_schema(ids), seed, 260, tag)
```

## CoT execution

`study_a/topologies.py` lines 99–112, file SHA-256 `6cda875f9c0a1176…`

```python
    def _cot(self, inst: dict, seed: int, trace: dict, tag: dict) -> dict | None:
        ids = [o["id"] for o in inst["options"]]
        user = (render_prefix(inst) + "MODE: reason in a single sequential chain. Write 3-6 steps; step k must build on step k-1 "
                "(depends_on_step = k-1, the first step uses 0) and cite the evidence ids it uses. Consider one line of reasoning "
                "only; do not enumerate and compare alternatives in parallel. After the last step give the decision. " + FINAL_TAIL)
        res = self._call(trace, "chain", user, _decision_schema(ids, steps=True), seed, 900, tag)
        if res:
            steps = res.get("steps", [])
            seq = all(s.get("depends_on_step") == i for i, s in enumerate(steps))
            trace["topology"] = {"nodes": len(steps) + 1, "edges": len(steps), "branches": 1, "steps": len(steps),
                                 "sequential_dependency_respected": seq,
                                 "evidence_refs_in_steps": sorted({e for s in steps for e in s.get("uses_evidence", [])})}
            trace["structure"] = [{"step": s.get("step"), "depends_on": s.get("depends_on_step"), "uses": s.get("uses_evidence")} for s in steps]
        return res
```

## ToT: isolated branch evaluation, deterministic pruning

`study_a/topologies.py` lines 134–155, file SHA-256 `6cda875f9c0a1176…`

```python
        for k, cand in enumerate(seen):
            ev = self._call(trace, f"evaluate_{k}", prefix + (
                f"MODE: tree search, stage 2/3 (evaluate ONE branch in isolation). Branch under evaluation: option "
                f"'{cand['option']}' — initial case: {cand['initial_case']}\n"
                "Expand it into exactly 2 refinements (each a concrete variant or condition of this option), list for each the "
                "supporting and the risk evidence ids and score it 1-10. Then give branch_score 1-10 for the branch as a whole and "
                "state whether it has a fatal flaw (policy violation, unsupported by evidence, or contradicted by evidence)."),
                {"type": "object", "properties": {
                    "refinements": {"type": "array", "minItems": 2, "maxItems": 2, "items": {"type": "object", "properties": {
                        "variant": {"type": "string"}, "supports": {"type": "array", "items": {"type": "string"}},
                        "risks": {"type": "array", "items": {"type": "string"}}, "score": {"type": "integer"}},
                        "required": ["variant", "supports", "risks", "score"]}},
                    "branch_score": {"type": "integer"}, "fatal_flaw": {"type": "boolean"}, "fatal_reason": {"type": "string"}},
                    "required": ["refinements", "branch_score", "fatal_flaw", "fatal_reason"]},
                seed, 450, tag)
            score = 0.0
            if ev:
                score = 0.0 if ev.get("fatal_flaw") else float(ev.get("branch_score", 0))
            branches.append({"option": cand["option"], "score": score, "eval": ev, "initial_case": cand["initial_case"]})
        ranked = sorted(branches, key=lambda b: -b["score"])
        keep = [b for b in ranked[:2] if b["score"] > 0] or ranked[:1]
        pruned = [b for b in branches if b not in keep]
```

## GoT: typed edges, deterministic propagation over the graph, aggregation input

`study_a/topologies.py` lines 218–232, file SHA-256 `6cda875f9c0a1176…`

```python
        E = [e for e in edges.get("edges", []) if e.get("claim") in claims and e.get("candidate") in cand_ids]
        E = [dict(t) for t in {tuple(sorted(e.items())) for e in E}]
        conflicts = [c for c in edges.get("claim_conflicts", []) if c.get("a") in claims and c.get("b") in claims and c["a"] != c["b"]]
        in_conflict = {c["a"] for c in conflicts} | {c["b"] for c in conflicts}
        # deterministic propagation: a claim carries weight 1, halved when it is in conflict; concerns count 1.5x on contradicts
        score = {c: 0.0 for c in cand_ids}
        for e in E:
            w = 0.5 if e["claim"] in in_conflict else 1.0
            if e["relation"] == "contradicts" and claims[e["claim"]].get("polarity") == "concern":
                w *= 1.5
            score[e["candidate"]] += w if e["relation"] == "supports" else -w
        fan = {cid: len({e["candidate"] for e in E if e["claim"] == cid}) for cid in claims}
        reused = [cid for cid, k in fan.items() if k >= 2]
        ranked = sorted(cand_ids, key=lambda c: -score[c])
        top2 = ranked[:2]
```

## Semantic condition construction

`study_b/conditions.py` lines 158–173, file SHA-256 `40387354965526a6…`

```python
def run_condition(llm: LLM, v: Variant, cond: str, seed: int, prof_rows: list[dict], dev_idx: Any, cands: list[dict],
                  tag: dict[str, Any]) -> dict[str, Any]:
    prof = render_profile(prof_rows, v)
    base = f"DATASET PROFILE (development split)\n{prof}\n{target_summary(v, dev_idx)}\n\n"
    doc = documentation(v, {"A_RAW": "none", "B_SELF": "none", "C_DICT": "dict", "D_RULES": "rules", "E_FULL": "rules"}[cond])
    trace: dict[str, Any] = {"condition": cond, "calls": [], "failures": []}

    def call(stage: str, user: str, schema: dict, max_tokens: int) -> dict | None:
        r = llm.call(system=SYSTEM, user=user + enum_legend(schema), schema=schema, seed=seed, max_tokens=max_tokens, tag={**tag, "stage": stage})
        trace["calls"].append({"stage": stage, "prompt_tokens": r.prompt_tokens, "output_tokens": r.output_tokens,
                               "latency_s": round(r.latency_s, 3), "compute_s": round((r.prefill_s or 0) + (r.decode_s or 0), 3) if r.decode_s is not None else None, "load_s": r.load_s, "parse_ok": r.parse_ok, "cached": r.cached, "request_hash": r.request_hash})
        if not r.parse_ok:
            trace["failures"].append({"stage": stage, "error": r.error or "parse_failure", "raw_head": r.raw[:300]})
        return r.content if r.parse_ok else None

    pre = ""
```

## Dictionary injection

`study_b/conditions.py` lines 142–155, file SHA-256 `40387354965526a6…`

```python
def documentation(v: Variant, level: str) -> str:
    if level == "none":
        return ""
    parts = [f"DATA OWNER DOCUMENTATION\nDescription: {v.description}", "Dictionary:"]
    parts += [f"- {c}: {d}" for c, d in v.dictionary.items()]
    if level == "rules":
        if v.rules:
            parts.append("Business rules:\n" + "\n".join(f"- {r}" for r in v.rules))
        if v.codes:
            parts.append("Code dictionary:\n" + "\n".join(f"- {c}: " + "; ".join(f"{k} = {m}" for k, m in codes.items())
                                                         for c, codes in v.codes.items()))
        if v.constraints:
            parts.append("Known constraints:\n" + "\n".join(f"- {r}" for r in v.constraints))
    return "\n".join(parts) + "\n\n"
```

## Feature-invention call (no candidates shown)

`replication/b2/invention.py` lines 57–65, file SHA-256 `0f0307d8043f0e3d…`

```python
def invent(llm: Any, v: Variant, cond: str, seed: int, prof_rows: list[dict], dev_idx: Any, tag: dict[str, Any]) -> dict[str, Any]:
    r = llm.call(system=SYSTEM, user=prompt(v, cond, prof_rows, dev_idx), schema=INVENT_SCHEMA, seed=seed, max_tokens=MAX_TOKENS,
                 tag={**tag, "stage": "feature_invention"})
    return {"call": {"stage": "feature_invention", "prompt_tokens": r.prompt_tokens, "output_tokens": r.output_tokens,
                     "latency_s": round(r.latency_s, 3),
                     "compute_s": round((r.prefill_s or 0) + (r.decode_s or 0), 3) if r.decode_s is not None else None,
                     "parse_ok": r.parse_ok, "cached": r.cached, "request_hash": r.request_hash, "error": r.error},
            "features": (r.content or {}).get("features") if r.parse_ok else None,
            "failure": None if r.parse_ok else {"error": r.error or "parse_failure", "raw_head": r.raw[:300]}}
```

## Feature validation: classes

`replication/b2/evaluate.py` lines 164–168, file SHA-256 `646bf92d32ba6acd…`

```python
    valid = not res["leakage"] and res["semantic_validity"] != "invalid"
    if valid:
        res["class"] = "VALID_USEFUL" if res["cv_gain"] > USEFUL_CV and res["test_gain_deploy"] > 0 else "VALID_NOT_USEFUL"
    else:
        res["class"] = "INVALID_HIGH_APPARENT" if res["cv_gain"] > HIGH_APPARENT_CV else "INVALID_LOW_GAIN"
```

## Frontier substrate: schema adaptation

`replication/providers.py` lines 86–108, file SHA-256 `db5bf881344cd1d7…`

```python
def strict_schema(schema: dict[str, Any], provider: str = "openai") -> dict[str, Any]:
    """The frozen schema plus ``additionalProperties: false`` on every object node (required by both providers'
    strict JSON-schema modes).  Property sets, required lists and enums are unchanged.  Anthropic's JSON-schema mode
    rejects array ``minItems`` / ``maxItems`` (400, 2026-10-29 smoke), so for that provider the bounds are dropped from
    the schema; the task text still states them, and the analysis keeps at most the frozen ``maxItems`` items."""
    s = copy.deepcopy(schema)

    def walk(n: Any) -> None:
        if isinstance(n, dict):
            if provider == "anthropic" and n.get("type") == "array":
                n.pop("minItems", None)
                n.pop("maxItems", None)
            if n.get("type") == "object":
                n.setdefault("additionalProperties", False)
                n.setdefault("properties", {})
                n.setdefault("required", list(n["properties"]))
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)
    walk(s)
    return s
```
