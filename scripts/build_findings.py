"""Build docs/findings_v1.md from data/summary/ only.

    .venv/bin/python scripts/build_findings.py

The tables are regenerated from the summary tables each time. The narrative sentences
were written against the 2026-09-30 build (pass-down routes); if the data changes, reread them.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import findings_tables as T  # noqa: E402

from ncs_track import paths  # noqa: E402

DOC = f"""# What the data shows: MOC qualification by Area, 2022–2026 (findings v1)

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

{T.makeup()}

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

{T.spots()}

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

{T.results(types=("automatic", "at_large_combined"))}

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

{T.core(groups_only=["all"])}

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

{T.tests()}

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

{T.core(pooled_only=True)}

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

{T.leftout()}

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

{T.pooled()}
"""

if __name__ == "__main__":
    out = paths.ROOT / "docs" / "findings_v1.md"
    out.write_text(DOC)
    print(f"wrote {out.relative_to(paths.ROOT)}")
