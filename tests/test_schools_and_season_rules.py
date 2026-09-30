import pandas as pd
import pytest
import yaml

from ncs_track import paths, schools, season_rules
from ncs_track.rules import check_rules, load_rules

CANON = """List,Order,School
Tri-Valley,1,California (San Ramon)
Tri-Valley,2,De La Salle
Tri-Valley,3,Foothill (Pleasanton)
Tri-Valley,4,San Ramon Valley
Class A,1,California - Fremont
Class A,2,Bay School of San Francisco
Bayshore,1,St Mary's College
Bayshore,2,John F. Kennedy (Fremont)
Bayshore,3,John F. Kennedy (Richmond)
Redwood Empire,1,Analy
"""


@pytest.fixture
def canon(tmp_path):
    p = tmp_path / "list.csv"
    p.write_text(CANON)
    return schools.load_canonical(p)


def spell(raw, area=""):
    return {"raw": raw, "source": "hytek", "source_file": "f", "meet_key": "k", "meet_area": area}


def test_matching_rules(canon):
    sp = pd.DataFrame([spell("San Ramon Va"), spell("DeLaSalle"), spell("Foothill (Nc)"),
                       spell("St. Mary's"), spell("California", "tri-valley"), spell("California"),
                       spell("California S"), spell("John F. Kenn", "bay-shore"), spell("West County"),
                       spell("Bay School o")])
    matched, review = schools.match_spellings(sp, canon)
    got = dict(zip(matched["raw"], matched["school_key"]))
    assert got == {"San Ramon Va": "san-ramon-valley", "DeLaSalle": "de-la-salle",
                   "Foothill (Nc)": "foothill-pleasanton", "St. Mary's": "st-mary-college",
                   "California": "california-san-ramon"}
    methods = dict(zip(matched["raw"], matched["method"]))
    assert methods["California"] == "base+area" and methods["San Ramon Va"] == "prefix"
    rv = review.set_index("raw")
    assert set(rv.index) == {"California S", "John F. Kenn", "West County", "Bay School o"}
    assert "one-letter" in rv.loc["California S", "reason"]
    assert rv.loc["John F. Kenn", "reason"].startswith("ambiguous")
    assert "Analy" in rv.loc["West County", "hint"]          # hint only, never merged


def test_seen_elsewhere_goes_to_review(canon):
    # Same raw string seen at two Area meets: area narrowing can't pick, so review.
    sp = pd.DataFrame([spell("California", "tri-valley"), spell("California", "class-a")])
    matched, review = schools.match_spellings(sp, canon)
    assert matched.empty and list(review["raw"]) == ["California"]


def test_hytek_school_strings():
    text = """
    Name                    Year School                  Finals        Wind H#
==============================================================================
  1 Quenby, Rosalind Mae      10 Pittsburg                12.01 NCS     2.2  3  12.004
 --  Benicia, Kid             11 Benicia                  X20.72  -0.4
    School                                               Finals                  H#
  1 Pittsburg (Nc)  'A'                                   46.71RNCS               3
     1) Arkwright, Delphine 11              2) Pellham, Soraya 10
  2 Castro Valle                                          DQ
"""
    assert schools.hytek_school_strings(text) == ["Pittsburg", "Benicia", "Pittsburg (Nc)  'A'", "Castro Valle"]
    assert schools.clean_raw("Pittsburg (Nc)  'A'") == "Pittsburg"
    assert schools.clean_raw("California C") == "California C"


def test_alias_table_has_every_season(canon):
    matched = pd.DataFrame([{"raw": "DeLaSalle", "school_key": "de-la-salle"}])
    t = schools.alias_table(canon, matched).set_index("school_key")
    assert t.loc["de-la-salle", "spellings"] == "DeLaSalle"
    assert {f"area_{s}" for s in schools.SEASONS} <= set(t.columns)
    assert t.loc["analy", "area_2019"] == "redwood-empire" and t.loc["analy", "athleticnet_school_id"] == ""


def test_printed_standards():
    text = """Girls 100 Meter Dash Varsity
=====
      NCS TV: R 11.76  5/20/2017   Mikayla Scott, Carondelet
                12.55  NCS At-Large
Girls 100 Meter Dash Unified
                30.00  NCS At-Large
Event 5  Boys High Jump Varsity
               6-02.00  NCS At-Large
"""
    assert season_rules.printed_standards(text) == {"girls": {"100": "12.55"}, "boys": {"HJ": "6-02.00"}}


def test_generated_season_files(tmp_path):
    base = yaml.safe_load(paths.rules_path(2026).read_text())
    for season in season_rules.SEASONS:
        r = load_rules(paths.rules_path(season))
        assert check_rules(r) == []
        std = r["area_to_moc"]["at_large"]["standards"]
        assert all(isinstance(v, dict) and v["source"] for g in std.values() for v in g.values())
        assert r["area_to_moc"]["auto"] == base["area_to_moc"]["auto"]
        assert r["provenance"]["area_to_moc.auto"] == "assumed from 2026"
    r19 = load_rules(paths.rules_path(2019))["area_to_moc"]["at_large"]["standards"]
    assert r19["girls"]["100"] == {"mark": "12.55",
                                   "source": "data/raw/hytek/2019-area-tri-valley.htm (printed in results)"}
    assert r19["girls"]["4x800"]["source"].startswith("assumed from 2026 — not printed")
    r23 = load_rules(paths.rules_path(2023))["area_to_moc"]["at_large"]["standards"]
    assert r23["girls"]["100"] == {"mark": "12.45", "source": "assumed from 2026 — no printed source"}


def test_generated_files_are_current():
    base = yaml.safe_load(paths.rules_path(2026).read_text())
    for season in season_rules.SEASONS:
        on_disk = yaml.safe_load(paths.rules_path(season).read_text())
        assert on_disk == season_rules.season_rules(season, base, paths.RAW_HYTEK), season
