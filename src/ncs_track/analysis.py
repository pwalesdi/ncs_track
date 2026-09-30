"""Analysis tables behind the dashboard (docs/analysis_tables.md defines every column).

One season at a time, with the best 2026 reading of the rules (BEST_READING) and its
overlays. Everything is split by season, gender and event; main events only (no Unified,
4x800 or relay splits).

  outputs/qualifiers.csv                  athlete-level (names): git-ignored
  data/summary/field_makeup.csv           no names: tracked
  data/summary/at_large_share.csv
  data/summary/moc_performance.csv
  data/summary/spot_utilization.csv       + _by_area.csv roll-up, + _flags.csv
  outputs/left_out.csv                    athlete-level: git-ignored
"""

from __future__ import annotations

import pandas as pd

from . import replay
from .events import EVENTS

BEST_READING = replay.Interpretation(
    name="best-2026", class_a_at_large_outside_top=3, fill_before_at_large=True, fill_source="moc_guide",
    fill_ties_include=True, wind_aided_at_large=True, replacement="same_area", entry_limit=0)

TYPE_OF = {"auto": "automatic", "fill": "next_best_mark", "at_large": "at_large_standard"}
QUALIFIER_TYPES = ("automatic", "next_best_mark", "at_large_standard", "replacement", "unexplained")
AT_LARGE_TYPES = ("next_best_mark", "at_large_standard")
TOP9_EVENTS = {"LJ", "TJ", "SP", "DT"}                 # 9 finalists get extra attempts
NO_PRELIM_EVENTS = {"3200", "HJ", "PV"}                # one final round at the MOC
NOT_COMPETED = {"DNS", "SCR"}
GUARANTEED_TYPES = ("automatic", "next_best_mark")     # the fixed spots; at-large standard has no cap
COMBINED_AREA = "bay-shore+redwood-empire"   # the two other Areas whose 5th-6th are automatic (Class A: top 3)
SPOT_USE = ("competed", "no_show", "not_used")          # guaranteed-spot segments (decision #33)
AUTO_SPOTS = {"tri-valley": 6, "bay-shore": 6, "redwood-empire": 6, "class-a": 3}
AREAS = replay.AREAS
KEY = ["season", "gender", "event_code"]


def top_cut(event: str) -> int:
    return 9 if event in TOP9_EVENTS else 8


# ---------------------------------------------------------------------------
# Athlete-level
# ---------------------------------------------------------------------------
def _with_identity(df: pd.DataFrame, name_col: str, school_col: str, school_key) -> pd.DataFrame:
    df = df.copy()
    df["school_key"] = df[school_col].map(school_key)
    df["identity"] = [replay._identity(n, s, r) for n, s, r in zip(df[name_col], df["school_key"], df["is_relay"])]
    return df


def _moc_outcome(rows: pd.DataFrame, event: str) -> dict:
    """competed, moc_status, moc_final_place, made_final, reached_final_round, scored."""
    if rows.empty:
        return {"competed": 0, "moc_status": "not_in_results", "moc_final_place": None, "made_final": 0,
                "reached_final_round": 0, "scored": 0}
    final = rows[rows["round"] == "final"]
    last = final.iloc[0] if len(final) else rows.iloc[0]
    competed = int((~rows["status"].isin(NOT_COMPETED)).any())
    place = last["place"] if (len(final) and last["status"] == "OK" and pd.notna(last["place"])) else None
    if event in TOP9_EVENTS:
        reached = int(place is not None and place <= 9)            # no attempt data: place <= 9
    else:
        reached = int(len(final) > 0 and competed == 1)
    return {"competed": competed, "moc_status": "OK" if (rows["status"] == "OK").any() else last["status"],
            "moc_final_place": place, "made_final": int(place is not None and place <= top_cut(event)),
            "reached_final_round": reached, "scored": int(place is not None and place <= 6)}


def competed_events(moc_all: pd.DataFrame, legs: pd.DataFrame | None) -> dict[str, set[str]]:
    """athlete_id -> MOC events they competed in (any status but DNS/SCR), incl. relay legs
    and the 4x800. Adaptive events excluded."""
    m = moc_all[~moc_all["is_adaptive"].astype(bool) & ~moc_all["status"].isin(NOT_COMPETED)]
    out: dict[str, set[str]] = {}
    for aid, ev in zip(m["athlete_id"], m["event_code"]):
        if isinstance(aid, str):
            out.setdefault(aid, set()).add(ev)
    if legs is not None and len(legs):
        rel = m[m["is_relay"].astype(bool)][["performance_id", "event_code"]]
        for aid, ev in legs.merge(rel, on="performance_id")[["athlete_id", "event_code"]].itertuples(index=False):
            if isinstance(aid, str):
                out.setdefault(aid, set()).add(ev)
    return out


