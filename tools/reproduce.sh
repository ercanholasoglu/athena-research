#!/usr/bin/env bash
# Regenerate every statistic, table, figure, report, trace and rendered doc from the committed run evidence, then show
# what changed. No model is called: runs and ledgers are committed, and the analyses read them.
#
#   bash tools/reproduce.sh            # full: data, freeze verification, statistics, figures, reports, checks
#   bash tools/reproduce.sh --no-data  # skip dataset download/verification and the steps that need the raw data
#
# Needs the environment from requirements-lock.txt (see docs/REPRODUCIBILITY.md). The B2 and Study B analyses
# re-evaluate every proposed feature with gradient-boosted models; budget roughly an hour on a laptop.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-python}"
step() { printf '\n== %s\n' "$*"; }

if [[ "${1:-}" != "--no-data" ]]; then
  step "datasets: download what is missing, verify against the frozen hashes"
  "$PY" tools/prepare_data.py
  step "freeze verification (sources, prompts, datasets, configuration)"
  (cd harness && "$PY" -m rs2610.freeze --verify A && "$PY" -m rs2610.freeze --verify B && "$PY" -m rs2610.replication.freeze --verify)
  step "statistics: original studies"
  (cd harness && "$PY" -m rs2610.study_a.analyze && "$PY" -m rs2610.study_b.analyze && "$PY" -m rs2610.study_a.structure_fig \
    && "$PY" -m rs2610.analyze_extra)
  step "statistics: frontier replication"
  (cd harness && "$PY" -m rs2610.replication.a2.analyze && "$PY" -m rs2610.replication.b2.analyze && "$PY" -m rs2610.replication.cross)
  step "prompt examples (replayed against the ledgers)"
  "$PY" tools/export_prompts.py
fi

step "facts and reports"
(cd harness && "$PY" -m rs2610.make_facts && "$PY" -m rs2610.make_report && "$PY" -m rs2610.replication.make_configs \
  && "$PY" -m rs2610.replication.make_facts && "$PY" -m rs2610.replication.make_excerpts && "$PY" -m rs2610.replication.make_report)
step "figures added for the public repository"
"$PY" tools/replication_figures.py
step "JEV facts, traces, rendered docs"
"$PY" research/jev/tools/derive_facts.py --check
"$PY" tools/make_trace.py --check
"$PY" tools/render_docs.py --check
step "public-release audit"
"$PY" tools/check_repo.py

step "difference from the committed files (empty = reproduced exactly)"
if git rev-parse --git-dir >/dev/null 2>&1; then
  git status --porcelain -- harness research docs README.md
else
  echo "not a git checkout: compare against a fresh clone"
fi
