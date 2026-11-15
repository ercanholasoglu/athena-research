"""Clean-kernel Restart + Run All of every notebook; writes outputs in place and a run record.

Each notebook runs in a fresh kernel started in ``notebooks/``. A notebook passes only when
every cell executes without an error. The record (``evidence/notebook_runs.json``) lists
the result, duration and environment of each run.
"""
from __future__ import annotations

import json
import platform
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    runs, failed = [], 0
    for path in sorted((ROOT / "notebooks").glob("[0-9][0-9]_*.ipynb")):
        book = nbformat.read(path, as_version=4)
        for cell in book.cells:  # Restart: drop every previous output and execution count
            if cell.cell_type == "code":
                cell.outputs, cell.execution_count = [], None
        t = time.time()
        try:
            NotebookClient(book, timeout=600, kernel_name="python3",
                           resources={"metadata": {"path": str(path.parent)}}).execute()
            result, error = "PASS", None
        except Exception as exc:  # recorded, never hidden
            result, error, failed = "FAIL", f"{type(exc).__name__}: {str(exc)[:300]}", failed + 1
        nbformat.write(book, path)
        cells = sum(c.cell_type == "code" for c in book.cells)
        runs.append({"notebook": f"notebooks/{path.name}", "result": result, "code_cells": cells,
                     "seconds": round(time.time() - t, 2), "error": error})
        print(result, path.name, f"{runs[-1]['seconds']}s", error or "")
    import nbclient
    import numpy
    import pandas
    record = {"recorded_at": datetime.now(UTC).isoformat(timespec="seconds"), "mode": "clean kernel, Restart + Run All",
              "environment": {"python": platform.python_version(), "system": platform.system(), "machine": platform.machine(),
                              "pandas": pandas.__version__, "numpy": numpy.__version__, "nbclient": nbclient.__version__},
              "seed": 11, "runs": runs}
    (ROOT / "evidence" / "notebook_runs.json").write_text(json.dumps(record, indent=1) + "\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
