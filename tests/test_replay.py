"""Replay on hand-built fixtures. Every expected entrant below is worked out by hand.

Girls 100 m, at-large standard 12.45 (2026 table). Non-auto marks, best first:

  TV7 12.30  BS7 12.35  TV8 12.40  RE7 12.44  CA4 12.44  BS8 12.46  CA5 12.47  TV9 12.50 ...

Auto: top 6 at Tri-Valley, Bay Shore and Redwood Empire, top 3 at Class A = 21.
"""

import pandas as pd
import pytest

from ncs_track import paths
from ncs_track.replay import (DEFAULT_GRID, Interpretation, _in_program, compare, pass_down, evaluate, interpretation_grid,
                              predict, rates, score, sweep, switch_effects)
from ncs_track.rules import load_rules

AREA_CODE = {"TV": "tri-valley", "BS": "bay-shore", "RE": "redwood-empire", "CA": "class-a"}

MARKS = {
    "TV": [12.00, 12.05, 12.10, 12.15, 12.20, 12.25, 12.30, 12.40, 12.50, 12.60],
    "BS": [12.02, 12.06, 12.11, 12.16, 12.21, 12.26, 12.35, 12.46],
    "RE": [12.03, 12.07, 12.12, 12.17, 12.22, 12.27, 12.44, 12.70],
    "CA": [12.20, 12.30, 12.40, 12.44, 12.47, 12.60, 12.61],
}


@pytest.fixture(scope="module")
def rules():
    return load_rules(paths.rules_path(2026))


def perf(area, place, mark, *, event="100", gender="girls", status="OK", wind_aided=False,
         relay=False, name=None, school=None):
    return {
        "performance_id": f"{area}{place}{event}", "meet_key": f"2026-area-{AREA_CODE[area]}",
        "season": 2026, "level": "area", "meet_area": AREA_CODE[area], "gender": gender,
        "event_code": event, "in_scope": True, "round": "final",
        "place": place if status == "OK" else None, "status": status,
        "mark_raw": f"{mark:.2f}" if mark else status, "mark_value": mark if status == "OK" else None,
        "wind_aided": wind_aided, "is_relay": relay,
        "athlete_name_raw": None if relay else (name or f"{area}{place}, Runner"),
        "school_name_raw": school or f"{area} School {place}",
        "athlete_id": None if relay else f"id-{name or f'{area}{place}'}",
    }


def results(extra=()):
    rows = [perf(a, i + 1, m) for a, ms in MARKS.items() for i, m in enumerate(ms)]
    return pd.DataFrame(rows + list(extra))


def who(df, how=None):
    d = df if how is None else df[df["qualified_by"] == how]
    return sorted(n.split(",")[0] for n in d["athlete_name_raw"])


AUTO = sorted([f"{a}{i}" for a in ("TV", "BS", "RE") for i in range(1, 7)] + ["CA1", "CA2", "CA3"])


def test_default_reading_class_a_from_4th_fill_first(rules):
    p = predict(results(), rules, Interpretation())
    assert who(p, "auto") == AUTO
    assert who(p, "fill") == ["BS7", "TV7", "TV8"]
    assert who(p, "at_large") == ["CA4", "RE7"]
    assert len(p) == 26


def test_class_a_from_7th_drops_class_a_4th(rules):
    p = predict(results(), rules, Interpretation(class_a_at_large_outside_top=6))
    assert who(p, "at_large") == ["RE7"]
    assert "CA4" not in who(p)
    assert len(p) == 25


def test_at_large_before_fill_adds_three(rules):
    p = predict(results(), rules, Interpretation(fill_before_at_large=False))
    assert who(p, "at_large") == ["BS7", "CA4", "RE7", "TV7", "TV8"]
    assert who(p, "fill") == ["BS8", "CA5", "TV9"]
    assert len(p) == 29


def test_both_switches(rules):
    p = predict(results(), rules, Interpretation(class_a_at_large_outside_top=6, fill_before_at_large=False))
    assert who(p, "at_large") == ["BS7", "RE7", "TV7", "TV8"]
    assert who(p, "fill") == ["BS8", "CA4", "CA5"]      # CA4 still reaches MOC, as fill


def test_nbl_flyer_fill_excludes_class_a(rules):
    p = predict(results(), rules, Interpretation(fill_source="nbl_flyer"))
    assert who(p, "fill") == ["BS7", "BS8", "RE7", "TV7", "TV8", "TV9"]
    assert who(p, "at_large") == ["CA4"]


