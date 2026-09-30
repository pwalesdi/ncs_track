# What the data shows: MOC qualification by Area, 2022–2026 (findings v1)

*For coaches and the committee. Built from the tables in `data/summary/`; every column is defined in
`docs/analysis_tables.md`. Rates always show their count, e.g. "42% (11 of 26)".*

> **What changed in this update (2026-09-30)**
> - **§5, left-out athletes: new cutoff.** The MOC cutoff is now the 8th-best valid mark
>   (9th in LJ/TJ/SP/DT) across all MOC rounds, one mark per athlete. Before, it was the
>   8th-place mark in the final, so one slow final could set it for every Area. Across
>   2022–2026, left-out athletes at or above the cutoff fell from 95 to 6.
> - **§4, the core comparison: two stronger tests.** A permutation test and a test that
>   accounts for athletes appearing more than once now sit next to the original p-values.
>   The result did not weaken.
> - All other sections are unchanged.

## How to read this

- **Seasons.** 2022, 2023, 2024, 2025 and 2026. Each season is shown on its own. A
  5-season pooled summary is at the end, clearly labelled.
- **Areas.** The four MOC qualifying meets: Tri-Valley, Bay Shore, Redwood Empire and
  Class A.
- **How athletes reach the MOC.**
  - **Automatic:** top 6 at the Area meet (Class A: top 3).
  - **Next best mark:** the 3 "fill" spots per event, which go to the next best marks
    across all four meets.
  - **At-large standard:** met the posted MOC standard in the Area final.
  - Next best mark + at-large standard together are called **at-large (combined)**.
  - **Replacement:** entered to fill a vacancy.
- **Two fields.**
  - **"Everyone who qualified":** who the current rules say earned a spot. This comes from
    replaying each season's rules against the Area results; the replay reproduces 98–99% of
    real MOC entries once athlete choices and replacements are accounted for.
  - **"Who actually declared":** who was in the MOC program.
- **Top finish:** 8th place or better in the MOC final (9th in the long jump, triple jump,
  shot put and discus). **Scored:** 6th or better.
- **This document describes; it doesn't recommend.** It doesn't propose any change to how
  spots are allocated.

## 1. Field makeup by Area

**What the data shows.** Each of the three large Areas gets about 192 automatic spots per
season (6 per event × 32 events); Class A gets about 96. The difference between Areas comes
from the at-large spots.
- **Tri-Valley** is about 35–36% of the qualified field every season, with 78–102
  at-large spots a season.
- **Bay Shore** is 24–26%, with 5–17 at-large spots.
- **Redwood Empire** is 25–27%, with 11–25 at-large spots.
- **Class A** is 12–13%, with 3–10 at-large spots.

The declared field has almost the same shares, because most qualifiers declare. "Unknown"
rows are program entries whose school couldn't be matched (see §7).

**Everyone who qualified** (share of the whole field; then counts by how they got in)

| Season | Area | Share of field | Automatic | Next best mark | At-large standard |
|---|---|---|---|---|---|
| 2022 | Tri-Valley | 35% (270 of 780) | 192 | 76 | 2 |
| 2022 | Bay Shore | 26% (200 of 780) | 192 | 6 | 2 |
| 2022 | Redwood Empire | 27% (212 of 780) | 192 | 20 | 0 |
| 2022 | Class A | 13% (98 of 780) | 95 | 3 | 0 |
| 2023 | Tri-Valley | 35% (280 of 807) | 192 | 71 | 17 |
| 2023 | Bay Shore | 26% (209 of 807) | 193 | 14 | 2 |
| 2023 | Redwood Empire | 27% (217 of 807) | 192 | 24 | 1 |
| 2023 | Class A | 13% (101 of 807) | 96 | 4 | 1 |
| 2024 | Tri-Valley | 36% (292 of 813) | 192 | 74 | 26 |
| 2024 | Bay Shore | 26% (210 of 813) | 193 | 14 | 3 |
| 2024 | Redwood Empire | 25% (203 of 813) | 192 | 9 | 2 |
| 2024 | Class A | 13% (108 of 813) | 98 | 5 | 5 |
| 2025 | Tri-Valley | 36% (288 of 806) | 192 | 77 | 19 |
| 2025 | Bay Shore | 24% (197 of 806) | 192 | 4 | 1 |
| 2025 | Redwood Empire | 27% (216 of 806) | 194 | 15 | 7 |
| 2025 | Class A | 13% (105 of 806) | 96 | 6 | 3 |
| 2026 | Tri-Valley | 36% (294 of 818) | 192 | 72 | 30 |
| 2026 | Bay Shore | 25% (207 of 818) | 192 | 12 | 3 |
| 2026 | Redwood Empire | 26% (216 of 818) | 192 | 17 | 7 |
| 2026 | Class A | 12% (101 of 818) | 96 | 2 | 3 |

**Who actually declared** (share of the whole field; then counts by how they got in)

