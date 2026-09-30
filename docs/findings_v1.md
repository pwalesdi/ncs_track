# What the data shows: MOC qualification by Area, 2022–2026 (findings v1)

*For coaches and the committee. Built from the tables in `data/summary/`; every column is defined in
`docs/analysis_tables.md`. Every number carries its unit, e.g. "25 of 284 entries made the final (9%)".*

> **What changed in this update (2026-09-30, fourth update)**
> - **Routes are now assigned after declarations ("pass-down").** When a finisher declines,
>   her automatic spot passes down to the next finisher from her Area; the next-best-mark
>   spots then go to the best remaining marks. "Actual entries" use these routes;
>   "All qualifiers" keeps the pre-declaration replay. The replay now reproduces 99.5–100%
>   of real MOC entries per season (was 97.9–99.1%). Checked by hand on the 2025 girls 1600.
> - **§4 changes.** With pass-down routes, Bay Shore's and Redwood Empire's lowest
>   automatics trail the comparison group by about 4 percentage points (was 5–8), and their
>   independent and athlete-clustered p-values are 0.05–0.07 (were ≤ 0.03). The permutation
>   test still puts all three Areas far outside random labels (p ≤ 0.003). Class A's result
>   holds on every test.
> - **§5, left out** is redefined: finished behind her Area's last automatic qualifier and not
>   entered; compared with other Areas' automatic qualifiers.
> - **§6, spot use** now counts no-shows: entered the event but didn't compete. Declines
>   aren't no-shows, and field size no longer plays any part. "Unfilled" is retired.
>
> **Earlier updates (same day):** "top 8" became "made the final"; MOC-place figures only for
> groups of 5 or more; "at-large" means only the at-large standard; §4 permutation and
> athlete-clustered tests.

## How to read this

- **Seasons.** 2022, 2023, 2024, 2025 and 2026, each shown on its own. A 5-season pooled
  summary is at the end, clearly labelled.
- **Areas.** The four MOC qualifying meets: Tri-Valley, Bay Shore, Redwood Empire and
  Class A.
- **How athletes reach the MOC** (routes are assigned after athletes declare):
  - **Automatic:** each Area's 6 automatic spots (Class A: 3) go to its top finishers who
    entered, in Area-place order. If a finisher declines, the spot passes down to the next
    finisher, so a 7th–10th-place finisher can be an automatic qualifier.
  - **Next best mark:** after declarations, the 3 spots per event go to the best remaining
    Area-final marks across all four meets.
  - **At-large:** anyone else remaining who met the posted at-large standard in the Area
    final. Only these athletes are called at-large here.
  - **Next best mark + at-large standard:** the two routes together.
  - **Declined:** finished ahead of her Area's last automatic qualifier but didn't enter.
- **Guaranteed spots.** Per Area and event: its automatic spots plus the next-best-mark spots
  it won. At-large spots come on top and have no fixed number.
