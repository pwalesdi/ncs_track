# Dashboard checks

`dashboard/index.html` is built by `.venv/bin/python scripts/build_dashboard.py`, from
`dashboard/template.html` and the tables in `data/summary/` (embedded as JSON; no athlete
names). Chart.js comes from cdnjs.

## How the checks work

`tests/test_dashboard.py` takes the dashboard's own aggregation code (the `agg` script
block) and its embedded data out of the built `index.html`, and runs them with macOS's
JavaScript engine (`osascript -l JavaScript`). It then compares the numbers the page would
show with pandas reading the summary tables directly. The rendering script is only
syntax-checked, because there is no browser here. Checked 2026-09-30; all pass.

| # | Panel and filter | Dashboard shows | Summary table | Match |
|---|---|---|---|---|
| 1 | Field makeup; qualified, 2026, all | Tri-Valley 294 of 818 | `field_makeup.csv`: 294, field 818 | ✓ |
| 2 | Field makeup; declared, 2026, all | Bay Shore automatic 187 | `field_makeup.csv`: 187 | ✓ |
| 3 | At-large share; qualified, 2026, all | Tri-Valley next best mark 72 of 146 | `at_large_share.csv`: 72; combined spots 146 | ✓ |
| 4 | MOC performance; 2026, all | Class A automatic top finish 7 of 83 | `moc_performance.csv`: 7 of 83 | ✓ |
| 5 | Spot utilization; 2026, all | Redwood Empire empty lanes 17 of 216; no-shows 3 of 193 | `spot_utilization_by_area.csv`: 17, 216, 3, 193 | ✓ |
| 6 | Left out; 2026, all | Tri-Valley 0 of 96 (3 of 96 before the all-rounds cutoff, 2026-09-30) | `left_out.csv`: 0 of 96 | ✓ |
| 7 | Makeup, girls 100, 2026; utilization, boys throws, 2026 | Per-Area totals | `field_makeup.csv`, `spot_utilization.csv` filtered | ✓ |
| 9 | Core question, 2026, all | Class A lowest autos 1 of 28; every Area/group count and median (from `core_place_counts.csv`) | `core_comparison.csv` (2026, all events) | ✓ |
| 10 | Headline cards (pooled 2022–2026) | Tri-Valley 464 of 659 at-large spots; every Area's lowest-auto and at-large top finishes; empty lanes | pandas on `at_large_share.csv`, `core_place_counts.csv` (cross-checked with `core_comparison.csv`), `spot_utilization_by_area.csv` | ✓ |
| 8 | Utilization, all seasons pooled; flag list | Bay Shore empty lanes, 5 seasons; 22 flags | Sum of `spot_utilization_by_area.csv`; `spot_utilization_flags_empty_lanes.csv` | ✓ |

## Browser check (redesign, 2026-09-30)

`scripts/checks/dashboard_browser.py` (also run by `tests/test_dashboard_browser.py`) opens
the page in headless Chromium through Playwright, with **every network request blocked**.
At each width it checks:
- the page as loaded, then with every "Show numbers" table open, then after switching to
  the declared field, all seasons, girls and the throws group;
- that the headline cards show the numbers pandas computes from `data/summary/`;
- that the filter bar is still at the top of the screen after scrolling to the bottom.

| Width | Page-level horizontal scroll | Charts drawn (4 bar + 4 donut) | Headline numbers | Sticky filters | Console / page errors | Network |
|---|---|---|---|---|---|---|
| 390 px | none (390 = 390) | 8 of 8 | match | yes | 0 | 0 requests |
| 1400 px | none (1400 = 1400) | 8 of 8 | match | yes | 0 | 0 requests |

Screenshots: `outputs/dashboard_{390,1400}{,_tables_open,_filtered}.png` (git-ignored).

## Not checked here

- **Real phones.** The check uses headless Chromium, not iOS Safari or Android Chrome.
- **Canvas text.** The automated checks confirm the charts drew; they can't read the canvas
  text. A "stray label" bug was caught by viewing the screenshots and fixed.
