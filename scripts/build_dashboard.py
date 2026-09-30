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
from ncs_track.analysis import SPOT_USE

S = paths.SUMMARY
DASH = paths.ROOT / "dashboard"
CHARTJS_VERSION = "4.4.1"
CHARTJS = DASH / "vendor" / f"chart-{CHARTJS_VERSION}.umd.min.js"
CHARTJS_SHA256 = "81ffafe13c37e1b25793b020d446f4d9739b949dadb7f9f79d709a0cad781c2f"   # cdnjs 4.4.1 chart.umd.min.js
EVENT_ORDER = ["100", "200", "400", "800", "1600", "3200", "100H", "110H", "300H", "4x100", "4x400",
               "HJ", "PV", "LJ", "TJ", "SP", "DT"]

# From docs/analysis_tables.md, in the dashboard's plain language.
DEFINITIONS = [
    ("Automatic", "Qualified by place at the Area meet: top 6 (Class A: top 3)."),
    ("Next best mark", "One of the 3 fill spots per event: the next best marks from all four Area meets."),
    ("At-large", "Met the posted at-large standard in the Area final, outside the automatic places. "
                 "Only these athletes are called at-large."),
    ("Next best mark + at-large standard", "The two routes together."),
    ("Guaranteed spots", "The fixed spots per event: 21 automatic (6 + 6 + 6 + 3) plus 3 next best mark = 24. "
                         "At-large-standard spots come on top and have no fixed number."),
    ("All qualifiers", "Everyone who earned a spot, whether or not they entered. A replay of each season's rules "
                       "against the Area results (it matches 98–99% of real entries once athlete choices and "
                       "replacements are counted)."),
    ("Actual entries", "Athletes who entered the MOC (the meet program)."),
    ("Entries", "Athlete-events: one athlete in two events counts twice."),
    ("Competed", "Has a row in the MOC results with any status other than DNS or scratch (DNF, DQ, no height and "
                 "fouls count)."),
    ("Top 8", "MOC final place 8th or better (9th or better in LJ, TJ, SP and DT). The 800/1600 finals seat 12 but "
              "top 8 is used; the 3200, HJ and PV have no prelims."),
    ("Typical MOC finish (median place)", "The middle MOC place of the entries in a group. Finalists keep their "
                                          "final place; everyone else with a valid MOC mark is ranked after the "
                                          "finalists by their best mark. Groups under 5 entries are not shown."),
    ("Spot use: Competed", "The qualifier ran the event at the MOC."),
    ("Spot use: Refilled", "The qualifier withdrew before the deadline and the next finalist from that Area took the spot."),
    ("Spot use: Chose another event", "The qualifier competed at the MOC, but in other events."),
    ("Spot use: Didn't enter", "The qualifier was not at the MOC at all (competed in no MOC event; includes a few "
                               "who were in the program but didn't start). Relay teams that didn't run count here."),
    ("Spot use: Unfilled (provisional)", "Nobody used the spot and the event field ended up short: a guaranteed spot "
                                         "whose qualifier didn't compete, nobody replaced them, and the event's MOC "
                                         "field ended below 24. Under verification."),
    ("Guaranteed spots used", "(Competed + refilled) ÷ guaranteed spots. At-large standard qualifiers are listed "
                              "separately and are not part of this %."),
    ("Left out", "The 3 best non-qualifiers per Area and event, by Area mark, compared with the 8th-best valid MOC "
                 "mark (9th for LJ/TJ/SP/DT) across all MOC rounds, one mark per athlete."),
    ("All seasons pooled", "Counts summed over 2022–2026; rates recomputed from the sums. Medians for pooled views "
                           "are computed from all five seasons' entries, not averaged."),
    ("Source", "Athletic.net Area and MOC results; MOC programs (Diablo Timing); rules per season. Pre-2026 "
               "allocations assumed from 2026; 2023 standards assumed from 2026. State results pending."),
]


CAVEATS = [
    "Small samples: many cells hold a handful of athletes (next-best-mark and at-large qualifiers outside "
    "Tri-Valley, Class A, any single event). A few athletes can move a rate by 10–30 points.",
    "Different meets: Area and MOC marks come from different days, wind, weather and competition.",
    "Rules before 2026 are partly assumed: allocations for 2022–2025 assumed from 2026; 2023 at-large standards "
    "assumed from 2026 (none printed).",
    "Unresolved school names (e.g. 'West County', 2022) appear as Unknown and are not compared.",
    "Unfilled spots are provisional (under verification). Three open questions: (1) in 23 events more guaranteed "
    "spots count as unfilled than the field was short of 24, because at-large qualifiers filled lanes (121 unfilled "
    "spots vs. 86 empty places); (2) 11 unfilled spots were taken by a lower finalist from the same Area, who isn't "
    "credited as a replacement because they weren't next in line; (3) 7 replacements didn't compete, and their "
    "spots still count as refilled.",
    "Privacy: MOC-place figures are published only for groups of 5 or more entries; single events are not shown "
    "on the Area place vs. MOC finish tab.",
    "State results are pending; state qualification is not shown.",
    "Statistical tests of the lowest-automatic vs. next-best-mark + at-large comparison (docs/findings_v1.md §4) "
    "support a consistent direction pooled over five seasons, not a precise gap, and say nothing about causes.",
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
    lo = lo[lo["moc_cutoff_mark"].notna()].assign(hit=lo["area_mark_would_have_been_top_finish"].fillna(False).astype(bool))
    # Only counts are embedded, never one row per athlete.
    lo = lo.groupby(["season", "gender", "event_code", "area"]).agg(hits=("hit", "sum"), total=("hit", "size")).reset_index()
    seasons = sorted(int(s) for s in su["season"].unique())
    events = [e for e in EVENT_ORDER if e in set(su["event_code"].astype(str))]
    return {
        "seasons": seasons, "events": events, "definitions": DEFINITIONS,
        "field_makeup": records(fm, ["season", "gender", "event_code", "field", "area", "qualifier_type", "count"]),
        "at_large_share": records(al, ["season", "gender", "event_code", "field", "spot_type", "area", "count"]),
        "moc_performance": records(mp, ["season", "gender", "event_code", "area", "qualifier_type", "competed",
                                        "top_finish", "scored"]),
        "spot_utilization": records(su, ["season", "gender", "event_code", "area", "guaranteed_spots", "at_large_spots",
                                         "declared", "no_show", "unfilled_spots",
                                         *[f"g_{k}" for k in SPOT_USE], *[f"al_{k}" for k in SPOT_USE if k != "unfilled"]]),
        "left_out": records(lo, ["season", "gender", "event_code", "area", "hits", "total"]),
        "place_curve": records(pd.read_csv(S / "core_place_curve.csv", dtype={"season": str, "area_place": str,
                                                                               "top8_count": "Int64"}),
                               ["season", "gender", "event_group", "area", "area_place", "entries", "top8_count",
                                "median_moc_place"]),
        "caveats": CAVEATS,
        "flags_unfilled": records(pd.read_csv(S / "spot_utilization_flags_unfilled.csv"),
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
