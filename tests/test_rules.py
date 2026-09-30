import copy
import html
import re

import pytest

from ncs_track import paths
from ncs_track.events import parse_event
from ncs_track.marks import parse_mark
from ncs_track.rules import check_rules, load_rules, load_rules_for, standard


@pytest.fixture(scope="module")
def rules():
    return load_rules(paths.rules_path(2026))


def test_loads_clean(rules):
    assert check_rules(rules) == []
    assert rules["applied_label"] == "2026 rules applied"


def test_fallback_label():
    rules, label = load_rules_for(2021)                 # no 2021 file -> latest
    assert rules["season"] == 2026 and label == "2026 rules applied"


def test_season_file_used_when_present():
    rules, label = load_rules_for(2019)
    assert rules["season"] == 2019 and "printed in 2019 results" in label


def test_every_standard_present(rules):
    for table in (rules["area_to_moc"]["at_large"]["standards"],
                  rules["league_to_area"]["class-a"]["at_large"]["standards"]):
        for gender in ("girls", "boys"):
            expected = set(rules["events"]["main_simulation"][gender]) | {"4x800"}
            assert set(table[gender]) == expected, gender


def test_spot_numbers(rules):
    moc = rules["area_to_moc"]
    assert moc["auto"] == {"tri-valley": 6, "redwood-empire": 6, "bay-shore": 6, "class-a": 3}
    assert moc["fill"]["moc_guide"]["count"] == 3 and moc["fill"]["nbl_flyer"]["count"] == 6
    assert moc["fill"]["authoritative"] == "moc_guide" and moc["field_min"] == 24
    re_fill = rules["league_to_area"]["redwood-empire"]["fill"]
    assert (re_fill["min"], re_fill["max"], re_fill["nbl_flyer"]) == (6, 10, 10)
    assert rules["league_to_area"]["tri-valley"]["auto"] == {"BVAL": 4, "DAL": 6, "EBAL": 6}
    assert rules["league_to_area"]["bay-shore"]["auto"] == {"MVAL": 4, "TCAL": 6, "WACC": 6}
    assert rules["relay_4x800"]["area_entries"]["max_per_meet"] == 16


def test_discrepancies_explicit(rules):
    assert set(rules["discrepancies"]) >= {f"D{i}" for i in range(1, 10)}
    assert rules["wind"]["required_for_qualifying"] is None
    assert rules["moc_to_state"]["at_large"]["standards_table"]["inference"] is True


def test_standard_lookup(rules):
    g100 = standard(rules, "area_to_moc", "girls", "100")
    assert g100.value == pytest.approx(12.45)
    ghj = standard(rules, "area_to_moc", "girls", "HJ")
    assert ghj.value == pytest.approx(5 * 0.3048)
    assert standard(rules, "area_to_moc", "girls", "110H") is None


def test_matches_hytek_2026_tri_valley(rules):
    """2026 Tri-Valley results print the NCS at-large standards; they must equal the YAML."""
    text = open(paths.RAW_HYTEK / "2026-area-tri-valley.htm", encoding="latin-1").read()
    text = html.unescape(re.sub(r"<[^>]+>", "", text)).replace("\r", "")
    lines = text.split("\n")
    printed = {}
    event = None
    for i, line in enumerate(lines):
        m = re.match(r"^(?:Event\s+\d+\s+)?(Girls|Boys)\s+(.+?)\s*$", line)
        if m and i + 1 < len(lines) and lines[i + 1].startswith("==="):
            ev = parse_event(m.group(2))
            event = None if ev.is_adaptive else (m.group(1).lower(), ev.code, ev.measure)
            continue
        m = re.match(r"^\s+(\S+)\s+NCS At-Large", line)
        if m and event:
            printed[event[:2]] = parse_mark(m.group(1), event[2]).value
    assert len(printed) == 34
    for (gender, code), value in printed.items():
        assert standard(rules, "area_to_moc", gender, code).value == pytest.approx(value), (gender, code)


def test_check_catches_problems(rules):
    bad = copy.deepcopy(rules)
    bad["area_to_moc"]["at_large"]["standards"]["girls"]["100"] = "12.4x"
    bad["area_to_moc"]["auto"]["class-a"] = 4
    bad["league_to_area"]["tri-valley"]["at_large"]["discrepancy"] = "D99"
    problems = " | ".join(check_rules(bad))
    assert "girls 100" in problems
    assert "field_min" in problems
    assert "D99" in problems
