#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml"]
# ///
"""
Sync the project.json "name" field for every corpus project from corpus-catalog.yaml.

For each enabled test set the catalog's `name` value (e.g. "c26v001_CORE_00000001")
is written into the corresponding project.json "name" field.

Usage:
    uv run scripts/sync-project-names.py [--dry-run]
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
CATALOG   = REPO_ROOT / "corpus-catalog.yaml"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    args = parser.parse_args()

    catalog = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    changed = skipped = 0

    for ts in catalog.get("testSets", []):
        corpus_name = ts.get("name")
        corpus_rel  = ts.get("corpus", "").lstrip("./")
        if not corpus_name or not corpus_rel:
            continue

        project_json = REPO_ROOT / corpus_rel / "project.json"
        if not project_json.exists():
            print(f"  missing  {corpus_rel}/project.json")
            continue

        data = json.loads(project_json.read_text(encoding="utf-8"))
        current = data.get("name", "")

        if current == corpus_name:
            skipped += 1
            continue

        print(f"  {'would update' if args.dry_run else 'update '} {corpus_rel}  \"{current}\" -> \"{corpus_name}\"")
        if not args.dry_run:
            data["name"] = corpus_name
            project_json.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        changed += 1

    print(f"\n  changed={changed}  skipped={skipped}")
    if args.dry_run and changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