| Season | Area | Share of field | Automatic | Next best mark | At-large standard | Replacement | Unexplained |
|---|---|---|---|---|---|---|---|
| 2022 | Tri-Valley | 34% (266 of 775) | 185 | 71 | 2 | 5 | 3 |
| 2022 | Bay Shore | 26% (202 of 775) | 182 | 6 | 2 | 10 | 2 |
| 2022 | Redwood Empire | 25% (196 of 775) | 168 | 15 | 0 | 11 | 2 |
| 2022 | Class A | 12% (96 of 775) | 85 | 1 | 0 | 8 | 2 |
| 2022 | Unknown | 2% (15 of 775) | 0 | 0 | 0 | 0 | 15 |
| 2023 | Tri-Valley | 34% (268 of 789) | 179 | 59 | 14 | 9 | 7 |
| 2023 | Bay Shore | 26% (202 of 789) | 177 | 14 | 2 | 7 | 2 |
| 2023 | Redwood Empire | 27% (215 of 789) | 186 | 22 | 1 | 5 | 1 |
| 2023 | Class A | 13% (99 of 789) | 86 | 4 | 1 | 8 | 0 |
| 2023 | Unknown | 1% (5 of 789) | 0 | 0 | 0 | 0 | 5 |
| 2024 | Tri-Valley | 35% (277 of 798) | 186 | 65 | 21 | 4 | 1 |
| 2024 | Bay Shore | 26% (210 of 798) | 185 | 14 | 2 | 5 | 4 |
| 2024 | Redwood Empire | 26% (207 of 798) | 179 | 8 | 2 | 10 | 8 |
| 2024 | Class A | 13% (104 of 798) | 85 | 5 | 4 | 7 | 3 |
| 2025 | Tri-Valley | 35% (277 of 789) | 181 | 70 | 19 | 6 | 1 |
| 2025 | Bay Shore | 25% (197 of 789) | 180 | 4 | 1 | 10 | 2 |
| 2025 | Redwood Empire | 27% (212 of 789) | 178 | 15 | 6 | 12 | 1 |
| 2025 | Class A | 13% (103 of 789) | 87 | 5 | 3 | 5 | 3 |
| 2026 | Tri-Valley | 36% (287 of 804) | 180 | 70 | 27 | 7 | 3 |
| 2026 | Bay Shore | 26% (207 of 804) | 187 | 12 | 3 | 3 | 2 |
| 2026 | Redwood Empire | 26% (209 of 804) | 175 | 12 | 6 | 9 | 7 |
| 2026 | Class A | 13% (101 of 804) | 88 | 2 | 3 | 5 | 3 |

## 2. Share of at-large spots by Area

**What the data shows.** Tri-Valley athletes took most at-large spots in every season:
- **Next best mark (the 3 fill spots):** 63–75% of those spots each season.
- **At-large standard:** 50–81%.
- **Combined:** 66–73%.

Caveats:
- **2022 standard spots are few.** Only 4 went on the standard, so its percentages rest
  on 4 athletes.
- **The standard spots count is small by construction.** Fill spots are assigned before
  standards, so athletes who meet the standard usually take a fill spot first.

**Everyone who qualified** (each Area's share of that season's spots of each type)

| Season | Area | Next best mark | At-large standard | Combined |
|---|---|---|---|---|
| 2022 | Tri-Valley | 72% (76 of 105) | 50% (2 of 4) | 72% (78 of 109) |
| 2022 | Bay Shore | 6% (6 of 105) | 50% (2 of 4) | 7% (8 of 109) |
| 2022 | Redwood Empire | 19% (20 of 105) | 0% (0 of 4) | 18% (20 of 109) |
| 2022 | Class A | 3% (3 of 105) | 0% (0 of 4) | 3% (3 of 109) |
| 2023 | Tri-Valley | 63% (71 of 113) | 81% (17 of 21) | 66% (88 of 134) |
| 2023 | Bay Shore | 12% (14 of 113) | 10% (2 of 21) | 12% (16 of 134) |
| 2023 | Redwood Empire | 21% (24 of 113) | 5% (1 of 21) | 19% (25 of 134) |
| 2023 | Class A | 4% (4 of 113) | 5% (1 of 21) | 4% (5 of 134) |
| 2024 | Tri-Valley | 73% (74 of 102) | 72% (26 of 36) | 72% (100 of 138) |
| 2024 | Bay Shore | 14% (14 of 102) | 8% (3 of 36) | 12% (17 of 138) |
| 2024 | Redwood Empire | 9% (9 of 102) | 6% (2 of 36) | 8% (11 of 138) |
| 2024 | Class A | 5% (5 of 102) | 14% (5 of 36) | 7% (10 of 138) |
| 2025 | Tri-Valley | 75% (77 of 102) | 63% (19 of 30) | 73% (96 of 132) |
| 2025 | Bay Shore | 4% (4 of 102) | 3% (1 of 30) | 4% (5 of 132) |
| 2025 | Redwood Empire | 15% (15 of 102) | 23% (7 of 30) | 17% (22 of 132) |
| 2025 | Class A | 6% (6 of 102) | 10% (3 of 30) | 7% (9 of 132) |
| 2026 | Tri-Valley | 70% (72 of 103) | 70% (30 of 43) | 70% (102 of 146) |
| 2026 | Bay Shore | 12% (12 of 103) | 7% (3 of 43) | 10% (15 of 146) |
| 2026 | Redwood Empire | 17% (17 of 103) | 16% (7 of 43) | 16% (24 of 146) |
| 2026 | Class A | 2% (2 of 103) | 7% (3 of 43) | 3% (5 of 146) |

**Who actually declared** (each Area's share of that season's spots of each type)

| Season | Area | Next best mark | At-large standard | Combined |
|---|---|---|---|---|
| 2022 | Tri-Valley | 76% (71 of 93) | 50% (2 of 4) | 75% (73 of 97) |
| 2022 | Bay Shore | 6% (6 of 93) | 50% (2 of 4) | 8% (8 of 97) |
| 2022 | Redwood Empire | 16% (15 of 93) | 0% (0 of 4) | 15% (15 of 97) |
| 2022 | Class A | 1% (1 of 93) | 0% (0 of 4) | 1% (1 of 97) |
| 2023 | Tri-Valley | 60% (59 of 99) | 78% (14 of 18) | 62% (73 of 117) |
| 2023 | Bay Shore | 14% (14 of 99) | 11% (2 of 18) | 14% (16 of 117) |
| 2023 | Redwood Empire | 22% (22 of 99) | 6% (1 of 18) | 20% (23 of 117) |
| 2023 | Class A | 4% (4 of 99) | 6% (1 of 18) | 4% (5 of 117) |
| 2024 | Tri-Valley | 71% (65 of 92) | 72% (21 of 29) | 71% (86 of 121) |
| 2024 | Bay Shore | 15% (14 of 92) | 7% (2 of 29) | 13% (16 of 121) |
| 2024 | Redwood Empire | 9% (8 of 92) | 7% (2 of 29) | 8% (10 of 121) |
| 2024 | Class A | 5% (5 of 92) | 14% (4 of 29) | 7% (9 of 121) |
| 2025 | Tri-Valley | 74% (70 of 94) | 66% (19 of 29) | 72% (89 of 123) |
| 2025 | Bay Shore | 4% (4 of 94) | 3% (1 of 29) | 4% (5 of 123) |
| 2025 | Redwood Empire | 16% (15 of 94) | 21% (6 of 29) | 17% (21 of 123) |
| 2025 | Class A | 5% (5 of 94) | 10% (3 of 29) | 7% (8 of 123) |
| 2026 | Tri-Valley | 73% (70 of 96) | 69% (27 of 39) | 72% (97 of 135) |
| 2026 | Bay Shore | 12% (12 of 96) | 8% (3 of 39) | 11% (15 of 135) |
| 2026 | Redwood Empire | 12% (12 of 96) | 15% (6 of 39) | 13% (18 of 135) |
| 2026 | Class A | 2% (2 of 96) | 8% (3 of 39) | 4% (5 of 135) |

