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

Overlays (they never change predictions, only explain mismatches):
- replacement: "same_area" pairs a predicted qualifier missing from the program with an
  unpredicted entrant who was the next finalist in line in the same Area; "fill_line"
  fills the event's vacancies with the next marks in the fill pool, section-wide.
- athlete choice: every predicted qualifier missing from the program is tagged
  "chose_other_events" (listed elsewhere in the program: another event, the 4x800 or a
  relay roster) or "did_not_declare" (not in the program at all).
- entry_limit (assumed, NFHS 4 events incl. relays, unverified): a missing qualifier who
  qualified in more events than the limit is tagged "entry_limit_assumed".

Two match rates: RAW counts every difference; RULES counts only differences no overlay
explains.

Not modelled: 4x800 (separate system), league -> Area.
"""

from __future__ import annotations

import itertools
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from difflib import SequenceMatcher
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
    # Overlay: how vacancies were refilled. "off" | "same_area" | "fill_line".
    replacement: str = "off"
    # Overlay: max events per athlete incl. relays (0 = off). 4 is ASSUMED, not verified.
    entry_limit: int = 0

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
# Rule switches change predictions; overlay switches only explain mismatches.
RULE_AXES = dict(class_a_at_large_outside_top=[3, 6], fill_before_at_large=[True, False],
                 fill_source=["moc_guide", "nbl_flyer"], fill_ties_include=[True, False],
                 wind_aided_at_large=[True, False])
OVERLAY_AXES = dict(replacement=["off", "same_area", "fill_line"], entry_limit=[0, 4])
FULL_GRID = {**RULE_AXES, **OVERLAY_AXES}


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
    "season", "gender", "event_code", "meet_key", "meet_area", "place", "status", "mark_raw", "athlete_id",
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
    rows: pd.DataFrame                  # one row per entrant with `outcome`, `reason`, `explained_by`
    summary: pd.DataFrame               # counts per outcome
    notes: list[str] = field(default_factory=list)


OUTCOMES = ("match", "match_name_variant", "predicted_not_entered", "entered_not_predicted")
ROW_COLUMNS = ["gender", "event_code", "outcome", "reason", "explained_by", "choice_tag", "qualified_by",
               "athlete_name", "school_name", "area", "place", "mark_raw", "meets_standard", "fill_rank",
               "program_name", "detail", "vacancy_filled_by_area", "fills_vacancy_of_area",
               "athlete_id", "identity"]
QUALIFIED_BY_ORDER = {"auto": 0, "at_large": 1, "fill": 2}


def _row(g, e, outcome, reason, **kw) -> dict:
    r = dict.fromkeys(ROW_COLUMNS)
    r.update(gender=g, event_code=e, outcome=outcome, reason=reason, **kw)
    return r


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
            interp: Interpretation = Interpretation(), legs: pd.DataFrame | None = None) -> Comparison:
    """Compare predicted qualifiers with MOC program entries for the same season.

    Only entrants from Areas present in `evaluated` are compared: an MOC entrant from an
    Area whose results we don't have can't be predicted, so they are counted separately
    (`not_comparable`), as are entrants whose school has no known area. An unpredicted
    entrant's area is the Area meet their result came from (their school's area only if
    they have no Area result). `legs` (relay_legs) lets the entry limit count relays.
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
    declared_ids = _declared_anywhere(entries, school_key)
    over_limit = _over_entry_limit(pred, legs, interp.entry_limit)

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
            base = dict(qualified_by=r["qualified_by"], athlete_name=r["athlete_name_raw"],
                        school_name=r["school_name_raw"], area=r["meet_area"], place=r["place"],
                        mark_raw=r["mark_raw"], meets_standard=r["meets_standard"], fill_rank=r["fill_rank"],
                        athlete_id=r["athlete_id"], identity=i)
            if i in exact:
                rows.append(_row(g, e, "match", "match", program_name=prog_name[i], **base))
            elif i in pairs:
                rows.append(_row(g, e, "match_name_variant", "name spelled differently",
                                 program_name=prog_name[pairs[i]], **base))
            else:
                choice = "chose_other_events" if _in_program(g, i, declared_ids) else "did_not_declare"
                limited = interp.entry_limit and r["athlete_id"] in over_limit
                pne.append(_row(g, e, "predicted_not_entered", f"predicted_{r['qualified_by']}_not_in_program",
                                choice_tag=choice, explained_by="entry_limit_assumed" if limited else choice,
                                detail="qualified under this reading but not in the MOC program", **base))
        for _, r in en[~en["identity"].isin(exact | set(pairs.values()))].iterrows():
            reason, detail, h = _diagnose(r["identity"], allperf, g, e, fill_n)
            enp.append(_row(g, e, "entered_not_predicted", reason, athlete_name=r["athlete_name"],
                            school_name=r["school_name"], area=r["area"] if h is None else h["meet_area"],
                            place=None if h is None else h["place"], mark_raw=r["seed_mark_raw"],
                            meets_standard=None if h is None else h["meets_standard"],
                            fill_rank=None if h is None else h["fill_rank"], program_name=r["athlete_name"],
                            athlete_id=None if h is None else h["athlete_id"], identity=r["identity"],
                            detail=detail))
        event_perf = allperf[(allperf["gender"] == g) & (allperf["event_code"] == e)]
        if interp.replacement == "same_area":
            _pair_same_area(pne, enp, event_perf)
        elif interp.replacement == "fill_line":
            _pair_fill_line(pne, enp, event_perf, interp.fill_ties_include)
        elif interp.replacement != "off":
            raise ValueError(f"unknown replacement mode {interp.replacement!r}")
        rows += pne + enp

    out = pd.DataFrame(rows, columns=ROW_COLUMNS)
    summary = out.groupby("outcome").size().reindex(OUTCOMES, fill_value=0).rename("n").reset_index()
    summary = pd.concat([summary, pd.DataFrame([
        {"outcome": "not_comparable_area_missing", "n": int(not_comparable["area"].notna().sum())},
        {"outcome": "not_comparable_area_unknown", "n": int(not_comparable["area"].isna().sum())},
    ])], ignore_index=True)
    return Comparison(out, summary, notes)


