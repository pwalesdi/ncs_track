"""Replay Area -> MOC qualification for one season and compare with the real MOC entries.

`evaluate` takes one season's Area-meet finals (performances schema) and that season's
rules and tags every final performance with how, if at all, it qualifies for the MOC:

  auto       place <= area_to_moc.auto[area]          (6 / 6 / 6 / Class A 3)
  fill       next best marks from the fill pool        (3 from all four meets, or 6 from
                                                        the three Areas: rules D1)
  at_large   not auto, eligible by place, and the final mark meets or beats the
             season's at-large standard

The parts of the rules we are unsure of are switches on `Interpretation`, so each reading
can be replayed and scored against the MOC programs; the reading whose predictions match
the real entries best is the one to believe. `compare` does the scoring.

Not modelled (yet): scratches and their replacements ("non-qualifying finalists may be
advanced into vacancies"), 4x800 (separate system), league -> Area.
"""

from __future__ import annotations

import itertools
from dataclasses import asdict, dataclass, field
from typing import Callable

import pandas as pd

from .events import EVENTS
from .marks import parse_mark, sort_key
from .names import name_key
from .rules import mark_of

AREAS = ("tri-valley", "bay-shore", "redwood-empire", "class-a")
EPS = 1e-9


@dataclass(frozen=True)
class Interpretation:
    """One reading of the ambiguous rules. Defaults follow the 2026 docs where they speak."""

    name: str = "default"
    # Class A at-large eligibility: eligible if place > this. 3 = "didn't qualify by place"
    # (4th or lower, Patrick's reading); 6 = literal "outside the top 6" (7th or lower). D8.
    class_a_at_large_outside_top: int = 3
    # True: fill spots go to the next best marks first and at-large takes whoever else meets
    # the standard (fill can be "spent" on athletes who had the standard anyway).
    # False: at-large first, then fill goes to the best of those still left.
    fill_before_at_large: bool = True
    # Which fill rule (D1): "authoritative" (whatever the rules file says), "moc_guide"
    # (3, all four meets) or "nbl_flyer" (6, three Areas only).
    fill_source: str = "authoritative"
    # Marks tied at the last fill spot: all in, or none of the tied group.
    fill_ties_include: bool = True
    # Wind-aided marks count for at-large (D6: documents are silent).
    wind_aided_at_large: bool = True

    def describe(self) -> str:
        d = asdict(self)
        return ", ".join(f"{k}={v}" for k, v in d.items() if k != "name")


def interpretation_grid(**axes) -> list[Interpretation]:
    """Every combination of the given axes, e.g. class_a_at_large_outside_top=[3, 6]."""
    keys = list(axes)
    out = []
    for combo in itertools.product(*(axes[k] for k in keys)):
        kw = dict(zip(keys, combo))
        out.append(Interpretation(name=";".join(f"{k}={v}" for k, v in kw.items()), **kw))
    return out


# Default sweep: the two questions Patrick asked to test.
DEFAULT_GRID = dict(class_a_at_large_outside_top=[3, 6], fill_before_at_large=[True, False])


# ---------------------------------------------------------------------------
# Rules access
# ---------------------------------------------------------------------------
def _fill_rule(rules: dict, interp: Interpretation) -> tuple[int, tuple[str, ...]]:
    fill = rules["area_to_moc"]["fill"]
    src = fill["authoritative"] if interp.fill_source == "authoritative" else interp.fill_source
    return int(fill[src]["count"]), tuple(fill[src]["pool"])


def _standard(rules: dict, gender: str, event: str) -> float | None:
    entry = rules["area_to_moc"]["at_large"]["standards"].get(gender, {}).get(event)
    if entry is None:
        return None
    return parse_mark(mark_of(entry), EVENTS[event][0]).value


def main_events(rules: dict) -> list[tuple[str, str]]:
    return [(g, e) for g, evs in rules["events"]["main_simulation"].items() for e in evs]