def moc_overall_places(moc: pd.DataFrame, school_key) -> dict:
    """(gender, event, key) -> overall MOC place, key = athlete_id or relay identity.

    Finalists with a valid final mark keep their final place. Everyone else with a valid
    mark (prelim-only athletes, and finalists without a valid final mark) is ranked after
    them by their best valid mark. Events without prelims: the final place."""
    m = _with_identity(moc, "athlete_name_raw", "school_name_raw", school_key)
    m = m[(m["status"] == "OK") & m["mark_value"].notna()]
    m["key"] = [a if isinstance(a, str) and not r else i for a, i, r in zip(m["athlete_id"], m["identity"], m["is_relay"])]
    out = {}
    for (g, e), x in m.groupby(["gender", "event_code"]):
        measure = EVENTS[e][0]
        fin = x[(x["round"] == "final") & x["place"].notna()]
        for k, pl in zip(fin["key"], fin["place"]):
            out[(g, e, k)] = float(pl)
        rest = x[~x["key"].isin(set(fin["key"]))]
        rest = rest.assign(k=rest["mark_value"] if measure == "time" else -rest["mark_value"])
        best = rest.sort_values("k").drop_duplicates("key")
        n = len(fin)
        for rank, (k, v) in enumerate(zip(best["key"], best["k"]), start=1):
            out[(g, e, k)] = float(n + rank)
    return out


def qualifiers(season: int, comp: replay.Comparison, routes: pd.DataFrame, moc: pd.DataFrame,
               unresolved: pd.DataFrame, school_key, competed_in: dict | None = None,
               overall: dict | None = None) -> pd.DataFrame:
    """One row per athlete (or relay team) x event in the qualified field (pre-declaration
    routes, `comp` from `replay.compare`), the declared field (the MOC program, routes from
    `replay.pass_down`), or who declined a spot.

    qualifier_type  pre-declaration route (who the rules made eligible), "All qualifiers"
    route           pass-down route of a program entrant, "Actual entries"; unexplained if none
    declined        the route whose spot the athlete declined (not in the program)"""
    competed_in = competed_in or {}
    overall = overall or {}
    moc = _with_identity(moc, "athlete_name_raw", "school_name_raw", school_key)
    moc_by_id = {k: g for k, g in moc[moc["athlete_id"].notna()].groupby(["gender", "event_code", "athlete_id"])}
    moc_by_ident = {k: g for k, g in moc.groupby(["gender", "event_code", "identity"])}

    pre = {}
    for r in comp.rows[comp.rows["outcome"] != "entered_not_predicted"].itertuples():
        pre[(r.gender, r.event_code, r.identity)] = r
    keep = routes[routes["declared"].astype(bool) | routes["route"].notna() | routes["declined"].notna()]
    area_perf = {(r.gender, r.event_code, r.identity): r for r in routes[routes["meet_area"].notna()].itertuples()}
    rows = {}
    for r in keep.itertuples():
        k = (r.gender, r.event_code, r.identity)
        if k in rows and not r.declared:
            continue
        rows[k] = r
    out = []
    for k in sorted(set(rows) | set(pre), key=str):
        g, e, ident = k
        r, p = rows.get(k), pre.get(k)
        declared = bool(r is not None and r.declared)
        aid = next((a for a in (getattr(r, "athlete_id", None), getattr(p, "athlete_id", None)) if isinstance(a, str)), None)
        is_relay = ident.startswith("relay|")
        mrows = moc_by_id.get((g, e, aid)) if aid else None
        if mrows is None:
            mrows = moc_by_ident.get((g, e, ident), moc.iloc[0:0])
        outcome = (_moc_outcome(mrows, e) if declared else
                   {"competed": 0, "moc_status": "not_declared", "moc_final_place": None, "made_final": 0,
                    "reached_final_round": 0, "scored": 0})
        qtype = TYPE_OF[p.qualified_by] if p is not None else None
        route = (TYPE_OF.get(r.route, "unexplained") if r.route else "unexplained") if declared else None
        src = r if r is not None else area_perf.get(k, p)
        name = getattr(src, "athlete_name", None)
        out.append({
            "season": season, "gender": g, "event_code": e,
            "athlete_name": name if isinstance(name, str) else None, "is_relay": is_relay, "athlete_id": aid,
            "area": (r.area if r is not None and isinstance(r.area, str) else getattr(p, "area", None)) or "unknown",
            "school": getattr(src, "school_name", None),
            "qualifier_type": qtype, "at_large_combined": int(qtype in AT_LARGE_TYPES),
            "route": route, "declined": TYPE_OF.get(r.declined) if r is not None and r.declined else None,
            "area_place": getattr(src, "place", None), "area_mark": getattr(src, "mark_raw", None),
            "in_qualified_field": int(p is not None), "in_declared_field": int(declared),
            **outcome,
            "no_show": int(declared and not outcome["competed"]),
            "choice_tag": getattr(p, "choice_tag", None) if p is not None and not declared else None,
            "competed_other_moc_event": (None if outcome["competed"] or is_relay or not aid
                                         else int(bool(competed_in.get(aid, set()) - {e}))),
            "moc_overall_place": overall.get((g, e, ident if is_relay else aid)) if declared else None,
            "state_qualified": "pending",
        })
    linked = {(r.gender, r.event_code, r.program_name) for r in routes[routes["declared"].astype(bool)].itertuples()}
    for r in unresolved.itertuples():        # declared, but the school has no area this season
        if (r.gender, r.event_code, r.athlete_name) in linked:
            continue                         # linked to an Area result by name (replay._match_unresolved)
        ident = replay._identity(r.athlete_name, school_key(r.school_name), r.is_relay)
        mrows = moc_by_ident.get((r.gender, r.event_code, ident), moc.iloc[0:0])
        o = _moc_outcome(mrows, r.event_code)
        out.append({"season": season, "gender": r.gender, "event_code": r.event_code,
                    "athlete_name": r.athlete_name if isinstance(r.athlete_name, str) else None,
                    "is_relay": bool(r.is_relay), "athlete_id": None, "area": "unknown", "school": r.school_name,
                    "qualifier_type": None, "at_large_combined": 0, "route": "unexplained", "declined": None,
                    "area_place": None, "area_mark": None, "in_qualified_field": 0, "in_declared_field": 1, **o,
                    "no_show": int(not o["competed"]), "choice_tag": None, "competed_other_moc_event": None,
                    "moc_overall_place": overall.get((r.gender, r.event_code, ident)) if r.is_relay else None,
                    "state_qualified": "pending"})
    return pd.DataFrame(out)


