"""Alternative MOC allocations, simulated on each season's real declarations (decision #35).

Every scenario keeps the pass-down rule (replay.assign_routes) and changes only the number
of automatic spots per Area (configs/allocation/*.yaml: auto_spots) and next-best-mark spots
(fill.count); the base field stays 24 and the at-large standard is applied on top as printed.

Declines. An athlete who declined in reality (the `declined` column of the real pass-down),
or who was walked past while a spot stayed unused, declines again. Everyone else is
assumed to accept any spot they are offered: real entrants, and finishers who were never
offered a spot in reality.

Per athlete (Area finalist with a valid mark and place) and scenario:
  in_field / route    the scenario's route (automatic / next_best_mark / at_large_standard)
  real_in             in the real field on a pass-down route (validated; decision #32)
  added / removed     in the scenario but not in reality, and the reverse
  left_out            behind the Area's last automatic qualifier in the scenario, no route,
                      no real decline (the validated Left out definition), not a real entrant
                      with no route
  beaten              automatic qualifiers from other Areas (scenario) with a worse Area mark
  top24               one of the 24 best Area-final marks in the event among athletes who
                      didn't decline (merit capture)
  above_cutoff        Area mark at or better than the season's MOC final cutoff (8th / 9th best
                      MOC mark across rounds): an estimate, the marks come from different meets
Program entrants the pass-down couldn't place (unexplained, unlinked schools) are outside
every scenario: never added, removed or left out.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import allocate, paths, replay
from .analysis import AREAS, EVENT_GROUPS, GROUP_OF, KEY, MIN_CELL, top_cut
from .events import EVENTS

SCENARIOS = ("current", "a_5553", "b_4443", "c_3333")
LABEL = {"current": "Current (6-6-6-3)", "a_5553": "5-5-5-3", "b_4443": "4-4-4-3", "c_3333": "3-3-3-3"}
ROUTE_NAME = {"auto": "automatic", "fill": "next_best_mark", "at_large": "at_large_standard"}
CONFIGS = paths.ROOT / "configs" / "allocation"
EPS = replay.EPS


def load(name: str) -> allocate.AllocationConfig:
    return allocate.load_config(CONFIGS / f"{name}.yaml")


def moc_cutoffs(moc: pd.DataFrame) -> pd.DataFrame:
    """The 8th-best (9th for LJ/TJ/SP/DT) valid MOC mark per season x gender x event, across
    all rounds combined; each athlete or relay team counts once, at their best valid mark."""
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
        rows.append({"season": s, "gender": g, "event_code": e,
                     "moc_cutoff_value": hit["mark_value"] if hit is not None else None})
    return pd.DataFrame(rows)


def _better(a, b, measure) -> bool:
    """Mark a strictly better than mark b."""
    return a < b - EPS if measure == "time" else a > b + EPS


def simulate(routes: pd.DataFrame, cfg: allocate.AllocationConfig) -> pd.DataFrame:
    """One season's Area finalists under `cfg`, from the real pass-down `routes`."""
    r = routes[routes["meet_area"].notna()].copy()
    r["real_decliner"] = r["declined"].notna() | r["passed_unused"].fillna(False).astype(bool)
    r["real_declined"] = r["declined"]
    r["real_unplaced"] = r["declared"].astype(bool) & r["route"].isna()        # real entrant, no route
    r["real_in"] = r["declared"].astype(bool) & r["route"].notna()
    r["real_route"] = r["route"].map(ROUTE_NAME)
    out = []
    for (g, e), x in r.groupby(["gender", "event_code"]):
        measure = EVENTS[e][0]
        ok = (x["status"] == "OK") & x["mark_value"].notna()
        # the fill pool is every valid mark from the pool's Areas; the walk only offers it to
        # finishers behind their Area's last automatic qualifier (evaluate's flag assumes 6/6/6/3)
        x = x.assign(declared=x["declared"].astype(bool) | ~x["real_decliner"],
                     fill_candidate=ok & x["meet_area"].isin(cfg.fill_pool),
                     meets_standard=x["meets_standard"].fillna(False).astype(bool))
        if cfg.at_large_mode == "off":
            x["meets_standard"] = False
        s = replay.assign_routes(x.drop(columns=["route", "declined", "left_out", "remaining", "passed_unused"]),
                                 cfg.auto_spots, cfg.fill_count, measure, cfg.fill_ties == "include",
                                 cfg.wind_aided_allowed)
        s["route"] = s["route"].map(ROUTE_NAME)
        s["in_field"] = s["route"].notna() | s["real_unplaced"]
        # as the validated Left out: finishers walked past an unused spot count, real decliners don't
        s["left_out"] = (s["remaining"] & s["route"].isna() & s["declined"].isna() & s["real_declined"].isna()
                         & ~s["real_unplaced"])
        # beaten: other Areas' automatic qualifiers in this scenario with a worse Area mark
        autos = s[s["route"] == "automatic"]
        nbm = s[s["route"] == "next_best_mark"]
        beaten, beaten_areas, beats_nbm = [], [], []
        for i, row in s.iterrows():
            if not row["left_out"]:
                beaten.append(0), beaten_areas.append(""), beats_nbm.append(False)
                continue
            w = autos[(autos["meet_area"] != row["meet_area"])
                      & autos["mark_value"].map(lambda v: _better(row["mark_value"], v, measure))]
            beaten.append(len(w))
            beaten_areas.append("|".join(sorted(w["meet_area"].unique())))
            beats_nbm.append(bool(nbm["mark_value"].map(lambda v: _better(row["mark_value"], v, measure)).any()))
        s["beaten_other_area_autos"] = beaten
        s["beaten_areas"] = beaten_areas
        s["beats_a_next_best_mark"] = beats_nbm
        for a in AREAS:
            s[f"beaten_{a}"] = [0 if not lo else int(((autos["meet_area"] == a) & (autos["meet_area"] != ma)
                                                      & autos["mark_value"].map(lambda v: _better(mv, v, measure))).sum())
                                for lo, ma, mv in zip(s["left_out"], s["meet_area"], s["mark_value"])]
        # merit: the 24 best marks among finishers who didn't decline
        ok = s[(s["status"] == "OK") & s["mark_value"].notna() & s["place"].notna() & ~s["real_decliner"]]
        order = ok["mark_value"].map(lambda v: replay.sort_key(v, measure)).sort_values(kind="stable")
        s["top24"] = s.index.isin(order.index[:24])
        out.append(s)
    res = pd.concat(out, ignore_index=True)
    res["scenario"] = cfg.name
    res["added"] = res["in_field"] & ~res["real_in"] & ~res["real_unplaced"]
    res["removed"] = res["real_in"] & ~res["in_field"]
    return res