def _declared_anywhere(entries: pd.DataFrame, school_key: Callable[[str], str | None]) -> set:
    """(gender, identity) of everyone listed anywhere in the program: every individual
    event including the 4x800, and every relay roster (legs and alternates)."""
    ent = entries[~entries["is_adaptive"].astype(bool)]
    out = set()
    for r in ent.itertuples():
        key = school_key(r.school_name)
        out.add((r.gender, _identity(r.athlete_name, key, r.is_relay)))
        if r.is_relay and isinstance(r.relay_legs, str):
            for leg in r.relay_legs.split(";"):
                name = re.sub(r"\s+\d{1,2}$", "", leg.strip())
                if name:
                    out.add((r.gender, _identity(name, key, False)))
    return out


SPELLING_RATIO = 0.9       # "jonas renwick" vs "jonas renwik" = 0.96; different first names fall well below


def _in_program(gender: str, identity: str, declared_ids: set) -> bool:
    """Listed anywhere in the program: exact identity, or the same school and gender with a
    near-identical name (one-letter spelling differences between Athletic.net and the program)."""
    if (gender, identity) in declared_ids:
        return True
    name, school = identity.rsplit("|", 1)
    return any(g == gender and d.rsplit("|", 1)[1] == school
               and SequenceMatcher(None, name, d.rsplit("|", 1)[0]).ratio() >= SPELLING_RATIO
               for g, d in declared_ids if not d.startswith("relay|"))


def _over_entry_limit(pred: pd.DataFrame, legs: pd.DataFrame | None, limit: int) -> set:
    """Athlete IDs predicted to qualify in more than `limit` events (relays via Area legs)."""
    if not limit:
        return set()
    ind = pred[~pred["is_relay"].astype(bool) & pred["athlete_id"].notna()][["athlete_id", "gender", "event_code"]]
    parts = [ind]
    if legs is not None and len(legs):
        rel = pred[pred["is_relay"].astype(bool)][["performance_id", "gender", "event_code"]]
        parts.append(legs.merge(rel, on="performance_id")[["athlete_id", "gender", "event_code"]].dropna())
    counts = pd.concat(parts).drop_duplicates().groupby("athlete_id").size()
    return set(counts[counts > limit].index)


