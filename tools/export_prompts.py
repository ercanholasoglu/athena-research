"""Export the exact prompts, schemas and outputs of real runs by replaying them through the frozen runners.

    python tools/export_prompts.py           # needs the prepared datasets for Study B / B2 (tools/prepare_data.py)

Nothing is re-rendered by hand and no model is called. Each runner is driven with a replay client that computes the
request hash exactly as the frozen client does (`common/llm.py` for the local model, `replication/providers.py` for
hosted models) and **refuses any request whose hash is not in the run ledger**. A prompt written here is therefore
byte-identical to the one that was sent: its hash is in the ledger, next to the recorded output.

Writes `research/*/*/prompts/examples/*.md` and `research/*/*/contracts/*.json`, plus `prompts/examples/INDEX.json`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "harness"))

import hashlib  # noqa: E402

from rs2610.common import llm as local  # noqa: E402
from rs2610.replication import providers  # noqa: E402

PKG = REPO / "harness" / "rs2610"
ART = PKG / "artifacts"
RES = REPO / "research"


class NotInLedger(RuntimeError):
    pass


class _Recorder:
    calls: list[dict[str, Any]]
    ledger_rel: str

    def _record(self, key: str, system: str, user: str, schema: dict, seed: int, max_tokens: int, tag: dict) -> None:
        if key not in self._cache:
            raise NotInLedger(f"{tag}: request hash {key[:12]} is not in {self.ledger_rel}")
        rec = self._cache[key]
        self.calls.append({"tag": tag, "request_hash": key, "system": system, "user": user, "schema": schema, "seed": seed,
                           "max_tokens": max_tokens, "recorded": {k: rec.get(k) for k in (
                               "model", "resolved_model", "model_digest", "temperature", "reasoning", "max_tokens_sent",
                               "structured_output", "prompt_tokens", "output_tokens", "reasoning_tokens", "stop_reason",
                               "truncated", "parse_ok")}, "raw": rec.get("raw")})


class ReplayLocal(_Recorder, local.LLM):
    def __init__(self, ledger: Path):
        self.calls, self.ledger_rel = [], str(ledger.relative_to(REPO))
        local.LLM.__init__(self, ledger)
        self.digest = next(iter(self._cache.values())).get("model_digest")

    def _digest(self) -> None:  # no network: provenance comes from the ledger
        return None

    def call(self, *, system, user, schema, seed, max_tokens, tag):
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        options = {"temperature": self.temperature, "seed": seed, "num_ctx": local.NUM_CTX, "num_predict": max_tokens}
        key = hashlib.sha256(json.dumps([self.model, messages, schema, options], sort_keys=True).encode()).hexdigest()
        self._record(key, system, user, schema, seed, max_tokens, tag)
        return local.LLM.call(self, system=system, user=user, schema=schema, seed=seed, max_tokens=max_tokens, tag=tag)


class ReplayFrontier(_Recorder, providers.FrontierLLM):
    def __init__(self, ledger: Path, provider: str, model: str):  # no client and no key: cache hits only
        self.calls, self.ledger_rel = [], str(ledger.relative_to(REPO))
        self.provider, self.model, self.budget, self.ledger, self.temperature, self.digest = provider, model, None, ledger, "NOT_CONFIGURABLE", None
        self._cache = {}
        for line in ledger.read_text().splitlines():
            rec = json.loads(line)
            if rec.get("error") is None:
                self._cache[rec["request_hash"]] = rec

    def call(self, *, system, user, schema, seed, max_tokens, tag):
        cap = max_tokens + providers.REASONING_ALLOWANCE
        key = hashlib.sha256(json.dumps([self.provider, self.model, providers.REASONING_EFFORT, system, user, schema, seed, cap],
                                        sort_keys=True).encode()).hexdigest()
        self._record(key, system, user, schema, seed, max_tokens, tag)
        return providers.FrontierLLM.call(self, system=system, user=user, schema=schema, seed=seed, max_tokens=max_tokens, tag=tag)


def fence(text: str, lang: str = "") -> str:
    tick = "````" if "```" in text else "```"
    return f"{tick}{lang}\n{text}\n{tick}"


def write(dest: Path, title: str, intro: str, calls: list[dict], ledger_rel: str) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    out = [f"# {title}", "", intro, "", f"Ledger: `{ledger_rel}`. Every request hash below is present in it; the output shown is "
           "the recorded `raw` field of that ledger row.", ""]
    for i, c in enumerate(calls, 1):
        stage = c["tag"].get("stage") or c["tag"].get("call") or c["tag"].get("condition") or "call"
        out += [f"## Call {i}: `{stage}`", "", f"- request_hash: `{c['request_hash']}`", f"- seed / replicate: {c['seed']}",
                f"- visible token cap: {c['max_tokens']}"]
        out += [f"- recorded `{k}`: `{v}`" for k, v in c["recorded"].items() if v is not None]
        out += ["", "### System", "", fence(c["system"]), "", "### User", "", fence(c["user"]), "", "### Output schema", "",
                fence(json.dumps(c["schema"], indent=1), "json"), "", "### Recorded output", "", fence(c["raw"] or ""), ""]
    dest.write_text("\n".join(out))
    return {"file": str(dest.relative_to(REPO)), "ledger": ledger_rel, "request_hashes": [c["request_hash"] for c in calls]}


def same_text(a: list[dict], b: list[dict]) -> bool:
    """Same frozen inputs on both models: the first call of a run is byte-identical (system, user, schema), and every
    later call has the same system prompt, stage and visible-token cap. Later user prompts (and, for ToT selection, the
    enum of surviving branches) embed the model's own earlier outputs, so they differ by design."""
    key = lambda c: (c["system"], c["tag"].get("stage") or c["tag"].get("call"), c["max_tokens"])  # noqa: E731
    return (len(a) == len(b) and (a[0]["system"], a[0]["user"], a[0]["schema"]) == (b[0]["system"], b[0]["user"], b[0]["schema"])
            and [key(c) for c in a] == [key(c) for c in b])


