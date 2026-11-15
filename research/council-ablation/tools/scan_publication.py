"""Pre-publication scan: secrets, PII, internal hosts, absolute user paths, raw model output, licence files.

Exit code 0 only when nothing blocking is found. Writes ``evidence/publication_scan.json``.
Allowed findings are listed explicitly in ``ALLOW`` with a reason; nothing is silently skipped.

    python research/council-ablation/tools/scan_publication.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # research/council-ablation; the whole repository is audited by tools/check_repo.py
REPO = ROOT.parents[1]
TEXT_SUFFIXES = {".md", ".json", ".jsonl", ".csv", ".py", ".ipynb", ".cff", ".txt", ".toml", ".yaml", ".yml", ""}

PATTERNS = {
    "absolute_user_path": r"(/Users/[A-Za-z0-9._-]+|/home/[a-z0-9._-]+|C:\\\\Users\\\\)",
    "private_tmp_path": r"/private/tmp/|/var/folders/",
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "private_ipv4": r"\b(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b",
    "internal_host": r"\.internal\b|\.local\b|\.corp\b",
    "anthropic_key": r"sk-ant-[A-Za-z0-9_-]{8,}",
    "openai_key": r"\bsk-[A-Za-z0-9]{20,}",
    "github_token": r"\b(ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{10,}",
    "aws_key": r"\bAKIA[0-9A-Z]{16}\b",
    "google_key": r"\bAIza[0-9A-Za-z_-]{30,}",
    "slack_token": r"\bxox[abposr]-[A-Za-z0-9-]{10,}",
    "private_key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "bearer_token": r"Bearer\s+[A-Za-z0-9._-]{20,}",
    "secret_assignment": r"(?i)\b(password|passwd|secret|api[_-]?key|token)\b\s*[=:]\s*[\"']?[A-Za-z0-9/+_.-]{12,}",
    "env_var_value": r"\bATHENA_[A-Z_]*(KEY|SECRET|PASSWORD|TOKEN)\s*=\s*\S+",
    "raw_model_output_field": r"\"raw\"\s*:",
    "first_person_plural_en": r"\b([Ww]e|[Oo]ur|[Oo]urs|us|[Ll]et's)\b",
    "first_person_plural_tr": r"(?i)\b(yaptık|ekledik|gördük|test ettik|karar verdik|denedik|ettik|ölçtük|kaydettik|yazdık|bizim|biz)\b",
}
#: SHA-256 of internal host, project and account tokens. Stored as hashes so the scanner itself does not
#: publish the names it looks for. Every token of the form [A-Za-z0-9._-]{4,} in every file is hashed and compared.
INTERNAL_TOKEN_SHA256 = frozenset({
    "0c07f1467ee0855cbf36a1742697eb17d8f82af5c19c8c7f1595a52096a50cef",
    "417498a88fd13b83b36aabf8370ee9a920f8144ee80194f307891b7b34c065c4",
    "49a433c0192b378bf836adab060aed86c3c4838d68a4c576daaed5f31d7d16fe",
    "8a07ab5c625865f1170373cf8a29caddcb37910bd741af7a875595466f1bb2d9",
    "d2ad8a6cb9b7b425a377bec8d58cc29e0765c721e1cde568757a7c2f51f25805",
    "f19ff641df2d3cba7aa84e7203b520d12a18c0de00e741765c39a30257e56c4d",
})
TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{3,}")

#: Pattern → files (prefix match) where the pattern applies; others are skipped for that pattern.
SCOPE = {
    "first_person_plural_en": ("writeups/council-ablation.en.md", "README.md", "METHODOLOGY.md", "LIMITATIONS.md",
                               "REPRODUCIBILITY.md", "DATA_AND_MODEL_LICENSES.md",
                               "EVIDENCE_MAP.md"),
    "first_person_plural_tr": ("writeups/council-ablation.tr.md",),
}
#: (pattern, file, literal match) → reason. Every allowed finding is reported, not hidden.
ALLOW = {
    ("internal_host", "tools/scan_publication.py"): "the scanner's own generic pattern list (no names)",
    ("absolute_user_path", "tools/scan_publication.py"): "the scanner's own pattern list",
    ("private_tmp_path", "tools/scan_publication.py"): "the scanner's own pattern list",
    ("raw_model_output_field", "tools/scan_publication.py"): "the scanner's own pattern list",
    ("secret_assignment", "tools/scan_publication.py"): "the scanner's own pattern list",
    ("env_var_value", "tools/scan_publication.py"): "the scanner's own pattern list",
    ("private_key", "tools/scan_publication.py"): "the scanner's own pattern list",
    ("bearer_token", "tools/scan_publication.py"): "the scanner's own pattern list",
    ("raw_model_output_field", "harness/run.py"): ("harness source that stores the completion when collecting; the "
                                                   "published evidence files carry no raw field"),
}


def files() -> list[Path]:
    out = []
    for p in sorted(ROOT.rglob("*")):
        rel = p.relative_to(ROOT).as_posix()
        if not p.is_file() or rel.startswith((".git/", ".venv/", ".ipynb_checkpoints")) or "/__pycache__/" in f"/{rel}":
            continue
        if rel == "evidence/publication_scan.json":
            continue  # the report of this scan
        if p.suffix in TEXT_SUFFIXES:
            out.append(p)
    return out


def main() -> int:
    findings, allowed = [], []
    for p in files():
        rel = p.relative_to(ROOT).as_posix()
        text = p.read_text(encoding="utf-8", errors="replace")
        for name, pat in PATTERNS.items():
            scope = SCOPE.get(name)
            if scope and not rel.startswith(scope):
                continue
            body = text
            if name.startswith("first_person_plural"):
                body = re.sub(r"`[^`]*`", "", text)  # identifiers in code spans are not prose
            for m in re.finditer(pat, body):
                line = body.count("\n", 0, m.start()) + 1
                item = {"pattern": name, "file": rel, "line": line, "match": m.group(0)[:80]}
                if (name, rel) in ALLOW:
                    allowed.append({**item, "match": "<pattern list>", "reason": ALLOW[(name, rel)]})
                else:
                    findings.append(item)
        for m in TOKEN.finditer(text):
            tok = m.group(0)
            for cand in {tok, tok.strip("._-"), tok.lower().strip("._-")}:
                if hashlib.sha256(cand.encode()).hexdigest() in INTERNAL_TOKEN_SHA256:
                    findings.append({"pattern": "internal_token_hash", "file": rel,
                                     "line": text.count("\n", 0, m.start()) + 1, "match": "<redacted>"})
                    break
    licence = {
        "LICENSE (Apache-2.0, repository root)": "Apache License" in (REPO / "LICENSE").read_text()
        and "Version 2.0" in (REPO / "LICENSE").read_text(),
        "LICENSE-CC-BY-4.0.md (repository root)": "Attribution 4.0 International" in (REPO / "LICENSE-CC-BY-4.0.md").read_text(),
        "DATA_AND_MODEL_LICENSES.md": (ROOT / "DATA_AND_MODEL_LICENSES.md").exists(),
        "CITATION.cff (repository root)": (REPO / "CITATION.cff").exists(),
        "no_dataset_rows_included": not any(p.suffix in {".parquet", ".xlsx", ".zip", ".gz"} for p in ROOT.rglob("*")),
    }
    blocking = bool(findings) or not all(licence.values())
    report = {"recorded_at": datetime.now(UTC).isoformat(timespec="seconds"), "files_scanned": len(files()),
              "patterns": sorted(PATTERNS), "result": "FAIL" if blocking else "PASS", "findings": findings,
              "allowed": allowed, "licence_checks": licence}
    (ROOT / "evidence" / "publication_scan.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps({k: report[k] for k in ("result", "files_scanned", "licence_checks")}, indent=1))
    for f in findings[:50]:
        print("FINDING", f)
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