- **Two fields.**
  - **All qualifiers:** who the rules made eligible before anyone declared (a replay of each
    season's rules against the Area results).
  - **Actual entries:** athletes in the MOC program, on the routes they actually took. The
    pass-down replay reproduces 99.5–100% of these entries per season.
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
- **Tri-Valley** holds 35–36% of all qualifiers every season, with 78–102 next-best-mark +
  at-large qualifiers a season (actual entries: 34–36%, 72–95).
- **Bay Shore** holds 24–26%, with 5–17 such qualifiers (entries: 25–26%, 5–17).
- **Redwood Empire** holds 25–27%, with 11–25 (entries: 26–27%, 14–23).
- **Class A** holds 12–13%, with 3–10 (entries: 13%, 4–8).

With pass-down, a declined automatic spot is re-filled from the same Area, so each Area's
automatic entries stay at about its quota. "Unknown" rows are program entries whose school
couldn't be matched (see §7).

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

| Season | Area | Share of MOC spots | Automatic | Next best mark | At-large standard | Unexplained |
|---|---|---|---|---|---|---|
| 2022 | Tri-Valley | 266 of 776 MOC spots (34%) | 192 spots | 72 spots | 2 spots | 0 spots |
| 2022 | Bay Shore | 202 of 776 MOC spots (26%) | 192 spots | 8 spots | 2 spots | 0 spots |
| 2022 | Redwood Empire | 206 of 776 MOC spots (27%) | 191 spots | 15 spots | 0 spots | 0 spots |
| 2022 | Class A | 99 of 776 MOC spots (13%) | 95 spots | 4 spots | 0 spots | 0 spots |
| 2022 | Unknown | 3 of 776 MOC spots (0%) | 0 spots | 0 spots | 0 spots | 3 spots |
| 2023 | Tri-Valley | 268 of 789 MOC spots (34%) | 192 spots | 65 spots | 7 spots | 4 spots |
| 2023 | Bay Shore | 204 of 789 MOC spots (26%) | 191 spots | 13 spots | 0 spots | 0 spots |
| 2023 | Redwood Empire | 215 of 789 MOC spots (27%) | 192 spots | 23 spots | 0 spots | 0 spots |
| 2023 | Class A | 99 of 789 MOC spots (13%) | 94 spots | 4 spots | 1 spots | 0 spots |
| 2023 | Unknown | 3 of 789 MOC spots (0%) | 0 spots | 0 spots | 0 spots | 3 spots |
| 2024 | Tri-Valley | 277 of 798 MOC spots (35%) | 192 spots | 70 spots | 15 spots | 0 spots |
| 2024 | Bay Shore | 210 of 798 MOC spots (26%) | 193 spots | 16 spots | 1 spots | 0 spots |
| 2024 | Redwood Empire | 207 of 798 MOC spots (26%) | 192 spots | 14 spots | 0 spots | 1 spots |
| 2024 | Class A | 104 of 798 MOC spots (13%) | 95 spots | 4 spots | 4 spots | 1 spots |
| 2025 | Tri-Valley | 277 of 789 MOC spots (35%) | 192 spots | 75 spots | 10 spots | 0 spots |
| 2025 | Bay Shore | 197 of 789 MOC spots (25%) | 192 spots | 4 spots | 1 spots | 0 spots |
| 2025 | Redwood Empire | 212 of 789 MOC spots (27%) | 195 spots | 15 spots | 2 spots | 0 spots |
| 2025 | Class A | 103 of 789 MOC spots (13%) | 96 spots | 6 spots | 1 spots | 0 spots |
| 2026 | Tri-Valley | 287 of 804 MOC spots (36%) | 192 spots | 76 spots | 19 spots | 0 spots |
| 2026 | Bay Shore | 207 of 804 MOC spots (26%) | 192 spots | 12 spots | 3 spots | 0 spots |
| 2026 | Redwood Empire | 209 of 804 MOC spots (26%) | 192 spots | 14 spots | 3 spots | 0 spots |
| 2026 | Class A | 101 of 804 MOC spots (13%) | 96 spots | 2 spots | 3 spots | 0 spots |

## 2. Next-best-mark and at-large spots by Area

**What the data shows.** Tri-Valley athletes took most of these spots in every season, before
and after declarations.
- **All qualifiers (before declarations):** 63–75% of next-best-mark spots, 50–81% of
  at-large spots, 66–73% of the two together; 464 of 659 over five seasons (70%).
- **Actual entries (pass-down routes):** 62–75% of next-best-mark spots, 50–88% of at-large
  spots, 64–75% together; 411 of 586 over five seasons (70%).
- **Pass-down barely moves the share.** When a Tri-Valley finisher declines, the next
  Tri-Valley finisher takes the automatic spot, and the next-best-mark spots still go to the
  best remaining marks, which are mostly Tri-Valley's.

Caveats:
- **2022 at-large spots are few** (4 athletes), so those percentages rest on 4 athletes.
- **At-large spots are few by construction.** Next-best-mark spots are assigned first.

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
| 2022 | Tri-Valley | 72 of 99 next-best-mark spots (73%) | 2 of 4 at-large spots (50%) | 74 of 103 next-best-mark + at-large spots (72%) |
| 2022 | Bay Shore | 8 of 99 next-best-mark spots (8%) | 2 of 4 at-large spots (50%) | 10 of 103 next-best-mark + at-large spots (10%) |
| 2022 | Redwood Empire | 15 of 99 next-best-mark spots (15%) | 0 of 4 at-large spots (0%) | 15 of 103 next-best-mark + at-large spots (15%) |
| 2022 | Class A | 4 of 99 next-best-mark spots (4%) | 0 of 4 at-large spots (0%) | 4 of 103 next-best-mark + at-large spots (4%) |
| 2023 | Tri-Valley | 65 of 105 next-best-mark spots (62%) | 7 of 8 at-large spots (88%) | 72 of 113 next-best-mark + at-large spots (64%) |
| 2023 | Bay Shore | 13 of 105 next-best-mark spots (12%) | 0 of 8 at-large spots (0%) | 13 of 113 next-best-mark + at-large spots (12%) |
| 2023 | Redwood Empire | 23 of 105 next-best-mark spots (22%) | 0 of 8 at-large spots (0%) | 23 of 113 next-best-mark + at-large spots (20%) |
| 2023 | Class A | 4 of 105 next-best-mark spots (4%) | 1 of 8 at-large spots (12%) | 5 of 113 next-best-mark + at-large spots (4%) |
| 2024 | Tri-Valley | 70 of 104 next-best-mark spots (67%) | 15 of 20 at-large spots (75%) | 85 of 124 next-best-mark + at-large spots (69%) |
| 2024 | Bay Shore | 16 of 104 next-best-mark spots (15%) | 1 of 20 at-large spots (5%) | 17 of 124 next-best-mark + at-large spots (14%) |
| 2024 | Redwood Empire | 14 of 104 next-best-mark spots (13%) | 0 of 20 at-large spots (0%) | 14 of 124 next-best-mark + at-large spots (11%) |
| 2024 | Class A | 4 of 104 next-best-mark spots (4%) | 4 of 20 at-large spots (20%) | 8 of 124 next-best-mark + at-large spots (6%) |
| 2025 | Tri-Valley | 75 of 100 next-best-mark spots (75%) | 10 of 14 at-large spots (71%) | 85 of 114 next-best-mark + at-large spots (75%) |
| 2025 | Bay Shore | 4 of 100 next-best-mark spots (4%) | 1 of 14 at-large spots (7%) | 5 of 114 next-best-mark + at-large spots (4%) |
| 2025 | Redwood Empire | 15 of 100 next-best-mark spots (15%) | 2 of 14 at-large spots (14%) | 17 of 114 next-best-mark + at-large spots (15%) |
| 2025 | Class A | 6 of 100 next-best-mark spots (6%) | 1 of 14 at-large spots (7%) | 7 of 114 next-best-mark + at-large spots (6%) |
| 2026 | Tri-Valley | 76 of 104 next-best-mark spots (73%) | 19 of 28 at-large spots (68%) | 95 of 132 next-best-mark + at-large spots (72%) |
| 2026 | Bay Shore | 12 of 104 next-best-mark spots (12%) | 3 of 28 at-large spots (11%) | 15 of 132 next-best-mark + at-large spots (11%) |
| 2026 | Redwood Empire | 14 of 104 next-best-mark spots (13%) | 3 of 28 at-large spots (11%) | 17 of 132 next-best-mark + at-large spots (13%) |
| 2026 | Class A | 2 of 104 next-best-mark spots (2%) | 3 of 28 at-large spots (11%) | 5 of 132 next-best-mark + at-large spots (4%) |

## 3. MOC results by Area and route

Entries that competed at the MOC, on their pass-down routes. To keep the table readable,
only automatic and next best mark + at-large standard qualifiers are shown; the full
breakdown is in `data/summary/moc_performance.csv`.

**What the data shows.**
- **Automatic qualifiers.** Tri-Valley's made the final in 59–64% of entries each season.
  Bay Shore's did in 30–32%, Redwood Empire's in 24–31%, and Class A's in 8–29%.
- **Class A varies most:** 7 of 91 entries made the final in 2026 (8%), but 27 of 94 in
  2024 (29%).
- **Next best mark + at-large qualifiers** made the final far less often than automatic
  qualifiers, in every Area and season. Outside Tri-Valley these groups are small, often
  under 20 entries, so their rates move a lot with one or two athletes.

| Season | Area | Route | Made the final | Scored (top 6) |
|---|---|---|---|---|
| 2022 | Tri-Valley | Automatic | 119 of 187 entries made the final (64%) | 91 of 187 entries scored (top 6) (49%) |
| 2022 | Tri-Valley | Next best mark + at-large standard | 19 of 71 entries made the final (27%) | 8 of 71 entries scored (top 6) (11%) |
| 2022 | Bay Shore | Automatic | 56 of 186 entries made the final (30%) | 43 of 186 entries scored (top 6) (23%) |
| 2022 | Bay Shore | Next best mark + at-large standard | 0 of 10 entries made the final (0%) | 0 of 10 entries scored (top 6) (0%) |
| 2022 | Redwood Empire | Automatic | 56 of 187 entries made the final (30%) | 44 of 187 entries scored (top 6) (24%) |
| 2022 | Redwood Empire | Next best mark + at-large standard | 4 of 14 entries made the final (29%) | 1 of 14 entries scored (top 6) (7%) |
| 2022 | Class A | Automatic | 9 of 94 entries made the final (10%) | 9 of 94 entries scored (top 6) (10%) |
| 2022 | Class A | Next best mark + at-large standard | 3 entries (fewer than 5: not shown) | 3 entries (fewer than 5: not shown) |
| 2023 | Tri-Valley | Automatic | 118 of 192 entries made the final (61%) | 91 of 192 entries scored (top 6) (47%) |
| 2023 | Tri-Valley | Next best mark + at-large standard | 3 of 68 entries made the final (4%) | 1 of 68 entries scored (top 6) (1%) |
| 2023 | Bay Shore | Automatic | 56 of 181 entries made the final (31%) | 45 of 181 entries scored (top 6) (25%) |
| 2023 | Bay Shore | Next best mark + at-large standard | 1 of 12 entries made the final (8%) | 1 of 12 entries scored (top 6) (8%) |
| 2023 | Redwood Empire | Automatic | 53 of 185 entries made the final (29%) | 37 of 185 entries scored (top 6) (20%) |
| 2023 | Redwood Empire | Next best mark + at-large standard | 3 of 20 entries made the final (15%) | 2 of 20 entries scored (top 6) (10%) |
| 2023 | Class A | Automatic | 26 of 90 entries made the final (29%) | 17 of 90 entries scored (top 6) (19%) |
| 2023 | Class A | Next best mark + at-large standard | 4 entries (fewer than 5: not shown) | 4 entries (fewer than 5: not shown) |
| 2024 | Tri-Valley | Automatic | 120 of 191 entries made the final (63%) | 95 of 191 entries scored (top 6) (50%) |
| 2024 | Tri-Valley | Next best mark + at-large standard | 11 of 82 entries made the final (13%) | 9 of 82 entries scored (top 6) (11%) |
| 2024 | Bay Shore | Automatic | 55 of 181 entries made the final (30%) | 36 of 181 entries scored (top 6) (20%) |
| 2024 | Bay Shore | Next best mark + at-large standard | 1 of 16 entries made the final (6%) | 0 of 16 entries scored (top 6) (0%) |
| 2024 | Redwood Empire | Automatic | 46 of 189 entries made the final (24%) | 33 of 189 entries scored (top 6) (17%) |
| 2024 | Redwood Empire | Next best mark + at-large standard | 1 of 10 entries made the final (10%) | 0 of 10 entries scored (top 6) (0%) |
| 2024 | Class A | Automatic | 27 of 94 entries made the final (29%) | 21 of 94 entries scored (top 6) (22%) |
| 2024 | Class A | Next best mark + at-large standard | 0 of 8 entries made the final (0%) | 0 of 8 entries scored (top 6) (0%) |
| 2025 | Tri-Valley | Automatic | 114 of 189 entries made the final (60%) | 92 of 189 entries scored (top 6) (49%) |
| 2025 | Tri-Valley | Next best mark + at-large standard | 9 of 84 entries made the final (11%) | 4 of 84 entries scored (top 6) (5%) |
| 2025 | Bay Shore | Automatic | 60 of 187 entries made the final (32%) | 44 of 187 entries scored (top 6) (24%) |
| 2025 | Bay Shore | Next best mark + at-large standard | 1 of 5 entries made the final (20%) | 0 of 5 entries scored (top 6) (0%) |
| 2025 | Redwood Empire | Automatic | 54 of 193 entries made the final (28%) | 40 of 193 entries scored (top 6) (21%) |
| 2025 | Redwood Empire | Next best mark + at-large standard | 0 of 14 entries made the final (0%) | 0 of 14 entries scored (top 6) (0%) |
| 2025 | Class A | Automatic | 20 of 91 entries made the final (22%) | 14 of 91 entries scored (top 6) (15%) |
| 2025 | Class A | Next best mark + at-large standard | 0 of 7 entries made the final (0%) | 0 of 7 entries scored (top 6) (0%) |
| 2026 | Tri-Valley | Automatic | 113 of 190 entries made the final (59%) | 88 of 190 entries scored (top 6) (46%) |
| 2026 | Tri-Valley | Next best mark + at-large standard | 14 of 93 entries made the final (15%) | 6 of 93 entries scored (top 6) (6%) |
| 2026 | Bay Shore | Automatic | 61 of 189 entries made the final (32%) | 53 of 189 entries scored (top 6) (28%) |
| 2026 | Bay Shore | Next best mark + at-large standard | 0 of 14 entries made the final (0%) | 0 of 14 entries scored (top 6) (0%) |
| 2026 | Redwood Empire | Automatic | 59 of 188 entries made the final (31%) | 41 of 188 entries scored (top 6) (22%) |
| 2026 | Redwood Empire | Next best mark + at-large standard | 1 of 16 entries made the final (6%) | 1 of 16 entries scored (top 6) (6%) |
| 2026 | Class A | Automatic | 7 of 91 entries made the final (8%) | 5 of 91 entries scored (top 6) (5%) |
| 2026 | Class A | Next best mark + at-large standard | 4 entries (fewer than 5: not shown) | 4 entries (fewer than 5: not shown) |

## 4. The core question: do some Areas' last automatic qualifiers do worse at the MOC than other Areas' next-best-mark + at-large qualifiers?

**The comparison.**
- **Lowest automatic qualifiers:** each Area's automatic qualifiers who placed 5th or 6th
  at their Area meet (3rd for Class A). With pass-down these are always automatic.
- **Next best mark + at-large qualifiers from the other three Areas** (pass-down routes).
- **Who is counted:** only entries that competed at the MOC, with genders combined.

**Two measures.**
- **Made-the-final rate.**
- **Median MOC place.** Finalists keep their final place; everyone else is ranked after the
  finalists by their best MOC mark. Lower is better.

Groups under 5 entries show counts only.

**Per season, all events**

| Season | Area (its lowest automatics) | Events | Lowest automatics: made the final | Lowest automatics: median MOC place | Other Areas' next best mark + at-large: made the final | Other Areas' next best mark + at-large: median MOC place |
|---|---|---|---|---|---|---|
| 2022 | Tri-Valley | all events | 17 of 58 entries made the final (29%) | 11.5th (56 entries) | 4 of 27 entries made the final (15%) | 14.5th (26 entries) |
| 2022 | Bay Shore | all events | 2 of 56 entries made the final (4%) | 18th (49 entries) | 23 of 88 entries made the final (26%) | 12th (82 entries) |
| 2022 | Redwood Empire | all events | 6 of 54 entries made the final (11%) | 15th (52 entries) | 19 of 84 entries made the final (23%) | 13th (79 entries) |
| 2022 | Class A | all events | 1 of 26 entries made the final (4%) | 18.5th (26 entries) | 23 of 95 entries made the final (24%) | 13th (89 entries) |
| 2023 | Tri-Valley | all events | 24 of 58 entries made the final (41%) | 10th (55 entries) | 4 of 36 entries made the final (11%) | 16th (35 entries) |
| 2023 | Bay Shore | all events | 4 of 51 entries made the final (8%) | 19th (47 entries) | 6 of 92 entries made the final (7%) | 16th (88 entries) |
| 2023 | Redwood Empire | all events | 5 of 61 entries made the final (8%) | 17th (60 entries) | 4 of 84 entries made the final (5%) | 16th (79 entries) |
| 2023 | Class A | all events | 0 of 24 entries made the final (0%) | 21th (21 entries) | 7 of 100 entries made the final (7%) | 16th (95 entries) |
| 2024 | Tri-Valley | all events | 30 of 61 entries made the final (49%) | 9th (60 entries) | 2 of 34 entries made the final (6%) | 17th (34 entries) |
| 2024 | Bay Shore | all events | 7 of 57 entries made the final (12%) | 18th (55 entries) | 12 of 100 entries made the final (12%) | 14.5th (98 entries) |
| 2024 | Redwood Empire | all events | 2 of 54 entries made the final (4%) | 19.5th (52 entries) | 12 of 106 entries made the final (11%) | 15th (104 entries) |
| 2024 | Class A | all events | 3 of 28 entries made the final (11%) | 17th (26 entries) | 13 of 108 entries made the final (12%) | 15th (106 entries) |
| 2025 | Tri-Valley | all events | 16 of 57 entries made the final (28%) | 11th (55 entries) | 1 of 26 entries made the final (4%) | 16th (25 entries) |
| 2025 | Bay Shore | all events | 8 of 61 entries made the final (13%) | 18.5th (56 entries) | 9 of 105 entries made the final (9%) | 15.5th (96 entries) |
| 2025 | Redwood Empire | all events | 3 of 55 entries made the final (5%) | 18th (53 entries) | 10 of 96 entries made the final (10%) | 15th (87 entries) |
| 2025 | Class A | all events | 2 of 26 entries made the final (8%) | 17th (24 entries) | 10 of 103 entries made the final (10%) | 16th (95 entries) |
| 2026 | Tri-Valley | all events | 19 of 59 entries made the final (32%) | 10th (53 entries) | 1 of 34 entries made the final (3%) | 15th (32 entries) |
| 2026 | Bay Shore | all events | 4 of 60 entries made the final (7%) | 19th (58 entries) | 15 of 113 entries made the final (13%) | 16th (109 entries) |
| 2026 | Redwood Empire | all events | 6 of 56 entries made the final (11%) | 15th (54 entries) | 14 of 111 entries made the final (13%) | 16th (109 entries) |
| 2026 | Class A | all events | 1 of 28 entries made the final (4%) | 21th (25 entries) | 15 of 123 entries made the final (12%) | 15th (119 entries) |

**What the data shows.**
- **Class A.** Its lowest automatic qualifiers made the final less often than the other
  Areas' next-best-mark + at-large qualifiers in all 5 seasons, with a worse median place
  in all 5.
- **Redwood Empire.** Less often in 4 of 5 seasons (2023 the exception); worse median place
  in 4 of 5 (2026 the exception).
- **Bay Shore.** Mixed on the made-the-final rate: less often in 2022 and 2026, equal in
  2024 (7 of 57 against 12 of 100), more often in 2023 and 2025. Its median place was worse
  in all 5 seasons.
- Each season's result rests on 0–8 finalists on the automatic side.
- **Tri-Valley.** The opposite, by a wide margin: 28–49% of its 5th–6th-place automatic
  entries made the final, against 3–15% of the other Areas' next-best-mark + at-large
  entries.
- **Who the comparison group is.** Tri-Valley holds most next-best-mark and at-large spots
  (§2), so for Bay Shore, Redwood Empire and Class A the comparison group is mostly
  Tri-Valley athletes. Across all five seasons, entries from next-best-mark + at-large
  qualifiers made the final as follows:
  - Tri-Valley: 56 of 398 entries (14%)
  - Redwood Empire: 9 of 74 entries (12%)
  - Bay Shore: 3 of 57 entries (5%)
  - Class A: 0 of 26 entries (0%)

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
| Tri-Valley | 106 of 293 entries made the final (36%) | 12 of 157 entries made the final (8%) | +28.5 percentage points | < 0.001 | < 0.001 | +4.5 percentage points | < 0.001 |
| Bay Shore | 25 of 285 entries made the final (9%) | 65 of 498 entries made the final (13%) | -4.3 percentage points | 0.071 | 0.054 | +3.5 percentage points | 0.001 |
| Redwood Empire | 22 of 280 entries made the final (8%) | 59 of 481 entries made the final (12%) | -4.4 percentage points | 0.057 | 0.044 | +4.3 percentage points | < 0.001 |
| Class A | 7 of 132 entries made the final (5%) | 68 of 529 entries made the final (13%) | -7.5 percentage points | 0.014 | 0.002 | +3.4 percentage points | 0.002 |

**Reading the tests.**
- **Class A holds on every test:** a gap of −7.6 percentage points, p = 0.014 (independent),
  0.002 (clustered), 0.002 (permutation).
- **Bay Shore and Redwood Empire are weaker than before.** Their gaps are −4.3 and −4.4
  percentage points; independent p = 0.071 and 0.057, clustered p = 0.054 and 0.045. With
  pass-down routes, some Tri-Valley 7th–10th-place finishers who used to count as
  next-best-mark or at-large qualifiers are automatic, which shrinks the comparison group's
  lead.
- **What the permutation test adds.** With random Area labels, a lowest-automatic group
  would be expected to make the final about 3–4 percentage points *more* often than the
  comparison group. Bay Shore's, Redwood Empire's and Class A's lowest automatics instead
  did 4–8 points *worse*; random labels almost never produce gaps that far out
  (p ≤ 0.003). Tri-Valley's did 29 points better, also far outside what random labels give.

**What the tests can't do.**
- **They don't explain the gap.** For example, they can't separate "the Area is weaker"
  from "that Area's 5th–6th-place athletes are younger" or "they ran other events that
  weekend".
- **They don't correct for multiple comparisons.** Four Areas are tested, plus event
  groups below. A correction would leave Class A's result and the permutation results in
  place, and would weaken Bay Shore's and Redwood Empire's independent and clustered tests.
- **Per-season and per-event-group results are much less certain** than the pooled ones.

**By event group (5 seasons pooled; single seasons are in `data/summary/core_comparison.csv`)**

| Season | Area (its lowest automatics) | Events | Lowest automatics: made the final | Lowest automatics: median MOC place | Other Areas' next best mark + at-large: made the final | Other Areas' next best mark + at-large: median MOC place |
|---|---|---|---|---|---|---|
| 2022-2026 pooled | Tri-Valley | sprints & hurdles | 29 of 74 entries made the final (39%) | 9th (72 entries) | 0 of 26 entries made the final (0%) | 15th (26 entries) |
| 2022-2026 pooled | Tri-Valley | 400/800 | 18 of 36 entries made the final (50%) | 8th (36 entries) | 0 of 13 entries made the final (0%) | 20th (13 entries) |
| 2022-2026 pooled | Tri-Valley | distance | 8 of 34 entries made the final (24%) | 11th (34 entries) | 1 of 21 entries made the final (5%) | 16.5th (20 entries) |
| 2022-2026 pooled | Tri-Valley | jumps | 23 of 72 entries made the final (32%) | 11th (62 entries) | 7 of 64 entries made the final (11%) | 15th (61 entries) |
| 2022-2026 pooled | Tri-Valley | throws | 14 of 39 entries made the final (36%) | 12th (39 entries) | 4 of 26 entries made the final (15%) | 16.5th (26 entries) |
| 2022-2026 pooled | Tri-Valley | relays | 14 of 38 entries made the final (37%) | 9th (36 entries) | 0 of 7 entries made the final (0%) | 15th (6 entries) |
| 2022-2026 pooled | Tri-Valley | all events | 106 of 293 entries made the final (36%) | 10th (279 entries) | 12 of 157 entries made the final (8%) | 16th (152 entries) |
| 2022-2026 pooled | Bay Shore | sprints & hurdles | 8 of 76 entries made the final (11%) | 18th (74 entries) | 9 of 140 entries made the final (6%) | 16th (137 entries) |
| 2022-2026 pooled | Bay Shore | 400/800 | 2 of 35 entries made the final (6%) | 19.5th (34 entries) | 8 of 69 entries made the final (12%) | 15th (67 entries) |
| 2022-2026 pooled | Bay Shore | distance | 2 of 37 entries made the final (5%) | 20th (37 entries) | 10 of 73 entries made the final (14%) | 16th (72 entries) |
| 2022-2026 pooled | Bay Shore | jumps | 11 of 66 entries made the final (17%) | 16th (53 entries) | 18 of 109 entries made the final (17%) | 13th (94 entries) |
| 2022-2026 pooled | Bay Shore | throws | 1 of 35 entries made the final (3%) | 19th (33 entries) | 11 of 52 entries made the final (21%) | 16th (52 entries) |
| 2022-2026 pooled | Bay Shore | relays | 1 of 36 entries made the final (3%) | 19.5th (34 entries) | 9 of 55 entries made the final (16%) | 14th (51 entries) |
| 2022-2026 pooled | Bay Shore | all events | 25 of 285 entries made the final (9%) | 18th (265 entries) | 65 of 498 entries made the final (13%) | 15th (473 entries) |
| 2022-2026 pooled | Redwood Empire | sprints & hurdles | 1 of 71 entries made the final (1%) | 20th (67 entries) | 9 of 149 entries made the final (6%) | 16th (146 entries) |
| 2022-2026 pooled | Redwood Empire | 400/800 | 1 of 33 entries made the final (3%) | 19th (32 entries) | 8 of 65 entries made the final (12%) | 15th (63 entries) |
| 2022-2026 pooled | Redwood Empire | distance | 3 of 37 entries made the final (8%) | 18th (37 entries) | 9 of 66 entries made the final (14%) | 16th (66 entries) |
| 2022-2026 pooled | Redwood Empire | jumps | 8 of 65 entries made the final (12%) | 15th (63 entries) | 17 of 110 entries made the final (15%) | 14th (96 entries) |
| 2022-2026 pooled | Redwood Empire | throws | 8 of 38 entries made the final (21%) | 14th (38 entries) | 7 of 32 entries made the final (22%) | 14.5th (32 entries) |
| 2022-2026 pooled | Redwood Empire | relays | 1 of 36 entries made the final (3%) | 18th (34 entries) | 9 of 59 entries made the final (15%) | 14th (55 entries) |
| 2022-2026 pooled | Redwood Empire | all events | 22 of 280 entries made the final (8%) | 17th (271 entries) | 59 of 481 entries made the final (12%) | 15th (458 entries) |
| 2022-2026 pooled | Class A | sprints & hurdles | 1 of 37 entries made the final (3%) | 20th (36 entries) | 9 of 147 entries made the final (6%) | 16th (144 entries) |
| 2022-2026 pooled | Class A | 400/800 | 2 of 15 entries made the final (13%) | 20th (14 entries) | 8 of 63 entries made the final (13%) | 15th (61 entries) |
| 2022-2026 pooled | Class A | distance | 3 of 17 entries made the final (18%) | 15th (16 entries) | 10 of 68 entries made the final (15%) | 16th (67 entries) |
| 2022-2026 pooled | Class A | jumps | 0 of 29 entries made the final (0%) | 18th (23 entries) | 21 of 137 entries made the final (15%) | 14th (121 entries) |
| 2022-2026 pooled | Class A | throws | 0 of 17 entries made the final (0%) | 18.5th (16 entries) | 11 of 55 entries made the final (20%) | 16th (55 entries) |
| 2022-2026 pooled | Class A | relays | 1 of 17 entries made the final (6%) | 19th (17 entries) | 9 of 59 entries made the final (15%) | 14th (56 entries) |
| 2022-2026 pooled | Class A | all events | 7 of 132 entries made the final (5%) | 19.5th (122 entries) | 68 of 529 entries made the final (13%) | 15th (504 entries) |

By event group the counts get small (often 15–40 entries on the automatic side), so treat
these as indications. The dashboard's "Area place vs. MOC finish" tab shows every Area
place from 1st to 12th.

## 5. Left-out athletes

**Left out** = finished in an Area final behind her Area's last automatic qualifier (so she
was never offered a spot), and not in the MOC field by any route. For each, we count the
automatic qualifiers from *other* Areas whose Area-final marks were slower (or shorter).
Only automatic qualifiers are compared: by design, nobody left out has a better mark than a
next-best-mark qualifier (checked: none does). Marks come from different Area meets.