COLUMNS = ["scenario", "season", "gender", "event_code", "area", "place", "mark_raw", "mark_value", "athlete_name",
           "school_name", "is_relay", "real_route", "real_in", "real_unplaced", "real_decliner", "route", "in_field",
           "added", "removed", "left_out", "beaten_other_area_autos", "beaten_areas", "beats_a_next_best_mark",
           *[f"beaten_{a}" for a in AREAS], "top24", "real_made_final", "above_cutoff"]


def run(routes: pd.DataFrame, qualifiers: pd.DataFrame, cutoffs: pd.DataFrame,
        scenarios=SCENARIOS) -> pd.DataFrame:
    """Athlete-level results for every scenario and season (outputs/ only: names)."""
    q = qualifiers[qualifiers["in_declared_field"] == 1][["season", "gender", "event_code", "athlete_name", "school",
                                                         "area_place", "made_final"]].copy()
    q["event_code"] = q["event_code"].astype(str)
    q = q.rename(columns={"school": "school_name", "area_place": "place", "made_final": "real_made_final"})
    q["athlete_name"] = q["athlete_name"].fillna("")
    parts = []
    for name in scenarios:
        cfg = load(name)
        for season, rs in routes.groupby("season"):
            s = simulate(rs, cfg)
            s["season"] = season
            parts.append(s)
    res = pd.concat(parts, ignore_index=True)
    res["event_code"] = res["event_code"].astype(str)
    res["area"] = res["meet_area"]
    res["athlete_name"] = res["athlete_name"].fillna("")
    res = res.merge(q.drop_duplicates(["season", "gender", "event_code", "athlete_name", "school_name", "place"]),
                    how="left", on=["season", "gender", "event_code", "athlete_name", "school_name", "place"])
    res = res.merge(cutoffs, how="left", on=["season", "gender", "event_code"])
    res["above_cutoff"] = [pd.notna(c) and not _better(c, v, EVENTS[e][0]) for c, v, e in
                           zip(res["moc_cutoff_value"], res["mark_value"], res["event_code"])]
    return res[COLUMNS]