## 3. MOC results by Area and how athletes qualified

Declared athletes who competed at the MOC. To keep the table readable, only automatic and
at-large (combined) qualifiers are shown. The full breakdown, including next best mark,
standard and replacement, is in `data/summary/moc_performance.csv`.

**What the data shows.**
- **Automatic qualifiers.** Tri-Valley's reached a top finish 62–65% of the time each
  season. Bay Shore's did 31–34%, Redwood Empire's 26–34%, and Class A's 8–32%. Class A
  varies most, with 8% (7 of 83) in 2026 and 32% (27 of 84) in 2024.
- **At-large qualifiers** reached a top finish far less often than automatic ones, in every
  Area and season. Outside Tri-Valley the at-large counts are small (often under 20), so
  those rates move a lot with one or two athletes.

| Season | Area | How they qualified | Top finish (top 8/9) | Scored (top 6) |
|---|---|---|---|---|
| 2022 | Tri-Valley | Automatic | 65% (118 of 181) | 50% (90 of 181) |
| 2022 | Tri-Valley | At-large (combined) | 28% (19 of 69) | 13% (9 of 69) |
| 2022 | Bay Shore | Automatic | 31% (55 of 176) | 24% (42 of 176) |
| 2022 | Bay Shore | At-large (combined) | 0% (0 of 8) | 0% (0 of 8) |
| 2022 | Redwood Empire | Automatic | 32% (53 of 167) | 25% (41 of 167) |
| 2022 | Redwood Empire | At-large (combined) | 31% (4 of 13) | 8% (1 of 13) |
| 2022 | Class A | Automatic | 11% (9 of 84) | 11% (9 of 84) |
| 2022 | Class A | At-large (combined) | 0% (0 of 1) | 0% (0 of 1) |
| 2023 | Tri-Valley | Automatic | 64% (115 of 179) | 50% (89 of 179) |
| 2023 | Tri-Valley | At-large (combined) | 9% (6 of 70) | 4% (3 of 70) |
| 2023 | Bay Shore | Automatic | 32% (54 of 168) | 26% (43 of 168) |
| 2023 | Bay Shore | At-large (combined) | 13% (2 of 15) | 13% (2 of 15) |
| 2023 | Redwood Empire | Automatic | 29% (52 of 179) | 21% (37 of 179) |
| 2023 | Redwood Empire | At-large (combined) | 15% (3 of 20) | 5% (1 of 20) |
| 2023 | Class A | Automatic | 29% (24 of 82) | 21% (17 of 82) |
| 2023 | Class A | At-large (combined) | 25% (1 of 4) | 0% (0 of 4) |
| 2024 | Tri-Valley | Automatic | 64% (119 of 185) | 51% (94 of 185) |
| 2024 | Tri-Valley | At-large (combined) | 14% (12 of 84) | 12% (10 of 84) |
| 2024 | Bay Shore | Automatic | 32% (55 of 173) | 21% (36 of 173) |
| 2024 | Bay Shore | At-large (combined) | 0% (0 of 15) | 0% (0 of 15) |
| 2024 | Redwood Empire | Automatic | 26% (46 of 176) | 19% (33 of 176) |
| 2024 | Redwood Empire | At-large (combined) | 11% (1 of 9) | 0% (0 of 9) |
| 2024 | Class A | Automatic | 32% (27 of 84) | 25% (21 of 84) |
| 2024 | Class A | At-large (combined) | 0% (0 of 9) | 0% (0 of 9) |
| 2025 | Tri-Valley | Automatic | 63% (113 of 179) | 51% (92 of 179) |
| 2025 | Tri-Valley | At-large (combined) | 11% (10 of 88) | 5% (4 of 88) |
| 2025 | Bay Shore | Automatic | 34% (60 of 176) | 25% (44 of 176) |
| 2025 | Bay Shore | At-large (combined) | 20% (1 of 5) | 0% (0 of 5) |
| 2025 | Redwood Empire | Automatic | 31% (54 of 176) | 23% (40 of 176) |
| 2025 | Redwood Empire | At-large (combined) | 0% (0 of 19) | 0% (0 of 19) |
| 2025 | Class A | Automatic | 25% (20 of 81) | 17% (14 of 81) |
| 2025 | Class A | At-large (combined) | 0% (0 of 8) | 0% (0 of 8) |
| 2026 | Tri-Valley | Automatic | 62% (111 of 178) | 48% (86 of 178) |
| 2026 | Tri-Valley | At-large (combined) | 15% (14 of 95) | 6% (6 of 95) |
| 2026 | Bay Shore | Automatic | 33% (61 of 184) | 29% (53 of 184) |
| 2026 | Bay Shore | At-large (combined) | 0% (0 of 14) | 0% (0 of 14) |
| 2026 | Redwood Empire | Automatic | 34% (58 of 172) | 23% (40 of 172) |
| 2026 | Redwood Empire | At-large (combined) | 11% (2 of 18) | 11% (2 of 18) |
| 2026 | Class A | Automatic | 8% (7 of 83) | 6% (5 of 83) |
| 2026 | Class A | At-large (combined) | 0% (0 of 4) | 0% (0 of 4) |

## 4. The core question: do some Areas' last automatic qualifiers do worse at the MOC than other Areas' at-large qualifiers?

