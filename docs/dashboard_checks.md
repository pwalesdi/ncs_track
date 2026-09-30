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
| 6 | Left out; 2026, all | Tri-Valley 3 of 96 | `left_out.csv`: 3 of 96 | ✓ |
| 7 | Makeup, girls 100, 2026; utilization, boys throws, 2026 | Per-Area totals | `field_makeup.csv`, `spot_utilization.csv` filtered | ✓ |
| 8 | Utilization, all seasons pooled; flag list | Bay Shore empty lanes, 5 seasons; 22 flags | Sum of `spot_utilization_by_area.csv`; `spot_utilization_flags_empty_lanes.csv` | ✓ |

## Not checked here

- **How it looks.** Layout and chart rendering were not viewed in a browser. The page uses
  one column below about 360 px, and every chart has a table of the same numbers under it.
- **Chart.js loading from the CDN.** Without it the charts don't draw, but the tables
  still show the numbers.
