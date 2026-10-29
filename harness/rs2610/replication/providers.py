"""Frontier-model substrate for the A2/B2 replication: the same ``call()`` contract as the frozen ``common.llm.LLM``.

The frozen Study A/B code (topologies, conditions) calls ``llm.call(system=, user=, schema=, seed=, max_tokens=, tag=)``
and reads an ``LLMResult``.  This module provides that interface for two hosted providers, so the frozen execution
semantics run unchanged; only the substrate differs.

What is recorded per call (ledger JSONL, one line per request): provider, requested model, provider-returned model id,
API version, reasoning setting, temperature / top_p / seed (or ``NOT_CONFIGURABLE``), the frozen visible-output cap and the
cap actually sent, structured-output mode, input / output / reasoning / cached tokens, wall latency, request id, stop
reason, computed cost and its status.  Unknown values are ``None`` with an ``*_status`` of ``UNKNOWN``; nothing unknown
is written as 0.

Provider differences that cannot be removed (documented in EXPERIMENT_CONFIG.md):

* Temperature, top_p and seed are not accepted by either frontier model; replicate k is an independent sample whose
  index enters the request hash only.
* Both models always reason before answering. ``max_tokens`` on these APIs bounds reasoning + visible output, so the
  frozen visible caps (260-3200 tokens) are sent as ``frozen_cap + REASONING_ALLOWANCE``.  The frozen cap is recorded.
* Structured output: the frozen JSON schemas are sent through each provider's native JSON-schema mode after one
  deterministic transform, ``strict_schema()`` (``additionalProperties: false`` on every object; nothing else changes).
* Cost is not returned by either API; it is computed from the usage block and the published per-token prices in
  ``PRICES`` (source and access date recorded), status ``CALCULATED_FROM_PUBLISHED_PRICES``.
"""
from __future__ import annotations

import copy
import hashlib
import json
import threading
import time
from pathlib import Path
from typing import Any

from rs2610.common.llm import LLMResult, append_line

REASONING_EFFORT = "medium"
REASONING_ALLOWANCE = 16000
OPENAI_KEY_FILE = Path.home() / ".config" / "rs2610" / "openai.key"

# USD per 1M tokens, standard (non-batch) short-context rates.
PRICES = {
    "gpt-6.1-sol": {"input": 2.00, "cached_input": 0.10, "output": 10.00,
                    "source": "https://developers.openai.com/api/docs/pricing", "accessed": "2026-10-29"},
    "gpt-6-luna": {"input": 0.10, "cached_input": 0.01, "output": 0.50,
                   "source": "https://developers.openai.com/api/docs/pricing", "accessed": "2026-10-29"},
    "claude-sonnet-5-5": {"input": 2.00, "cached_input": 0.20, "output": 10.00,
                          "source": "Anthropic model table (claude-api reference, models.md), Claude Sonnet 5.5 $2 / $10 per MTok",
                          "accessed": "2026-10-29"},
    "claude-opus-5-5": {"input": 4.00, "cached_input": 0.20, "output": 20.00,
                        "source": "Anthropic model table (claude-api reference, models.md), Claude Opus 5.5 $4 / $20 per MTok",
                        "accessed": "2026-10-29"},
}


class BudgetExceeded(RuntimeError):
    pass


class Budget:
    """Hard spending cap shared by every frontier ledger of one study arm.  A call is refused *before* it is sent when
    spent + its worst-case cost (full input at the uncached rate + the whole token cap at the output rate) would pass the
    cap.  Spent is re-read from the ledgers at start, so a resumed run cannot overspend."""

    def __init__(self, cap_usd: float, ledgers: list[Path]):
        self.cap = cap_usd
        self.spent = 0.0
        self.lock = threading.Lock()
        for p in ledgers:
            if p.exists():
                for line in p.read_text().splitlines():
                    try:
                        self.spent += json.loads(line).get("cost_usd") or 0.0
                    except json.JSONDecodeError:
                        continue

    def reserve(self, worst: float) -> None:
        with self.lock:
            if self.spent + worst > self.cap:
                raise BudgetExceeded(f"cap {self.cap:.2f} USD; spent {self.spent:.2f}; next call could cost {worst:.2f}")

    def add(self, cost: float | None) -> None:
        with self.lock:
            self.spent += cost or 0.0


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


def _cost(model: str, inp: int | None, cached: int | None, out: int | None) -> tuple[float | None, str]:
    p = PRICES.get(model)
    if p is None or inp is None or out is None:
        return None, "UNKNOWN"
    c = cached or 0
    return round(((inp - c) * p["input"] + c * p["cached_input"] + out * p["output"]) / 1e6, 6), "CALCULATED_FROM_PUBLISHED_PRICES"


