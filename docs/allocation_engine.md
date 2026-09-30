# Allocation engine

`src/ncs_track/allocate.py` works out who reaches the MOC under an allocation described by a
config in `configs/allocation/`. It generalises the rules replay. The only config in the
repo is **`current.yaml`, the existing system**; no alternative allocations have been
created or evaluated.

```
python -m ncs_track allocate --config configs/allocation/current.yaml --season 2022 2023 2024 2025 2026 [--compare]
```

The command writes `outputs/allocation_{name}_{season}.csv` (git-ignored: it names
athletes) and prints allocated spots by Area and route. `--compare` scores the allocation
against the real MOC program, which is only meaningful for `current.yaml`.

## Config

| Key | Meaning |
|---|---|
| `name`, `description` | Label (used in output file names) and plain-English summary |
| `auto_spots` | Automatic places per Area: `tri-valley`, `bay-shore`, `redwood-empire`, `class-a` |
| `fill.count` | Fill spots per event ("next best marks") |
| `fill.pool` | Areas whose non-automatic marks compete for fill spots |
| `fill.order` | `before_at_large` (fill first; at-large takes whoever else meets the standard) or `after_at_large` |
| `fill.ties` | `include` (all marks tied at the last fill spot get in) or `exclude` |
| `at_large.mode` | `on` (each season's printed standards), `off` (no at-large) or `adjusted` |
| `at_large.adjust_pct` | With `adjusted`: a positive value makes every standard harder by that % of the mark (faster time, longer or higher mark); a negative value makes it easier |
| `at_large.eligible_outside_top` | Per Area: eligible for at-large if Area place is greater than this |
| `at_large.wind_aided_allowed` | Whether wind-aided marks can meet the standard |
| `replacement` | How vacancies are refilled when comparing with a real program: `off`, `same_area` or `fill_line`. It never changes who is allocated. |
| `qualifying_rounds` | Area rounds whose marks count (`[final]`) |

Standards always come from each season's rules file (`data/reference/rules/{season}.yaml`).
The config only says how to use them.

## Verification

`tests/test_allocate.py` checks that the engine with `current.yaml` reproduces the
validated replay **exactly** for 2022–2026:
- the same allocation, row for row;
- the same RAW and RULES scores against the MOC programs.

It also checks that `current.yaml` agrees with the 2026 rules file (6/6/6/3 automatic,
3 fill spots), and checks config validation and the off/adjusted modes on test fixtures.