# ---------------------------------------------------------------------------
# Summary tables (no names)
# ---------------------------------------------------------------------------
def entrants(q: pd.DataFrame) -> pd.DataFrame:
    """Program entrants with their pass-down route as qualifier_type (the "Actual entries" view)."""
    d = q[q["in_declared_field"] == 1].copy()
    d["qualifier_type"] = d["route"]
    d["at_large_combined"] = d["route"].isin(AT_LARGE_TYPES).astype(int)
    return d


def _fields(q: pd.DataFrame):
    yield "qualified", q[q["in_qualified_field"] == 1]
    yield "declared", entrants(q)


def field_makeup(q: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for field, f in _fields(q):
        size = f.groupby(KEY).size().rename("field_size")
        c = f.groupby(KEY + ["area", "qualifier_type"]).size().rename("count").reset_index()
        comb = (f[f["at_large_combined"] == 1].groupby(KEY + ["area"]).size().rename("count").reset_index()
                .assign(qualifier_type="at_large_combined"))
        t = pd.concat([c.assign(rollup=False), comb.assign(rollup=True)]).merge(size.reset_index(), on=KEY)
        t["share_of_field"] = (t["count"] / t["field_size"]).round(4)
        parts.append(t.assign(field=field))
    cols = ["season", "gender", "event_code", "field", "area", "qualifier_type", "rollup", "count", "field_size",
            "share_of_field"]
    return pd.concat(parts)[cols].sort_values(cols[:6]).reset_index(drop=True)


def at_large_share(q: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for field, f in _fields(q):
        f = f[f["at_large_combined"] == 1]
        for qtype in (*AT_LARGE_TYPES, "at_large_combined"):
            g = f if qtype == "at_large_combined" else f[f["qualifier_type"] == qtype]
            events = q[KEY].drop_duplicates()
            grid = events.merge(pd.DataFrame({"area": AREAS}), how="cross")
            c = g.groupby(KEY + ["area"]).size().rename("count").reset_index()
            t = grid.merge(c, how="left", on=KEY + ["area"]).fillna({"count": 0})
            t["spots"] = t.groupby(KEY)["count"].transform("sum")
            t["area_share"] = (t["count"] / t["spots"]).where(t["spots"] > 0).round(4)
            parts.append(t.assign(field=field, spot_type=qtype))
    cols = ["season", "gender", "event_code", "field", "spot_type", "area", "count", "spots", "area_share"]
    out = pd.concat(parts)[cols]
    out["count"] = out["count"].astype(int)
    out["spots"] = out["spots"].astype(int)
    return out.sort_values(cols[:6]).reset_index(drop=True)


def moc_performance(q: pd.DataFrame) -> pd.DataFrame:
    """MOC results by route, aggregated to the dashboard's filter grain for the public repo.

    Rows: season (each, plus "2022-2026 pooled") x gender (girls, boys, all) x event (each
    event, "group:<name>", "all") x area x qualifier_type (plus the at_large_combined rollup).
    Entries = athlete-events who competed. made_final, scored, reached_final_round and their
    rates are blank when competed < MIN_CELL (decision #29)."""
    c = entrants(q)
    c = c[c["competed"] == 1]
    c["event_code"] = c["event_code"].astype(str)
    c = pd.concat([c.assign(rollup=False),
                   c[c["at_large_combined"] == 1].assign(qualifier_type="at_large_combined", rollup=True)])
    pooled = f"{int(c['season'].min())}-{int(c['season'].max())} pooled"
    seasons = [(str(int(s)), c[c["season"] == s]) for s in sorted(c["season"].unique())] + [(pooled, c)]
    events = ([(e, [e]) for e in sorted(c["event_code"].unique())]
              + [(f"group:{g}", evs) for g, evs in EVENT_GROUPS.items()] + [("all", None)])
    rows = []
    for season, cs in seasons:
        for gender in ("girls", "boys", "all"):
            cg = cs if gender == "all" else cs[cs["gender"] == gender]
            for ev, evs in events:
                ce = cg if evs is None else cg[cg["event_code"].isin(evs)]
                for (area, qtype, rollup), x in ce.groupby(["area", "qualifier_type", "rollup"]):
                    n = len(x)
                    ok = n >= MIN_CELL
                    row = {"season": season, "gender": gender, "event": ev, "area": area, "qualifier_type": qtype,
                           "rollup": rollup, "competed": n}
                    for k in ("made_final", "scored", "reached_final_round"):
                        row[k] = int(x[k].sum()) if ok else None
                        row[f"{k}_rate"] = round(x[k].mean(), 4) if ok else None
                    rows.append(row)
    out = pd.DataFrame(rows)
    for k in ("made_final", "scored", "reached_final_round"):
        out[k] = out[k].astype("Int64")
    return out


def spot_utilization(q: pd.DataFrame) -> pd.DataFrame:
    """Per season x gender x event x Area (decision #33). Field size plays no part.

    guaranteed_spots  the Area's automatic spots (6; Class A 3; one more per tie at the last
                      automatic place) + next-best-mark spots it won
    g_competed        automatic / next-best-mark entrants who competed in the event
    g_no_show         ... who were in the program for it but didn't compete (DNS or absent)
    g_not_used        guaranteed spots no entrant from the Area took (too few declared finishers)
    passed_down       automatic spots passed down because a finisher ahead declined
    al_*              at-large standard entrants, reported apart
    entries / no_show every program entrant from the Area, any route"""
    d = entrants(q)
    events = q[KEY].drop_duplicates()
    grid = events.merge(pd.DataFrame({"area": AREAS}), how="cross")
    rows = []
    for r in grid.itertuples():
        m = lambda x: x[(x["season"] == r.season) & (x["gender"] == r.gender) & (x["event_code"] == r.event_code)
                        & (x["area"] == r.area)]
        x, allq = m(d), m(q)
        gtd = x[x["qualifier_type"].isin(GUARANTEED_TYPES)]
        al = x[x["qualifier_type"] == "at_large_standard"]
        nbm = int((x["qualifier_type"] == "next_best_mark").sum())
        autos = max(AUTO_SPOTS[r.area], int((x["qualifier_type"] == "automatic").sum()))   # a tie can add one
        spots = autos + nbm
        rows.append({"season": r.season, "gender": r.gender, "event_code": r.event_code, "area": r.area,
                     "auto_spots": autos, "nbm_spots": nbm, "guaranteed_spots": spots,
                     "g_competed": int(gtd["competed"].sum()), "g_no_show": int((gtd["competed"] == 0).sum()),
                     "g_not_used": max(spots - len(gtd), 0),
                     "passed_down": int((allq["declined"] == "automatic").sum()),
                     "declined_nbm": int((allq["declined"] == "next_best_mark").sum()),
                     "declined_at_large": int((allq["declined"] == "at_large_standard").sum()),
                     "at_large_spots": len(al), "al_competed": int(al["competed"].sum()),
                     "al_no_show": int((al["competed"] == 0).sum()),
                     "entries": len(x), "no_show": int((x["competed"] == 0).sum()),
                     "no_show_competed_other_event": int(((x["competed"] == 0) & (x["competed_other_moc_event"] == 1)).sum())})
    return _derived(pd.DataFrame(rows))


def _derived(t: pd.DataFrame) -> pd.DataFrame:
    t = t.copy()
    t["guaranteed_used"] = t["g_competed"]
    t["guaranteed_used_rate"] = (t["g_competed"] / t["guaranteed_spots"]).where(t["guaranteed_spots"] > 0).round(4)
    t["no_show_rate"] = (t["no_show"] / t["entries"]).where(t["entries"] > 0).round(4)
    return t


ADDITIVE = ["auto_spots", "nbm_spots", "guaranteed_spots", "g_competed", "g_no_show", "g_not_used", "passed_down",
            "declined_nbm", "declined_at_large", "at_large_spots", "al_competed", "al_no_show", "entries", "no_show",
            "no_show_competed_other_event"]


def spot_utilization_by_area(t: pd.DataFrame) -> pd.DataFrame:
    """Roll-up per season x area over all events."""
    return _derived(t.groupby(["season", "area"])[ADDITIVE].sum().reset_index())


EVENT_GROUPS = {
    "sprints_hurdles": ["100", "200", "100H", "110H", "300H"], "400_800": ["400", "800"],
    "distance": ["1600", "3200"], "jumps": ["HJ", "PV", "LJ", "TJ"], "throws": ["SP", "DT"],
    "relays": ["4x100", "4x400"],
}
GROUP_OF = {e: g for g, evs in EVENT_GROUPS.items() for e in evs}
LOWEST_AUTO_PLACES = {"tri-valley": (5, 6), "bay-shore": (5, 6), "redwood-empire": (5, 6), "class-a": (3,)}


def core_comparison(q: pd.DataFrame) -> pd.DataFrame:
    """Each Area's lowest automatic qualifiers (places 5-6; Class A 3rd) vs at-large
    qualifiers (next_best_mark + at_large_standard) from the other Areas, among athletes who
    competed at the MOC. Genders combined. Per season and pooled 2022-2026; per event group
    and all events."""
    c = entrants(q)
    c = c[c["competed"] == 1]
    c["event_group"] = c["event_code"].map(GROUP_OF)
    rows = []
    seasons = [(str(s), c[c["season"] == s]) for s in sorted(c["season"].unique())]
    seasons.append((f"{c['season'].min()}-{c['season'].max()} pooled", c))
    for season, cs in seasons:
        for group in (*EVENT_GROUPS, "all"):
            cg = cs if group == "all" else cs[cs["event_group"] == group]
            for area, places in LOWEST_AUTO_PLACES.items():
                low = cg[(cg["area"] == area) & (cg["qualifier_type"] == "automatic") & cg["area_place"].isin(places)]
                other = cg[(cg["area"] != area) & (cg["area"] != "unknown") & (cg["at_large_combined"] == 1)]
                for label, x in (("lowest_automatic", low), ("at_large_other_areas", other)):
                    placed = x["moc_overall_place"].dropna()
                    ok = len(x) >= MIN_CELL            # small cells: counts only, no MOC-place figures
                    rows.append({"season": season, "event_group": group, "area": area, "comparison_group": label,
                                 "places_compared": "|".join(map(str, places)) if label == "lowest_automatic" else "",
                                 "competed": len(x), "made_final": int(x["made_final"].sum()) if ok else None,
                                 "made_final_rate": round(x["made_final"].mean(), 4) if ok else None,
                                 "with_moc_place": len(placed),
                                 "median_moc_place": float(placed.median()) if ok and len(placed) else None})
    return pd.DataFrame(rows)


def _core_rows(q: pd.DataFrame) -> pd.DataFrame:
    """Athletes in either comparison group, with a fixed 'lowest automatic' flag."""
    c = entrants(q)
    c = c[(c["competed"] == 1) & c["area"].isin(AREAS)]
    low_places = c["area"].map(LOWEST_AUTO_PLACES)
    c["lowest_auto"] = [(t == "automatic") and (p in pl) for t, p, pl in
                        zip(c["qualifier_type"], c["area_place"], low_places)]
    c["at_large"] = c["at_large_combined"] == 1
    c = c[c["lowest_auto"] | c["at_large"]].reset_index(drop=True)
    # Cluster: the athlete (relays: the team, i.e. school x season).
    c["cluster"] = [f"a{a}" if isinstance(a, str) else f"t{s}|{sch}" for a, s, sch in
                    zip(c["athlete_id"], c["season"], c["school"])]
    return c


MIN_CELL = 5          # public tables: MOC-place figures only for cells with at least this many entries
PLACE_BANDS = {"5-6": (5, 6), "7-8": (7, 8)}
NOT_AUTO_BAND = "7-8 not automatic"   # Area 7th-8th entrants on a next-best-mark or at-large route


def core_place_curve(q: pd.DataFrame) -> pd.DataFrame:
    """Where Area finishers end up at the MOC, aggregated for the public repo.

    Rows: season (each, plus "2022-2026 pooled") x gender (girls, boys, all) x event_group
    (six groups, plus all) x area (plus COMBINED_AREA) x area_place ("1".."12", plus the bands "5-6" and "7-8").
    Entries = athlete-events who competed at the MOC (one athlete in two events counts twice).
    made_final_count and median_moc_place are blank when entries < MIN_CELL, so no row reveals a
    single athlete's MOC place."""
    c = entrants(q)
    c = c[(c["competed"] == 1) & c["area"].isin(AREAS) & c["area_place"].between(1, 12)]
    c["event_group"] = c["event_code"].astype(str).map(GROUP_OF)
    c["area_place"] = c["area_place"].astype(int)
    pooled = f"{int(c['season'].min())}-{int(c['season'].max())} pooled"
    seasons = [(str(int(s)), c[c["season"] == s]) for s in sorted(c["season"].unique())] + [(pooled, c)]
    places = [(str(p), (p,)) for p in range(1, 13)] + list(PLACE_BANDS.items()) + [(NOT_AUTO_BAND, (7, 8))]
    rows = []
    for season, cs in seasons:
        for gender in ("girls", "boys", "all"):
            cg = cs if gender == "all" else cs[cs["gender"] == gender]
            for group in (*EVENT_GROUPS, "all"):
                ce = cg if group == "all" else cg[cg["event_group"] == group]
                for area in (*AREAS, COMBINED_AREA):
                    ca = ce[ce["area"].isin(area.split("+"))]
                    for label, pl in places:
                        x = ca[ca["area_place"].isin(pl)]
                        rest = 0
                        if label == NOT_AUTO_BAND:            # 7th-8th who got in without an automatic spot
                            rest = int((x["qualifier_type"] == "automatic").sum())
                            x = x[x["qualifier_type"] != "automatic"]
                        n = len(x)
                        # a combined or subset cell is shown only when its parts are, so no suppressed
                        # cell can be recovered by subtraction
                        ok = (n >= MIN_CELL and all((x["area"] == a).sum() >= MIN_CELL for a in area.split("+"))
                              and (rest == 0 or rest >= MIN_CELL))
                        placed = x["moc_overall_place"].dropna()
                        rows.append({"season": season, "gender": gender, "event_group": group, "area": area,
                                     "area_place": label, "entries": n,
                                     "made_final_count": int(x["made_final"].sum()) if ok else None,
                                     "median_moc_place": float(placed.median()) if ok and len(placed) else None})
    out = pd.DataFrame(rows)
    out["made_final_count"] = out["made_final_count"].astype("Int64")
    return out


def _naive_p(k1, n1, k2, n2) -> float:
    import math
    p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return math.erfc(abs(k1 / n1 - k2 / n2) / se / math.sqrt(2)) if se else float("nan")


def _clustered_p(y, g, clusters) -> tuple[float, float]:
    """Difference in means (g=1 minus g=0) with an athlete-clustered (CR1) standard error,
    from a linear probability model y = a + b*g. Returns (b, two-sided normal p)."""
    import math

    import numpy as np
    y = np.asarray(y, float)
    X = np.column_stack([np.ones(len(y)), np.asarray(g, float)])
    xtx_inv = np.linalg.inv(X.T @ X)
    beta = xtx_inv @ X.T @ y
    u = y - X @ beta
    codes, uniq = pd.factorize(pd.Series(clusters))
    meat = np.zeros((2, 2))
    for c in range(len(uniq)):
        m = codes == c
        s_c = X[m].T @ u[m]
        meat += np.outer(s_c, s_c)
    n, k, G = len(y), 2, len(uniq)
    corr = G / (G - 1) * (n - 1) / (n - k)
    V = corr * xtx_inv @ meat @ xtx_inv
    se = math.sqrt(V[1, 1])
    return float(beta[1]), math.erfc(abs(beta[1]) / se / math.sqrt(2)) if se else float("nan")


def core_tests(q: pd.DataFrame, n_perm: int = 10000, seed: int = 20260930) -> pd.DataFrame:
    """Pooled 2022-2026, all events: each Area's lowest automatic qualifiers vs other Areas'
    at-large qualifiers, with three p-values.

    naive_p        two-proportion z test, every athlete-event independent (the old test)
    clustered_p    same difference, standard error clustered by athlete (repeat athletes)
    permutation_p  Area labels shuffled within season x gender x event (route kept fixed),
                   10,000 times: is this Area's gap larger than random Area labels give?
                   Two-sided around the permutation mean (reported as expected_gap)."""
    import numpy as np
    c = _core_rows(q)
    c["stratum"] = c["season"].astype(str) + "|" + c["gender"] + "|" + c["event_code"].astype(str)
    c = c.sort_values("stratum", kind="stable").reset_index(drop=True)
    strata = pd.factorize(c["stratum"])[0]
    y = c["made_final"].to_numpy(float)
    low = c["lowest_auto"].to_numpy()
    atl = c["at_large"].to_numpy()
    areas = c["area"].to_numpy()

    def gaps(area_labels):
        out = {}
        for a in AREAS:
            lm = low & (area_labels == a)
            om = atl & (area_labels != a)
            out[a] = (y[lm].mean() - y[om].mean()) if lm.any() and om.any() else np.nan
        return out

    observed = gaps(areas)
    rng = np.random.default_rng(seed)
    null = {a: np.empty(n_perm) for a in AREAS}
    for i in range(n_perm):
        order = np.lexsort((rng.random(len(c)), strata))
        g = gaps(areas[order])
        for a in AREAS:
            null[a][i] = g[a]
    rows = []
    for a in AREAS:
        lm, om = low & (areas == a), atl & (areas != a)
        k1, n1, k2, n2 = int(y[lm].sum()), int(lm.sum()), int(y[om].sum()), int(om.sum())
        sub = c[lm | om]
        if n1 == 0 or n2 == 0:
            rows.append({"area": a, "lowest_auto_n": n1, "other_at_large_n": n2})
            continue
        b, p_cl = _clustered_p(sub["made_final"], sub["lowest_auto"] & (sub["area"] == a), sub["cluster"])
        nd = null[a][~np.isnan(null[a])]
        centre = nd.mean()
        p_perm = (np.sum(np.abs(nd - centre) >= abs(observed[a] - centre) - 1e-12) + 1) / (len(nd) + 1)
        rows.append({"area": a, "seasons": f"{q['season'].min()}-{q['season'].max()}", "event_group": "all",
                     "lowest_auto_top": k1, "lowest_auto_n": n1, "other_at_large_top": k2, "other_at_large_n": n2,
                     "gap": round(k1 / n1 - k2 / n2, 4), "naive_p": round(_naive_p(k1, n1, k2, n2), 4),
                     "clustered_p": round(p_cl, 4), "clusters": int(sub["cluster"].nunique()),
                     "expected_gap_random_areas": round(float(centre), 4),
                     "permutation_p": round(float(p_perm), 4), "permutations": n_perm})
    return pd.DataFrame(rows)


def left_out(season: int, routes: pd.DataFrame, q: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Left out (decision #34): finished in an Area final behind the Area's last automatic
    qualifier, no route and not in the program (so never offered a spot). Each is compared
    with the automatic qualifiers (pass-down) from the other Areas: a qualifier is "beaten"
    when their Area-final mark is strictly worse. Returns (one row per left-out athlete,
    one row per left-out athlete x beaten qualifier), both athlete-level: outputs/ only."""
    r = routes[routes["left_out"].astype(bool)]
    autos = routes[routes["route"] == "auto"]
    d = entrants(q)
    moc_of = {(x.gender, x.event_code, x.area, x.area_place): x for x in d[d["qualifier_type"] == "automatic"].itertuples()}
    lo_rows, pair_rows = [], []
    for x in r.itertuples():
        measure = EVENTS[x.event_code][0]
        a = autos[(autos["gender"] == x.gender) & (autos["event_code"] == x.event_code) & (autos["meet_area"] != x.meet_area)]
        worse = a[a["mark_value"] > x.mark_value + 1e-9] if measure == "time" else a[a["mark_value"] < x.mark_value - 1e-9]
        base = {"season": season, "gender": x.gender, "event_code": x.event_code, "area": x.meet_area,
                "area_place": x.place, "area_mark": x.mark_raw, "athlete_name": x.athlete_name,
                "school": x.school_name, "is_relay": bool(x.is_relay)}
        lo_rows.append({**base, "beaten_other_area_autos": len(worse),
                        **{f"beaten_{b}": int((worse["meet_area"] == b).sum()) for b in AREAS}})
        for w in worse.itertuples():
            m = moc_of.get((w.gender, w.event_code, w.meet_area, w.place))
            pair_rows.append({**base, "beaten_area": w.meet_area, "beaten_name": w.athlete_name,
                              "beaten_school": w.school_name, "beaten_area_place": w.place, "beaten_mark": w.mark_raw,
                              "beaten_competed": getattr(m, "competed", None),
                              "beaten_made_final": getattr(m, "made_final", None),
                              "beaten_moc_overall_place": getattr(m, "moc_overall_place", None)})
    return pd.DataFrame(lo_rows), pd.DataFrame(pair_rows)


def left_out_summary(lo: pd.DataFrame, pairs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Public, counts only.
    left_out_counts: per season x gender x event x left-out Area x beaten Area, the number of
      left-out athletes who beat at least one automatic qualifier from the beaten Area, and the
      number of distinct beaten qualifiers; plus per event the left-out total.
    left_out_beaten_moc: how the beaten automatic qualifiers did at the MOC, per season (and
      pooled) x left-out Area x beaten Area: entries, made the final, median MOC place; the
      MOC figures blank below MIN_CELL entries."""
    k = ["season", "gender", "event_code"]
    tot = lo.groupby(k + ["area"]).agg(left_out=("athlete_name", "size"),
                                      beat_any=("beaten_other_area_autos", lambda s: int((s > 0).sum()))).reset_index()
    tot["beaten_area"] = "any"
    if len(pairs):
        pairs = pairs.assign(ath=pairs["athlete_name"].astype(str) + "|" + pairs["school"].astype(str),
                             beaten=pairs["beaten_name"].astype(str) + "|" + pairs["beaten_school"].astype(str))
        pc = pairs.groupby(k + ["area", "beaten_area"]).agg(beat_any=("ath", "nunique"),
                                                             beaten_autos=("beaten", "nunique")).reset_index()
    else:
        pc = pd.DataFrame(columns=k + ["area", "beaten_area", "beat_any", "beaten_autos"])
    counts = pd.concat([tot, pc], ignore_index=True)[k + ["area", "beaten_area", "left_out", "beat_any", "beaten_autos"]]
    rows = []
    if len(pairs):
        b = pairs.drop_duplicates(k + ["area", "beaten_area", "beaten"])
        pooled = f"{int(b['season'].min())}-{int(b['season'].max())} pooled"
        for season, bs in [(str(int(s)), b[b["season"] == s]) for s in sorted(b["season"].unique())] + [(pooled, b)]:
            for area in (*AREAS, "all"):
                for beaten in (*AREAS, "all"):
                    x = bs[((bs["area"] == area) | (area == "all")) & ((bs["beaten_area"] == beaten) | (beaten == "all"))]
                    x = x.drop_duplicates(k + ["beaten"]) if "all" in (area, beaten) else x
                    comp = x[x["beaten_competed"] == 1]
                    n = len(comp)
                    ok = n >= MIN_CELL
                    placed = comp["beaten_moc_overall_place"].dropna()
                    rows.append({"season": season, "area": area, "beaten_area": beaten, "beaten_autos": len(x),
                                 "competed": n, "made_final": int(comp["beaten_made_final"].sum()) if ok else None,
                                 "median_moc_place": float(placed.median()) if ok and len(placed) else None})
    beaten = pd.DataFrame(rows)
    if len(beaten):
        beaten["made_final"] = beaten["made_final"].astype("Int64")
    return counts.sort_values(k + ["area", "beaten_area"]).reset_index(drop=True), beaten


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_season(season: int, results, entries, rules, kw, legs, moc_perf):
    ev = replay.evaluate(results, rules, BEST_READING)
    comp = replay.compare(ev, entries, rules, interp=BEST_READING, legs=legs, **kw)       # pre-declaration
    routes, pd_comp = replay.pass_down(ev, entries, rules, interp=BEST_READING, **kw)      # after declarations
    events = set(replay.main_events(rules))
    ent = entries[~entries["is_adaptive"].astype(bool) & entries["event_modifier"].isna()]
    ent = ent[[(g, e) in events for g, e in zip(ent["gender"], ent["event_code"])]]
    unresolved = ent[ent["school_name"].map(kw["school_area"]).isna()]
    moc_all = moc_perf[(moc_perf["season"] == season) & (moc_perf["level"] == "moc")]
    moc = moc_all[moc_all["in_scope"]]
    q = qualifiers(season, comp, routes, moc, unresolved, kw["school_key"], competed_events(moc_all, legs),
                   moc_overall_places(moc, kw["school_key"]))
    lo, pairs = left_out(season, routes, q)
    return q, lo, pairs, comp, pd_comp
