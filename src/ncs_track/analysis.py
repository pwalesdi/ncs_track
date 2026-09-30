"""Analysis tables behind the dashboard (docs/analysis_tables.md defines every column).

One season at a time, with the best 2026 reading of the rules (BEST_READING) and its
overlays. Everything is split by season, gender and event; main events only (no Unified,
4x800 or relay splits).

  outputs/qualifiers.csv                  athlete-level (names): git-ignored
  data/summary/field_makeup.csv           no names: tracked
  data/summary/at_large_share.csv
  data/summary/moc_performance.csv
  data/summary/spot_utilization.csv       + _by_area.csv roll-up, + _flags.csv
  data/summary/left_out.csv
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
MOC_FIELD = 24                                         # 6 + 6 + 6 + 3 automatic + 3 next best mark
GUARANTEED_TYPES = ("automatic", "next_best_mark")     # the fixed spots; at-large standard has no cap
SPOT_USE = ("competed", "refilled", "unfilled", "chose_another_event", "did_not_enter")   # spot_use segments
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
    """competed, moc_status, moc_final_place, top_finish, reached_final_round, scored."""
    if rows.empty:
        return {"competed": 0, "moc_status": "not_in_results", "moc_final_place": None, "top_finish": 0,
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
            "moc_final_place": place, "top_finish": int(place is not None and place <= top_cut(event)),
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


def qualifiers(season: int, comp: replay.Comparison, evaluated: pd.DataFrame, moc: pd.DataFrame,
               unresolved: pd.DataFrame, school_key, competed_in: dict | None = None,
               overall: dict | None = None) -> pd.DataFrame:
    """One row per athlete (or relay team) x event: the union of the qualified and declared fields."""
    competed_in = competed_in or {}
    overall = overall or {}
    ev = _with_identity(evaluated, "athlete_name_raw", "school_name_raw", school_key)
    area_rows = {}
    for r in ev.itertuples():
        area_rows.setdefault((r.gender, r.event_code, r.identity), r)
    moc = _with_identity(moc, "athlete_name_raw", "school_name_raw", school_key)
    moc_by_id = {k: g for k, g in moc[moc["athlete_id"].notna()].groupby(["gender", "event_code", "athlete_id"])}
    moc_by_ident = {k: g for k, g in moc.groupby(["gender", "event_code", "identity"])}

    out = []
    for r in comp.rows.itertuples():
        o = r.outcome
        qualified = o != "entered_not_predicted"
        declared = o != "predicted_not_entered"
        if qualified:
            qtype = TYPE_OF[r.qualified_by]
        else:
            qtype = "replacement" if str(r.explained_by).startswith("replacement") else "unexplained"
        area_row = area_rows.get((r.gender, r.event_code, r.identity))
        aid = r.athlete_id if isinstance(r.athlete_id, str) else (
            area_row.athlete_id if area_row is not None and isinstance(area_row.athlete_id, str) else None)
        rows = moc_by_id.get((r.gender, r.event_code, aid)) if isinstance(aid, str) else None
        if rows is None:
            rows = moc_by_ident.get((r.gender, r.event_code, r.identity), moc.iloc[0:0])
        outcome = (_moc_outcome(rows, r.event_code) if declared else
                   {"competed": 0, "moc_status": "not_declared", "moc_final_place": None, "top_finish": 0,
                    "reached_final_round": 0, "scored": 0})
        out.append({
            "season": season, "gender": r.gender, "event_code": r.event_code,
            "athlete_name": r.athlete_name if isinstance(r.athlete_name, str) else None,
            "is_relay": r.identity.startswith("relay|"), "athlete_id": aid,
            "area": r.area, "school": r.school_name,
            "qualifier_type": qtype, "at_large_combined": int(qtype in AT_LARGE_TYPES),
            "area_place": area_row.place if area_row is not None else None,
            "area_mark": area_row.mark_raw if area_row is not None else None,
            "in_qualified_field": int(qualified), "in_declared_field": int(declared),
            **outcome,
            "choice_tag": r.choice_tag, "replacement_for_area": r.fills_vacancy_of_area,
            "vacancy_refilled_by_area": r.vacancy_filled_by_area,
            # every qualifier who didn't compete in this event, whether or not they were in its program
            "competed_other_moc_event": (None if outcome["competed"] or r.identity.startswith("relay|")
                                         or not isinstance(aid, str)
                                         else int(bool(competed_in.get(aid, set()) - {r.event_code}))),
            "moc_overall_place": overall.get((r.gender, r.event_code,
                                              r.identity if r.identity.startswith("relay|") else aid)) if declared else None,
            "state_qualified": "pending",
        })
    for r in unresolved.itertuples():        # declared, but the school has no area this season
        ident = replay._identity(r.athlete_name, school_key(r.school_name), r.is_relay)
        rows = moc_by_ident.get((r.gender, r.event_code, ident), moc.iloc[0:0])
        out.append({"season": season, "gender": r.gender, "event_code": r.event_code,
                    "athlete_name": r.athlete_name if isinstance(r.athlete_name, str) else None,
                    "is_relay": bool(r.is_relay), "athlete_id": None, "area": "unknown", "school": r.school_name,
                    "qualifier_type": "unexplained", "at_large_combined": 0, "area_place": None, "area_mark": None,
                    "in_qualified_field": 0, "in_declared_field": 1, **_moc_outcome(rows, r.event_code),
                    "choice_tag": None, "replacement_for_area": None, "vacancy_refilled_by_area": None,
                    "competed_other_moc_event": None,
                    "moc_overall_place": overall.get((r.gender, r.event_code, ident)) if r.is_relay else None,
                    "state_qualified": "pending"})
    return pd.DataFrame(out)


# ---------------------------------------------------------------------------
# Summary tables (no names)
# ---------------------------------------------------------------------------
def _fields(q: pd.DataFrame):
    yield "qualified", q[q["in_qualified_field"] == 1]
    yield "declared", q[q["in_declared_field"] == 1]


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
    c = q[(q["in_declared_field"] == 1) & (q["competed"] == 1)]
    parts = [c.assign(rollup=False), c[c["at_large_combined"] == 1].assign(qualifier_type="at_large_combined", rollup=True)]
    c = pd.concat(parts)
    g = c.groupby(KEY + ["area", "qualifier_type", "rollup"]).agg(
        competed=("competed", "size"), top_finish=("top_finish", "sum"), scored=("scored", "sum"),
        reached_final_round=("reached_final_round", "sum")).reset_index()
    for k in ("top_finish", "scored", "reached_final_round"):
        g[f"{k}_rate"] = (g[k] / g["competed"]).round(4)
    return g.sort_values(KEY + ["area", "qualifier_type"]).reset_index(drop=True)


def spot_utilization(q: pd.DataFrame) -> pd.DataFrame:
    earned = q[q["in_qualified_field"] == 1]
    rows = []
    for (s, g, e, a), x in earned.groupby(KEY + ["area"]):
        decl = x[x["in_declared_field"] == 1]
        nd = x[x["in_declared_field"] == 0]
        refilled = nd["vacancy_refilled_by_area"].dropna()
        into = q[(q["season"] == s) & (q["gender"] == g) & (q["event_code"] == e) & (q["area"] == a)
                 & (q["qualifier_type"] == "replacement")]
        rows.append({"season": s, "gender": g, "event_code": e, "area": a,
                     "spots_earned": len(x), "declared": len(decl), "competed": int(decl["competed"].sum()),
                     "no_show": int((decl["competed"] == 0).sum()), "not_declared": len(nd),
                     "not_declared_chose_other_events": int((nd["choice_tag"] == "chose_other_events").sum()),
                     "not_declared_did_not_declare": int((nd["choice_tag"] == "did_not_declare").sum()),
                     "vacancies_refilled": len(refilled),
                     "guaranteed_spots": int(x["qualifier_type"].isin(GUARANTEED_TYPES).sum()),
                     "unfilled_spots": int(x.get("unfilled_spot", pd.Series(False, index=x.index)).fillna(False).astype(bool).sum()),
                     "not_declared_individual": int(nd["competed_other_moc_event"].notna().sum()),
                     "not_declared_competed_other_event": int((nd["competed_other_moc_event"] == 1).sum()),
                     "refilled_by_area": "|".join(f"{k}:{v}" for k, v in refilled.value_counts().sort_index().items()),
                     "replacements_from_this_area": len(into),
                     **_segments(x)})
    t = pd.DataFrame(rows)
    return _derived(t)


def _segments(x: pd.DataFrame) -> dict:
    """Spot-use segment counts: guaranteed spots (g_*) and at-large standard spots (al_*)."""
    use = x["spot_use"] if "spot_use" in x else pd.Series(index=x.index, dtype=object)
    g = use[x["qualifier_type"].isin(GUARANTEED_TYPES)].value_counts()
    al = use[x["qualifier_type"] == "at_large_standard"].value_counts()
    return {**{f"g_{k}": int(g.get(k, 0)) for k in SPOT_USE},
            **{f"al_{k}": int(al.get(k, 0)) for k in SPOT_USE if k != "unfilled"},
            "at_large_spots": int((x["qualifier_type"] == "at_large_standard").sum())}


def _derived(t: pd.DataFrame) -> pd.DataFrame:
    t = t.copy()
    t["unused_total"] = t["spots_earned"] - t["competed"]
    t["utilization_rate"] = (t["competed"] / t["spots_earned"]).round(4)
    t["unused_not_refilled"] = (t["unused_total"] - t["vacancies_refilled"]).clip(lower=0)
    t["other_unused"] = (t["unused_total"] - t["vacancies_refilled"] - t["unfilled_spots"]).clip(lower=0)
    t["unfilled_rate"] = (t["unfilled_spots"] / t["guaranteed_spots"]).where(t["guaranteed_spots"] > 0).round(4)
    t["guaranteed_used"] = t["g_competed"] + t["g_refilled"]
    t["guaranteed_used_rate"] = (t["guaranteed_used"] / t["guaranteed_spots"]).where(t["guaranteed_spots"] > 0).round(4)
    t["no_show_rate"] = (t["no_show"] / t["declared"]).where(t["declared"] > 0).round(4)
    t["double_qualifier_share"] = (t["not_declared_competed_other_event"] / t["not_declared_individual"]).where(
        t["not_declared_individual"] > 0).round(4)
    return t


ADDITIVE = ["spots_earned", "declared", "competed", "no_show", "not_declared", "not_declared_chose_other_events",
            "not_declared_did_not_declare", "vacancies_refilled", "guaranteed_spots", "unfilled_spots",
            "not_declared_individual", "not_declared_competed_other_event", "replacements_from_this_area",
            *[f"g_{k}" for k in SPOT_USE], *[f"al_{k}" for k in SPOT_USE if k != "unfilled"], "at_large_spots"]


def spot_utilization_by_area(t: pd.DataFrame) -> pd.DataFrame:
    """Roll-up per season x area. unused_not_refilled and other_unused are summed from the
    event rows (each floored at 0 per event), not recomputed from the totals."""
    keep = ["unused_not_refilled", "other_unused"]
    r = t.groupby(["season", "area"])[ADDITIVE + keep].sum().reset_index()
    saved = r[keep].copy()
    r = _derived(r.drop(columns=keep))
    r[keep] = saved
    return r


def no_shows_unfilled(t: pd.DataFrame) -> pd.DataFrame:
    """Per Area x season: the counts behind no-show and unfilled-spot rates."""
    r = spot_utilization_by_area(t)
    return r[["season", "area", "spots_earned", "guaranteed_spots", "declared", "no_show", "no_show_rate",
              "not_declared", "vacancies_refilled", "unfilled_spots", "unfilled_rate", "unused_not_refilled"]]


def spot_utilization_flags(t: pd.DataFrame, min_seasons: int = 3, metric: str = "unused_total") -> pd.DataFrame:
    """Area x gender x event with `metric` > 0 in at least `min_seasons` seasons."""
    u = t[t[metric] > 0].groupby(["area", "gender", "event_code"]).agg(
        seasons_flagged=("season", "nunique"), seasons=("season", lambda s: "|".join(map(str, sorted(s)))),
        total_all_seasons=(metric, "sum")).reset_index()
    n = t.groupby(["area", "gender", "event_code"])["season"].nunique().rename("seasons_analysed").reset_index()
    u = u.merge(n, on=["area", "gender", "event_code"]).assign(metric=metric)
    return u[u["seasons_flagged"] >= min_seasons].sort_values(
        ["seasons_flagged", "total_all_seasons"], ascending=False).reset_index(drop=True)


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
    c = q[(q["in_declared_field"] == 1) & (q["competed"] == 1)].copy()
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
                                 "competed": len(x), "top_finish": int(x["top_finish"].sum()) if ok else None,
                                 "top_finish_rate": round(x["top_finish"].mean(), 4) if ok else None,
                                 "with_moc_place": len(placed),
                                 "median_moc_place": float(placed.median()) if ok and len(placed) else None})
    return pd.DataFrame(rows)


def _core_rows(q: pd.DataFrame) -> pd.DataFrame:
    """Athletes in either comparison group, with a fixed 'lowest automatic' flag."""
    c = q[(q["in_declared_field"] == 1) & (q["competed"] == 1) & (q["area"].isin(AREAS))].copy()
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


def core_place_curve(q: pd.DataFrame) -> pd.DataFrame:
    """Where Area finishers end up at the MOC, aggregated for the public repo.

    Rows: season (each, plus "2022-2026 pooled") x gender (girls, boys, all) x event_group
    (six groups, plus all) x area x area_place ("1".."12", plus the bands "5-6" and "7-8").
    Entries = athlete-events who competed at the MOC (one athlete in two events counts twice).
    top8_count and median_moc_place are blank when entries < MIN_CELL, so no row reveals a
    single athlete's MOC place."""
    c = q[(q["in_declared_field"] == 1) & (q["competed"] == 1) & q["area"].isin(AREAS)
          & q["area_place"].between(1, 12)].copy()
    c["event_group"] = c["event_code"].astype(str).map(GROUP_OF)
    c["area_place"] = c["area_place"].astype(int)
    pooled = f"{int(c['season'].min())}-{int(c['season'].max())} pooled"
    seasons = [(str(int(s)), c[c["season"] == s]) for s in sorted(c["season"].unique())] + [(pooled, c)]
    places = [(str(p), (p,)) for p in range(1, 13)] + list(PLACE_BANDS.items())
    rows = []
    for season, cs in seasons:
        for gender in ("girls", "boys", "all"):
            cg = cs if gender == "all" else cs[cs["gender"] == gender]
            for group in (*EVENT_GROUPS, "all"):
                ce = cg if group == "all" else cg[cg["event_group"] == group]
                for area in AREAS:
                    ca = ce[ce["area"] == area]
                    for label, pl in places:
                        x = ca[ca["area_place"].isin(pl)]
                        n = len(x)
                        ok = n >= MIN_CELL
                        placed = x["moc_overall_place"].dropna()
                        rows.append({"season": season, "gender": gender, "event_group": group, "area": area,
                                     "area_place": label, "entries": n,
                                     "top8_count": int(x["top_finish"].sum()) if ok else None,
                                     "median_moc_place": float(placed.median()) if ok and len(placed) else None})
    out = pd.DataFrame(rows)
    out["top8_count"] = out["top8_count"].astype("Int64")
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
    y = c["top_finish"].to_numpy(float)
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
        b, p_cl = _clustered_p(sub["top_finish"], sub["lowest_auto"] & (sub["area"] == a), sub["cluster"])
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