def study_a(index: dict) -> None:
    from rs2610.replication.a2.run import instances
    from rs2610.study_a.topologies import MODES, Runner

    inst = instances()[0]
    unseen = {i["instance_id"] for i in json.loads((ART / "study_a" / "instances" / "UNSEEN.json").read_text())}
    assert inst["instance_id"] in unseen
    base = RES / "reasoning-topology"
    for mode in MODES:
        q = ReplayLocal(ART / "study_a" / "ledger.jsonl")
        Runner(q).run(inst, mode, 1)
        f = base / "original-study" / "prompts" / "examples" / f"{inst['instance_id'].replace('::', '__')}__{mode}.md"
        index.setdefault("A", []).append(write(f, f"Study A, {mode}: {inst['instance_id']}, seed 1",
                                               f"Every call the {mode} topology made for this instance, replayed through "
                                               "`harness/rs2610/study_a/topologies.py` against the Study A ledger.", q.calls, q.ledger_rel))
        lu = ReplayFrontier(ART / "replication" / "a2" / "ledger_openai.jsonl", "openai", "gpt-6-luna")
        Runner(lu).run(inst, mode, 1)
        assert same_text(q.calls, lu.calls), f"A2 {mode}: hosted prompt text differs from the baseline"
        f = base / "frontier-replication" / "prompts" / "examples" / f"{inst['instance_id'].replace('::', '__')}__{mode}__gpt-6-luna.md"
        index.setdefault("A2", []).append(write(f, f"Study A2, {mode} on gpt-6-luna: {inst['instance_id']}, replicate 1",
                                                "The same frozen inputs as the Study A example: the first call is byte-identical "
                                                "(system, user, schema) and every later call has the same system prompt, stage "
                                                "and token cap; later calls embed this model's own earlier outputs. See "
                                                "`providers/` for the provider request shape.", lu.calls, lu.ledger_rel))


