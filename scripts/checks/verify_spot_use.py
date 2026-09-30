"""Verification: spot use (read-only). Writes to outputs/verify/ (git-ignored; real names).

    .venv/bin/python scripts/checks/verify_spot_use.py

B1  One Area, season and event(s), qualifier by qualifier: Area place, route, and what
    happened at the MOC (competed / refilled by whom / chose another event (which) /
    didn't enter / unfilled), next to the bucket the dashboard used before this round.
B2  Refill and unfilled chains across all seasons: who vacated, who moved in, final field.
B3  Consistency checks: unfilled count vs. how far the field actually fell short of 24;
    refills whose replacement didn't compete.
"""

import argparse

import pandas as pd

from ncs_track import paths
from ncs_track.analysis import GUARANTEED_TYPES, MOC_FIELD, NOT_COMPETED, competed_events

OUT = paths.OUTPUTS / "verify"
ROUTE = {"automatic": "automatic", "next_best_mark": "next best mark", "at_large_standard": "at-large standard"}


def load():
    q = pd.read_csv(paths.OUTPUTS / "qualifiers.csv", low_memory=False, dtype={"athlete_id": str})
    q["event_code"] = q["event_code"].astype(str)
    perf = pd.read_csv(paths.PROCESSED / "performances.csv", low_memory=False, dtype={"athlete_id": str})
    perf["event_code"] = perf["event_code"].astype(str)
    legs = pd.read_csv(paths.PROCESSED / "relay_legs.csv", dtype={"athlete_id": str})
    comp = {s: competed_events(perf[(perf["season"] == s) & (perf["level"] == "moc")], legs)
            for s in sorted(q["season"].unique())}
    return q, perf, comp


def old_bucket(r) -> str:
    """The pre-round dashboard donut: all spots (at-large included)."""
    if r.competed == 1:
        return "competed"
    if isinstance(r.vacancy_refilled_by_area, str):
        return "refilled"
    return "unfilled" if r.unfilled_spot is True else "other unused"


def elsewhere(r, comp) -> list[str]:
    if r.is_relay or not isinstance(r.athlete_id, str):
        return []
    return sorted(comp[r.season].get(r.athlete_id, set()) - {r.event_code})


def new_bucket(r, comp) -> str:
    if r.competed == 1:
        return "competed"
    if isinstance(r.vacancy_refilled_by_area, str):
        return "refilled"
    if r.unfilled_spot is True:
        return "unfilled"
    return "chose another event" if elsewhere(r, comp) else "didn't enter"


def pairs(q, season, gender, event, area):
    """Same-Area pairing, as replay._pair_same_area: vacancies and replacements by place."""
    x = q[(q["season"] == season) & (q["gender"] == gender) & (q["event_code"] == event) & (q["area"] == area)]
    vac = x[x["vacancy_refilled_by_area"].notna()].sort_values("area_place")
    sub = x[x["qualifier_type"] == "replacement"].sort_values("area_place")
    return list(zip(vac.itertuples(), sub.itertuples()))


def who(r) -> str:
    return f"{r.athlete_name or r.school} ({r.school}, {r.area} place {r.area_place:g})"


def event_detail(q, comp, season, gender, event, area) -> pd.DataFrame:
    x = q[(q["season"] == season) & (q["gender"] == gender) & (q["event_code"] == event) & (q["area"] == area)]
    pair_of = {v.Index: s for v, s in pairs(q, season, gender, event, area)}
    rows = []
    for r in x.sort_values("area_place").itertuples():
        if r.qualifier_type == "replacement":
            what = f"replacement: competed={r.competed}, MOC place {r.moc_final_place}"
        elif r.competed == 1:
            what = f"competed in this event (MOC status {r.moc_status}, final place {r.moc_final_place})"
        elif isinstance(r.vacancy_refilled_by_area, str):
            s = pair_of.get(r.Index)
            what = f"refilled by {who(s) if s is not None else '?'}"
        else:
            ev = elsewhere(r, comp)
            what = ("chose another event: competed in " + ", ".join(ev) if ev
                    else "didn't enter (competed in no MOC event)")
            if r.in_declared_field == 1:
                what += "; was in the program for this event but did not start"
            if r.unfilled_spot is True:
                what += "; spot counted UNFILLED (field below 24)"
        rows.append({"season": season, "gender": gender, "event": event, "area": area,
                     "athlete": r.athlete_name, "school": r.school, "area_place": r.area_place,
                     "area_mark": r.area_mark, "route": ROUTE.get(r.qualifier_type, r.qualifier_type),
                     "guaranteed": r.qualifier_type in GUARANTEED_TYPES, "choice_tag": r.choice_tag,
                     "what_happened": what, "old_dashboard_bucket": old_bucket(r) if r.qualifier_type != "replacement" else "",
                     "new_bucket": new_bucket(r, comp) if r.qualifier_type != "replacement" else "",
                     "moc_field": r.moc_field})
    return pd.DataFrame(rows)


def field(perf, season, gender, event):
    m = perf[(perf["season"] == season) & (perf["level"] == "moc") & perf["in_scope"]
             & (perf["gender"] == gender) & (perf["event_code"] == event)]
    first = m[m["round"] == ("prelim" if (m["round"] == "prelim").any() else "final")]
    return int((~first["status"].isin(NOT_COMPETED)).sum())


