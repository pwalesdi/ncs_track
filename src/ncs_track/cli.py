"""Command line: python -m ncs_track <command>."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from . import athleticnet, manifest, paths, validate
from .issues import errors, to_frame
from .rules import load_rules, load_rules_for


def cmd_manifest(args) -> int:
    if args.check:
        problems = manifest.check()
        for p in problems:
            print(p)
        print("manifest OK" if not problems else f"{len(problems)} problem(s)")
        return 1 if problems else 0
    df = manifest.build()
    print(f"wrote {paths.MANIFEST.relative_to(paths.ROOT)} ({len(df)} files)")
    return 0


def cmd_rules_check(args) -> int:
    for p in sorted(paths.RULES.glob("*.yaml")):
        load_rules(p)
        print(f"{p.relative_to(paths.ROOT)}: OK")
    return 0


def cmd_ingest(args) -> int:
    files = [Path(f) for f in args.files] or sorted(paths.RAW_ATHLETICNET.glob("athleticnet_*.csv"))
    if not files:
        print("no Athletic.net files found in data/raw/athleticnet/")
        return 1
    meets = athleticnet.load_meets()
    perfs, legs, issues = [], [], []
    for f in files:
        season, _ = athleticnet.parse_filename(f)
        rules, label = load_rules_for(season)
        p, l, i = athleticnet.ingest_file(f, meets, rules)
        i += validate.run_all(p, l, rules)
        perfs.append(p); legs.append(l); issues += i
        print(f"{f.name}: {len(p)} rows, {len(errors(i))} errors ({label})")
    paths.PROCESSED.mkdir(parents=True, exist_ok=True)
    paths.REVIEW.mkdir(parents=True, exist_ok=True)
    perf = pd.concat(perfs, ignore_index=True)
    perf.to_csv(paths.PROCESSED / "performances.csv", index=False)
    pd.concat(legs, ignore_index=True).to_csv(paths.PROCESSED / "relay_legs.csv", index=False)
    to_frame(issues).to_csv(paths.REVIEW / "validation_issues.csv", index=False)
    validate.review_queue(perf).to_csv(paths.REVIEW / "athlete_id_review.csv", index=False)
    n_err = len(errors(issues))
    print(f"{n_err} errors total; see data/review/validation_issues.csv")
    return 1 if n_err else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ncs_track")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("manifest", help="build or check data/raw/MANIFEST.csv")
    m.add_argument("--check", action="store_true")
    m.set_defaults(func=cmd_manifest)
    r = sub.add_parser("rules-check", help="load and check every rules YAML")
    r.set_defaults(func=cmd_rules_check)
    i = sub.add_parser("ingest-athleticnet", help="normalise Athletic.net CSVs")
    i.add_argument("files", nargs="*")
    i.set_defaults(func=cmd_ingest)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
