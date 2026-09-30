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
- same-Area replacement
- no entry limit

Each season uses its own rules file. See `docs/replay_2026.md` and
`docs/replay_seasons.md`.

**What is tracked.** `outputs/qualifiers.csv` names athletes and is git-ignored. The
`data/summary/` tables contain no names and are tracked; `tests/test_no_athlete_names.py`
checks them.

## Terms

- **qualifier_type**
  - `automatic`: qualified by place at the Area meet (top 6; Class A top 3).
  - `next_best_mark`: one of the 3 fill spots (next best marks from all four meets).
  - `at_large_standard`: met the posted at-large standard in the Area final, outside the
    automatic places.
  - `replacement`: in the program though not predicted, and paired with a vacancy by the
    replacement overlay (same Area: the next finalist in line).
  - `unexplained`: in the program, not predicted, no explanation. Also used for program
    entries whose school spelling has no area that season (area = `unknown`).
- **at_large_combined** = `next_best_mark` + `at_large_standard`. In athlete rows it's a
  0/1 column. In summary tables it appears as extra rows with `rollup = True`; don't add
  them to the per-type rows.
- **Fields**
  - **qualified**: everyone the rules say qualified, i.e. the replay prediction (types
    `automatic`, `next_best_mark`, `at_large_standard`).
  - **declared**: everyone in the MOC program, including replacements and unexplained
    entrants.
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
| top_finish | 1 if `moc_final_place` ≤ 9 for LJ, TJ, SP and DT, ≤ 8 for every other event. The dashboard's "made the final" metric. |
| reached_final_round | 1 if the athlete appears in the MOC finals round (see note) |
| scored | 1 if `moc_final_place` ≤ 6 |
| choice_tag | For a qualified athlete not in the program: `chose_other_events` (listed elsewhere in the program, incl. the 4x800 and relay rosters) or `did_not_declare` |
| replacement_for_area, vacancy_refilled_by_area | The Area whose vacancy a replacement filled / the Area of the athlete who refilled a vacancy |
| competed_other_moc_event | For a qualified athlete not in the program (individuals only): 1 if they competed in any other MOC event that season (individual, relay leg or 4x800; any status but DNS/SCR) |
| moc_overall_place | Overall MOC place in the event (see note) |
| state_qualified | `pending` until the CIF State meet data arrives |

**Notes on the finals columns**
- **top_finish uses top 8 even where a final seats more.** The 800 and 1600 finals seat 12.
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

At-large spots only, per season × gender × event × field × `spot_type`
(`next_best_mark`, `at_large_standard`, `at_large_combined`) × area. Every Area is listed,
including zeros. Columns: `count`, `spots` (all Areas' spots of that type in the event)
and `area_share = count / spots` (blank when `spots` is 0).

## data/summary/moc_performance.csv

Declared athletes who competed, per season × gender × event × area × qualifier_type, plus
`at_large_combined` rollup rows. Columns: `competed` (count); `top_finish`, `scored`,
`reached_final_round` (counts); and `*_rate` (count / competed).

## data/summary/spot_utilization.csv

Per season × gender × event × area, over the spots the rules gave that Area:

| Column | Meaning |
|---|---|
| spots_earned | Qualified by the rules (the replay prediction) |
| declared | Of those, in the program |
| competed | Of those, competed (see terms) |
| no_show | Declared but did not compete |
| not_declared | Qualified but not in the program. `= spots_earned − declared`. |
| not_declared_chose_other_events / not_declared_did_not_declare | Split of `not_declared` by athlete choice |
| unused_total | `spots_earned − competed` (= `no_show + not_declared`) |
| utilization_rate | `competed / spots_earned` |
| vacancies_refilled | This Area's not-declared spots paired with a replacement |
| refilled_by_area | Which Areas the replacements came from, `area:count` |
| replacements_from_this_area | This Area's athletes who entered as replacements, for any Area |
| empty_lanes | Spots that went to nobody: `unused_total − vacancies_refilled`, never below 0. Computed per event; the roll-ups sum the event values. The "wasted spot" metric. |
| no_show_rate | `no_show / declared` |
| not_declared_individual | Not-declared spots held by individuals (relay teams excluded) |
| not_declared_competed_other_event | Of those, athletes who competed in another MOC event that season |
| double_qualifier_share | `not_declared_competed_other_event / not_declared_individual` |

**How to read it**
- **No-shows are never refilled.** A vacancy can only be seen when a qualified athlete is
  missing from the program.
- **Replacements count only in `replacements_from_this_area`.** A replacement never counts
  toward the `competed` of the Area whose spot it filled. So utilization measures how many
  of an Area's earned spots its own qualifiers used.
- **`refilled_by_area` is always the same Area in these tables.** With same-Area
  replacement, a vacancy is always refilled from its own Area. It would only differ under
  fill-line replacement.

**`spot_utilization_by_area.csv`** is the roll-up per season × area over all events,
with `utilization_rate` recomputed from the sums.

**Flag lists.** Each lists every Area × gender × event with the metric above 0 in at least
3 of the seasons analysed. Columns: the seasons, how many there were, and the metric summed
over all seasons.
- `spot_utilization_flags.csv`: `unused_total`
- `spot_utilization_flags_empty_lanes.csv`: `empty_lanes`

**`no_shows_empty_lanes_by_area.csv`** gives per season × area the counts behind the rates:
`spots_earned`, `declared`, `no_show`, `no_show_rate`, `not_declared`,
`vacancies_refilled`, `empty_lanes` and `empty_lane_rate` (= `empty_lanes /
spots_earned`).

**Empty lanes include no-shows.** A no-show declared, so the vacancy is invisible in the
program and is never counted as refilled.

## data/summary/left_out.csv

Per season × gender × event × area: the 3 best non-qualifiers by Area mark (valid marks
only; ties broken by Area place). No names.

| Column | Meaning |
|---|---|
| rank_among_non_qualifiers | 1–3 |
| area_place, area_mark, area_mark_value | Area final result (value in seconds or metres) |
| is_relay | |
| declared_anyway | In the MOC program anyway, e.g. as a replacement (blank for relays) |
| moc_cutoff_place, moc_cutoff_mark | The MOC final's 8th-place mark (9th for LJ/TJ/SP/DT) that season |
| area_mark_would_have_been_top_finish | The Area mark equals or beats the cutoff |
| caveat | See below |

**Caveat:** the Area mark and the MOC marks come from different meets, with different
wind, weather, competition and (field events) attempts. The comparison doesn't predict how
the athlete would have placed at the MOC.

## Known limits

- **MOC linking.** MOC results are linked by Athletic.net athlete ID, or by name and school
  when there is no ID. 1,292 of 1,297 MOC top-8/9 finishes, 2022–2026, link to a
  qualifiers row.
  - The rest: one 2024 program spelling differs from Athletic.net, and "West County" (2022)
    is an unconfirmed rename kept in review. Athletic.net lists those athletes under Analy.
- **Unknown area.** Program entries whose school spelling is unresolved have `area =
  unknown`: 15 in 2022 and 5 in 2023.
- **Assumed allocations.** Allocation numbers before 2026 are assumed from 2026; standards
  come from each season's results (2023: assumed). See `docs/decisions.md`.
