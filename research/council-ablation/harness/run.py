"""Council ablation harness — implements PREREGISTRATION.md exactly.

  python run.py collect OUT   # one answer per (member, case); resumable cache
  python run.py judge OUT     # condition E judge over the C answers
  python run.py analyze OUT   # conditions A–F, metrics, CIs, characteristics, decision
"""
from __future__ import annotations

import itertools
import json
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cases import cases  # noqa: E402

OLLAMA = "http://localhost:11434"
HAIKU, SONNET = "anthropic/claude-haiku-5-5", "anthropic/claude-sonnet-5-5"
Q7, Q1 = "ollama/qwen2.5:7b", "ollama/qwen2.5:1.5b"
PROVIDER = {HAIKU: "anthropic", SONNET: "anthropic", Q7: "qwen-local", Q1: "qwen-local"}

SYSTEM = (
    "You are an ML-governance reviewer inside Athena, an enterprise AutoML platform. Answer the question by choosing "
    "exactly one option id. Use only the facts given; if the facts do not decide it and an option says it cannot be "
    'decided, choose that option.\nReturn only JSON: {"answer": "<option id>", "confidence": <0..1>, "reason": "<one sentence>"}'
)
ROLES = {
    "neutral": "",
    "verifier": "Perspective: conservative verifier. Look first for what would make the permissive answer wrong "
                "(timing after the prediction point, outcome-derived values, protected proxies, unsupported claims).",
    "domain": "Perspective: domain expert. Reason first from what the business process and the data actually mean.",
    "critic": "Perspective: semantic critic. Check whether names and descriptions really support the conclusion; "
              "distrust suggestive names and read the description and numbers literally.",
}
# Amendment 1: Claude 5.5 models accept only temperature=1 (provider-enforced).
CLAUDE_T = 1.0
# Amendment 2: 300 output tokens truncated 186 Claude answers before their JSON; budget raised,
# and only calls that hit the old budget without a parsed answer are re-asked.
MAX_TOKENS = 1024
OLD_BUDGET = 300
MEMBERS = {
    "sonnet": (SONNET, CLAUDE_T, "neutral"), "haiku": (HAIKU, CLAUDE_T, "neutral"), "haiku_repeat": (HAIKU, CLAUDE_T, "neutral"),
    **{f"haiku_s{i}": (HAIKU, CLAUDE_T, "neutral") for i in (1, 2, 3)},
    "haiku_verifier": (HAIKU, CLAUDE_T, "verifier"), "haiku_domain": (HAIKU, CLAUDE_T, "domain"), "haiku_critic": (HAIKU, CLAUDE_T, "critic"),
    "qwen7b": (Q7, 0.0, "neutral"), "qwen1_5b": (Q1, 0.0, "neutral"),
}
SOLO_CANDIDATES = ("sonnet", "haiku", "qwen7b", "qwen1_5b")
B1 = ("haiku_verifier", "haiku_domain", "haiku_critic")
B2 = ("haiku_s1", "haiku_s2", "haiku_s3")
C_MEMBERS = ("sonnet", "haiku", "qwen7b")
D_POOL = ("sonnet", "haiku", "haiku_verifier", "haiku_domain", "haiku_critic", "qwen7b", "qwen1_5b")
JUDGE_SYSTEM = SYSTEM + ("\nYou are the judge. Three independent reviewers answered below. Weigh their reasons, not "
                         "their number; you may disagree with all of them.")
ROUTE_JUDGE_CONF = 0.6


def prompt(c: dict) -> str:
    opts = "\n".join(f"- {k}: {v}" for k, v in c["options"].items())
    return f"{c['question']}\n\nOptions:\n{opts}"


def parse(text: str | None, options) -> dict:
    m = re.search(r"\{.*\}", text or "", re.S)
    try:
        d = json.loads(m.group(0)) if m else {}
    except ValueError:
        d = {}
    a = str(d.get("answer", "")).strip().upper()
    ans = next((k for k in options if k.upper() == a), None)
    try:
        conf = max(0.0, min(1.0, float(d.get("confidence"))))
    except (TypeError, ValueError):
        conf = None
    return {"answer": ans, "confidence": conf, "reason": str(d.get("reason", ""))[:400]}


