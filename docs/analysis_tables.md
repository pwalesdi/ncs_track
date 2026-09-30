# Analysis tables

Built by `python -m ncs_track analysis --season 2022 2023 2024 2025 2026`
(`src/ncs_track/analysis.py`).

**Scope.** Every table is split by season, gender and event; years are never pooled. Main
events only: no Unified, Ambulatory, 4x800, relay splits or exhibition rows.

**Reading of the rules.** Every season uses the best 2026 reading (`analysis.BEST_READING`):
- Class A at-large from 4th
- fill before at-large
- MOC-guide fill (3 spots from all four meets)
- fill ties included
- wind-aided marks allowed
- no entry limit
- routes of actual entries by pass-down (decision #32, `replay.pass_down`)

Each season uses its own rules file. See `docs/replay_2026.md` and
`docs/replay_seasons.md`.

**What is tracked.** `outputs/qualifiers.csv`, `outputs/no_shows.csv`, `outputs/left_out.csv`
and `outputs/left_out_beaten.csv` name athletes and are git-ignored. The
`data/summary/` tables contain no names and are tracked; `tests/test_no_athlete_names.py`
checks them.

## Terms

**Wording.** "At-large" means only athletes who met the at-large standard. The 3 fill spots
per event are "next best mark", and the two together are "next best mark + at-large
standard" (the column name `at_large_combined` is kept for compatibility). "Entries" are
athlete-events: one athlete in two events counts twice. "Guaranteed spots" per Area and event
are its automatic spots (6; Class A 3) plus the next-best-mark spots it won.

- **qualifier_type** — the pre-declaration route ("All qualifiers": who the rules made
  eligible before anyone declared; `replay.evaluate`)
  - `automatic`: top 6 at the Area meet (Class A top 3).
  - `next_best_mark`: one of the 3 fill spots (next best marks from all four meets).
  - `at_large_standard`: met the posted at-large standard in the Area final, outside the
    automatic places.
- **route** — the pass-down route of a program entrant ("Actual entries"; decision #32)
  - `automatic`: one of the Area's first 6 (Class A 3) entrants in Area-place order; ties at
    the last place all count.
  - `next_best_mark`: after declarations, one of the 3 best remaining marks, all four meets.
  - `at_large_standard`: remaining and met the standard.
  - `unexplained`: in the program with no route; also program entries whose school has no
    area that season and couldn't be linked by name (area = `unknown`).
- **declined** — `automatic` (finished ahead of the Area's last automatic qualifier, not in
  the program), `next_best_mark` (a better remaining mark than a next-best-mark taker, not in
  the program) or `at_large_standard` (remaining, met the standard, not in the program).
- **at_large_combined** = next best mark + at-large standard. In athlete rows it's a
  0/1 column. In summary tables it appears as extra rows with `rollup = True`; don't add
  them to the per-type rows.
- **Fields**
  - **qualified** ("All qualifiers" on the dashboard): the pre-declaration replay; summary
    tables use `qualifier_type`.
  - **declared** ("Actual entries"): athletes in the MOC program; summary tables use `route`
    (as their `qualifier_type` column).
- **competed** = 1 if the athlete has a row in the MOC results with any status other than
  DNS or SCR.
  - DNF, DQ, NH, FOUL and FS count as competed without a valid mark. The status is kept in
    `moc_status`.
  - DNS, SCR, or being in the program but missing from the results, count as not competed.
- **area**: the Area meet the athlete's result came from, per result row. For declared
  entrants with no Area result, it's their school's area that season.

## outputs/qualifiers.csv (athlete level, git-ignored)

One row per athlete (or relay team) × event × season, covering the qualified and declared
fields together.

| Column | Meaning |
|---|---|
| season, gender, event_code | |
| athlete_name, athlete_id, is_relay | Athletic.net name and ID (blank for relays) |
| area, school | See terms |
| qualifier_type, at_large_combined | See terms |
| area_place, area_mark | Place and mark in the Area final |
| in_qualified_field, in_declared_field | 0/1 |
| competed | See terms |
| moc_status | `OK`, a result status, `not_in_results` (declared but absent from the results) or `not_declared` |
| moc_final_place | Place in the MOC final round, when the athlete has a valid mark there |
| made_final | 1 if `moc_final_place` ≤ 9 for LJ, TJ, SP and DT, ≤ 8 for every other event. The dashboard's "made the final" metric. |
| reached_final_round | 1 if the athlete appears in the MOC finals round (see note) |
| scored | 1 if `moc_final_place` ≤ 6 |
| route, declined | See terms |
| no_show | 1 if in the program for the event but didn't compete in it |
| choice_tag | For a pre-declaration qualifier not in the program: `chose_other_events` (listed elsewhere in the program, incl. the 4x800 and relay rosters) or `did_not_declare` |
| competed_other_moc_event | For every qualified individual who didn't compete in this event (in the program or not): 1 if they competed in any other MOC event that season (individual, relay leg or 4x800; any status but DNS/SCR), else 0. Blank for relays, competitors and rows without an Athletic.net ID |
| moc_overall_place | Overall MOC place in the event (see note) |
| state_qualified | `pending` until the CIF State meet data arrives |

**Notes on the finals columns**
- **made_final uses top 8 even where a final seats more.** The 800 and 1600 finals seat 12.
  The 3200, HJ and PV have no prelims, so there is no separate final and top 8 is used
  there too.
- **reached_final_round depends on the event.**
  - Running events with prelims: 1 if the athlete has a row in the MOC finals round.
  - 3200, HJ and PV: one final round, so 1 for everyone who competed.
  - LJ, TJ, SP and DT: 9 athletes get three extra attempts, but neither the Athletic.net
    nor the Hy-Tek results record attempts. The column falls back to final place ≤ 9.

**moc_overall_place.** Finalists with a valid final mark keep their final place. Everyone
else with a valid MOC mark (prelim-only athletes, and finalists without a valid final mark)
is ranked after them by their best valid mark. In events without prelims, it is the final
place. It is blank for athletes with no valid MOC mark.

## data/summary/field_makeup.csv

Rows are season × gender × event × field (`qualified` / `declared`) × area ×
qualifier_type, plus `rollup` rows for `at_large_combined`. Columns: `count`,
`field_size` (athletes in that field for the event) and `share_of_field = count /
field_size`.

## data/summary/at_large_share.csv

Next-best-mark and at-large spots only, per season × gender × event × field × `spot_type`
(`next_best_mark`, `at_large_standard`, `at_large_combined`) × area. Every Area is listed,
including zeros. Columns: `count`, `spots` (all Areas' spots of that type in the event)
and `area_share = count / spots` (blank when `spots` is 0).

## data/summary/moc_performance.csv

Declared athletes who competed, aggregated to the dashboard's filter grain: season (each,
plus `2022-2026 pooled`) × gender (`girls`, `boys`, `all`) × event (each event code,
`group:<name>`, `all`) × area × qualifier_type, plus `at_large_combined` rollup rows. Only
groups with at least one entry have a row. Columns: `competed` (count); `made_final`,
`scored`, `reached_final_round` (counts); and `*_rate` (count / competed).
**Small cells:** when `competed` < 5, the counts and rates are blank (decision #29).

## data/summary/spot_utilization.csv

Per season × gender × event × Area (every Area, zeros included; decision #33). Field size
plays no part.

| Column | Meaning |
|---|---|
| auto_spots, nbm_spots | The Area's automatic spots (6; Class A 3; +1 per tie at the last automatic place) and the next-best-mark spots it won |
| guaranteed_spots | `auto_spots + nbm_spots` |
| g_competed, g_no_show, g_not_used | Guaranteed spots whose entrant competed / was in the program but didn't compete / that no entrant from the Area took. They sum to `guaranteed_spots`. |
| passed_down | Automatic spots passed down because a finisher ahead declined |
| declined_nbm, declined_at_large | Next-best-mark and at-large spots declined |
| at_large_spots, al_competed, al_no_show | At-large standard entrants, reported apart from guaranteed spots |
| entries, no_show | Every program entrant from the Area (any route, incl. unexplained), and those who didn't compete |
| no_show_competed_other_event | No-shows who competed in another MOC event that season |
| guaranteed_used, guaranteed_used_rate | `g_competed`, and ÷ `guaranteed_spots` |
| no_show_rate | `no_show / entries` |

**`spot_utilization_by_area.csv`** is the roll-up per season × area over all events.

## data/summary/core_comparison.csv and core_tests.csv

`core_comparison.csv` compares each Area's lowest automatic qualifiers (Area places 5–6;
3rd for Class A) with next-best-mark + at-large qualifiers from the other Areas. Only entries that competed
at the MOC count, with genders combined. Rows are per season (plus `2022-2026 pooled`) ×
event group (plus `all`) × area × `comparison_group`. Columns: `competed`, `made_final`,
`made_final_rate`, `with_moc_place` and `median_moc_place`. Cells with fewer than 5
entries publish `competed` and `with_moc_place` only; the MOC-place figures are blank.

`core_tests.csv` (pooled 2022–2026, all events) gives three p-values for the
`gap = lowest-automatic made-the-final rate − other Areas' next-best-mark + at-large made-the-final rate`:

| Column | Test |
|---|---|
| naive_p | Two-proportion z test; treats every athlete-event as independent (the original test) |
| clustered_p | Difference in rates with standard errors clustered by athlete (relay teams by school × season). Repeat athletes are handled; there are `clusters` athletes. |
| permutation_p | Area labels shuffled within season × gender × event, 10,000 times (seed 20260930), keeping each athlete's route (lowest automatic / at-large) fixed. It asks whether this Area's gap is larger than random Area labels produce. `expected_gap_random_areas` is the mean gap under shuffling, and the p-value is two-sided around it. |

## data/summary/core_place_curve.csv

Where Area finishers end up at the MOC, aggregated for the public repo. It is the data
behind the dashboard's "Area place vs. MOC finish" tab and the Overview cards.
- **Rows:** season (each, plus `2022-2026 pooled`) × gender (`girls`, `boys`, `all`) ×
  `event_group` (six groups, plus `all`) × area (plus `bay-shore+redwood-empire`) ×
  `area_place` (`1`…`12`, the bands `5-6` and `7-8`, and `7-8 not automatic`: 7th–8th-place
  entrants on a next-best-mark or at-large route).
- **Guards:** a combined-Area cell is shown only when each Area's own cell is; the
  `7-8 not automatic` cell only when the automatic 7th–8th cell is 0 or ≥ 5 entries.
- **Columns:** `entries` (athlete-events that competed at the MOC), `made_final_count` and
  `median_moc_place`.
- **Small cells:** when `entries` < 5, `made_final_count` and `median_moc_place` are blank, so no
  row reveals one athlete's MOC place.
- **No single events:** the table has no single-event rows.

## Left out (decision #34)

**Left out** = finished in an Area final behind the Area's last automatic qualifier, no
route and not in the program. Compared with other Areas' automatic qualifiers (pass-down);
"beaten" = the qualifier's Area-final mark is strictly worse. Marks come from different Area
meets.

- **`outputs/left_out.csv`** (local, names): one row per left-out athlete, with
  `beaten_other_area_autos` and `beaten_<area>` counts.
- **`outputs/left_out_beaten.csv`** (local, names): one row per left-out athlete × beaten
  qualifier, with the qualifier's MOC outcome.
- **`data/summary/left_out_counts.csv`:** per season × gender × event × `area` (left-out
  athlete's) × `beaten_area`: `beat_any` (left-out athletes who beat ≥ 1 automatic qualifier
  from `beaten_area`) and `beaten_autos` (distinct qualifiers beaten). Rows with
  `beaten_area = any` carry `left_out` (all left-out finishers) and `beat_any` (beat ≥ 1
  from any other Area).
- **`data/summary/left_out_beaten_moc.csv`:** how the beaten qualifiers did at the MOC, per
  season (+ pooled) × `area` × `beaten_area` (each also `all`): `beaten_autos`, `competed`,
  `made_final`, `median_moc_place`; the last two blank below 5 entries.

## data/summary/match_rates.csv

Per season: RULES and RAW match rates of the pre-declaration replay and of pass-down
against the real MOC programs, pass-down matched entries and unexplained entries.

## Known limits

- **MOC linking.** MOC results are linked by Athletic.net athlete ID, or by name and school
  when there is no ID. 1,292 of 1,297 MOC finalists (top 8, top 9 in LJ/TJ/SP/DT), 2022–2026, link to a
  qualifiers row.
  - The rest: one 2024 program spelling differs from Athletic.net, and "West County" (2022)
    is an unconfirmed rename kept in review. Athletic.net lists those athletes under Analy;
    pass-down links most of them by name (decision #32).
- **Unknown area.** Program entries whose school spelling is unresolved have `area =
  unknown`: 15 in 2022 and 5 in 2023.
- **Assumed allocations.** Allocation numbers before 2026 are assumed from 2026; standards
  come from each season's results (2023: assumed). See `docs/decisions.md`.
