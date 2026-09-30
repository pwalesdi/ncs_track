"""Markdown tables for docs/findings_v1.md, computed only from data/summary/.

    .venv/bin/python scripts/findings_tables.py [section]

Sections: makeup, atlarge, results, core, leftout, utilization, all (default). Every rate
is printed with its count, e.g. "42% (11 of 26)".
"""

import sys

import pandas as pd

from ncs_track import paths

S = paths.SUMMARY
AREAS = ["tri-valley", "bay-shore", "redwood-empire", "class-a"]
AREA_NAME = {"tri-valley": "Tri-Valley", "bay-shore": "Bay Shore", "redwood-empire": "Redwood Empire",
             "class-a": "Class A", "unknown": "Unknown"}
TYPE_NAME = {"automatic": "Automatic", "next_best_mark": "Next best mark", "at_large_standard": "At-large standard",
             "replacement": "Replacement", "unexplained": "Unexplained", "at_large_combined": "At-large (combined)"}


def rate(k, n) -> str:
    if not n:
        return "–"
    return f"{100 * k / n:.0f}% ({int(k)} of {int(n)})"


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
    for field, label in (("qualified", "Everyone who qualified"), ("declared", "Who actually declared")):
        f = fm[fm["field"] == field]
        types = [t for t in ("automatic", "next_best_mark", "at_large_standard", "replacement", "unexplained")
                 if t in set(f["qualifier_type"])]
        rows = []
        for s in seasons(f):
            fs = f[f["season"] == s]
            total = fs["count"].sum()
            for a in [a for a in AREAS + ["unknown"] if a in set(fs["area"])]:
                fa = fs[fs["area"] == a]
                rows.append([s, AREA_NAME[a], rate(fa["count"].sum(), total)]
                            + [int(fa.loc[fa["qualifier_type"] == t, "count"].sum()) for t in types])
        parts.append(f"**{label}** (share of the whole field; then counts by how they got in)\n\n"
                     + table(rows, ["Season", "Area", "Share of field"] + [TYPE_NAME[t] for t in types]))
    return "\n\n".join(parts)


def atlarge() -> str:
    a = pd.read_csv(S / "at_large_share.csv")
    parts = []
    for field, label in (("qualified", "Everyone who qualified"), ("declared", "Who actually declared")):
        f = a[a["field"] == field]
        rows = []
        for s in seasons(f):
            fs = f[f["season"] == s]
            for area in AREAS:
                row = [s, AREA_NAME[area]]
                for t in ("next_best_mark", "at_large_standard", "at_large_combined"):
                    ft = fs[fs["spot_type"] == t]
                    row.append(rate(ft.loc[ft["area"] == area, "count"].sum(), ft["count"].sum()))
                rows.append(row)
        parts.append(f"**{label}** (each Area's share of that season's spots of each type)\n\n"
                     + table(rows, ["Season", "Area", "Next best mark", "At-large standard", "Combined"]))
    return "\n\n".join(parts)


def results(types=("automatic", "at_large_combined", "next_best_mark", "at_large_standard", "replacement")) -> str:
    m = pd.read_csv(S / "moc_performance.csv")
    m = m[~m["rollup"] | (m["qualifier_type"] == "at_large_combined")]
    rows = []
    for s in seasons(m):
        ms = m[m["season"] == s]
        for area in AREAS:
            for t in types:
                x = ms[(ms["area"] == area) & (ms["qualifier_type"] == t)]
                n = x["competed"].sum()
                if n:
                    rows.append([s, AREA_NAME[area], TYPE_NAME[t], rate(x["top_finish"].sum(), n),
                                 rate(x["scored"].sum(), n)])
    return table(rows, ["Season", "Area", "How they qualified", "Top finish (top 8/9)", "Scored (top 6)"])


