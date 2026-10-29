"""Exact code excerpts for the articles: cut verbatim from the frozen harness, with file, line range and file SHA-256.

    python -m rs2610.replication.make_excerpts    # -> outputs/replication/CODE_EXCERPTS.md

Nothing is paraphrased. An excerpt is either a whole function (``ast``) or the lines between two marker strings.
"""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "replication" / "CODE_EXCERPTS.md"

EXCERPTS = [
    ("DIRECT execution", "study_a/topologies.py", ("func", "_direct")),
    ("CoT execution", "study_a/topologies.py", ("func", "_cot")),
    ("ToT: isolated branch evaluation, deterministic pruning", "study_a/topologies.py", ("range", "        for k, cand in enumerate(seen):", "        pruned = [b for b in branches if b not in keep]")),
    ("GoT: typed edges, deterministic propagation over the graph, aggregation input", "study_a/topologies.py", ("range", "        E = [e for e in edges.get(\"edges\", [])", "        top2 = ranked[:2]")),
    ("Semantic condition construction", "study_b/conditions.py", ("range", "def run_condition(", "    pre = \"\"")),
    ("Dictionary injection", "study_b/conditions.py", ("func", "documentation")),
    ("Feature-invention call (no candidates shown)", "replication/b2/invention.py", ("func", "invent")),
    ("Feature validation: classes", "replication/b2/evaluate.py", ("range", "    valid = not res[\"leakage\"]", "        res[\"class\"] = \"INVALID_HIGH_APPARENT\"")),
    ("Frontier substrate: schema adaptation", "replication/providers.py", ("func", "strict_schema")),
]


def cut(src: str, spec: tuple) -> tuple[str, int, int]:
    lines = src.splitlines()
    if spec[0] == "func":
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == spec[1]:
                return "\n".join(lines[node.lineno - 1: node.end_lineno]), node.lineno, node.end_lineno
        raise KeyError(spec)
    start = next(i for i, l in enumerate(lines) if l.startswith(spec[1]))
    end = next(i for i, l in enumerate(lines) if i >= start and l.startswith(spec[2]))
    return "\n".join(lines[start: end + 1]), start + 1, end + 1


def main() -> None:
    L = ["# Code excerpts (verbatim from the research harness)", "",
         "Each block is cut by `replication/make_excerpts.py` from the file named, at the lines given. The file hash is the one "
         "recorded in the governing freeze record, so the excerpt is the code that ran. Nothing is simplified.", ""]
    for title, f, spec in EXCERPTS:
        src = (ROOT / f).read_text()
        code, a, b = cut(src, spec)
        L += [f"## {title}", "", f"`{f}` lines {a}–{b}, file SHA-256 `{hashlib.sha256(src.encode()).hexdigest()[:16]}…`", "", "```python", code, "```", ""]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L))
    print("written", OUT, len(EXCERPTS), "excerpts")


if __name__ == "__main__":
    main()
