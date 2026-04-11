#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml", "rich"]
# ///
"""
Run WatchfulAnvil corpus tests: setup worktree → analyze each project → compare vs expected.yaml.

Usage:
    uv run scripts/run-corpus-tests.py [options]

Options:
    --no-worktree   Skip worktree teardown/recreate (reuse existing T:\\wa-worktrees)
    --filter ID     Only run test sets whose id contains ID (substring match)
    --verbose       Print raw uipcli output on failure
"""
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path, PureWindowsPath

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import yaml
from rich.console import Console
from rich.table import Table

# ── configuration ────────────────────────────────────────────────────────────
UIPCLI      = Path(r"C:\Users\cpm\AppData\Local\cpmf\tools\uipcli-25.10.11\uipcli.exe")
NUGET_FEED  = Path(r"C:\Users\Public\Documents\myNugetPackages")
WORKTREE    = Path(r"T:\wa-worktrees")
REPO_ROOT   = Path(__file__).parent.parent
CATALOG     = REPO_ROOT / "corpus-catalog.yaml"
ANALYZER_LEVEL = "Warning"   # catches Warning + Error severity violations
RULE_PACK_VERSION = "0.1.13-alpha"
RESULTS_DIR = WORKTREE / ".wa-results"
# ─────────────────────────────────────────────────────────────────────────────

console = Console(legacy_windows=False)


# ── worktree ──────────────────────────────────────────────────────────────────

