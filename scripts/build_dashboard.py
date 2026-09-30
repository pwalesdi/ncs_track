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
    ("Automatic", "Each Area's automatic spots (6; Class A 3) go to its top finishers who entered, in order of Area "
                  "place. If a finisher declines, the spot passes down to the next finisher, so e.g. a 10th-place "
                  "finisher can be an automatic qualifier."),
    ("Next best mark", "After declarations, the 3 spots per event go to the 3 best remaining Area-final marks across all "
                       "four Area meets (not automatic, didn't decline)."),
    ("At-large", "Anyone else remaining who met the posted at-large standard in the Area final. Only these athletes "
                 "are called at-large."),
    ("Next best mark + at-large standard", "The two routes together."),
    ("All qualifiers", "Who the rules made eligible before anyone declared: a replay of each season's rules against "
                       "the Area results (top 6 / top 3, then next best marks, then the standard)."),
    ("Actual entries", "Athletes in the MOC program, on the routes they actually took (after declines passed spots "
                       "down). The replay reproduces 99.5–100% of real entries per season."),
    ("Entries", "Athlete-events: one athlete in two events counts twice."),
    ("Competed", "Has a row in the MOC results with any status other than DNS or scratch (DNF, DQ, no height and "
                 "fouls count)."),
    ("Made the final", "Finished top 9 in the long jump, triple jump, shot put or discus, or top 8 in every other "
                       "event, relays included. (The 800 and 1600 finals seat 12; we count top 8.)"),
    ("Typical MOC finish (median place)", "The middle MOC place of the entries in a group. Finalists keep their "
                                          "final place; everyone else with a valid MOC mark is ranked after the "
                                          "finalists by their best mark. Groups under 5 entries are not shown."),
    ("Guaranteed spots", "Per Area and event: its automatic spots (6; Class A 3) plus the next-best-mark spots it won."),
    ("Declined", "Finished ahead of the Area's last automatic qualifier but not in the MOC program. The spot passes down "
                 "to the next finisher. A decline is not a no-show and carries no penalty."),
    ("Spot use: Competed", "The qualifier ran the event at the MOC."),
    ("Spot use: No-show", "The qualifier was in the MOC program for the event but didn't compete in it (did not start, "
                          "or absent from its results), including athletes who competed in other events that day and "
                          "athletes who got the spot by pass-down."),
    ("Spot use: Not used", "No entrant from that Area took the spot."),
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
    mp = pd.read_csv(S / "moc_performance.csv", dtype={"season": str, "made_final": "Int64"})
    mp = mp[mp["qualifier_type"].isin(["automatic", "at_large_combined"])]
    su = pd.read_csv(S / "spot_utilization.csv")
    seasons = sorted(int(s) for s in su["season"].unique())
    events = [e for e in EVENT_ORDER if e in set(su["event_code"].astype(str))]
    return {
        "seasons": seasons, "events": events, "definitions": DEFINITIONS,
        "field_makeup": records(fm, ["season", "gender", "event_code", "field", "area", "qualifier_type", "count"]),
        "at_large_share": records(al, ["season", "gender", "event_code", "field", "spot_type", "area", "count"]),
        "moc_performance": records(mp, ["season", "gender", "event", "area", "qualifier_type", "competed", "made_final"]),
        "spot_utilization": records(su, ["season", "gender", "event_code", "area", "guaranteed_spots", "passed_down",
                                         "at_large_spots", "entries", "no_show",
                                         *[f"g_{k}" for k in SPOT_USE], *[f"al_{k}" for k in SPOT_USE if k != "not_used"]]),
        "place_curve": records(pd.read_csv(S / "core_place_curve.csv", dtype={"season": str, "area_place": str,
                                                                               "made_final_count": "Int64"}),
                               ["season", "gender", "event_group", "area", "area_place", "entries", "made_final_count",
                                "median_moc_place"]),
        "caveats": CAVEATS,
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