# ---------------------------------------------------------------------------
# Public tables: counts only; MOC-place figures (removed who made the final) below MIN_CELL blank
# ---------------------------------------------------------------------------
def _levels(res: pd.DataFrame):
    """(season label, gender, event label, frame) for every roll-up level."""
    pooled = f"{int(res['season'].min())}-{int(res['season'].max())} pooled"
    res = res.assign(group=res["event_code"].map(GROUP_OF))
    for season, xs in [(str(int(s)), res[res["season"] == s]) for s in sorted(res["season"].unique())] + [(pooled, res)]:
        for gender in ("girls", "boys", "all"):
            xg = xs if gender == "all" else xs[xs["gender"] == gender]
            for ev, xe in ([(e, xg[xg["event_code"] == e]) for e in sorted(xg["event_code"].unique())]
                           + [(f"group:{g}", xg[xg["group"] == g]) for g in EVENT_GROUPS] + [("all", xg)]):
                yield season, gender, ev, xe


def tables(res: pd.DataFrame) -> dict[str, pd.DataFrame]:
    makeup, changes, left, merit = [], [], [], []
    for scen, rs in res.groupby("scenario", sort=False):
        for season, gender, ev, x in _levels(rs):
            key = {"scenario": scen, "season": season, "gender": gender, "event": ev}
            f = x[x["route"].notna()]
            size = len(f)
            for a in AREAS:
                fa, xa = f[f["area"] == a], x[x["area"] == a]
                for rt in ("automatic", "next_best_mark", "at_large_standard"):
                    n = int((fa["route"] == rt).sum())
                    makeup.append({**key, "area": a, "route": rt, "count": n, "field_size": size,
                                   "share_of_field": round(n / size, 4) if size else None})
                rem = xa[xa["removed"]]
                ok = len(rem) >= MIN_CELL or len(rem) == 0
                changes.append({**key, "area": a, "added": int(xa["added"].sum()), "removed": len(rem),
                                "removed_made_final": int(rem["real_made_final"].fillna(0).sum()) if ok else None,
                                "added_above_cutoff": int((xa["added"] & xa["above_cutoff"]).sum())})
                lo = xa[xa["left_out"]]
                row = {**key, "area": a, "left_out": len(lo),
                       "beat_any": int((lo["beaten_other_area_autos"] > 0).sum()),
                       "beat_any_excl_class_a": int((lo[[f"beaten_{b}" for b in AREAS if b != "class-a"]].sum(axis=1) > 0).sum()),
                       "beats_a_next_best_mark": int(lo["beats_a_next_best_mark"].sum())}
                for b in AREAS:
                    row[f"beat_{b}"] = int((lo[f"beaten_{b}"] > 0).sum())
                left.append(row)
            merit.append({**key, "top_marks": int(x["top24"].sum()),
                          "captured": int((x["top24"] & x["route"].notna()).sum())})
    out = {"scenario_field_makeup": pd.DataFrame(makeup), "scenario_changes": pd.DataFrame(changes),
           "scenario_left_out": pd.DataFrame(left), "scenario_merit": pd.DataFrame(merit)}
    out["scenario_changes"]["removed_made_final"] = out["scenario_changes"]["removed_made_final"].astype("Int64")
    return out


def build(season_list=None) -> dict[str, pd.DataFrame]:
    routes = pd.read_csv(paths.OUTPUTS / "routes.csv", low_memory=False, dtype={"event_code": str, "athlete_id": str})
    q = pd.read_csv(paths.OUTPUTS / "qualifiers.csv", low_memory=False, dtype={"event_code": str})
    if season_list:
        routes, q = routes[routes["season"].isin(season_list)], q[q["season"].isin(season_list)]
    perf = pd.read_csv(paths.PROCESSED / "performances.csv", low_memory=False, dtype={"athlete_id": str})
    moc = perf[(perf["level"] == "moc") & perf["in_scope"].fillna(False).astype(bool)].copy()
    moc["event_code"] = moc["event_code"].astype(str)
    res = run(routes, q, moc_cutoffs(moc))
    res.to_csv(paths.OUTPUTS / "scenario_athletes.csv", index=False)
    res[res["removed"] & (res["real_made_final"] == 1)].sort_values(["scenario", "season", "area"]).to_csv(
        paths.OUTPUTS / "scenario_removed_finalists.csv", index=False)
    res[res["left_out"] & (res["beaten_other_area_autos"] > 0)].to_csv(
        paths.OUTPUTS / "scenario_left_out.csv", index=False)
    t = tables(res)
    for name, df in t.items():
        df.to_csv(paths.SUMMARY / f"{name}.csv", index=False)
    return t