def _mark_pair(vacancy: dict, sub: dict, how: str) -> None:
    vacancy["vacancy_filled_by_area"] = sub["area"]
    sub["fills_vacancy_of_area"] = vacancy["area"]
    sub["explained_by"] = f"replacement_{how}"
    vacancy["detail"] = f"{vacancy['detail']}; vacancy refilled ({how}) by {sub['area']} place {sub['place']}"
    sub["detail"] = f"{sub['detail']}; replacement ({how}) for {vacancy['area']} vacancy"


def _pair_same_area(pne: list[dict], enp: list[dict], event_perf: pd.DataFrame) -> None:
    """Pair each Area's vacancies with that Area's next finalists in line."""
    for area in {r["area"] for r in pne}:
        vac = sorted((r for r in pne if r["area"] == area),
                     key=lambda r: r["place"] if pd.notna(r["place"]) else 1e9)
        line = event_perf[(event_perf["meet_area"] == area) & event_perf["qualified_by"].isna()
                          & (event_perf["status"] == "OK") & event_perf["place"].notna()].sort_values("place")
        next_places = set(line["place"].iloc[:len(vac)])
        subs = sorted((r for r in enp if r["area"] == area and r["explained_by"] is None
                       and pd.notna(r["place"]) and r["place"] in next_places), key=lambda r: r["place"])
        for v, sub in zip(vac, subs):
            _mark_pair(v, sub, "same_area")


def _pair_fill_line(pne: list[dict], enp: list[dict], event_perf: pd.DataFrame, ties: bool) -> None:
    """Fill the event's vacancies with the next marks in the fill pool, any Area.
    Which vacancy each replacement is paired with is a convention (vacancies by auto /
    at-large / fill, then place; replacements by fill rank)."""
    if not pne:
        return
    cands = event_perf[event_perf["fill_candidate"] & event_perf["qualified_by"].isna()
                       & (event_perf["status"] == "OK")].sort_values("fill_rank")
    if cands.empty:
        return
    n = len(pne)
    cutoff = cands["fill_rank"].iloc[min(n, len(cands)) - 1]
    line = cands[cands["fill_rank"] <= cutoff] if ties else cands.iloc[:n]
    ids = set(line["identity"])
    subs = sorted((r for r in enp if r["explained_by"] is None and r["identity"] in ids),
                  key=lambda r: r["fill_rank"] if pd.notna(r["fill_rank"]) else 1e9)
    vac = sorted(pne, key=lambda r: (QUALIFIED_BY_ORDER.get(r["qualified_by"], 9),
                                     r["place"] if pd.notna(r["place"]) else 1e9))
    for v, sub in zip(vac, subs):
        _mark_pair(v, sub, "fill_line")


def score(comp: Comparison) -> dict:
    """RAW: every difference counts. RULES: only differences no overlay explains."""
    rows = comp.rows
    matched = int(rows["outcome"].isin(["match", "match_name_variant"]).sum())
    pne = int((rows["outcome"] == "predicted_not_entered").sum())
    enp = int((rows["outcome"] == "entered_not_predicted").sum())
    unexplained = rows[rows["outcome"].isin(["predicted_not_entered", "entered_not_predicted"])
                       & rows["explained_by"].isna()]
    s = dict(zip(comp.summary["outcome"], comp.summary["n"]))
    return {**s, "matched": matched, "raw_mismatches": pne + enp,
            "raw_match_rate": matched / (matched + pne + enp) if matched + pne + enp else None,
            "rules_mismatches": len(unexplained),
            "rules_match_rate": matched / (matched + len(unexplained)) if matched + len(unexplained) else None,
            "precision": matched / (matched + pne) if matched + pne else None,
            "recall": matched / (matched + enp) if matched + enp else None,
            "explained_by_choice": int(rows["explained_by"].isin(["chose_other_events", "did_not_declare"]).sum()),
            "explained_by_entry_limit": int((rows["explained_by"] == "entry_limit_assumed").sum()),
            "explained_by_replacement": int(rows["explained_by"].fillna("").str.startswith("replacement").sum())}


