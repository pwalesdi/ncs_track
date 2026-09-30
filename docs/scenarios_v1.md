# Alternative MOC allocations, simulated (scenarios v1)

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

## The current system (6-6-6-3 + 3 next best mark), the baseline

Replayed with pass-down routes on each season's real declarations; it reproduces what actually
happened (0 athletes added, 0 removed). Over 2022–2026: 3,944 athletes in the fields
(3,358 automatic, 512 next best mark,
74 at-large standard).
- **Field share by Area:** Tri-Valley 1,371 athletes (35%); Bay Shore 1,020 athletes (26%); Redwood Empire 1,048 athletes (27%); Class A 505 athletes (13%).
- **Faster but left out:** 1,575 left-out athletes beat at least one automatic qualifier from another
  Area (1,073 athletes with Class A qualifiers excluded from the comparison), out of
  8,587 left-out finishers.
- **Merit capture:** 3,463 marks of the 3,836 top-24 Area marks per event were in the
  field (90%).

## Scenario 5-5-5-3: 5/5/5/3 automatic + 6 next best mark

**What changes vs. current, 2022–2026 pooled.** 165 athletes would have been in the field who
weren't in reality, and 158 athletes who were in reality would have been out. The field holds
2,888 automatic qualifiers, 1,019 next-best-mark qualifiers
and 48 at-large standard qualifiers (3,955 athletes; current 3,944 athletes).

**Who gains and who loses spots, by Area (pooled).**

| Area | Added | Removed | Net | Field under 5-5-5-3 | Field under current | Removed who made the MOC final |
|---|---|---|---|---|---|---|
| Tri-Valley | 123 added | 1 removed | +122 | 1496 (38%) | 1371 (35%) | not shown (fewer than 5 removed) |
| Bay Shore | 13 added | 85 removed | -72 | 948 (24%) | 1020 (26%) | 0 athletes |
| Redwood Empire | 16 added | 72 removed | -56 | 993 (25%) | 1048 (27%) | 1 athlete |
| Class A | 13 added | 0 removed | +13 | 518 (13%) | 505 (13%) | 0 athletes |

- **Faster but left out:** 1,209 left-out athletes beat at least one automatic qualifier from another
  Area, against 1,575 athletes under current. With Class A qualifiers excluded from the comparison:
  582 athletes, against 1,073 athletes.
- **Cost (removed finalists):** of the 158 removed athletes, 1 athlete made the MOC final in
  reality.
- **Estimated gain (estimate — different meets):** of the 165 added athletes,
  4 athletes had an Area mark at or better than that season's MOC final cutoff.
- **Merit capture:** 3,594 marks of 3,836 top-24 Area marks in the field
  (94%; current 90%).

**Per season.**

| Season | Added | Removed | Faster but left out (Class A in) | Faster but left out (Class A out) | Removed who made the final | Estimated gain | Merit capture |
|---|---|---|---|---|---|---|---|
| 2022 | 30 added | 29 removed | 243 athletes (current 328) | 101 athletes (current 225) | 0 athletes | 0 athletes | 719 of 765 (94%) |
| 2023 | 30 added | 28 removed | 243 athletes (current 297) | 96 athletes (current 191) | 1 athlete | 4 athletes | 723 of 768 (94%) |
| 2024 | 37 added | 31 removed | 172 athletes (current 258) | 72 athletes (current 162) | 0 athletes | 0 athletes | 733 of 767 (96%) |
| 2025 | 37 added | 35 removed | 289 athletes (current 364) | 172 athletes (current 271) | 0 athletes | 0 athletes | 704 of 768 (92%) |
| 2026 | 31 added | 35 removed | 262 athletes (current 328) | 141 athletes (current 224) | 0 athletes | 0 athletes | 715 of 768 (93%) |

## Scenario 4-4-4-3: 4/4/4/3 automatic + 9 next best mark

**What changes vs. current, 2022–2026 pooled.** 251 athletes would have been in the field who
weren't in reality, and 250 athletes who were in reality would have been out. The field holds
2,403 automatic qualifiers, 1,505 next-best-mark qualifiers
and 41 at-large standard qualifiers (3,949 athletes; current 3,944 athletes).

**Who gains and who loses spots, by Area (pooled).**

| Area | Added | Removed | Net | Field under 4-4-4-3 | Field under current | Removed who made the MOC final |
|---|---|---|---|---|---|---|
| Tri-Valley | 180 added | 3 removed | +177 | 1551 (39%) | 1371 (35%) | not shown (fewer than 5 removed) |
| Bay Shore | 19 added | 135 removed | -116 | 904 (23%) | 1020 (26%) | 0 athletes |
| Redwood Empire | 28 added | 112 removed | -84 | 965 (24%) | 1048 (27%) | 2 athletes |
| Class A | 24 added | 0 removed | +24 | 529 (13%) | 505 (13%) | 0 athletes |