LEFT_OUT_CAVEAT = ("Area mark and MOC marks come from different meets (different day, wind, weather, "
                   "competition and, for field events, attempts); a comparison, not a prediction.")


def moc_cutoffs(moc: pd.DataFrame) -> pd.DataFrame:
    """The 8th-best (9th for LJ/TJ/SP/DT) valid MOC mark per season x gender x event,
    across all rounds combined (prelims + finals). Each athlete or relay team counts once,
    at their best valid mark, so one slow final can't set the cutoff."""
    ok = moc[(moc["status"] == "OK") & moc["mark_value"].notna()].copy()
    ok["key"] = [a if isinstance(a, str) and not r else f"{s}|{n}" for a, r, s, n in
                 zip(ok["athlete_id"], ok["is_relay"], ok["school_name_raw"], ok["athlete_name_raw"])]
    rows = []
    for (s, g, e), x in ok.groupby(KEY):
        n = top_cut(e)
        measure = EVENTS[e][0]
        best = (x.assign(k=x["mark_value"] if measure == "time" else -x["mark_value"])
                .sort_values("k").drop_duplicates("key"))
        hit = best.iloc[n - 1] if len(best) >= n else None
        rows.append({"season": s, "gender": g, "event_code": e, "moc_cutoff_place": n,
                     "moc_cutoff_mark": hit["mark_raw"] if hit is not None else None,
                     "moc_cutoff_value": hit["mark_value"] if hit is not None else None,
                     "moc_cutoff_source": None if hit is None else "best_mark_all_rounds"})
    return pd.DataFrame(rows)


