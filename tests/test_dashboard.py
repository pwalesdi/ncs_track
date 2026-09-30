"""Dashboard numbers vs data/summary/.

Runs the dashboard's own aggregation code (the `agg` script in dashboard/index.html) with its
embedded data through macOS JavaScript (osascript -l JavaScript), and compares the numbers it
would show against pandas reading the summary tables directly. Skips where osascript or the
built dashboard is missing.
"""

import json
import re
import shutil
import subprocess

import pandas as pd
import pytest

from ncs_track import paths

HTML = paths.ROOT / "dashboard" / "index.html"
S = paths.SUMMARY
AREAS = ("tri-valley", "bay-shore", "redwood-empire", "class-a")
pytestmark = pytest.mark.skipif(not HTML.exists() or shutil.which("osascript") is None,
                                reason="needs dashboard/index.html and osascript")


def _scripts():
    html = HTML.read_text()
    data = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S).group(1)
    agg = re.search(r'<script id="agg">(.*?)</script>', html, re.S).group(1)
    return data, agg


def js(expr: str, tmp_path):
    data, agg = _scripts()
    f = tmp_path / "q.js"
    f.write_text(f"{agg}\nvar D = {data};\nJSON.stringify({expr});\n")
    out = subprocess.run(["osascript", "-l", "JavaScript", str(f)], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


F2026 = '{field:"qualified", season:"2026", gender:"all", event:"all"}'


def summary(name, **kw):
    return pd.read_csv(S / name, **kw)


def expected_headline():
    """The Overview cards' numbers, computed with pandas from data/summary/ (pooled 2022-2026)."""
    c = summary("core_place_curve.csv", dtype={"season": str, "area_place": str})
    c = c[c["season"].str.contains("pooled") & (c["gender"] == "all") & (c["event_group"] == "all")]
    band = {"tri-valley": "7-8", "bay-shore": "5-6", "redwood-empire": "5-6", "class-a": "3"}
    finish = {a: c[(c["area"] == a) & (c["area_place"] == band[a])].iloc[0] for a in AREAS}
    al = summary("at_large_share.csv")
    al = al[(al["field"] == "qualified") & (al["spot_type"] == "at_large_combined")]
    su = summary("spot_utilization_by_area.csv")
    return {"finish": {a: (int(r["entries"]), float(r["median_moc_place"])) for a, r in finish.items()},
            "tv_spots": (int(al.loc[al["area"] == "tri-valley", "count"].sum()), int(al["count"].sum())),
            "unfilled": (int(su["unfilled_spots"].sum()), int(su["guaranteed_spots"].sum()))}


# The spot checks recorded in docs/dashboard_checks.md.
def test_1_makeup_all_qualifiers(tmp_path):
    m = js(f"makeup(D, {F2026})", tmp_path)
    fm = summary("field_makeup.csv")
    fm = fm[(fm["season"] == 2026) & (fm["field"] == "qualified") & ~fm["rollup"]]
    assert (m["tri-valley"]["total"], m["_total"]) == (fm.loc[fm["area"] == "tri-valley", "count"].sum(), fm["count"].sum()) == (294, 818)
    assert m["tri-valley"]["next_best_mark"] == 72 and m["tri-valley"]["at_large_standard"] == 30


def test_2_makeup_actual_entries(tmp_path):
    m = js('makeup(D, {field:"declared", season:"2026", gender:"all", event:"all"})', tmp_path)
    fm = summary("field_makeup.csv")
    x = fm[(fm["season"] == 2026) & (fm["field"] == "declared") & (fm["area"] == "bay-shore") & (fm["qualifier_type"] == "automatic")]
    assert m["bay-shore"]["automatic"] == x["count"].sum() == 187


def test_3_next_best_mark_and_at_large_spots(tmp_path):
    a = js(f"spotShare(D, {F2026})", tmp_path)
    s = summary("at_large_share.csv")
    s = s[(s["season"] == 2026) & (s["field"] == "qualified")]
    get = lambda t, area=None: s[(s["spot_type"] == t) & ((s["area"] == area) if area else True)]["count"].sum()
    assert (a["tri-valley"]["next_best_mark"], a["_nbm"], a["_std"], a["_total"]) == \
        (get("next_best_mark", "tri-valley"), get("next_best_mark"), get("at_large_standard"), get("at_large_combined")) == (72, 103, 43, 146)


def test_4_performance_class_a_automatic(tmp_path):
    p = js(f"performance(D, {F2026})", tmp_path)
    m = summary("moc_performance.csv")
    x = m[(m["season"] == 2026) & (m["area"] == "class-a") & (m["qualifier_type"] == "automatic")]
    assert (p["class-a"]["automatic"]["top8"], p["class-a"]["automatic"]["entries"]) == (x["top_finish"].sum(), x["competed"].sum()) == (7, 83)


def test_5_spot_use_every_area_every_season(tmp_path):
    r = summary("spot_utilization_by_area.csv").set_index(["season", "area"])
    for season in (2022, 2023, 2024, 2025, 2026):
        u = js(f'spotUse(D, {{season:"{season}", gender:"all", event:"all"}})', tmp_path)
        for a in AREAS:
            row = r.loc[(season, a)]
            assert (u[a]["spots_earned"], u[a]["competed"], u[a]["vacancies_refilled"], u[a]["unfilled_spots"], u[a]["other_unused"]) == \
                (row["spots_earned"], row["competed"], row["vacancies_refilled"], row["unfilled_spots"], row["other_unused"])
            assert u[a]["competed"] + u[a]["vacancies_refilled"] + u[a]["unfilled_spots"] + u[a]["other_unused"] == u[a]["spots_earned"]


def test_6_left_out(tmp_path):
    lo = js(f"leftOut(D, {F2026})", tmp_path)["tri-valley"]
    s = summary("left_out.csv")
    s = s[(s["season"] == 2026) & (s["area"] == "tri-valley") & s["moc_cutoff_mark"].notna()]
    assert (lo["hits"], lo["total"]) == (int(s["area_mark_would_have_been_top_finish"].fillna(False).astype(bool).sum()), len(s)) == (0, 96)


def test_7_place_curve(tmp_path):
    c = js('curve(D, "2022-2026 pooled", "all", "all")', tmp_path)
    t = summary("core_place_curve.csv", dtype={"season": str, "area_place": str})
    t = t[t["season"].str.contains("pooled") & (t["gender"] == "all") & (t["event_group"] == "all")].set_index(["area", "area_place"])
    for a in AREAS:
        for p in [str(i) for i in range(1, 13)] + ["5-6", "7-8"]:
            row = t.loc[(a, p)]
            cell = c[a][p]
            assert cell["entries"] == row["entries"]
            if pd.isna(row["median_moc_place"]):
                assert cell["median"] is None
            else:
                assert cell["median"] == row["median_moc_place"] and cell["top8"] == row["top8_count"]
    assert (c["tri-valley"]["5-6"]["entries"], c["tri-valley"]["5-6"]["top8"], c["tri-valley"]["5-6"]["median"]) == (293, 106, 10)
    g = js('curve(D, "2024", "girls", "throws")', tmp_path)
    tt = summary("core_place_curve.csv", dtype={"season": str, "area_place": str})
    x = tt[(tt["season"] == "2024") & (tt["gender"] == "girls") & (tt["event_group"] == "throws") & (tt["area"] == "bay-shore") & (tt["area_place"] == "1")].iloc[0]
    assert g["bay-shore"]["1"]["entries"] == x["entries"]


def test_8_headline_matches_summary(tmp_path):
    h = js("headline(D)", tmp_path)
    e = expected_headline()
    for a in AREAS:
        assert (h["finish"][a]["cell"]["entries"], h["finish"][a]["cell"]["median"]) == e["finish"][a]
    assert (h["tv_spots"]["k"], h["tv_spots"]["n"]) == e["tv_spots"] == (464, 659)
    assert (h["unfilled"]["k"], h["unfilled"]["n"]) == e["unfilled"]


def test_9_flags_and_filters(tmp_path):
    fl = js('flags(D, {season:"side", gender:"all", event:"all"})', tmp_path)
    assert len(fl) == len(summary("spot_utilization_flags_unfilled.csv"))
    u = js('spotUse(D, {season:"2026", gender:"boys", event:"group:throws"})', tmp_path)
    su = summary("spot_utilization.csv")
    y = su[(su["season"] == 2026) & (su["gender"] == "boys") & su["event_code"].isin(["SP", "DT"])]
    for a in ("tri-valley", "class-a"):
        assert u[a]["spots_earned"] == y.loc[y["area"] == a, "spots_earned"].sum()


def test_10_units_and_ordinals(tmp_path):
    assert js('[spotsTxt(294, 818), top8Txt(19, 59), ordinal(18), ordinal(1), ordinal(22), ordinal(19.5)]', tmp_path) == \
        ["294 of 818 MOC spots (36%)", "19 of 59 entries finished top 8 (32%)", "18th", "1st", "22nd", "19.5th"]


def test_render_script_compiles(tmp_path):
    """The DOM script runs in tests/test_dashboard_browser.py; here, make sure it parses."""
    main = re.findall(r"<script>(.*?)</script>", HTML.read_text(), re.S)[-1]
    f = tmp_path / "c.js"
    f.write_text(f"new Function({json.dumps(main)}); 'ok';")
    out = subprocess.run(["osascript", "-l", "JavaScript", str(f)], capture_output=True, text=True)
    assert out.returncode == 0 and out.stdout.strip() == "ok", out.stderr
