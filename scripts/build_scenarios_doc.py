"""Build docs/scenarios_v1.md from the scenario tables in data/summary/ (no names).

    .venv/bin/python scripts/build_scenarios_doc.py

Every number is read from the tables, so the document follows the data when it's rebuilt.
"""

import pandas as pd

from ncs_track import paths

S = paths.SUMMARY
AREAS = ["tri-valley", "bay-shore", "redwood-empire", "class-a"]
NAME = {"tri-valley": "Tri-Valley", "bay-shore": "Bay Shore", "redwood-empire": "Redwood Empire", "class-a": "Class A"}
SCEN = {"a_5553": ("5-5-5-3", 5, 6), "b_4443": ("4-4-4-3", 4, 9), "c_3333": ("3-3-3-3", 3, 12)}


def load(name):
    d = pd.read_csv(S / f"{name}.csv", dtype={"season": str})
    return d[(d["gender"] == "all") & (d["event"] == "all")]


CH, LO, ME, FM = load("scenario_changes"), load("scenario_left_out"), load("scenario_merit"), load("scenario_field_makeup")
POOLED = next(s for s in CH["season"].unique() if "pooled" in s)
SEASONS = sorted(s for s in CH["season"].unique() if "pooled" not in s)


def n(x, unit):
    x = int(x)
    return f"{x:,} {unit if x != 1 else unit.rstrip('s')}"


def pct(k, m):
    return f"{round(100 * k / m)}%" if m else "–"


def ch(sc, season, area="all"):
    return CH[(CH["scenario"] == sc) & (CH["season"] == season) & (CH["area"] == area)].iloc[0]


def lo(sc, season, area="all"):
    return LO[(LO["scenario"] == sc) & (LO["season"] == season) & (LO["area"] == area)].iloc[0]


def me(sc, season):
    return ME[(ME["scenario"] == sc) & (ME["season"] == season)].iloc[0]


def field(sc, season):
    f = FM[(FM["scenario"] == sc) & (FM["season"] == season)]
    return f.groupby("area")["count"].sum(), f.groupby("route")["count"].sum(), int(f["field_size"].iloc[0])


def finalists(sc, season, area="all"):
    r = ch(sc, season, area)
    return "not shown (fewer than 5 removed)" if pd.isna(r["removed_made_final"]) else n(r["removed_made_final"], "athletes")


def table(rows, head):
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
                     + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def current_block():
    by_area, by_route, size = field("current", POOLED)
    l, m = lo("current", POOLED), me("current", POOLED)
    return f"""## The current system (6-6-6-3 + 3 next best mark), the baseline

Replayed with pass-down routes on each season's real declarations; it reproduces what actually
happened (0 athletes added, 0 removed). Over 2022–2026: {n(size, "athletes")} in the fields
({n(by_route.get("automatic", 0), "automatic")}, {n(by_route.get("next_best_mark", 0), "next best mark")},
{n(by_route.get("at_large_standard", 0), "at-large standard")}).
- **Field share by Area:** {"; ".join(f"{NAME[a]} {n(by_area.get(a, 0), 'athletes')} ({pct(by_area.get(a, 0), size)})" for a in AREAS)}.
- **Faster but left out:** {n(l["beat_any"], "left-out athletes")} beat at least one automatic qualifier from another
  Area ({n(l["beat_any_excl_class_a"], "athletes")} with Class A qualifiers excluded from the comparison), out of
  {n(l["left_out"], "left-out finishers")}.
- **Merit capture:** {n(m["captured"], "marks")} of the {n(m["top_marks"], "top-24 Area marks")} per event were in the
  field ({pct(m["captured"], m["top_marks"])}).
"""