- **Faster but left out:** 976 left-out athletes beat at least one automatic qualifier from another
  Area, against 1,575 athletes under current. With Class A qualifiers excluded from the comparison:
  253 athletes, against 1,073 athletes.
- **Cost (removed finalists):** of the 250 removed athletes, 2 athletes made the MOC final in
  reality.
- **Estimated gain (estimate — different meets):** of the 251 added athletes,
  4 athletes had an Area mark at or better than that season's MOC final cutoff.
- **Merit capture:** 3,662 marks of 3,836 top-24 Area marks in the field
  (95%; current 90%).

**Per season.**

| Season | Added | Removed | Faster but left out (Class A in) | Faster but left out (Class A out) | Removed who made the final | Estimated gain | Merit capture |
|---|---|---|---|---|---|---|---|
| 2022 | 51 added | 42 removed | 217 athletes (current 328) | 56 athletes (current 225) | 0 athletes | 0 athletes | 729 of 765 (95%) |
| 2023 | 48 added | 49 removed | 199 athletes (current 297) | 36 athletes (current 191) | 2 athletes | 4 athletes | 736 of 768 (96%) |
| 2024 | 45 added | 44 removed | 137 athletes (current 258) | 23 athletes (current 162) | 0 athletes | 0 athletes | 743 of 767 (97%) |
| 2025 | 56 added | 57 removed | 220 athletes (current 364) | 78 athletes (current 271) | 0 athletes | 0 athletes | 723 of 768 (94%) |
| 2026 | 51 added | 58 removed | 203 athletes (current 328) | 60 athletes (current 224) | 0 athletes | 0 athletes | 731 of 768 (95%) |

## Scenario 3-3-3-3: 3/3/3/3 automatic + 12 next best mark

**What changes vs. current, 2022–2026 pooled.** 288 athletes would have been in the field who
weren't in reality, and 297 athletes who were in reality would have been out. The field holds
1,925 automatic qualifiers, 1,977 next-best-mark qualifiers
and 37 at-large standard qualifiers (3,939 athletes; current 3,944 athletes).

**Who gains and who loses spots, by Area (pooled).**

| Area | Added | Removed | Net | Field under 3-3-3-3 | Field under current | Removed who made the MOC final |
|---|---|---|---|---|---|---|
| Tri-Valley | 213 added | 3 removed | +210 | 1584 (40%) | 1371 (35%) | not shown (fewer than 5 removed) |
| Bay Shore | 18 added | 167 removed | -149 | 871 (22%) | 1020 (26%) | 1 athlete |
| Redwood Empire | 32 added | 127 removed | -95 | 954 (24%) | 1048 (27%) | 2 athletes |
| Class A | 25 added | 0 removed | +25 | 530 (13%) | 505 (13%) | 0 athletes |

- **Faster but left out:** 880 left-out athletes beat at least one automatic qualifier from another
  Area, against 1,575 athletes under current. With Class A qualifiers excluded from the comparison:
  108 athletes, against 1,073 athletes.
- **Cost (removed finalists):** of the 297 removed athletes, 3 athletes made the MOC final in
  reality.
- **Estimated gain (estimate — different meets):** of the 288 added athletes,
  4 athletes had an Area mark at or better than that season's MOC final cutoff.
- **Merit capture:** 3,696 marks of 3,836 top-24 Area marks in the field
  (96%; current 90%).

**Per season.**

| Season | Added | Removed | Faster but left out (Class A in) | Faster but left out (Class A out) | Removed who made the final | Estimated gain | Merit capture |
|---|---|---|---|---|---|---|---|
| 2022 | 53 added | 49 removed | 196 athletes (current 328) | 26 athletes (current 225) | 0 athletes | 0 athletes | 733 of 765 (96%) |
| 2023 | 54 added | 58 removed | 182 athletes (current 297) | 10 athletes (current 191) | 3 athletes | 4 athletes | 742 of 768 (97%) |
| 2024 | 51 added | 52 removed | 131 athletes (current 258) | 10 athletes (current 162) | 0 athletes | 0 athletes | 747 of 767 (97%) |
| 2025 | 69 added | 70 removed | 193 athletes (current 364) | 38 athletes (current 271) | 0 athletes | 0 athletes | 736 of 768 (96%) |
| 2026 | 61 added | 68 removed | 178 athletes (current 328) | 24 athletes (current 224) | 0 athletes | 0 athletes | 738 of 768 (96%) |


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