class FrontierLLM:
    """``provider`` is 'openai' or 'anthropic'; ``model`` is the requested id (the resolved id is recorded per call)."""

    def __init__(self, ledger: Path, provider: str, model: str, budget: Budget):
        self.provider, self.model, self.budget, self.ledger = provider, model, budget, ledger
        self.temperature = "NOT_CONFIGURABLE"
        self.digest = None  # hosted models expose no weights digest; the resolved model id is recorded per call
        ledger.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._cache: dict[str, dict[str, Any]] = {}
        if ledger.exists():
            for line in ledger.read_text().splitlines():
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("error") is None:
                    self._cache[rec["request_hash"]] = rec
        if provider == "openai":
            import openai
            self.client = openai.OpenAI(api_key=OPENAI_KEY_FILE.read_text().strip(), max_retries=6, timeout=900)
            self.sdk = f"openai-python {openai.__version__}"
        elif provider == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic(max_retries=6, timeout=900)
            self.sdk = f"anthropic-python {anthropic.__version__}"
        else:
            raise ValueError(provider)

    def _send(self, system: str, user: str, schema: dict[str, Any], cap: int) -> dict[str, Any]:
        s = strict_schema(schema, self.provider)
        if self.provider == "openai":
            r = self.client.responses.create(
                model=self.model, instructions=system, input=user, max_output_tokens=cap, store=False,
                reasoning={"effort": REASONING_EFFORT},
                text={"format": {"type": "json_schema", "name": "output", "schema": s, "strict": True}})
            u = r.usage
            det = getattr(u, "output_tokens_details", None)
            cin = getattr(getattr(u, "input_tokens_details", None), "cached_tokens", None)
            stop = r.status if r.status != "incomplete" else f"incomplete:{getattr(r.incomplete_details, 'reason', None)}"
            return {"raw": r.output_text or "", "resolved_model": r.model, "response_id": r.id,
                    "request_id": getattr(r, "_request_id", None), "input_tokens": u.input_tokens if u else None,
                    "cached_input_tokens": cin, "output_tokens": u.output_tokens if u else None,
                    "reasoning_tokens": getattr(det, "reasoning_tokens", None), "stop_reason": stop,
                    "truncated": r.status == "incomplete"}
        with self.client.messages.stream(
                model=self.model, max_tokens=cap, system=system, messages=[{"role": "user", "content": user}],
                output_config={"effort": REASONING_EFFORT, "format": {"type": "json_schema", "schema": s}}) as st:
            m = st.get_final_message()
        text = "".join(b.text for b in m.content if b.type == "text")
        u = m.usage
        return {"raw": text, "resolved_model": m.model, "response_id": m.id, "request_id": getattr(m, "_request_id", None),
                "input_tokens": (u.input_tokens or 0) + (u.cache_read_input_tokens or 0) + (u.cache_creation_input_tokens or 0),
                "cached_input_tokens": u.cache_read_input_tokens, "output_tokens": u.output_tokens,
                "reasoning_tokens": None,  # not reported separately by this API; included in output_tokens
                "stop_reason": m.stop_reason, "truncated": m.stop_reason == "max_tokens"}

    def call(self, *, system: str, user: str, schema: dict[str, Any], seed: int, max_tokens: int,
             tag: dict[str, Any]) -> LLMResult:
        cap = max_tokens + REASONING_ALLOWANCE
        key = hashlib.sha256(json.dumps([self.provider, self.model, REASONING_EFFORT, system, user, schema, seed, cap],
                                        sort_keys=True).encode()).hexdigest()
        if key in self._cache:
            rec = self._cache[key]
            return LLMResult(rec["content"], rec["raw"], rec["prompt_tokens"], rec["output_tokens"], rec["latency_s"],
                             rec["parse_ok"], None, True, key)
        p = PRICES[self.model]
        self.budget.reserve(((len(system) + len(user)) / 2.5 * p["input"] + cap * p["output"]) / 1e6)
        t0 = time.time()
        err, res = None, {}
        try:
            res = self._send(system, user, schema, cap)
        except Exception as e:  # noqa: BLE001 — the SDKs already retried transient errors; record and move on
            err = f"{type(e).__name__}: {str(e)[:300]}"
        latency = time.time() - t0
        raw = res.get("raw", "")
        content, parse_ok = None, False
        if err is None:
            try:
                content = json.loads(raw)
                parse_ok = isinstance(content, dict)
            except json.JSONDecodeError:
                content = None
        cost, cost_status = _cost(self.model, res.get("input_tokens"), res.get("cached_input_tokens"), res.get("output_tokens"))
        self.budget.add(cost)
        rec = {"request_hash": key, "ts": time.time(), "provider": self.provider, "model": self.model,
               "resolved_model": res.get("resolved_model"), "sdk": self.sdk,
               "reasoning": {"effort": REASONING_EFFORT, "thinking": "always on (provider)", "allowance": REASONING_ALLOWANCE},
               "temperature": "NOT_CONFIGURABLE", "top_p": "NOT_CONFIGURABLE", "seed": "NOT_CONFIGURABLE", "replicate": seed,
               "frozen_visible_cap": max_tokens, "max_tokens_sent": cap, "structured_output": "json_schema strict (strict_schema)",
               "tag": tag, "response_id": res.get("response_id"), "request_id": res.get("request_id"),
               "prompt_tokens": res.get("input_tokens"), "prompt_tokens_status": "ACTUAL" if res.get("input_tokens") is not None else "UNKNOWN",
               "cached_input_tokens": res.get("cached_input_tokens"),
               "output_tokens": res.get("output_tokens"), "output_tokens_status": "ACTUAL" if res.get("output_tokens") is not None else "UNKNOWN",
               "reasoning_tokens": res.get("reasoning_tokens"),
               "reasoning_tokens_status": "ACTUAL" if res.get("reasoning_tokens") is not None else "NOT_REPORTED_SEPARATELY",
               "latency_s": round(latency, 3), "latency_status": "WALL_CLOCK_CLIENT_SIDE",
               "cost_usd": cost, "cost_status": cost_status, "price_table": PRICES.get(self.model),
               "stop_reason": res.get("stop_reason"), "truncated": bool(res.get("truncated")),
               "parse_ok": parse_ok, "error": err, "content": content, "raw": raw}
        with self._lock:
            append_line(self.ledger, json.dumps(rec))
            if err is None:
                self._cache[key] = rec
        return LLMResult(content, raw, res.get("input_tokens"), res.get("output_tokens"), latency, parse_ok, err, False, key)
