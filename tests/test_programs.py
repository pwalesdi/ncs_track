"""MOC program parser on hand-copied lines from the real programs."""

import pandas as pd
import pytest

from ncs_track import paths, programs

# (page, column, line) as extract_lines yields them. Taken from 2024/2026 MOC programs.
LINES = [
    (1, "L", "Diablo Timing - Contractor License"),
    (1, "L", "NCS Meet of Champions"),
    (1, "L", "Event 26 Girls Discus Throw Varsity"),
    (1, "L", "Friday 5/22/2026 - 12:30 PM"),
    (1, "L", "MOC: 165-02 2002 Kamiya Warren"),
    (1, "L", "139-05 CIF At-Large"),
    (1, "L", "Pos Name Yr School Seed Mark"),
    (1, "L", "Flight 1 of 2 Finals"),
    (1, "L", "1 Fairweather, Opal 11 Middletown 89-10"),
    (1, "L", "2 Wexley, Bryony 11 St. Bernard (Nc) 92-02"),
    (1, "L", "3 Ormsby, Caspian El Cerrito 130-07"),
    (1, "R", "Hy-Tek's MEET MANAGER 5/21/2026 Page 1"),
    (1, "R", "Flight 2 of 2 Finals"),                                 # continues Event 26
    (1, "R", "8 Lindqvist, Saffron 12 Miramonte 141-01 CIF"),
    (1, "R", "9 Harrowgate II, Leopold 11 Heritage 42-09.00"),
    (2, "L", "Event 1 Girls 4x100 Meter Relay Varsity"),
    (2, "L", "8 Advance: Top 1 Each Heat plus Next 5 Best Times"),
    (2, "L", "Lane Team Relay Seed Time"),
    (2, "L", "Heat 1 of 2 Prelims"),
    (2, "L", "4 St. Mary's 46.98 CIF"),
    (2, "L", "1) Pemberly, Averil 11 2) Sturridge, Elowen 10"),
    (2, "L", "8 Santa Rosa ( 52.10"),
    (2, "L", "5 California C 50.00"),
    (2, "R", "Section 1 of 1 Finals...(Event 1 Girls 4x100 Meter Relay Varsity)"),
    (2, "R", "Lane Team Relay Prelims"),
    (2, "R", "4 St. Mary's 47.10"),                                  # advancement round
    (3, "L", "Event 9 Girls 100 Meter Dash Varsity"),
    (3, "L", "Heat 1 of 1 Prelims"),
    (3, "L", "8 Radcliffe, Anselm 12 Dublin NT"),
    (3, "L", "3 Castellane, Rupert -- Cardinal New 12.80"),
    (3, "L", "1 Hawksworth, Ferris M11 Miramonte 17-09.75"),              # not an entry line
    (3, "L", "Event 40 Boys 100 Meter Dash Boys Divisio Unif"),
    (3, "L", "Section 1 of 1 Finals"),
    (3, "L", "1 Montclair, Jasper M12 Amador Valley 32.93"),
]


@pytest.fixture(scope="module")
def parsed():
    return programs.parse_lines(LINES, season=2026, meet_key="2026-moc", source_file="x.pdf",
                                known_schools={"El Cerrito"})


def rows(parsed):
    return programs.to_frame(parsed.rows)


def test_individual_rows(parsed):
    df = rows(parsed)
    dt = df[df["event_code"] == "DT"].set_index("athlete_name")
    assert list(dt.index) == ["Fairweather, Opal", "Wexley, Bryony", "Ormsby, Caspian",
                              "Lindqvist, Saffron", "Harrowgate II, Leopold"]
    assert dt.loc["Wexley, Bryony", "school_name"] == "St. Bernard (Nc)"
    assert dt.loc["Lindqvist, Saffron", "seed_flags"] == "CIF"
    assert dt.loc["Lindqvist, Saffron", "heat"] == 2                     # right column kept the event
    assert dt.loc["Fairweather, Opal", "seed_mark_value"] == pytest.approx(89 * 0.3048 + 10 * 0.0254)


def test_missing_grade_split_by_known_school(parsed):
    r = rows(parsed).set_index("athlete_name").loc["Ormsby, Caspian"]
    assert r["school_name"] == "El Cerrito" and pd.isna(r["grade"])
    assert r["parse_issues"] == "grade missing"
    r = rows(parsed).set_index("athlete_name").loc["Castellane, Rupert"]
    assert r["school_name"] == "Cardinal New"


def test_relays_and_legs(parsed):
    rel = rows(parsed)[lambda d: d["event_code"] == "4x100"]
    prelim = rel[rel["round"] == "prelim"].set_index("school_name")
    assert list(prelim.index) == ["St. Mary's", "Santa Rosa (", "California C"]
    assert prelim.loc["St. Mary's", "relay_legs"] == "Pemberly, Averil 11; Sturridge, Elowen 10"


def test_entry_rows_drop_advancement_rounds(parsed):
    ent = programs.entry_rows(rows(parsed))
    rel = ent[ent["event_code"] == "4x100"]
    assert set(rel["round"]) == {"prelim"} and len(rel) == 3
    assert set(ent.loc[ent["event_code"] == "DT", "round"]) == {"final"}


def test_no_mark_seed_and_adaptive(parsed):
    df = rows(parsed)
    nt = df.set_index("athlete_name").loc["Radcliffe, Anselm"]
    assert nt["seed_status"] == "NT" and pd.isna(nt["seed_mark_value"])
    unparsed = pd.DataFrame(parsed.unparsed)
    assert set(unparsed["line"]) == {"1 Hawksworth, Ferris M11 Miramonte 17-09.75",
                                     "1 Montclair, Jasper M12 Amador Valley 32.93"}
    assert unparsed.set_index("line").loc["1 Montclair, Jasper M12 Amador Valley 32.93", "in_scope"] == False  # noqa: E712


def test_validation_flags_counts(parsed):
    ent = programs.entry_rows(rows(parsed))
    counts, issues = programs.validate_entries(ent, pd.DataFrame(parsed.unparsed),
                                               {"girls": ["100", "DT", "4x100"]})
    assert set(counts["flag"].dropna()) == {"under 24"}
    kinds = set(issues["kind"])
    assert {"count", "field", "seed_no_mark", "unparsed_line", "unparsed_line_adaptive"} <= kinds


@pytest.mark.skipif(not (paths.PROCESSED / "moc_entries.csv").exists(), reason="run moc-entries first")
def test_real_entries_shape():
    df = pd.read_csv(paths.PROCESSED / "moc_entries.csv")
    assert set(df["season"]) == {2022, 2023, 2024, 2025, 2026}
    main = df[~df["is_adaptive"] & df["event_modifier"].isna() & (df["event_code"] != "4x800")]
    per_event = main.groupby(["season", "gender", "event_code"]).size()
    assert len(per_event) == 5 * 32 and per_event.between(20, 40).all()
