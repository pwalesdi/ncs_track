"""Table-level validation of normalised performances.

Row-level checks (V01-V04, V06 parse, V09 leg counts, V11, V13 parse) run during
ingest. The checks here need a whole meet or event at once. Check IDs match
docs/ingest_spec_athleticnet.md.
"""

from __future__ import annotations

import pandas as pd

from .issues import Issue
from .marks import sort_key

# Loose sanity bounds, seconds or meters, either gender. Outside -> warning.
PLAUSIBLE: dict[str, tuple[float, float]] = {
    "100": (9.5, 20), "200": (19, 40), "400": (43, 90), "800": (100, 240),
    "1600": (230, 480), "3200": (500, 1000), "100H": (12, 25), "110H": (12.5, 25),
    "300H": (34, 70), "4x100": (40, 65), "4x400": (190, 300), "4x800": (440, 720),
    "HJ": (1.0, 2.4), "PV": (1.5, 6.0), "LJ": (3.0, 8.5), "TJ": (7, 17),
    "SP": (5, 22), "DT": (15, 70),
}

# One placed "race": places restart for each division (Unified is placed separately).
GROUP = ["meet_key", "gender", "division_raw", "event_code", "event_modifier", "round"]


def _groups(perf: pd.DataFrame):
    return perf.groupby(GROUP, dropna=False, sort=False)


def _entrant(row) -> str:
    if row["is_relay"]:
        return f"team:{row['school_id']}:{row['relay_team_label'] or ''}"
    return f"athlete:{row['athlete_id']}"


def check_plausible(perf: pd.DataFrame) -> list[Issue]:
    out = []
    ok = perf[perf["mark_value"].notna() & perf["event_code"].notna()]
    for r in ok.itertuples():
        lo, hi = PLAUSIBLE[r.event_code]
        if not lo <= r.mark_value <= hi:
            out.append(Issue("V05", "warning", r.meet_key,
                             f"{r.event_code} mark {r.mark_raw!r} = {r.mark_value} outside [{lo}, {hi}]",
                             r.performance_id))
    return out


def check_place_order(perf: pd.DataFrame) -> list[Issue]:
    """Places must not contradict marks; ties are reported as info."""
    out = []
    placed = perf[(perf["status"] == "OK") & perf["place"].notna() & perf["mark_value"].notna()]
    for key, g in _groups(placed):
        g = g.sort_values("place")
        measure = g["measure"].iloc[0]
        prev = None
        for r in g.itertuples():
            k = sort_key(r.mark_value, measure)
            if prev is not None and k < prev[0] - 1e-9 and r.place > prev[1]:
                out.append(Issue("V06", "error", r.meet_key,
                                 f"{key[1:]}: place {r.place} ({r.mark_raw}) beats place {prev[1]} ({prev[2]})",
                                 r.performance_id))
            prev = (k, r.place, r.mark_raw)
        dup = g[g.duplicated("place", keep=False)]
        if len(dup):
            out.append(Issue("V06", "info", g["meet_key"].iloc[0],
                             f"{key[1:]}: tied places {sorted(dup['place'].unique().tolist())}"))
        if g["round"].iloc[0] == "final" and g["place"].min() != 1:
            out.append(Issue("V06", "warning", g["meet_key"].iloc[0], f"{key[1:]}: first place is {g['place'].min()}"))
    return out


def check_identity(perf: pd.DataFrame) -> list[Issue]:
    out = []
    ind = perf[~perf["is_relay"].fillna(False).astype(bool)]
    for r in ind[ind["athlete_id"].isna() & ind["in_scope"]].itertuples():
        out.append(Issue("V07", "warning", r.meet_key, "individual row without athlete_id (review queue)",
                         r.performance_id))
    with_id = ind[ind["athlete_id"].notna()]
    bad = with_id[~with_id["athlete_id"].str.fullmatch(r"\d+")]
    for r in bad.itertuples():
        out.append(Issue("V07", "error", r.meet_key, f"non-numeric athlete_id {r.athlete_id!r}", r.performance_id))
    dup = with_id[with_id.duplicated(GROUP + ["athlete_id"], keep=False)]
    for r in dup.itertuples():
        out.append(Issue("V07", "error", r.meet_key,
                         f"athlete_id {r.athlete_id} appears twice in {r.gender} {r.event_code} {r.round}",
                         r.performance_id))
    # V08: one id, several names; one name+school, several ids.
    for (meet, aid), g in with_id.groupby(["meet_key", "athlete_id"]):
        if g["athlete_name_key"].nunique() > 1:
            out.append(Issue("V08", "warning", meet,
                             f"athlete_id {aid} has names {sorted(g['athlete_name_raw'].unique())}"))
    for (meet, nk, sid), g in with_id.groupby(["meet_key", "athlete_name_key", "school_id"]):
        if g["athlete_id"].nunique() > 1:
            out.append(Issue("V08", "warning", meet,
                             f"{g['athlete_name_raw'].iloc[0]} ({sid}) has ids {sorted(g['athlete_id'].unique())}"))
    return out