def test_fill_ties(rules):
    tie = [perf("BS", 9, 12.40, name="BSX, Tie")]           # ties TV8 for the 3rd fill spot
    incl = predict(results(tie), rules, Interpretation())
    assert who(incl, "fill") == ["BS7", "BSX", "TV7", "TV8"]
    excl = predict(results(tie), rules, Interpretation(fill_ties_include=False))
    assert who(excl, "fill") == ["BS7", "TV7"]
    # Tied athletes left out of fill still meet the standard, so they come in at-large.
    assert {"BSX", "TV8"} <= set(who(excl, "at_large"))


def test_dq_and_wind(rules):
    extra = [perf("TV", None, None, status="DQ", name="TVDQ, Runner")]
    df = results(extra)
    df.loc[df["athlete_name_raw"] == "RE7, Runner", "wind_aided"] = True
    ev = evaluate(df, rules, Interpretation(wind_aided_at_large=False))
    assert ev.loc[ev["athlete_name_raw"] == "TVDQ, Runner", "qualified_by"].isna().all()
    assert who(ev[ev["qualified_by"] == "at_large"]) == ["CA4"]
    assert "RE7" not in who(ev[ev["qualified_by"].notna()])


def test_non_final_rounds_and_other_levels_ignored(rules):
    df = results([{**perf("TV", 1, 11.00, name="Prelim, Only"), "round": "prelim"},
                  {**perf("TV", 1, 11.00, name="League, Only"), "level": "league"}])
    assert "Prelim" not in who(predict(df, rules)) and "League" not in who(predict(df, rules))


def test_relays(rules):
    rel = [perf("TV", i, 48.0 + i, event="4x100", relay=True, school=f"TV School {i}") for i in range(1, 9)]
    p = predict(pd.DataFrame(rel), rules)
    auto = p[p["qualified_by"] == "auto"]
    assert sorted(auto["school_name_raw"]) == [f"TV School {i}" for i in range(1, 7)]
    # TV7 (55.00) and TV8 (56.00) miss the 49.40 standard; as the only non-auto teams in
    # the pool they take two of the three fill spots.
    assert sorted(p.loc[p["qualified_by"] == "fill", "school_name_raw"]) == ["TV School 7", "TV School 8"]


# ---------------------------------------------------------------------------
# compare / sweep
# ---------------------------------------------------------------------------
def key(s):
    return s.lower().replace(" ", "-") if s else None


def area(s):
    if not s:
        return None
    return {"TV": "tri-valley", "BS": "bay-shore", "RE": "redwood-empire", "CA": "class-a"}.get(s[:2])


def entries_from(pred, drop=(), add=(), rename=None):
    rows = []
    for _, r in pred.iterrows():
        name = r["athlete_name_raw"]
        if name.split(",")[0] in drop:
            continue
        if rename and name.split(",")[0] in rename:
            name = rename[name.split(",")[0]]
        rows.append({"gender": r["gender"], "event_code": r["event_code"], "is_adaptive": False,
                     "event_modifier": None, "is_relay": False, "athlete_name": name,
                     "school_name": r["school_name_raw"], "seed_mark_raw": r["mark_raw"]})
    for name, school, mark in add:
        rows.append({"gender": "girls", "event_code": "100", "is_adaptive": False, "event_modifier": None,
                     "is_relay": False, "athlete_name": name, "school_name": school, "seed_mark_raw": mark})
    return pd.DataFrame(rows)


def test_compare_outcomes(rules):
    ev = evaluate(results(), rules)
    pred = ev[ev["qualified_by"].notna()]
    ent = entries_from(pred, drop={"TV8"}, rename={"BS7": "BS7, Runnerina"},
                       add=[("TV9, Runner", "TV School 9", "12.50"),
                            ("Nowhere, Kid", "Unknown High", "12.00")])
    comp = compare(ev, ent, rules, school_key=key, school_area=area)
    by = comp.rows.groupby("outcome")["athlete_name"].apply(sorted).to_dict()
    assert by["predicted_not_entered"] == ["TV8, Runner"]
    assert by["entered_not_predicted"] == ["TV9, Runner"]
    assert by["match_name_variant"] == ["BS7, Runner"]
    tv9 = comp.rows[comp.rows["athlete_name"] == "TV9, Runner"].iloc[0]
    assert tv9["reason"] == "below_standard_not_fill"
    assert "tri-valley place 9" in tv9["detail"] and "fill rank 8" in tv9["detail"]
    s = score(comp)
    assert s["match"] == 24 and s["match_name_variant"] == 1 and s["not_comparable_area_unknown"] == 1
    assert comp.notes == []                                   # all four Areas present


def test_compare_skips_areas_without_results(rules):
    only_tv = results()[lambda d: d["meet_area"] == "tri-valley"]
    ev = evaluate(only_tv, rules)
    full = evaluate(results(), rules)
    ent = entries_from(full[full["qualified_by"].notna()])
    comp = compare(ev, ent, rules, school_key=key, school_area=area)
    s = score(comp)
    assert s["not_comparable_area_missing"] == len(ent) - len(ent[ent["school_name"].str.startswith("TV")])
    assert any("fill pool incomplete" in n for n in comp.notes)


