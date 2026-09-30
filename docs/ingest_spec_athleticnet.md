# Athletic.net ingest spec

Status: **stub parser built and tested against hand-built fixtures; no real Athletic.net
file has been ingested yet.** Code: `src/ncs_track/athleticnet.py` (ingest),
`validate.py` (table checks), `schema.py` (column definitions). A test fails if this
document is missing any column or check ID defined in code.

## 1. Scope

- One CSV per meet, for the 25 Area and MOC meets from 2022–2026 (`athleticnet_meet_id`
  in `data/reference/meets.csv`). 2019 is not yet sourced.
- Athletic.net is the **primary** source. Hy-Tek HTML (`data/raw/hytek/`) is the
  secondary source used for cross-checking (§7, planned).
- **Ingest never drops a row.** Out-of-scope rows are kept with `in_scope = False` so
  counts always reconcile back to the raw file. These include:
  - adaptive divisions (Unified, Ambulatory)
  - exhibition, rerun and jump-off blocks
  - the 4x800

## 2. Input files

| Item | Requirement |
|---|---|
| Location | `data/raw/athleticnet/` (never edited; checksummed in `data/raw/MANIFEST.csv`) |
| Name | `{season}_{meet}_{meet_id}.csv`, `meet` ∈ `moc`, `tri-valley`, `bay-shore`, `redwood-empire`, `class-a`; e.g. `2026_moc_629241.csv`. Must equal the meet's `file_name` in `meets.csv`. |
| Encoding | UTF-8, with or without a BOM |
| Header | One header row containing all 21 columns below. Order doesn't matter. Extra columns raise a warning (V01) and are ignored. |
| Meet match | `meet_id` must match exactly one row of `meets.csv`; the filename season and meet must equal that row's season and meet; the filename must equal its `file_name`. Otherwise ingest stops. The `meet_name` values inside the file must name the same meet (V16). |

### 2.1 Raw columns

The layout is agreed; the **value formats are unconfirmed.** The last column lists
what to check on the first real file.

| Column | Expected content | How it is parsed | Confirm on first real file |
|---|---|---|---|
| `meet_id` | Athletic.net meet ID | Must equal the filename ID on every row (V02) | – |
| `meet_name` | Display name | Carried for reference only | – |
| `meet_date` | Meet date | Not parsed yet | Format (ISO? "May 17, 2024"?) |
| `gender` | Girls/Boys, F/M, Women/Men | `events.parse_gender` → `girls` / `boys` | Actual values |
| `division` | Varsity, Unified, … | Combined with the event name to detect adaptive events | Label for Ambulatory events |
| `event_raw` | e.g. `100 Meters`, `110m Hurdles - 39"`, `Shot Put - 4kg` | `events.parse_event` → canonical code. Unknown labels are an error (V03). | Full list of labels |
| `round_raw` | Finals / Prelims / … | `events.parse_round`. **Blank → `unknown` → error (V03).** | Does a single-round Area meet use "Finals" or leave it blank? |
| `heat` | Heat or flight number | Integer or null | Present for field flights? |
| `place` | Overall place | Integer. `--`, `-` or blank means not placed. | Overall or per heat for timed finals? (V06 catches per-heat places.) |
| `athlete_name` | Athlete name | Kept raw, plus a `name_key` (matching aid only) | "First Last" or "Last, First" (both handled) |
| `athlete_id` | Athletic.net athlete ID | String of digits. Blank → review queue (V07). | – |
| `grade` | 9–12 | Integer. Anything else is an error (V11). | – |
| `school_name` | School display name | Kept raw | – |
| `school_id` | Athletic.net school ID | Required (V10) | – |
| `mark_raw` | Time, distance or status word | `marks.parse_mark`, strict (see §3) | Field event format (`18-01.75`? `18' 1.75"`?), flags, hand times |
| `wind` | m/s | Float; a leading `+` is allowed | Blank vs `NWI` for no reading |
| `status` | DNS / DNF / DQ / FS / SCR / NH / NM / FOUL / NT / blank | Takes precedence over a status word in `mark_raw` (V04) | Actual vocabulary; are DNS rows included at all? |
| `relay_team_label` | A / B … | Kept | – |
| `relay_leg_names` | Leg names | Split on `\|` or `;` (never on commas, since names contain them) | Separator |
| `relay_leg_ids` | Leg athlete IDs | Same separator; the count must match the names (V09) | – |
| `source_url` | Results page URL | Kept | – |