**The comparison.**
- **Lowest automatic qualifiers:** each Area's automatic qualifiers who placed 5th or 6th
  at their Area meet (3rd for Class A).
- **At-large qualifiers from the other three Areas:** next best mark and at-large standard
  combined.
- **Who is counted:** only athletes who competed at the MOC, with genders combined.

**Two measures.**
- **Top-finish rate.**
- **Median MOC place.** Finalists keep their final place; everyone else is ranked after the
  finalists by their best MOC mark. Lower is better.

**Per season, all events**

| Season | Area (its lowest autos) | Event group | Lowest autos: top finish | Lowest autos: median MOC place | Other Areas' at-large: top finish | Other Areas' at-large: median MOC place |
|---|---|---|---|---|---|---|
| 2022 | Tri-Valley | all | 29% (17 of 58) | 11.5 (n=56) | 18% (4 of 22) | 14.5 (n=22) |
| 2022 | Bay Shore | all | 4% (2 of 56) | 18 (n=49) | 28% (23 of 83) | 12 (n=78) |
| 2022 | Redwood Empire | all | 12% (6 of 51) | 16 (n=49) | 24% (19 of 78) | 13 (n=73) |
| 2022 | Class A | all | 4% (1 of 26) | 18.5 (n=26) | 26% (23 of 90) | 13 (n=85) |
| 2023 | Tri-Valley | all | 41% (24 of 58) | 10 (n=55) | 15% (6 of 39) | 15 (n=38) |
| 2023 | Bay Shore | all | 8% (4 of 50) | 19.5 (n=46) | 11% (10 of 94) | 16 (n=89) |
| 2023 | Redwood Empire | all | 8% (5 of 61) | 17 (n=60) | 10% (9 of 89) | 15 (n=83) |
| 2023 | Class A | all | 0% (0 of 24) | 21 (n=21) | 10% (11 of 105) | 16 (n=99) |
| 2024 | Tri-Valley | all | 49% (30 of 61) | 9 (n=60) | 3% (1 of 33) | 18 (n=33) |
| 2024 | Bay Shore | all | 12% (7 of 57) | 18 (n=55) | 13% (13 of 102) | 14.5 (n=100) |
| 2024 | Redwood Empire | all | 4% (2 of 54) | 19.5 (n=52) | 11% (12 of 108) | 15 (n=106) |
| 2024 | Class A | all | 11% (3 of 28) | 17 (n=26) | 12% (13 of 108) | 15 (n=106) |
| 2025 | Tri-Valley | all | 28% (16 of 57) | 11 (n=55) | 3% (1 of 32) | 16 (n=31) |
| 2025 | Bay Shore | all | 13% (8 of 61) | 18.5 (n=56) | 9% (10 of 115) | 15 (n=107) |
| 2025 | Redwood Empire | all | 5% (3 of 55) | 18 (n=53) | 11% (11 of 101) | 15 (n=93) |
| 2025 | Class A | all | 8% (2 of 26) | 17 (n=24) | 10% (11 of 112) | 15 (n=105) |
| 2026 | Tri-Valley | all | 32% (19 of 59) | 10 (n=53) | 6% (2 of 36) | 15 (n=34) |
| 2026 | Bay Shore | all | 7% (4 of 60) | 19 (n=58) | 14% (16 of 117) | 15 (n=113) |
| 2026 | Redwood Empire | all | 11% (6 of 56) | 15 (n=54) | 12% (14 of 113) | 15 (n=111) |
| 2026 | Class A | all | 4% (1 of 28) | 21 (n=25) | 13% (16 of 127) | 15 (n=123) |

**What the data shows.**
- **Bay Shore, Redwood Empire and Class A.** In most seasons, their lowest automatic
  qualifiers reached a top finish *less* often than the other Areas' at-large qualifiers,
  and had a worse median place.
  - Redwood Empire and Class A: lower in all 5 seasons.
  - Bay Shore: lower in 4 of 5; 2025 was the exception.
  - Several single-season gaps are small, e.g. 2024 Bay Shore 12% (7 of 57) vs 13% (13 of
    102). Each season's result rests on 0–8 top finishes on the automatic side.
- **Tri-Valley.** The opposite, by a wide margin: its 5th–6th-place automatic qualifiers
  reached a top finish 28–49% of the time, against 3–18% for other Areas' at-large
  qualifiers.
- **Who "other Areas' at-large" are.** Tri-Valley holds most at-large spots (§2), so for
  Bay Shore, Redwood Empire and Class A that comparison group is mostly Tri-Valley
  athletes. Across all five seasons, at-large qualifiers who competed reached a top finish:
  - Tri-Valley 15% (61 of 406)
  - Redwood Empire 13% (10 of 79)
  - Bay Shore 5% (3 of 57)
  - Class A 4% (1 of 26)

**How confident can we be?** Pooled over five seasons, three tests:
- **Old test** (the first version): treats every athlete-event as independent.
- **Clustered test:** the same comparison, but it allows for the same athlete appearing in
  several events or seasons.
- **Permutation test:** shuffles which Area each athlete belongs to, within each season,
  gender and event, 10,000 times, keeping how each athlete qualified fixed. It asks whether
  this Area's gap is bigger than you'd see if Area labels were random. Random labels
  themselves produce a small positive gap, because lowest automatics usually do a little
  better than at-large qualifiers overall.

| Area | Lowest autos: top finish | Other Areas' at-large: top finish | Gap | Old p (independent) | Clustered by athlete p | Gap if Areas were random | Permutation p |
|---|---|---|---|---|---|---|---|
| Tri-Valley | 36% (106 of 293) | 9% (14 of 162) | +27.5 pts | < 0.001 | < 0.001 | +3.7 pts | < 0.001 |
| Bay Shore | 9% (25 of 284) | 14% (72 of 511) | -5.3 pts | 0.029 | 0.018 | +2.4 pts | 0.001 |
| Redwood Empire | 8% (22 of 277) | 13% (65 of 489) | -5.3 pts | 0.025 | 0.017 | +3.3 pts | < 0.001 |
| Class A | 5% (7 of 132) | 14% (74 of 542) | -8.3 pts | 0.008 | < 0.001 | +2.4 pts | 0.003 |