**What the data shows.**
- **Pooled 2022–2026:** 1,582 of 8,597 left-out finishers beat at least one automatic
  qualifier from another Area.
- **2025 girls 1600:** 12 of 53 left-out finishers did. Redwood Empire's 10th (5:17.28) beat
  5 Bay Shore automatic qualifiers and its 11th (5:26.07) beat 3. All 5 Bay Shore qualifiers
  they beat competed at the MOC and finished 17th–24th; none made the final.
- **How the beaten qualifiers did at the MOC (pooled):** 15 of 632 entries made the final
  (2%), median MOC place 20th.

**Left-out athletes (rows: their Area) who beat at least one automatic qualifier from each other Area, 2022–2026 pooled**

| Left out from | Beat a Tri-Valley automatic | Beat a Bay Shore automatic | Beat a Redwood Empire automatic | Beat a Class A automatic | Beat any |
|---|---|---|---|---|---|
| Tri-Valley | – | 412 athletes | 340 athletes | 464 athletes | 790 of 2059 left out (38%) |
| Bay Shore | 6 athletes | – | 123 athletes | 181 athletes | 264 of 2205 left out (12%) |
| Redwood Empire | 8 athletes | 202 athletes | – | 247 athletes | 395 of 2333 left out (17%) |
| Class A | 2 athletes | 93 athletes | 52 athletes | – | 133 of 2000 left out (7%) |

