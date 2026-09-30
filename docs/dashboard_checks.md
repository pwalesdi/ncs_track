# Dashboard checks

`dashboard/index.html` is built by `.venv/bin/python scripts/build_dashboard.py`, from
`dashboard/template.html` and the tables in `data/summary/`. The tables are embedded as
JSON with no athlete names, and MOC-place figures only for groups of 5 or more entries. Chart.js 4.4.1 is inlined from `dashboard/vendor/`, pinned by
SHA-256, so the page works offline.

## Numbers: the page's own code against the summary tables

`tests/test_dashboard.py` runs the page's aggregation code (the `agg` script block) on its
embedded data with macOS's JavaScript engine (`osascript -l JavaScript`), then compares the
results with pandas reading `data/summary/`. Checked 2026-09-30; all pass.

| # | View | Checked | Summary table |
|---|---|---|---|
| 1 | Field makeup, all qualifiers, 2026 | Tri-Valley 294 of 818 MOC spots; 72 next best mark, 30 at-large | `field_makeup.csv` |
| 2 | Field makeup, actual entries, 2026 | Bay Shore 187 automatic | `field_makeup.csv` |
| 3 | Next best mark + at-large spots, 2026 | Tri-Valley 72 of 103 next-best-mark spots; 43 at-large; 146 together | `at_large_share.csv` |
| 4 | MOC performance, 2026 | Class A automatic: 7 of 83 entries made the final; a 1-entry cell comes through blank | `moc_performance.csv` |
| 5 | Spot use, every Area × season | Five guaranteed-spot segments sum to guaranteed spots; guaranteed spots used; at-large line sums to at-large spots | `spot_utilization_by_area.csv` |
| 5b | Donut captions | "6 of 6 guaranteed spots: 5 competed · 1 chose another event"; at-large line | – |
| 5c | Unfilled table | Area × season and Area × event totals | `spot_utilization.csv` |
| 7 | Area place vs. MOC finish, pooled + 2024 girls throws | Every Area × place: entries, made the final, median (blank below 5) | `core_place_curve.csv` |
| 8 | Overview cards | 6th place per Area (CA 3rd); TV 7th–8th (253, 13th) vs BS + RE 5th–6th (561, 18th); 464 of 659 spots; unfilled total | `core_place_curve.csv`, `at_large_share.csv`, `spot_utilization_by_area.csv` |
| 9 | Flag list; boys throws filter | Rows = `spot_utilization_flags_unfilled.csv`; spots earned by Area | `spot_utilization.csv` |
| 10 | Units | "294 of 818 MOC spots (36%)", "19 of 59 entries made the final (32%)", ordinals | – |

## Browser: every tab at both widths

`scripts/checks/dashboard_browser.py` (also run by `tests/test_dashboard_browser.py`) opens
the page in headless Chromium through Playwright, with every network request blocked. At
390 px and 1400 px it visits every tab in three views: all seasons side by side (the
default), focused on 2026, and all seasons pooled. In each it checks:
- no page-level horizontal scroll;
- every chart in the visible tab drew;
- no "undefined" or "NaN" in the page text, chart labels, tooltips or donut centres;
- no console errors;
- that the Overview cards match pandas;
- that below 700 px the filters sit behind the "Filters" button;
- on Spot use, that every donut caption's counts sum to its total (both the embedded counts and
  the numbers printed in the caption), and that the legend swatches are the colors drawn.

Result 2026-09-30: all pass at both widths, with 0 network requests. Charts drawn per tab
and view (the same at both widths):

| Tab | Side by side | Focus on 2026 | Pooled |
|---|---|---|---|
| Area place vs. MOC finish | 10 (5 seasons × median, made the final) | 2 | 2 |
| Field makeup | grid | 1 | 1 |
| Next best mark + at-large spots | grid | 1 | 1 |
| MOC performance | 2 grids | 1 | 1 |
| Spot use | 20 donuts (Area × season), 20 captions checked | 4 (4 captions) | 4 (4 captions) |

Screenshots: `outputs/tabs/{390,1400}_{tab}.png` for the default view, plus
`_{2026,pooled}` versions (git-ignored).

## Not checked here

- **Real phones and projectors.** The check uses headless Chromium only.
- **Canvas text.** Labels are checked through the chart objects, not by reading pixels.