# ---------------------------------------------------------------------------
# Replay
# ---------------------------------------------------------------------------
EVAL_COLUMNS = [
    "season", "gender", "event_code", "meet_key", "meet_area", "place", "status", "mark_raw",
    "mark_value", "wind_aided", "athlete_name_raw", "school_name_raw", "is_relay",
    "performance_id", "standard_value", "meets_standard", "auto", "at_large_eligible",
    "fill_candidate", "fill_rank", "qualified_by", "interpretation",
]


def _fill_pick(cands: pd.DataFrame, n: int, measure: str, include_ties: bool) -> pd.Index:
    if n <= 0 or cands.empty:
        return cands.index[:0]
    keyed = cands["mark_value"].map(lambda v: sort_key(v, measure)).sort_values(kind="stable")
    if len(keyed) <= n:
        return keyed.index
    cutoff = keyed.iloc[n - 1]
    beyond_is_tied = abs(keyed.iloc[n] - cutoff) < EPS
    if not beyond_is_tied:
        return keyed.index[:n]
    if include_ties:
        return keyed[keyed <= cutoff + EPS].index
    return keyed[keyed < cutoff - EPS].index


def evaluate(results: pd.DataFrame, rules: dict, interp: Interpretation = Interpretation()) -> pd.DataFrame:
    """Every in-scope Area final performance, tagged with how (if at all) it reaches MOC."""
    fill_n, fill_pool = _fill_rule(rules, interp)
    auto_n = rules["area_to_moc"]["auto"]
    outside_top = {a: auto_n[a] for a in AREAS}
    outside_top["class-a"] = interp.class_a_at_large_outside_top
    rounds = set(rules["area_to_moc"]["qualifying_rounds"])

    df = results[(results["level"] == "area") & results["in_scope"].fillna(False)
                 & results["round"].isin(rounds)].copy()
    frames = []
    for gender, event in main_events(rules):
        ev = df[(df["gender"] == gender) & (df["event_code"] == event)].copy()
        if ev.empty:
            continue
        measure = EVENTS[event][0]
        std = _standard(rules, gender, event)
        ok = (ev["status"] == "OK") & ev["mark_value"].notna()
        place = ev["place"].astype("Float64")
        ev["auto"] = ok & place.notna() & (place <= ev["meet_area"].map(auto_n).astype("Float64"))
        ev["auto"] = ev["auto"].fillna(False).astype(bool)
        if std is None:
            ev["meets_standard"] = False
        else:
            better = ev["mark_value"] <= std + EPS if measure == "time" else ev["mark_value"] >= std - EPS
            ev["meets_standard"] = (ok & better).fillna(False).astype(bool)
        by_place = (place > ev["meet_area"].map(outside_top).astype("Float64")).fillna(False)
        wind_ok = True if interp.wind_aided_at_large else ~ev["wind_aided"].fillna(False).astype(bool)
        ev["at_large_eligible"] = (ok & ~ev["auto"] & by_place & wind_ok).astype(bool)
        ev["fill_candidate"] = (ok & ~ev["auto"] & ev["meet_area"].isin(fill_pool)).astype(bool)
        ev["standard_value"] = std

        at_large = ev["at_large_eligible"] & ev["meets_standard"]
        if interp.fill_before_at_large:
            fill_idx = _fill_pick(ev[ev["fill_candidate"]], fill_n, measure, interp.fill_ties_include)
            at_large &= ~ev.index.isin(fill_idx)
        else:
            fill_idx = _fill_pick(ev[ev["fill_candidate"] & ~at_large], fill_n, measure, interp.fill_ties_include)
        ranks = ev.loc[ev["fill_candidate"], "mark_value"].map(lambda v: sort_key(v, measure)).rank(method="min")
        ev["fill_rank"] = ranks.reindex(ev.index).astype("Int64")
        ev["qualified_by"] = None
        ev.loc[ev["auto"], "qualified_by"] = "auto"
        ev.loc[fill_idx, "qualified_by"] = "fill"
        ev.loc[at_large, "qualified_by"] = "at_large"
        frames.append(ev)

    if not frames:
        return pd.DataFrame(columns=EVAL_COLUMNS)
    out = pd.concat(frames)
    out["interpretation"] = interp.name
    return out[EVAL_COLUMNS].reset_index(drop=True)


