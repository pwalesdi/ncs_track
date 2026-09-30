import pandas as pd

from ncs_track import analysis


def moc_rows(rows):
    return pd.DataFrame(rows, columns=["round", "status", "place"])


def test_moc_outcome_rules():
    o = analysis._moc_outcome(moc_rows([("prelim", "OK", 3), ("final", "OK", 8)]), "100")
    assert (o["competed"], o["top_finish"], o["reached_final_round"], o["scored"]) == (1, 1, 1, 0)
    assert analysis._moc_outcome(moc_rows([("final", "OK", 9)]), "100")["top_finish"] == 0
    lj = analysis._moc_outcome(moc_rows([("final", "OK", 9)]), "LJ")
    assert lj["top_finish"] == 1 and lj["reached_final_round"] == 1          # place <= 9 fallback
    assert analysis._moc_outcome(moc_rows([("final", "OK", 10)]), "LJ")["reached_final_round"] == 0
    dns = analysis._moc_outcome(moc_rows([("prelim", "DNS", None)]), "400")
    assert dns["competed"] == 0 and dns["moc_status"] == "DNS"
    dq = analysis._moc_outcome(moc_rows([("prelim", "DQ", None)]), "400")
    assert dq["competed"] == 1 and dq["top_finish"] == 0 and dq["moc_status"] == "DQ"
    assert analysis._moc_outcome(moc_rows([]), "400")["moc_status"] == "not_in_results"
    hj = analysis._moc_outcome(moc_rows([("final", "NH", None)]), "HJ")
    assert hj["competed"] == 1 and hj["reached_final_round"] == 1 and hj["top_finish"] == 0


def q_rows():
    base = dict(season=2026, gender="girls", event_code="100", athlete_name=None, is_relay=False, athlete_id=None,
                school="S", area_place=1, area_mark="12.00", moc_status="OK", moc_final_place=None,
                reached_final_round=0, replacement_for_area=None, state_qualified="pending")
    rows = [
        dict(area="tri-valley", qualifier_type="automatic", in_qualified_field=1, in_declared_field=1, competed=1,
             top_finish=1, scored=1, choice_tag=None, vacancy_refilled_by_area=None),
        dict(area="tri-valley", qualifier_type="automatic", in_qualified_field=1, in_declared_field=1, competed=0,
             top_finish=0, scored=0, choice_tag=None, vacancy_refilled_by_area=None),
        dict(area="tri-valley", qualifier_type="next_best_mark", in_qualified_field=1, in_declared_field=0,
             competed=0, top_finish=0, scored=0, choice_tag="chose_other_events", vacancy_refilled_by_area="tri-valley",
             competed_other_moc_event=1),
        dict(area="tri-valley", qualifier_type="replacement", in_qualified_field=0, in_declared_field=1, competed=1,
             top_finish=0, scored=0, choice_tag=None, vacancy_refilled_by_area=None),
        dict(area="bay-shore", qualifier_type="at_large_standard", in_qualified_field=1, in_declared_field=1,
             competed=1, top_finish=1, scored=0, choice_tag=None, vacancy_refilled_by_area=None),
    ]
    q = pd.DataFrame([{"competed_other_moc_event": None, **base, **r} for r in rows])
    q["at_large_combined"] = q["qualifier_type"].isin(analysis.AT_LARGE_TYPES).astype(int)
    return q


def test_spot_utilization_accounting():
    su = analysis.spot_utilization(q_rows()).set_index("area")
    tv = su.loc["tri-valley"]
    assert (tv["spots_earned"], tv["declared"], tv["competed"], tv["no_show"], tv["not_declared"]) == (3, 2, 1, 1, 1)
    assert tv["unused_total"] == 2 and tv["utilization_rate"] == round(1 / 3, 4)
    assert tv["not_declared_chose_other_events"] == 1 and tv["vacancies_refilled"] == 1
    assert tv["refilled_by_area"] == "tri-valley:1" and tv["replacements_from_this_area"] == 1
    roll = analysis.spot_utilization_by_area(su.reset_index()).set_index("area")
    assert roll.loc["bay-shore", "utilization_rate"] == 1.0


def test_field_makeup_and_at_large_share():
    fm = analysis.field_makeup(q_rows())
    per_type = fm[~fm["rollup"]].groupby("field")["share_of_field"].sum().round(6)
    assert (per_type == 1).all()
    decl = fm[(fm["field"] == "declared") & ~fm["rollup"]].set_index(["area", "qualifier_type"])["count"]
    assert decl[("tri-valley", "replacement")] == 1
    share = analysis.at_large_share(q_rows())
    comb = share[(share["field"] == "qualified") & (share["spot_type"] == "at_large_combined")].set_index("area")
    assert comb.loc["tri-valley", "area_share"] == 0.5 and comb.loc["class-a", "count"] == 0
    perf = analysis.moc_performance(q_rows())
    auto = perf[(perf["area"] == "tri-valley") & (perf["qualifier_type"] == "automatic")].iloc[0]
    assert auto["competed"] == 1 and auto["top_finish_rate"] == 1.0


