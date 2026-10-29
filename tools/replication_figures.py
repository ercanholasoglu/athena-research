"""Figures for A2, B2 and the cross-study comparison, drawn from the committed result tables.

    python tools/replication_figures.py

Descriptive figures only, added for the public repository. Each figure names its source table; the table is the
accessible view of the same numbers. Colours follow the model, never its rank: qwen2.5:7b blue, gpt-6-luna orange,
claude-sonnet-5-5 aqua (validated categorical palette; every bar carries a value label because aqua is below 3:1
contrast on the surface).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "harness" / "rs2610" / "outputs"
RES = REPO / "research"
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
COLOR = {"qwen2.5:7b": "#2a78d6", "gpt-6-luna": "#eb6834", "claude-sonnet-5-5": "#1baf7a"}
MODES = ["DIRECT", "COT", "TOT", "GOT"]


def style(ax, title: str, source: str) -> None:
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.grid(axis="y", color="#e6e5e1", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", color=INK, fontsize=11, pad=12)
    ax.figure.text(0.01, 0.01, f"Source: {source}", color=MUTED, fontsize=7.5)


def save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.patch.set_facecolor(SURFACE)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=SURFACE, metadata={"Software": None})
    plt.close(fig)
    print("wrote", path.relative_to(REPO))


def bars(ax, groups: list[str], series: dict[str, list[float]], lo: dict | None = None, hi: dict | None = None,
         pct: bool = True) -> None:
    n = len(series)
    w = 0.8 / n
    x = np.arange(len(groups))
    for i, (name, vals) in enumerate(series.items()):
        pos = x - 0.4 + w * (i + 0.5)
        v = np.array(vals, dtype=float)
        ax.bar(pos, v, width=w - 0.02, color=COLOR[name], label=name, edgecolor=SURFACE, linewidth=1)
        if lo and hi:
            ax.errorbar(pos, v, yerr=[v - np.array(lo[name]), np.array(hi[name]) - v], fmt="none", ecolor=INK2,
                        elinewidth=1, capsize=2)
        for p, val in zip(pos, v):
            if not np.isnan(val):
                ax.text(p, val + (0.02 if pct else 0.01), f"{100 * val:.0f}" if pct else f"{val:.2f}", ha="center",
                        va="bottom", fontsize=7.5, color=INK)
    ax.set_xticks(x, groups)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left", bbox_to_anchor=(1.0, 1.0), labelcolor=INK2)


def a2() -> None:
    r = pd.read_csv(OUT / "replication" / "a2" / "a2-results.csv").set_index(["model", "mode"])
    models = ["qwen2.5:7b", "gpt-6-luna"]
    fig, ax = plt.subplots(figsize=(8, 4))
    bars(ax, MODES, {m: [r.loc[(m, k), "accuracy"] for k in MODES] for m in models},
         {m: [r.loc[(m, k), "acc_ci_lo"] for k in MODES] for m in models},
         {m: [r.loc[(m, k), "acc_ci_hi"] for k in MODES] for m in models})
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("accuracy (share of runs correct)", color=INK2, fontsize=9)
    style(ax, "A2: accuracy by topology, 64 unseen decisions × 3 replicates (95% instance-cluster CI)",
          "harness/rs2610/outputs/replication/a2/a2-results.csv")
    save(fig, RES / "reasoning-topology" / "frontier-replication" / "figures" / "a2-accuracy-by-topology.png")

    e = pd.read_csv(OUT / "replication" / "a2" / "a2-error-decomposition.csv").set_index(["model", "mode"])
    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(MODES))
    for i, m in enumerate(models):
        pos = x - 0.2 + 0.4 * i
        opt = np.array([e.loc[(m, k), "wrong_option"] for k in MODES], dtype=float)
        ab = np.array([e.loc[(m, k), "wrong_abstained"] for k in MODES], dtype=float)
        ax.bar(pos, opt, width=0.38, color=COLOR[m], edgecolor=SURFACE, linewidth=1, label=f"{m}: wrong option")
        ax.bar(pos, ab, width=0.38, bottom=opt, color=SURFACE, edgecolor=COLOR[m], hatch="////", linewidth=1,
               label=f"{m}: abstained")
        for p, a_, b_ in zip(pos, opt, ab):
            ax.text(p, a_ + b_ + 1, f"{int(a_)}+{int(b_)}", ha="center", va="bottom", fontsize=7.5, color=INK)
    ax.set_xticks(x, MODES)
    ax.set_ylabel("wrong runs (of 192)", color=INK2, fontsize=9)
    ax.legend(frameon=False, fontsize=8, loc="upper left", bbox_to_anchor=(1.0, 1.0), labelcolor=INK2)
    style(ax, "A2: wrong runs split into wrong option (solid) and abstention (hatched)",
          "harness/rs2610/outputs/replication/a2/a2-error-decomposition.csv")
    save(fig, RES / "reasoning-topology" / "frontier-replication" / "figures" / "a2-error-decomposition.png")


def b2() -> None:
    r = pd.read_csv(OUT / "replication" / "b2" / "b2-results.csv").set_index(["model", "cell"])
    models = ["qwen2.5:7b", "gpt-6-luna", "claude-sonnet-5-5"]
    cells = ["trapped:A_RAW", "trapped:C_DICT", "trapped:D_RULES", "anonymized:A_RAW", "anonymized:C_DICT",
             "incomplete:D_RULES", "misleading:D_RULES"]
    labels = [c.replace(":", "\n") for c in cells]
    for metric, title, name in (("all_traps_blocked", "B2: share of runs that blocked every trap", "b2-all-traps-blocked.png"),
                                ("core_semantic_accuracy", "B2: core semantic accuracy", "b2-core-semantic-accuracy.png")):
        fig, ax = plt.subplots(figsize=(10, 4))
        bars(ax, labels, {m: [r.loc[(m, c), metric] for c in cells] for m in models})
        ax.set_ylim(0, 1.12)
        style(ax, f"{title} (qwen, luna: 8 units per cell; sonnet: 4)", "harness/rs2610/outputs/replication/b2/b2-results.csv")
        save(fig, RES / "semantic-context" / "frontier-replication" / "figures" / name)

    fc = pd.read_csv(OUT / "replication" / "b2" / "b2-feature-classes.csv")
    fc = fc[fc.source == "invention"].set_index("model")
    classes = ["VALID_USEFUL", "VALID_NOT_USEFUL", "INVALID_LOW_GAIN", "INVALID_HIGH_APPARENT", "NOT_EXECUTABLE"]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    share = fc[classes].div(fc[classes].sum(axis=1), axis=0)
    y = np.arange(len(models))
    hatch = ["", "", "..", "////", "xx"]
    left = np.zeros(len(models))
    for k, h in zip(classes, hatch):
        v = share.loc[models, k].to_numpy()
        ax.barh(y, v, left=left, color=[COLOR[m] for m in models], alpha=1.0 if k.startswith("VALID") else 0.35,
                hatch=h, edgecolor=SURFACE, linewidth=1.5, label=k)
        for yy, l_, vv in zip(y, left, v):
            if vv >= 0.06:
                ax.text(l_ + vv / 2, yy, f"{100 * vv:.0f}", ha="center", va="center", fontsize=7.5, color=INK)
        left += v
    ax.set_yticks(y, models)
    ax.set_xlim(0, 1)
    ax.grid(False)
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=MUTED, alpha=1.0 if k.startswith("VALID") else 0.35, hatch=h,
                             edgecolor=SURFACE) for k, h in zip(classes, hatch)]
    ax.legend(handles, classes, frameon=False, fontsize=7.5, loc="upper left", bbox_to_anchor=(1.0, 1.0), labelcolor=INK2)
    style(ax, "B2: invented features by validator class (share of each model's inventions)",
          "harness/rs2610/outputs/replication/b2/b2-feature-classes.csv")
    save(fig, RES / "semantic-context" / "frontier-replication" / "figures" / "b2-invention-classes.png")


def cross() -> None:
    x = pd.read_csv(OUT / "replication" / "cross-study.csv")
    x["label"] = x.axis + " · " + x.study + " · " + x.metric.str.replace("_", " ")
    order = x.sort_values(["axis", "study", "metric"])
    fig, ax = plt.subplots(figsize=(9, 5))
    rows = list(dict.fromkeys(order.label))
    for i, lab in enumerate(rows):
        g = order[order.label == lab]
        for j, (_, r) in enumerate(g.iterrows()):
            yy = i + (j - (len(g) - 1) / 2) * 0.22
            ax.plot([100 * r.ci_lo, 100 * r.ci_hi], [yy, yy], color=COLOR[r.model], linewidth=2, solid_capstyle="round")
            ax.plot(100 * r.effect, yy, "o", markersize=8, color=COLOR[r.model], markeredgecolor=SURFACE, markeredgewidth=2)
            ax.text(100 * r.ci_hi + 2, yy, f"{100 * r.effect:+.1f}", va="center", fontsize=7.5, color=INK)
    ax.axvline(0, color=MUTED, linewidth=1)
    ax.set_yticks(range(len(rows)), rows, fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlabel("effect, percentage points (95% CI); scales differ across rows, compare order only", color=INK2, fontsize=9)
    ax.grid(axis="x", color="#e6e5e1", linewidth=0.8)
    ax.grid(axis="y", visible=False)
    handles = [plt.Line2D([], [], marker="o", color=c, linewidth=2, markersize=7) for c in COLOR.values()]
    ax.legend(handles, list(COLOR), frameon=False, fontsize=8.5, loc="upper left", bbox_to_anchor=(1.0, 1.0), labelcolor=INK2)
    style(ax, "Capability, structure and semantics: effect sizes side by side", "harness/rs2610/outputs/replication/cross-study.csv")
    save(fig, RES / "cross-study" / "figures" / "cross-study-effects.png")


if __name__ == "__main__":
    a2()
    b2()
    cross()
