"""Four reasoning topologies with genuinely different execution semantics.

All four receive a byte-identical task prefix (system prompt, task, policy,
evidence, options), use the same model, temperature and seed, and end in the
same final-decision schema.  What differs is the *execution*:

DIRECT  1 call.  Decision only — a no-reasoning control arm.
COT     1 call.  The schema forces 3-6 ordered steps, each step must depend on
        the previous one, before the decision field is generated.
TOT     5 calls. propose 3 distinct candidate branches → evaluate each branch in
        an isolated call (it sees only its own branch) producing 2 refinement
        leaves + a branch score → deterministic pruning to the top 2 → a select
        call that sees only the surviving branches.
GOT     5 calls. extract atomic claim nodes (shared by every candidate) →
        generate candidate nodes → build typed edges (claim→candidate
        supports/contradicts, claim↔claim conflicts) → deterministic weighted
        propagation over the graph → recombination call (merge the top two
        candidates into an aggregate node when compatible) → decision over the
        graph summary.  Shared claims give candidates common parents, so the
        structure is a DAG with multi-parent nodes, not a tree.

Only structured, user-visible artifacts are stored.  No hidden reasoning exists
on this substrate and none is requested.
"""
from __future__ import annotations

import time
from typing import Any

from rs2610.common.llm import LLM

MODES = ("DIRECT", "COT", "TOT", "GOT")
UNDET = "UNDETERMINED"

SYSTEM = ("You are the analytical decision engine of an AutoML platform. You make one bounded decision from the evidence "
          "packet you are given. Use only the evidence and the policy shown; never invent numbers. Evidence ids look like E1, E2. "
          "If the evidence does not support a defensible single choice, choose UNDETERMINED. "
          "confidence is your probability (0-1) that your decision is the defensible one. Answer in JSON only.")


def render_prefix(inst: dict[str, Any]) -> str:
    ev = "\n".join(f"{e['id']}: {e['text']}" for e in inst["evidence"])
    pol = "\n".join(f"- {p}" for p in inst.get("policy", [])) or "- (none)"
    opts = "\n".join(f"- {o['id']}: {o['label']}" for o in inst["options"])
    return (f"TASK ({inst['family']}): {inst['question']}\n\nPOLICY:\n{pol}\n\nEVIDENCE:\n{ev}\n\nOPTIONS:\n{opts}\n\n")


def _decision_schema(option_ids: list[str], steps: bool = False) -> dict[str, Any]:
    props: dict[str, Any] = {}
    if steps:
        props["steps"] = {"type": "array", "minItems": 3, "maxItems": 6, "items": {
            "type": "object", "properties": {"step": {"type": "integer"}, "depends_on_step": {"type": "integer"},
                                             "uses_evidence": {"type": "array", "items": {"type": "string"}},
                                             "claim": {"type": "string"}},
            "required": ["step", "depends_on_step", "uses_evidence", "claim"]}}
    props.update({"decision": {"type": "string", "enum": option_ids}, "confidence": {"type": "number"},
                  "evidence_refs": {"type": "array", "items": {"type": "string"}},
                  "contradictions": {"type": "array", "items": {"type": "string"}},
                  "rationale_summary": {"type": "string"}})
    return {"type": "object", "properties": props, "required": list(props)}


FINAL_TAIL = ("Return decision, confidence, evidence_refs (ids you relied on), contradictions (each naming the conflicting "
              "evidence ids, e.g. 'E2 vs E5'; empty if none) and rationale_summary (at most 40 words).")


