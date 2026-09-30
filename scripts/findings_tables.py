"""Markdown tables for docs/findings_v1.md, computed only from data/summary/.

    .venv/bin/python scripts/findings_tables.py [section]

Sections: makeup, spots, results, core, corepooled, tests, leftout, use, pooled.
Every number carries its unit, e.g. "25 of 284 entries made the final (9%)".
"At-large" means only athletes who met the at-large standard; the combined group is
"next best mark + at-large standard".
"""

import sys

import pandas as pd

from ncs_track import paths

S = paths.SUMMARY
AREAS = ["tri-valley", "bay-shore", "redwood-empire", "class-a"]
AREA_NAME = {"tri-valley": "Tri-Valley", "bay-shore": "Bay Shore", "redwood-empire": "Redwood Empire",
             "class-a": "Class A", "unknown": "Unknown"}
TYPE_NAME = {"automatic": "Automatic", "next_best_mark": "Next best mark", "at_large_standard": "At-large standard",
             "replacement": "Replacement", "unexplained": "Unexplained",
             "at_large_combined": "Next best mark + at-large standard"}
TOP8 = "entries made the final"


def rate(k, n, unit: str) -> str:
    """'k of n unit (p%)'; unit is required so no number appears without one."""
    if n is None or pd.isna(n) or not n:
        return f"no {unit.split(' ')[0]}"
    if k is None or pd.isna(k):
        return f"{int(n)} {unit.split(' ')[0]}; too few to show"
    return f"{int(k)} of {int(n)} {unit} ({100 * k / n:.0f}%)"


def table(rows, header) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def seasons(df) -> list:
    return sorted(df["season"].unique())


def makeup() -> str:
    fm = pd.read_csv(S / "field_makeup.csv")
    fm = fm[~fm["rollup"]]
    parts = []
    for field, label in (("qualified", "All qualifiers (everyone who earned a spot, whether or not they entered)"),
                         ("declared", "Actual entries (athletes who entered the MOC)")):
        f = fm[fm["field"] == field]
        types = [t for t in ("automatic", "next_best_mark", "at_large_standard", "replacement", "unexplained")
                 if t in set(f["qualifier_type"])]
        rows = []
        for s in seasons(f):
            fs = f[f["season"] == s]
            total = fs["count"].sum()
            for a in [a for a in AREAS + ["unknown"] if a in set(fs["area"])]:
                fa = fs[fs["area"] == a]
                rows.append([s, AREA_NAME[a], rate(fa["count"].sum(), total, "MOC spots")]
                            + [f"{int(fa.loc[fa['qualifier_type'] == t, 'count'].sum())} spots" for t in types])
        parts.append(f"**{label}**\n\n" + table(rows, ["Season", "Area", "Share of MOC spots"] + [TYPE_NAME[t] for t in types]))
    return "\n\n".join(parts)


def spots() -> str:
    a = pd.read_csv(S / "at_large_share.csv")
    parts = []
    for field, label in (("qualified", "All qualifiers"), ("declared", "Actual entries")):
        f = a[a["field"] == field]
        rows = []
        for s in seasons(f):
            fs = f[f["season"] == s]
            for area in AREAS:
                row = [s, AREA_NAME[area]]
                for t, unit in (("next_best_mark", "next-best-mark spots"), ("at_large_standard", "at-large spots"),
                                ("at_large_combined", "next-best-mark + at-large spots")):
                    ft = fs[fs["spot_type"] == t]
                    row.append(rate(ft.loc[ft["area"] == area, "count"].sum(), ft["count"].sum(), unit))
                rows.append(row)
        parts.append(f"**{label}**\n\n" + table(rows, ["Season", "Area", "Next best mark", "At-large standard",
                                                       "Next best mark + at-large standard"]))
    return "\n\n".join(parts)


def results(types=("automatic", "at_large_combined", "next_best_mark", "at_large_standard", "replacement")) -> str:
    m = pd.read_csv(S / "moc_performance.csv", dtype={"season": str})
    m = m[(m["gender"] == "all") & (m["event"] == "all") & ~m["season"].str.contains("pooled")]
    rows = []
    for s in sorted(m["season"].unique()):
        for area in AREAS:
            for t in types:
                x = m[(m["season"] == s) & (m["area"] == area) & (m["qualifier_type"] == t)]
                if len(x):
                    x = x.iloc[0]
                    rows.append([s, AREA_NAME[area], TYPE_NAME[t], rate_or_small(x["made_final"], x["competed"], TOP8),
                                 rate_or_small(x["scored"], x["competed"], "entries scored (top 6)")])
    return table(rows, ["Season", "Area", "Route", "Made the final", "Scored (top 6)"])


def rate_or_small(k, n, unit) -> str:
    return f"{int(n)} entr{'y' if int(n) == 1 else 'ies'} (fewer than 5: not shown)" if pd.isna(k) else rate(int(k), int(n), unit)


def core(pooled_only=False, groups_only=None) -> str:
    c = pd.read_csv(S / "core_comparison.csv", dtype={"season": str})
    groups = groups_only or ["sprints_hurdles", "400_800", "distance", "jumps", "throws", "relays", "all"]
    gname = {"sprints_hurdles": "sprints & hurdles", "400_800": "400/800", "all": "all events"}
    med = lambda r: "too few to show" if pd.isna(r["median_moc_place"]) else f"{r['median_moc_place']:g}th ({int(r['with_moc_place'])} entries)"
    rows = []
    for s in sorted(c["season"].unique(), key=lambda x: (len(x), x)):
        if pooled_only != ("pooled" in s):
            continue
        for area in AREAS:
            for g in groups:
                x = c[(c["season"] == s) & (c["area"] == area) & (c["event_group"] == g)].set_index("comparison_group")
                lo, ot = x.loc["lowest_automatic"], x.loc["at_large_other_areas"]
                rows.append([s, AREA_NAME[area], gname.get(g, g), rate(lo["made_final"], lo["competed"], TOP8), med(lo),
                             rate(ot["made_final"], ot["competed"], TOP8), med(ot)])
    return table(rows, ["Season", "Area (its lowest automatics)", "Events", "Lowest automatics: made the final",
                        "Lowest automatics: median MOC place", "Other Areas' next best mark + at-large: made the final",
                        "Other Areas' next best mark + at-large: median MOC place"])


