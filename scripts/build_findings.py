"""Build docs/findings_v1.md from data/summary/ only.

    .venv/bin/python scripts/build_findings.py

The tables are regenerated from the summary tables each time. The narrative sentences
were written against the 2026-09-30 build; if the data changes, reread them.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import findings_tables as T  # noqa: E402

from ncs_track import paths  # noqa: E402

DOC = f"""# What the data shows: MOC qualification by Area, 2022–2026 (findings v1)

*For coaches and the committee. Built from the tables in `data/summary/`; every column is defined in
`docs/analysis_tables.md`. Rates always show their count, e.g. "42% (11 of 26)".*

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

{T.makeup()}

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

{T.atlarge()}

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

{T.results(types=("automatic", "at_large_combined"))}

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

{T.core(groups_only=["all"])}

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

**How confident can we be?** Pooled over five seasons, a simple two-proportion test finds
each gap unlikely to be chance alone:
- **Bay Shore:** 9% (25 of 284) vs 14% (72 of 511), p ≈ 0.03
- **Redwood Empire:** 8% (22 of 277) vs 13% (65 of 489), p ≈ 0.02
- **Class A:** 5% (7 of 132) vs 14% (74 of 542), p ≈ 0.008
- **Tri-Valley:** 36% (106 of 293) vs 9% (14 of 162), p < 0.001

These tests treat every athlete-event as independent. They aren't: the same athlete can
appear in several events and seasons, so the true uncertainty is larger than the p-values
suggest. They also don't adjust for making many comparisons. The direction is consistent
across seasons; the size of the gap for any single season or event group is not well
determined.

**By event group (5 seasons pooled; single seasons are in `data/summary/core_comparison.csv`)**

{T.core(pooled_only=True)}

By event group the counts get small (often 15–40 athletes on the automatic side), so treat
these as indications.

## 5. Left-out athletes

For each Area and event, we took the three best athletes who did *not* qualify, ranked by
their Area mark. We then checked whether that mark was at or better than the MOC top-8
mark that year (top 9 in the long jump, triple jump, shot put and discus).

**Caveat: these marks come from different meets**, with different days, wind, weather,
competition and (in field events) attempts. A good Area mark doesn't mean the athlete
would have finished that high at the MOC. This is a comparison, not a prediction.

**What the data shows.**
- **How often it happens.** Between 0% and 11% of an Area's best non-qualifiers had a mark
  at or better than the MOC cutoff.
- **Tri-Valley has the most in 4 of 5 seasons**, e.g. 11% (11 of 96) in 2023. Its
  non-qualifiers include 7th–12th-place finishers from a deep meet.
- **2026 comes from one race.** Every Area shows 3% (3 of 96), and all 12 come from the
  boys 4x400: the 8th-place team in that MOC final ran 3:59.34, nearly 30 seconds behind
  7th. Without that event, 2026 has none in any Area.

{T.leftout()}

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

{T.utilization()}

## 7. Limits of this analysis

- **Small samples.** Many cells hold a handful of athletes: at-large qualifiers outside
  Tri-Valley, Class A in general, and any single event. A few athletes can move a rate by
  10–30 points. Where the text says "consistent", it means the same direction across
  seasons, not a precisely measured gap.
- **Comparing marks across meets.** Section 5 compares marks made at different meets.
  Wind, weather, heats and competition differ.
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
| Tri-Valley | {T.rate(1424, 4024)} | {T.rate(464, 659)} | {T.rate(576, 902)} | {T.rate(61, 406)} | {T.rate(106, 293)} vs {T.rate(14, 162)} | {T.rate(85, 1424)} | {T.rate(21, 1329)} |
| Bay Shore | {T.rate(1023, 4024)} | {T.rate(61, 659)} | {T.rate(285, 877)} | {T.rate(3, 57)} | {T.rate(25, 284)} vs {T.rate(72, 511)} | {T.rate(54, 1023)} | {T.rate(37, 971)} |
| Redwood Empire | {T.rate(1064, 4024)} | {T.rate(102, 659)} | {T.rate(263, 870)} | {T.rate(10, 79)} | {T.rate(22, 277)} vs {T.rate(65, 489)} | {T.rate(68, 1064)} | {T.rate(24, 973)} |
| Class A | {T.rate(513, 4024)} | {T.rate(32, 659)} | {T.rate(87, 414)} | {T.rate(1, 26)} | {T.rate(7, 132)} vs {T.rate(74, 542)} | {T.rate(40, 513)} | {T.rate(19, 459)} |
"""

if __name__ == "__main__":
    out = paths.ROOT / "docs" / "findings_v1.md"
    out.write_text(DOC)
    print(f"wrote {out.relative_to(paths.ROOT)}")
