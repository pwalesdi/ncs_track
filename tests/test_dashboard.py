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
pytestmark = pytest.mark.skipif(not HTML.exists() or shutil.which("osascript") is None,
                                reason="needs dashboard/index.html and osascript")


def _scripts():
    html = HTML.read_text()
    data = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S).group(1)
    agg = re.search(r'<script id="agg">(.*?)</script>', html, re.S).group(1)
    return data, agg


def js(expr: str, tmp_path):
    data, agg = _scripts()
    src = f"{agg}\nvar D = {data};\nJSON.stringify({expr});\n"
    f = tmp_path / "q.js"
    f.write_text(src)
    out = subprocess.run(["osascript", "-l", "JavaScript", str(f)], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


F2026 = '{field:"qualified", season:"2026", gender:"all", event:"all"}'


def summary(name):
    return pd.read_csv(S / name)


# The spot checks recorded in docs/dashboard_checks.md.
def test_1_makeup_qualified_tri_valley(tmp_path):
    m = js(f"makeup(D, {F2026})", tmp_path)
    fm = summary("field_makeup.csv")
    fm = fm[(fm["season"] == 2026) & (fm["field"] == "qualified") & ~fm["rollup"]]
    assert m["tri-valley"]["total"] == fm.loc[fm["area"] == "tri-valley", "count"].sum() == 294
    assert m["_total"] == fm["count"].sum() == 818


def test_2_makeup_declared_bay_shore_automatic(tmp_path):
    m = js('makeup(D, {field:"declared", season:"2026", gender:"all", event:"all"})', tmp_path)
    fm = summary("field_makeup.csv")
    x = fm[(fm["season"] == 2026) & (fm["field"] == "declared") & (fm["area"] == "bay-shore")
           & (fm["qualifier_type"] == "automatic")]
    assert m["bay-shore"]["automatic"] == x["count"].sum() == 187


def test_3_at_large_tri_valley_next_best_mark(tmp_path):
    a = js(f"atLarge(D, {F2026})", tmp_path)
    s = summary("at_large_share.csv")
    s = s[(s["season"] == 2026) & (s["field"] == "qualified")]
    nbm = s[(s["spot_type"] == "next_best_mark") & (s["area"] == "tri-valley")]["count"].sum()
    comb = s[s["spot_type"] == "at_large_combined"]["count"].sum()
    assert (a["tri-valley"]["next_best_mark"], a["_total"]) == (nbm, comb) == (72, 146)


def test_4_performance_class_a_automatic(tmp_path):
    p = js(f"performance(D, {F2026})", tmp_path)
    m = summary("moc_performance.csv")
    x = m[(m["season"] == 2026) & (m["area"] == "class-a") & (m["qualifier_type"] == "automatic")]
    assert (p["class-a"]["automatic"]["top_finish"], p["class-a"]["automatic"]["competed"]) == \
        (x["top_finish"].sum(), x["competed"].sum()) == (7, 83)


def test_5_utilization_redwood_empire(tmp_path):
    u = js(f"utilization(D, {F2026})", tmp_path)["redwood-empire"]
    r = summary("spot_utilization_by_area.csv")
    r = r[(r["season"] == 2026) & (r["area"] == "redwood-empire")].iloc[0]
    assert (u["empty_lanes"], u["spots_earned"], u["no_show"], u["declared"]) == \
        (r["empty_lanes"], r["spots_earned"], r["no_show"], r["declared"]) == (17, 216, 3, 193)


def test_6_left_out_tri_valley(tmp_path):
    lo = js(f"leftOut(D, {F2026})", tmp_path)["tri-valley"]
    s = summary("left_out.csv")
    s = s[(s["season"] == 2026) & (s["area"] == "tri-valley") & s["moc_cutoff_mark"].notna()]
    assert (lo["hits"], lo["total"]) == (int(s["area_mark_would_have_been_top_finish"].fillna(False).astype(bool).sum()),
                                         len(s)) == (0, 96)   # 3 of 96 before the all-rounds cutoff


def test_7_single_event_and_group_filters(tmp_path):
    m = js('makeup(D, {field:"qualified", season:"2026", gender:"girls", event:"100"})', tmp_path)
    fm = summary("field_makeup.csv")
    x = fm[(fm["season"] == 2026) & (fm["field"] == "qualified") & ~fm["rollup"] & (fm["gender"] == "girls")
           & (fm["event_code"].astype(str) == "100")]
    for area in ("tri-valley", "bay-shore", "redwood-empire", "class-a"):
        assert m[area]["total"] == x.loc[x["area"] == area, "count"].sum()
    u = js('utilization(D, {field:"qualified", season:"2026", gender:"boys", event:"group:throws"})', tmp_path)
    su = summary("spot_utilization.csv")
    y = su[(su["season"] == 2026) & (su["gender"] == "boys") & su["event_code"].isin(["SP", "DT"])]
    for area in ("tri-valley", "class-a"):
        assert u[area]["spots_earned"] == y.loc[y["area"] == area, "spots_earned"].sum()


def test_8_pooled_seasons_and_flags(tmp_path):
    u = js('utilization(D, {field:"qualified", season:"all", gender:"all", event:"all"})', tmp_path)
    r = summary("spot_utilization_by_area.csv")
    assert u["bay-shore"]["empty_lanes"] == r.loc[r["area"] == "bay-shore", "empty_lanes"].sum()
    fl = js('flags(D, {field:"qualified", season:"2026", gender:"all", event:"all"})', tmp_path)
    assert len(fl["empty_lanes"]) == len(summary("spot_utilization_flags_empty_lanes.csv"))


def test_render_script_compiles(tmp_path):
    """The DOM script can't run without a browser; at least make sure it parses."""
    html = HTML.read_text()
    main = re.findall(r"<script>(.*?)</script>", html, re.S)[-1]
    f = tmp_path / "c.js"
    f.write_text(f"new Function({json.dumps(main)}); 'ok';")
    out = subprocess.run(["osascript", "-l", "JavaScript", str(f)], capture_output=True, text=True)
    assert out.returncode == 0 and out.stdout.strip() == "ok", out.stderr


def test_9_panel6_matches_core_comparison(tmp_path):
    cc = js(f"coreCompare(D, {F2026})", tmp_path)
    t = pd.read_csv(S / "core_comparison.csv", dtype={"season": str})
    t = t[(t["season"] == "2026") & (t["event_group"] == "all")].set_index(["area", "comparison_group"])
    for area in ("tri-valley", "bay-shore", "redwood-empire", "class-a"):
        for js_key, grp in (("lowest_automatic", "lowest_automatic"), ("other_at_large", "at_large_other_areas")):
            x = t.loc[(area, grp)]
            assert (cc[area][js_key]["competed"], cc[area][js_key]["top_finish"]) == (x["competed"], x["top_finish"])
            assert cc[area][js_key]["median_place"] == x["median_moc_place"]
    assert (cc["class-a"]["lowest_automatic"]["top_finish"], cc["class-a"]["lowest_automatic"]["competed"]) == (1, 28)


def expected_headline():
    """The headline cards' numbers computed with pandas from data/summary/ (pooled 2022-2026)."""
    al = summary("at_large_share.csv")
    al = al[(al["field"] == "qualified") & (al["spot_type"] == "at_large_combined")]
    cc = summary("core_place_counts.csv")
    cmp_ = pd.read_csv(S / "core_comparison.csv", dtype={"season": str})
    pooled = cmp_[cmp_["season"].str.contains("pooled") & (cmp_["event_group"] == "all")]
    su = summary("spot_utilization_by_area.csv")
    out = {"tv_at_large": (int(al.loc[al["area"] == "tri-valley", "count"].sum()), int(al["count"].sum())),
           "empty_lanes": (int(su["empty_lanes"].sum()), int(su["spots_earned"].sum())), "lowest_auto": {}, "at_large": {}}
    for a in ("tri-valley", "bay-shore", "redwood-empire", "class-a"):
        low = cc[(cc["area"] == a) & (cc["route"] == "lowest_automatic")]
        own = cc[(cc["area"] == a) & (cc["route"] == "at_large")]
        out["lowest_auto"][a] = (int(low.loc[low["top_finish"] == 1, "count"].sum()), int(low["count"].sum()))
        out["at_large"][a] = (int(own.loc[own["top_finish"] == 1, "count"].sum()), int(own["count"].sum()))
        p = pooled[(pooled["area"] == a) & (pooled["comparison_group"] == "lowest_automatic")].iloc[0]
        assert out["lowest_auto"][a] == (p["top_finish"], p["competed"])     # counts table agrees with core_comparison
    return out


def test_10_headline_matches_summary(tmp_path):
    h = js("headline(D)", tmp_path)
    e = expected_headline()
    assert (h["tv_at_large"]["k"], h["tv_at_large"]["n"]) == e["tv_at_large"] == (464, 659)
    assert (h["empty_lanes"]["k"], h["empty_lanes"]["n"]) == e["empty_lanes"]
    for a, (k, n) in e["lowest_auto"].items():
        assert (h["lowest_auto"][a]["k"], h["lowest_auto"][a]["n"]) == (k, n)
    for a, (k, n) in e["at_large"].items():
        assert (h["at_large"][a]["k"], h["at_large"][a]["n"]) == (k, n)
