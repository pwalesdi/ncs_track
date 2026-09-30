"""Verification round A (read-only). Writes to outputs/verify/ (git-ignored; real names).

    .venv/bin/python scripts/checks/verify_round_a.py

A1  Tri-Valley boys 800 athlete by athlete, 2022-2026; which rows count as "empty"; and a
    breakdown of empty spots by qualifier type for every Area and season.
A2  "Unused guaranteed spots": only the fixed spots (automatic + next best mark) whose
    qualifier didn't compete, in events whose MOC field ended below 24; per Area and season,
    next to the old empty-lane number.
A3  Every 2026 next-best-mark qualifier, and per event the best Class A non-qualifier's mark
    against the 3rd next-best-mark cutoff.
"""

import pandas as pd

from ncs_track import allocate, paths, replay
from ncs_track.analysis import NOT_COMPETED
from ncs_track.cli import replay_inputs
from ncs_track.events import EVENTS

OUT = paths.OUTPUTS / "verify"
TYPE = {"auto": "automatic", "fill": "next_best_mark", "at_large": "at_large_standard"}
SEASONS = (2022, 2023, 2024, 2025, 2026)
FIELD = 24


def tok(n):
    return " ".join(replay._name_tokens(str(n)))


def load():
    q = pd.read_csv(paths.OUTPUTS / "qualifiers.csv", low_memory=False, dtype={"athlete_id": str})
    q["event_code"] = q["event_code"].astype(str)
    perf = pd.read_csv(paths.PROCESSED / "performances.csv", low_memory=False, dtype={"athlete_id": str})
    ent = pd.read_csv(paths.PROCESSED / "moc_entries.csv")
    ent = ent[~ent["is_adaptive"] & ent["event_modifier"].isna()]
    return q, perf, ent


def empty_flag(q):
    """The old metric per athlete: qualified, did not compete, spot not refilled."""
    return (q["in_qualified_field"] == 1) & (q["competed"] == 0) & q["vacancy_refilled_by_area"].isna()


def moc_field(perf, season, gender, event):
    """Athletes/teams who competed in the MOC event (any status but DNS/SCR), first round."""
    m = perf[(perf["season"] == season) & (perf["level"] == "moc") & perf["in_scope"]
             & (perf["gender"] == gender) & (perf["event_code"].astype(str) == event)]
    rounds = set(m["round"])
    first = m[m["round"] == ("prelim" if "prelim" in rounds else "final")]
    return int((~first["status"].isin(NOT_COMPETED)).sum()), len(first)


