# NCS Track & Field Qualification Analysis — Repo Audit

Audit date: 2026-09-29. Nothing in the repo was modified, moved, or deleted. The only
new files are `docs/audit.md` (this file) and `data/reference/meets.csv`.

Figures below come from a throwaway parser that was run over the files. It lives
outside the repo and is not part of the project.

---

## 1. Inventory

### 1.1 What is in the repo

The repo (`/Users/pwalesdinan/Developer/ncs_track`) holds **12 files, all in the repo
root, with no subdirectories.** It is **not a git repository**. There are no hidden
files (`.git`, `.ipynb_checkpoints`, `.env`) and no config.

- **Scripts, notebooks, or code:** none.
- **CSV, Excel, or database files:** none.
- **Athletic.net exports:** none.
- **Previous attempt's code or outputs:** not present. The accuracy problems can't be
  traced to specific code, so §2 audits the *data* for the hazards you listed. The
  hazards are real in this data and any naive parser would hit them.

| File | Format | Meet | Varsity events | Varsity rows (prelim / final) | Adaptive rows |
|---|---|---|---|---|---|
| `2019_NCS_Meet_of_Champions_results.htm` | Hy-Tek text (`<pre>`), "Event N" headers, CRLF | MOC 5/17–18/2019, DVC | 35* | 436 / 528 | 59 |
| `2019_NCS_Tri_Valley_Area_Championships_results.htm` | Hy-Tek text, **no** "Event N" headers, CRLF | Tri-Valley 5/11/2019, Dublin HS | 32 | – / 734 | 50 |
| `2022_NCS_Meet_of_Champions_results.htm` | Hy-Tek, "Event N" | MOC 5/20–21/2022, Dublin HS | 34* | 428 / 514 | 50 |
| `2022_NCS_Tri_Valley_Area_Championships_results.htm` | Hy-Tek, "Event N" | Tri-Valley 5/14/2022, Freedom HS | 32 | – / 707 | 56 |
| `2023_NCS_Meet_of_Champions_results.htm` | Hy-Tek, "Event N" | MOC 5/19–20/2023, Dublin HS | 35* | 441 / 526 | 72 |
| `2023_NCS_Tri_Valley_Area_Championships_results.htm` | Hy-Tek, "Event N" | Tri-Valley 5/13/2023, Foothill HS | 34 | – / 764 | 77 |
| `2024_NCS_Meet_of_Champions_results.htm` | Hy-Tek, "Event N" | MOC 5/17–18/2024, Dublin HS | 34 | 446 / 516 | 71 |
| `2024_NCS_Tri_Valley_Area_Championships_results.htm` | Hy-Tek, **no** "Event N" | Tri-Valley 5/11/2024, Pittsburg HS | 34 | – / 753 | 86 |
| `2025_NCS_Meet_of_Champions_results.htm` | Hy-Tek, "Event N" | MOC 5/23–24/2025, Dublin HS | 34 | 438 / 522 | 68 |
| `2025_NCS_Tri_Valley_Area_Championships_results.html` | **Diablo Timing index page. It has links only and NO RESULTS.** | Tri-Valley 5/17/2025, Clayton Valley HS | 0 | 0 | 0 |
| `2026_NCS_Meet_of_Champions_results.htm` | Hy-Tek, **no** "Event N" | MOC 5/22–23/2026, Dublin HS | 34 | 451 / 519 | 97 |
| `2026_NCS_Tri_Valley_Area_Championships_results.htm` | Hy-Tek, "Event N" | Tri-Valley 5/16/2026, Foothill HS | 34 | – / 772 | 0 |

\* Includes one-off event blocks: `4x800 Relay Exhibition` (2019, 2022),
`Girls 300 Meter Hurdles Heat 1 Rerun` (2019 MOC), and `Boys High Jump Jump Off` (2023 MOC).

"Rows" means placed or `--` result lines (one per athlete or relay team). Relay leg lines
are not counted.

### 1.2 Coverage against the project's scope

| Season | MOC | Tri-Valley | Bay Shore | Redwood Empire | Class A | League meets |
|---|---|---|---|---|---|---|
| 2019 | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| 2022 | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| 2023 | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| 2024 | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| 2025 | ✅ | ⚠️ index page only | ❌ | ❌ | ❌ | ❌ |
| 2026 | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

**Coverage summary:** 11 of the 30 needed area and MOC result sets are usable, and none
of the roughly 90 league meets are present. Three of the four areas have no data at all.
Any earlier analysis that compared areas could not have used real results for Bay Shore,
Redwood Empire, or Class A.

