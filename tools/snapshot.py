"""Take a metrics snapshot of the repo and regenerate metrics/HISTORY.md.

Run after every reviewed change:  python tools/snapshot.py "label for this change"
Writes metrics/snapshots/<date>_<n>_<slug>.json. Engineering metrics now (size, tests, coverage,
lint, types, complexity, API surface); model and eval metrics are added as those phases land.
"""

from __future__ import annotations

import ast
import datetime as dt
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "pyscroll_lab"
TESTS = ROOT / "tests"
OUT = ROOT / "metrics"
BIN = Path(sys.executable).parent


def run(*cmd: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)


def code_lines(path: Path) -> int:
    lines = path.read_text(encoding="utf-8").splitlines()
    return sum(1 for ln in lines if ln.strip() and not ln.strip().startswith("#"))


def count_tests() -> int:
    n = 0
    for f in TESTS.rglob("test_*.py"):
        tree = ast.parse(f.read_text(encoding="utf-8"))
        n += sum(isinstance(x, ast.FunctionDef) and x.name.startswith("test_") for x in ast.walk(tree))
    return n


def pytest_metrics() -> dict[str, Any]:
    cov_json, junit = ROOT / ".coverage.json", ROOT / ".junit.xml"
    p = run(
        str(BIN / "pytest"), "-q", "-p", "no:cacheprovider", f"--junitxml={junit}",
        "--cov=pyscroll_lab", f"--cov-report=json:{cov_json}",
    )  # fmt: skip
    suite = ElementTree.parse(junit).getroot()
    suite = suite if suite.tag == "testsuite" else suite[0]
    total, failed = int(suite.get("tests", 0)), int(suite.get("failures", 0)) + int(suite.get("errors", 0))
    skipped = int(suite.get("skipped", 0))
    warn = re.search(r"(\d+) warnings? summary|=+ warnings summary", p.stdout)
    cov = round(json.loads(cov_json.read_text())["totals"]["percent_covered"], 1)
    cov_json.unlink()
    junit.unlink()
    return {
        "passed": total - failed - skipped,
        "failed": failed,
        "warnings": p.stdout.count("Warning:") if warn else 0,
        "seconds": round(float(suite.get("time", 0)), 2),
        "coverage_pct": cov,
    }


def ruff_issues() -> int:
    p = run(str(BIN / "ruff"), "check", ".", "--output-format", "json")
    return len(json.loads(p.stdout or "[]"))


def mypy_errors() -> int:
    m = re.search(r"Found (\d+) error", run(str(BIN / "mypy")).stdout)
    return int(m.group(1)) if m else 0


def complexity() -> dict[str, float]:
    data = json.loads(run(str(BIN / "radon"), "cc", "-j", str(SRC)).stdout or "{}")
    scores = [b["complexity"] for items in data.values() for b in items if isinstance(b, dict)]
    if not scores:
        return {"blocks": 0, "avg": 0.0, "max": 0}
    return {"blocks": len(scores), "avg": round(sum(scores) / len(scores), 2), "max": max(scores)}


def api_routes() -> list[str]:
    sys.path.insert(0, str(ROOT / "src"))
    from pyscroll_lab.api import app

    out = []
    for r in app.routes:
        if getattr(r, "include_in_schema", False):
            methods = ",".join(sorted(getattr(r, "methods", None) or []))
            out.append(f"{methods} {getattr(r, 'path', '')}")
    return sorted(out)


def main() -> None:
    label = " ".join(sys.argv[1:]) or "snapshot"
    sha = run("git", "rev-parse", "--short", "HEAD").stdout.strip() or "none"
    dirty = bool(run("git", "status", "--porcelain").stdout.strip())
    runtime_deps = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["dependencies"]
    snap = {
        "taken_at": dt.datetime.now().isoformat(timespec="seconds"),
        "label": label,
        "git": {"sha": sha, "dirty": dirty},
        "size": {
            "src_files": len(list(SRC.rglob("*.py"))),
            "src_loc": sum(code_lines(f) for f in SRC.rglob("*.py")),
            "test_loc": sum(code_lines(f) for f in TESTS.rglob("*.py")),
            "test_functions": count_tests(),
        },
        "tests": pytest_metrics(),
        "lint": {"ruff_issues": ruff_issues(), "mypy_errors": mypy_errors()},
        "complexity": complexity(),
        "api": {"routes": api_routes()},
        "deps": {"runtime": len(runtime_deps)},
    }
    snaps = OUT / "snapshots"
    snaps.mkdir(parents=True, exist_ok=True)
    n = len(list(snaps.glob("*.json"))) + 1
    slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")[:40]
    path = snaps / f"{dt.date.today()}_{n:03d}_{slug}.json"
    path.write_text(json.dumps(snap, indent=2) + "\n", encoding="utf-8")
    write_history(snaps)
    print(json.dumps(snap, indent=2))
    print(f"wrote {path.relative_to(ROOT)}")


COLUMNS = [
    "#", "date", "label", "sha", "src LOC", "test LOC", "tests", "pass/fail", "coverage %",
    "test s", "warnings", "ruff", "mypy", "avg cc", "max cc", "routes", "deps",
]  # fmt: skip


def row(i: int, s: dict[str, Any]) -> str:
    t, z, c = s["tests"], s["size"], s["complexity"]
    cells = [
        i, s["taken_at"][:10], s["label"], s["git"]["sha"] + ("*" if s["git"]["dirty"] else ""),
        z["src_loc"], z["test_loc"], z["test_functions"], f"{t['passed']}/{t['failed']}", t["coverage_pct"],
        t["seconds"], t["warnings"], s["lint"]["ruff_issues"], s["lint"]["mypy_errors"], c["avg"], c["max"],
        len(s["api"]["routes"]), s["deps"]["runtime"],
    ]  # fmt: skip
    return "| " + " | ".join(str(x) for x in cells) + " |"


def write_history(snaps: Path) -> None:
    snapshots = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(snaps.glob("*.json"))]
    lines = [
        "# Metrics history",
        "",
        "Generated by `tools/snapshot.py`, one row per reviewed change. Do not edit by hand.",
        "",
        "| " + " | ".join(COLUMNS) + " |",
        "|" + "---|" * len(COLUMNS),
        *(row(i, s) for i, s in enumerate(snapshots, 1)),
        "",
        "`*` after the sha: taken with uncommitted changes (the change under review).",
        "cc = cyclomatic complexity.",
    ]
    (OUT / "HISTORY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