def rates(rows: pd.DataFrame, by) -> pd.DataFrame:
    """RAW and RULES match rates per group."""
    t = rows.assign(ok=rows["outcome"].isin(["match", "match_name_variant"]),
                    pne=rows["outcome"] == "predicted_not_entered",
                    enp=rows["outcome"] == "entered_not_predicted")
    t["unexplained"] = (t["pne"] | t["enp"]) & t["explained_by"].isna()
    g = t.groupby(by)[["ok", "pne", "enp", "unexplained"]].sum().astype(int)
    g["raw_match_rate"] = (g["ok"] / (g["ok"] + g["pne"] + g["enp"])).round(3)
    g["rules_match_rate"] = (g["ok"] / (g["ok"] + g["unexplained"])).round(3)
    return g.rename(columns={"ok": "matched", "pne": "predicted_not_entered", "enp": "entered_not_predicted",
                             "unexplained": "rules_mismatches"})


def sweep(results: pd.DataFrame, rules: dict, entries: pd.DataFrame, interps: list[Interpretation],
          legs: pd.DataFrame | None = None, **compare_kw) -> pd.DataFrame:
    """Score each interpretation. Predictions depend only on the rule switches, so each rule
    reading is evaluated once and every overlay is applied to it."""
    rows, cache = [], {}
    rule_keys = list(RULE_AXES)
    for interp in interps:
        rk = tuple(getattr(interp, k) for k in rule_keys)
        if rk not in cache:
            ev = evaluate(results, rules, interp)
            pred = ev[ev["qualified_by"].notna()]
            cache[rk] = (ev, frozenset(zip(pred["performance_id"], pred["qualified_by"])))
        ev, pset = cache[rk]
        comp = compare(ev, entries, rules, interp=interp, legs=legs, **compare_kw)
        rows.append({"interpretation": interp.name, **asdict(interp), **score(comp), "predicted_set": pset})
    df = pd.DataFrame(rows)
    return df.sort_values(["raw_mismatches", "rules_mismatches", "interpretation"]).reset_index(drop=True)


def best_reading(table: pd.DataFrame, grid: list[Interpretation]) -> tuple[Interpretation, Interpretation]:
    """(best rule reading with overlays off, same reading with its best overlays)."""
    off = table[(table["replacement"] == "off") & (table["entry_limit"] == 0)].sort_values(["raw_mismatches", "interpretation"])
    rule = next(i for i in grid if i.name == off.iloc[0]["interpretation"])
    same = table
    for k in RULE_AXES:
        same = same[same[k] == getattr(rule, k)]
    over = same.sort_values(["rules_mismatches", "interpretation"]).iloc[0]
    return rule, next(i for i in grid if i.name == over["interpretation"])


def switch_effects(table: pd.DataFrame, axes: dict, metric: str = "raw_mismatches",
                   hold_fixed: dict | None = None) -> pd.DataFrame:
    """For each switch in `axes`: across sets of readings that differ only in that switch
    (every switch in `hold_fixed`, default `axes`, held fixed), how often the predicted list
    changes and how `metric` moves from the first value to the last."""
    out = []
    fixed = hold_fixed or axes
    for k, values in axes.items():
        others = [a for a in fixed if a != k]
        changed = n = 0
        deltas = []
        for _, grp in table.groupby(others):
            if len(grp) != len(values):
                continue
            n += 1
            sets = grp.set_index(k)["predicted_set"]
            mism = grp.set_index(k)[metric]
            changed += int(len(set(sets)) > 1)
            deltas.append(int(mism[values[-1]] - mism[values[0]]))
        out.append({"switch": k, "values": f"{values[0]} -> {values[-1]}", "metric": metric, "pairs": n,
                    "predicted_list_changes_in": changed,
                    "delta_min": min(deltas), "delta_max": max(deltas)})
    return pd.DataFrame(out)
