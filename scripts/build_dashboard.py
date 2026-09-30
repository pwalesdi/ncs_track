"""Build dashboard/index.html from dashboard/template.html and data/summary/ only.

    .venv/bin/python scripts/build_dashboard.py

The summary tables are embedded as JSON and Chart.js is inlined from the pinned copy in
dashboard/vendor/ (checksum-verified), so index.html is one self-contained file that works
offline. No athlete names: only data/summary/ is read.
"""

import hashlib
import json
from datetime import date

import pandas as pd

from ncs_track import paths

S = paths.SUMMARY
DASH = paths.ROOT / "dashboard"
CHARTJS_VERSION = "4.4.1"
CHARTJS = DASH / "vendor" / f"chart-{CHARTJS_VERSION}.umd.min.js"
CHARTJS_SHA256 = "81ffafe13c37e1b25793b020d446f4d9739b949dadb7f9f79d709a0cad781c2f"   # cdnjs 4.4.1 chart.umd.min.js
EVENT_ORDER = ["100", "200", "400", "800", "1600", "3200", "100H", "110H", "300H", "4x100", "4x400",
               "HJ", "PV", "LJ", "TJ", "SP", "DT"]

# From docs/analysis_tables.md (Terms), shortened for the footer.
DEFINITIONS = [
    ("Automatic", "Qualified by place at the Area meet: top 6 (Class A: top 3)."),
    ("Next best mark", "One of the 3 fill spots per event: the next best marks from all four Area meets."),
    ("At-large standard", "Met the posted at-large standard in the Area final, outside the automatic places."),
    ("At-large (combined)", "Next best mark + at-large standard."),
    ("Replacement", "In the MOC program though not predicted, filling a vacancy (next finalist in line, same Area)."),
    ("Unexplained", "In the program, not predicted, no explanation (includes schools that could not be matched)."),
    ("Everyone who qualified", "Who the current rules say earned a spot: a replay of each season's rules against the "
                               "Area results (matches 98–99% of real entries once athlete choices and replacements are counted)."),
    ("Who actually declared", "Everyone in the MOC program."),
    ("Competed", "Has a row in the MOC results with any status other than DNS or scratch (DNF, DQ, no height, fouls count)."),
    ("Top finish", "MOC final place 8th or better (9th or better in LJ, TJ, SP and DT). The 800/1600 finals seat 12 but "
                   "top 8 is used; the 3200, HJ and PV have no prelims."),
    ("Empty lane", "A spot that went to nobody: earned but not used and not refilled. Includes no-shows, which cannot be refilled."),
    ("No-show", "Declared but did not compete."),
    ("Utilization", "Spots used by the Area's own qualifiers ÷ spots earned."),
    ("Left out", "The 3 best non-qualifiers per Area and event, by Area mark, compared with the 8th-best valid MOC "
                 "mark (9th for LJ/TJ/SP/DT) across all MOC rounds, one mark per athlete. Marks from different meets: "
                 "a comparison, not a prediction."),
    ("Panel 4 columns", "Used = utilization (competed ÷ spots earned); Empty = empty lanes ÷ spots earned; "
                        "No-shows = of declared; Not decl. = qualified but not in the program; Refilled = vacancies refilled."),
    ("All seasons", "Counts summed over 2022–2026 (pooled); rates recomputed from the sums."),
    ("Lowest automatic", "An Area's automatic qualifiers who placed 5th–6th at the Area meet (3rd for Class A)."),
    ("Median MOC place", "Finalists keep their final place; everyone else with a valid MOC mark is ranked after the "
                         "finalists by their best mark. Lower is better."),
    ("Source", "Athletic.net Area and MOC results, MOC programs (Diablo Timing); rules per season. "
               "Pre-2026 allocations assumed from 2026; 2023 standards assumed from 2026. State results pending."),
]


CAVEATS = [
    "Small samples: many cells hold a handful of athletes (at-large qualifiers outside Tri-Valley, Class A, any "
    "single event). A few athletes can move a rate by 10–30 points.",
    "Different meets: Area and MOC marks come from different days, wind, weather and competition.",
    "Rules before 2026 are partly assumed: allocations for 2022–2025 assumed from 2026; 2023 at-large standards "
    "assumed from 2026 (none printed).",
    "Unresolved school names (e.g. 'West County', 2022) appear as Unknown and are not compared.",
    "State results are pending; state qualification is not shown.",
    "The core-comparison tests (docs/findings_v1.md §4) support a consistent direction pooled over five seasons, "
    "not a precise gap, and say nothing about causes.",
]


def records(df: pd.DataFrame, cols: list[str]) -> list[dict]:
    return json.loads(df[cols].to_json(orient="records"))


def build() -> dict:
    fm = pd.read_csv(S / "field_makeup.csv")
    fm = fm[~fm["rollup"]]
    al = pd.read_csv(S / "at_large_share.csv")
    al = al[al["count"] > 0]
    mp = pd.read_csv(S / "moc_performance.csv")
    mp = mp[~mp["rollup"]]
    su = pd.read_csv(S / "spot_utilization.csv")
    lo = pd.read_csv(S / "left_out.csv")
    lo = lo.assign(has_cutoff=lo["moc_cutoff_mark"].notna(),
                   hit=lo["area_mark_would_have_been_top_finish"].fillna(False).astype(bool))
    seasons = sorted(int(s) for s in su["season"].unique())
    events = [e for e in EVENT_ORDER if e in set(su["event_code"].astype(str))]
    return {
        "seasons": seasons, "events": events, "definitions": DEFINITIONS,
        "field_makeup": records(fm, ["season", "gender", "event_code", "field", "area", "qualifier_type", "count"]),
        "at_large_share": records(al, ["season", "gender", "event_code", "field", "spot_type", "area", "count"]),
        "moc_performance": records(mp, ["season", "gender", "event_code", "area", "qualifier_type", "competed",
                                        "top_finish", "scored"]),
        "spot_utilization": records(su, ["season", "gender", "event_code", "area", "spots_earned", "declared",
                                         "competed", "no_show", "not_declared", "vacancies_refilled", "empty_lanes"]),
        "left_out": records(lo, ["season", "gender", "event_code", "area", "has_cutoff", "hit"]),
        "core_place_counts": records(pd.read_csv(S / "core_place_counts.csv", dtype={"moc_overall_place": "Int64"}),
                                     ["season", "gender", "event_code", "area", "route", "moc_overall_place",
                                      "top_finish", "count"]),
        "caveats": CAVEATS,
        "flags_empty_lanes": records(pd.read_csv(S / "spot_utilization_flags_empty_lanes.csv"),
                                     ["area", "gender", "event_code", "seasons_flagged", "seasons", "total_all_seasons"]),
        "flags_unused": records(pd.read_csv(S / "spot_utilization_flags.csv"),
                                ["area", "gender", "event_code", "seasons_flagged", "seasons", "total_all_seasons"]),
    }


def main() -> None:
    data = build()
    html = (DASH / "template.html").read_text()
    payload = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    lib = CHARTJS.read_bytes()
    if hashlib.sha256(lib).hexdigest() != CHARTJS_SHA256:
        raise SystemExit(f"{CHARTJS} does not match the pinned checksum")
    html = (html.replace("__CHARTJS__", lib.decode().replace("</script", "<\\/script"))
            .replace("__CHARTJS_VERSION__", CHARTJS_VERSION)
            .replace("__DATA__", payload).replace("__BUILT__", date.today().isoformat()))
    (DASH / "index.html").write_text(html)
    print(f"wrote dashboard/index.html ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