def left_out(season: int, evaluated: pd.DataFrame, q: pd.DataFrame, cutoffs: pd.DataFrame,
             school_key, n: int = 3) -> pd.DataFrame:
    ev = _with_identity(evaluated, "athlete_name_raw", "school_name_raw", school_key)
    ev = ev[ev["qualified_by"].isna() & (ev["status"] == "OK") & ev["mark_value"].notna()]
    declared = q[(q["season"] == season) & (q["in_declared_field"] == 1)]
    decl_ids = set(zip(declared["gender"], declared["event_code"], declared["athlete_id"].astype(str)))
    rows = []
    for (g, e, a), x in ev.groupby(["gender", "event_code", "meet_area"]):
        measure = EVENTS[e][0]
        x = x.assign(k=(x["mark_value"] if measure == "time" else -x["mark_value"])).sort_values(["k", "place"]).head(n)
        cut = cutoffs[(cutoffs["season"] == season) & (cutoffs["gender"] == g) & (cutoffs["event_code"] == e)]
        cv = cut["moc_cutoff_value"].iloc[0] if len(cut) else None
        for rank, r in enumerate(x.itertuples(), start=1):
            better = None if cv is None or pd.isna(cv) else bool(
                r.mark_value <= cv + 1e-9 if measure == "time" else r.mark_value >= cv - 1e-9)
            rows.append({"season": season, "gender": g, "event_code": e, "area": a,
                         "rank_among_non_qualifiers": rank, "area_place": r.place, "area_mark": r.mark_raw,
                         "area_mark_value": r.mark_value, "is_relay": bool(r.is_relay),
                         "declared_anyway": (g, e, str(r.athlete_id)) in decl_ids if not r.is_relay else None,
                         "moc_cutoff_place": cut["moc_cutoff_place"].iloc[0] if len(cut) else None,
                         "moc_cutoff_mark": cut["moc_cutoff_mark"].iloc[0] if len(cut) else None,
                         "moc_cutoff_source": cut["moc_cutoff_source"].iloc[0] if len(cut) else None,
                         "area_mark_would_have_been_top_finish": better, "caveat": LEFT_OUT_CAVEAT})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def moc_fields(moc: pd.DataFrame) -> dict:
    """(gender, event) -> athletes/teams who competed in the event at the MOC: the largest
    competed count over its rounds (the first round, except where the results carry a stray
    small 'Prelims' block, e.g. a high-jump jump-off; decision #25)."""
    out = {}
    for (g, e), x in moc.groupby(["gender", "event_code"]):
        c = x[~x["status"].isin(NOT_COMPETED)].groupby("round").size()
        out[(g, str(e))] = int(c.max()) if len(c) else 0
    return out


