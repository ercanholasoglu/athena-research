"""Draw the observable structure of one ToT and one GoT run (ids, scores and edge types only).

    python -m rs2610.study_a.structure_fig [instance_id] [seed]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from rs2610.common.viz import INK, INK2, SERIES, SURFACE, plt, save

ART = Path(__file__).resolve().parents[1] / "artifacts" / "study_a"
FIG = Path(__file__).resolve().parents[1] / "outputs" / "study_a" / "study-a-figures"


def _runs(tag: str = "unseen") -> list[dict]:
    p = ART / f"runs_{tag}.jsonl"
    return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []


def tot(ax, run: dict) -> None:
    st = run["trace"]["structure"]
    ax.set_axis_off()
    ax.scatter([0], [0], s=500, color=INK2, zorder=3)
    ax.text(0, 0.18, "root", ha="center", fontsize=8, color=INK)
    for i, b in enumerate(st):
        y = (len(st) - 1) / 2 - i
        col = SERIES[0] if b["kept"] else "#c9c8c2"
        ax.plot([0, 1], [0, y], color=col, lw=2 if b["kept"] else 1, ls="-" if b["kept"] else "--", zorder=1)
        ax.scatter([1], [y], s=420, color=col, zorder=3, edgecolor=SURFACE, linewidth=2)
        ax.text(1, y + 0.2, f"{b['option']}\nscore {b['score']:.0f}{'' if b['kept'] else ' · pruned'}", ha="center", fontsize=7.5, color=INK)
        for j, s in enumerate(b["leaf_scores"]):
            yy = y + (j - 0.5) * 0.42
            ax.plot([1, 2], [y, yy], color=col, lw=1, zorder=1)
            ax.scatter([2], [yy], s=160, color=col, zorder=3, edgecolor=SURFACE, linewidth=1.5)
            ax.text(2.12, yy, f"refinement {j + 1}: {s}", va="center", fontsize=7, color=INK2)
    final = run["decision"]
    ax.text(0, -1.9, f"final decision: {final}  (correct: {run['correct']})", fontsize=8, color=INK)
    ax.set_xlim(-0.3, 3.1)
    ax.set_title(f"ToT — {run['instance_id']} (seed {run['seed']})", fontsize=9)


def got(ax, run: dict) -> None:
    st = run["trace"]["structure"]
    edges = st["edges"]
    claims = sorted({e[0] for e in edges} | {c for pair in st["conflicts"] for c in pair}, key=lambda c: int("".join(ch for ch in c if ch.isdigit()) or 0))
    cands = sorted(st["scores"], key=lambda c: -st["scores"][c])
    cy = {c: (len(claims) - 1) / 2 - i for i, c in enumerate(claims)}
    ky = {c: ((len(cands) - 1) / 2 - i) * 1.6 for i, c in enumerate(cands)}
    ax.set_axis_off()
    for cl, ca, rel in edges:
        ax.plot([0, 2], [cy[cl], ky[ca]], color=SERIES[0] if rel == "supports" else SERIES[1], lw=1.2, ls="-" if rel == "supports" else "--", alpha=0.8)
    for a, b in st["conflicts"]:
        if a in cy and b in cy:
            ax.annotate("", (-0.05, cy[b]), (-0.05, cy[a]), arrowprops={"arrowstyle": "-", "color": SERIES[4], "lw": 1.5, "connectionstyle": "arc3,rad=0.5"})
    for c in claims:
        reused = c in st["reused_claims"]
        ax.scatter([0], [cy[c]], s=200 if reused else 120, color=SERIES[2] if reused else "#c9c8c2", edgecolor=SURFACE, linewidth=1.5, zorder=3)
        ax.text(-0.15, cy[c], c, ha="right", va="center", fontsize=7.5, color=INK)
    for c in cands:
        ax.scatter([2], [ky[c]], s=420, color=SERIES[3], edgecolor=SURFACE, linewidth=2, zorder=3)
        ax.text(2.15, ky[c], f"{c}  ({st['scores'][c]:+.1f})", va="center", fontsize=7.5, color=INK)
    if st.get("merged"):
        ax.scatter([3.3], [0], s=420, color=SERIES[4], zorder=3)
        ax.text(3.3, 0.3, f"merged: {st['merged']}", ha="center", fontsize=7.5)
        for c in cands[:2]:
            ax.plot([2, 3.3], [ky[c], 0], color=SERIES[4], lw=1)
    ax.text(-0.4, min(cy.values(), default=0) - 1.0,
            f"claims reused by ≥2 candidates: {len(st['reused_claims'])} (aqua) · claim conflicts: {len(st['conflicts'])} (magenta arcs) · "
            f"solid = supports, dashed = contradicts · final: {run['decision']} (correct: {run['correct']})", fontsize=7, color=INK2)
    ax.set_xlim(-0.8, 4.2)
    ax.set_title(f"GoT — {run['instance_id']} (seed {run['seed']})", fontsize=9)


def main() -> None:
    runs = _runs() or _runs("dev")
    want = sys.argv[1] if len(sys.argv) > 1 else None
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    pick = [r for r in runs if (want is None or r["instance_id"] == want) and r["seed"] == seed]
    t = next(r for r in pick if r["mode"] == "TOT" and r["trace"].get("structure"))
    g = next(r for r in pick if r["mode"] == "GOT" and r["trace"].get("structure") and r["instance_id"] == t["instance_id"])
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.6))
    tot(axs[0], t)
    got(axs[1], g)
    save(fig, FIG / "sample_structures.png")
    print(t["instance_id"])


if __name__ == "__main__":
    main()