## 6. Spot use

**Guaranteed spots** per Area and event: its automatic spots (6; Class A 3) plus the
next-best-mark spots it won. Each falls in one segment:
- **Competed:** the qualifier ran the event at the MOC.
- **No-show:** the qualifier was in the MOC program for the event but didn't compete in it
  (did not start, or absent from its results), even if they competed in other events that
  day, and including pass-down entrants who didn't start.
- **Not used:** no entrant from that Area took the spot.

A decline before the deadline is not a no-show and isn't counted against the Area; the spot
passes down. Field size plays no part.

**What the data shows.**
- **Guaranteed spots:** 3,759 of 3,876 competed (97%), 111 no-shows, 6 not used.
- **Declines:** 247 automatic spots were passed down from declines over five seasons.
- **No-shows, all entries (any route):** 114 of 3,950 entries (3%); by Area, Tri-Valley 24
  of 1,375 (2%), Bay Shore 39 of 1,020 (4%), Redwood Empire 32 of 1,049 (3%), Class A 19 of
  506 (4%). 34 of the 114 competed in another MOC event that day.
- **At-large standard entrants:** 74, of whom 71 competed.

| Season | Area | Guaranteed spots | Competed | No-show | Not used | Passed down from declines | At-large standard (separate) | No-shows, all entries |
|---|---|---|---|---|---|---|---|---|
| 2022 | Bay Shore | 200 spots | 194 | 6 | 0 | 10 spots | 2 entrants: 2 competed, 0 no-show | 6 of 202 entries (3%) |
| 2022 | Class A | 100 spots | 97 | 2 | 1 | 13 spots | none | 2 of 99 entries (2%) |
| 2022 | Redwood Empire | 207 spots | 201 | 5 | 1 | 17 spots | none | 5 of 206 entries (2%) |
| 2022 | Tri-Valley | 264 spots | 256 | 8 | 0 | 8 spots | 2 entrants: 2 competed, 0 no-show | 8 of 266 entries (3%) |
| 2023 | Bay Shore | 205 spots | 193 | 11 | 1 | 14 spots | none | 11 of 204 entries (5%) |
| 2023 | Class A | 100 spots | 93 | 5 | 2 | 8 spots | 1 entrants: 1 competed, 0 no-show | 5 of 99 entries (5%) |
| 2023 | Redwood Empire | 215 spots | 205 | 10 | 0 | 6 spots | none | 10 of 215 entries (5%) |
| 2023 | Tri-Valley | 257 spots | 253 | 4 | 0 | 18 spots | 7 entrants: 7 competed, 0 no-show | 4 of 268 entries (1%) |
| 2024 | Bay Shore | 209 spots | 196 | 13 | 0 | 10 spots | 1 entrants: 1 competed, 0 no-show | 13 of 210 entries (6%) |
| 2024 | Class A | 100 spots | 98 | 1 | 1 | 13 spots | 4 entrants: 4 competed, 0 no-show | 1 of 104 entries (1%) |
| 2024 | Redwood Empire | 206 spots | 199 | 7 | 0 | 14 spots | none | 7 of 207 entries (3%) |
| 2024 | Tri-Valley | 262 spots | 258 | 4 | 0 | 8 spots | 15 entrants: 15 competed, 0 no-show | 4 of 277 entries (1%) |
| 2025 | Bay Shore | 196 spots | 191 | 5 | 0 | 14 spots | 1 entrants: 1 competed, 0 no-show | 5 of 197 entries (3%) |
| 2025 | Class A | 102 spots | 97 | 5 | 0 | 14 spots | 1 entrants: 1 competed, 0 no-show | 5 of 103 entries (5%) |
| 2025 | Redwood Empire | 210 spots | 206 | 4 | 0 | 17 spots | 2 entrants: 1 competed, 1 no-show | 5 of 212 entries (2%) |
| 2025 | Tri-Valley | 267 spots | 263 | 4 | 0 | 14 spots | 10 entrants: 10 competed, 0 no-show | 4 of 277 entries (1%) |
| 2026 | Bay Shore | 204 spots | 201 | 3 | 0 | 6 spots | 3 entrants: 2 competed, 1 no-show | 4 of 207 entries (2%) |
| 2026 | Class A | 98 spots | 93 | 5 | 0 | 9 spots | 3 entrants: 2 competed, 1 no-show | 6 of 101 entries (6%) |
| 2026 | Redwood Empire | 206 spots | 201 | 5 | 0 | 22 spots | 3 entrants: 3 competed, 0 no-show | 5 of 209 entries (2%) |
| 2026 | Tri-Valley | 268 spots | 264 | 4 | 0 | 12 spots | 19 entrants: 19 competed, 0 no-show | 4 of 287 entries (1%) |

