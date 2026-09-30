"""Audit pass-down routes against a hand-checked event (read-only).

    .venv/bin/python scripts/checks/audit_routes.py [expected.csv]

The expected file (git-ignored; real names) lists season, gender, event_code, area, route,
surname (or any name part) and area_mark for every athlete in the MOC field of one event.
The check: the entrants of that event in outputs/qualifiers.csv are exactly those athletes,
on those routes, with those Area-final marks; the field size; and the no-shows.
Writes outputs/verify/audit_<season>_<gender>_<event>.csv and exits 1 on any difference.
"""

import sys

import pandas as pd

from ncs_track import paths

DEFAULT = paths.OUTPUTS / "verify" / "audit_expected_2025_girls_1600.csv"


def main(path=DEFAULT) -> int:
    want = pd.read_csv(path, dtype=str)
    s, g, e = want.iloc[0][["season", "gender", "event_code"]]
    q = pd.read_csv(paths.OUTPUTS / "qualifiers.csv", low_memory=False, dtype={"event_code": str})
    got = q[(q["season"] == int(s)) & (q["gender"] == g) & (q["event_code"] == e) & (q["in_declared_field"] == 1)].copy()
    got["mark"] = got["area_mark"].astype(str).str.rstrip("a")
    rows, bad = [], 0
    for w in want.itertuples():
        hit = got[got["athlete_name"].str.contains(w.surname, case=False, na=False) & (got["mark"] == w.area_mark)]
        r = hit.iloc[0] if len(hit) == 1 else None
        ok = r is not None and r["area"] == w.area and r["route"] == w.route
        bad += not ok
        rows.append({"expected_area": w.area, "expected_route": w.route, "name": w.surname, "area_mark": w.area_mark,
                     "found": r is not None, "model_area": None if r is None else r["area"],
                     "model_route": None if r is None else r["route"],
                     "area_place": None if r is None else r["area_place"],
                     "competed": None if r is None else r["competed"], "ok": ok})
    extra = len(got) - sum(x["found"] for x in rows)
    out = pd.DataFrame(rows)
    out.to_csv(paths.OUTPUTS / "verify" / f"audit_{s}_{g}_{e}.csv", index=False)
    print(out.to_string(index=False))
    print(f"field: {len(got)} entrants (expected {len(want)}); not on the list: {extra}; "
          f"no-shows: {int(got['no_show'].sum())}; route mismatches: {bad}")
    fail = bad or extra or len(got) != len(want)
    print("AUDIT FAIL" if fail else "AUDIT PASS")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
