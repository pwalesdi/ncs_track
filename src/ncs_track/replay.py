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

Scratches: with `scratch_replacement` on, a predicted qualifier missing from the program
and an unpredicted entrant from the same Area who was the next finalist in line are
paired and tagged "probable_scratch_replacement" instead of counting as two mismatches.

Not modelled: 4x800 (separate system), league -> Area.
"""

from __future__ import annotations

import itertools
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Callable

import pandas as pd

from .events import EVENTS
from .marks import parse_mark, sort_key
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
    # Pair "predicted but not entered" with "entered, next finalist in line, same Area".
    scratch_replacement: bool = False

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
# Every switch (64 readings).
FULL_GRID = dict(class_a_at_large_outside_top=[3, 6], fill_before_at_large=[True, False],
                 fill_source=["moc_guide", "nbl_flyer"], fill_ties_include=[True, False],
                 wind_aided_at_large=[True, False], scratch_replacement=[False, True])


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
def _name_tokens(name: str) -> list[str]:
    """Order-free name tokens: "Last, First" and "First Last" give the same result."""
    t = unicodedata.normalize("NFKD", name)
    t = "".join(ch for ch in t if not unicodedata.combining(ch)).lower().replace("'", "").replace("’", "")
    t = re.sub(r"\([^)]*\)|\b(jr|sr|ii|iii|iv)\b\.?", " ", t)
    return sorted(re.findall(r"[a-z0-9]+", t))


def _identity(name: str | None, school_key: str | None, is_relay: bool) -> str:
    if is_relay or not isinstance(name, str) or not name.strip():
        return f"relay|{school_key}"
    return f"{' '.join(_name_tokens(name))}|{school_key}"


def _variant_of(a: str, b: str) -> bool:
    """Same school, and the names share a token of 2+ letters (Tess/Tessa Quill)."""
    (na, sa), (nb, sb) = a.rsplit("|", 1), b.rsplit("|", 1)
    return sa == sb and bool({t for t in na.split() if len(t) >= 2} & set(nb.split()))


@dataclass
class Comparison:
    rows: pd.DataFrame                  # one row per entrant with `outcome` and `reason`
    summary: pd.DataFrame               # counts per outcome
    notes: list[str] = field(default_factory=list)


OUTCOMES = ("match", "match_name_variant", "probable_scratch_replacement",
            "predicted_not_entered", "entered_not_predicted")
ROW_COLUMNS = ["gender", "event_code", "outcome", "reason", "qualified_by", "athlete_name", "school_name",
               "area", "place", "mark_raw", "meets_standard", "fill_rank", "program_name", "detail"]


def _row(g, e, outcome, reason, *, qualified_by=None, name=None, school=None, area=None, place=None,
         mark=None, meets=None, fill_rank=None, program_name=None, detail=None) -> dict:
    return dict(zip(ROW_COLUMNS, (g, e, outcome, reason, qualified_by, name, school, area, place, mark,
                                  meets, fill_rank, program_name, detail)))


def _diagnose(identity: str, allperf: pd.DataFrame, gender: str, event: str, fill_n: int) -> tuple[str, str, pd.Series | None]:
    """(reason code, detail, the athlete's Area performance or None) for an unpredicted entrant."""
    hit = allperf[(allperf["gender"] == gender) & (allperf["event_code"] == event) & (allperf["identity"] == identity)]
    if hit.empty:
        return "not_in_area_final", "no matching athlete/team in this event's Area finals", None
    h = hit.iloc[0]
    where = f"{h['meet_area']} place {h['place'] if pd.notna(h['place']) else '-'}, {h['mark_raw']}"
    if h["status"] != "OK":
        return f"area_status_{h['status']}", where, h
    if h["meets_standard"] and not h["at_large_eligible"]:
        why = "wind-aided" if h.get("wind_aided") else f"place {h['place']} not eligible for at-large"
        return "meets_standard_but_not_eligible", f"{where}; {why}", h
    if h["fill_candidate"] and pd.notna(h["fill_rank"]) and h["fill_rank"] <= fill_n + 3:
        return "just_outside_fill", f"{where}; below standard; fill rank {h['fill_rank']} of {fill_n} spots", h
    return "below_standard_not_fill", f"{where}; below standard" + (
        f"; fill rank {h['fill_rank']}" if pd.notna(h["fill_rank"]) else "; not in fill pool"), h


def compare(evaluated: pd.DataFrame, entries: pd.DataFrame, rules: dict, *,
            school_key: Callable[[str], str | None], school_area: Callable[[str], str | None],
            interp: Interpretation = Interpretation()) -> Comparison:
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
    fill_n, _ = _fill_rule(rules, interp)

    allperf = evaluated.copy()
    allperf["school_key"] = allperf["school_name_raw"].map(school_key)
    allperf["identity"] = [_identity(n, s, r) for n, s, r in
                           zip(allperf["athlete_name_raw"], allperf["school_key"], allperf["is_relay"])]
    pred = allperf[allperf["qualified_by"].notna()]

    ent = entries[~entries["is_adaptive"].astype(bool) & entries["event_modifier"].isna()].copy()
    ent = ent[[(g, e) in events for g, e in zip(ent["gender"], ent["event_code"])]]
    ent["school_key"] = ent["school_name"].map(school_key)
    ent["area"] = ent["school_name"].map(school_area)
    ent["identity"] = [_identity(n, s, r) for n, s, r in
                       zip(ent["athlete_name"], ent["school_key"], ent["is_relay"])]
    not_comparable = ent[~ent["area"].isin(areas)]
    ent = ent[ent["area"].isin(areas)]

    rows = []
    for g, e in sorted(events):
        p = pred[(pred["gender"] == g) & (pred["event_code"] == e)]
        en = ent[(ent["gender"] == g) & (ent["event_code"] == e)]
        exact = set(p["identity"]) & set(en["identity"])
        pairs = {}
        e_left = [i for i in en["identity"] if i not in exact and not i.startswith("relay|")]
        for pi in sorted(set(p["identity"]) - exact):
            hits = [ei for ei in e_left if _variant_of(pi, ei) and ei not in pairs.values()]
            if len(hits) == 1 and not pi.startswith("relay|"):
                pairs[pi] = hits[0]
        prog_name = dict(zip(en["identity"], en["athlete_name"]))
        pne, enp = [], []
        for _, r in p.iterrows():
            i = r["identity"]
            base = dict(qualified_by=r["qualified_by"], name=r["athlete_name_raw"], school=r["school_name_raw"],
                        area=r["meet_area"], place=r["place"], mark=r["mark_raw"], meets=r["meets_standard"],
                        fill_rank=r["fill_rank"])
            if i in exact:
                rows.append(_row(g, e, "match", "match", program_name=prog_name[i], **base))
            elif i in pairs:
                rows.append(_row(g, e, "match_name_variant", "name spelled differently",
                                 program_name=prog_name[pairs[i]], **base))
            else:
                pne.append(_row(g, e, "predicted_not_entered", f"predicted_{r['qualified_by']}_not_in_program",
                                detail="qualified under this reading but not in the MOC program", **base))
        for _, r in en[~en["identity"].isin(exact | set(pairs.values()))].iterrows():
            reason, detail, h = _diagnose(r["identity"], allperf, g, e, fill_n)
            enp.append(_row(g, e, "entered_not_predicted", reason, name=r["athlete_name"], school=r["school_name"],
                            area=r["area"], place=None if h is None else h["place"], mark=r["seed_mark_raw"],
                            meets=None if h is None else h["meets_standard"],
                            fill_rank=None if h is None else h["fill_rank"], program_name=r["athlete_name"],
                            detail=detail))
        if interp.scratch_replacement:
            _pair_scratches(pne, enp, allperf[(allperf["gender"] == g) & (allperf["event_code"] == e)])
        rows += pne + enp

    out = pd.DataFrame(rows, columns=ROW_COLUMNS)
    summary = out.groupby("outcome").size().reindex(OUTCOMES, fill_value=0).rename("n").reset_index()
    summary = pd.concat([summary, pd.DataFrame([
        {"outcome": "not_comparable_area_missing", "n": int(not_comparable["area"].notna().sum())},
        {"outcome": "not_comparable_area_unknown", "n": int(not_comparable["area"].isna().sum())},
    ])], ignore_index=True)
    return Comparison(out, summary, notes)


def _pair_scratches(pne: list[dict], enp: list[dict], event_perf: pd.DataFrame) -> None:
    """Tag (predicted-not-entered, entered-not-predicted) pairs from one Area where the
    entrant was among the next finalists in line after that Area's qualifiers."""
    for area in {r["area"] for r in pne}:
        missing = sorted((r for r in pne if r["area"] == area and r["outcome"] == "predicted_not_entered"),
                         key=lambda r: r["place"] if pd.notna(r["place"]) else 1e9)
        line = event_perf[(event_perf["meet_area"] == area) & event_perf["qualified_by"].isna()
                          & (event_perf["status"] == "OK") & event_perf["place"].notna()].sort_values("place")
        next_places = list(line["place"].iloc[:len(missing)])
        subs = [r for r in enp if r["area"] == area and r["outcome"] == "entered_not_predicted"
                and pd.notna(r["place"]) and r["place"] in next_places]
        for m, sub in zip(missing, sorted(subs, key=lambda r: r["place"])):
            for r, other in ((m, sub), (sub, m)):
                r["outcome"] = "probable_scratch_replacement"
                r["reason"] = "probable_scratch_replacement"
                r["detail"] = f"paired with {other['athlete_name'] or other['school_name']} ({area} place {other['place']})"


def score(comp: Comparison) -> dict:
    s = dict(zip(comp.summary["outcome"], comp.summary["n"]))
    matched = s["match"] + s["match_name_variant"]
    scratch_pairs = s["probable_scratch_replacement"] // 2
    predicted = matched + s["predicted_not_entered"] + scratch_pairs
    entered = matched + s["entered_not_predicted"] + scratch_pairs
    mismatches = s["predicted_not_entered"] + s["entered_not_predicted"]
    return {**s, "mismatches": mismatches,
            "match_rate": matched / (matched + mismatches + 2 * scratch_pairs) if matched + mismatches else None,
            "precision": matched / predicted if predicted else None,
            "recall": matched / entered if entered else None}


def rates(rows: pd.DataFrame, by: str) -> pd.DataFrame:
    """Match rate per group: matched / (matched + predicted-not-entered + entered-not-predicted)."""
    t = rows.assign(ok=rows["outcome"].isin(["match", "match_name_variant"]),
                    pne=rows["outcome"] == "predicted_not_entered",
                    enp=rows["outcome"] == "entered_not_predicted",
                    scr=rows["outcome"] == "probable_scratch_replacement")
    g = t.groupby(by)[["ok", "pne", "enp", "scr"]].sum().astype(int)
    g["match_rate"] = (g["ok"] / (g["ok"] + g["pne"] + g["enp"] + g["scr"])).round(3)
    return g.rename(columns={"ok": "matched", "pne": "predicted_not_entered", "enp": "entered_not_predicted",
                             "scr": "scratch_pairs_rows"})


def sweep(results: pd.DataFrame, rules: dict, entries: pd.DataFrame,
          interps: list[Interpretation], **compare_kw) -> pd.DataFrame:
    """Score each interpretation; the one that best reproduces real entries ranks first."""
    rows = []
    for interp in interps:
        ev = evaluate(results, rules, interp)
        comp = compare(ev, entries, rules, interp=interp, **compare_kw)
        pred = ev[ev["qualified_by"].notna()]
        rows.append({"interpretation": interp.name, **asdict(interp), **score(comp),
                     "predicted_set": frozenset(zip(pred["performance_id"], pred["qualified_by"]))})
    df = pd.DataFrame(rows)
    return df.sort_values(["mismatches", "interpretation"]).reset_index(drop=True)


def switch_effects(table: pd.DataFrame, axes: dict) -> pd.DataFrame:
    """For each switch: across pairs of readings that differ only in that switch, how often
    the predicted list changes and how the mismatch count moves."""
    out = []
    for k, values in axes.items():
        others = [a for a in axes if a != k]
        changed = n = 0
        deltas = []
        for _, grp in table.groupby(others):
            if len(grp) != len(values):
                continue
            n += 1
            sets = grp.set_index(k)["predicted_set"]
            mism = grp.set_index(k)["mismatches"]
            changed += int(len(set(sets)) > 1)
            deltas.append(int(mism[values[1]] - mism[values[0]]))
        out.append({"switch": k, "values": f"{values[0]} -> {values[1]}", "pairs": n,
                    "predicted_list_changes_in": changed,
                    "mismatch_delta_min": min(deltas), "mismatch_delta_max": max(deltas)})
    return pd.DataFrame(out)
