# Overnight report (2026-09-29/30)

**All four parts are done and pushed.** Every push went through `pre_push.sh` with all
checks passing. **184 tests pass.** No raw data was modified and no history was rewritten.

| Part | Status | Where |
|---|---|---|
| 1. Spot utilization | Done. New: `empty_lanes`, `no_show_rate`, `double_qualifier_share`; empty-lane flag list; per-Area no-show/empty-lane counts | `data/summary/spot_utilization*.csv`, `no_shows_empty_lanes_by_area.csv` |
| 2. Findings | Done. Plain-English write-up; tables regenerate from `data/summary/` | `docs/findings_v1.md`, `scripts/build_findings.py` |
| 3. Dashboard | Done, with 8 spot checks (all match). **Not viewed in a browser** (none available here). | `dashboard/index.html`, `docs/dashboard_checks.md` |
| 4. Allocation engine | Done. `current.yaml` reproduces the validated replay exactly, 2022–2026. No alternative allocations made. | `src/ncs_track/allocate.py`, `docs/allocation_engine.md` |

**Overnight decisions to review** (details in `docs/decisions.md`, items 1–14):
- **Empty lanes (1–2):** computed per event and never below 0; no-shows count as empty
  lanes.
- **Double qualifiers (3):** individuals only.
- **Left-out cutoff (5):** a short final (DNS/DQ) takes its cutoff from prelim marks.
- **Core comparison (6):** genders combined.
- **Dashboard:**
  - (7) "All seasons" sums counts;
  - (8) the field toggle affects panels 1–2 only;
  - (9) every chart has a table of its numbers;
  - (10) tested through `osascript`.
- **Engine:**
  - (11) its own code, not a replay wrapper;
  - (12) `adjust_pct` = % of the mark, positive = harder;
  - (13) replacement only affects comparisons;
  - (14) `tests/` is now a package.

**Look at these first**
1. **The core question (findings §4).** Pooled over five seasons, the lowest automatic
   qualifiers of Bay Shore, Redwood Empire and Class A reached a top finish less often
   than other Areas' at-large qualifiers:
   - Bay Shore: 9% (25 of 284) vs 14% (72 of 511)
   - Redwood Empire: 8% (22 of 277) vs 13% (65 of 489)
   - Class A: 5% (7 of 132) vs 14% (74 of 542)
   - Tri-Valley is the reverse: 36% (106 of 293) vs 9% (14 of 162).

   The "other Areas' at-large" group is mostly Tri-Valley athletes. The p-values
   (≈0.01–0.03) come from a naive test and overstate certainty.
2. **Empty lanes.** Counting only spots that went to nobody, 22 Area × event combinations
   are flagged in 3+ seasons (51 if every unused spot counts). By Area and season, 3–10%
   of spots were empty.
3. **2026 left-out figure.** It comes from one race: the 8th team in the 2026 boys 4x400
   final ran 3:59.34, so every Area's best non-qualifying relays "beat" the cutoff.
4. **Open `dashboard/index.html` on a phone and a desktop.** Its numbers are tested; its
   look is not.
5. **Engine config vocabulary** (`configs/allocation/current.yaml`, decision 12). Check it
   fits the alternatives you plan to design.