def stamp_rule_pack(root: Path) -> None:
    """Inject/bump Cpmf.WorkflowAnalyzerRules into every project.json under root."""
    nuget_ver = f"[{RULE_PACK_VERSION}]"
    for path in sorted(root.glob("*/project.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        deps = data.setdefault("dependencies", {})
        if deps.get("Cpmf.WorkflowAnalyzerRules") != nuget_ver:
            deps["Cpmf.WorkflowAnalyzerRules"] = nuget_ver
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    console.print(f"  [green]OK[/green] rule pack stamped  ({RULE_PACK_VERSION})")


def setup_worktree() -> None:
    console.print(f"[bold]Setting up worktree at[/bold] {WORKTREE}")

    # Remove from git's worktree list
    subprocess.run(
        ["git", "worktree", "remove", str(WORKTREE), "--force"],
        capture_output=True, cwd=REPO_ROOT,
    )
    subprocess.run(["git", "worktree", "prune"], capture_output=True, cwd=REPO_ROOT)

    # Nuke the directory if it still exists
    if WORKTREE.exists():
        shutil.rmtree(WORKTREE)

    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True, cwd=REPO_ROOT
    ).strip()

    subprocess.run(
        ["git", "worktree", "add", "--detach", str(WORKTREE), commit],
        check=True, cwd=REPO_ROOT,
    )
    console.print(f"  [green]OK[/green] worktree ready  (detached @ {commit[:12]})")


# ── nuget config ─────────────────────────────────────────────────────────────

def write_nuget_config(path: Path) -> None:
    path.write_text(
        f"""<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <add key="local-cpmf" value="{NUGET_FEED}" />
  </packageSources>
</configuration>
""",
        encoding="utf-8",
    )


# ── uipcli analyze ────────────────────────────────────────────────────────────

def run_analyze(project_dir: Path, nuget_cfg: Path, result_json: Path) -> subprocess.CompletedProcess:
    cmd = [
        str(UIPCLI), "package", "analyze", str(project_dir),
        "--analyzerTraceLevel", ANALYZER_LEVEL,
        "--nugetConfigFilePath", str(nuget_cfg),
        "--disableBuiltInNugetFeeds",
        "--resultPath", str(result_json),
        "--traceLevel", "Warning",
    ]
    return subprocess.run(cmd, capture_output=True, text=True)


# ── result parsing ────────────────────────────────────────────────────────────

_SEVERITY_MAP = {1: "Error", 2: "Warning", 3: "Info", 4: "Verbose"}


def parse_violations(result_json: Path) -> list[dict]:
    """
    Parse the uipcli --resultPath JSON into a flat list of
    {"ruleId": str, "severity": str} dicts.
    """
    if not result_json.exists():
        return []

    raw = json.loads(result_json.read_text(encoding="utf-8"))
    items = raw if isinstance(raw, list) else raw.get("AnalyzerResults", raw.get("violations", []))

    violations = []
    for item in items:
        rule_id  = item.get("ErrorCode") or item.get("RuleId") or item.get("ruleId", "?")
        severity = item.get("ErrorSeverity") or item.get("Severity") or item.get("severity", "?")
        if isinstance(severity, int):
            severity = _SEVERITY_MAP.get(severity, str(severity))
        violations.append({"ruleId": rule_id, "severity": severity})

    return violations


# ── comparison ────────────────────────────────────────────────────────────────

def compare(expected: list[dict], actual: list[dict]) -> tuple[list, list]:
    def key(v):
        return (v["ruleId"], v.get("severity", ""))

    exp_set = {key(v) for v in expected}
    act_set = {key(v) for v in actual}

    missing    = sorted(exp_set - act_set)   # expected but not found
    unexpected = sorted(act_set - exp_set)   # found but not expected
    return missing, unexpected


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-worktree", action="store_true")
    parser.add_argument("--filter", default="")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if not UIPCLI.exists():
        console.print(f"[red]uipcli not found:[/red] {UIPCLI}")
        sys.exit(1)

    if not args.no_worktree:
        setup_worktree()
    stamp_rule_pack(WORKTREE)

    catalog = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    default_governance_rel = catalog.get("defaultGovernance", "")

    results = []

    run_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = RESULTS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    nuget_cfg = run_dir / "nuget.config"
    write_nuget_config(nuget_cfg)
    console.print(f"  results -> {run_dir}")

    for ts in catalog.get("testSets", []):
        if not ts.get("enabled", False):
            continue
        if args.filter and args.filter not in ts["id"]:
            continue

        ts_id   = ts["id"]
        corpus  = ts["corpus"].lstrip("./")
        project_dir = WORKTREE / corpus
        expected_yaml = project_dir / "expected.yaml"

        if not project_dir.exists():
            results.append((ts_id, "SKIP", "project dir missing in worktree", [], []))
            continue

        if not expected_yaml.exists():
            results.append((ts_id, "SKIP", "expected.yaml missing", [], []))
            continue

        expected_violations = (
            yaml.safe_load(expected_yaml.read_text(encoding="utf-8"))
            .get("expectedViolations", []) or []
        )

        result_json = run_dir / f"{ts_id}.json"
        proc = run_analyze(project_dir, nuget_cfg, result_json)

        if args.verbose or proc.returncode not in (0, 1):
            console.print(f"\n[dim]--- {ts_id} stdout ---[/dim]")
            console.print(proc.stdout[-3000:] if proc.stdout else "(empty)")
            if proc.stderr:
                console.print(f"[dim]--- stderr ---[/dim]\n{proc.stderr[-1000:]}")

        actual_violations = parse_violations(result_json)
        missing, unexpected = compare(expected_violations, actual_violations)

        if not missing and not unexpected:
            results.append((ts_id, "PASS", "", missing, unexpected))
        else:
            detail = []
            if missing:    detail.append(f"missing: {missing}")
            if unexpected: detail.append(f"unexpected: {unexpected}")
            results.append((ts_id, "FAIL", "; ".join(detail), missing, unexpected))

    # ── summary table ─────────────────────────────────────────────────────────
    table = Table(title="Corpus Test Results", show_lines=False)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Result", no_wrap=True)
    table.add_column("Detail")

    passed = failed = skipped = 0
    for ts_id, status, detail, *_ in results:
        color = {"PASS": "green", "FAIL": "red", "SKIP": "yellow"}.get(status, "white")
        table.add_row(ts_id, f"[{color}]{status}[/{color}]", detail)
        if status == "PASS":   passed  += 1
        elif status == "FAIL": failed  += 1
        else:                  skipped += 1

    console.print()
    console.print(table)
    console.print(f"\n  passed={passed}  failed={failed}  skipped={skipped}\n")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