**Reading the tests.**
- **Every result holds.** No Area's result weakens under the stronger tests; every
  p-value stays below 0.03.
- **Why the clustered p-values are a little smaller than the old ones.** Athletes rarely
  repeat, about 1.15 rows per athlete, so allowing for repeats changes little. The old
  test's pooled standard error is conservative when the two rates differ.
- **What the permutation test adds.** With random Area labels, a lowest-automatic group
  would be expected to do 2–4 points *better* than the at-large comparison group.
  - Bay Shore's, Redwood Empire's and Class A's lowest automatics instead did 5–8 points
    *worse*. Random labels almost never produce gaps that far out (p ≤ 0.003).
  - Tri-Valley's lowest automatics did 27 points better, also far outside what random
    labels give.

**What the tests can't do.**
- **They don't explain the gap.** For example, they can't separate "the Area is weaker"
  from "that Area's 5th–6th-place athletes are younger" or "they ran other events that
  weekend".
- **They don't correct for multiple comparisons.** Four Areas are tested, plus event
  groups below. With the p-values this small, a correction would not change the pooled
  conclusion.
- **Per-season and per-event-group results are much less certain** than the pooled ones.

**By event group (5 seasons pooled; single seasons are in `data/summary/core_comparison.csv`)**

| Season | Area (its lowest autos) | Event group | Lowest autos: top finish | Lowest autos: median MOC place | Other Areas' at-large: top finish | Other Areas' at-large: median MOC place |
|---|---|---|---|---|---|---|
| 2022-2026 pooled | Tri-Valley | sprints hurdles | 39% (29 of 74) | 9 (n=72) | 3% (1 of 30) | 15.5 (n=30) |
| 2022-2026 pooled | Tri-Valley | 400/800 | 50% (18 of 36) | 8 (n=36) | 0% (0 of 20) | 20 (n=20) |
| 2022-2026 pooled | Tri-Valley | distance | 24% (8 of 34) | 11 (n=34) | 12% (3 of 25) | 15 (n=25) |
| 2022-2026 pooled | Tri-Valley | jumps | 32% (23 of 72) | 11 (n=62) | 12% (7 of 57) | 15 (n=54) |
| 2022-2026 pooled | Tri-Valley | throws | 36% (14 of 39) | 12 (n=39) | 12% (3 of 24) | 16.5 (n=24) |
| 2022-2026 pooled | Tri-Valley | relays | 37% (14 of 38) | 9 (n=36) | 0% (0 of 6) | 15 (n=5) |
| 2022-2026 pooled | Tri-Valley | all | 36% (106 of 293) | 10 (n=279) | 9% (14 of 162) | 16 (n=158) |
| 2022-2026 pooled | Bay Shore | sprints hurdles | 11% (8 of 75) | 18 (n=73) | 8% (11 of 146) | 16 (n=144) |
| 2022-2026 pooled | Bay Shore | 400/800 | 6% (2 of 35) | 19.5 (n=34) | 13% (10 of 76) | 15 (n=74) |
| 2022-2026 pooled | Bay Shore | distance | 5% (2 of 37) | 20 (n=37) | 17% (14 of 81) | 16 (n=81) |
| 2022-2026 pooled | Bay Shore | jumps | 17% (11 of 66) | 16 (n=53) | 18% (18 of 102) | 13 (n=86) |
| 2022-2026 pooled | Bay Shore | throws | 3% (1 of 35) | 19 (n=33) | 20% (10 of 51) | 16 (n=51) |
| 2022-2026 pooled | Bay Shore | relays | 3% (1 of 36) | 19.5 (n=34) | 16% (9 of 55) | 13 (n=51) |
| 2022-2026 pooled | Bay Shore | all | 9% (25 of 284) | 18 (n=264) | 14% (72 of 511) | 15 (n=487) |
| 2022-2026 pooled | Redwood Empire | sprints hurdles | 1% (1 of 70) | 20 (n=66) | 8% (12 of 154) | 15.5 (n=152) |
| 2022-2026 pooled | Redwood Empire | 400/800 | 3% (1 of 32) | 19 (n=31) | 15% (10 of 66) | 14 (n=64) |
| 2022-2026 pooled | Redwood Empire | distance | 8% (3 of 37) | 18 (n=37) | 17% (12 of 71) | 16 (n=71) |
| 2022-2026 pooled | Redwood Empire | jumps | 12% (8 of 64) | 14.5 (n=62) | 14% (15 of 107) | 14 (n=92) |
| 2022-2026 pooled | Redwood Empire | throws | 21% (8 of 38) | 14 (n=38) | 21% (7 of 33) | 14 (n=33) |
| 2022-2026 pooled | Redwood Empire | relays | 3% (1 of 36) | 18 (n=34) | 16% (9 of 58) | 13.5 (n=54) |
| 2022-2026 pooled | Redwood Empire | all | 8% (22 of 277) | 17 (n=268) | 13% (65 of 489) | 15 (n=466) |
| 2022-2026 pooled | Class A | sprints hurdles | 3% (1 of 37) | 20 (n=36) | 8% (12 of 153) | 15 (n=151) |
| 2022-2026 pooled | Class A | 400/800 | 13% (2 of 15) | 20 (n=14) | 14% (10 of 69) | 15 (n=67) |
| 2022-2026 pooled | Class A | distance | 18% (3 of 17) | 15 (n=16) | 17% (13 of 78) | 16 (n=78) |
| 2022-2026 pooled | Class A | jumps | 0% (0 of 29) | 18 (n=23) | 15% (20 of 130) | 14 (n=113) |
| 2022-2026 pooled | Class A | throws | 0% (0 of 17) | 18.5 (n=16) | 19% (10 of 54) | 15.5 (n=54) |
| 2022-2026 pooled | Class A | relays | 6% (1 of 17) | 19 (n=17) | 16% (9 of 58) | 14 (n=55) |
| 2022-2026 pooled | Class A | all | 5% (7 of 132) | 19.5 (n=122) | 14% (74 of 542) | 15 (n=518) |