## 3. Parsing rules

- **Marks** (`marks.py`):
  - Times become seconds. Formats: `11.60`, `4:57.94`, `1:02:03.4`, thousandths.
  - Field marks become meters. Formats: `5-04.00`, `31-2.75`, `142-05`, `5-0`,
    `18' 1.75"`, `12.34m`.
  - Recognised prefixes and suffixes are split off into `mark_flags`:
    - a `J` prefix (tie resolved by the judges)
    - suffixes `Q q R NCS CIF h`, including glued-together forms such as `47.20QCIF`
  - Anything else is an error, never a guess. Inches ≥ 12 and seconds ≥ 60 are rejected.
- **Status:** the `status` column wins when set. Otherwise the status comes from the mark.
  - `mark_value` is filled **only** when status is `OK`.
  - A status of DQ/DNF/etc. together with a numeric mark is an error (V04).
  - A place on a non-OK row is an error (V06).
- **Rounds** stay separate: prelim and final marks are never merged. Area at-large and fill
  logic reads `round == "final"` only (per the rules). MOC downstream metrics read
  finals for "made final / scored / state qualified".
- **Wind:** stored as `wind`. `wind_aided = True` when the event is a wind event
  (100, 200, 100H, 110H, LJ, TJ) and wind > `rules.wind.legal_max_mps` (2.0). The flag is
  informational only; **no mark is excluded for wind.**
- **Scope:** `in_scope` is true when all of these hold:
  - the gender and event is in `rules.events.main_simulation`
  - the event is not adaptive
  - there is no exhibition, rerun or jump-off modifier
- **Identity:** `athlete_id` is the key. `athlete_name_key` (`last|first`, accents,
  punctuation and case folded) and `grad_year` (season + 12 − grade) exist only for
  matching Hy-Tek rows. The fallback key is (gender, `athlete_name_key`, `school_id`,
  `grad_year`). Anything that doesn't match exactly goes to `data/review/`. **No
  automatic merges.**

## 4. Output tables

These are written to `data/processed/`, which git ignores and which is rebuilt from raw.

### 4.1 `performances.csv`

One row per athlete (or relay team) per round, per event, per meet.

| Column | Type | Meaning |
|---|---|---|
| `performance_id` | string | `{meet_key}#{source_row}`, stable because raw files never change |
| `meet_key` | string | e.g. `2024-area-tri-valley` |
| `season` | int | – |
| `level` | string | `moc` / `area` / `league` |
| `meet_area` | string | Area slug of the meet (blank for MOC) |
| `source` | string | `athleticnet` / `hytek` |
| `source_file` | string | Raw filename |
| `source_row` | int | 1-based data row in the raw file |
| `gender` | string | `girls` / `boys` |
| `event_raw` | string | As received |
| `division_raw` | string | As received |
| `event_code` | string | `100` … `DT`, `4x800` (see `events.EVENTS`) |
| `event_modifier` | string | `exhibition` / `rerun` / `jump_off` / blank |
| `measure` | string | `time` / `distance` |
| `is_relay` | bool | – |
| `is_adaptive` | bool | Unified / Ambulatory |
| `in_scope` | bool | See §3 |
| `round_raw` | string | As received |
| `round` | string | `final` / `prelim` / `semi` / `unknown` |
| `heat` | int | – |
| `place_raw` | string | As received |
| `place` | int | Null when not placed |
| `status_raw` | string | As received |
| `status` | string | `OK DNS DNF DQ FS SCR NH NM FOUL NT` |
| `mark_raw` | string | **As received, always kept** |
| `mark_value` | float | Seconds or meters; null unless `OK` |
| `mark_unit` | string | `s` / `m` |
| `mark_flags` | string | Space-separated flags (`J`, `Q`, `q`, `R`, `NCS`, `CIF`, `h`) |
| `wind_raw` | string | As received |
| `wind` | float | m/s |
| `wind_aided` | bool | Informational only |
| `athlete_id` | string | Null for relays and for unmatched Hy-Tek rows |
| `athlete_name_raw` | string | – |
| `athlete_name_key` | string | Matching aid |
| `grade` | int | – |
| `grad_year` | int | – |
| `school_id` | string | Athletic.net school ID |
| `school_name_raw` | string | – |
| `relay_team_label` | string | – |
| `source_url` | string | – |

### 4.2 `relay_legs.csv`