def tests() -> str:
    t = pd.read_csv(S / "core_tests.csv")
    fmt = lambda p: "< 0.001" if p < 0.001 else f"{p:.3f}"
    rows = [[AREA_NAME[r.area], rate(r.lowest_auto_top, r.lowest_auto_n, TOP8), rate(r.other_at_large_top, r.other_at_large_n, TOP8),
             f"{100 * r.gap:+.1f} percentage points", fmt(r.naive_p), fmt(r.clustered_p),
             f"{100 * r.expected_gap_random_areas:+.1f} percentage points", fmt(r.permutation_p)] for r in t.itertuples()]
    return table(rows, ["Area", "Lowest automatics", "Other Areas' next best mark + at-large", "Gap",
                        "Old p (independent)", "Clustered by athlete p", "Gap if Areas were random", "Permutation p"])


def use() -> str:
    r = pd.read_csv(S / "spot_utilization_by_area.csv")
    rows = []
    for x in r.itertuples():
        al = (f"{x.at_large_spots} qualifiers: {x.al_competed} competed, {x.al_chose_another_event} chose another event, "
              f"{x.al_did_not_enter} didn't enter" if x.at_large_spots else "none")
        rows.append([x.season, AREA_NAME[x.area], f"{x.guaranteed_spots} spots", x.g_competed, x.g_refilled,
                     x.g_chose_another_event, x.g_did_not_enter, x.g_unfilled,
                     rate(x.guaranteed_used, x.guaranteed_spots, "guaranteed spots used"), al,
                     rate(x.no_show, x.declared, "entries")])
    main = table(rows, ["Season", "Area", "Guaranteed spots", "Competed", "Refilled", "Chose another event",
                        "Didn't enter", "Unfilled (provisional)", "Guaranteed spots used", "At-large standard (separate)",
                        "No-shows"])
    fl = []
    for name, f, unit in (("unfilled spots", "spot_utilization_flags_unfilled.csv", "unfilled spots"),
                          ("any unused spot", "spot_utilization_flags_unused.csv", "unused spots")):
        t = pd.read_csv(S / f)
        fl.append(f"**Area × event with {name} in 3 or more of the 5 seasons: {len(t)} combinations**\n\n" + table(
            [[AREA_NAME[x.area], x.gender, x.event_code, f"{x.seasons_flagged} seasons", x.seasons.replace("|", ", "),
              f"{x.total_all_seasons} {unit}"] for x in t.itertuples()],
            ["Area", "Gender", "Event", "Seasons", "Which", "Total over 5 seasons"]))
    return main + "\n\n" + "\n\n".join(fl)


def pooled() -> str:
    """5-season pooled summary, computed from the tables."""
    fm = pd.read_csv(S / "field_makeup.csv")
    fm = fm[(~fm["rollup"]) & (fm["field"] == "qualified")]
    al = pd.read_csv(S / "at_large_share.csv")
    al = al[(al["field"] == "qualified") & (al["spot_type"] == "at_large_combined")]
    mp = pd.read_csv(S / "moc_performance.csv", dtype={"season": str})
    mp = mp[mp["season"].str.contains("pooled") & (mp["gender"] == "all") & (mp["event"] == "all")]
    ct = pd.read_csv(S / "core_tests.csv").set_index("area")
    su = pd.read_csv(S / "spot_utilization_by_area.csv").groupby("area").sum(numeric_only=True)
    rows = []
    for a in AREAS:
        auto = mp[(mp["area"] == a) & (mp["qualifier_type"] == "automatic")]
        comb = mp[(mp["area"] == a) & (mp["qualifier_type"] == "at_large_combined")]
        t = ct.loc[a]
        rows.append([AREA_NAME[a], rate(fm.loc[fm["area"] == a, "count"].sum(), fm["count"].sum(), "MOC spots"),
                     rate(al.loc[al["area"] == a, "count"].sum(), al["count"].sum(), "next-best-mark + at-large spots"),
                     rate(auto["made_final"].sum(), auto["competed"].sum(), TOP8),
                     rate(comb["made_final"].sum(), comb["competed"].sum(), TOP8),
                     rate(t.lowest_auto_top, t.lowest_auto_n, TOP8) + " vs " + rate(t.other_at_large_top, t.other_at_large_n, TOP8),
                     rate(su.loc[a, "unfilled_spots"], su.loc[a, "guaranteed_spots"], "guaranteed spots unfilled"),
                     rate(su.loc[a, "no_show"], su.loc[a, "declared"], "entries were no-shows")])
    return table(rows, ["Area", "Share of all qualifiers", "Next-best-mark + at-large spots held", "Automatic: made the final",
                        "Next best mark + at-large: made the final", "Lowest automatics vs other Areas' next best mark + at-large: made the final",
                        "Unfilled spots (provisional)", "No-shows"])


SECTIONS = {"makeup": makeup, "spots": spots, "results": results, "core": core,
            "corepooled": lambda: core(True), "tests": tests, "use": use, "pooled": pooled}

if __name__ == "__main__":
    for w in sys.argv[1:] or list(SECTIONS):
        print(f"\n<!-- {w} -->\n")
        print(SECTIONS[w]())