## 7. Limits of this analysis

- **Small samples.** Many groups hold a handful of entries: next-best-mark and at-large
  qualifiers outside Tri-Valley, Class A in general, and any single event. A few athletes
  can move a rate by 10–30 percentage points. Where the text says "consistent", it means
  the same direction across seasons, not a precisely measured gap.
- **Comparing marks across meets.** Section 5 compares marks made at different meets, with
  different wind, weather, heats and competition.
- **Statistical tests.** The §4 p-values are pooled over five seasons and all events. They
  support a consistent direction, not a precise gap, and say nothing about causes.
- **Rules before 2026 are partly assumed.**
  - Allocation numbers for 2022–2025 are assumed to equal 2026's.
  - Each season's at-large standards come from its printed results, except 2023, where
    none were printed and 2026's are used.
- **Unresolved school names.** Program entries whose school name didn't resolve ("West
  County", truncated names) are linked to an Area result when the athlete's name is
  identical and unique in the event; 8 entries (3 in 2022, 5 in 2023) remain "Unknown".
  "West County" is still unconfirmed as Analy.
- **Privacy.** MOC-place figures (made-the-final counts, medians) are published only for groups of 5
  or more entries.
- **State results pending.** State qualification isn't included yet.
- **What the replay can't see.** Why an athlete declined, and whether a spot was actually
  offered to each finisher down the line. Declines are inferred from the program: finished
  ahead of the Area's last automatic qualifier but not entered.