def test_flags_need_three_seasons():
    su = pd.concat([analysis.spot_utilization(q_rows().assign(season=s)) for s in (2022, 2023, 2024)])
    flags = analysis.spot_utilization_flags(su)
    assert list(flags["area"]) == ["tri-valley"] and flags.iloc[0]["seasons_flagged"] == 3
    assert analysis.spot_utilization_flags(su[su["season"] != 2024]).empty


def test_unused_not_refilled_no_show_rate_double_qualifier():
    tv = analysis.spot_utilization(q_rows()).set_index("area").loc["tri-valley"]
    # unused 2 (1 no-show + 1 not declared); the not-declared spot was refilled -> 1 unused, not refilled
    assert tv["unused_not_refilled"] == 1 and tv["no_show_rate"] == 0.5
    assert tv["not_declared_individual"] == 1 and tv["double_qualifier_share"] == 1.0
    su = pd.concat([analysis.spot_utilization(q_rows().assign(season=s)) for s in (2022, 2023, 2024)])
    flags = analysis.spot_utilization_flags(su, metric="unused_not_refilled")
    assert list(flags["area"]) == ["tri-valley"] and flags.iloc[0]["metric"] == "unused_not_refilled"


def _moc(field_size):
    return pd.DataFrame({"gender": "girls", "event_code": "100", "round": "prelim",
                         "status": ["OK"] * field_size})


def test_unfilled_spots_need_a_short_field():
    # TV: auto who competed; auto no-show; next-best-mark not declared but refilled; BS at-large-std who competed.
    q = q_rows()
    q.loc[1, "vacancy_refilled_by_area"] = None
    short = analysis.mark_unfilled(q, _moc(23))
    full = analysis.mark_unfilled(q, _moc(24))
    # Only the TV automatic no-show counts, and only when the field ended below 24.
    assert short["unfilled_spot"].tolist() == [False, True, False, False, False]
    assert not full["unfilled_spot"].any()
    tv = analysis.spot_utilization(short).set_index("area").loc["tri-valley"]
    assert (tv["guaranteed_spots"], tv["unfilled_spots"], tv["unfilled_rate"]) == (3, 1, round(1 / 3, 4))
    assert tv["competed"] + tv["vacancies_refilled"] + tv["unfilled_spots"] + tv["other_unused"] == tv["spots_earned"]
    ns = analysis.no_shows_unfilled(analysis.spot_utilization(short)).set_index("area")
    assert ns.loc["tri-valley", "unfilled_spots"] == 1


def test_moc_overall_places():
    moc = pd.DataFrame({
        "athlete_name_raw": ["A B", "C D", "E F", "G H"], "school_name_raw": "S", "is_relay": False,
        "athlete_id": ["1", "2", "3", "4"], "gender": "girls", "event_code": "100",
        "round": ["final", "final", "prelim", "prelim"], "status": "OK", "place": [1, 2, 5, 6],
        "mark_value": [12.0, 12.1, 12.3, 12.2]})
    places = analysis.moc_overall_places(moc, lambda s: "s")
    assert places[("girls", "100", "1")] == 1 and places[("girls", "100", "4")] == 3 and places[("girls", "100", "3")] == 4


def test_core_comparison_groups():
    q = q_rows()
    q.loc[0, "area_place"] = 6                                   # a TV 6th-place auto who competed
    q["moc_overall_place"] = [3.0, None, None, 12.0, 5.0]
    cc = analysis.core_comparison(q)
    tv = cc[(cc["season"] == "2026") & (cc["event_group"] == "sprints_hurdles") & (cc["area"] == "tri-valley")]
    low = tv[tv["comparison_group"] == "lowest_automatic"].iloc[0]
    other = tv[tv["comparison_group"] == "at_large_other_areas"].iloc[0]
    # One athlete per group: counts are published, MOC-place figures are suppressed (< MIN_CELL).
    assert low["competed"] == 1 and pd.isna(low["top_finish"]) and pd.isna(low["median_moc_place"])
    assert other["competed"] == 1 and pd.isna(other["top_finish"]) and pd.isna(other["median_moc_place"])
    big = pd.concat([q.assign(season=s) for s in range(2020, 2026)])       # 6 seasons -> pooled cell of 6
    pooled = analysis.core_comparison(big)
    row = pooled[pooled["season"].str.contains("pooled") & (pooled["event_group"] == "sprints_hurdles")
                 & (pooled["area"] == "tri-valley") & (pooled["comparison_group"] == "lowest_automatic")].iloc[0]
    assert (row["competed"], row["top_finish"], row["median_moc_place"]) == (6, 6, 3.0)
    assert set(cc["season"]) == {"2026", "2026-2026 pooled"}
    assert set(pooled["season"]) >= {"2020-2025 pooled"}


