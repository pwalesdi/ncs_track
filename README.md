# ncs_track

Analysis of how athletes qualify for the CIF North Coast Section (NCS) track & field
Meet of Champions (MOC): replaying each season's qualification rules against the Area
meet results and checking the replay against who actually entered the MOC.

## Layout

| Path | What |
|---|---|
| `src/ncs_track/` | Package: ingest, mark/event parsing, rules loading, MOC program parser, school aliases, replay |
| `data/reference/rules/` | Rules per season (`2026.yaml` transcribed; earlier seasons generated, see `docs/decisions.md`) |
| `data/reference/meets.csv` | Every meet: key, season, level, area, Athletic.net meet ID, source URLs |
| `data/reference/school_aliases.csv` | Canonical schools, every spelling seen, area per season, Athletic.net school ID |
| `data/raw/MANIFEST.csv` | SHA-256 and provenance of every raw file (the files themselves are not in git) |
| `docs/` | Audit, ingest spec, decisions log, rules sources and cross-checks |
| `scripts/checks/` | One-off data checks, kept so they can be re-run |

Commands (from the repo root, with the virtualenv active):

```
python -m ncs_track manifest --check     # raw files match MANIFEST.csv checksums
python -m ncs_track ingest-athleticnet   # data/raw/athleticnet -> data/processed/performances.csv
python -m ncs_track moc-entries          # MOC programs -> data/processed/moc_entries.csv
python -m ncs_track school-aliases       # data/reference/school_aliases.csv + review queue
python -m ncs_track rules-seasons        # regenerate rules/2019, 2022-2025.yaml
pytest
```

## Data

**The raw results are not in this repository.** 

- `data/raw/athleticnet/`: Athletic.net results, one CSV per meet
- `data/raw/hytek/`: Hy-Tek result pages from Diablo Timing
- `data/reference/entries/`: MOC and Area meet programs (heat sheets, PDFs)
- `data/processed/`, `data/review/`, `outputs/`: everything built from the above

What *is* here is enough to rebuild them and prove the rebuild is identical:

1. **Athletic.net results.** `data/reference/meets.csv` gives each meet's
   `athleticnet_meet_id` and the `file_name` to save it under
   (`{season}_{meet}_{meet_id}.csv`, e.g. `2026_moc_629241.csv`). The results page is
   `https://www.athletic.net/TrackAndField/meet/{athleticnet_meet_id}/results`; the CSVs
   were extracted from Athletic.net's results data (`GetResultsData3`) into the columns
   listed in `docs/ingest_spec_athleticnet.md`. Save them in `data/raw/athleticnet/`.
2. **Hy-Tek results and meet programs.** `data/raw/MANIFEST.csv` lists every file with
   its `source_url` (Diablo Timing). Download each to the `path` shown.
3. **Verify.** `python -m ncs_track manifest --check` compares every file's SHA-256 with
   the manifest. A re-export that differs (Athletic.net results can be edited after a
   meet) shows up as `CHANGED`.
4. **Build.** Run the commands above.

Tests that need the real data skip themselves when it is absent. Test fixtures use
made-up athlete names. `tests/test_no_athlete_names.py` fails if any tracked file contains
a name from `data/processed/`, and `scripts/checks/name_leaks.py` checks every commit in
history the same way; run both before pushing.
