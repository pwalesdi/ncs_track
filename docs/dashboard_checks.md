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
| 9 | Panel 6, 2026, all | Class A lowest autos 1 of 28; every Area/group count and median | `core_comparison.csv` (2026, all events) | ✓ |
| 8 | Utilization, all seasons pooled; flag list | Bay Shore empty lanes, 5 seasons; 22 flags | Sum of `spot_utilization_by_area.csv`; `spot_utilization_flags_empty_lanes.csv` | ✓ |

## Browser check (2026-09-30)

`scripts/checks/dashboard_browser.py` (also run by `tests/test_dashboard_browser.py`) opens
the page in headless Chromium through Playwright, with **every network request blocked**:
Chart.js 4.4.1 is inlined, so the page must work offline. At each width it checks the page
as loaded and again after switching to the declared field, all seasons, girls and the
throws group.

| Width | Page-level horizontal scroll | Charts drawn | Console / page errors | Network requests |
|---|---|---|---|---|
| 390 px | none (scrollWidth 390 = clientWidth 390) | 6 of 6 | 0 | 0 |
| 1400 px | none (1400 = 1400) | 6 of 6 | 0 | 0 |

Screenshots are in `outputs/dashboard_{390,1400}{,_filtered}.png` (git-ignored). Wide
tables scroll inside their own container. The flag list is a full-width panel.