def call(model: str, temperature: float, system: str, user: str, options) -> dict:
    import litellm

    litellm.suppress_debug_info = True
    t, retries = time.time(), 0
    kw = {"api_base": OLLAMA} if model.startswith("ollama") else {}
    while True:
        try:
            r = litellm.completion(model=model, temperature=temperature, max_tokens=MAX_TOKENS,
                                   messages=[{"role": "system", "content": system}, {"role": "user", "content": user}], **kw)
            break
        except Exception as exc:  # noqa: BLE001 — retried, then recorded as an abstention
            retries += 1
            if retries > 3:
                return {"raw": None, "error": f"{type(exc).__name__}: {str(exc)[:200]}", "retries": retries,
                        "latency_s": round(time.time() - t, 2), "tokens_in": 0, "tokens_out": 0, "cost_usd": None,
                        **parse(None, options)}
            time.sleep(2 ** retries)
    cost = 0.0
    if model.startswith("anthropic"):
        try:
            cost = litellm.completion_cost(completion_response=r)
        except Exception:  # noqa: BLE001 — unknown price: UNKNOWN, never estimated
            cost = None
    text = r.choices[0].message.content
    return {"raw": text, "error": None, "retries": retries, "latency_s": round(time.time() - t, 2),
            "tokens_in": r.usage.prompt_tokens, "tokens_out": r.usage.completion_tokens, "cost_usd": cost,
            **parse(text, options)}


class Cache:
    def __init__(self, path: Path):
        self.path, self.lock, self.rows = path, threading.Lock(), {}
        if path.exists():
            for line in path.read_text().splitlines():
                r = json.loads(line)
                self.rows[(r["member"], r["case_id"])] = r

    def put(self, row: dict) -> None:
        with self.lock:
            self.rows[(row["member"], row["case_id"])] = row
            with self.path.open("a") as f:
                f.write(json.dumps(row) + "\n")


