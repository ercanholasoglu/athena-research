"""Canonical experiment configuration for A2 and B2: ``experiment-config.json`` + ``EXPERIMENT_CONFIG.md`` per study.

    python -m rs2610.replication.make_configs

Built from the governing freeze record (original + amendments) and the run ledgers, so every published parameter is
the one that ran. Resolved model ids, request counts, token totals and costs come from the ledgers.
"""
from __future__ import annotations

import json
from pathlib import Path

from rs2610.replication.freeze import AMENDMENTS, RECORD

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "replication"
OUT = ROOT / "outputs" / "replication"

CODE = {
    "A2": {"DIRECT / CoT / ToT / GoT execution": "study_a/topologies.py (frozen Study A, unchanged)",
           "instances, evidence, answer keys": "study_a/tasks.py, study_a/evidence.py (frozen)",
           "scoring": "study_a/scoring.py (frozen)", "frontier substrate": "replication/providers.py",
           "runner": "replication/a2/run.py", "statistics": "replication/a2/analyze.py"},
    "B2": {"semantic conditions and dictionary injection": "study_b/conditions.py (frozen: run_condition, documentation)",
           "variants and traps": "study_b/variants.py (frozen) + replication/b2/variants.py (target-derived trap, B2 grid)",
           "feature-invention call": "replication/b2/invention.py", "feature validation": "replication/b2/evaluate.py",
           "semantic scoring": "study_b/score.py (frozen)", "frontier substrate": "replication/providers.py",
           "runner": "replication/b2/run.py", "statistics": "replication/b2/analyze.py"},
}


def ledger_summary(path: Path) -> dict:
    if not path.exists():
        return {}
    recs = [json.loads(line) for line in path.read_text().splitlines()]
    ok = [r for r in recs if not r.get("error")]
    out = {"requests": len(recs), "successful": len(ok), "errors": len(recs) - len(ok),
           "resolved_model_ids": sorted({r.get("resolved_model") or r.get("model") for r in ok}),
           "input_tokens": sum(r.get("prompt_tokens") or 0 for r in ok), "output_tokens": sum(r.get("output_tokens") or 0 for r in ok),
           "truncated_calls": sum(bool(r.get("truncated")) for r in ok)}
    if ok and "provider" in ok[0]:
        out.update({"reasoning_tokens": sum(r.get("reasoning_tokens") or 0 for r in ok) if any(r.get("reasoning_tokens") is not None for r in ok) else "NOT_REPORTED_SEPARATELY",
                    "cost_usd": round(sum(r.get("cost_usd") or 0 for r in ok), 4), "cost_status": "CALCULATED_FROM_PUBLISHED_PRICES",
                    "sdk": ok[0].get("sdk"), "first_request_id": ok[0].get("request_id")})
    else:
        out.update({"model_digest": ok[0].get("model_digest") if ok else None, "cost_usd": None, "cost_status": "NOT_APPLICABLE_LOCAL"})
    return out


def build(study: str) -> dict:
    gov = AMENDMENTS[-1] if AMENDMENTS else RECORD
    fr = json.loads(gov.read_text())
    c = fr["config"]
    s = c[study.lower()]
    from rs2610.replication.providers import PRICES, REASONING_ALLOWANCE, REASONING_EFFORT
    arms = {"baseline": {"provider": "local (Ollama)", "requested_model": "qwen2.5:7b", "model_digest": "845dbda0ea48…",
                         "temperature": 0.4, "top_p": "Ollama default", "seed": "= replicate index",
                         "reasoning": "none", "max_output_tokens": "frozen per-call caps (260–3200)",
                         "structured_output": "JSON schema via Ollama `format`",
                         "runs": "frozen Study A UNSEEN runs, seeds 1–3, reused (not re-run)" if study == "A2" else "new runs, replicates 1–2"},
            "openai": {"provider": "OpenAI Responses API", "requested_model": c["models"]["openai"]["model"],
                       "reasoning": {"effort": REASONING_EFFORT}, "temperature": "NOT_CONFIGURABLE", "top_p": "NOT_CONFIGURABLE",
                       "seed": "NOT_CONFIGURABLE (replicate index enters the request hash only)",
                       "max_output_tokens": f"frozen visible cap + {REASONING_ALLOWANCE}", "structured_output": "json_schema strict",
                       "store": False, "price_per_mtok": PRICES.get(c["models"]["openai"]["model"])}}
    if study == "B2":
        arms["anthropic"] = {"provider": "Anthropic Messages API", "requested_model": c["models"]["anthropic"]["model"],
                             "reasoning": {"effort": REASONING_EFFORT, "thinking": "adaptive, provider default (always on)"},
                             "temperature": "NOT_CONFIGURABLE", "top_p": "NOT_CONFIGURABLE", "seed": "NOT_CONFIGURABLE",
                             "max_output_tokens": f"frozen visible cap + {REASONING_ALLOWANCE}",
                             "structured_output": "output_config.format json_schema (array minItems/maxItems removed)",
                             "replicates": c["models"]["anthropic"].get("b2_replicates"),
                             "price_per_mtok": PRICES.get(c["models"]["anthropic"]["model"])}
    else:
        arms["anthropic"] = {"status": "NOT RUN (INCOMPLETE): account had no credit for an A2 run; see PREREGISTRATION amendment 2"}
    ledgers = {"openai": ART / study.lower() / "ledger_openai.jsonl", "anthropic": ART / study.lower() / "ledger_anthropic.jsonl",
               "baseline": ART / study.lower() / "ledger_local.jsonl"}
    for k, p in ledgers.items():
        if k in arms and p.exists():
            arms[k]["observed"] = ledger_summary(p)
    return {"study": study, "program": "rs2610", "freeze": {"original": RECORD.name, "governing": gov.name, "git_head": fr["git"]["head"],
                                                             "frozen_at": fr["frozen_at"]},
            "arms": arms, "datasets": [d for d in fr["datasets"] if d[f"in_{study.lower()}"]],
            "design": s, "code": CODE[study], "prompts": "per-instance / per-cell SHA-256 in the governing freeze record",
            "statistics": "PREREGISTRATION.md section " + ("6" if study == "A2" else "7")}