def check_relays(perf: pd.DataFrame, legs: pd.DataFrame) -> list[Issue]:
    out = []
    counts = legs.groupby("performance_id").size()
    relays = perf[perf["is_relay"].fillna(False).astype(bool) & (perf["status"] == "OK")]
    for r in relays.itertuples():
        n = int(counts.get(r.performance_id, 0))
        if n != 4:
            out.append(Issue("V09", "warning", r.meet_key, f"relay has {n} legs listed", r.performance_id))
    return out


def check_schools(perf: pd.DataFrame, known_school_ids: set[str] | None = None) -> list[Issue]:
    out = []
    for r in perf[perf["school_id"].isna()].itertuples():
        out.append(Issue("V10", "error", r.meet_key, "missing school_id", r.performance_id))
    for (meet, sid), g in perf[perf["school_id"].notna()].groupby(["meet_key", "school_id"]):
        names = sorted(g["school_name_raw"].unique())
        if len(names) > 1:
            out.append(Issue("V10", "warning", meet, f"school_id {sid} has names {names}"))
        if known_school_ids is not None and sid not in known_school_ids:
            out.append(Issue("V10", "warning", meet, f"school_id {sid} ({names[0]}) not in schools reference"))
    return out


def check_coverage(perf: pd.DataFrame, rules: dict) -> list[Issue]:
    out = []
    finals = perf[perf["in_scope"] & (perf["round"] == "final")]
    for meet in perf["meet_key"].unique():
        have = set(zip(finals.loc[finals["meet_key"] == meet, "gender"], finals.loc[finals["meet_key"] == meet, "event_code"]))
        for gender, codes in rules["events"]["main_simulation"].items():
            for code in codes:
                if (gender, code) not in have:
                    out.append(Issue("V12", "warning", meet, f"no in-scope final rows for {gender} {code}"))
    return out


def check_rounds(perf: pd.DataFrame) -> list[Issue]:
    """Everyone in a final should appear in that event's prelim, when a prelim exists."""
    out = []
    scoped = perf[perf["in_scope"]]
    for (meet, gender, code), g in scoped.groupby(["meet_key", "gender", "event_code"]):
        rounds = set(g["round"])
        if not {"prelim", "final"} <= rounds:
            continue
        pre = {_entrant(r) for _, r in g[g["round"] == "prelim"].iterrows()}
        for _, r in g[g["round"] == "final"].iterrows():
            if _entrant(r) not in pre:
                out.append(Issue("V14", "warning", meet, f"{gender} {code}: finalist {_entrant(r)} not in prelims",
                                 r["performance_id"]))
    return out


def summarize(perf: pd.DataFrame) -> list[Issue]:
    out = []
    for meet, g in perf.groupby("meet_key"):
        n_adapt = int(g["is_adaptive"].sum())
        n_mod = int(g["event_modifier"].notna().sum())
        n_out = int((~g["in_scope"]).sum())
        n_wind = int(g["wind_aided"].sum())
        out.append(Issue("V15", "info", meet,
                         f"{len(g)} rows; out of scope {n_out} (adaptive {n_adapt}, modifier blocks {n_mod}); "
                         f"wind-aided {n_wind}"))
    return out


def run_all(perf: pd.DataFrame, legs: pd.DataFrame, rules: dict,
            known_school_ids: set[str] | None = None) -> list[Issue]:
    return (check_plausible(perf) + check_place_order(perf) + check_identity(perf)
            + check_relays(perf, legs) + check_schools(perf, known_school_ids)
            + check_coverage(perf, rules) + check_rounds(perf) + summarize(perf))


def review_queue(perf: pd.DataFrame) -> pd.DataFrame:
    """In-scope individual rows with no athlete_id: to be matched by hand."""
    ind = perf[~perf["is_relay"].fillna(False).astype(bool) & perf["in_scope"] & perf["athlete_id"].isna()]
    return ind[["performance_id", "meet_key", "gender", "event_code", "round", "athlete_name_raw",
                "athlete_name_key", "grade", "grad_year", "school_id", "school_name_raw", "mark_raw"]]
