# Test fixtures

`2024_moc_520990.csv` (2024 MOC) and `2024_tri-valley_523900.csv` (2024 Tri-Valley)
are **hand-built** in the agreed Athletic.net extraction layout. They are not real
Athletic.net exports.

- **Real, copied from the Hy-Tek results** (`data/raw/hytek/2024-moc.htm`,
  `2024-area-tri-valley.htm`): grades, schools, events, rounds, heats, places, marks, wind,
  and DQ/DNF/FS/NH outcomes.
- **Made up:** every athlete and relay-leg name. The repo is public and the athletes are
  minors; `tests/test_no_athlete_names.py` fails if a real name comes back.
- **Synthetic:** `athlete_id` (9000001+), `school_id` (99001+), `source_url`. Names are
  written "First Last" and schools unabbreviated, as Athletic.net displays them.
  `gender` uses `F`/`M`.
- **Mark formats are mixed on purpose.** The MOC file keeps Hy-Tek formatting, with flags
  glued on (`47.20QCIF`, `J5-00.00`, `8:56.42 CIF`) and status words in `mark_raw`. The
  Tri-Valley file uses the clean style Athletic.net probably uses (`12.01`, `18' 1.75"`,
  status only in `status`). The real format is unconfirmed, so the parser must handle both.

Replace or add to these once the first real extraction arrives. Keep at least one
fixture per meet level.