def test_sweep_ranks_the_reading_that_reproduces_entries(rules):
    truth = predict(results(), rules, Interpretation(class_a_at_large_outside_top=6, fill_before_at_large=False))
    ent = entries_from(truth)
    grid = interpretation_grid(**DEFAULT_GRID)
    assert len(grid) == 4
    table = sweep(results(), rules, ent, grid, school_key=key, school_area=area)
    best = table.iloc[0]
    assert best["interpretation"] == "class_a_at_large_outside_top=6;fill_before_at_large=False"
    assert best["raw_mismatches"] == 0 and best["precision"] == 1.0 and best["recall"] == 1.0
    assert (table["raw_mismatches"].iloc[1:] > 0).all()


def test_name_order_does_not_matter(rules):
    ev = evaluate(results(), rules)
    pred = ev[ev["qualified_by"].notna()]
    ent = entries_from(pred)
    ent["athlete_name"] = [" ".join(reversed(n.split(", "))) for n in ent["athlete_name"]]   # "Runner TV1"
    assert score(compare(ev, ent, rules, school_key=key, school_area=area))["raw_mismatches"] == 0


def test_replacement_same_area_pairs_next_in_line(rules):
    ev = evaluate(results(), rules)
    pred = ev[ev["qualified_by"].notna()]
    ent = entries_from(pred, drop={"TV3"}, add=[("TV9, Runner", "TV School 9", "12.50")])
    off = score(compare(ev, ent, rules, school_key=key, school_area=area))
    assert off["raw_mismatches"] == 2 and off["rules_mismatches"] == 1   # TV3: athlete choice; TV9: unexplained
    on = compare(ev, ent, rules, school_key=key, school_area=area, interp=Interpretation(replacement="same_area"))
    s = score(on)
    assert s["raw_mismatches"] == 2 and s["rules_mismatches"] == 0 and s["explained_by_replacement"] == 1
    tv3 = on.rows[on.rows["athlete_name"] == "TV3, Runner"].iloc[0]
    assert tv3["choice_tag"] == "did_not_declare" and tv3["vacancy_filled_by_area"] == "tri-valley"
    # TV10 is not next in line (TV9 is), so it stays unexplained.
    ent2 = entries_from(pred, drop={"TV3"}, add=[("TV10, Runner", "TV School 10", "12.60")])
    on2 = compare(ev, ent2, rules, school_key=key, school_area=area, interp=Interpretation(replacement="same_area"))
    assert score(on2)["rules_mismatches"] == 1


def test_replacement_fill_line_takes_next_mark_any_area(rules):
    ev = evaluate(results(), rules)
    pred = ev[ev["qualified_by"].notna()]
    # A Tri-Valley auto spot is vacated; the next fill mark after TV7/BS7/TV8 is RE7 or
    # CA4 (both 12.44), but they are at-large already, so the line continues: BS8 12.46.
    ent = entries_from(pred, drop={"TV3"}, add=[("BS8, Runner", "BS School 8", "12.46")])
    same = score(compare(ev, ent, rules, school_key=key, school_area=area, interp=Interpretation(replacement="same_area")))
    line = compare(ev, ent, rules, school_key=key, school_area=area, interp=Interpretation(replacement="fill_line"))
    assert same["rules_mismatches"] == 1 and score(line)["rules_mismatches"] == 0
    bs8 = line.rows[line.rows["athlete_name"] == "BS8, Runner"].iloc[0]
    assert bs8["explained_by"] == "replacement_fill_line" and bs8["fills_vacancy_of_area"] == "tri-valley"


def test_choice_tags_and_entry_limit(rules):
    ev = evaluate(results(), rules)
    pred = ev[ev["qualified_by"].notna()]
    ent = entries_from(pred, drop={"TV1"})
    other = ent.iloc[[0]].assign(event_code="200", athlete_name="TV2, Runner", school_name="TV School 2")
    ent = pd.concat([ent[ent["athlete_name"] != "TV2, Runner"], other])       # TV2 entered the 200 instead
    comp = compare(ev, ent, rules, school_key=key, school_area=area)
    pne = comp.rows[comp.rows["outcome"] == "predicted_not_entered"]
    tags = pne.set_index("athlete_name")["choice_tag"]
    assert tags["TV1, Runner"] == "did_not_declare" and tags["TV2, Runner"] == "chose_other_events"
    ev2 = ev.assign(athlete_id=ev["athlete_name_raw"])
    many = pd.concat([ev2.assign(event_code=c) for c in ("100", "200", "400", "800", "1600")])
    lim = compare(many, ent, rules, school_key=key, school_area=area, interp=Interpretation(entry_limit=4))
    assert (lim.rows.loc[lim.rows["athlete_name"] == "TV1, Runner", "explained_by"] == "entry_limit_assumed").all()