class Runner:
    def __init__(self, llm: LLM):
        self.llm = llm

    def _call(self, trace: dict[str, Any], stage: str, user: str, schema: dict[str, Any], seed: int, max_tokens: int,
              tag: dict[str, Any]) -> dict[str, Any] | None:
        r = self.llm.call(system=SYSTEM, user=user, schema=schema, seed=seed, max_tokens=max_tokens, tag={**tag, "stage": stage})
        trace["calls"].append({"stage": stage, "prompt_tokens": r.prompt_tokens, "output_tokens": r.output_tokens,
                               "latency_s": round(r.latency_s, 3), "compute_s": round((r.prefill_s or 0) + (r.decode_s or 0), 3) if r.decode_s is not None else None, "load_s": r.load_s, "parse_ok": r.parse_ok, "cached": r.cached,
                               "error": r.error, "request_hash": r.request_hash})
        if not r.parse_ok or r.content is None:
            trace["failures"].append({"stage": stage, "error": r.error or "parse_failure", "raw_head": r.raw[:300]})
            return None
        return r.content

    def run(self, inst: dict[str, Any], mode: str, seed: int) -> dict[str, Any]:
        trace: dict[str, Any] = {"mode": mode, "calls": [], "failures": [], "topology": {}}
        tag = {"study": "A", "instance": inst["instance_id"], "mode": mode, "seed": seed}
        t0 = time.time()
        out = getattr(self, f"_{mode.lower()}")(inst, seed, trace, tag)
        trace["wall_s"] = round(time.time() - t0, 3)
        trace["final"] = out
        return trace

    # ── DIRECT ──────────────────────────────────────────────────────────────
    def _direct(self, inst: dict, seed: int, trace: dict, tag: dict) -> dict | None:
        ids = [o["id"] for o in inst["options"]]
        user = render_prefix(inst) + "MODE: answer directly. Do not write reasoning steps. " + FINAL_TAIL
        trace["topology"] = {"nodes": 1, "edges": 0, "branches": 1}
        return self._call(trace, "direct", user, _decision_schema(ids), seed, 260, tag)

    # ── CHAIN OF THOUGHT ────────────────────────────────────────────────────
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

    # ── TREE OF THOUGHT ─────────────────────────────────────────────────────
    def _tot(self, inst: dict, seed: int, trace: dict, tag: dict) -> dict | None:
        ids = [o["id"] for o in inst["options"]]
        prefix = render_prefix(inst)
        prop = self._call(trace, "propose", prefix + (
            "MODE: tree search, stage 1/3 (propose). Propose exactly 3 DIFFERENT candidate options from OPTIONS as root branches. "
            "For each give the initial case for it (at most 30 words) and the evidence ids behind it. Do not decide yet."),
            {"type": "object", "properties": {"candidates": {"type": "array", "minItems": 3, "maxItems": 3, "items": {
                "type": "object", "properties": {"option": {"type": "string", "enum": ids}, "initial_case": {"type": "string"},
                                                 "evidence_refs": {"type": "array", "items": {"type": "string"}}},
                "required": ["option", "initial_case", "evidence_refs"]}}}, "required": ["candidates"]},
            seed, 450, tag)
        if not prop:
            return None
        seen: list[dict] = []
        for c in prop.get("candidates", []):
            if c.get("option") in ids and c["option"] not in [s["option"] for s in seen]:
                seen.append(c)
        duplicates = len(prop.get("candidates", [])) - len(seen)
        branches = []
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
        leaves = sum(len((b["eval"] or {}).get("refinements", [])) for b in branches)
        trace["topology"] = {"branches": len(branches), "leaves": leaves, "nodes": 1 + len(branches) + leaves,
                             "edges": len(branches) + leaves, "pruned": len(pruned), "duplicate_proposals": duplicates,
                             "depth": 2, "evaluated_alternatives": len(branches)}
        trace["structure"] = [{"option": b["option"], "score": b["score"], "kept": b in keep,
                               "leaf_scores": [r.get("score") for r in (b["eval"] or {}).get("refinements", [])]} for b in branches]
        summary = "\n".join(
            f"- branch '{b['option']}' score {b['score']:.0f}/10; refinements: "
            + "; ".join(f"{r.get('variant', '')[:80]} (score {r.get('score')}, supports {r.get('supports')}, risks {r.get('risks')})"
                        for r in (b["eval"] or {}).get("refinements", []))
            for b in keep)
        allowed = sorted({b["option"] for b in keep} | {UNDET}, key=ids.index)
        return self._call(trace, "select", prefix + (
            "MODE: tree search, stage 3/3 (select). After evaluation and pruning, these branches survive:\n" + summary +
            f"\nPruned branches: {[b['option'] for b in pruned]}.\nChoose among the surviving branches (or UNDETERMINED). " + FINAL_TAIL),
            _decision_schema(allowed), seed, 300, tag)

    # ── GRAPH OF THOUGHT ────────────────────────────────────────────────────
    def _got(self, inst: dict, seed: int, trace: dict, tag: dict) -> dict | None:
        ids = [o["id"] for o in inst["options"]]
        prefix = render_prefix(inst)
        ext = self._call(trace, "extract_claims", prefix + (
            "MODE: graph reasoning, stage 1/4 (claim nodes). Decompose the evidence and policy into 4-10 atomic claims that "
            "matter for this decision. Give each an id C1, C2, ..., the evidence ids it rests on, and polarity: 'fact' or 'concern'. "
            "Do not decide and do not mention options yet."),
            {"type": "object", "properties": {"claims": {"type": "array", "minItems": 4, "maxItems": 10, "items": {
                "type": "object", "properties": {"id": {"type": "string"}, "text": {"type": "string"},
                                                 "source": {"type": "array", "items": {"type": "string"}},
                                                 "polarity": {"type": "string", "enum": ["fact", "concern"]}},
                "required": ["id", "text", "source", "polarity"]}}}, "required": ["claims"]},
            seed, 900, tag)  # caps must never bind: DEVELOPMENT max was 609 at 650
        if not ext:
            return None
        claims = {c["id"]: c for c in ext.get("claims", []) if c.get("id")}
        ctext = "\n".join(f"{cid} [{c.get('polarity')}; {','.join(c.get('source', []))}]: {c.get('text', '')[:140]}" for cid, c in claims.items())
        cands = self._call(trace, "candidates", prefix + "CLAIM NODES:\n" + ctext + (
            "\n\nMODE: graph reasoning, stage 2/4 (candidate nodes). Name exactly 3 DIFFERENT candidate options from OPTIONS "
            "worth comparing, each with a one-line description."),
            {"type": "object", "properties": {"candidates": {"type": "array", "minItems": 3, "maxItems": 3, "items": {
                "type": "object", "properties": {"option": {"type": "string", "enum": ids}, "description": {"type": "string"}},
                "required": ["option", "description"]}}}, "required": ["candidates"]},
            seed, 300, tag)
        if not cands:
            return None
        cand_ids: list[str] = []
        for c in cands.get("candidates", []):
            if c.get("option") in ids and c["option"] not in cand_ids:
                cand_ids.append(c["option"])
        edges = self._call(trace, "edges", prefix + "CLAIM NODES:\n" + ctext + f"\n\nCANDIDATE NODES: {cand_ids}\n" + (
            "MODE: graph reasoning, stage 3/4 (edges). Link claims to candidates: for every claim that bears on a candidate add an "
            "edge with relation 'supports' or 'contradicts'. One claim may link to several candidates. Also list pairs of claims "
            "that conflict with each other."),
            {"type": "object", "properties": {
                "edges": {"type": "array", "items": {"type": "object", "properties": {
                    "claim": {"type": "string"}, "candidate": {"type": "string", "enum": cand_ids or ids},
                    "relation": {"type": "string", "enum": ["supports", "contradicts"]}}, "required": ["claim", "candidate", "relation"]}},
                "claim_conflicts": {"type": "array", "items": {"type": "object", "properties": {
                    "a": {"type": "string"}, "b": {"type": "string"}, "why": {"type": "string"}}, "required": ["a", "b", "why"]}}},
                "required": ["edges", "claim_conflicts"]},
            seed, 1200, tag)  # 1/41 DEVELOPMENT edge calls truncated at 700 (up to 10 claims x 3 candidates)
        if not edges:
            return None
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
        shared = sorted({e["claim"] for e in E if e["candidate"] == top2[0]} & {e["claim"] for e in E if e["candidate"] == top2[-1]}) if len(top2) == 2 else []
        merge = self._call(trace, "aggregate", prefix + "CLAIM NODES:\n" + ctext + (
            f"\n\nGRAPH: candidate scores after propagation {({c: round(score[c], 2) for c in ranked})}; "
            f"claims shared by the top two candidates {shared}; claim conflicts {[(c['a'], c['b']) for c in conflicts]}.\n"
            "MODE: graph reasoning, stage 4a (aggregation). Can the top two candidates be recombined into one option from OPTIONS "
            "that keeps the strengths of both (for example a model plus a remedy)? If yes give merged_option, else 'NONE'. "
            "List the conflicts that remain unresolved."),
            {"type": "object", "properties": {"merge_possible": {"type": "boolean"},
                                              "merged_option": {"type": "string", "enum": ids + ["NONE"]},
                                              "unresolved_conflicts": {"type": "array", "items": {"type": "string"}}},
             "required": ["merge_possible", "merged_option", "unresolved_conflicts"]},
            seed, 250, tag)
        merged = None
        if merge and merge.get("merge_possible") and merge.get("merged_option") in ids:
            merged = merge["merged_option"]
        n_nodes = len(claims) + len(cand_ids) + (1 if merged else 0) + 1
        n_edges = len(E) + len(conflicts) + (2 if merged else 0) + 1
        trace["topology"] = {"claim_nodes": len(claims), "candidate_nodes": len(cand_ids), "merged_nodes": 1 if merged else 0,
                             "nodes": n_nodes, "edges": n_edges, "claim_conflict_edges": len(conflicts),
                             "reused_claims": len(reused), "max_claim_fanout": max(fan.values()) if fan else 0,
                             "branching_factor": round(len(E) / max(1, len(claims)), 3),
                             "discarded_candidates": max(0, len(cand_ids) - 2),
                             "is_dag_beyond_tree": bool(reused) or bool(merged) or bool(conflicts),
                             "evaluated_alternatives": len(cand_ids)}
        trace["structure"] = {"scores": score, "reused_claims": reused, "conflicts": [(c["a"], c["b"]) for c in conflicts],
                              "claim_sources": {cid: list(c.get("source", []) or []) for cid, c in claims.items()},
                              "merged": merged, "edges": [(e["claim"], e["candidate"], e["relation"]) for e in E]}
        unresolved = (merge or {}).get("unresolved_conflicts", [])
        summary = (f"Candidate scores (support minus contradiction, conflicted claims down-weighted): "
                   f"{ {c: round(score[c], 2) for c in ranked} }.\nReused claims (linked to 2+ candidates): {reused}.\n"
                   f"Claim conflicts: {[(c['a'], c['b'], c['why'][:80]) for c in conflicts]}.\n"
                   f"Aggregation node: {merged or 'none'}. Unresolved conflicts: {unresolved}.")
        return self._call(trace, "decide", prefix + "CLAIM NODES:\n" + ctext + "\n\nGRAPH SUMMARY:\n" + summary + (
            "\n\nMODE: graph reasoning, stage 4b (decide over the graph). Choose the option best supported by the graph, or "
            "UNDETERMINED if unresolved conflicts make a single choice indefensible. " + FINAL_TAIL),
            _decision_schema(ids), seed, 300, tag)
