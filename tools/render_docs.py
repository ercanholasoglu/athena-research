"""Render the documentation from `templates/`: every number in a README or doc is a `{{key|mode}}` fact reference.

    python tools/render_docs.py           # templates/<path>.md -> <path>.md
    python tools/render_docs.py --check   # fails if a rendered file differs from its template + facts

Keys resolve from `harness/rs2610/outputs/facts.json` (Studies A, B), `.../replication/facts-replication.json` (`r.*`,
A2, B2), `research/jev/results/facts.json` (prefix `jev:`) and `research/council-ablation/results/facts.json` (prefix
`council:`). Formatting is the harness's own
(`rs2610.make_facts.fmt`): `pct`, `pp`, `p`, `int`, `0`–`4` decimals. An unknown key fails. Write `\\{\\{x\\}\\}` for
literal double braces.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "harness"))

from rs2610.make_facts import render  # noqa: E402

OUT = REPO / "harness" / "rs2610" / "outputs"
TEMPLATES = REPO / "templates"


def facts() -> dict:
    f = json.loads((OUT / "facts.json").read_text())
    f.update(json.loads((OUT / "replication" / "facts-replication.json").read_text()))
    f.update({f"jev:{k}": v for k, v in json.loads((REPO / "research" / "jev" / "results" / "facts.json").read_text()).items()})
    f.update({f"council:{k}": v for k, v in json.loads((REPO / "research" / "council-ablation" / "results" / "facts.json").read_text()).items()})
    return f


def main() -> None:
    fx, stale = facts(), []
    for t in sorted(TEMPLATES.rglob("*.md")):
        rel = t.relative_to(TEMPLATES)
        raw = t.read_text().replace("\\{\\{", "\x00").replace("\\}\\}", "\x01")  # \{\{ ... \}\} = literal braces
        text = render(raw, fx).replace("p = < 0.001", "p < 0.001").replace("\x00", "{{").replace("\x01", "}}")
        dest = REPO / rel
        if "--check" in sys.argv:
            if not dest.exists() or dest.read_text() != text:
                stale.append(str(rel))
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text)
            print("wrote", rel)
    if stale:
        sys.exit(f"rendered docs differ from templates: {stale}")
    if "--check" in sys.argv:
        print("DOCS OK")


if __name__ == "__main__":
    main()
