import pytest

from ncs_track.events import parse_event, parse_gender, parse_round
from ncs_track.names import grad_year, name_key, split_name


@pytest.mark.parametrize("raw, code", [
    # Hy-Tek event titles
    ("Girls 100 Meter Dash Varsity", "100"),
    ("Girls 100 Meter Hurdles Varsity", "100H"),
    ("Boys 110 Meter Hurdles Varsity", "110H"),
    ("Boys 300 Meter Hurdles Varsity", "300H"),
    ("Girls 4x100 Meter Relay Varsity", "4x100"),
    ("Boys 4x800 Meter Relay Varsity", "4x800"),
    ("Girls 1600 Meter Run Varsity", "1600"),
    ("Boys 3200 Meter Run Varsity", "3200"),
    ("Girls Discus Throw Varsity", "DT"),
    # Athletic.net-style labels
    ("100 Meters", "100"),
    ("110m Hurdles - 39\"", "110H"),
    ("300m Hurdles - 30\"", "300H"),
    ("4x400 Relay", "4x400"),
    ("4 x 100 Relay", "4x100"),
    ("Shot Put - 4kg", "SP"),
    ("Discus - 1.6kg", "DT"),
    ("Pole Vault", "PV"),
    ("800m", "800"),
])
def test_event_codes(raw, code):
    ev = parse_event(raw)
    assert ev.code == code
    assert not ev.is_adaptive and ev.modifier is None


def test_event_flags():
    assert parse_event("4x100 Relay").is_relay
    assert parse_event("Long Jump").wind_event and parse_event("Long Jump").measure == "distance"
    assert not parse_event("400 Meters").wind_event
    assert parse_event("Girls 100 Meter Dash Unified").is_adaptive
    assert parse_event("100 Meters", "Unified").is_adaptive
    assert parse_event("Boys 200 Meter Dash Ambulatory").is_adaptive
    assert parse_event("Girls 4x800 Meter Relay Exhibition Varsity").modifier == "exhibition"
    assert parse_event("Girls 300 Meter Hurdles Heat 1 Rerun Varsity").modifier == "rerun"
    rerun = parse_event("Boys High Jump Jump Off Varsity")
    assert rerun.code == "HJ" and rerun.modifier == "jump_off"
    assert parse_event("Javelin").code is None


@pytest.mark.parametrize("raw, gender", [
    ("F", "girls"), ("M", "boys"), ("Girls", "girls"), ("Boys", "boys"),
    ("Women", "girls"), ("Men", "boys"), ("x", None), ("", None),
])
def test_gender(raw, gender):
    assert parse_gender(raw) == gender


@pytest.mark.parametrize("raw, rnd", [
    ("Finals", "final"), ("Final", "final"), ("Timed Finals", "final"), ("F", "final"),
    ("Prelims", "prelim"), ("Preliminaries", "prelim"), ("Trials", "prelim"),
    ("Semi-Finals", "semi"), ("", "unknown"), ("Round 2", "unknown"),
])
def test_round(raw, rnd):
    assert parse_round(raw) == rnd


def test_names():
    assert name_key("Quenby, Rosalind Mae") == name_key("Rosalind Mae Quenby") == "quenby|rosalind mae"
    assert name_key("O'Brannagh, Tesslyn") == "obrannagh|tesslyn"
    assert name_key("Corrie' Vantassel") == "vantassel|corrie"
    assert split_name("Quenby, Rosalind (Mae)") == ("Quenby", "Rosalind", "Mae")
    assert name_key("José Núñez") == "nunez|jose"
    assert grad_year(2024, 12) == 2024 and grad_year(2024, 9) == 2027 and grad_year(2024, None) is None
