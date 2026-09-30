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
`docs/analysis_tables.md`. Every number carries its unit, e.g. "25 of 284 entries finished top 8 (9%)".*

> **What changed in this update (2026-09-30, second update)**
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
> - **First update (same day).** §5 uses the all-rounds MOC cutoff; §4 adds the permutation
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
- **Top 8:** 8th place or better in the MOC final (9th in the long jump, triple jump, shot
  put and discus). **Scored:** 6th or better.
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

{T.makeup()}

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

{T.spots()}

## 3. MOC results by Area and route

Entries that competed at the MOC. To keep the table readable, only automatic and next best
mark + at-large standard qualifiers are shown. The full breakdown, including replacements,
is in `data/summary/moc_performance.csv`.

**What the data shows.**
- **Automatic qualifiers.** Tri-Valley's finished top 8 in 62–65% of entries each season.
  Bay Shore's did in 31–34%, Redwood Empire's in 26–34%, and Class A's in 8–32%.
- **Class A varies most:** 7 of 83 entries finished top 8 in 2026 (8%), but 27 of 84 in
  2024 (32%).
- **Next best mark + at-large qualifiers** finished top 8 far less often than automatic
  qualifiers, in every Area and season. Outside Tri-Valley these groups are small, often
  under 20 entries, so their rates move a lot with one or two athletes.

{T.results(types=("automatic", "at_large_combined"))}

## 4. The core question: do some Areas' last automatic qualifiers do worse at the MOC than other Areas' next-best-mark + at-large qualifiers?

**The comparison.**
- **Lowest automatic qualifiers:** each Area's automatic qualifiers who placed 5th or 6th
  at their Area meet (3rd for Class A).
- **Next best mark + at-large qualifiers from the other three Areas.**
- **Who is counted:** only entries that competed at the MOC, with genders combined.

**Two measures.**
- **Top-8 rate.**
- **Median MOC place.** Finalists keep their final place; everyone else is ranked after the
  finalists by their best MOC mark. Lower is better.

Groups under 5 entries show counts only.

**Per season, all events**

{T.core(groups_only=["all"])}

**What the data shows.**
- **Bay Shore, Redwood Empire and Class A.** In most seasons, their lowest automatic
  qualifiers finished top 8 *less* often than the other Areas' next-best-mark + at-large
  qualifiers, and had a worse median place.
  - Redwood Empire and Class A: lower in all 5 seasons.
  - Bay Shore: lower in 4 of 5 seasons; 2025 was the exception.
  - Several single-season gaps are small. In 2024, Bay Shore's lowest automatics had 7 of
    57 entries finish top 8, against 13 of 102 entries for the comparison group.
  - Each season's result rests on 0–8 top-8 finishes on the automatic side.
- **Tri-Valley.** The opposite, by a wide margin: 28–49% of its 5th–6th-place automatic
  entries finished top 8, against 3–18% of the other Areas' next-best-mark + at-large
  entries.
- **Who the comparison group is.** Tri-Valley holds most next-best-mark and at-large spots
  (§2), so for Bay Shore, Redwood Empire and Class A the comparison group is mostly
  Tri-Valley athletes. Across all five seasons, entries from next-best-mark + at-large
  qualifiers finished top 8 as follows:
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

{T.tests()}

**Reading the tests.**
- **Every result holds.** No Area's result weakens under the stronger tests; every
  p-value stays below 0.03.
- **Why the clustered p-values are a little smaller than the old ones.** Athletes rarely
  repeat (about 1.15 rows per athlete), so allowing for repeats changes little. The old
  test's pooled standard error is conservative when the two rates differ.
- **What the permutation test adds.** With random Area labels, a lowest-automatic group
  would be expected to finish top 8 about 2–4 percentage points *more* often than the
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

{T.core(pooled_only=True)}

By event group the counts get small (often 15–40 entries on the automatic side), so treat
these as indications. The dashboard's "Area place vs. MOC finish" tab shows every Area
place from 1st to 12th.

## 5. Left-out athletes

For each Area and event, we took the three best athletes who did *not* qualify, ranked by
their Area mark. We then checked whether that mark was at or better than the MOC top-8 mark
that year (top 9 in the long jump, triple jump, shot put and discus).

**The cutoff.** The 8th-best valid MOC mark that year (9th in LJ/TJ/SP/DT), across prelims
and finals combined, one mark per athlete.

