# CLAUDE.md — ncs_track

## Purpose
Evaluate how the CIF North Coast Section (NCS) allocates Meet of Champions (MOC) qualifying spots
across the four Area meets (Tri-Valley, Bay Shore, Redwood Empire, Class A), 2022–2026, for a
committee presentation. We replay each season's rules against Area results, check the replay against
real MOC entries, then describe who qualifies, how they perform, and how spots are used.
Describe, don't recommend: no allocation proposals unless the user designs them.

## Repo map (git-ignored = local only, contains athlete data)
- `data/raw/` — **ignored**: `athleticnet/` ({season}_{meet}_{meet_id}.csv), `hytek/` results. Only
  `data/raw/MANIFEST.csv` (checksums + source URLs) is tracked.
- `data/reference/` — tracked: `meets.csv`, `rules/{season}.yaml`, `school_aliases.csv`,
  `school_alias_spellings.csv`, `row_overrides.csv`, source-of-truth school list.
  `data/reference/entries/` (MOC program PDFs) — **ignored**.
- `data/processed/` — **ignored**: performances, relay_legs, moc_entries.
- `data/review/` — **ignored** except `school_aliases_review.csv`.
- `data/summary/` — tracked, name-free aggregates feeding docs + dashboard.
- `outputs/` — **ignored**: qualifiers.csv (athlete level), replay_{season}/, verify/, screenshots.
- `docs/` — decisions.md (all judgment calls), findings_v1.md, analysis_tables.md (column defs),
  replay_2026.md, replay_seasons.md, dashboard_checks.md, allocation_engine.md, checks/.
- `src/ncs_track/` — athleticnet.py (ingest), validate.py, programs.py (MOC program PDFs),
  schools.py (aliases, IDs, areas), rules.py / season_rules.py, replay.py (rules replay + overlays),
  analysis.py (summary tables), allocate.py (allocation engine), privacy.py (name-leak scan), cli.py.
- `scripts/` — build_findings.py + findings_tables.py, build_dashboard.py,
  `checks/` (pre_push.sh, name_leaks.py, athlete_rows_history.py, dashboard_browser.py,
  relay_splits.py, verify_round_a.py).
- `dashboard/` — template.html → built index.html (single offline file; Chart.js 4.4.1 vendored,
  SHA-256 pinned in build script).
- `configs/allocation/current.yaml` — the existing system for the allocation engine.

## Rebuild everything (from repo root; raw data must exist locally, verify with manifest)
```
.venv/bin/python -m ncs_track manifest --check
.venv/bin/python -m ncs_track ingest-athleticnet          # -> data/processed/performances.csv
.venv/bin/python -m ncs_track moc-entries                 # MOC programs -> moc_entries.csv
.venv/bin/python -m ncs_track school-aliases              # aliases, Athletic.net IDs, areas
.venv/bin/python -m ncs_track replay --season 2026        # full sweep (192 readings)
.venv/bin/python -m ncs_track replay --season 2022 2023 2024 2025 --reading \
  '{"class_a_at_large_outside_top":3,"fill_before_at_large":true,"fill_source":"moc_guide","fill_ties_include":true,"wind_aided_at_large":true}'
.venv/bin/python -m ncs_track analysis --season 2022 2023 2024 2025 2026   # data/summary/*
.venv/bin/python scripts/build_findings.py                # docs/findings_v1.md
.venv/bin/python scripts/build_dashboard.py               # dashboard/index.html
.venv/bin/python scripts/checks/dashboard_browser.py      # Playwright, 390 + 1400 px
.venv/bin/python -m pytest -q                             # ~191 tests
scripts/checks/pre_push.sh [git push args]                # ALWAYS push through this
```
Engine: `.venv/bin/python -m ncs_track allocate --config configs/allocation/current.yaml --season 2026 --compare`.

## Key definitions (use exactly)
- **Automatic**: top 6 at the Area meet (Class A top 3). 21 per event.
- **Next best mark**: the 3 fill spots per event, next best marks across all four Area meets.
- **At-large (standard)**: met the posted at-large standard in the Area final, outside automatic
  places. "At-large" means ONLY these. Combined group = "next best mark + at-large standard" —
  never call the combined group "at-large".
