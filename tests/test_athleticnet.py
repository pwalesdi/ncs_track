from pathlib import Path

import pandas as pd
import pytest

from ncs_track import athleticnet, paths, validate
from ncs_track.issues import errors
from ncs_track.rules import load_rules

FIX = Path(__file__).parent / "fixtures"
MOC = FIX / "2024_moc_520990.csv"
TV = FIX / "2024_tri-valley_523900.csv"


@pytest.fixture(scope="module")
def rules():
    return load_rules(paths.rules_path(2026))


@pytest.fixture(scope="module")
def meets():
    return athleticnet.load_meets()


@pytest.fixture(scope="module")
def moc(meets, rules):
    return athleticnet.ingest_file(MOC, meets, rules)


@pytest.fixture(scope="module")
def tv(meets, rules):
    return athleticnet.ingest_file(TV, meets, rules)


def row(perf, **kw):
    m = perf
    for k, v in kw.items():
        m = m[m[k] == v]
    assert len(m) == 1, f"{kw} matched {len(m)} rows"
    return m.iloc[0]


def test_meet_lookup(moc, tv):
    assert set(moc[0]["meet_key"]) == {"2024-moc"}
    assert set(tv[0]["meet_key"]) == {"2024-area-tri-valley"}
    assert set(tv[0]["meet_area"]) == {"tri-valley"}


def test_no_rows_dropped(moc, tv):
    assert len(moc[0]) == len(pd.read_csv(MOC)) == 22
    assert len(tv[0]) == len(pd.read_csv(TV)) == 7


def test_fixtures_have_no_errors(moc, tv, rules):
    for perf, legs, issues in (moc, tv):
        issues = issues + validate.run_all(perf, legs, rules)
        assert errors(issues) == [], errors(issues)


def test_rounds_kept_separate(moc):
    perf = moc[0]
    sprinter = perf[perf["athlete_id"] == "9000001"].set_index("round")
    assert sprinter.loc["prelim", "mark_value"] == pytest.approx(11.99)
    assert sprinter.loc["final", "mark_value"] == pytest.approx(12.05)
    assert sprinter.loc["prelim", "mark_flags"] == "Q"


def test_relays(moc):
    perf, legs, _ = moc
    pit = row(perf, event_code="4x100", round="prelim", school_id="99001")
    assert pit["mark_value"] == pytest.approx(47.20) and pit["mark_flags"] == "Q CIF"
    assert pd.isna(pit["athlete_id"]) and pit["is_relay"]
    assert legs.groupby("performance_id").size().eq(4).all()
    assert list(legs[legs["performance_id"] == pit["performance_id"]]["athlete_id"]) == \
        ["9000002", "9000005", "9000006", "9000004"]
    dub = row(perf, event_code="4x100", round="final", school_id="99003")
    assert dub["status"] == "DNF" and pd.isna(dub["place"]) and pd.isna(dub["mark_value"])


def test_statuses_and_ties(moc):
    perf = moc[0]
    assert row(perf, athlete_id="9000104")["status"] == "NH"
    assert row(perf, athlete_id="9000401")["status"] == "DQ"
    lahanas = perf[perf["athlete_id"] == "9000501"]
    assert set(lahanas["status"]) == {"FS", "OK"}
    tied = perf[(perf["event_code"] == "HJ") & (perf["place"] == 15)]
    assert len(tied) == 2 and set(tied["mark_flags"]) == {"J"}


def test_wind(moc, tv):
    fin = row(moc[0], athlete_id="9000001", round="final")
    assert fin["wind"] == pytest.approx(2.6) and fin["wind_aided"]          # 2.6 > 2.0, flagged not dropped
    pre = row(moc[0], athlete_id="9000001", round="prelim")
    assert not pre["wind_aided"]
    hansen = row(tv[0], athlete_id="9000702")
    assert hansen["wind"] == 0.0 and hansen["mark_value"] == pytest.approx(16 * 0.3048 + 2.75 * 0.0254, abs=1e-4)
    assert not row(moc[0], athlete_id="9000301")["wind_aided"]                # shot put: never a wind event


def test_scope(tv, moc):
    unified = row(tv[0], athlete_id="9000901")
    assert unified["is_adaptive"] and not unified["in_scope"]
    assert moc[0]["in_scope"].all()


def test_status_only_row(tv):
    ahuja = row(tv[0], athlete_id="9000801")
    assert ahuja["status"] == "NH" and pd.isna(ahuja["place"]) and ahuja["mark_raw"] == ""


def test_identity_columns(moc):
    r = row(moc[0], athlete_id="9000004", round="final")
    assert r["athlete_name_key"] == "quenby|rosalind mae"
    assert r["grade"] == 10 and r["grad_year"] == 2026


# ----- failure cases: mutate the good fixture and check the right V-check fires -----

def _ingest_mutated(tmp_path, meets, rules, mutate, name=MOC.name):
    df = pd.read_csv(MOC, dtype=str, keep_default_na=False)
    df = mutate(df)
    p = tmp_path / name
    df.to_csv(p, index=False)
    perf, legs, issues = athleticnet.ingest_file(p, meets, rules)
    return issues + validate.run_all(perf, legs, rules)


def _checks(issues, severity="error"):
    return {i.check for i in issues if i.severity == severity}


def test_missing_column(tmp_path, meets, rules):
    with pytest.raises(athleticnet.IngestError, match="missing columns"):
        _ingest_mutated(tmp_path, meets, rules, lambda d: d.drop(columns=["wind"]))