def predict(results: pd.DataFrame, rules: dict, interp: Interpretation = Interpretation()) -> pd.DataFrame:
    """Predicted MOC entrants: one row per qualifier, tagged auto / fill / at_large."""
    ev = evaluate(results, rules, interp)
    return ev[ev["qualified_by"].notna()].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Compare with MOC programs
# ---------------------------------------------------------------------------
def _identity(name: str | None, school_key: str | None, is_relay: bool) -> str:
    if is_relay or not isinstance(name, str) or not name.strip():
        return f"relay|{school_key}"
    return f"{name_key(name)}|{school_key}"


def _surname_school(identity: str) -> tuple[str, str]:
    """("last", "school_key") from "last|first|school_key"."""
    return identity.split("|", 1)[0], identity.rsplit("|", 1)[1]


@dataclass
class Comparison:
    rows: pd.DataFrame                  # one row per entrant with `outcome`
    summary: pd.DataFrame               # counts per outcome (and per qualified_by)
    notes: list[str] = field(default_factory=list)


OUTCOMES = ("match", "match_last_name_school", "predicted_not_entered", "entered_not_predicted")


def compare(evaluated: pd.DataFrame, entries: pd.DataFrame, rules: dict, *,
            school_key: Callable[[str], str | None], school_area: Callable[[str], str | None]) -> Comparison:
    """Compare predicted qualifiers with MOC program entries for the same season.

    Only entrants from Areas present in `evaluated` are compared: an MOC entrant from an
    Area whose results we don't have can't be predicted, so they are counted separately
    (`not_comparable`), as are entrants whose school has no known area.
    """
    notes = []
    areas = set(evaluated["meet_area"].dropna().unique())
    if areas != set(AREAS):
        notes.append(f"fill pool incomplete: results only for {sorted(areas)}; fill predictions are provisional")
    events = set(main_events(rules))

    pred = evaluated[evaluated["qualified_by"].notna()].copy()
    pred["school_key"] = pred["school_name_raw"].map(school_key)
    pred["identity"] = [_identity(n, s, r) for n, s, r in
                        zip(pred["athlete_name_raw"], pred["school_key"], pred["is_relay"])]

    ent = entries[~entries["is_adaptive"].astype(bool) & entries["event_modifier"].isna()].copy()
    ent = ent[[(g, e) in events for g, e in zip(ent["gender"], ent["event_code"])]]
    ent["school_key"] = ent["school_name"].map(school_key)
    ent["area"] = ent["school_name"].map(school_area)
    ent["identity"] = [_identity(n, s, r) for n, s, r in
                       zip(ent["athlete_name"], ent["school_key"], ent["is_relay"])]
    not_comparable = ent[~ent["area"].isin(areas)]
    ent = ent[ent["area"].isin(areas)]

    # Diagnostic lookup: every evaluated performance (qualified or not) by identity.
    allperf = evaluated.copy()
    allperf["school_key"] = allperf["school_name_raw"].map(school_key)
    allperf["identity"] = [_identity(n, s, r) for n, s, r in
                           zip(allperf["athlete_name_raw"], allperf["school_key"], allperf["is_relay"])]

    rows = []
    for (g, e), p in pred.groupby(["gender", "event_code"]):
        en = ent[(ent["gender"] == g) & (ent["event_code"] == e)]
        p_ids, e_ids = set(p["identity"]), set(en["identity"])
        exact = p_ids & e_ids
        # Same school and surname, different first-name spelling: reported, not merged.
        loose_e = {i: _surname_school(i) for i in e_ids - exact if not i.startswith("relay|")}
        pairs = {}
        for pi in sorted(p_ids - exact):
            if pi.startswith("relay|"):
                continue
            hits = [ei for ei, ek in loose_e.items() if ek == _surname_school(pi) and ei not in pairs.values()]
            if len(hits) == 1:
                pairs[pi] = hits[0]
        for _, r in p.iterrows():
            i = r["identity"]
            outcome = ("match" if i in exact else "match_last_name_school" if i in pairs
                       else "predicted_not_entered")
            rows.append({"gender": g, "event_code": e, "outcome": outcome, "qualified_by": r["qualified_by"],
                         "athlete_name": r["athlete_name_raw"], "school_name": r["school_name_raw"],
                         "area": r["meet_area"], "place": r["place"], "mark_raw": r["mark_raw"],
                         "meets_standard": r["meets_standard"], "fill_rank": r["fill_rank"],
                         "program_name": (en.loc[en["identity"] == pairs[i], "athlete_name"].iloc[0]
                                          if i in pairs else None),
                         "diagnosis": None})
        matched_e = exact | set(pairs.values())
        for _, r in en[~en["identity"].isin(matched_e)].iterrows():
            rows.append({"gender": g, "event_code": e, "outcome": "entered_not_predicted",
                         "qualified_by": None, "athlete_name": r["athlete_name"],
                         "school_name": r["school_name"], "area": r["area"], "place": None,
                         "mark_raw": r["seed_mark_raw"], "meets_standard": None, "fill_rank": None,
                         "program_name": r["athlete_name"],
                         "diagnosis": _diagnose(r, allperf, g, e)})
    # Events with entries but no predictions at all.
    for (g, e), en in ent.groupby(["gender", "event_code"]):
        if ((pred["gender"] == g) & (pred["event_code"] == e)).any():
            continue
        for _, r in en.iterrows():
            rows.append({"gender": g, "event_code": e, "outcome": "entered_not_predicted",
                         "qualified_by": None, "athlete_name": r["athlete_name"], "school_name": r["school_name"],
                         "area": r["area"], "place": None, "mark_raw": r["seed_mark_raw"],
                         "meets_standard": None, "fill_rank": None, "program_name": r["athlete_name"],
                         "diagnosis": _diagnose(r, allperf, g, e)})

    out = pd.DataFrame(rows, columns=["gender", "event_code", "outcome", "qualified_by", "athlete_name",
                                      "school_name", "area", "place", "mark_raw", "meets_standard",
                                      "fill_rank", "program_name", "diagnosis"])
    summary = out.groupby(["outcome"]).size().reindex(OUTCOMES, fill_value=0).rename("n").reset_index()
    summary = pd.concat([summary, pd.DataFrame([
        {"outcome": "not_comparable_area_missing", "n": int(not_comparable["area"].notna().sum())},
        {"outcome": "not_comparable_area_unknown", "n": int(not_comparable["area"].isna().sum())},
    ])], ignore_index=True)
    return Comparison(out, summary, notes)