## 5-season pooled summary (2022–2026 combined)

*Pooling combines different seasons, rule details and fields. Use it for the overall
picture only; the per-season tables above are primary.*

| Area | Share of all qualifiers | Next-best-mark + at-large spots held | Automatic: made the final | Next best mark + at-large: made the final | Lowest automatics vs other Areas' next best mark + at-large: made the final | No-shows |
|---|---|---|---|---|---|---|
| Tri-Valley | 1424 of 4024 MOC spots (35%) | 464 of 659 next-best-mark + at-large spots (70%) | 584 of 949 entries made the final (62%) | 56 of 398 entries made the final (14%) | 106 of 293 entries made the final (36%) vs 12 of 157 entries made the final (8%) | 24 of 1375 entries were no-shows (2%) |
| Bay Shore | 1023 of 4024 MOC spots (25%) | 61 of 659 next-best-mark + at-large spots (9%) | 288 of 924 entries made the final (31%) | 3 of 57 entries made the final (5%) | 25 of 285 entries made the final (9%) vs 65 of 498 entries made the final (13%) | 39 of 1020 entries were no-shows (4%) |
| Redwood Empire | 1064 of 4024 MOC spots (26%) | 102 of 659 next-best-mark + at-large spots (15%) | 268 of 942 entries made the final (28%) | 9 of 74 entries made the final (12%) | 22 of 280 entries made the final (8%) vs 59 of 481 entries made the final (12%) | 32 of 1049 entries were no-shows (3%) |
| Class A | 513 of 4024 MOC spots (13%) | 32 of 659 next-best-mark + at-large spots (5%) | 89 of 460 entries made the final (19%) | 0 of 26 entries made the final (0%) | 7 of 132 entries made the final (5%) vs 68 of 529 entries made the final (13%) | 19 of 506 entries were no-shows (4%) |