**Caveat: these marks come from different meets**, with different days, wind, weather,
competition and (in field events) attempts. A good Area mark doesn't mean the athlete would
have finished that high at the MOC. This is a comparison, not a prediction.

**What the data shows.**
- **Almost never.** In 19 of the 20 Area-seasons, none of an Area's best non-qualifiers had
  a mark at or better than the MOC cutoff.
- **The exception is 2023 Tri-Valley:** 6 of 96 best non-qualifiers (6%), in the boys 200
  and 400 and the girls 200 and discus.
  - The 2023 MOC marks were unusually slow; a 22.93 won a boys 200 prelim heat.
  - 2023 at-large standards are assumed from 2026, so Tri-Valley's places 7–14 in the boys
    200 all qualified, and its best non-qualifiers were 15th.

{T.leftout()}

## 6. Spot use

**The segments.**
- **Competed:** the Area's qualifier competed at the MOC.
- **Refilled:** the Area's qualifier withdrew before the entry deadline, and the next
  finalist from that Area took the spot.
- **Unfilled (provisional, under verification):** a guaranteed spot nobody used. The
  qualifier didn't compete, nobody replaced them, and the event's MOC field (athletes who
  competed in the first round) ended below 24.
- **Other unused:** a qualifier didn't use the spot, but no gap followed. Either the field
  still had 24, or the spot came from the at-large standard, which has no fixed number.

**Why the first count was too high.** It counted every unused spot that wasn't refilled.
- **It counted spots that didn't shorten the field.** For example, over five seasons
  Tri-Valley's boys 800 showed 8 unused, unreplaced spots. All 8 of those athletes ran other MOC
  events instead: the 1600, the 4x800, or four other events. 2 were at-large qualifiers,
  whose spots have no fixed number. The MOC boys 800 field had at least 24 entries every
  season, and fell below 24 competitors only in 2025.
- **The corrected count** keeps 2 unfilled spots there, and 121 of 3,890 guaranteed spots
  over all Areas and five seasons.

**What the data shows.**
- **Competed:** 85–96% of spots earned were used by the Area's own qualifier, by Area and
  season.
- **Unfilled:** 1–6% of guaranteed spots per Area and season (provisional).
- **No-shows:** 1–6% of entries.
- **Double qualifiers:** most qualifiers who didn't enter an event ran a different MOC
  event.
- **Flag list.** 4 Area × event combinations had unfilled spots in 3 or more of the 5
  seasons, each with 4–5 unfilled spots in total. Counting any unused spot gives 51
  combinations.

{T.use()}

## 7. Limits of this analysis

- **Small samples.** Many groups hold a handful of entries: next-best-mark and at-large
  qualifiers outside Tri-Valley, Class A in general, and any single event. A few athletes
  can move a rate by 10–30 percentage points. Where the text says "consistent", it means
  the same direction across seasons, not a precisely measured gap.
- **Comparing marks across meets.** Section 5 compares marks made at different meets, with
  different wind, weather, heats and competition.
- **Statistical tests.** The §4 p-values are pooled over five seasons and all events. They
  support a consistent direction, not a precise gap, and say nothing about causes.
- **Unfilled spots are provisional.** They depend on how the MOC field is counted: athletes
  who competed in the first round.
- **Rules before 2026 are partly assumed.**
  - Allocation numbers for 2022–2025 are assumed to equal 2026's.
  - Each season's at-large standards come from its printed results, except 2023, where
    none were printed and 2026's are used.
- **Unresolved school names.** "West County" (2022, 12 program entries) is kept unmatched
  pending confirmation that it is Analy. A few truncated names are also unmatched (15
  entries in 2022, 5 in 2023). These appear as "Unknown" and aren't compared.
- **Privacy.** MOC-place figures (top-8 counts, medians) are published only for groups of 5
  or more entries.
- **State results pending.** State qualification isn't included yet.
- **What the rules replay can't see.** Scratches after the program was printed, why an
  athlete chose one event over another, and whether a vacancy was offered and declined.
- **Replacements.** Only replacements from the same Area are recognised; that setting
  matched the programs best.

## 5-season pooled summary (2022–2026 combined)

*Pooling combines different seasons, rule details and fields. Use it for the overall
picture only; the per-season tables above are primary.*

{T.pooled()}
"""

if __name__ == "__main__":
    out = paths.ROOT / "docs" / "findings_v1.md"
    out.write_text(DOC)
    print(f"wrote {out.relative_to(paths.ROOT)}")