def test_rates_and_switch_effects(rules):
    truth = predict(results(), rules, Interpretation())
    ent = entries_from(truth)
    axes = dict(class_a_at_large_outside_top=[3, 6], wind_aided_at_large=[True, False])
    table = sweep(results(), rules, ent, interpretation_grid(**axes), school_key=key, school_area=area)
    eff = switch_effects(table, axes).set_index("switch")
    assert eff.loc["class_a_at_large_outside_top", "predicted_list_changes_in"] == 2
    assert eff.loc["wind_aided_at_large", "predicted_list_changes_in"] == 0     # no wind-aided marks
    comp = compare(evaluate(results(), rules), ent, rules, school_key=key, school_area=area)
    r = rates(comp.rows, "area")
    assert (r["raw_match_rate"] == 1.0).all() and set(r.index) == set(AREA_CODE.values())


def test_in_program_accepts_one_letter_spellings_only():
    declared = {("boys", "jonas renwick|foothill"), ("boys", "relay|foothill"), ("girls", "mara renwik|foothill")}
    assert _in_program("boys", "jonas renwick|foothill", declared)
    assert _in_program("boys", "jonas renwik|foothill", declared)          # program spells it without the c
    assert not _in_program("boys", "jonas renwik|granada", declared)       # other school
    assert not _in_program("boys", "renwick tobias|foothill", declared)    # sibling, same school
    assert not _in_program("boys", "mara renwik|foothill", declared)       # other gender


def _routes(rules, ent, res=None):
    ev = evaluate(res if res is not None else results(), rules)
    routes, comp = pass_down(ev, ent, rules, school_key=key, school_area=area)
    r = routes[routes["meet_area"].notna()].copy()
    r["who"] = r["athlete_name"].str.split(",").str[0]
    return r.set_index("who"), comp


def test_pass_down_moves_declined_spots_down_the_area(rules):
    ev = evaluate(results(), rules)
    pred = ev[ev["qualified_by"].notna()]
    # TV2 and TV3 decline; TV7 and TV8 (fill before) become automatic; TV9 enters too.
    ent = entries_from(pred, drop={"TV2", "TV3"}, add=[("TV9, Runner", "TV School 9", "12.50")])
    r, comp = _routes(rules, ent)
    auto = sorted(r.index[r["route"] == "auto"])
    assert auto == sorted(["TV1", "TV4", "TV5", "TV6", "TV7", "TV8"] + [f"{a}{i}" for a in ("BS", "RE") for i in range(1, 7)]
                          + ["CA1", "CA2", "CA3"])
    assert sorted(r.index[r["declined"] == "auto"]) == ["TV2", "TV3"]
    # next best mark after declarations: BS7 12.35, then RE7 and CA4 tied at 12.44 (ties in)
    assert sorted(r.index[r["route"] == "fill"]) == ["BS7", "CA4", "RE7"]
    assert r.loc["TV9", "declared"] and r.loc["TV9", "route"] is None          # no route: unexplained
    assert not r.loc["TV9", "left_out"]
    assert r.loc["TV10", "left_out"] and r.loc["CA5", "left_out"] and not r.loc["TV2", "left_out"]
    s = score(comp)
    assert s["matched"] == 24 and s["rules_mismatches"] == 1


def test_pass_down_next_best_mark_decline_passes_on(rules):
    ev = evaluate(results(), rules)
    pred = ev[ev["qualified_by"].notna()]
    ent = entries_from(pred, drop={"BS7"})
    r, _ = _routes(rules, ent)
    # TV7 12.30 takes one, BS7 12.35 isn't in the program, TV8 12.40, then RE7 / CA4 tied at 12.44
    assert sorted(r.index[r["route"] == "fill"]) == ["CA4", "RE7", "TV7", "TV8"]
    assert r.loc["BS7", "declined"] == "fill"            # a better mark than a taker, not in the program
    assert r.loc["BS8", "declined"] is None              # behind every taker: not a decline


def test_pass_down_ties_at_the_last_automatic_place(rules):
    extra = [perf("CA", 3, 12.39, name="CA3b, Runner", school="CA School 3b")]
    res = results(extra)
    ev = evaluate(res, rules)
    pred = ev[ev["qualified_by"].notna()]
    r, _ = _routes(rules, entries_from(pred), res)
    assert r.loc["CA3", "route"] == "auto" and r.loc["CA3b", "route"] == "auto"