def chains(q, comp):
    refills, unfilled = [], []
    for (s, g, e, a), x in q[q["vacancy_refilled_by_area"].notna()].groupby(["season", "gender", "event_code", "area"]):
        for v, sub in pairs(q, s, g, e, a):
            refills.append({"season": s, "gender": g, "event": e, "area": a, "vacated_by": who(v),
                            "vacated_route": ROUTE.get(v.qualifier_type), "vacater_competed_elsewhere": ", ".join(elsewhere(v, comp)),
                            "moved_in": who(sub), "replacement_competed": sub.competed,
                            "replacement_moc_place": sub.moc_final_place, "final_field": v.moc_field})
    for r in q[q["unfilled_spot"] == True].itertuples():  # noqa: E712
        ev = q[(q["season"] == r.season) & (q["gender"] == r.gender) & (q["event_code"] == r.event_code)]
        unfilled.append({"season": r.season, "gender": r.gender, "event": r.event_code, "area": r.area,
                         "vacated_by": who(r), "route": ROUTE.get(r.qualifier_type),
                         "vacater_competed_elsewhere": ", ".join(elsewhere(r, comp)),
                         "in_program_for_event": r.in_declared_field, "moved_in": "nobody",
                         "final_field": r.moc_field,
                         "event_unfilled_total": int((ev["unfilled_spot"] == True).sum()),  # noqa: E712
                         "event_at_large_competed": int(((ev["qualifier_type"] == "at_large_standard") & (ev["competed"] == 1)).sum())})
    return pd.DataFrame(refills), pd.DataFrame(unfilled)


def field_any_round(perf, season, gender, event):
    """Largest competed count over the event's rounds (a stray 'Prelims' block can't shrink it)."""
    m = perf[(perf["season"] == season) & (perf["level"] == "moc") & perf["in_scope"]
             & (perf["gender"] == gender) & (perf["event_code"] == event)]
    m = m[~m["status"].isin(NOT_COMPETED)]
    return int(m.groupby("round").size().max()) if len(m) else 0


def consistency(q, perf):
    unused = ((q["qualifier_type"].isin(GUARANTEED_TYPES)) & (q["competed"] == 0) & q["vacancy_refilled_by_area"].isna())
    ev = q.assign(unused=unused).groupby(["season", "gender", "event_code"]).agg(
        field=("moc_field", "first"), unfilled=("unfilled_spot", lambda s: int((s == True).sum())),  # noqa: E712
        unused_guaranteed_not_refilled=("unused", "sum")).reset_index()
    ev["field_any_round"] = [field_any_round(perf, s, g, e) for s, g, e in ev[["season", "gender", "event_code"]].values]
    ev["unfilled_fixed_field"] = ev["unused_guaranteed_not_refilled"].where(ev["field_any_round"] < MOC_FIELD, 0)
    ev["short_by_fixed"] = (MOC_FIELD - ev["field_any_round"]).clip(lower=0)
    ev["unfilled_capped_at_shortfall"] = ev[["unfilled_fixed_field", "short_by_fixed"]].min(axis=1)
    ev["short_by"] = (MOC_FIELD - ev["field"]).clip(lower=0)
    ev["over_count"] = (ev["unfilled"] - ev["short_by"]).clip(lower=0)
    ev["under_count"] = (ev["short_by"] - ev["unfilled"]).clip(lower=0)
    return ev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--season", type=int, default=2025)
    ap.add_argument("--gender", default="girls")
    ap.add_argument("--area", default="tri-valley")
    ap.add_argument("--events", nargs="+", default=["1600", "800"])
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    q, perf, comp = load()
    d = pd.concat([event_detail(q, comp, a.season, a.gender, e, a.area) for e in a.events])
    d.to_csv(OUT / f"spot_use_{a.area}_{a.season}_{a.gender}.csv", index=False)
    ref, unf = chains(q, comp)
    ref.to_csv(OUT / "refill_chains.csv", index=False)
    unf.to_csv(OUT / "unfilled_chains.csv", index=False)
    c = consistency(q, perf)
    c.to_csv(OUT / "unfilled_vs_shortfall.csv", index=False)
    pd.set_option("display.width", 250), pd.set_option("display.max_columns", 30), pd.set_option("display.max_colwidth", 90)
    print(d[["event", "athlete", "area_place", "route", "what_happened", "old_dashboard_bucket", "new_bucket"]].to_string(index=False))
    print(f"\nrefill chains: {len(ref)} (replacement didn't compete: {int((ref['replacement_competed'] == 0).sum()) if len(ref) else 0})")
    print(f"unfilled spots: {len(unf)}; events with unfilled: {int((c['unfilled'] > 0).sum())}; "
          f"sum of shortfall below 24: {int(c['short_by'].sum())}; over-counted: {int(c['over_count'].sum())} "
          f"in {int((c['over_count'] > 0).sum())} events; under-counted: {int(c['under_count'].sum())} in {int((c['under_count'] > 0).sum())} events")
    print(f"field counted over any round: unfilled {int(c['unfilled_fixed_field'].sum())}, shortfall {int(c['short_by_fixed'].sum())}, "
          f"capped at shortfall {int(c['unfilled_capped_at_shortfall'].sum())}; "
          f"events where unfilled > shortfall: {int((c['unfilled_fixed_field'] > c['short_by_fixed']).sum())}")


if __name__ == "__main__":
    main()