The 2025 Tri-Valley page links to `results.htm`, `results.pdf`, and per-event
`diablotiming.com/readHytek/getResults.php?file=250517F0NN.htm&dir=2025-05-17` URLs, so
the missing results are probably still recoverable.

### 1.3 How athletes are identified

- **Athletic.net IDs: none.** No file has an athlete, team, or meet ID of any kind.
- **Athletes** appear as `Last, First` plus grade (`9`–`12`, sometimes blank) plus a
  school string.
- **Relays** show a school string plus four legs, formatted `Last, First Grade`.
- **School strings** come in two widths, depending on the file and even the event:
  - truncated to 12 characters (`San Ramon Va`, `Moreau Catho`, `Livermore (N`)
  - full length, with an inconsistent `(Nc)` suffix (`Acalanes (Nc)` next to `Carondelet`)

Identity can therefore only be inferred from names, and the name data is dirty (§2.1).

---

## 2. Accuracy hazards found

Each subsection maps to a concern from the brief.

### 2.1 Joins or dedupes on names instead of IDs ⚠️ HIGH

The source data has no IDs, so any athlete join is a name join. Measured problems:

- **School strings.**
  - 259 distinct raw school strings collapse to about 139 schools. 100 schools have
    more than one spelling.
  - Examples of the variants:
    - `Amador Valle` / `Amador Valley` / `Amador Valley (Nc)`
    - `Bishop O'Dow` / `Bishop O'Dowd` / `Bishop Odowd (Nc)`
    - `De La Salle` / `DeLaSalle`
    - `De Anza` / `DeAnza`
    - `St. Marys` / `St. Mary's`
    - `Saint Mary's College`
  - **12-character truncation causes collisions:** `California C` and `California S`
    are different schools that share the prefix `California`. Truncation also cuts the
    suffix (`Livermore (N`, `Santa Rosa (`).
- **Renamed schools and possible transfers.**
  - 34 cases have the same athlete name, same gender, and different schools across
    files. Several are renames:
    - `Analy` ↔ `West County`
    - `San Francisco University` ↔ `University-SF`
    - `Kennedy (Fremont)` ↔ `Kennedy JFK`-style variants
  - Other cases may be transfers or two different people (`Lindgren, Jessamy`:
    Salesian and John Swett).
- **One athlete, several spellings.**
  - In the same season, school, and surname, different events list different first names:
    - `Fairlie, Nick` / `Fairlie, Nicholas` (2019)
    - `Vantassel, Breana` / `Vantassel, Brenee'` (2019)
    - `Quist, Manu` / `Quist, Manolo` (2022)
  - Relay legs add nickname forms such as `Quenby, Rosalind (Mae)` versus
    `Quenby, Rosalind Mae`.
- **Grade inconsistencies.** For example, `Hartigan, Julia` (San Ramon Valley) is listed as
  grade 11 in both 2022 and 2023. A dedupe that uses grade + name + school can split one
  athlete into two, or merge two athletes into one.
- **Missing grades.** 22 individual varsity rows have no grade.

### 2.2 Prelim and final marks mixed ⚠️ HIGH

- **MOC files contain both rounds.** Every running event except the 3200 and the 4x800
  has a `Preliminaries` block *and* a `Finals` block. The same athletes appear twice with
  different marks.
- **What goes wrong with naive handling:**
  - Reading every row double-counts finalists.
  - Keeping only `Finals` loses about 440 non-finalists per year, whose only mark is
    their prelim mark.
  - Taking the "best mark" mixes rounds.
- **Round is not always labelled.** In some files the round comes from a section line
  (`Preliminaries` / `Finals`). In others it is shown only by the column header
  (`Prelims` vs `Finals`). 2019, 2022, and 2023 have event blocks with **no** section line.
- **Area meets are single-round.** Tri-Valley running events are timed finals across
  heats (`H#` column), so every row there is a "final".
- **Anomalous duplicate blocks** each create a second set of rows for the same athletes
  in the same event:
  - `Girls 300 Meter Hurdles Heat 1 Rerun` (2019 MOC)
  - `Boys High Jump Jump Off` (2023 MOC)
  - Jump-off annotations inside rows (2023 and 2025 MOC)

### 2.3 Hardcoded allocation numbers ⚠️ HIGH