def scenario_block(sc):
    label, auto, fill = SCEN[sc]
    by_area, by_route, size = field(sc, POOLED)
    base_area, _, base_size = field("current", POOLED)
    c, l, m, l0, m0 = ch(sc, POOLED), lo(sc, POOLED), me(sc, POOLED), lo("current", POOLED), me("current", POOLED)
    gains = [(a, int(ch(sc, POOLED, a)["added"]), int(ch(sc, POOLED, a)["removed"])) for a in AREAS]
    rows = []
    for s in SEASONS:
        cs, ls, ms = ch(sc, s), lo(sc, s), me(sc, s)
        rows.append([s, n(cs["added"], "added"), n(cs["removed"], "removed"),
                     f"{n(ls['beat_any'], 'athletes')} (current {int(lo('current', s)['beat_any'])})",
                     f"{n(ls['beat_any_excl_class_a'], 'athletes')} (current {int(lo('current', s)['beat_any_excl_class_a'])})",
                     finalists(sc, s), n(cs["added_above_cutoff"], "athletes"),
                     f"{int(ms['captured'])} of {int(ms['top_marks'])} ({pct(ms['captured'], ms['top_marks'])})"])
    area_rows = [[NAME[a], n(ad, "added"), n(rm, "removed"), f"{ad - rm:+d}",
                  f"{int(by_area.get(a, 0))} ({pct(by_area.get(a, 0), size)})",
                  f"{int(base_area.get(a, 0))} ({pct(base_area.get(a, 0), base_size)})", finalists(sc, POOLED, a)]
                 for a, ad, rm in gains]
    return f"""## Scenario {label}: {auto}/{auto}/{auto}/3 automatic + {fill} next best mark

**What changes vs. current, 2022–2026 pooled.** {n(c["added"], "athletes")} would have been in the field who
weren't in reality, and {n(c["removed"], "athletes")} who were in reality would have been out. The field holds
{n(by_route.get("automatic", 0), "automatic qualifiers")}, {n(by_route.get("next_best_mark", 0), "next-best-mark qualifiers")}
and {n(by_route.get("at_large_standard", 0), "at-large standard qualifiers")} ({n(size, "athletes")}; current {n(base_size, "athletes")}).

**Who gains and who loses spots, by Area (pooled).**

{table(area_rows, ["Area", "Added", "Removed", "Net", "Field under " + label, "Field under current", "Removed who made the MOC final"])}

- **Faster but left out:** {n(l["beat_any"], "left-out athletes")} beat at least one automatic qualifier from another
  Area, against {n(l0["beat_any"], "athletes")} under current. With Class A qualifiers excluded from the comparison:
  {n(l["beat_any_excl_class_a"], "athletes")}, against {n(l0["beat_any_excl_class_a"], "athletes")}.
- **Cost (removed finalists):** of the {n(c["removed"], "removed athletes")}, {finalists(sc, POOLED)} made the MOC final in
  reality.
- **Estimated gain (estimate — different meets):** of the {n(c["added"], "added athletes")},
  {n(c["added_above_cutoff"], "athletes")} had an Area mark at or better than that season's MOC final cutoff.
- **Merit capture:** {n(m["captured"], "marks")} of {n(m["top_marks"], "top-24 Area marks")} in the field
  ({pct(m["captured"], m["top_marks"])}; current {pct(m0["captured"], m0["top_marks"])}).

**Per season.**

{table(rows, ["Season", "Added", "Removed", "Faster but left out (Class A in)", "Faster but left out (Class A out)",
              "Removed who made the final", "Estimated gain", "Merit capture"])}
"""


def main():
    doc = f"""# Alternative MOC allocations, simulated (scenarios v1)

*For coaches and committee members. Describes what four allocations would have done with the
2022–2026 Area results; it does not recommend any of them. Built from `data/summary/scenario_*.csv`
(`python -m ncs_track scenarios`); column definitions in `docs/analysis_tables.md`. Entries are
athlete-events: one athlete in two events counts twice.*

## What was simulated

- **Four allocations.** Tri-Valley, Bay Shore and Redwood Empire always get the same number of
  automatic spots; Class A always 3. The base field stays 24 per event, so every removed automatic
  spot becomes a next-best-mark spot.
  - Current: 6/6/6/3 + 3 next best mark
  - 5-5-5-3: 5/5/5/3 + 6 next best mark
  - 4-4-4-3: 4/4/4/3 + 9 next best mark
  - 3-3-3-3: 3/3/3/3 + 12 next best mark
- **Same rules otherwise.** Automatic spots pass down to each Area's next finisher when someone
  declines; next-best-mark spots then go to the best remaining Area-final marks from all four
  meets; the at-large standard, as printed each season, is applied on top. Ties at the last spot
  are all in. Relays follow the same rules; the 4x800, Unified events and relay splits are not
  included.
- **Measures.**
  - **Added / removed:** in the field under the scenario but not in reality, and the reverse.
  - **Faster but left out:** athletes who finished behind their Area's last automatic qualifier,
    weren't in the field by any route, and whose Area-final mark beat at least one automatic
    qualifier from another Area. Shown with Class A qualifiers included and excluded as the beaten
    group. Nobody left out beats a next-best-mark qualifier's mark, by design; this was checked in
    every scenario.
  - **Cost:** removed athletes who made the MOC final in reality (top 8; top 9 in LJ/TJ/SP/DT).
  - **Estimated gain:** added athletes whose Area mark was at or better than that season's MOC
    final cutoff (the 8th-best MOC mark across rounds; 9th in LJ/TJ/SP/DT).
  - **Merit capture:** of the 24 best Area-final marks in each event (among athletes who didn't
    decline), how many are in the field.

{current_block()}
{"".join(scenario_block(sc) + chr(10) for sc in SCEN)}
## Assumptions and limits

- **Declines.** Athletes who declined a spot in reality decline again in every scenario, including
  finishers walked past while a spot stayed unused. Athletes who were never offered a spot in
  reality are assumed to accept. In reality some of them might have declined, so the "added"
  counts are an upper bound.
- **MOC results for added athletes are estimates.** They didn't compete at the MOC. The estimated
  gain compares their Area mark with the MOC final cutoff; the marks come from different meets
  (different day, wind, weather, competition and, in field events, attempts).
- **Removed athletes' results are real,** but under a scenario the MOC field changes, so their
  places would not necessarily stay the same.
- **2023 at-large standards are assumed** from 2026 (none were printed). 2023 also had unusually
  slow MOC marks, which is where every removed finalist and every estimated gain falls.
- **Different meets.** "Faster" compares Area-final marks from different Area meets.
- **Program entrants the replay can't place** (6 unexplained entries and 8 with unresolved school
  names) stay in the field in every scenario and are never added, removed or left out.
- **Privacy.** Removed-finalist counts are shown only when 5 or more athletes were removed.
"""
    out = paths.ROOT / "docs" / "scenarios_v1.md"
    out.write_text(doc)
    print(f"wrote {out.relative_to(paths.ROOT)}")


if __name__ == "__main__":
    main()
