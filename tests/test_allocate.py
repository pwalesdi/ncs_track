"""Allocation engine: current.yaml must reproduce the validated replay exactly."""

import pandas as pd
import pytest

from ncs_track import allocate, analysis, paths, replay
from ncs_track.rules import load_rules

CURRENT = paths.ROOT / "configs" / "allocation" / "current.yaml"


@pytest.fixture(scope="module")
def cfg():
    return allocate.load_config(CURRENT)


def test_current_config_matches_best_reading(cfg):
    r = analysis.BEST_READING
    assert cfg.auto_spots == {"tri-valley": 6, "bay-shore": 6, "redwood-empire": 6, "class-a": 3}
    assert (cfg.fill_count, set(cfg.fill_pool)) == (3, set(replay.AREAS))
    assert cfg.fill_order == ("before_at_large" if r.fill_before_at_large else "after_at_large")
    assert cfg.fill_ties == ("include" if r.fill_ties_include else "exclude")
    assert cfg.at_large_outside_top["class-a"] == r.class_a_at_large_outside_top
    assert cfg.wind_aided_allowed == r.wind_aided_at_large and cfg.replacement == r.replacement
    rules = load_rules(paths.rules_path(2026))
    assert cfg.auto_spots == rules["area_to_moc"]["auto"]
    assert cfg.fill_count == rules["area_to_moc"]["fill"]["moc_guide"]["count"]


def test_config_validation(tmp_path):
    bad = CURRENT.read_text().replace("order: before_at_large", "order: sometimes")
    p = tmp_path / "bad.yaml"
    p.write_text(bad)
    with pytest.raises(allocate.ConfigError, match="fill.order"):
        allocate.load_config(p)
    p.write_text(CURRENT.read_text().replace("  class-a: 3\nfill:", "fill:"))
    with pytest.raises(allocate.ConfigError, match="auto_spots"):
        allocate.load_config(p)


def _real_data():
    return (paths.PROCESSED / "performances.csv").exists() and (paths.PROCESSED / "moc_entries.csv").exists()


@pytest.mark.skipif(not _real_data(), reason="needs rebuilt data/processed (see README, Data)")
@pytest.mark.parametrize("season", [2022, 2023, 2024, 2025, 2026])
def test_engine_reproduces_validated_replay(season, cfg):
    from ncs_track.cli import replay_inputs
    results, entries, rules, _, kw, legs = replay_inputs(season)
    expected = replay.evaluate(results, rules, analysis.BEST_READING)
    got = allocate.allocate(results, rules, cfg)
    cols = [c for c in replay.EVAL_COLUMNS if c != "interpretation"]
    pd.testing.assert_frame_equal(got[cols].reset_index(drop=True), expected[cols].reset_index(drop=True))
    a = replay.score(allocate.compare(got, entries, rules, cfg, legs=legs, **kw))
    b = replay.score(replay.compare(expected, entries, rules, interp=analysis.BEST_READING, legs=legs, **kw))
    assert a == b


def test_engine_modes_on_fixture():
    """Mechanics only, on the replay test fixture: no real data, no alternative allocations."""
    from tests.test_replay import results
    rules = load_rules(paths.rules_path(2026))
    base = allocate.load_config(CURRENT)
    same = allocate.allocate(results(), rules, base)
    assert same["qualified_by"].tolist() == replay.evaluate(results(), rules, analysis.BEST_READING)["qualified_by"].tolist()
    off = allocate.allocate(results(), rules, allocate.AllocationConfig(**{**base.__dict__, "at_large_mode": "off"}))
    assert "at_large" not in set(off["qualified_by"].dropna())
    std = allocate.standard_value(allocate.AllocationConfig(**{**base.__dict__, "at_large_mode": "adjusted",
                                                               "at_large_adjust_pct": 1.0}), rules, "girls", "100")
    assert std == pytest.approx(12.45 * 0.99)
