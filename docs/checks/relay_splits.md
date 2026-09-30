# Check: relay splits mislabelled as individual 400/800 rows

Run 2026-09-29 on all 25 Athletic.net files (2022–2026: MOC, Tri-Valley, Bay Shore,
Redwood Empire, Class A). Re-run with `.venv/bin/python scripts/checks/relay_splits.py`.

**Result: no meet has relay-split legs mislabelled as individual 400 m or 800 m rows.**

## Why it was checked

Athletic.net labels relay splits "400 Meters (Relay Split)" / "800 Meters (Relay Split)".
Most files have those rows in groups of 4 or 8. The 2023 MOC file (483067) has none. The
question was whether the 2023 splits had leaked into the individual 400/800 instead.

## Method and results

1. **Row counts.** At every MOC 2022–2026 the individual events have 24–29 prelim rows and
   7–13 final rows per gender. The 2023 MOC has 24 + 8 (400 m) and 24–25 + 12 (800 m) per
   gender. The Area meets have 23–27 rows, except Class A (below).
2. **Row-level signs, all 25 files.**
   - No `athlete_id` appears twice in one event and round. A split row for a leg who also
     ran the open event would repeat that athlete's ID.
   - No blank `athlete_id` values.
   - No individual row has relay columns filled.
3. **Against independent sources.**
   - **MOC programs:** Athletic.net 400/800 prelim counts equal the program entry counts in
     all 20 cases (5 seasons × 2 genders × 2 events).
   - **Hy-Tek results:** all 5 MOCs, Tri-Valley 2022–2026 and Bay Shore 2024. 1,268
     Athletic.net rows were checked against 1,232 Hy-Tek rows. Every Athletic.net row
     matched a Hy-Tek athlete, except:
     - **36 DNS/DQ rows.** Hy-Tek leaves out non-starters.
     - **49 rows** with the same athlete spelled differently. Examples: a short first name
       versus the full name, a surname with a hyphen or an extra letter, or a double
       surname shown as one name. Each pairs one-for-one with an unmatched Hy-Tek row in the
       same event and round.
   - No row is left unexplained.

2023 MOC in particular: 400/800 counts equal the program, and every row matches Hy-Tek,
apart from four spelling variants and one DNS in the boys 400 final. That file has no
split rows because none were published, not because they were relabelled.

## Not independently checkable

Redwood Empire and Class A (all years), and Bay Shore outside 2024, have no Hy-Tek file.
They pass the row-level checks only. Two notes, neither blocking:

- **2025 Class A 400 m field size (warning).** 35 girls rows and 28 boys rows, against
  14–23 in other Class A years. There are no repeated IDs, and 3 rows are DNS. This looks
  like a genuinely large field but is unconfirmed. Validation logs it as a warning.
- **2023 Class A has no relay-leg IDs.** None of its 400/800 runners appears as a relay
  leg, while every other file has some. Relay-leg data for that meet is empty.
