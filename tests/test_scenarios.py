"""Scenario engine: 'current' must reproduce the validated pass-down exactly."""

import pandas as pd
import pytest

from ncs_track import allocate, paths, scenarios
from ncs_track.replay import evaluate, pass_down
from ncs_track.rules import load_rules
from tests.test_replay import area, entries_from, key, results


@pytest.fixture(scope="module")
def rules():
    return load_rules(paths.rules_path(2026))


def _routes(rules, drop=()):
    ev = evaluate(results(), rules)
    pred = ev[ev["qualified_by"].notna()]
    routes, _ = pass_down(ev, entries_from(pred, drop=set(drop)), rules, school_key=key, school_area=area)
    return routes


def _sim(routes, name):
    s = scenarios.simulate(routes, scenarios.load(name))
    s["who"] = s["athlete_name"].str.split(",").str[0]
    return s.set_index("who")


def test_configs_keep_a_field_of_24():
    for name in scenarios.SCENARIOS:
        cfg = scenarios.load(name)
        a = cfg.auto_spots
        assert a["tri-valley"] == a["bay-shore"] == a["redwood-empire"] and a["class-a"] == 3
        assert sum(a.values()) + cfg.fill_count == 24


def test_current_reproduces_pass_down(rules):
    routes = _routes(rules, drop={"TV2", "BS7"})              # a declined automatic and a declined fill spot
    s = _sim(routes, "current")
    assert (s["in_field"] == s["real_in"]).all() and not s["added"].any() and not s["removed"].any()
    real = routes[routes["meet_area"].notna()].assign(who=lambda d: d["athlete_name"].str.split(",").str[0]).set_index("who")
    assert (s["left_out"] == real["left_out"].reindex(s.index)).all()


def test_fewer_automatic_spots_move_places_to_next_best_mark(rules):
    s = _sim(_routes(rules, drop={"TV2"}), "c_3333")
    # 3 automatic spots per Area: TV2 declined, so TV1, TV3, TV4; the 12 next-best-mark spots
    # go down the remaining marks; TV2 declines again (real declines are kept)
    assert sorted(s.index[s["route"] == "automatic"]) == sorted(
        ["TV1", "TV3", "TV4", "BS1", "BS2", "BS3", "RE1", "RE2", "RE3", "CA1", "CA2", "CA3"])
    assert s.loc["TV6", "route"] == "next_best_mark" and pd.isna(s.loc["TV2", "route"])
    assert (s["route"] == "next_best_mark").sum() == 13        # RE7 and CA4 tie at the 12th spot (12.44): both in
    assert not (s["left_out"] & s["beats_a_next_best_mark"]).any()


OUT = paths.OUTPUTS / "scenario_athletes.csv"


@pytest.mark.skipif(not OUT.exists(), reason="needs outputs/scenario_athletes.csv (run analysis + scenarios)")
def test_real_seasons_current_matches_validated_and_no_left_out_beats_a_next_best_mark():
    r = pd.read_csv(OUT, low_memory=False)
    c = r[r["scenario"] == "current"]
    assert not c["added"].any() and not c["removed"].any()
    assert (c["route"].fillna("") == c["real_route"].fillna("")).all()
    lo = pd.read_csv(paths.OUTPUTS / "left_out.csv")
    assert c["left_out"].sum() == len(lo)
    assert ((c["left_out"]) & (c["beaten_other_area_autos"] > 0)).sum() == (lo["beaten_other_area_autos"] > 0).sum()
    assert not r["beats_a_next_best_mark"].any()             # every scenario