def test_cutoff_is_nth_best_mark_across_all_rounds():
    # A slow 8th-place final (25.00) must not set the cutoff; athletes count once at their best mark.
    moc = pd.DataFrame({
        "season": 2026, "gender": "boys", "event_code": "200", "is_relay": False, "school_name_raw": "S",
        "athlete_name_raw": [f"A{i}" for i in range(8)] + [f"A{i}" for i in range(8)] + ["P1", "P2", "P3"],
        "athlete_id": [str(i) for i in range(8)] * 2 + ["p1", "p2", "p3"],
        "round": ["final"] * 8 + ["prelim"] * 11, "status": "OK",
        "place": list(range(1, 9)) + [None] * 11,
        "mark_raw": [f"{21 + i / 10:.2f}" for i in range(7)] + ["25.00"]
                    + [f"{21.05 + i / 10:.2f}" for i in range(7)] + ["21.75"] + ["21.72", "21.90", "22.40"],
        "mark_value": [21 + i / 10 for i in range(7)] + [25.0]
                      + [21.05 + i / 10 for i in range(7)] + [21.75] + [21.72, 21.90, 22.40]})
    cut = analysis.moc_cutoffs(moc).iloc[0]
    # best marks: 21.0..21.6 (7 athletes), 21.72, 21.75, ... -> 8th best = 21.72
    assert cut["moc_cutoff_mark"] == "21.72" and cut["moc_cutoff_source"] == "best_mark_all_rounds"


def _core_q():
    rows = []
    for season in (2025, 2026):
        for ev in ("100", "200"):
            for area, place, qtype, top in (("tri-valley", 5, "automatic", 1), ("tri-valley", 6, "automatic", 1),
                                            ("bay-shore", 5, "automatic", 0), ("bay-shore", 6, "automatic", 0),
                                            ("tri-valley", 8, "next_best_mark", 1), ("redwood-empire", 7, "at_large_standard", 0),
                                            ("class-a", 3, "automatic", 0), ("class-a", 5, "next_best_mark", 1)):
                rows.append(dict(season=season, gender="girls", event_code=ev, area=area, area_place=place,
                                 qualifier_type=qtype, top_finish=top, in_declared_field=1, competed=1,
                                 at_large_combined=int(qtype in analysis.AT_LARGE_TYPES),
                                 athlete_id=f"{area}{place}{ev}", school="S", moc_overall_place=float(place)))
    return pd.DataFrame(rows)


def test_core_tests_columns_and_logic():
    t = analysis.core_tests(_core_q(), n_perm=200).set_index("area")
    bs = t.loc["bay-shore"]
    # Bay Shore lowest autos: 0 of 8; other Areas' at-large: TV nbm 4 of 4 + RE std 0 of 4 + CA nbm 4 of 4
    assert (bs["lowest_auto_top"], bs["lowest_auto_n"], bs["other_at_large_top"], bs["other_at_large_n"]) == (0, 8, 8, 12)
    assert bs["gap"] == round(0 - 8 / 12, 4)
    assert pd.isna(t.loc["redwood-empire", "gap"])                 # no RE lowest autos in the fixture
    for col in ("naive_p", "clustered_p", "permutation_p"):
        assert 0 <= bs[col] <= 1
    assert t.loc["bay-shore", "permutation_p"] == analysis.core_tests(_core_q(), n_perm=200).set_index("area").loc["bay-shore", "permutation_p"]


def test_clustered_se_equals_robust_when_every_row_is_its_own_cluster():
    y = [1, 0, 1, 1, 0, 0, 1, 0, 0, 0]
    g = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
    b1, p1 = analysis._clustered_p(y, g, list(range(10)))
    b2, p2 = analysis._clustered_p(y, g, ["a", "a", "b", "b", "c", "d", "d", "e", "f", "g"])
    assert abs(b1 - 0.4) < 1e-12 and abs(b2 - 0.4) < 1e-12 and p1 != p2


def test_core_place_curve_aggregates_and_suppresses():
    q = _core_q().assign(in_declared_field=1, competed=1)
    c = analysis.core_place_curve(q)
    assert {"entries", "top8_count", "median_moc_place"} <= set(c.columns)
    small = c[(c["entries"] > 0) & (c["entries"] < analysis.MIN_CELL)]
    assert small["top8_count"].isna().all() and small["median_moc_place"].isna().all()
    big = c[(c["season"].str.contains("pooled")) & (c["gender"] == "all") & (c["event_group"] == "all")
            & (c["area"] == "tri-valley") & (c["area_place"] == "5-6")].iloc[0]
    assert big["entries"] == 8 and big["top8_count"] == 8          # TV 5th/6th, 2 events x 2 seasons x 2 places
    assert set(c["area_place"]) == {str(p) for p in range(1, 13)} | {"5-6", "7-8"}