- **The rules changed between seasons.** The number of `NCS`-tagged (MOC-qualifying)
  rows at Tri-Valley varies widely:

  | Season | NCS-tagged rows |
  |---|---|
  | 2019 | 139 |
  | 2022 | 106 |
  | 2024 | 204 |
  | 2026 | 234 |

  Any single hardcoded allocation would be wrong for most seasons.
- **At-large standards also change by year.** For example, the Girls 100 m standard was
  `12.55 NCS At-Large` in 2019 and `12.50` in 2024.
- **The standard lines are missing in several files.** 2023 Tri-Valley, 2019/2022/2023
  MOC, and 2026 MOC have no "At-Large" lines. Standards must come from rules documents,
  not be scraped.
- **Qualifier tags are inconsistent across years:**

  | Tag | Files that have it | Files that don't |
  |---|---|---|
  | `NCS` | Tri-Valley 2019, 2022, 2024, 2026 | Tri-Valley 2023 |
  | `CIF` | MOC 2019, 2022, 2024, 2025 | MOC 2023, 2026 |
  | `Q` / `q` | MOC prelims, all years | – |

  The actual qualifier set can't be read from tags in every season. It has to be
  reconstructed from who appears at the next meet, which is itself incomplete (§2.5).

### 2.4 Missing seasons, meets, events, or genders ⚠️ HIGH

- **Seasons and meets:** see §1.2. There is no Bay Shore, Redwood Empire, Class A, or
  league data, and no 2025 Tri-Valley results.
- **Events.** Varsity coverage in the files that exist is complete: 16 events per gender
  plus 4x800 in every file. Two caveats:
  - The **4x800 was an exhibition** at the 2019 and 2022 MOC and was not contested at
    Tri-Valley in those years. It is a scoring event from 2023. The rules must list
    events by season.
  - **Adaptive events** (Unified 100 / LJ / 4x100 / SP, and Ambulatory 100 / 200 in 2025)
    are interleaved with varsity events and vary by year. 2026 Tri-Valley has none, and
    2026 MOC has only some. They must be filtered out explicitly, not by position.
- **Genders:** both are present in every usable file. Event names use `Girls` / `Boys`.

### 2.5 DNS, DQ, and scratch rows ⚠️ HIGH

- **No `DNS` or `SCR` rows exist in any file.** These Hy-Tek exports leave out
  non-starters, so athletes who qualified for MOC but scratched are **invisible**. The
  field at MOC as shown here is smaller than the true qualifier list. Counting
  "qualifiers from area X" from MOC results undercounts.
- **Non-numeric outcomes do appear.** Each file has 1–16 `DQ`, 1–8 `DNF`, 5–25 `NH`
  (no height), a few `FOUL`, and `FS` (false start) rows. They have place `--` and no
  numeric mark.
  - Dropping them loses real participants.
  - Treating them as marks causes parse failures or sorts them wrongly.
  - Some carry a rule citation (`NFHS 5-12-1d`).
- **Ties are common:** 171 tied places across the files (`J`-prefixed HJ/PV marks,
  identical places). Any "top N" allocation needs an explicit tie rule.

### 2.6 Marks stored as strings, and parsing traps ⚠️ HIGH

Every mark is a string with flags glued on. Examples of what a parser has to handle:

| Pattern | Example | Meaning |
|---|---|---|
| Qualifier flag with no space | `47.20QCIF`, `11.84q` | Q = place qualifier, q = time qualifier, CIF = state qualifier |
| Record flag | `11.60RNCS`, `46.71R` | Record (R), plus NCS-qualifier tag |
| Tie-break prefix | `J5-01.00`, `J11-08.00` | Tied height, placed on misses |
| Imperial field marks | `5-04.00`, `10-07.00` | feet-inches.hundredths |
| Minutes:seconds | `4:57.94`, `9:xx.xx` | – |
| Thousandths column | `12.38 … 12.373` | Tie-break for times shown to hundredths, in a trailing column |
| Wind column | `0.9`, `-0.4`, `2.6` | Present in some files and events, absent in others. Wind-aided marks (>+2.0) are not flagged. |
| Jump-off text | `Jump-Off: 6-2 X` | Free text after the mark |
| Unified `J` times | `J15.02` | `J` prefix on a *time* in Unified events |

Fixed-column parsing is also unsafe: column widths differ between files and between
events in the same file (the school field is 12 characters or full length).

---

## 3. Proposed layout: what I'd change and why

Your skeleton is sound. These are the changes I'd make, most important first.

