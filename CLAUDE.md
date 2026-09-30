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
- `outputs/` — **ignored**: qualifiers.csv and left_out.csv (athlete level), replay_{season}/, verify/,
  tabs/ (dashboard screenshots).
- `docs/` — decisions.md (all judgment calls), findings_v1.md, analysis_tables.md (column defs),
  replay_2026.md, replay_seasons.md, dashboard_checks.md, allocation_engine.md, checks/.
- `src/ncs_track/` — athleticnet.py (ingest), validate.py, programs.py (MOC program PDFs),
  schools.py (aliases, IDs, areas), rules.py / season_rules.py, replay.py (rules replay + overlays),
  analysis.py (summary tables), allocate.py (allocation engine), privacy.py (name-leak scan), cli.py.
- `scripts/` — build_findings.py + findings_tables.py, build_dashboard.py,
  `checks/` (pre_push.sh, name_leaks.py, athlete_rows_history.py, dashboard_browser.py,
  relay_splits.py, verify_round_a.py, verify_spot_use.py).
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
.venv/bin/python -m pytest -q                             # ~196 tests
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
- **Made the final** (formerly "top finish / top 8"; columns `made_final*`): finished top 9 in LJ, TJ,
  SP or DT, or top 8 in every other event, relays included (800/1600 finals seat 12; we count top 8).
- **Spot use** (guaranteed spots only; `spot_use` column, first match wins): Competed · Refilled ·
  Unfilled · Chose another event (competed at the MOC in other events only) · Didn't enter (competed
  in no MOC event). **Guaranteed spots used** = (competed + refilled) ÷ guaranteed spots. At-large
  standard qualifiers reported on a separate line, never in the donut or %.
- **Unfilled spot** (provisional): guaranteed spot, qualifier didn't compete, not refilled, AND the
  event's MOC field (largest competed count over its rounds, not DNS/SCR) ended below 24.
  Old "empty lane" metric kept only as `unused_not_refilled`.

## Validated results so far
- Replay vs real MOC entries: RAW 87–89%, **RULES 97.9–99.1% per season** (2022–2026), using the
  best reading: Class A at-large eligible from 4th, fill before at-large, MOC-guide fill (3 spots,
  all four meets), fill ties included, wind-aided allowed; same-Area replacement overlay; entry limit
  (4, assumed) explains nothing. Engine with current.yaml reproduces the replay exactly (tested).
- Tri-Valley holds 464 of 659 next-best-mark + at-large spots (70%), 2022–2026.
- Guaranteed spots used: 3,661 of 3,890 (94%) over 5 seasons (3,515 competed, 146 refilled); 70 chose
  another event, 38 didn't enter, 121 unfilled (3%; 1–6% per Area-season; 4 Area×event combos in 3+
  seasons). Unfilled stays provisional (decision #28): 121 unfilled vs 86 places short of 24 (at-large
  fills lanes); 11 spots taken by a lower same-Area finalist not credited as refills; 7 refills no-show.
- Area place vs MOC finish (pooled, median MOC place): 6th place — Tri-Valley 11th (141 entries),
  Bay Shore 19th (142), Redwood Empire 18.5th (140); Class A 3rd 19.5th (132). Tri-Valley 7th–8th 13th
  (253) vs Bay Shore + Redwood Empire 5th–6th 18th (561). Tri-Valley 5th–6th: 10th. Lowest automatics
  of Bay Shore / Redwood Empire / Class A make the final less often than other Areas' next-best-mark + at-large qualifiers (9% vs 14%, 8% vs 13%,
  5% vs 14%; permutation and athlete-clustered p ≤ 0.03). Direction consistent; not a cause.
- Left-out (cutoff = mark of the 8th-best MOC finisher, 9th in LJ/TJ/SP/DT, any round): 6 cases in
  5 seasons, all 2023 Tri-Valley. Local only (`outputs/left_out.csv`); findings §5 is one paragraph.

## Privacy rules (non-negotiable)
- The public repo (github.com/pwalesdi/ncs_track) must never contain athlete names or athlete-level
  rows in tracked files, docs, dashboard data or commit history. Athlete-level work goes to
  `outputs/` or other ignored paths.
- Small-cell rule: MOC-place figures (made-the-final counts, medians) only for groups of ≥ 5 entries
  (core_place_curve, core_comparison, moc_performance — all pre-aggregated to the dashboard grain).
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
- Log every judgment call in `docs/decisions.md` (numbered; next is #32).
- Plain-English labels with units on every number ("19 of 59 entries made the final (32%)").
- Don't tune rules to force matches; mismatches are findings. Don't create alternative allocations.

## Open items
- Unfilled definition (decision #28): cap at the field shortfall? credit deeper-line same-Area
  refills? count refilled-then-no-show as unfilled? Committee/user to decide; badge stays until then.
- Older `dashboard/index.html` blobs in history embed per-event MOC performance rows; rewriting that
  path needs separate approval (decision #29).
- West County / El Molino / Analy rename still unconfirmed (kept in review).
- CIF State meet results not yet pulled (state_qualified = "pending").
- Alternative allocations not yet designed; engine ready: `src/ncs_track/allocate.py` +
  `configs/allocation/current.yaml` (see docs/allocation_engine.md).