def a1(q, perf, ent):
    rows, entry_counts = [], []
    ent_all = pd.read_csv(paths.PROCESSED / "moc_entries.csv")
    ent_all = ent_all[~ent_all["is_adaptive"]]                   # incl. 4x800 and relay rosters
    cfg = allocate.load_config(paths.ROOT / "configs" / "allocation" / "current.yaml")
    for season in SEASONS:
        results, entries, rules, _, kw, legs = replay_inputs(season)
        ev = allocate.allocate(results, rules, cfg)
        ev = ev[(ev["meet_area"] == "tri-valley") & (ev["gender"] == "boys") & (ev["event_code"] == "800")]
        qs = q[(q["season"] == season) & (q["gender"] == "boys") & (q["event_code"] == "800")]
        moc = perf[(perf["season"] == season) & (perf["level"] == "moc")]
        moc_all = moc[~moc["is_adaptive"].astype(bool)]          # incl. 4x800 and relay rows
        rel = moc_all[moc_all["is_relay"].astype(bool) & ~moc_all["status"].isin(NOT_COMPETED)]
        legs_run = legs.merge(rel[["performance_id", "event_code"]], on="performance_id")
        moc = moc[moc["in_scope"]]
        se = ent_all[ent_all["season"] == season]
        competed, listed = moc_field(perf, season, "boys", "800")
        prog800 = int(((se["gender"] == "boys") & (se["event_code"].astype(str) == "800")).sum())
        entry_counts.append({"season": season, "moc_boys_800_program_entries": prog800,
                             "moc_boys_800_first_round_rows": listed, "moc_boys_800_competed": competed})
        for r in ev.sort_values("place").itertuples():
            aid = r.athlete_id
            qr = qs[qs["athlete_id"] == aid]
            qr = qr.iloc[0] if len(qr) else None
            m800 = moc[(moc["athlete_id"] == aid) & (moc["event_code"].astype(str) == "800") & (moc["gender"] == "boys")]
            other = set(moc_all.loc[(moc_all["athlete_id"] == aid) & ~moc_all["status"].isin(NOT_COMPETED)
                                    & (moc_all["event_code"].astype(str) != "800"), "event_code"].astype(str))
            other |= {f"{e} (relay leg)" for e in legs_run.loc[legs_run["athlete_id"] == aid, "event_code"].astype(str)}
            other = sorted(other)
            t0 = tok(r.athlete_name_raw)
            prog = se[(se["gender"] == "boys") & ((se["athlete_name"].map(tok) == t0)
                      | se["relay_legs"].fillna("").map(lambda s: any(tok(x.strip().rsplit(" ", 1)[0]) == t0 for x in s.split(";"))))]
            rows.append({
                "season": season, "area_place": r.place, "name": r.athlete_name_raw, "school": r.school_name_raw,
                "area_mark": r.mark_raw, "qualifier_type": TYPE.get(r.qualified_by, "not qualified"),
                "in_moc_program_800": bool(qr is not None and qr["in_declared_field"] == 1),
                "competed_moc_800": "; ".join(f"{x.round} {x.mark_raw} (place {x.place if pd.notna(x.place) else '-'}, {x.status})"
                                              for x in m800.itertuples()) or "no",
                "program_events": ", ".join(sorted(set(prog["event_code"].astype(str) + prog["is_relay"].map({True: " (roster)", False: ""})))) or "none",
                "competed_other_moc_events": ", ".join(other) or "none",
                "choice_tag": qr["choice_tag"] if qr is not None else None,
                "refilled_by": qr["vacancy_refilled_by_area"] if qr is not None else None,
                "counted_as_empty": bool(qr is not None and qr["in_qualified_field"] == 1 and qr["competed"] == 0
                                         and pd.isna(qr["vacancy_refilled_by_area"])),
            })
    t = pd.DataFrame(rows)
    counts = pd.DataFrame(entry_counts)
    t.to_csv(OUT / "tv_boys_800.csv", index=False)
    counts.to_csv(OUT / "moc_boys_800_entries.csv", index=False)
    by_type = (q[empty_flag(q)].groupby(["season", "area", "qualifier_type"]).size()
               .unstack(fill_value=0).reset_index())
    by_type.to_csv(OUT / "empty_by_qualifier_type.csv", index=False)
    return t, counts, by_type


def a2(q, perf):
    """Unused guaranteed spots per Area x season, next to the old empty-lane count."""
    fields = {}
    for (s, g, e), _ in q.groupby(["season", "gender", "event_code"]):
        fields[(s, g, e)] = moc_field(perf, s, g, e)[0]
    q = q.assign(moc_field=[fields[(s, g, e)] for s, g, e in zip(q["season"], q["gender"], q["event_code"])])
    guaranteed = q["qualifier_type"].isin(["automatic", "next_best_mark"]) & (q["in_qualified_field"] == 1)
    unused_g = guaranteed & (q["competed"] == 0) & q["vacancy_refilled_by_area"].isna()
    q = q.assign(unfilled_guaranteed=unused_g & (q["moc_field"] < FIELD), old_empty=empty_flag(q))
    per_event = q.groupby(["season", "gender", "event_code", "area"]).agg(
        unfilled_guaranteed=("unfilled_guaranteed", "sum"), old_empty=("old_empty", "sum"),
        moc_field=("moc_field", "first")).reset_index()
    per_area = q.groupby(["season", "area"]).agg(
        guaranteed_spots=("qualifier_type", lambda s: int(s.isin(["automatic", "next_best_mark"]).sum())),
        old_empty_lanes=("old_empty", "sum"), unfilled_guaranteed=("unfilled_guaranteed", "sum")).reset_index()
    # guaranteed_spots counted over the qualified field only
    gs = q[guaranteed].groupby(["season", "area"]).size().rename("guaranteed_spots")
    per_area = per_area.drop(columns="guaranteed_spots").merge(gs.reset_index(), on=["season", "area"])
    short = per_event.drop_duplicates(["season", "gender", "event_code"])
    short_events = short[short["moc_field"] < FIELD].groupby("season").size().rename("events_with_field_below_24")
    per_area.to_csv(OUT / "unused_guaranteed_by_area.csv", index=False)
    per_event.to_csv(OUT / "unused_guaranteed_by_event.csv", index=False)
    return per_area, short_events, q


