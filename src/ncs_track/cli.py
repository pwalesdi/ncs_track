"""Command line: python -m ncs_track <command>."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from . import athleticnet, manifest, paths, programs, schools, season_rules, validate
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


def cmd_rules_seasons(args) -> int:
    for p in season_rules.write_all():
        load_rules(p)
        print(f"wrote {p.relative_to(paths.ROOT)}")
    return 0


def cmd_ingest(args) -> int:
    files = [Path(f) for f in args.files] or sorted(paths.RAW_ATHLETICNET.glob("*.csv"))
    if not files:
        print("no Athletic.net files found in data/raw/athleticnet/")
        return 1
    meets = athleticnet.load_meets()
    perfs, legs, issues = [], [], []
    for f in files:
        season, _, _ = athleticnet.parse_filename(f)
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


def cmd_moc_entries(args) -> int:
    files = programs.program_files(paths.ENTRIES)
    if not files:
        print("no MOC programs in data/reference/entries/")
        return 1
    rules, _ = load_rules_for(2026)
    canonical = set(pd.read_csv(paths.AREA_LISTS, dtype=str)["School"])
    entries, unparsed = programs.build_moc_entries(files, paths.ROOT, canonical)
    counts, issues = programs.validate_entries(entries, unparsed, rules["events"]["main_simulation"])
    paths.PROCESSED.mkdir(parents=True, exist_ok=True)
    paths.REVIEW.mkdir(parents=True, exist_ok=True)
    entries.to_csv(paths.PROCESSED / "moc_entries.csv", index=False)
    counts.to_csv(paths.REVIEW / "moc_entry_counts.csv", index=False)
    issues.to_csv(paths.REVIEW / "moc_entries_issues.csv", index=False)
    print(f"{len(entries)} entry rows from {len(files)} programs -> data/processed/moc_entries.csv")
    print(issues["kind"].value_counts().to_string() if len(issues) else "no issues")
    return 0


def cmd_school_aliases(args) -> int:
    entries_path = paths.PROCESSED / "moc_entries.csv"
    moc = pd.read_csv(entries_path) if entries_path.exists() else None
    if moc is None:
        print("note: data/processed/moc_entries.csv missing; run moc-entries first to include programs")
    hytek = sorted(paths.RAW_HYTEK.glob("*.htm"))
    meets = pd.read_csv(paths.MEETS, dtype=str)
    aliases, matched, review = schools.build(paths.ROOT, paths.AREA_LISTS, hytek, moc, meets)
    paths.REVIEW.mkdir(parents=True, exist_ok=True)
    aliases.to_csv(paths.SCHOOL_ALIASES, index=False)
    matched.to_csv(paths.SCHOOL_SPELLINGS, index=False)
    review.to_csv(paths.REVIEW / "school_aliases_review.csv", index=False)
    print(f"{len(aliases)} canonical schools, {len(matched)} spellings matched, "
          f"{len(review)} to review (data/review/school_aliases_review.csv)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ncs_track")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("manifest", help="build or check data/raw/MANIFEST.csv")
    m.add_argument("--check", action="store_true")
    m.set_defaults(func=cmd_manifest)
    r = sub.add_parser("rules-check", help="load and check every rules YAML")
    r.set_defaults(func=cmd_rules_check)
    rs = sub.add_parser("rules-seasons", help="generate rules YAML for 2019, 2022-2025 from 2026 + printed standards")
    rs.set_defaults(func=cmd_rules_seasons)
    i = sub.add_parser("ingest-athleticnet", help="normalise Athletic.net CSVs")
    i.add_argument("files", nargs="*")
    i.set_defaults(func=cmd_ingest)
    e = sub.add_parser("moc-entries", help="parse MOC programs into data/processed/moc_entries.csv")
    e.set_defaults(func=cmd_moc_entries)
    a = sub.add_parser("school-aliases", help="build data/reference/school_aliases.csv + review queue")
    a.set_defaults(func=cmd_school_aliases)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
