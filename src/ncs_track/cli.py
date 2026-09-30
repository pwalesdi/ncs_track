"""Command line: python -m ncs_track <command>."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, replace
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
    perf_path = paths.PROCESSED / "performances.csv"
    perf = pd.read_csv(perf_path, dtype={"school_id": str}, low_memory=False) if perf_path.exists() else None
    if perf is None:
        print("note: data/processed/performances.csv missing; run ingest-athleticnet first for IDs and areas")
    aliases, matched, review, diff = schools.build(paths.ROOT, paths.AREA_LISTS, hytek, moc, meets, perf)
    paths.REVIEW.mkdir(parents=True, exist_ok=True)
    aliases.to_csv(paths.SCHOOL_ALIASES, index=False)
    matched.to_csv(paths.SCHOOL_SPELLINGS, index=False)
    review.to_csv(paths.REVIEW / "school_aliases_review.csv", index=False)
    diff.to_csv(paths.REVIEW / "school_area_2026_vs_list.csv", index=False)
    n_id = (aliases["athleticnet_school_id"] != "").sum()
    print(f"{len(aliases)} canonical schools ({(~aliases['in_source_list']).sum()} not on the list), "
          f"{n_id} with an Athletic.net ID, {len(matched)} spellings matched, {len(review)} to review; "
          f"{len(diff)} schools' 2026 participation area differs from the list")
    return 0


def replay_inputs(season: int):
    """(results, entries, rules, label, compare kwargs, legs) for one season."""
    perf = pd.read_csv(paths.PROCESSED / "performances.csv", dtype={"school_id": str, "athlete_id": str},
                       low_memory=False)
    results = perf[(perf["season"] == season) & (perf["level"] == "area")]
    entries = pd.read_csv(paths.PROCESSED / "moc_entries.csv")
    entries = entries[entries["season"] == season]
    legs = pd.read_csv(paths.PROCESSED / "relay_legs.csv", dtype=str)
    rules, label = load_rules_for(season)
    spell = pd.read_csv(paths.SCHOOL_SPELLINGS, dtype=str, keep_default_na=False)
    aliases = pd.read_csv(paths.SCHOOL_ALIASES, dtype=str, keep_default_na=False)
    key_of = dict(zip(spell["raw"], spell["school_key"]))
    area_of = dict(zip(aliases["school_key"], aliases[f"area_{season}"].replace("", None)))
    kw = dict(school_key=key_of.get, school_area=lambda raw: area_of.get(key_of.get(raw)))
    return results, entries, rules, label, kw, legs


def cmd_replay(args) -> int:
    from . import replay
    out_all = []
    for season in args.season:
        results, entries, rules, label, kw, legs = replay_inputs(season)
        if args.reading:
            base = replay.Interpretation(**json.loads(args.reading))
            grid = [replace(base, replacement=r, entry_limit=l, name=f"given;replacement={r};entry_limit={l}")
                    for r in replay.OVERLAY_AXES["replacement"] for l in replay.OVERLAY_AXES["entry_limit"]]
            grid = [replace(grid[0], replacement="off", entry_limit=0, name="given;replacement=off;entry_limit=0")] + grid[1:]
        else:
            grid = replay.interpretation_grid(**replay.FULL_GRID)
        table = replay.sweep(results, rules, entries, grid, legs=legs, **kw)
        rule, over = replay.best_reading(table, grid)
        ev = replay.evaluate(results, rules, rule)
        comp_raw = replay.compare(ev, entries, rules, interp=rule, legs=legs, **kw)
        comp = replay.compare(ev, entries, rules, interp=over, legs=legs, **kw)
        out = paths.OUTPUTS / f"replay_{season}"
        out.mkdir(parents=True, exist_ok=True)
        table.drop(columns="predicted_set").to_csv(out / "sweep.csv", index=False)
        ev.to_csv(out / "evaluated.csv", index=False)
        comp.rows.to_csv(out / "best_rows.csv", index=False)
        replay.rates(comp.rows, "area").to_csv(out / "rates_by_area.csv")
        replay.rates(comp.rows, ["gender", "event_code"]).to_csv(out / "rates_by_event.csv")
        if not args.reading:
            eff = pd.concat([
                replay.switch_effects(table[(table["replacement"] == "off") & (table["entry_limit"] == 0)],
                                      replay.RULE_AXES, "raw_mismatches"),
                replay.switch_effects(table, replay.OVERLAY_AXES, "rules_mismatches", replay.FULL_GRID)])
            eff.to_csv(out / "switch_effects.csv", index=False)
        (out / "best_reading.json").write_text(json.dumps({"rule": asdict(rule), "overlay": asdict(over)}, indent=1))
        sc = {"rules only": replay.score(comp_raw), "with overlays": replay.score(comp)}
        print(f"{season} ({label}); {len(grid)} readings\n  rule reading: {rule.name}\n  overlays: "
              f"replacement={over.replacement}, entry_limit={over.entry_limit}")
        print(pd.DataFrame(sc).loc[["matched", "raw_mismatches", "raw_match_rate", "rules_mismatches",
                                     "rules_match_rate", "explained_by_choice", "explained_by_entry_limit",
                                     "explained_by_replacement", "not_comparable_area_unknown"]].to_string())
        for n in comp.notes:
            print("note:", n)
        out_all.append({"season": season, **replay.score(comp)})
    pd.DataFrame(out_all).to_csv(paths.OUTPUTS / "replay_seasons.csv", index=False)
    return 0


def cmd_analysis(args) -> int:
    from . import analysis, replay
    perf = pd.read_csv(paths.PROCESSED / "performances.csv", dtype={"school_id": str, "athlete_id": str},
                       low_memory=False)
    qs, los = [], []
    for season in args.season:
        results, entries, rules, label, kw, legs = replay_inputs(season)
        q, lo, comp = analysis.build_season(season, results, entries, rules, kw, legs, perf)
        qs.append(q)
        los.append(lo)
        s = replay.score(comp)
        print(f"{season}: {len(q)} athlete-event rows; RULES match {s['rules_match_rate']:.3f}, RAW {s['raw_match_rate']:.3f}")
    q = pd.concat(qs, ignore_index=True)
    paths.OUTPUTS.mkdir(parents=True, exist_ok=True)
    q.to_csv(paths.OUTPUTS / "qualifiers.csv", index=False)
    out = paths.SUMMARY
    out.mkdir(parents=True, exist_ok=True)
    analysis.field_makeup(q).to_csv(out / "field_makeup.csv", index=False)
    analysis.at_large_share(q).to_csv(out / "at_large_share.csv", index=False)
    analysis.moc_performance(q).to_csv(out / "moc_performance.csv", index=False)
    su = analysis.spot_utilization(q)
    su.to_csv(out / "spot_utilization.csv", index=False)
    analysis.spot_utilization_by_area(su).to_csv(out / "spot_utilization_by_area.csv", index=False)
    analysis.spot_utilization_flags(su).to_csv(out / "spot_utilization_flags_unused.csv", index=False)
    analysis.spot_utilization_flags(su, metric="unfilled_spots").to_csv(
        out / "spot_utilization_flags_unfilled.csv", index=False)
    analysis.no_shows_unfilled(su).to_csv(out / "no_shows_unfilled_by_area.csv", index=False)
    analysis.core_comparison(q).to_csv(out / "core_comparison.csv", index=False)
    analysis.core_tests(q).to_csv(out / "core_tests.csv", index=False)
    analysis.core_place_curve(q).to_csv(out / "core_place_curve.csv", index=False)
    pd.concat(los, ignore_index=True).to_csv(out / "left_out.csv", index=False)
    print(f"wrote outputs/qualifiers.csv (git-ignored) and {out.relative_to(paths.ROOT)}/*.csv")
    return 0


def cmd_allocate(args) -> int:
    from . import allocate, replay
    cfg = allocate.load_config(Path(args.config))
    paths.OUTPUTS.mkdir(parents=True, exist_ok=True)
    for season in args.season:
        results, entries, rules, label, kw, legs = replay_inputs(season)
        got = allocate.allocate(results, rules, cfg)
        got.to_csv(paths.OUTPUTS / f"allocation_{cfg.name}_{season}.csv", index=False)
        by = got[got["qualified_by"].notna()].groupby(["meet_area", "qualified_by"]).size().unstack(fill_value=0)
        print(f"{season} ({label}), config {cfg.name}: {int(got['qualified_by'].notna().sum())} allocated")
        print(by.to_string())
        if args.compare:
            s = replay.score(allocate.compare(got, entries, rules, cfg, legs=legs, **kw))
            print(f"  vs MOC program: RAW {s['raw_match_rate']:.3f}, RULES {s['rules_match_rate']:.3f}")
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
    rp = sub.add_parser("replay", help="replay Area -> MOC qualification and sweep rule readings")
    rp.add_argument("--season", type=int, nargs="+", required=True)
    rp.add_argument("--reading", help="JSON of rule switches to use instead of sweeping them")
    rp.set_defaults(func=cmd_replay)
    an = sub.add_parser("analysis", help="build outputs/qualifiers.csv and data/summary/ tables")
    an.add_argument("--season", type=int, nargs="+", required=True)
    an.set_defaults(func=cmd_analysis)
    al = sub.add_parser("allocate", help="run the allocation engine with a config (configs/allocation/*.yaml)")
    al.add_argument("--config", required=True)
    al.add_argument("--season", type=int, nargs="+", required=True)
    al.add_argument("--compare", action="store_true", help="also score against the real MOC program")
    al.set_defaults(func=cmd_allocate)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