def a3(perf):
    cfg = allocate.load_config(paths.ROOT / "configs" / "allocation" / "current.yaml")
    results, entries, rules, _, kw, legs = replay_inputs(2026)
    ev = allocate.allocate(results, rules, cfg)
    nbm = ev[ev["qualified_by"] == "fill"].copy()
    rows, cmp_rows = [], []
    for r in nbm.sort_values(["gender", "event_code", "fill_rank"]).itertuples():
        rows.append({"gender": r.gender, "event": r.event_code, "area": r.meet_area, "name": r.athlete_name_raw,
                     "school": r.school_name_raw, "area_place": r.place, "area_mark": r.mark_raw, "fill_rank": r.fill_rank})
    for (g, e), x in ev.groupby(["gender", "event_code"]):
        measure = EVENTS[e][0]
        fills = x[x["qualified_by"] == "fill"]
        if fills.empty:
            continue
        key = lambda d: d["mark_value"] if measure == "time" else -d["mark_value"]
        cutoff = fills.assign(k=key(fills)).sort_values("k").iloc[-1]
        ca = x[(x["meet_area"] == "class-a") & x["qualified_by"].isna() & (x["status"] == "OK") & x["mark_value"].notna()]
        best = ca.assign(k=key(ca)).sort_values("k").iloc[0] if len(ca) else None
        gap = None
        if best is not None:
            gap = round(abs(best["mark_value"] - cutoff["mark_value"]), 2)
        cmp_rows.append({"gender": g, "event": e, "class_a_nbm_qualifiers": int((fills["meet_area"] == "class-a").sum()),
                         "third_nbm_cutoff_mark": cutoff["mark_raw"], "cutoff_area": cutoff["meet_area"],
                         "best_class_a_non_qualifier": best["athlete_name_raw"] if best is not None else None,
                         "best_class_a_place": best["place"] if best is not None else None,
                         "best_class_a_mark": best["mark_raw"] if best is not None else None,
                         "gap_to_cutoff": gap, "unit": "s" if measure == "time" else "m"})
    a = pd.DataFrame(rows)
    b = pd.DataFrame(cmp_rows)
    a.to_csv(OUT / "nbm_2026.csv", index=False)
    b.to_csv(OUT / "nbm_2026_class_a_vs_cutoff.csv", index=False)
    return a, b


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_rows", 200)
    pd.set_option("display.max_colwidth", 60)
    q, perf, ent = load()
    t, counts, by_type = a1(q, perf, ent)
    print("A1 MOC boys 800 entries:\n", counts.to_string(index=False))
    print("\nA1 Tri-Valley boys 800 rows counted as empty:")
    print(t[t["counted_as_empty"]].drop(columns=["counted_as_empty"]).to_string(index=False))
    print("\nA1 empty spots by qualifier type (all Areas):\n", by_type.to_string(index=False))
    print("\nA1 totals by type:", by_type.drop(columns=["season", "area"]).sum().to_dict())
    per_area, short_events, _ = a2(q, perf)
    print("\nA2 unused guaranteed spots vs old empty lanes:\n", per_area.to_string(index=False))
    print("\nA2 events with MOC field below 24:", short_events.to_dict())
    a, b = a3(perf)
    print("\nA3 2026 next-best-mark qualifiers by Area:", a.groupby("area").size().to_dict(), "total", len(a))
    print(b.to_string(index=False))


if __name__ == "__main__":
    main()