| Column | Type | Meaning |
|---|---|---|
| `performance_id` | string | FK to performances |
| `meet_key` | string | – |
| `leg_order` | int | 1–4, in the order listed (not necessarily running order) |
| `athlete_id` | string | – |
| `athlete_name_raw` | string | – |
| `athlete_name_key` | string | – |

### 4.3 Review outputs (`data/review/`)

- `validation_issues.csv`: every issue, with check, severity, meet_key, message and
  performance_id.
- `athlete_id_review.csv`: in-scope individual rows with no `athlete_id`, for manual
  matching.

## 5. Validation checks

**Severity:**
- **error** stops the row or meet from being used until it's resolved.
- **warning** needs a human look.
- **info** is reported only.

| ID | Stage | Severity | Check |
|---|---|---|---|
| V01 | read | error / warning | All 21 columns present (missing columns stop ingest); unexpected extra columns are a warning |
| V02 | read | error | Filename matches `{season}_{meet}_{meet_id}.csv` and `meets.csv` `file_name`; meet_id is in `meets.csv` exactly once; season and meet match; the `meet_id` column equals the filename ID on every row |
| V03 | row | error | Gender, event and round each map to a canonical value |
| V04 | row | error / warning | Mark parses; status is a known code; no numeric mark on a non-OK row; status column vs status word in mark disagree (warning) |
| V05 | table | warning | Mark inside the loose plausibility range for the event |
| V06 | row + table | error / warning / info | Place is an integer or `--`; no place on a non-OK row; within one race (meet, gender, division, event, modifier, round) a later place never has a better mark (error in finals; warning in prelims, whose places can follow qualifying order); one place shared by different marks (warning); places restarting per section/heat in a final (error; Area places were checked 2026-09-29 and are overall); first place in a final is 1 (warning); tied places listed (info). In-scope rows only. |
| V07 | table | error / warning | Individual rows without `athlete_id` → review queue (warning); non-numeric ID (error); same ID twice in one race (error) |
| V08 | table | warning | One `athlete_id` with different names in a meet; one name + school with different IDs |
| V09 | row + table | error / warning | Relay leg ID count equals name count (error); relay has 4 legs (warning); relay row carrying an `athlete_id` (warning); a meet whose relays have leg names but no leg IDs at all (warning, e.g. 2023 Class A) |
| V10 | table | error / warning | `school_id` present (error); one `school_id` with several names in a meet (warning); `school_id` not in the schools reference, once that exists (warning) |
| V11 | row | error | Grade in 9–12 or blank |
| V12 | table | warning | Every main-simulation event × gender has in-scope final rows at every meet |
| V13 | row | error / info | Wind parses (error); wind-aided counts reported (info) |
| V14 | table | warning | Every finalist appears in that event's prelims, when prelims exist |
| V15 | table | info | Per-meet row counts: total, out of scope, adaptive, modifier blocks, wind-aided |
| V17 | table | warning | An in-scope Area event with more than 1.5× the meet's median rows per event (a very large field, e.g. 2025 Class A 400 m: confirm it's real) |
| V16 | read | error | Every `meet_name` value names the filename's meet (e.g. "Meet of Champions" for `moc`, "Bayshore"/"Bay Shore" for `bay-shore`), and any year in it equals the filename season |

## 6. How to run

```
.venv/bin/python -m ncs_track manifest --check        # raw files untouched?
.venv/bin/python -m ncs_track rules-check             # rules YAML loads and checks
.venv/bin/python -m ncs_track ingest-athleticnet      # all files in data/raw/athleticnet/
.venv/bin/python -m pytest
```

`ingest-athleticnet` exits non-zero if any error-level issue exists. Every output carries
the rules label (`2026 rules applied`) that `rules.load_rules_for` returns.

## 7. Planned (not built)

1. **Hy-Tek parser plus cross-check.** Parse `data/raw/hytek/*.htm` into the same
   `performances` schema (`source = hytek`, `athlete_id` null). Then join to Athletic.net
   rows on (meet, gender, event, round, place, school) and compare marks. Mismatches in
   round, place, mark, or qualifier tag (`Q`/`q`/`NCS`/`CIF`) become cross-check issues.
2. **School → Area join** from `data/reference/ncs_source_of_truth_lists.csv`, via
   `school_aliases.csv` (raw name → Athletic.net `school_id`).
3. **Heat sheets** (`day_1_program.pdf`, `day_2_program.pdf`) as the true MOC entry list,
   pending approval to download.