def spot_use(r) -> str | None:
    """One segment per qualified spot, in this order of precedence: competed in the event;
    refilled (same-Area replacement); unfilled (guaranteed spot, field below 24); chose
    another event (competed at the MOC in other events only); didn't enter (competed in no
    MOC event: not in the program, or in it but didn't start). Relays can't choose another
    event. Individuals without an Athletic.net ID fall back to the program-based choice tag."""
    if r["in_qualified_field"] != 1:
        return None
    if r["competed"] == 1:
        return "competed"
    if isinstance(r["vacancy_refilled_by_area"], str):
        return "refilled"
    if r["unfilled_spot"]:
        return "unfilled"
    other = r["competed_other_moc_event"]
    if pd.isna(other):
        other = (not r["is_relay"]) and r["choice_tag"] == "chose_other_events"
    return "chose_another_event" if other else "did_not_enter"


def mark_unfilled(q: pd.DataFrame, moc: pd.DataFrame) -> pd.DataFrame:
    """unfilled_spot: a guaranteed spot (automatic or next best mark) whose qualifier didn't
    compete, whose spot wasn't refilled, in an event whose MOC field ended below 24."""
    fields = moc_fields(moc)
    q = q.copy()
    q["moc_field"] = [fields.get((g, str(e))) for g, e in zip(q["gender"], q["event_code"])]
    q["unfilled_spot"] = ((q["in_qualified_field"] == 1) & q["qualifier_type"].isin(GUARANTEED_TYPES)
                          & (q["competed"] == 0) & q["vacancy_refilled_by_area"].isna()
                          & (q["moc_field"].fillna(MOC_FIELD) < MOC_FIELD))
    q["spot_use"] = q.apply(spot_use, axis=1)
    return q


def build_season(season: int, results, entries, rules, kw, legs, moc_perf):
    ev = replay.evaluate(results, rules, BEST_READING)
    comp = replay.compare(ev, entries, rules, interp=BEST_READING, legs=legs, **kw)
    events = set(replay.main_events(rules))
    ent = entries[~entries["is_adaptive"].astype(bool) & entries["event_modifier"].isna()]
    ent = ent[[(g, e) in events for g, e in zip(ent["gender"], ent["event_code"])]]
    unresolved = ent[ent["school_name"].map(kw["school_area"]).isna()]
    moc_all = moc_perf[(moc_perf["season"] == season) & (moc_perf["level"] == "moc")]
    moc = moc_all[moc_all["in_scope"]]
    q = qualifiers(season, comp, ev, moc, unresolved, kw["school_key"], competed_events(moc_all, legs),
                   moc_overall_places(moc, kw["school_key"]))
    q = mark_unfilled(q, moc)
    cut = moc_cutoffs(moc)
    lo = left_out(season, ev, q, cut, kw["school_key"])
    return q, lo, comp