By event group the counts get small (often 15–40 athletes on the automatic side), so treat
these as indications.

## 5. Left-out athletes

For each Area and event, we took the three best athletes who did *not* qualify, ranked by
their Area mark. We then checked whether that mark was at or better than the MOC top-8
mark that year (top 9 in the long jump, triple jump, shot put and discus).

**Caveat: these marks come from different meets**, with different days, wind, weather,
competition and (in field events) attempts. A good Area mark doesn't mean the athlete
would have finished that high at the MOC. This is a comparison, not a prediction.

**The cutoff.** The 8th-best valid MOC mark that year (9th in LJ/TJ/SP/DT), across
prelims and finals combined, one mark per athlete. The first version used the 8th-place
mark in the final. That let one slow final (e.g. a 2026 boys 4x400 team at 3:59.34) set
the cutoff for every Area.

**What the data shows.**
- **Almost never.** In 19 of the 20 Area-seasons, none of an Area's best non-qualifiers
  had a mark at or better than the MOC cutoff.
- **The exception is 2023 Tri-Valley:** 6% (6 of 96), in the boys 200 and 400 and the
  girls 200 and discus.
  - The 2023 MOC marks were unusually slow; a 22.93 won a boys 200 prelim heat.
  - 2023 at-large standards are assumed from 2026, so Tri-Valley's places 7–14 in the
    boys 200 all qualified at-large, and its best non-qualifiers were 15th.
- **The first version was dominated by slow finals:** 95 cases (39 Tri-Valley, 23 Bay
  Shore, 20 Redwood Empire, 13 Class A).

| Season | Area | Best non-qualifiers with an Area mark at/above the MOC top-8/9 cutoff | …of whom were in the MOC program anyway |
|---|---|---|---|
| 2022 | Tri-Valley | 0% (0 of 96) | 0 |
| 2022 | Bay Shore | 0% (0 of 96) | 0 |
| 2022 | Redwood Empire | 0% (0 of 96) | 0 |
| 2022 | Class A | 0% (0 of 93) | 0 |
| 2023 | Tri-Valley | 6% (6 of 96) | 0 |
| 2023 | Bay Shore | 0% (0 of 96) | 0 |
| 2023 | Redwood Empire | 0% (0 of 96) | 0 |
| 2023 | Class A | 0% (0 of 95) | 0 |
| 2024 | Tri-Valley | 0% (0 of 96) | 0 |
| 2024 | Bay Shore | 0% (0 of 96) | 0 |
| 2024 | Redwood Empire | 0% (0 of 96) | 0 |
| 2024 | Class A | 0% (0 of 96) | 0 |
| 2025 | Tri-Valley | 0% (0 of 96) | 0 |
| 2025 | Bay Shore | 0% (0 of 96) | 0 |
| 2025 | Redwood Empire | 0% (0 of 96) | 0 |
| 2025 | Class A | 0% (0 of 96) | 0 |
| 2026 | Tri-Valley | 0% (0 of 96) | 0 |
| 2026 | Bay Shore | 0% (0 of 96) | 0 |
| 2026 | Redwood Empire | 0% (0 of 96) | 0 |
| 2026 | Class A | 0% (0 of 96) | 0 |

## 6. Spot utilization: empty lanes and no-shows

**The terms.**
- **Unused spot:** a qualified athlete who didn't compete in that event. Most unused spots
  are athletes who qualified in two events and ran one. Most of those athletes competed in
  another MOC event, and many of their spots were given to someone else.
- **Empty lane:** a spot that went to nobody, i.e. unused and not refilled. It includes
  no-shows, because a declared athlete who doesn't run can't be replaced.

**What the data shows.**
- **Used spots:** 85–96% of spots earned were used each season, by Area.
- **No-shows:** 1–6% of declared athletes, by Area and season.
- **Empty lanes:** 3–10% of spots, e.g. 2026 Redwood Empire 8% (17 of 216) and Class A 9%
  (9 of 101).
- **Double qualifiers:** among qualifiers who didn't declare an event, most ran a
  different MOC event; the share ranges from 43% to 100% by Area and season.
- **Flag lists.** 22 Area × event combinations have empty lanes in 3 or more of the 5
  seasons. Counting every unused spot instead gives 51. Most flagged entries are 1–2
  empty lanes a season.

| Season | Area | Spots earned | Used (competed) | No-shows (of declared) | Not declared | …ran another MOC event | Refilled | Empty lanes |
|---|---|---|---|---|---|---|---|---|
| 2022 | Bay Shore | 200 | 92% (184 of 200) | 3% (6 of 190) | 10 | 90% (9 of 10) | 10 | 3% (6 of 200) |
| 2022 | Class A | 98 | 87% (85 of 98) | 1% (1 of 86) | 12 | 64% (7 of 11) | 8 | 5% (5 of 98) |
| 2022 | Redwood Empire | 212 | 85% (180 of 212) | 2% (3 of 183) | 29 | 73% (19 of 26) | 11 | 10% (21 of 212) |
| 2022 | Tri-Valley | 270 | 93% (250 of 270) | 3% (8 of 258) | 12 | 64% (7 of 11) | 5 | 6% (15 of 270) |
| 2023 | Bay Shore | 209 | 88% (183 of 209) | 5% (10 of 193) | 16 | 79% (11 of 14) | 7 | 9% (19 of 209) |
| 2023 | Class A | 101 | 85% (86 of 101) | 5% (5 of 91) | 10 | 67% (6 of 9) | 8 | 7% (7 of 101) |
| 2023 | Redwood Empire | 217 | 92% (199 of 217) | 5% (10 of 209) | 8 | 62% (5 of 8) | 5 | 6% (13 of 217) |
| 2023 | Tri-Valley | 280 | 89% (249 of 280) | 1% (3 of 252) | 28 | 75% (21 of 28) | 9 | 8% (22 of 280) |
| 2024 | Bay Shore | 210 | 90% (188 of 210) | 6% (13 of 201) | 9 | 62% (5 of 8) | 5 | 8% (17 of 210) |
| 2024 | Class A | 108 | 86% (93 of 108) | 1% (1 of 94) | 14 | 58% (7 of 12) | 7 | 7% (8 of 108) |
| 2024 | Redwood Empire | 203 | 91% (185 of 203) | 2% (4 of 189) | 14 | 54% (7 of 13) | 10 | 4% (8 of 203) |
| 2024 | Tri-Valley | 292 | 92% (269 of 292) | 1% (3 of 272) | 20 | 84% (16 of 19) | 4 | 7% (19 of 292) |
| 2025 | Bay Shore | 197 | 92% (181 of 197) | 2% (4 of 185) | 12 | 100% (11 of 11) | 10 | 3% (6 of 197) |
| 2025 | Class A | 105 | 85% (89 of 105) | 6% (6 of 95) | 10 | 67% (6 of 9) | 5 | 10% (11 of 105) |
| 2025 | Redwood Empire | 216 | 90% (195 of 216) | 2% (4 of 199) | 17 | 64% (9 of 14) | 12 | 4% (9 of 216) |
| 2025 | Tri-Valley | 288 | 93% (267 of 288) | 1% (3 of 270) | 18 | 94% (17 of 18) | 6 | 5% (15 of 288) |
| 2026 | Bay Shore | 207 | 96% (198 of 207) | 2% (4 of 202) | 5 | 100% (5 of 5) | 3 | 3% (6 of 207) |
| 2026 | Class A | 101 | 86% (87 of 101) | 6% (6 of 93) | 8 | 43% (3 of 7) | 5 | 9% (9 of 101) |
| 2026 | Redwood Empire | 216 | 88% (190 of 216) | 2% (3 of 193) | 23 | 73% (16 of 22) | 9 | 8% (17 of 216) |
| 2026 | Tri-Valley | 294 | 93% (273 of 294) | 1% (4 of 277) | 17 | 93% (14 of 15) | 7 | 5% (14 of 294) |

