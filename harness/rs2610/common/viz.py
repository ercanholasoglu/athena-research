"""Shared figure style (reference palette, validated light mode; values labelled because 3 slots < 3:1 contrast)."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e4e3df"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
MARKERS = ["o", "s", "^", "D", "v"]

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10, "axes.titlesize": 11,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "legend.frameon": False, "figure.dpi": 150,
})


def bars(ax, labels, values, errs=None, colors=None, fmt="{:.2f}", ylabel="", ylim=None):
    colors = colors or SERIES[: len(labels)]
    x = range(len(labels))
    yerr = None
    if errs is not None:
        yerr = [[max(0, v - lo) for v, (lo, hi) in zip(values, errs)], [max(0, hi - v) for v, (lo, hi) in zip(values, errs)]]
    ax.bar(x, values, color=colors, width=0.62, edgecolor=SURFACE, linewidth=2, yerr=yerr,
           error_kw={"ecolor": INK2, "elinewidth": 1, "capsize": 3})
    for i, v in enumerate(values):
        if v == v:  # not NaN
            top = (errs[i][1] if errs is not None else v)
            ax.text(i, top, " " + fmt.format(v), ha="center", va="bottom", fontsize=8, color=INK)
    ax.set_xticks(list(x), labels)
    ax.set_ylabel(ylabel)
    if ylim:
        ax.set_ylim(*ylim)
    ax.grid(axis="x", visible=False)
    return ax


def save(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