- **Guaranteed spots**: 24 per event (21 automatic + 3 next best mark); at-large has no cap.
- **Replacement**: entered the MOC to fill a vacancy (next finalist in line, same Area).
- **All qualifiers** = everyone who earned a spot (replay prediction), whether or not they entered.
  **Actual entries** = athletes in the MOC program. **Entries** = athlete-events (one athlete in two
  events counts twice).
- **Top finish / top 8**: MOC final place ≤ 8 (≤ 9 in LJ, TJ, SP, DT).
- **Unused guaranteed spot / unfilled spot** (corrected metric, provisional): automatic or next-best-mark
  qualifier didn't compete, spot not refilled, AND the event's MOC field (competed in first round,
  not DNS/SCR) ended below 24. Old "empty lane" metric kept only as `unused_not_refilled`.

## Validated results so far
- Replay vs real MOC entries: RAW 87–89%, **RULES 97.9–99.1% per season** (2022–2026), using the
  best reading: Class A at-large eligible from 4th, fill before at-large, MOC-guide fill (3 spots,
  all four meets), fill ties included, wind-aided allowed; same-Area replacement overlay; entry limit
  (4, assumed) explains nothing. Engine with current.yaml reproduces the replay exactly (tested).
- Tri-Valley holds 464 of 659 next-best-mark + at-large spots (70%), 2022–2026.
- Unfilled spots: 121 of 3,890 guaranteed spots (3%) over 5 seasons (old metric said 247);
  1–6% per Area-season. Only 4 Area×event combos have unfilled spots in 3+ seasons.
- Area place vs MOC finish (pooled): Tri-Valley 7th–8th finishers typically finish 13th at the MOC
  (253 entries); Bay Shore 5th–6th 18th (284); Redwood Empire 5th–6th 17th (277); Class A 3rd 19.5th
  (132). Tri-Valley 5th–6th: 10th. Lowest automatics of Bay Shore / Redwood Empire / Class A finish
  top 8 less often than other Areas' next-best-mark + at-large qualifiers (9% vs 14%, 8% vs 13%,
  5% vs 14%; permutation and athlete-clustered p ≤ 0.03). Direction consistent; not a cause.
- Left-out (all-rounds 8th/9th-best MOC cutoff): 6 cases in 5 seasons, all 2023 Tri-Valley.

## Privacy rules (non-negotiable)
- The public repo (github.com/pwalesdi/ncs_track) must never contain athlete names or athlete-level
  rows in tracked files, docs, dashboard data or commit history. Athlete-level work goes to
  `outputs/` or other ignored paths.
- Small-cell rule: MOC-place figures (top-8 counts, medians) only for groups of ≥ 5 entries.
- Every push goes through `scripts/checks/pre_push.sh` (leak test, all-history name scan, commit
  email, ignored-path check, athlete-level-table history scan). Never bypass it; if it fails, fix
  the leak or don't push.
- Commit email: 50930764+pwalesdi@users.noreply.github.com.
- History rewrites (git filter-repo, in .venv) and force pushes ONLY with explicit user approval for
  the specific paths; back up first; push with `--force-with-lease=main:<old sha>`.
- Test fixtures and code comments use made-up names only.

## Working rules
- The user relays prompts from another Claude conversation. Do the requested steps in order,
  commit + push each part through pre_push.sh, then stop and report.
- Log every judgment call in `docs/decisions.md` (numbered; next is #25).
- Plain-English labels with units on every number ("19 of 59 entries finished top 8 (32%)").
- Don't tune rules to force matches; mismatches are findings. Don't create alternative allocations.

## Open items
- Aggregate `data/summary/left_out.csv` (athlete-level rows) and single-entry cells in
  `moc_performance.csv` — pending user approval (may need a history rewrite).
- Fix the Karnik/Karnick name alias (choice tag wrongly "did_not_declare", 2024).
- Rename donut segment "Other unused" → "Chose another event" (dashboard + docs).
- West County / El Molino / Analy rename still unconfirmed (kept in review).
- CIF State meet results not yet pulled (state_qualified = "pending").
- Alternative allocations not yet designed; engine ready: `src/ncs_track/allocate.py` +
  `configs/allocation/current.yaml` (see docs/allocation_engine.md).