1. **Don't assume Athletic.net CSV is the raw source.**
   - The data in hand is Hy-Tek HTML from Diablo Timing. It's the official timer's
     record, has the rounds, heats, qualifier tags, and wind, and has no IDs.
   - Athletic.net has IDs but may merge prelims and finals or omit DQs.
   - Use **`data/raw/{source}/{meet_key}.{ext}`** with `source ∈ {hytek, athleticnet}`.
     Keep both sources when available, and treat Athletic.net as the ID crosswalk rather
     than the only truth.
   - Add a `data/raw/MANIFEST.csv` (file, source URL, fetched_at, sha256) so raw files
     can be proven untouched.
2. **Use a stable `meet_key` (e.g. `2024-area-tri-valley`), not `{meet_id}`, as the
   primary key.** Athletic.net IDs are blank for now and don't exist for Hy-Tek-only
   files. Keep `athleticnet_meet_id` as an attribute.
3. **Model area membership at the school level, not the league level.**
   - Your own list puts CMC, MCAL, and HDNL in two areas (Redwood Empire and Class A).
     League → area is therefore not a function.
   - Use `schools.csv` with `school_id, season, league, sub_league, area, class_a_eligible`.
   - Add a separate **`school_aliases.csv`** (`raw_string, source, school_id`). With 259
     raw strings, an explicit, reviewed alias table beats any fuzzy matching.
4. **Add `data/reference/athletes_xwalk.csv` plus a review queue.**
   - Where Athletic.net IDs exist, use them.
   - Otherwise build a provisional key from (gender, normalized name, school_id,
     graduation year = season + 12 − grade).
   - Send ambiguous cases to a `review/` CSV. Never auto-merge them.
5. **Rules YAML should hold more than spot counts:**
   - the event list for the season
   - at-large standards per event and gender, plus whether they are wind-legal and
     which meets count
   - tie-break policy
   - the scratch and replacement ("fill") policy
   - relay handling
   - school-level exceptions

   Validate each YAML against a schema so a typo can't silently become a zero.
6. **`processed/` should have one long `performances` table**, one row per athlete or
   team per round. Columns:
   - `meet_key, event, gender, round, heat, place, status` (OK / DQ / DNF / NH / FOUL / FS / DNS)
   - `mark_raw, mark_value_si` (seconds or meters), `wind, tiebreak_value`
   - `flags` (Q, q, CIF, NCS, R, J)
   - `athlete_key, school_id`

   Add a separate `relay_legs` table. The raw string is always kept next to the parsed
   value.
7. **Add `data/reference/entries/`** (heat sheets or "Entries by Team") as the only way to
   see DNS and scratches (§2.5), and therefore the true qualifier lists.
8. **Validation checks (`validate` stage):**
   - event × gender coverage against the rules
   - places monotonic, with ties explained
   - every school string resolved
   - the MOC field is a subset of the area qualifiers
   - where tags exist, reconstructed qualifiers match `NCS` / `CIF` tags
   - row counts compared to the prior run

   Add **hand-checked golden fixtures** (a few events per file) in `tests/`.
9. **Separate `outputs/`** (simulation results, reports) from `processed/`, and add
   `src/cli.py` or a Makefile so one command rebuilds everything from raw.
10. **`git init` before building.** The repo is not under version control, so nothing
    records how the earlier results were produced.

---

## 4. Open questions (need answers before ingest code)

These are listed in the chat summary. They are repeated here so the audit stands alone.

1. Where is the previous attempt's code or output? Only these 12 HTML files are here.
2. Do you have Athletic.net CSV export access (coach account), or should Hy-Tek HTML be
   the primary source?
3. Who times Bay Shore, Redwood Empire, and Class A, and where are their results posted?
4. May I fetch the 2025 Tri-Valley results from diablotiming.com?
5. Do you have NCS allocation rules per season (bylaws or bulletins)?
6. What is the evaluation metric for "a better allocation"?
7. Which marks feed the simulation: area-meet marks only, or season bests?
8. Which events are in scope (adaptive? 4x800 in 2019 and 2022? relays)?
9. Leagues possibly missing from the list: BCL West/East, NCL I/II/III, SCL.
10. Do you want league meets ingested (about 90 meets)?
11. What should the athlete-key fallback be when there's no Athletic.net ID?
12. Can you confirm the school renames?
13. Do you have entries or heat sheets, for DNS?
14. What tooling do you prefer?
15. Can the 12 HTML files be moved into `data/raw/hytek/` once the layout is agreed?