def study_b(index: dict) -> None:
    from rs2610.common.data import by_id
    from rs2610.common.prep import holdout_split
    from rs2610.replication.b2.invention import invent
    from rs2610.replication.b2.variants import CELLS, MAKERS, b2_base
    from rs2610.study_b.conditions import CONDITIONS, run_condition
    from rs2610.study_b.profile import candidate_features, profile
    from rs2610.study_b.variants import trapped

    did = "taiwan_default"
    ds = by_id(did)
    v = trapped(ds)
    dev, _, _ = holdout_split(ds, v.frame)
    prof, cands = profile(v, dev), candidate_features(v, dev)
    base = RES / "semantic-context"
    for cond in CONDITIONS:
        q = ReplayLocal(ART / "study_b" / "ledger.jsonl")
        run_condition(q, v, cond, 1, prof, dev, cands, {"study": "B", "dataset": did, "variant": "trapped", "condition": cond, "seed": 1})
        f = base / "original-study" / "prompts" / "examples" / f"{did}__trapped__{cond}.md"
        index.setdefault("B", []).append(write(f, f"Study B, {cond}: {did} (trapped), seed 1",
                                               "Every call this condition made, replayed through `harness/rs2610/study_b/conditions.py`.",
                                               q.calls, q.ledger_rel))
    b2 = b2_base(ds)
    dev2, _, _ = holdout_split(ds, b2.frame)
    for kind, cond in CELLS:
        v2 = MAKERS[kind](b2)
        prof2, cands2 = profile(v2, dev2), candidate_features(v2, dev2)
        tag = {"study": "B2", "dataset": did, "variant": kind, "condition": cond, "seed": 1}
        q = ReplayLocal(ART / "replication" / "b2" / "ledger_local.jsonl")
        run_condition(q, v2, cond, 1, prof2, dev2, cands2, tag)
        invent(q, v2, cond, 1, prof2, dev2, tag)
        f = base / "frontier-replication" / "prompts" / "examples" / f"{did}__{kind}__{cond}.md"
        index.setdefault("B2", []).append(write(f, f"Study B2, {kind} {cond}: {did}, replicate 1 (qwen2.5:7b baseline)",
                                                "The analysis calls of the condition, then the feature-invention call "
                                                "(`harness/rs2610/replication/b2/invention.py`).", q.calls, q.ledger_rel))
        for prov, model in (("openai", "gpt-6-luna"), ("anthropic", "claude-sonnet-5-5")):
            h = ReplayFrontier(ART / "replication" / "b2" / f"ledger_{prov}.jsonl", prov, model)
            run_condition(h, v2, cond, 1, prof2, dev2, cands2, tag)
            invent(h, v2, cond, 1, prof2, dev2, tag)
            assert same_text(q.calls, h.calls), f"B2 {kind}:{cond} {model}: hosted prompt text differs from the baseline"
            index.setdefault("B2_hosted_identical", []).append({"cell": f"{kind}:{cond}", "model": model, "ledger": h.ledger_rel,
                                                                "request_hashes": [c["request_hash"] for c in h.calls]})


def contracts() -> None:
    from rs2610.replication.b2 import invention
    from rs2610.study_b import conditions as c

    def dump(path: Path, obj: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")

    sc = RES / "semantic-context"
    for name in ("ANALYSIS_SCHEMA", "FE_SCHEMA", "INFER_SCHEMA", "VERIFY_SCHEMA"):
        dump(sc / "original-study" / "contracts" / f"{name.lower()}.json", getattr(c, name))
    dump(sc / "original-study" / "contracts" / "enums.json", c.ENUMS)
    dump(sc / "frontier-replication" / "feature-invention" / "invent_schema.json", invention.INVENT_SCHEMA)
    (sc / "frontier-replication" / "feature-invention" / "invent_task.txt").write_text(invention.INVENT_TASK + "\n")
    for prov in ("openai", "anthropic"):
        dump(RES / "reasoning-topology" / "frontier-replication" / "providers" / f"strict_schema_example_{prov}.json",
             {"source": "harness/rs2610/replication/providers.py:strict_schema applied to the B2 invention schema",
              "schema_sent": providers.strict_schema(invention.INVENT_SCHEMA, prov)})


def main() -> None:
    index: dict[str, list] = {}
    contracts()
    study_a(index)
    study_b(index)
    (RES / "PROMPT_EXAMPLES_INDEX.json").write_text(json.dumps(index, indent=1) + "\n")
    print({k: len(v) for k, v in index.items()}, "examples written; every request hash found in its ledger")


if __name__ == "__main__":
    main()