def _diagnose(entry: pd.Series, allperf: pd.DataFrame, gender: str, event: str) -> str:
    hit = allperf[(allperf["gender"] == gender) & (allperf["event_code"] == event)
                  & (allperf["identity"] == entry["identity"])]
    if hit.empty:
        return "not found in Area finals for this event (name/school mismatch, or entered another way)"
    h = hit.iloc[0]
    bits = [f"Area place {h['place']}", f"mark {h['mark_raw']}",
            "meets standard" if h["meets_standard"] else "below standard"]
    if not h["at_large_eligible"] and not h["auto"]:
        bits.append("not at-large eligible by place under this reading")
    if h["fill_candidate"]:
        bits.append(f"fill rank {h['fill_rank']}")
    return "; ".join(bits)


def score(comp: Comparison) -> dict:
    s = dict(zip(comp.summary["outcome"], comp.summary["n"]))
    matched = s["match"] + s["match_last_name_school"]
    predicted = matched + s["predicted_not_entered"]
    entered = matched + s["entered_not_predicted"]
    return {**s, "precision": matched / predicted if predicted else None,
            "recall": matched / entered if entered else None}


def sweep(results: pd.DataFrame, rules: dict, entries: pd.DataFrame,
          interps: list[Interpretation], **compare_kw) -> pd.DataFrame:
    """Score each interpretation; the one that best reproduces real entries ranks first."""
    rows = []
    for interp in interps:
        comp = compare(evaluate(results, rules, interp), entries, rules, **compare_kw)
        rows.append({"interpretation": interp.name, **score(comp)})
    df = pd.DataFrame(rows)
    df["mismatches"] = df["predicted_not_entered"] + df["entered_not_predicted"]
    return df.sort_values(["mismatches", "interpretation"]).reset_index(drop=True)