def core(pooled_only=False, groups_only=None) -> str:
    c = pd.read_csv(S / "core_comparison.csv", dtype={"season": str})
    groups = groups_only or ["sprints_hurdles", "400_800", "distance", "jumps", "throws", "relays", "all"]
    rows = []
    for s in sorted(c["season"].unique(), key=lambda x: (len(x), x)):
        if pooled_only != ("pooled" in s):
            continue
        for area in AREAS:
            for g in groups:
                x = c[(c["season"] == s) & (c["area"] == area) & (c["event_group"] == g)].set_index("comparison_group")
                lo, ot = x.loc["lowest_automatic"], x.loc["at_large_other_areas"]
                med = lambda r: "–" if pd.isna(r["median_moc_place"]) else f"{r['median_moc_place']:g} (n={int(r['with_moc_place'])})"
                rows.append([s, AREA_NAME[area], g.replace("_", " / " if g == "400_800" else " ").replace("400 / 800", "400/800"),
                             rate(lo["top_finish"], lo["competed"]), med(lo),
                             rate(ot["top_finish"], ot["competed"]), med(ot)])
    return table(rows, ["Season", "Area (its lowest autos)", "Event group", "Lowest autos: top finish",
                        "Lowest autos: median MOC place", "Other Areas' at-large: top finish",
                        "Other Areas' at-large: median MOC place"])


def leftout() -> str:
    lo = pd.read_csv(S / "left_out.csv")
    lo = lo[lo["moc_cutoff_mark"].notna()]
    rows = []
    for s in seasons(lo):
        for area in AREAS:
            x = lo[(lo["season"] == s) & (lo["area"] == area)]
            k = x["area_mark_would_have_been_top_finish"].fillna(False).astype(bool).sum()
            d = x.loc[x["area_mark_would_have_been_top_finish"].fillna(False).astype(bool), "declared_anyway"]
            rows.append([s, AREA_NAME[area], rate(k, len(x)), int(d.fillna(False).astype(bool).sum())])
    return table(rows, ["Season", "Area", "Best non-qualifiers with an Area mark at/above the MOC top-8/9 cutoff",
                        "…of whom were in the MOC program anyway"])


def utilization() -> str:
    n = pd.read_csv(S / "no_shows_empty_lanes_by_area.csv")
    r = pd.read_csv(S / "spot_utilization_by_area.csv")
    rows = []
    for x in n.merge(r[["season", "area", "competed", "not_declared_individual", "not_declared_competed_other_event"]],
                     on=["season", "area"]).itertuples():
        rows.append([x.season, AREA_NAME[x.area], x.spots_earned, rate(x.competed, x.spots_earned),
                     rate(x.no_show, x.declared), x.not_declared,
                     rate(x.not_declared_competed_other_event, x.not_declared_individual),
                     x.vacancies_refilled, rate(x.empty_lanes, x.spots_earned)])
    main = table(rows, ["Season", "Area", "Spots earned", "Used (competed)", "No-shows (of declared)",
                        "Not declared", "…ran another MOC event", "Refilled", "Empty lanes"])
    fl = []
    for name, f in (("empty lanes", "spot_utilization_flags_empty_lanes.csv"), ("unused spots", "spot_utilization_flags.csv")):
        t = pd.read_csv(S / f)
        fl.append(f"**Area × event with {name} in 3+ of 5 seasons: {len(t)}**\n\n" + table(
            [[AREA_NAME[x.area], x.gender, x.event_code, x.seasons_flagged, x.seasons.replace("|", ", "), x.total_all_seasons]
             for x in t.itertuples()], ["Area", "Gender", "Event", "Seasons", "Which", f"Total {name}"]))
    return main + "\n\n" + "\n\n".join(fl)


def tests() -> str:
    t = pd.read_csv(S / "core_tests.csv")
    fmt = lambda p: "< 0.001" if p < 0.001 else f"{p:.3f}"
    rows = [[AREA_NAME[r.area], rate(r.lowest_auto_top, r.lowest_auto_n), rate(r.other_at_large_top, r.other_at_large_n),
             f"{100 * r.gap:+.1f} pts", fmt(r.naive_p), fmt(r.clustered_p),
             f"{100 * r.expected_gap_random_areas:+.1f} pts", fmt(r.permutation_p)] for r in t.itertuples()]
    return table(rows, ["Area", "Lowest autos: top finish", "Other Areas' at-large: top finish", "Gap",
                        "Old p (independent)", "Clustered by athlete p", "Gap if Areas were random",
                        "Permutation p"])


SECTIONS = {"tests": tests, "makeup": makeup, "atlarge": atlarge, "results": results, "core": core,
            "corepooled": lambda: core(True), "leftout": leftout, "utilization": utilization}

if __name__ == "__main__":
    which = sys.argv[1:] or list(SECTIONS)
    for w in which:
        print(f"\n<!-- {w} -->\n")
        print(SECTIONS[w]())