def render(cfg: dict) -> str:
    L = [f"# {cfg['study']} experiment configuration", "",
         f"Generated by `replication/make_configs.py` from `{cfg['freeze']['governing']}` (git `{cfg['freeze']['git_head'][:10]}`, "
         f"{cfg['freeze']['frozen_at']}) and the run ledgers. Machine-readable twin: `experiment-config.json`.", "", "## Models", "",
         "| Arm | Provider | Requested model | Resolved id | Reasoning | Temperature | Seed | Token budget | Structured output |",
         "|---|---|---|---|---|---|---|---|---|"]
    for k, a in cfg["arms"].items():
        if "status" in a:
            L.append(f"| {k} | — | — | — | — | — | — | — | {a['status']} |")
            continue
        obs = a.get("observed", {})
        L.append(f"| {k} | {a['provider']} | `{a['requested_model']}` | {', '.join(f'`{m}`' for m in obs.get('resolved_model_ids', [])) or '—'} | "
                 f"{json.dumps(a['reasoning']) if isinstance(a['reasoning'], dict) else a['reasoning']} | {a['temperature']} | {a['seed']} | "
                 f"{a['max_output_tokens']} | {a['structured_output']} |")
    L += ["", "## Observed usage", "", "| Arm | Requests | Errors | Input tokens | Output tokens | Reasoning tokens | Truncated | Cost (USD) |",
          "|---|---|---|---|---|---|---|---|"]
    for k, a in cfg["arms"].items():
        o = a.get("observed")
        if o:
            L.append(f"| {k} | {o['requests']} | {o['errors']} | {o['input_tokens']} | {o['output_tokens']} | {o.get('reasoning_tokens', '—')} | "
                     f"{o['truncated_calls']} | {o['cost_usd'] if o['cost_usd'] is not None else o['cost_status']} |")
    L += ["", "## Datasets and frozen splits", "", "| Dataset | Rows | Columns | Holdout | Frame SHA-256 | Test-index SHA-256 |", "|---|---|---|---|---|---|"]
    for d in cfg["datasets"]:
        L.append(f"| {d['dataset_id']} | {d['rows']} | {d['columns']} | {d['holdout_scheme']} | `{d['frame_sha256'][:16]}…` | `{d['test_idx_sha256'][:16]}…` |")
    L += ["", "## Design", "", "```json", json.dumps(cfg["design"], indent=1), "```", "", "## Code", ""]
    L += [f"- {k}: `{v}`" for k, v in cfg["code"].items()]
    L += ["", f"Prompts: {cfg['prompts']}. Statistics: {cfg['statistics']}.", ""]
    return "\n".join(L)


def main() -> None:
    for st in ("A2", "B2"):
        d = OUT / st.lower()
        d.mkdir(parents=True, exist_ok=True)
        cfg = build(st)
        (d / "experiment-config.json").write_text(json.dumps(cfg, indent=1, default=str))
        (d / "EXPERIMENT_CONFIG.md").write_text(render(cfg))
        print("written", d / "EXPERIMENT_CONFIG.md")


if __name__ == "__main__":
    main()