def collect(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    cache = Cache(out / "answers.jsonl")
    # Amendment 1: a provider/transport error is re-asked on the next run; only a
    # completed call (parsed or not) is final. Unparseable answers stay abstentions.
    todo = [(m, c) for m in MEMBERS for c in cases()
            if (m, c["case_id"]) not in cache.rows or cache.rows[(m, c["case_id"])].get("error")
            or (cache.rows[(m, c["case_id"])].get("answer") is None
                and (cache.rows[(m, c["case_id"])].get("tokens_out") or 0) >= OLD_BUDGET
                and cache.rows[(m, c["case_id"])].get("max_tokens", OLD_BUDGET) == OLD_BUDGET)]
    print(f"{len(todo)} calls", flush=True)

    def run(job):
        member, c = job
        model, temp, role = MEMBERS[member]
        system = SYSTEM if role == "neutral" else ROLES[role] + "\n" + SYSTEM
        cache.put({"member": member, "case_id": c["case_id"], "model": model, "temperature": temp, "role": role, "max_tokens": MAX_TOKENS,
                   **call(model, temp, system, prompt(c), c["options"])})

    remote = [j for j in todo if not MEMBERS[j[0]][0].startswith("ollama")]
    local = [j for j in todo if MEMBERS[j[0]][0].startswith("ollama")]
    with ThreadPoolExecutor(6) as pr, ThreadPoolExecutor(1) as pl:
        futs = [pr.submit(run, j) for j in remote] + [pl.submit(run, j) for j in local]
        for i, f in enumerate(futs, 1):
            f.result()
            if i % 100 == 0:
                print(f"{i}/{len(futs)}", flush=True)


def judge(out: Path) -> None:
    ans = Cache(out / "answers.jsonl").rows
    jc = Cache(out / "judge.jsonl")

    def run(c):
        if ("judge", c["case_id"]) in jc.rows and not jc.rows[("judge", c["case_id"])].get("error"):
            return
        block = "\n".join(f"Reviewer {k}: answer={ans[(m, c['case_id'])]['answer']} confidence={ans[(m, c['case_id'])]['confidence']} "
                          f"reason={ans[(m, c['case_id'])]['reason']}" for k, m in enumerate(C_MEMBERS, 1))
        jc.put({"member": "judge", "case_id": c["case_id"], "model": SONNET, "temperature": CLAUDE_T, "role": "judge",
                **call(SONNET, CLAUDE_T, JUDGE_SYSTEM, prompt(c) + "\n\nReviewer answers:\n" + block, c["options"])})

    with ThreadPoolExecutor(6) as pool:
        list(pool.map(run, cases()))


# ── analysis ─────────────────────────────────────────────────────────────────
def plurality(rows: list[dict]) -> dict:
    votes = [r for r in rows if r["answer"]]
    if not votes:
        return {"answer": None, "confidence": None}
    groups: dict[str, list[float]] = {}
    for r in votes:
        groups.setdefault(r["answer"], []).append(r["confidence"] or 0.0)
    top = max(len(v) for v in groups.values())
    tied = {k: sum(v) / len(v) for k, v in groups.items() if len(v) == top}
    return {"answer": max(tied, key=tied.get), "confidence": top / len(rows)}


def macro_f1(y, p, labels):
    f = []
    for lab in labels:
        tp = sum(a == lab and b == lab for a, b in zip(y, p)); fp = sum(a != lab and b == lab for a, b in zip(y, p))
        fn = sum(a == lab and b != lab for a, b in zip(y, p))
        if tp + fp + fn:
            f.append(2 * tp / (2 * tp + fp + fn))
    return sum(f) / len(f) if f else None


def analyze(out: Path) -> dict:
    cs = cases()
    by = {c["case_id"]: c for c in cs}
    ans = Cache(out / "answers.jsonl").rows
    jud = Cache(out / "judge.jsonl").rows
    cal = [c["case_id"] for c in cs if c["split"] == "calibration"]
    ev = [c["case_id"] for c in cs if c["split"] == "evaluation"]
    ids = cal + ev
    pred = {m: {i: ans[(m, i)]["answer"] for i in ids} for m in MEMBERS}

    def acc(p, sel):
        return sum(p[i] == by[i]["answer"] for i in sel) / len(sel) if sel else None

    def crit(p, sel):
        prot = [i for i in sel if by[i]["answer"] not in by[i]["permissive"]]
        return sum(p[i] in by[i]["permissive"] for i in prot) / len(prot) if prot else None

    def alarm(p, sel):
        perm = [i for i in sel if by[i]["answer"] in by[i]["permissive"]]
        return sum(p[i] != by[i]["answer"] and p[i] is not None and p[i] not in by[i]["permissive"] for i in perm) / len(perm) if perm else None

    def boot(pa, pb, sel, fn=acc, n=2000, seed=11):
        if not sel:
            return None
        rng, diffs = random.Random(seed), []
        for _ in range(n):
            s = [rng.choice(sel) for _ in sel]
            a, b = fn(pa, s), fn(pb, s)
            if a is not None and b is not None:
                diffs.append(a - b)
        diffs.sort()
        a, b = fn(pa, sel), fn(pb, sel)
        return {"delta": None if a is None or b is None else round(a - b, 4),
                "ci95": [round(diffs[int(0.025 * len(diffs))], 4), round(diffs[min(len(diffs) - 1, int(0.975 * len(diffs)))], 4)] if diffs else None}

    def council(members):
        return {i: plurality([ans[(m, i)] for m in members])["answer"] for i in ids}

    def usage(members, i, judge_too=False):
        rows = [ans[(m, i)] for m in members] + ([jud[("judge", i)]] if judge_too else [])
        lat = max(ans[(m, i)]["latency_s"] for m in members) + (jud[("judge", i)]["latency_s"] if judge_too else 0)
        cost = None if any(r["cost_usd"] is None for r in rows) else sum(r["cost_usd"] for r in rows)
        return {"calls": len(rows), "tokens": sum(r["tokens_in"] + r["tokens_out"] for r in rows), "latency": lat,
                "cost": cost, "retries": sum(r.get("retries", 0) for r in rows)}

    # A — strong solo by calibration accuracy
    best_solo = max(SOLO_CANDIDATES, key=lambda m: (acc(pred[m], cal), m == "sonnet"))
    conds = {f"A_solo:{m}": {"members": [m], "pred": pred[m], "use": lambda i, m=m: usage([m], i)} for m in MEMBERS}
    for name, mem in (("B1_same_provider_roles", B1), ("B2_same_provider_sampling", B2), ("C_multi_provider", C_MEMBERS)):
        conds[name] = {"members": list(mem), "pred": council(mem), "use": lambda i, mem=mem: usage(mem, i)}

    # failure characteristics → D (calibration only)
    def errs(m, sel):
        return [pred[m][i] != by[i]["answer"] for i in sel]

    def phi(a, b):
        n11 = sum(x and y for x, y in zip(a, b)); n00 = sum(not x and not y for x, y in zip(a, b))
        n10 = sum(x and not y for x, y in zip(a, b)); n01 = sum(not x and y for x, y in zip(a, b))
        d = ((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00)) ** 0.5
        return None if d == 0 else (n11 * n00 - n10 * n01) / d

    def diversity(combo, sel):
        pairs = list(itertools.combinations(combo, 2))
        ph = [x for x in (phi(errs(a, sel), errs(b, sel)) for a, b in pairs) if x is not None]
        df = sum(sum(x and y for x, y in zip(errs(a, sel), errs(b, sel))) / len(sel) for a, b in pairs) / len(pairs)
        return {"mean_error_phi": round(sum(ph) / len(ph), 4) if ph else None, "mean_double_fault": round(df, 4)}

    eligible = [m for m in D_POOL if acc(pred[m], cal) >= 0.5]
    combos = list(itertools.combinations(eligible, 3))
    d_members = list(min(combos, key=lambda c: ((diversity(c, cal)["mean_error_phi"] if diversity(c, cal)["mean_error_phi"] is not None else 1.0),
                                                 diversity(c, cal)["mean_double_fault"]))) if combos else list(C_MEMBERS)
    conds["D_characteristic_diverse"] = {"members": d_members, "pred": council(d_members), "use": lambda i: usage(d_members, i),
                                         "selection": {"eligible": eligible, "calibration": diversity(d_members, cal)}}
    have_judge = all(("judge", i) in jud for i in ids)
    if have_judge:
        conds["E_judge"] = {"members": [*C_MEMBERS, "judge(sonnet)"], "pred": {i: jud[("judge", i)]["answer"] for i in ids},
                            "use": lambda i: usage(C_MEMBERS, i, judge_too=True)}

    # F — adaptive routing (fixed rule)
    routes, f_pred, f_use = {}, {}, {}
    for i in ids:
        c = by[i]
        if c["consequence"] == "high":
            r = "HIGH_CONSEQUENCE"
        elif pred["haiku"][i] is not None and pred["haiku"][i] == pred["qwen7b"][i]:
            r = "NORMAL"
        elif have_judge and (jud[("judge", i)]["confidence"] or 0) >= ROUTE_JUDGE_CONF:
            r = "DISAGREEMENT"
        else:
            r = "PERSISTENT_AMBIGUITY"
        routes[i] = r
        if r == "NORMAL":
            f_pred[i], u = pred["haiku"][i], usage(["haiku", "qwen7b"], i)
        elif r == "DISAGREEMENT":
            f_pred[i], u = jud[("judge", i)]["answer"], usage(list({"haiku", "qwen7b", *C_MEMBERS}), i, judge_too=True)
        else:
            f_pred[i] = conds["D_characteristic_diverse"]["pred"][i]
            base = ["haiku", "qwen7b"] if r == "HIGH_CONSEQUENCE" else list({"haiku", "qwen7b", *C_MEMBERS})
            u = usage(list(dict.fromkeys([*base, *d_members])), i, judge_too=(r == "PERSISTENT_AMBIGUITY" and have_judge))
        f_use[i] = u
    conds["F_adaptive_routing"] = {"members": ["route"], "pred": f_pred, "use": lambda i: f_use[i]}

    solo = pred[best_solo]
    segs = {
        "difficulty:easy": [i for i in ev if by[i]["difficulty"] == "easy"],
        "difficulty:adversarial": [i for i in ev if by[i]["difficulty"] == "adversarial"],
        "difficulty:ambiguous": [i for i in ev if by[i]["difficulty"] == "ambiguous"],
        "consequence:high": [i for i in ev if by[i]["consequence"] == "high"],
        "consequence:normal": [i for i in ev if by[i]["consequence"] == "normal"],
        **{f"family:{f}": [i for i in ev if by[i]["family"] == f] for f in sorted({c["family"] for c in cs})},
    }
    risk_segments = ("difficulty:adversarial", "difficulty:ambiguous", "consequence:high")
    labels_fs = ("LEAKAGE", "PROXY", "REVIEW", "OK")
    fs_ev = segs["family:feature_screening"]

    results = {}
    for name, c in conds.items():
        p = c["pred"]
        u = [c["use"](i) for i in ev]
        disagree = [i for i in ev if len({pred[m][i] for m in (c["members"] if name[:1] in "BCD" else C_MEMBERS) if m in pred}) > 1]
        row = {
            "members": c["members"], "accuracy": round(acc(p, ev), 4), "critical_miss_rate": crit(p, ev), "false_alarm_rate": alarm(p, ev),
            "feature_screening_macro_f1": macro_f1([by[i]["answer"] for i in fs_ev], [p[i] for i in fs_ev], labels_fs),
            "format_failures": sum(p[i] is None for i in ev),
            "vs_strong_solo": boot(p, solo, ev),
            "vs_strong_solo_critical_miss": boot(p, solo, ev, crit),
            "segments": {k: {"n": len(v), "accuracy": acc(p, v), "vs_strong_solo": boot(p, solo, v)} for k, v in segs.items() if v},
            "correction_rate_vs_solo": f"{sum(solo[i] != by[i]['answer'] and p[i] == by[i]['answer'] for i in ev)} / {sum(solo[i] != by[i]['answer'] for i in ev)}",
            "new_errors_vs_solo": f"{sum(solo[i] == by[i]['answer'] and p[i] != by[i]['answer'] for i in ev)} / {sum(solo[i] == by[i]['answer'] for i in ev)}",
            "disagreement_resolution": f"{sum(p[i] == by[i]['answer'] for i in disagree)} / {len(disagree)}",
            "calls_per_decision": round(sum(x["calls"] for x in u) / len(u), 2),
            "tokens_per_decision": round(sum(x["tokens"] for x in u) / len(u), 1),
            "latency_s_per_decision": round(sum(x["latency"] for x in u) / len(u), 2),
            "cost_usd_per_decision": None if any(x["cost"] is None for x in u) else round(sum(x["cost"] for x in u) / len(u), 6),
            "retries": sum(x["retries"] for x in u),
        }
        row["segments_improved"] = [k for k, v in row["segments"].items() if v["vs_strong_solo"] and v["vs_strong_solo"]["ci95"][0] > 0]
        row["segments_degraded"] = [k for k, v in row["segments"].items() if v["vs_strong_solo"] and v["vs_strong_solo"]["ci95"][1] < 0]
        if name[:1] in "BCD":
            best_m = max(c["members"], key=lambda m: acc(pred[m], ev))
            row["vs_own_best_member"] = {"member": best_m, **boot(p, pred[best_m], ev)}
            row["evaluation_diversity"] = diversity(c["members"], ev)
        if "selection" in c:
            row["selection"] = c["selection"]
        if name == "F_adaptive_routing":
            row["routes"] = {r: sum(routes[i] == r for i in ev) for r in ("NORMAL", "DISAGREEMENT", "PERSISTENT_AMBIGUITY", "HIGH_CONSEQUENCE")}
            row["escalated_to_human"] = f"{row['routes']['HIGH_CONSEQUENCE']} / {len(ev)}"
        results[name] = row

    # characteristics per member (derived from behaviour)
    def char(m):
        p = pred[m]
        easy, adv = acc(p, segs["difficulty:easy"]), acc(p, segs["difficulty:adversarial"])
        return {"model": MEMBERS[m][0], "role": MEMBERS[m][2], "temperature": MEMBERS[m][1],
                "accuracy": round(acc(p, ev), 4), "calibration_accuracy": round(acc(p, cal), 4),
                "permissiveness_critical_miss": crit(p, ev), "conservatism_false_alarm": alarm(p, ev),
                "literal_vs_inferential_gap": None if easy is None or adv is None else round(easy - adv, 4),
                "ambiguity_handling": acc(p, segs["difficulty:ambiguous"]),
                "leakage_sensitivity": acc(p, [i for i in ev if by[i]["answer"] == "LEAKAGE"]),
                "verifier_strength": acc(p, segs["family:validation_interpretation"]),
                "quantitative_strength": acc(p, segs["family:model_selection"]),
                "policy_reasoning": acc(p, segs["family:policy_conflict"]),
                "format_failures": sum(p[i] is None for i in ev)}

    profiles = {m: char(m) for m in MEMBERS}
    pair_phi = {f"{a}~{b}": phi(errs(a, ev), errs(b, ev)) for a, b in itertools.combinations(D_POOL, 2)}

    # H2 — association over all 3-combinations of the pool
    combo_rows = []
    for cmb in itertools.combinations(D_POOL, 3):
        p = council(cmb)
        best = max(acc(pred[m], ev) for m in cmb)
        combo_rows.append({"members": list(cmb), "providers": len({PROVIDER[MEMBERS[m][0]] for m in cmb}),
                           "accuracy": round(acc(p, ev), 4), "gain_over_best_member": round(acc(p, ev) - best, 4), **diversity(cmb, ev)})

    def spearman(xs, ys):
        pts = [(x, y) for x, y in zip(xs, ys) if x is not None]
        if len(pts) < 4:
            return None

        def rank(v):
            o = sorted(range(len(v)), key=lambda k: v[k]); r = [0.0] * len(v); k = 0
            while k < len(v):
                j = k
                while j + 1 < len(v) and v[o[j + 1]] == v[o[k]]:
                    j += 1
                for t in range(k, j + 1):
                    r[o[t]] = (k + j) / 2
                k = j + 1
            return r
        rx, ry = rank([a for a, _ in pts]), rank([b for _, b in pts]); n = len(pts)
        mx, my = sum(rx) / n, sum(ry) / n
        sx = sum((a - mx) ** 2 for a in rx) ** 0.5; sy = sum((b - my) ** 2 for b in ry) ** 0.5
        return None if not sx or not sy else round(sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / (sx * sy), 3)

    g = [r["gain_over_best_member"] for r in combo_rows]
    by_prov = {}
    for r in combo_rows:
        by_prov.setdefault(r["providers"], []).append(r["gain_over_best_member"])
    h2 = {"combinations": len(combo_rows),
          "spearman_gain_vs_error_phi": spearman([r["mean_error_phi"] for r in combo_rows], g),
          "spearman_gain_vs_double_fault": spearman([r["mean_double_fault"] for r in combo_rows], g),
          "spearman_gain_vs_provider_count": spearman([r["providers"] for r in combo_rows], g),
          "mean_gain_by_provider_count": {k: {"n": len(v), "mean_gain": round(sum(v) / len(v), 4)} for k, v in sorted(by_prov.items())},
          "top5_by_gain": sorted(combo_rows, key=lambda r: -r["gain_over_best_member"])[:5],
          "C_vs_D": {"C_multi_provider": results["C_multi_provider"]["accuracy"], "D_characteristic_diverse": results["D_characteristic_diverse"]["accuracy"],
                     "D_minus_C": boot(conds["D_characteristic_diverse"]["pred"], conds["C_multi_provider"]["pred"], ev)},
          "note": "Descriptive: combinations overlap and are not independent samples."}

    # decisions per condition (pre-registered rules)
    def decide(name, r):
        overall = r["vs_strong_solo"]
        no_worse_safety = (r["critical_miss_rate"] or 0) <= (results[f"A_solo:{best_solo}"]["critical_miss_rate"] or 0)
        if overall["ci95"][0] > 0 and no_worse_safety:
            return "SUPPORTED"
        seg_gain = [k for k in risk_segments if r["segments"].get(k, {}).get("vs_strong_solo") and r["segments"][k]["vs_strong_solo"]["ci95"][0] > 0]
        f_frontier = False
        if name == "F_adaptive_routing":
            always = [k for k in ("B1_same_provider_roles", "B2_same_provider_sampling", "C_multi_provider", "D_characteristic_diverse", "E_judge") if k in results]
            bestc = max(always, key=lambda k: results[k]["accuracy"])
            f_frontier = r["accuracy"] >= results[bestc]["accuracy"] - 0.03 and r["tokens_per_decision"] <= 0.5 * results[bestc]["tokens_per_decision"]
        if seg_gain or f_frontier:
            return "CONDITIONAL_VALUE"
        if overall["ci95"][1] < 0.02:
            return "REJECTED"
        return "INSUFFICIENT_EVIDENCE"

    decisions = {k: decide(k, v) for k, v in results.items() if not k.startswith("A_solo")}
    always = [k for k in decisions if k != "F_adaptive_routing"]
    overall_sup = [k for k in always if decisions[k] == "SUPPORTED"]
    seg_only = [k for k in always if decisions[k] == "CONDITIONAL_VALUE"]
    best_always = max(always, key=lambda k: results[k]["accuracy"])
    fr = results["F_adaptive_routing"]
    hyp = {
        "H0": "REJECTED" if overall_sup else "NOT_REJECTED",
        "H1": "SUPPORTED" if seg_only and not overall_sup else ("PARTIAL" if seg_only else "NOT_SUPPORTED"),
        "H2": h2,
        "H3": {"F_accuracy": fr["accuracy"], "F_tokens": fr["tokens_per_decision"], "F_latency": fr["latency_s_per_decision"],
               "best_always_on": best_always, "best_always_accuracy": results[best_always]["accuracy"],
               "best_always_tokens": results[best_always]["tokens_per_decision"],
               "best_always_latency": results[best_always]["latency_s_per_decision"],
               "F_vs_best_always": boot(conds["F_adaptive_routing"]["pred"], conds[best_always]["pred"], ev),
               "F_decision": decisions["F_adaptive_routing"]},
    }
    repro = sum(pred["haiku"][i] == pred["haiku_repeat"][i] for i in ids)
    return {"n_cases": len(cs), "n_calibration": len(cal), "n_evaluation": len(ev), "strong_solo": best_solo,
            "decisions": decisions, "hypotheses": hyp, "conditions": results, "member_characteristics": profiles,
            "pairwise_error_phi_evaluation": pair_phi,
            "system_quality": {"reproducibility_haiku_T1_two_samples": f"{repro} / {len(ids)} identical answers on re-run",
                               "validator_agreement": "NOT_MEASURED — harness calls models directly, not through the product's Validator path",
                               "organization_context_use": "NOT_MEASURED — cases carry their own facts; no tenant context was injected"}}


if __name__ == "__main__":
    cmd, out = sys.argv[1], Path(sys.argv[2])
    if cmd == "collect":
        collect(out)
    elif cmd == "judge":
        judge(out)
    elif cmd == "analyze":
        res = analyze(out)
        (out / "results.json").write_text(json.dumps(res, indent=1, default=str))
        print(json.dumps({"strong_solo": res["strong_solo"], "decisions": res["decisions"],
                          "H0": res["hypotheses"]["H0"], "H1": res["hypotheses"]["H1"]}, indent=1))
