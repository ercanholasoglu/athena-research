"""One controlled LLM substrate for both studies.

* Backend: a local Ollama model (default ``qwen2.5:7b``), temperature and seed
  fixed per call — the run is reproducible given (model digest, prompt, seed).
* Every call is appended to a JSONL ledger with ACTUAL prompt/output token
  counts and ACTUAL wall-clock latency as reported by the server.
* Cost: local inference has no provider bill.  ``cost_usd`` is therefore None
  with ``cost_status = "NOT_APPLICABLE_LOCAL"`` (energy cost UNKNOWN) — it is
  never written as 0.  A price-equivalent figure is produced only in analysis,
  labelled ESTIMATED.
* Responses are cached by request hash, so an interrupted run resumes without
  re-sampling (a resumed call is flagged ``cached=True`` and its original
  latency is kept).
* Only the structured JSON the model emits is stored.  The substrate exposes no
  hidden reasoning channel; nothing beyond the visible output exists to store.
"""
from __future__ import annotations

import hashlib
import json
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

OLLAMA = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:7b"
TEMPERATURE = 0.4
NUM_CTX = 12288

_lock = threading.Lock()


def append_line(path: Path, line: str, wait_s: float = 1800.0) -> None:
    """Append one line, retrying through transient PermissionError (the host briefly revokes file access to background
    jobs while the session is suspended; seen three times during development). Results are unaffected: a line is
    either written whole or the job stops after `wait_s` and resumes from what is on disk."""
    deadline, delay = time.time() + wait_s, 2.0
    while True:
        try:
            with path.open("a") as fh:
                fh.write(line + "\n")
            return
        except PermissionError:
            if time.time() > deadline:
                raise
            time.sleep(delay)
            delay = min(60.0, delay * 2)


@dataclass
class LLMResult:
    content: dict[str, Any] | None
    raw: str
    prompt_tokens: int | None
    output_tokens: int | None
    latency_s: float
    parse_ok: bool
    error: str | None
    cached: bool
    request_hash: str
    prefill_s: float | None = None
    decode_s: float | None = None
    load_s: float | None = None


class LLM:
    def __init__(self, ledger: Path, model: str = DEFAULT_MODEL, temperature: float = TEMPERATURE):
        self.model = model
        self.temperature = temperature
        self.ledger = ledger
        ledger.parent.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, dict[str, Any]] = {}
        if ledger.exists():
            for line in ledger.read_text().splitlines():
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("error") is None:
                    self._cache[rec["request_hash"]] = rec
        self.digest = self._digest()

    def _digest(self) -> str | None:
        try:
            with urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=10) as r:
                tags = json.load(r)
            return next((m["digest"] for m in tags["models"] if m["name"] == self.model), None)
        except Exception:  # noqa: BLE001 — digest is provenance, not a precondition
            return None

    def call(self, *, system: str, user: str, schema: dict[str, Any], seed: int, max_tokens: int,
             tag: dict[str, Any]) -> LLMResult:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        options = {"temperature": self.temperature, "seed": seed, "num_ctx": NUM_CTX, "num_predict": max_tokens}
        key = hashlib.sha256(json.dumps([self.model, messages, schema, options], sort_keys=True).encode()).hexdigest()
        if key in self._cache:
            rec = self._cache[key]
            return LLMResult(rec["content"], rec["raw"], rec["prompt_tokens"], rec["output_tokens"], rec["latency_s"],
                             rec["parse_ok"], None, True, key, rec.get("prefill_s"), rec.get("decode_s"), rec.get("load_s"))
        body = {"model": self.model, "messages": messages, "stream": False, "format": schema, "options": options,
                "keep_alive": "30m"}
        t0 = time.time()
        err: str | None = None
        raw, pt, ot, pdur, edur, ldur = "", None, None, None, None, None
        for attempt in range(3):
            try:
                req = urllib.request.Request(f"{OLLAMA}/api/chat", data=json.dumps(body).encode(),
                                             headers={"content-type": "application/json"})
                with urllib.request.urlopen(req, timeout=900) as r:
                    resp = json.load(r)
                raw = resp["message"]["content"]
                pt, ot = resp.get("prompt_eval_count"), resp.get("eval_count")
                pdur = resp.get("prompt_eval_duration", 0) / 1e9 if resp.get("prompt_eval_duration") is not None else None
                edur = resp.get("eval_duration", 0) / 1e9 if resp.get("eval_duration") is not None else None
                ldur = resp.get("load_duration", 0) / 1e9 if resp.get("load_duration") is not None else None
                err = None
                break
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:  # transient → retry
                err = f"{type(e).__name__}: {e}"
                time.sleep(5 * (attempt + 1))
        latency = time.time() - t0
        content: dict[str, Any] | None = None
        parse_ok = False
        if err is None:
            try:
                content = json.loads(raw)
                parse_ok = isinstance(content, dict)
            except json.JSONDecodeError as e:
                err = None  # a parse failure is a *model* outcome, recorded, not retried
                parse_ok = False
                content = None
                raw = raw if raw else f"<empty> {e}"
        rec = {"request_hash": key, "ts": time.time(), "model": self.model, "model_digest": self.digest,
               "temperature": self.temperature, "seed": seed, "max_tokens": max_tokens, "tag": tag,
               "prompt_tokens": pt, "prompt_tokens_status": "ACTUAL" if pt is not None else "UNKNOWN",
               "output_tokens": ot, "output_tokens_status": "ACTUAL" if ot is not None else "UNKNOWN",
               "latency_s": round(latency, 3), "latency_status": "ACTUAL",
               "prefill_s": pdur, "decode_s": edur, "load_s": ldur,
               "cost_usd": None, "cost_status": "NOT_APPLICABLE_LOCAL",
               "truncated": bool(ot is not None and ot >= max_tokens),
               "parse_ok": parse_ok, "error": err, "content": content, "raw": raw}
        with _lock:
            append_line(self.ledger, json.dumps(rec))
        if err is None:
            self._cache[key] = rec
        return LLMResult(content, raw, pt, ot, latency, parse_ok, err, False, key, pdur, edur, ldur)


def ledger_compute(ledger: Path) -> dict[str, tuple[float | None, float | None]]:
    """request_hash -> (server compute seconds, load seconds), for backfilling traces written before compute_s existed."""
    out: dict[str, tuple[float | None, float | None]] = {}
    if ledger.exists():
        for line in ledger.read_text().splitlines():
            r = json.loads(line)
            if r.get("decode_s") is not None:
                out[r["request_hash"]] = ((r.get("prefill_s") or 0) + r["decode_s"], r.get("load_s"))
    return out


def backfill(calls: list[dict[str, Any]], table: dict[str, tuple[float | None, float | None]]) -> None:
    for c in calls:
        if c.get("compute_s") is None and c.get("request_hash") in table:
            c["compute_s"], c["load_s"] = table[c["request_hash"]]