**Area × event with empty lanes in 3+ of 5 seasons: 22**

| Area | Gender | Event | Seasons | Which | Total empty lanes |
|---|---|---|---|---|---|
| Tri-Valley | boys | 800 | 4 | 2023, 2024, 2025, 2026 | 8 |
| Tri-Valley | boys | 1600 | 4 | 2022, 2023, 2024, 2026 | 7 |
| Bay Shore | boys | 200 | 4 | 2022, 2023, 2024, 2026 | 6 |
| Tri-Valley | girls | 800 | 4 | 2023, 2024, 2025, 2026 | 6 |
| Bay Shore | boys | LJ | 4 | 2023, 2024, 2025, 2026 | 5 |
| Bay Shore | girls | LJ | 4 | 2022, 2023, 2024, 2026 | 5 |
| Tri-Valley | girls | 200 | 4 | 2022, 2023, 2025, 2026 | 5 |
| Redwood Empire | girls | DT | 4 | 2022, 2023, 2025, 2026 | 4 |
| Tri-Valley | girls | 3200 | 4 | 2022, 2024, 2025, 2026 | 4 |
| Tri-Valley | girls | HJ | 3 | 2022, 2023, 2026 | 8 |
| Redwood Empire | boys | 800 | 3 | 2024, 2025, 2026 | 6 |
| Bay Shore | girls | DT | 3 | 2022, 2023, 2024 | 5 |
| Bay Shore | girls | SP | 3 | 2022, 2023, 2024 | 5 |
| Bay Shore | boys | 300H | 3 | 2023, 2024, 2025 | 4 |
| Class A | girls | 1600 | 3 | 2022, 2024, 2026 | 4 |
| Redwood Empire | boys | 200 | 3 | 2023, 2024, 2025 | 4 |
| Redwood Empire | boys | LJ | 3 | 2022, 2024, 2026 | 4 |
| Bay Shore | girls | 1600 | 3 | 2023, 2024, 2025 | 3 |
| Class A | boys | HJ | 3 | 2023, 2025, 2026 | 3 |
| Class A | girls | 800 | 3 | 2024, 2025, 2026 | 3 |
| Class A | girls | TJ | 3 | 2023, 2024, 2025 | 3 |
| Redwood Empire | boys | 400 | 3 | 2022, 2024, 2026 | 3 |

**Area × event with unused spots in 3+ of 5 seasons: 51**

