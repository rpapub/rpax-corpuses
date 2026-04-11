#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""
Add or bump the Cpmf.WorkflowAnalyzerRules dependency in every corpus project.json.

Usage:
    uv run scripts/update-rule-pack.py [version]

    version  NuGet version string without brackets (default: 0.1.13-alpha)
"""
import json
import sys
from pathlib import Path

RULE_PACK = "Cpmf.WorkflowAnalyzerRules"
DEFAULT_VERSION = "0.1.13-alpha"


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_VERSION
    nuget_ver = f"[{version}]"

    repo_root = Path(__file__).parent.parent
    projects = sorted(repo_root.glob("*/project.json"))

    if not projects:
        print("No project.json files found.")
        return

    for path in projects:
        data = json.loads(path.read_text(encoding="utf-8"))
        deps = data.setdefault("dependencies", {})
        old = deps.get(RULE_PACK, "(absent)")
        if old == nuget_ver:
            print(f"  skip   {path.parent.name}  already {nuget_ver}")
            continue
        deps[RULE_PACK] = nuget_ver
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  update {path.parent.name}  {old} -> {nuget_ver}")


if __name__ == "__main__":
    main()
