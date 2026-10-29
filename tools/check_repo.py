"""Public-release audit. Run before every push; exits 1 on any finding.

    python tools/check_repo.py            # prints a summary, writes nothing
    python tools/check_repo.py --json

Checks every file tracked or about to be tracked (everything except .git and git-ignored paths):
1. credentials and keys;
2. personal identifiers, e-mail addresses, home-directory and temporary paths;
3. private infrastructure and Athena product code;
4. forbidden file types, files over 10 MB, total size;
5. links: every relative Markdown link and every repository path written in backticks must exist (checked on the
   rendered docs, not on `templates/`, whose links are relative to where they are rendered).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OWNER_URL = re.compile(r"https://github\.com/ercanholasoglu/athena-research\b[^\s)\"'`>]*")

SECRET = {
    "openai_key": r"(?<![A-Za-z0-9])sk-(?:proj-)?[A-Za-z0-9_\-]{20,}",
    "anthropic_key": r"(?<![A-Za-z0-9])sk-ant-[A-Za-z0-9_\-]{20,}",
    "github_token": r"\bgh[opsu]_[A-Za-z0-9]{20,}",
    "aws_key": r"\bAKIA[0-9A-Z]{16}\b",
    "private_key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "bearer": r"(?i)\bbearer\s+[a-z0-9._\-]{20,}",
    "jwt": r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}",
    "assigned_secret": r"(?i)\b(api[_-]?key|secret|password|passwd|token)\b\s*[=:]\s*['\"][^'\"\s]{8,}['\"]",
    "env_secret_names": r"\b(JWT_SECRET|PREFS_SECRET|BOOTSTRAP_TOKEN|DATABASE_URL|GOOGLE_APPLICATION_CREDENTIALS)\b",
}
PERSONAL = {
    "home_path": r"/Users/[A-Za-z0-9_.\-]+|/home/[A-Za-z0-9_.\-]+/",
    "username": r"ercanholasoglu",
    "email": r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}",
    "temp_path": r"/private/tmp|/var/folders/|claude-50[0-9]|scratchpad/",
}
PRIVATE = {
    "infra": r"athena-vm|us-central1|gcloud\b|/etc/athena|docker-compose\.gcp|tunnel-through-iap|c713bfb2",
    "ipv4": r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b",
    "athena_code": r"\bfrom athena\b|\bimport athena\b|src/athena/|frontend/src/",
    "private_repo": r"github\.com[:/]ercanholasoglu/athena(?:\.git)?\b(?!-research|-docs)",
}
# Reviewed exceptions: (pattern name, path glob, required substring of the match context, reason).
ALLOW: list[tuple[str, str, str, str]] = [
    # filled only after each hit has been reviewed by hand
]
FORBIDDEN_FILES = re.compile(r"(^|/)(\.env(\..*)?|.*\.pem|.*\.key|id_rsa.*|.*\.gguf|.*\.safetensors|.*\.bin|catboost_info|node_modules|\.venv)(/|$)")
MAX_FILE = 10_000_000
LINK = re.compile(r"\]\(([^)\s]+)\)")
PATHREF = re.compile(r"`((?:harness|research|docs|tools|data)/[A-Za-z0-9_./\-{},*]+)`")


def files() -> list[Path]:
    try:
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=REPO,
                             capture_output=True, text=True, check=True).stdout.split("\n")
        return [REPO / p for p in out if p and (REPO / p).is_file()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return [p for p in REPO.rglob("*") if p.is_file() and ".git" not in p.parts]


def allowed(name: str, rel: str) -> bool:
    from fnmatch import fnmatch
    return any(n == name and fnmatch(rel, g) for n, g, _, _ in ALLOW)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    findings: list[dict] = []
    total = 0
    fs = files()
    for p in fs:
        rel = str(p.relative_to(REPO))
        size = p.stat().st_size
        total += size
        if FORBIDDEN_FILES.search(rel):
            findings.append({"check": "forbidden_file", "file": rel})
        if size > MAX_FILE:
            findings.append({"check": "large_file", "file": rel, "bytes": size})
        if p.suffix in (".png", ".svg", ".pdf", ".xls", ".zip") or rel == "tools/check_repo.py":
            continue
        text = p.read_text(errors="ignore")
        scrubbed = OWNER_URL.sub("<repo-url>", text)
        for group, pats in (("secret", SECRET), ("personal", PERSONAL), ("private", PRIVATE)):
            for name, pat in pats.items():
                for m in re.finditer(pat, scrubbed):
                    if allowed(name, rel):
                        break
                    findings.append({"check": f"{group}.{name}", "file": rel,
                                     "context": scrubbed[max(0, m.start() - 40): m.end() + 20].replace("\n", " ")})
                    break
        if p.suffix == ".md" and not rel.startswith("templates/"):  # templates link from their rendered location
            for m in LINK.finditer(text):
                t = m.group(1).split("#")[0]
                if not t or re.match(r"^(https?:|mailto:)", t):
                    continue
                if not (p.parent / t).resolve().exists():
                    findings.append({"check": "link.broken", "file": rel, "target": t})
            for m in (PATHREF.finditer(text) if not rel.startswith("harness/") else ()):  # harness docs use package paths
                t = m.group(1).rstrip(".,")
                if any(ch in t for ch in "{}*"):
                    continue
                if not (REPO / t).exists():
                    findings.append({"check": "path.missing", "file": rel, "target": t})
    summary = {"files": len(fs), "bytes": total, "findings": len(findings)}
    if a.json:
        print(json.dumps({"summary": summary, "findings": findings}, indent=1))
    else:
        for f in findings[:200]:
            print("FINDING", json.dumps(f)[:300])
        print(f"{summary['files']} files, {total / 1e6:.1f} MB, {len(findings)} findings")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
