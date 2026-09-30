# Unattended run report (2026-09-30): alternative MOC allocations

**Done, all pushed through `pre_push.sh`. No history rewrites; `data/raw/` untouched.**

**Part 1: scenarios.** `src/ncs_track/scenarios.py` plus configs `current`, `a_5553`, `b_4443` and `c_3333`, run on 2022–2026 with pass-down and the real declines. Current reproduces the validated routes and left-out set exactly, and a test checks this. No left-out athlete beats a next-best-mark mark in any scenario (also tested).

**Part 2: tables.** Four tables in `data/summary/scenario_*.csv`: field makeup, added/removed, faster-but-left-out, and merit capture. Each is split by scenario × season (plus pooled) × gender × event (plus groups and all) × Area. Named lists are in `outputs/scenario_*.csv`.

**Part 3: dashboard.**
- A scenario selector replaces the Rules toggle.
- A new Compare scenarios tab has 8 metrics and a pooled grouped-bar chart.
- The place grid, with its automatic cutoff line, replaces the line charts.
- The Left out tab shows its headline with Class A qualifiers included and excluded.
- Playwright passes at 390 and 1400 px: every tab under every scenario and every Compare metric. Screenshots are in `outputs/tabs/`.

**Part 4.** `docs/scenarios_v1.md`, generated from the tables.

**Not done or partly done.**
- Under an alternative scenario, MOC performance, Spot use and the place grid still show real MOC results, with a banner. Added athletes never ran at the MOC, so there are no results to show. The place grid does move its cutoff line.
- The older engine `allocate.allocate()` still has no pass-down; the scenarios bypass it.

## Decisions to review (docs/decisions.md, "Unattended decisions to review")
- **#35 Decline model.** Real decliners, and finishers walked past an unused spot, decline again; everyone else accepts. The 14 program entries the replay can't place stay in the field.
- **#36 A tie is an offer.** A finisher tied with the last automatic or next-best-mark qualifier who didn't enter now counts as a decline. This shifted the validated figures slightly:
  - passed-down spots: 247 → 250
  - left out: 8,597 → 8,587
  - left out who beat an automatic qualifier from another Area: 1,582 → 1,575
- **#37 Which tabs follow the scenario**, and **#38–39**: how the Compare tab and the place grid are built.

## Look at these first (pooled 2022–2026)
1. **Faster but left out falls as automatic spots fall:** 1,575 → 1,209 → 976 → 880 (current, 5-5-5-3, 4-4-4-3, 3-3-3-3). With Class A qualifiers excluded as the beaten group: 1,073 → 582 → 253 → 108.
2. **Who gains.** Tri-Valley's net change is +122 / +177 / +210 athletes. Bay Shore's is −72 / −116 / −149, Redwood Empire's −56 / −84 / −95, and Class A's +13 / +24 / +25.
3. **The cost is small.** Removed athletes who made the MOC final in reality: 1 / 2 / 3, all in 2023.
4. **The estimated gain is also small.** Only 4 added athletes per scenario had an Area mark at or better than the MOC final cutoff, all in 2023, and it's an estimate from different meets. Merit capture rises from 90% to 94% / 96% / 96%.
5. **Check decision #36 before quoting the updated left-out numbers.**
