# What the data shows: MOC qualification by Area, 2022–2026 (findings v1)

*For coaches and the committee. Built from the tables in `data/summary/`; every column is defined in
`docs/analysis_tables.md`. Every number carries its unit, e.g. "25 of 284 entries made the final (9%)".*

> **What changed in this update (2026-09-30, third update)**
> - **"Top 8" is now "made the final"** (same definition: top 9 in LJ/TJ/SP/DT, top 8
>   elsewhere).
> - **§5, left-out athletes** is now one paragraph; its athlete-level table is no longer
>   published.
> - **Privacy.** `moc_performance.csv` now follows the small-cell rule: made-the-final and
>   scored counts are published only for groups of 5 or more entries.
> - **§6, spot use rebuilt on guaranteed spots only.** Five segments (competed, refilled,
>   chose another event, didn't enter, unfilled); "Other unused" is gone. At-large standard
>   qualifiers are reported separately. Unfilled stays provisional, with the three open
>   questions listed in §6.
>
> **Earlier (second update)**
> - **Wording.** "At-large" now means only athletes who met the at-large standard. The 3 fill
>   spots are "next best mark", and the two together are "next best mark + at-large
>   standard". Every number now states its unit. "Entries" means athlete-events: one
>   athlete in two events counts twice.
> - **§6, spot use: corrected metric.** "Empty lanes" is replaced by **unfilled spots**
>   (provisional, under verification). An unfilled spot is a guaranteed spot (automatic or
>   next best mark) that nobody used, in an event whose MOC field ended below 24. The old
>   count also included spots whose field was still full, and at-large-standard spots,
>   which have no fixed number. Over five seasons, 247 "empty lanes" become 121 unfilled
>   spots.
> - **Privacy.** MOC-place figures are published only for groups of 5 or more entries.
> - **First update (same day).** §5 used the all-rounds MOC cutoff; §4 adds the permutation
>   and athlete-clustered tests.

## How to read this

- **Seasons.** 2022, 2023, 2024, 2025 and 2026, each shown on its own. A 5-season pooled
  summary is at the end, clearly labelled.
- **Areas.** The four MOC qualifying meets: Tri-Valley, Bay Shore, Redwood Empire and
  Class A.
- **How athletes reach the MOC.**
  - **Automatic:** top 6 at the Area meet (Class A: top 3).
  - **Next best mark:** the 3 fill spots per event, which go to the next best marks across
    all four meets.
  - **At-large:** met the posted at-large standard in the Area final, outside the automatic
    places. Only these athletes are called at-large here.
  - **Next best mark + at-large standard:** the two routes together.
  - **Replacement:** entered to fill a vacancy.
- **Guaranteed spots.** Each event has 24 fixed spots: 21 automatic (6 + 6 + 6 + 3) plus
  3 next best mark. At-large spots come on top and have no fixed number.
- **Two fields.**
  - **All qualifiers:** everyone who earned a spot, whether or not they entered. This comes
    from replaying each season's rules against the Area results; the replay matches 98–99%
    of real MOC entries once athlete choices and replacements are counted.
  - **Actual entries:** athletes who entered the MOC (the meet program).
- **Entries** are athlete-events: one athlete in two events counts twice.
- **Made the final:** finished top 9 in the long jump, triple jump, shot put or discus, or
  top 8 in every other event, relays included. (The 800 and 1600 finals seat 12; we count
  top 8.) **Scored:** 6th or better.
- **This document describes; it doesn't recommend.** It doesn't propose any change to how
  spots are allocated.

## 1. Field makeup by Area

**What the data shows.** Each of the three large Areas gets about 192 automatic spots per
season (6 per event × 32 events); Class A gets about 96. The differences between Areas come
from the next-best-mark and at-large spots.
- **Tri-Valley** holds 35–36% of all MOC spots every season, with 78–102 next-best-mark +
  at-large spots a season.
- **Bay Shore** holds 24–26%, with 5–17 such spots.
- **Redwood Empire** holds 25–27%, with 11–25 such spots.
- **Class A** holds 12–13%, with 3–10 such spots.

Actual entries show almost the same shares, because most qualifiers enter. "Unknown" rows
are program entries whose school couldn't be matched (see §7).

**All qualifiers (everyone who earned a spot, whether or not they entered)**

| Season | Area | Share of MOC spots | Automatic | Next best mark | At-large standard |
|---|---|---|---|---|---|
| 2022 | Tri-Valley | 270 of 780 MOC spots (35%) | 192 spots | 76 spots | 2 spots |
| 2022 | Bay Shore | 200 of 780 MOC spots (26%) | 192 spots | 6 spots | 2 spots |
| 2022 | Redwood Empire | 212 of 780 MOC spots (27%) | 192 spots | 20 spots | 0 spots |
| 2022 | Class A | 98 of 780 MOC spots (13%) | 95 spots | 3 spots | 0 spots |
| 2023 | Tri-Valley | 280 of 807 MOC spots (35%) | 192 spots | 71 spots | 17 spots |
| 2023 | Bay Shore | 209 of 807 MOC spots (26%) | 193 spots | 14 spots | 2 spots |
| 2023 | Redwood Empire | 217 of 807 MOC spots (27%) | 192 spots | 24 spots | 1 spots |
| 2023 | Class A | 101 of 807 MOC spots (13%) | 96 spots | 4 spots | 1 spots |
| 2024 | Tri-Valley | 292 of 813 MOC spots (36%) | 192 spots | 74 spots | 26 spots |
| 2024 | Bay Shore | 210 of 813 MOC spots (26%) | 193 spots | 14 spots | 3 spots |
| 2024 | Redwood Empire | 203 of 813 MOC spots (25%) | 192 spots | 9 spots | 2 spots |
| 2024 | Class A | 108 of 813 MOC spots (13%) | 98 spots | 5 spots | 5 spots |
| 2025 | Tri-Valley | 288 of 806 MOC spots (36%) | 192 spots | 77 spots | 19 spots |
| 2025 | Bay Shore | 197 of 806 MOC spots (24%) | 192 spots | 4 spots | 1 spots |
| 2025 | Redwood Empire | 216 of 806 MOC spots (27%) | 194 spots | 15 spots | 7 spots |
| 2025 | Class A | 105 of 806 MOC spots (13%) | 96 spots | 6 spots | 3 spots |
| 2026 | Tri-Valley | 294 of 818 MOC spots (36%) | 192 spots | 72 spots | 30 spots |
| 2026 | Bay Shore | 207 of 818 MOC spots (25%) | 192 spots | 12 spots | 3 spots |
| 2026 | Redwood Empire | 216 of 818 MOC spots (26%) | 192 spots | 17 spots | 7 spots |
| 2026 | Class A | 101 of 818 MOC spots (12%) | 96 spots | 2 spots | 3 spots |

**Actual entries (athletes who entered the MOC)**

| Season | Area | Share of MOC spots | Automatic | Next best mark | At-large standard | Replacement | Unexplained |
|---|---|---|---|---|---|---|---|
| 2022 | Tri-Valley | 266 of 775 MOC spots (34%) | 185 spots | 71 spots | 2 spots | 5 spots | 3 spots |
| 2022 | Bay Shore | 202 of 775 MOC spots (26%) | 182 spots | 6 spots | 2 spots | 10 spots | 2 spots |
| 2022 | Redwood Empire | 196 of 775 MOC spots (25%) | 168 spots | 15 spots | 0 spots | 11 spots | 2 spots |
| 2022 | Class A | 96 of 775 MOC spots (12%) | 85 spots | 1 spots | 0 spots | 8 spots | 2 spots |
| 2022 | Unknown | 15 of 775 MOC spots (2%) | 0 spots | 0 spots | 0 spots | 0 spots | 15 spots |
| 2023 | Tri-Valley | 268 of 789 MOC spots (34%) | 179 spots | 59 spots | 14 spots | 9 spots | 7 spots |
| 2023 | Bay Shore | 202 of 789 MOC spots (26%) | 177 spots | 14 spots | 2 spots | 7 spots | 2 spots |
| 2023 | Redwood Empire | 215 of 789 MOC spots (27%) | 186 spots | 22 spots | 1 spots | 5 spots | 1 spots |
| 2023 | Class A | 99 of 789 MOC spots (13%) | 86 spots | 4 spots | 1 spots | 8 spots | 0 spots |
| 2023 | Unknown | 5 of 789 MOC spots (1%) | 0 spots | 0 spots | 0 spots | 0 spots | 5 spots |
| 2024 | Tri-Valley | 277 of 798 MOC spots (35%) | 186 spots | 65 spots | 21 spots | 4 spots | 1 spots |
| 2024 | Bay Shore | 210 of 798 MOC spots (26%) | 185 spots | 14 spots | 2 spots | 5 spots | 4 spots |
| 2024 | Redwood Empire | 207 of 798 MOC spots (26%) | 179 spots | 8 spots | 2 spots | 10 spots | 8 spots |
| 2024 | Class A | 104 of 798 MOC spots (13%) | 85 spots | 5 spots | 4 spots | 7 spots | 3 spots |
| 2025 | Tri-Valley | 277 of 789 MOC spots (35%) | 181 spots | 70 spots | 19 spots | 6 spots | 1 spots |
| 2025 | Bay Shore | 197 of 789 MOC spots (25%) | 180 spots | 4 spots | 1 spots | 10 spots | 2 spots |
| 2025 | Redwood Empire | 212 of 789 MOC spots (27%) | 178 spots | 15 spots | 6 spots | 12 spots | 1 spots |
| 2025 | Class A | 103 of 789 MOC spots (13%) | 87 spots | 5 spots | 3 spots | 5 spots | 3 spots |
| 2026 | Tri-Valley | 287 of 804 MOC spots (36%) | 180 spots | 70 spots | 27 spots | 7 spots | 3 spots |
| 2026 | Bay Shore | 207 of 804 MOC spots (26%) | 187 spots | 12 spots | 3 spots | 3 spots | 2 spots |
| 2026 | Redwood Empire | 209 of 804 MOC spots (26%) | 175 spots | 12 spots | 6 spots | 9 spots | 7 spots |
| 2026 | Class A | 101 of 804 MOC spots (13%) | 88 spots | 2 spots | 3 spots | 5 spots | 3 spots |

## 2. Next-best-mark and at-large spots by Area

**What the data shows.** Tri-Valley athletes took most of these spots in every season:
- **Next best mark (the 3 fill spots):** 63–75% of next-best-mark spots.
- **At-large standard:** 50–81% of at-large spots.
- **Both together:** 66–73% of next-best-mark + at-large spots.

Caveats:
- **2022 at-large spots are few.** Only 4 athletes qualified on the standard, so those
  percentages rest on 4 athletes.
- **At-large spots are few by construction.** Next-best-mark spots are assigned first, so
  athletes who meet the standard usually take a next-best-mark spot.

**All qualifiers**

| Season | Area | Next best mark | At-large standard | Next best mark + at-large standard |
|---|---|---|---|---|
| 2022 | Tri-Valley | 76 of 105 next-best-mark spots (72%) | 2 of 4 at-large spots (50%) | 78 of 109 next-best-mark + at-large spots (72%) |
| 2022 | Bay Shore | 6 of 105 next-best-mark spots (6%) | 2 of 4 at-large spots (50%) | 8 of 109 next-best-mark + at-large spots (7%) |
| 2022 | Redwood Empire | 20 of 105 next-best-mark spots (19%) | 0 of 4 at-large spots (0%) | 20 of 109 next-best-mark + at-large spots (18%) |
| 2022 | Class A | 3 of 105 next-best-mark spots (3%) | 0 of 4 at-large spots (0%) | 3 of 109 next-best-mark + at-large spots (3%) |
| 2023 | Tri-Valley | 71 of 113 next-best-mark spots (63%) | 17 of 21 at-large spots (81%) | 88 of 134 next-best-mark + at-large spots (66%) |
| 2023 | Bay Shore | 14 of 113 next-best-mark spots (12%) | 2 of 21 at-large spots (10%) | 16 of 134 next-best-mark + at-large spots (12%) |
| 2023 | Redwood Empire | 24 of 113 next-best-mark spots (21%) | 1 of 21 at-large spots (5%) | 25 of 134 next-best-mark + at-large spots (19%) |
| 2023 | Class A | 4 of 113 next-best-mark spots (4%) | 1 of 21 at-large spots (5%) | 5 of 134 next-best-mark + at-large spots (4%) |
| 2024 | Tri-Valley | 74 of 102 next-best-mark spots (73%) | 26 of 36 at-large spots (72%) | 100 of 138 next-best-mark + at-large spots (72%) |
| 2024 | Bay Shore | 14 of 102 next-best-mark spots (14%) | 3 of 36 at-large spots (8%) | 17 of 138 next-best-mark + at-large spots (12%) |
| 2024 | Redwood Empire | 9 of 102 next-best-mark spots (9%) | 2 of 36 at-large spots (6%) | 11 of 138 next-best-mark + at-large spots (8%) |
| 2024 | Class A | 5 of 102 next-best-mark spots (5%) | 5 of 36 at-large spots (14%) | 10 of 138 next-best-mark + at-large spots (7%) |
| 2025 | Tri-Valley | 77 of 102 next-best-mark spots (75%) | 19 of 30 at-large spots (63%) | 96 of 132 next-best-mark + at-large spots (73%) |
| 2025 | Bay Shore | 4 of 102 next-best-mark spots (4%) | 1 of 30 at-large spots (3%) | 5 of 132 next-best-mark + at-large spots (4%) |
| 2025 | Redwood Empire | 15 of 102 next-best-mark spots (15%) | 7 of 30 at-large spots (23%) | 22 of 132 next-best-mark + at-large spots (17%) |
| 2025 | Class A | 6 of 102 next-best-mark spots (6%) | 3 of 30 at-large spots (10%) | 9 of 132 next-best-mark + at-large spots (7%) |
| 2026 | Tri-Valley | 72 of 103 next-best-mark spots (70%) | 30 of 43 at-large spots (70%) | 102 of 146 next-best-mark + at-large spots (70%) |
| 2026 | Bay Shore | 12 of 103 next-best-mark spots (12%) | 3 of 43 at-large spots (7%) | 15 of 146 next-best-mark + at-large spots (10%) |
| 2026 | Redwood Empire | 17 of 103 next-best-mark spots (17%) | 7 of 43 at-large spots (16%) | 24 of 146 next-best-mark + at-large spots (16%) |
| 2026 | Class A | 2 of 103 next-best-mark spots (2%) | 3 of 43 at-large spots (7%) | 5 of 146 next-best-mark + at-large spots (3%) |

**Actual entries**

| Season | Area | Next best mark | At-large standard | Next best mark + at-large standard |
|---|---|---|---|---|
| 2022 | Tri-Valley | 71 of 93 next-best-mark spots (76%) | 2 of 4 at-large spots (50%) | 73 of 97 next-best-mark + at-large spots (75%) |
| 2022 | Bay Shore | 6 of 93 next-best-mark spots (6%) | 2 of 4 at-large spots (50%) | 8 of 97 next-best-mark + at-large spots (8%) |
| 2022 | Redwood Empire | 15 of 93 next-best-mark spots (16%) | 0 of 4 at-large spots (0%) | 15 of 97 next-best-mark + at-large spots (15%) |
| 2022 | Class A | 1 of 93 next-best-mark spots (1%) | 0 of 4 at-large spots (0%) | 1 of 97 next-best-mark + at-large spots (1%) |
| 2023 | Tri-Valley | 59 of 99 next-best-mark spots (60%) | 14 of 18 at-large spots (78%) | 73 of 117 next-best-mark + at-large spots (62%) |
| 2023 | Bay Shore | 14 of 99 next-best-mark spots (14%) | 2 of 18 at-large spots (11%) | 16 of 117 next-best-mark + at-large spots (14%) |
| 2023 | Redwood Empire | 22 of 99 next-best-mark spots (22%) | 1 of 18 at-large spots (6%) | 23 of 117 next-best-mark + at-large spots (20%) |
| 2023 | Class A | 4 of 99 next-best-mark spots (4%) | 1 of 18 at-large spots (6%) | 5 of 117 next-best-mark + at-large spots (4%) |
| 2024 | Tri-Valley | 65 of 92 next-best-mark spots (71%) | 21 of 29 at-large spots (72%) | 86 of 121 next-best-mark + at-large spots (71%) |
| 2024 | Bay Shore | 14 of 92 next-best-mark spots (15%) | 2 of 29 at-large spots (7%) | 16 of 121 next-best-mark + at-large spots (13%) |
| 2024 | Redwood Empire | 8 of 92 next-best-mark spots (9%) | 2 of 29 at-large spots (7%) | 10 of 121 next-best-mark + at-large spots (8%) |
| 2024 | Class A | 5 of 92 next-best-mark spots (5%) | 4 of 29 at-large spots (14%) | 9 of 121 next-best-mark + at-large spots (7%) |
| 2025 | Tri-Valley | 70 of 94 next-best-mark spots (74%) | 19 of 29 at-large spots (66%) | 89 of 123 next-best-mark + at-large spots (72%) |
| 2025 | Bay Shore | 4 of 94 next-best-mark spots (4%) | 1 of 29 at-large spots (3%) | 5 of 123 next-best-mark + at-large spots (4%) |
| 2025 | Redwood Empire | 15 of 94 next-best-mark spots (16%) | 6 of 29 at-large spots (21%) | 21 of 123 next-best-mark + at-large spots (17%) |
| 2025 | Class A | 5 of 94 next-best-mark spots (5%) | 3 of 29 at-large spots (10%) | 8 of 123 next-best-mark + at-large spots (7%) |
| 2026 | Tri-Valley | 70 of 96 next-best-mark spots (73%) | 27 of 39 at-large spots (69%) | 97 of 135 next-best-mark + at-large spots (72%) |
| 2026 | Bay Shore | 12 of 96 next-best-mark spots (12%) | 3 of 39 at-large spots (8%) | 15 of 135 next-best-mark + at-large spots (11%) |
| 2026 | Redwood Empire | 12 of 96 next-best-mark spots (12%) | 6 of 39 at-large spots (15%) | 18 of 135 next-best-mark + at-large spots (13%) |
| 2026 | Class A | 2 of 96 next-best-mark spots (2%) | 3 of 39 at-large spots (8%) | 5 of 135 next-best-mark + at-large spots (4%) |

## 3. MOC results by Area and route

Entries that competed at the MOC. To keep the table readable, only automatic and next best
mark + at-large standard qualifiers are shown. The full breakdown, including replacements,
is in `data/summary/moc_performance.csv`.

**What the data shows.**
- **Automatic qualifiers.** Tri-Valley's made the final in 62–65% of entries each season.
  Bay Shore's did in 31–34%, Redwood Empire's in 26–34%, and Class A's in 8–32%.
- **Class A varies most:** 7 of 83 entries made the final in 2026 (8%), but 27 of 84 in
  2024 (32%).
- **Next best mark + at-large qualifiers** made the final far less often than automatic
  qualifiers, in every Area and season. Outside Tri-Valley these groups are small, often
  under 20 entries, so their rates move a lot with one or two athletes.

| Season | Area | Route | Made the final | Scored (top 6) |
|---|---|---|---|---|
| 2022 | Tri-Valley | Automatic | 118 of 181 entries made the final (65%) | 90 of 181 entries scored (top 6) (50%) |
| 2022 | Tri-Valley | Next best mark + at-large standard | 19 of 69 entries made the final (28%) | 9 of 69 entries scored (top 6) (13%) |
| 2022 | Bay Shore | Automatic | 55 of 176 entries made the final (31%) | 42 of 176 entries scored (top 6) (24%) |
| 2022 | Bay Shore | Next best mark + at-large standard | 0 of 8 entries made the final (0%) | 0 of 8 entries scored (top 6) (0%) |
| 2022 | Redwood Empire | Automatic | 53 of 167 entries made the final (32%) | 41 of 167 entries scored (top 6) (25%) |
| 2022 | Redwood Empire | Next best mark + at-large standard | 4 of 13 entries made the final (31%) | 1 of 13 entries scored (top 6) (8%) |
| 2022 | Class A | Automatic | 9 of 84 entries made the final (11%) | 9 of 84 entries scored (top 6) (11%) |
| 2022 | Class A | Next best mark + at-large standard | 1 entry (fewer than 5: not shown) | 1 entry (fewer than 5: not shown) |
| 2023 | Tri-Valley | Automatic | 115 of 179 entries made the final (64%) | 89 of 179 entries scored (top 6) (50%) |
| 2023 | Tri-Valley | Next best mark + at-large standard | 6 of 70 entries made the final (9%) | 3 of 70 entries scored (top 6) (4%) |
| 2023 | Bay Shore | Automatic | 54 of 168 entries made the final (32%) | 43 of 168 entries scored (top 6) (26%) |
| 2023 | Bay Shore | Next best mark + at-large standard | 2 of 15 entries made the final (13%) | 2 of 15 entries scored (top 6) (13%) |
| 2023 | Redwood Empire | Automatic | 52 of 179 entries made the final (29%) | 37 of 179 entries scored (top 6) (21%) |
| 2023 | Redwood Empire | Next best mark + at-large standard | 3 of 20 entries made the final (15%) | 1 of 20 entries scored (top 6) (5%) |
| 2023 | Class A | Automatic | 24 of 82 entries made the final (29%) | 17 of 82 entries scored (top 6) (21%) |
| 2023 | Class A | Next best mark + at-large standard | 4 entries (fewer than 5: not shown) | 4 entries (fewer than 5: not shown) |
| 2024 | Tri-Valley | Automatic | 119 of 185 entries made the final (64%) | 94 of 185 entries scored (top 6) (51%) |
| 2024 | Tri-Valley | Next best mark + at-large standard | 12 of 84 entries made the final (14%) | 10 of 84 entries scored (top 6) (12%) |
| 2024 | Bay Shore | Automatic | 55 of 173 entries made the final (32%) | 36 of 173 entries scored (top 6) (21%) |
| 2024 | Bay Shore | Next best mark + at-large standard | 0 of 15 entries made the final (0%) | 0 of 15 entries scored (top 6) (0%) |
| 2024 | Redwood Empire | Automatic | 46 of 176 entries made the final (26%) | 33 of 176 entries scored (top 6) (19%) |
| 2024 | Redwood Empire | Next best mark + at-large standard | 1 of 9 entries made the final (11%) | 0 of 9 entries scored (top 6) (0%) |
| 2024 | Class A | Automatic | 27 of 84 entries made the final (32%) | 21 of 84 entries scored (top 6) (25%) |
| 2024 | Class A | Next best mark + at-large standard | 0 of 9 entries made the final (0%) | 0 of 9 entries scored (top 6) (0%) |
| 2025 | Tri-Valley | Automatic | 113 of 179 entries made the final (63%) | 92 of 179 entries scored (top 6) (51%) |
| 2025 | Tri-Valley | Next best mark + at-large standard | 10 of 88 entries made the final (11%) | 4 of 88 entries scored (top 6) (5%) |
| 2025 | Bay Shore | Automatic | 60 of 176 entries made the final (34%) | 44 of 176 entries scored (top 6) (25%) |
| 2025 | Bay Shore | Next best mark + at-large standard | 1 of 5 entries made the final (20%) | 0 of 5 entries scored (top 6) (0%) |
| 2025 | Redwood Empire | Automatic | 54 of 176 entries made the final (31%) | 40 of 176 entries scored (top 6) (23%) |
| 2025 | Redwood Empire | Next best mark + at-large standard | 0 of 19 entries made the final (0%) | 0 of 19 entries scored (top 6) (0%) |
| 2025 | Class A | Automatic | 20 of 81 entries made the final (25%) | 14 of 81 entries scored (top 6) (17%) |
| 2025 | Class A | Next best mark + at-large standard | 0 of 8 entries made the final (0%) | 0 of 8 entries scored (top 6) (0%) |
| 2026 | Tri-Valley | Automatic | 111 of 178 entries made the final (62%) | 86 of 178 entries scored (top 6) (48%) |
| 2026 | Tri-Valley | Next best mark + at-large standard | 14 of 95 entries made the final (15%) | 6 of 95 entries scored (top 6) (6%) |
| 2026 | Bay Shore | Automatic | 61 of 184 entries made the final (33%) | 53 of 184 entries scored (top 6) (29%) |
| 2026 | Bay Shore | Next best mark + at-large standard | 0 of 14 entries made the final (0%) | 0 of 14 entries scored (top 6) (0%) |
| 2026 | Redwood Empire | Automatic | 58 of 172 entries made the final (34%) | 40 of 172 entries scored (top 6) (23%) |
| 2026 | Redwood Empire | Next best mark + at-large standard | 2 of 18 entries made the final (11%) | 2 of 18 entries scored (top 6) (11%) |
| 2026 | Class A | Automatic | 7 of 83 entries made the final (8%) | 5 of 83 entries scored (top 6) (6%) |
| 2026 | Class A | Next best mark + at-large standard | 4 entries (fewer than 5: not shown) | 4 entries (fewer than 5: not shown) |

## 4. The core question: do some Areas' last automatic qualifiers do worse at the MOC than other Areas' next-best-mark + at-large qualifiers?

**The comparison.**
- **Lowest automatic qualifiers:** each Area's automatic qualifiers who placed 5th or 6th
  at their Area meet (3rd for Class A).
- **Next best mark + at-large qualifiers from the other three Areas.**
- **Who is counted:** only entries that competed at the MOC, with genders combined.

**Two measures.**
- **Made-the-final rate.**
- **Median MOC place.** Finalists keep their final place; everyone else is ranked after the
  finalists by their best MOC mark. Lower is better.

Groups under 5 entries show counts only.

**Per season, all events**

| Season | Area (its lowest automatics) | Events | Lowest automatics: made the final | Lowest automatics: median MOC place | Other Areas' next best mark + at-large: made the final | Other Areas' next best mark + at-large: median MOC place |
|---|---|---|---|---|---|---|
| 2022 | Tri-Valley | all events | 17 of 58 entries made the final (29%) | 11.5th (56 entries) | 4 of 22 entries made the final (18%) | 14.5th (22 entries) |
| 2022 | Bay Shore | all events | 2 of 56 entries made the final (4%) | 18th (49 entries) | 23 of 83 entries made the final (28%) | 12th (78 entries) |
| 2022 | Redwood Empire | all events | 6 of 51 entries made the final (12%) | 16th (49 entries) | 19 of 78 entries made the final (24%) | 13th (73 entries) |
| 2022 | Class A | all events | 1 of 26 entries made the final (4%) | 18.5th (26 entries) | 23 of 90 entries made the final (26%) | 13th (85 entries) |
| 2023 | Tri-Valley | all events | 24 of 58 entries made the final (41%) | 10th (55 entries) | 6 of 39 entries made the final (15%) | 15th (38 entries) |
| 2023 | Bay Shore | all events | 4 of 50 entries made the final (8%) | 19.5th (46 entries) | 10 of 94 entries made the final (11%) | 16th (89 entries) |
| 2023 | Redwood Empire | all events | 5 of 61 entries made the final (8%) | 17th (60 entries) | 9 of 89 entries made the final (10%) | 15th (83 entries) |
| 2023 | Class A | all events | 0 of 24 entries made the final (0%) | 21th (21 entries) | 11 of 105 entries made the final (10%) | 16th (99 entries) |
| 2024 | Tri-Valley | all events | 30 of 61 entries made the final (49%) | 9th (60 entries) | 1 of 33 entries made the final (3%) | 18th (33 entries) |
| 2024 | Bay Shore | all events | 7 of 57 entries made the final (12%) | 18th (55 entries) | 13 of 102 entries made the final (13%) | 14.5th (100 entries) |
| 2024 | Redwood Empire | all events | 2 of 54 entries made the final (4%) | 19.5th (52 entries) | 12 of 108 entries made the final (11%) | 15th (106 entries) |
| 2024 | Class A | all events | 3 of 28 entries made the final (11%) | 17th (26 entries) | 13 of 108 entries made the final (12%) | 15th (106 entries) |
| 2025 | Tri-Valley | all events | 16 of 57 entries made the final (28%) | 11th (55 entries) | 1 of 32 entries made the final (3%) | 16th (31 entries) |
| 2025 | Bay Shore | all events | 8 of 61 entries made the final (13%) | 18.5th (56 entries) | 10 of 115 entries made the final (9%) | 15th (107 entries) |
| 2025 | Redwood Empire | all events | 3 of 55 entries made the final (5%) | 18th (53 entries) | 11 of 101 entries made the final (11%) | 15th (93 entries) |
| 2025 | Class A | all events | 2 of 26 entries made the final (8%) | 17th (24 entries) | 11 of 112 entries made the final (10%) | 15th (105 entries) |
| 2026 | Tri-Valley | all events | 19 of 59 entries made the final (32%) | 10th (53 entries) | 2 of 36 entries made the final (6%) | 15th (34 entries) |
| 2026 | Bay Shore | all events | 4 of 60 entries made the final (7%) | 19th (58 entries) | 16 of 117 entries made the final (14%) | 15th (113 entries) |
| 2026 | Redwood Empire | all events | 6 of 56 entries made the final (11%) | 15th (54 entries) | 14 of 113 entries made the final (12%) | 15th (111 entries) |
| 2026 | Class A | all events | 1 of 28 entries made the final (4%) | 21th (25 entries) | 16 of 127 entries made the final (13%) | 15th (123 entries) |

**What the data shows.**
- **Bay Shore, Redwood Empire and Class A.** In most seasons, their lowest automatic
  qualifiers made the final *less* often than the other Areas' next-best-mark + at-large
  qualifiers, and had a worse median place.
  - Redwood Empire and Class A: lower in all 5 seasons.
  - Bay Shore: lower in 4 of 5 seasons; 2025 was the exception.
  - Several single-season gaps are small. In 2024, Bay Shore's lowest automatics had 7 of
    57 entries make the final, against 13 of 102 entries for the comparison group.
  - Each season's result rests on 0–8 finalists on the automatic side.
- **Tri-Valley.** The opposite, by a wide margin: 28–49% of its 5th–6th-place automatic
  entries made the final, against 3–18% of the other Areas' next-best-mark + at-large
  entries.
- **Who the comparison group is.** Tri-Valley holds most next-best-mark and at-large spots
  (§2), so for Bay Shore, Redwood Empire and Class A the comparison group is mostly
  Tri-Valley athletes. Across all five seasons, entries from next-best-mark + at-large
  qualifiers made the final as follows:
  - Tri-Valley: 61 of 406 entries (15%)
  - Redwood Empire: 10 of 79 entries (13%)
  - Bay Shore: 3 of 57 entries (5%)
  - Class A: 1 of 26 entries (4%)

**How confident can we be?** Pooled over five seasons, three tests:
- **Old test:** treats every athlete-event as independent.
- **Clustered test:** the same comparison, allowing for the same athlete appearing in
  several events or seasons.
- **Permutation test:** shuffles which Area each athlete belongs to, within each season,
  gender and event, 10,000 times, keeping each athlete's route fixed. It asks whether this
  Area's gap is bigger than random Area labels would give. Random labels themselves give a
  small positive gap, because lowest automatics usually do a little better than
  next-best-mark + at-large qualifiers overall.

| Area | Lowest automatics | Other Areas' next best mark + at-large | Gap | Old p (independent) | Clustered by athlete p | Gap if Areas were random | Permutation p |
|---|---|---|---|---|---|---|---|
| Tri-Valley | 106 of 293 entries made the final (36%) | 14 of 162 entries made the final (9%) | +27.5 percentage points | < 0.001 | < 0.001 | +3.7 percentage points | < 0.001 |
| Bay Shore | 25 of 284 entries made the final (9%) | 72 of 511 entries made the final (14%) | -5.3 percentage points | 0.029 | 0.018 | +2.4 percentage points | 0.001 |
| Redwood Empire | 22 of 277 entries made the final (8%) | 65 of 489 entries made the final (13%) | -5.3 percentage points | 0.025 | 0.017 | +3.3 percentage points | < 0.001 |
| Class A | 7 of 132 entries made the final (5%) | 74 of 542 entries made the final (14%) | -8.3 percentage points | 0.008 | < 0.001 | +2.4 percentage points | 0.003 |

**Reading the tests.**
- **Every result holds.** No Area's result weakens under the stronger tests; every
  p-value stays below 0.03.
- **Why the clustered p-values are a little smaller than the old ones.** Athletes rarely
  repeat (about 1.15 rows per athlete), so allowing for repeats changes little. The old
  test's pooled standard error is conservative when the two rates differ.
- **What the permutation test adds.** With random Area labels, a lowest-automatic group
  would be expected to make the final about 2–4 percentage points *more* often than the
  comparison group.
  - Bay Shore's, Redwood Empire's and Class A's lowest automatics instead did 5–8
    percentage points *worse*. Random labels almost never produce gaps that far out
    (p ≤ 0.003).
  - Tri-Valley's did 27 percentage points better, also far outside what random labels
    give.

**What the tests can't do.**
- **They don't explain the gap.** For example, they can't separate "the Area is weaker"
  from "that Area's 5th–6th-place athletes are younger" or "they ran other events that
  weekend".
- **They don't correct for multiple comparisons.** Four Areas are tested, plus event
  groups below. With p-values this small, a correction would not change the pooled
  conclusion.
- **Per-season and per-event-group results are much less certain** than the pooled ones.

**By event group (5 seasons pooled; single seasons are in `data/summary/core_comparison.csv`)**

| Season | Area (its lowest automatics) | Events | Lowest automatics: made the final | Lowest automatics: median MOC place | Other Areas' next best mark + at-large: made the final | Other Areas' next best mark + at-large: median MOC place |
|---|---|---|---|---|---|---|
| 2022-2026 pooled | Tri-Valley | sprints & hurdles | 29 of 74 entries made the final (39%) | 9th (72 entries) | 1 of 30 entries made the final (3%) | 15.5th (30 entries) |
| 2022-2026 pooled | Tri-Valley | 400/800 | 18 of 36 entries made the final (50%) | 8th (36 entries) | 0 of 20 entries made the final (0%) | 20th (20 entries) |
| 2022-2026 pooled | Tri-Valley | distance | 8 of 34 entries made the final (24%) | 11th (34 entries) | 3 of 25 entries made the final (12%) | 15th (25 entries) |
| 2022-2026 pooled | Tri-Valley | jumps | 23 of 72 entries made the final (32%) | 11th (62 entries) | 7 of 57 entries made the final (12%) | 15th (54 entries) |
| 2022-2026 pooled | Tri-Valley | throws | 14 of 39 entries made the final (36%) | 12th (39 entries) | 3 of 24 entries made the final (12%) | 16.5th (24 entries) |
| 2022-2026 pooled | Tri-Valley | relays | 14 of 38 entries made the final (37%) | 9th (36 entries) | 0 of 6 entries made the final (0%) | 15th (5 entries) |
| 2022-2026 pooled | Tri-Valley | all events | 106 of 293 entries made the final (36%) | 10th (279 entries) | 14 of 162 entries made the final (9%) | 16th (158 entries) |
| 2022-2026 pooled | Bay Shore | sprints & hurdles | 8 of 75 entries made the final (11%) | 18th (73 entries) | 11 of 146 entries made the final (8%) | 16th (144 entries) |
| 2022-2026 pooled | Bay Shore | 400/800 | 2 of 35 entries made the final (6%) | 19.5th (34 entries) | 10 of 76 entries made the final (13%) | 15th (74 entries) |
| 2022-2026 pooled | Bay Shore | distance | 2 of 37 entries made the final (5%) | 20th (37 entries) | 14 of 81 entries made the final (17%) | 16th (81 entries) |
| 2022-2026 pooled | Bay Shore | jumps | 11 of 66 entries made the final (17%) | 16th (53 entries) | 18 of 102 entries made the final (18%) | 13th (86 entries) |
| 2022-2026 pooled | Bay Shore | throws | 1 of 35 entries made the final (3%) | 19th (33 entries) | 10 of 51 entries made the final (20%) | 16th (51 entries) |
| 2022-2026 pooled | Bay Shore | relays | 1 of 36 entries made the final (3%) | 19.5th (34 entries) | 9 of 55 entries made the final (16%) | 13th (51 entries) |
| 2022-2026 pooled | Bay Shore | all events | 25 of 284 entries made the final (9%) | 18th (264 entries) | 72 of 511 entries made the final (14%) | 15th (487 entries) |
| 2022-2026 pooled | Redwood Empire | sprints & hurdles | 1 of 70 entries made the final (1%) | 20th (66 entries) | 12 of 154 entries made the final (8%) | 15.5th (152 entries) |
| 2022-2026 pooled | Redwood Empire | 400/800 | 1 of 32 entries made the final (3%) | 19th (31 entries) | 10 of 66 entries made the final (15%) | 14th (64 entries) |
| 2022-2026 pooled | Redwood Empire | distance | 3 of 37 entries made the final (8%) | 18th (37 entries) | 12 of 71 entries made the final (17%) | 16th (71 entries) |
| 2022-2026 pooled | Redwood Empire | jumps | 8 of 64 entries made the final (12%) | 14.5th (62 entries) | 15 of 107 entries made the final (14%) | 14th (92 entries) |
| 2022-2026 pooled | Redwood Empire | throws | 8 of 38 entries made the final (21%) | 14th (38 entries) | 7 of 33 entries made the final (21%) | 14th (33 entries) |
| 2022-2026 pooled | Redwood Empire | relays | 1 of 36 entries made the final (3%) | 18th (34 entries) | 9 of 58 entries made the final (16%) | 13.5th (54 entries) |
| 2022-2026 pooled | Redwood Empire | all events | 22 of 277 entries made the final (8%) | 17th (268 entries) | 65 of 489 entries made the final (13%) | 15th (466 entries) |
| 2022-2026 pooled | Class A | sprints & hurdles | 1 of 37 entries made the final (3%) | 20th (36 entries) | 12 of 153 entries made the final (8%) | 15th (151 entries) |
| 2022-2026 pooled | Class A | 400/800 | 2 of 15 entries made the final (13%) | 20th (14 entries) | 10 of 69 entries made the final (14%) | 15th (67 entries) |
| 2022-2026 pooled | Class A | distance | 3 of 17 entries made the final (18%) | 15th (16 entries) | 13 of 78 entries made the final (17%) | 16th (78 entries) |
| 2022-2026 pooled | Class A | jumps | 0 of 29 entries made the final (0%) | 18th (23 entries) | 20 of 130 entries made the final (15%) | 14th (113 entries) |
| 2022-2026 pooled | Class A | throws | 0 of 17 entries made the final (0%) | 18.5th (16 entries) | 10 of 54 entries made the final (19%) | 15.5th (54 entries) |
| 2022-2026 pooled | Class A | relays | 1 of 17 entries made the final (6%) | 19th (17 entries) | 9 of 58 entries made the final (16%) | 14th (55 entries) |
| 2022-2026 pooled | Class A | all events | 7 of 132 entries made the final (5%) | 19.5th (122 entries) | 74 of 542 entries made the final (14%) | 15th (518 entries) |

By event group the counts get small (often 15–40 entries on the automatic side), so treat
these as indications. The dashboard's "Area place vs. MOC finish" tab shows every Area
place from 1st to 12th.

## 5. Left-out athletes

The current system rarely excludes an athlete whose Area mark would have made the MOC
final: 6 cases in 5 seasons, all 2023 Tri-Valley. We took each Area's three best
non-qualifiers per event, by Area mark, and compared that mark with the MOC cutoff: the
mark of the 8th-best MOC finisher (9th in the long jump, triple jump, shot put and discus),
taking each athlete's best mark from any MOC round. The marks come from different meets
(wind, weather, competition), so this is a comparison, not a prediction.

## 6. Spot use

**Guaranteed spots only** (automatic + next best mark; 24 per event). Each spot falls in
exactly one segment:
- **Competed:** the qualifier ran the event at the MOC.
- **Refilled:** the qualifier withdrew before the deadline and the next finalist from that
  Area took the spot.
- **Chose another event:** the qualifier competed at the MOC, but in other events.
- **Didn't enter:** the qualifier was not at the MOC at all.
- **Unfilled (provisional, under verification):** nobody used the spot and the event field
  ended up short (below 24 athletes or teams competing).

**Guaranteed spots used** = (competed + refilled) ÷ guaranteed spots. At-large standard
qualifiers have no fixed number of spots, so they are reported separately and are in
neither the segments nor the %.

**What the data shows.**
- **Used:** 3,661 of 3,890 guaranteed spots (94%) over five seasons: 3,515 competed and 146
  refilled. By Area and season, 89–98% of guaranteed spots were used.
- **Not used:** 70 qualifiers chose another event, 38 didn't enter, and 121 spots were
  unfilled (provisional; 1–6% of guaranteed spots per Area and season).
- **At-large standard qualifiers:** 134 over five seasons; 116 competed, 17 chose another
  event, 1 didn't enter.
- **No-shows:** 1–6% of entries.
- **Flag list.** 4 Area × event combinations had unfilled spots in 3 or more of the 5
  seasons, each with 4–5 unfilled spots in total. Counting any unused spot gives 51
  combinations.

**Why "unfilled" is still provisional.** A spot-by-spot check (decision #28) found three
open questions:
- **Unfilled spots ≠ empty places.** The 121 unfilled spots sit in events whose fields
  fell a total of 86 places short of 24; in 23 events at-large qualifiers took some of the
  lanes.
- **Refills further down the line aren't credited.** In 11 cases a lower finalist from the
  same Area ran the event, but wasn't next in line, so the spot above them counts as unfilled.
- **Refilled, then no-show.** 7 replacements didn't compete; those spots count as refilled.

| Season | Area | Guaranteed spots | Competed | Refilled | Chose another event | Didn't enter | Unfilled (provisional) | Guaranteed spots used | At-large standard (separate) | No-shows |
|---|---|---|---|---|---|---|---|---|---|---|
| 2022 | Bay Shore | 198 spots | 182 | 10 | 0 | 3 | 3 | 192 of 198 guaranteed spots used (97%) | 2 qualifiers: 2 competed, 0 chose another event, 0 didn't enter | 6 of 190 entries (3%) |
| 2022 | Class A | 98 spots | 85 | 8 | 3 | 0 | 2 | 93 of 98 guaranteed spots used (95%) | none | 1 of 86 entries (1%) |
| 2022 | Redwood Empire | 212 spots | 180 | 11 | 5 | 3 | 13 | 191 of 212 guaranteed spots used (90%) | none | 3 of 183 entries (2%) |
| 2022 | Tri-Valley | 268 spots | 248 | 5 | 2 | 2 | 11 | 253 of 268 guaranteed spots used (94%) | 2 qualifiers: 2 competed, 0 chose another event, 0 didn't enter | 8 of 258 entries (3%) |
| 2023 | Bay Shore | 207 spots | 181 | 7 | 6 | 2 | 11 | 188 of 207 guaranteed spots used (91%) | 2 qualifiers: 2 competed, 0 chose another event, 0 didn't enter | 10 of 193 entries (5%) |
| 2023 | Class A | 100 spots | 85 | 8 | 0 | 2 | 5 | 93 of 100 guaranteed spots used (93%) | 1 qualifiers: 1 competed, 0 chose another event, 0 didn't enter | 5 of 91 entries (5%) |
| 2023 | Redwood Empire | 216 spots | 198 | 5 | 3 | 0 | 10 | 203 of 216 guaranteed spots used (94%) | 1 qualifiers: 1 competed, 0 chose another event, 0 didn't enter | 10 of 209 entries (5%) |
| 2023 | Tri-Valley | 263 spots | 235 | 9 | 11 | 3 | 5 | 244 of 263 guaranteed spots used (93%) | 17 qualifiers: 14 competed, 3 chose another event, 0 didn't enter | 3 of 252 entries (1%) |
| 2024 | Bay Shore | 207 spots | 186 | 5 | 1 | 3 | 12 | 191 of 207 guaranteed spots used (92%) | 3 qualifiers: 2 competed, 1 chose another event, 0 didn't enter | 13 of 201 entries (6%) |
| 2024 | Class A | 103 spots | 89 | 7 | 3 | 2 | 2 | 96 of 103 guaranteed spots used (93%) | 5 qualifiers: 4 competed, 1 chose another event, 0 didn't enter | 1 of 94 entries (1%) |
| 2024 | Redwood Empire | 201 spots | 183 | 10 | 2 | 2 | 4 | 193 of 201 guaranteed spots used (96%) | 2 qualifiers: 2 competed, 0 chose another event, 0 didn't enter | 4 of 189 entries (2%) |
| 2024 | Tri-Valley | 266 spots | 248 | 4 | 6 | 1 | 7 | 252 of 266 guaranteed spots used (95%) | 26 qualifiers: 21 competed, 5 chose another event, 0 didn't enter | 3 of 272 entries (1%) |
| 2025 | Bay Shore | 196 spots | 180 | 10 | 3 | 2 | 1 | 190 of 196 guaranteed spots used (97%) | 1 qualifiers: 1 competed, 0 chose another event, 0 didn't enter | 4 of 185 entries (2%) |
| 2025 | Class A | 102 spots | 86 | 5 | 3 | 3 | 5 | 91 of 102 guaranteed spots used (89%) | 3 qualifiers: 3 competed, 0 chose another event, 0 didn't enter | 6 of 95 entries (6%) |
| 2025 | Redwood Empire | 209 spots | 190 | 12 | 0 | 2 | 5 | 202 of 209 guaranteed spots used (97%) | 7 qualifiers: 5 competed, 2 chose another event, 0 didn't enter | 4 of 199 entries (2%) |
| 2025 | Tri-Valley | 269 spots | 248 | 6 | 9 | 2 | 4 | 254 of 269 guaranteed spots used (94%) | 19 qualifiers: 19 competed, 0 chose another event, 0 didn't enter | 3 of 270 entries (1%) |
| 2026 | Bay Shore | 204 spots | 196 | 3 | 1 | 0 | 4 | 199 of 204 guaranteed spots used (98%) | 3 qualifiers: 2 competed, 1 chose another event, 0 didn't enter | 4 of 202 entries (2%) |
| 2026 | Class A | 98 spots | 85 | 5 | 2 | 0 | 6 | 90 of 98 guaranteed spots used (92%) | 3 qualifiers: 2 competed, 0 chose another event, 1 didn't enter | 6 of 93 entries (6%) |
| 2026 | Redwood Empire | 209 spots | 184 | 9 | 7 | 3 | 6 | 193 of 209 guaranteed spots used (92%) | 7 qualifiers: 6 competed, 1 chose another event, 0 didn't enter | 3 of 193 entries (2%) |
| 2026 | Tri-Valley | 264 spots | 246 | 7 | 3 | 3 | 5 | 253 of 264 guaranteed spots used (96%) | 30 qualifiers: 27 competed, 3 chose another event, 0 didn't enter | 4 of 277 entries (1%) |

**Area × event with unfilled spots in 3 or more of the 5 seasons: 4 combinations**

| Area | Gender | Event | Seasons | Which | Total over 5 seasons |
|---|---|---|---|---|---|
| Tri-Valley | girls | 3200 | 4 seasons | 2022, 2024, 2025, 2026 | 4 unfilled spots |
| Bay Shore | girls | SP | 3 seasons | 2022, 2023, 2024 | 5 unfilled spots |
| Bay Shore | boys | LJ | 3 seasons | 2023, 2024, 2025 | 4 unfilled spots |
| Bay Shore | girls | LJ | 3 seasons | 2022, 2024, 2026 | 4 unfilled spots |

**Area × event with any unused spot in 3 or more of the 5 seasons: 51 combinations**

| Area | Gender | Event | Seasons | Which | Total over 5 seasons |
|---|---|---|---|---|---|
| Redwood Empire | girls | 200 | 5 seasons | 2022, 2023, 2024, 2025, 2026 | 10 unused spots |
| Tri-Valley | boys | 1600 | 5 seasons | 2022, 2023, 2024, 2025, 2026 | 9 unused spots |
| Tri-Valley | girls | 800 | 5 seasons | 2022, 2023, 2024, 2025, 2026 | 7 unused spots |
| Redwood Empire | boys | 200 | 5 seasons | 2022, 2023, 2024, 2025, 2026 | 6 unused spots |
| Tri-Valley | boys | 800 | 4 seasons | 2023, 2024, 2025, 2026 | 10 unused spots |
| Tri-Valley | girls | 1600 | 4 seasons | 2022, 2023, 2024, 2025 | 10 unused spots |
| Tri-Valley | girls | 400 | 4 seasons | 2023, 2024, 2025, 2026 | 10 unused spots |
| Tri-Valley | girls | HJ | 4 seasons | 2022, 2023, 2024, 2026 | 10 unused spots |
| Bay Shore | boys | 800 | 4 seasons | 2023, 2024, 2025, 2026 | 7 unused spots |
| Bay Shore | girls | 1600 | 4 seasons | 2022, 2023, 2024, 2025 | 7 unused spots |
| Class A | girls | 1600 | 4 seasons | 2022, 2023, 2024, 2026 | 7 unused spots |
| Redwood Empire | girls | LJ | 4 seasons | 2022, 2023, 2024, 2025 | 7 unused spots |
| Tri-Valley | girls | 200 | 4 seasons | 2022, 2023, 2025, 2026 | 7 unused spots |
| Bay Shore | boys | 200 | 4 seasons | 2022, 2023, 2024, 2026 | 6 unused spots |
| Bay Shore | boys | LJ | 4 seasons | 2023, 2024, 2025, 2026 | 6 unused spots |
| Bay Shore | girls | 800 | 4 seasons | 2022, 2023, 2024, 2026 | 6 unused spots |
| Bay Shore | girls | LJ | 4 seasons | 2022, 2023, 2024, 2026 | 6 unused spots |
| Class A | boys | 1600 | 4 seasons | 2022, 2023, 2024, 2026 | 6 unused spots |
| Class A | girls | 800 | 4 seasons | 2023, 2024, 2025, 2026 | 6 unused spots |
| Redwood Empire | boys | PV | 4 seasons | 2022, 2023, 2024, 2026 | 6 unused spots |
| Redwood Empire | girls | 400 | 4 seasons | 2022, 2024, 2025, 2026 | 6 unused spots |
| Redwood Empire | boys | LJ | 4 seasons | 2022, 2024, 2025, 2026 | 5 unused spots |
| Class A | boys | 200 | 4 seasons | 2022, 2023, 2025, 2026 | 4 unused spots |
| Class A | boys | LJ | 4 seasons | 2022, 2023, 2024, 2026 | 4 unused spots |
| Redwood Empire | boys | 400 | 4 seasons | 2022, 2024, 2025, 2026 | 4 unused spots |
| Redwood Empire | boys | TJ | 4 seasons | 2023, 2024, 2025, 2026 | 4 unused spots |
| Redwood Empire | girls | DT | 4 seasons | 2022, 2023, 2025, 2026 | 4 unused spots |
| Tri-Valley | girls | 3200 | 4 seasons | 2022, 2024, 2025, 2026 | 4 unused spots |
| Redwood Empire | boys | 800 | 3 seasons | 2024, 2025, 2026 | 7 unused spots |
| Tri-Valley | boys | 200 | 3 seasons | 2023, 2025, 2026 | 7 unused spots |
| Bay Shore | boys | 300H | 3 seasons | 2023, 2024, 2025 | 6 unused spots |
| Bay Shore | girls | SP | 3 seasons | 2022, 2023, 2024 | 6 unused spots |
| Redwood Empire | boys | 1600 | 3 seasons | 2023, 2025, 2026 | 6 unused spots |
| Redwood Empire | girls | TJ | 3 seasons | 2022, 2024, 2026 | 6 unused spots |
| Bay Shore | boys | 1600 | 3 seasons | 2022, 2024, 2026 | 5 unused spots |
| Bay Shore | girls | DT | 3 seasons | 2022, 2023, 2024 | 5 unused spots |
| Redwood Empire | boys | HJ | 3 seasons | 2023, 2024, 2026 | 5 unused spots |
| Tri-Valley | girls | LJ | 3 seasons | 2023, 2025, 2026 | 5 unused spots |
| Bay Shore | girls | 4x400 | 3 seasons | 2023, 2025, 2026 | 4 unused spots |
| Redwood Empire | boys | 4x400 | 3 seasons | 2024, 2025, 2026 | 4 unused spots |
| Redwood Empire | girls | 1600 | 3 seasons | 2022, 2023, 2024 | 4 unused spots |
| Tri-Valley | boys | LJ | 3 seasons | 2022, 2023, 2024 | 4 unused spots |
| Tri-Valley | girls | 100H | 3 seasons | 2022, 2023, 2026 | 4 unused spots |
| Class A | boys | 4x400 | 3 seasons | 2022, 2024, 2025 | 3 unused spots |
| Class A | boys | HJ | 3 seasons | 2023, 2025, 2026 | 3 unused spots |
| Class A | boys | TJ | 3 seasons | 2022, 2023, 2026 | 3 unused spots |
| Class A | girls | 3200 | 3 seasons | 2022, 2023, 2026 | 3 unused spots |
| Class A | girls | TJ | 3 seasons | 2023, 2024, 2025 | 3 unused spots |
| Redwood Empire | boys | 110H | 3 seasons | 2022, 2023, 2026 | 3 unused spots |
| Redwood Empire | girls | 100 | 3 seasons | 2022, 2025, 2026 | 3 unused spots |
| Redwood Empire | girls | HJ | 3 seasons | 2023, 2024, 2025 | 3 unused spots |

## 7. Limits of this analysis

- **Small samples.** Many groups hold a handful of entries: next-best-mark and at-large
  qualifiers outside Tri-Valley, Class A in general, and any single event. A few athletes
  can move a rate by 10–30 percentage points. Where the text says "consistent", it means
  the same direction across seasons, not a precisely measured gap.
- **Comparing marks across meets.** Section 5 compares marks made at different meets, with
  different wind, weather, heats and competition.
- **Statistical tests.** The §4 p-values are pooled over five seasons and all events. They
  support a consistent direction, not a precise gap, and say nothing about causes.
- **Unfilled spots are provisional.** See §6 for the three open questions.
- **Rules before 2026 are partly assumed.**
  - Allocation numbers for 2022–2025 are assumed to equal 2026's.
  - Each season's at-large standards come from its printed results, except 2023, where
    none were printed and 2026's are used.
- **Unresolved school names.** "West County" (2022, 12 program entries) is kept unmatched
  pending confirmation that it is Analy. A few truncated names are also unmatched (15
  entries in 2022, 5 in 2023). These appear as "Unknown" and aren't compared.
- **Privacy.** MOC-place figures (made-the-final counts, medians) are published only for groups of 5
  or more entries.
- **State results pending.** State qualification isn't included yet.
- **What the rules replay can't see.** Scratches after the program was printed, why an
  athlete chose one event over another, and whether a vacancy was offered and declined.
- **Replacements.** Only replacements from the same Area are recognised; that setting
  matched the programs best.

## 5-season pooled summary (2022–2026 combined)

*Pooling combines different seasons, rule details and fields. Use it for the overall
picture only; the per-season tables above are primary.*

| Area | Share of all qualifiers | Next-best-mark + at-large spots held | Automatic: made the final | Next best mark + at-large: made the final | Lowest automatics vs other Areas' next best mark + at-large: made the final | Unfilled spots (provisional) | No-shows |
|---|---|---|---|---|---|---|---|
| Tri-Valley | 1424 of 4024 MOC spots (35%) | 464 of 659 next-best-mark + at-large spots (70%) | 576 of 902 entries made the final (64%) | 61 of 406 entries made the final (15%) | 106 of 293 entries made the final (36%) vs 14 of 162 entries made the final (9%) | 32 of 1330 guaranteed spots unfilled (2%) | 21 of 1329 entries were no-shows (2%) |
| Bay Shore | 1023 of 4024 MOC spots (25%) | 61 of 659 next-best-mark + at-large spots (9%) | 285 of 877 entries made the final (32%) | 3 of 57 entries made the final (5%) | 25 of 284 entries made the final (9%) vs 72 of 511 entries made the final (14%) | 31 of 1012 guaranteed spots unfilled (3%) | 37 of 971 entries were no-shows (4%) |
| Redwood Empire | 1064 of 4024 MOC spots (26%) | 102 of 659 next-best-mark + at-large spots (15%) | 263 of 870 entries made the final (30%) | 10 of 79 entries made the final (13%) | 22 of 277 entries made the final (8%) vs 65 of 489 entries made the final (13%) | 38 of 1047 guaranteed spots unfilled (4%) | 24 of 973 entries were no-shows (2%) |
| Class A | 513 of 4024 MOC spots (13%) | 32 of 659 next-best-mark + at-large spots (5%) | 87 of 414 entries made the final (21%) | 1 of 26 entries made the final (4%) | 7 of 132 entries made the final (5%) vs 74 of 542 entries made the final (14%) | 20 of 501 guaranteed spots unfilled (4%) | 19 of 459 entries were no-shows (4%) |