def test_bad_filename(tmp_path, meets, rules):
    with pytest.raises(athleticnet.IngestError):
        _ingest_mutated(tmp_path, meets, rules, lambda d: d, name="moc_2024.csv")


def test_season_mismatch(tmp_path, meets, rules):
    with pytest.raises(athleticnet.IngestError, match="season"):
        _ingest_mutated(tmp_path, meets, rules, lambda d: d, name="2023_moc_520990.csv")


def test_old_filename_rejected(tmp_path, meets, rules):
    with pytest.raises(athleticnet.IngestError, match="expected"):
        _ingest_mutated(tmp_path, meets, rules, lambda d: d, name="athleticnet_2024_520990.csv")


def test_filename_meet_mismatch(tmp_path, meets, rules):
    with pytest.raises(athleticnet.IngestError, match="filename says 'tri-valley'"):
        _ingest_mutated(tmp_path, meets, rules, lambda d: d, name="2024_tri-valley_520990.csv")


def test_meet_name_must_match_filename(tmp_path, meets, rules):
    def m(d):
        d["meet_name"] = "NCS Tri-Valley Area Championships"
        return d
    assert "V16" in _checks(_ingest_mutated(tmp_path, meets, rules, m))

    def y(d):
        d["meet_name"] = "2023 NCS Meet of Champions"
        return d
    msgs = [i.message for i in _ingest_mutated(tmp_path, meets, rules, y) if i.check == "V16"]
    assert msgs and "year 2023" in msgs[0]


def test_meet_id_column_mismatch(tmp_path, meets, rules):
    def m(d):
        d.loc[0, "meet_id"] = "483067"
        return d
    assert "V02" in _checks(_ingest_mutated(tmp_path, meets, rules, m))


def test_unknown_labels(tmp_path, meets, rules):
    def m(d):
        d.loc[5, "event_raw"] = "Javelin"
        d.loc[6, "round_raw"] = "Round 2"
        d.loc[7, "gender"] = "X"
        return d
    issues = _ingest_mutated(tmp_path, meets, rules, m)
    msgs = " | ".join(i.message for i in issues if i.check == "V03")
    assert "Javelin" in msgs and "Round 2" in msgs and "'X'" in msgs


def test_mark_status_conflicts(tmp_path, meets, rules):
    def m(d):
        d.loc[5, "mark_raw"] = "11.99zz"        # unparseable
        d.loc[6, "status"] = "DQ"               # status DQ with a numeric mark
        return d
    issues = _ingest_mutated(tmp_path, meets, rules, m)
    assert "V04" in _checks(issues)


def test_place_contradicts_mark(tmp_path, meets, rules):
    def m(d):
        i = d.index[(d["event_raw"] == "3200 Meters")]
        d.loc[i, "place"] = ["2", "1"]          # 8:56.42 now listed 2nd behind 8:57.17
        return d
    assert "V06" in _checks(_ingest_mutated(tmp_path, meets, rules, m))


def test_identity_errors(tmp_path, meets, rules):
    def m(d):
        d.loc[6, "athlete_id"] = d.loc[5, "athlete_id"]   # two athletes, same id, same prelim
        d.loc[7, "athlete_id"] = "abc"
        d.loc[8, "grade"] = "13"
        return d
    issues = _ingest_mutated(tmp_path, meets, rules, m)
    assert {"V07", "V11"} <= _checks(issues)
    assert "V08" in _checks(issues, "warning")


def test_missing_athlete_id_goes_to_review(tmp_path, meets, rules):
    df = pd.read_csv(MOC, dtype=str, keep_default_na=False)
    df.loc[10, "athlete_id"] = ""
    p = tmp_path / MOC.name
    df.to_csv(p, index=False)
    perf, legs, issues = athleticnet.ingest_file(p, meets, rules)
    issues += validate.run_all(perf, legs, rules)
    assert "V07" in _checks(issues, "warning") and "V07" not in _checks(issues)
    queue = validate.review_queue(perf)
    assert list(queue["athlete_name_raw"]) == ["Wren Halloway"]


def test_relay_leg_mismatch(tmp_path, meets, rules):
    def m(d):
        d.loc[0, "relay_leg_ids"] = "9000002|9000005"
        return d
    assert "V09" in _checks(_ingest_mutated(tmp_path, meets, rules, m))


def test_missing_school(tmp_path, meets, rules):
    def m(d):
        d.loc[3, "school_id"] = ""
        return d
    assert "V10" in _checks(_ingest_mutated(tmp_path, meets, rules, m))


def test_coverage_warns_on_partial_meet(moc, rules):
    msgs = {i.message for i in validate.check_coverage(moc[0], rules)}
    assert "no in-scope final rows for boys 100" in msgs
    assert "no in-scope final rows for girls 100" not in msgs     # fixture has a girls 100 final


def test_cli_end_to_end(tmp_path, monkeypatch, capsys):
    from ncs_track import cli
    monkeypatch.setattr(paths, "PROCESSED", tmp_path / "processed")
    monkeypatch.setattr(paths, "REVIEW", tmp_path / "review")
    assert cli.main(["ingest-athleticnet", str(MOC), str(TV)]) == 0
    out = capsys.readouterr().out
    assert "2024 rules (standards printed in 2024 results" in out and "0 errors total" in out
    perf = pd.read_csv(tmp_path / "processed" / "performances.csv", dtype=str)
    assert len(perf) == 29 and perf["performance_id"].is_unique
    assert (tmp_path / "review" / "validation_issues.csv").exists()