| Area | Gender | Event | Seasons | Which | Total unused spots |
|---|---|---|---|---|---|
| Redwood Empire | girls | 200 | 5 | 2022, 2023, 2024, 2025, 2026 | 10 |
| Tri-Valley | boys | 1600 | 5 | 2022, 2023, 2024, 2025, 2026 | 9 |
| Tri-Valley | girls | 800 | 5 | 2022, 2023, 2024, 2025, 2026 | 7 |
| Redwood Empire | boys | 200 | 5 | 2022, 2023, 2024, 2025, 2026 | 6 |
| Tri-Valley | boys | 800 | 4 | 2023, 2024, 2025, 2026 | 10 |
| Tri-Valley | girls | 1600 | 4 | 2022, 2023, 2024, 2025 | 10 |
| Tri-Valley | girls | 400 | 4 | 2023, 2024, 2025, 2026 | 10 |
| Tri-Valley | girls | HJ | 4 | 2022, 2023, 2024, 2026 | 10 |
| Bay Shore | boys | 800 | 4 | 2023, 2024, 2025, 2026 | 7 |
| Bay Shore | girls | 1600 | 4 | 2022, 2023, 2024, 2025 | 7 |
| Class A | girls | 1600 | 4 | 2022, 2023, 2024, 2026 | 7 |
| Redwood Empire | girls | LJ | 4 | 2022, 2023, 2024, 2025 | 7 |
| Tri-Valley | girls | 200 | 4 | 2022, 2023, 2025, 2026 | 7 |
| Bay Shore | boys | 200 | 4 | 2022, 2023, 2024, 2026 | 6 |
| Bay Shore | boys | LJ | 4 | 2023, 2024, 2025, 2026 | 6 |
| Bay Shore | girls | 800 | 4 | 2022, 2023, 2024, 2026 | 6 |
| Bay Shore | girls | LJ | 4 | 2022, 2023, 2024, 2026 | 6 |
| Class A | boys | 1600 | 4 | 2022, 2023, 2024, 2026 | 6 |
| Class A | girls | 800 | 4 | 2023, 2024, 2025, 2026 | 6 |
| Redwood Empire | boys | PV | 4 | 2022, 2023, 2024, 2026 | 6 |
| Redwood Empire | girls | 400 | 4 | 2022, 2024, 2025, 2026 | 6 |
| Redwood Empire | boys | LJ | 4 | 2022, 2024, 2025, 2026 | 5 |
| Class A | boys | 200 | 4 | 2022, 2023, 2025, 2026 | 4 |
| Class A | boys | LJ | 4 | 2022, 2023, 2024, 2026 | 4 |
| Redwood Empire | boys | 400 | 4 | 2022, 2024, 2025, 2026 | 4 |
| Redwood Empire | boys | TJ | 4 | 2023, 2024, 2025, 2026 | 4 |
| Redwood Empire | girls | DT | 4 | 2022, 2023, 2025, 2026 | 4 |
| Tri-Valley | girls | 3200 | 4 | 2022, 2024, 2025, 2026 | 4 |
| Redwood Empire | boys | 800 | 3 | 2024, 2025, 2026 | 7 |
| Tri-Valley | boys | 200 | 3 | 2023, 2025, 2026 | 7 |
| Bay Shore | boys | 300H | 3 | 2023, 2024, 2025 | 6 |
| Bay Shore | girls | SP | 3 | 2022, 2023, 2024 | 6 |
| Redwood Empire | boys | 1600 | 3 | 2023, 2025, 2026 | 6 |
| Redwood Empire | girls | TJ | 3 | 2022, 2024, 2026 | 6 |
| Bay Shore | boys | 1600 | 3 | 2022, 2024, 2026 | 5 |
| Bay Shore | girls | DT | 3 | 2022, 2023, 2024 | 5 |
| Redwood Empire | boys | HJ | 3 | 2023, 2024, 2026 | 5 |
| Tri-Valley | girls | LJ | 3 | 2023, 2025, 2026 | 5 |
| Bay Shore | girls | 4x400 | 3 | 2023, 2025, 2026 | 4 |
| Redwood Empire | boys | 4x400 | 3 | 2024, 2025, 2026 | 4 |
| Redwood Empire | girls | 1600 | 3 | 2022, 2023, 2024 | 4 |
| Tri-Valley | boys | LJ | 3 | 2022, 2023, 2024 | 4 |
| Tri-Valley | girls | 100H | 3 | 2022, 2023, 2026 | 4 |
| Class A | boys | 4x400 | 3 | 2022, 2024, 2025 | 3 |
| Class A | boys | HJ | 3 | 2023, 2025, 2026 | 3 |
| Class A | boys | TJ | 3 | 2022, 2023, 2026 | 3 |
| Class A | girls | 3200 | 3 | 2022, 2023, 2026 | 3 |
| Class A | girls | TJ | 3 | 2023, 2024, 2025 | 3 |
| Redwood Empire | boys | 110H | 3 | 2022, 2023, 2026 | 3 |
| Redwood Empire | girls | 100 | 3 | 2022, 2025, 2026 | 3 |
| Redwood Empire | girls | HJ | 3 | 2023, 2024, 2025 | 3 |

## 7. Limits of this analysis

- **Small samples.** Many cells hold a handful of athletes: at-large qualifiers outside
  Tri-Valley, Class A in general, and any single event. A few athletes can move a rate by
  10–30 points. Where the text says "consistent", it means the same direction across
  seasons, not a precisely measured gap.
- **Comparing marks across meets.** Section 5 compares marks made at different meets.
  Wind, weather, heats and competition differ. The result also depends on how the MOC
  cutoff is defined; see the note at the top.
- **Statistical tests.** The §4 p-values are pooled over five seasons and all events.
  They support a consistent direction, not a precise gap, and they say nothing about
  causes.
- **Rules before 2026 are partly assumed.**
  - Allocation numbers for 2022–2025 are assumed to equal 2026's.
  - Each season's at-large standards come from its printed results, except 2023, where
    none were printed and 2026's are used.
- **Unresolved school names.**
  - "West County" (2022, 12 program entries) is kept unmatched pending confirmation that
    it is Analy.
  - A few other truncated names are also unmatched: 15 entries in 2022 and 5 in 2023.
  - These athletes appear as "Unknown" and aren't compared.
- **State results pending.** State qualification isn't included yet.
- **What the rules replay can't see.**
  - Scratches after the program was printed.
  - Why an athlete chose one event over another.
  - Whether a vacancy was offered and declined.
- **Replacements.** Only replacements from the same Area are recognised; that setting
  matched the programs best.

## 5-season pooled summary (2022–2026 combined)

*Pooling combines different seasons, rule details and fields. Use it for the overall
picture only; the per-season tables above are primary.*

| Area | Share of qualified field | At-large spots held | Automatic: top finish | At-large (combined): top finish | Lowest autos: top finish vs other Areas' at-large | Empty lanes | No-shows |
|---|---|---|---|---|---|---|---|
| Tri-Valley | 35% (1424 of 4024) | 70% (464 of 659) | 64% (576 of 902) | 15% (61 of 406) | 36% (106 of 293) vs 9% (14 of 162) | 6% (85 of 1424) | 2% (21 of 1329) |
| Bay Shore | 25% (1023 of 4024) | 9% (61 of 659) | 32% (285 of 877) | 5% (3 of 57) | 9% (25 of 284) vs 14% (72 of 511) | 5% (54 of 1023) | 4% (37 of 971) |
| Redwood Empire | 26% (1064 of 4024) | 15% (102 of 659) | 30% (263 of 870) | 13% (10 of 79) | 8% (22 of 277) vs 13% (65 of 489) | 6% (68 of 1064) | 2% (24 of 973) |
| Class A | 13% (513 of 4024) | 5% (32 of 659) | 21% (87 of 414) | 4% (1 of 26) | 5% (7 of 132) vs 14% (74 of 542) | 8% (40 of 513) | 4% (19 of 459) |
