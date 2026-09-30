import pandas as pd

from ncs_track import analysis


def moc_rows(rows):
    return pd.DataFrame(rows, columns=["round", "status", "place"])


def test_moc_outcome_rules():
    o = analysis._moc_outcome(moc_rows([("prelim", "OK", 3), ("final", "OK", 8)]), "100")
    assert (o["competed"], o["made_final"], o["reached_final_round"], o["scored"]) == (1, 1, 1, 0)
    assert analysis._moc_outcome(moc_rows([("final", "OK", 9)]), "100")["made_final"] == 0
    lj = analysis._moc_outcome(moc_rows([("final", "OK", 9)]), "LJ")
    assert lj["made_final"] == 1 and lj["reached_final_round"] == 1          # place <= 9 fallback
    assert analysis._moc_outcome(moc_rows([("final", "OK", 10)]), "LJ")["reached_final_round"] == 0
    dns = analysis._moc_outcome(moc_rows([("prelim", "DNS", None)]), "400")
    assert dns["competed"] == 0 and dns["moc_status"] == "DNS"
    dq = analysis._moc_outcome(moc_rows([("prelim", "DQ", None)]), "400")
    assert dq["competed"] == 1 and dq["made_final"] == 0 and dq["moc_status"] == "DQ"
    assert analysis._moc_outcome(moc_rows([]), "400")["moc_status"] == "not_in_results"
    hj = analysis._moc_outcome(moc_rows([("final", "NH", None)]), "HJ")
    assert hj["competed"] == 1 and hj["reached_final_round"] == 1 and hj["made_final"] == 0


def q_rows():
    """TV: an automatic who competed; an automatic no-show; a pre-declaration next-best-mark
    qualifier who declined; a finisher further down who took an automatic spot by pass-down
    (not a pre-declaration qualifier); an automatic who declined. BS: an at-large entrant."""
    base = dict(season=2026, gender="girls", event_code="100", athlete_name=None, is_relay=False, athlete_id=None,
                school="S", area_place=1, area_mark="12.00", moc_status="OK", moc_final_place=None,
                reached_final_round=0, state_qualified="pending", choice_tag=None, declined=None)
    rows = [
        dict(area="tri-valley", qualifier_type="automatic", route="automatic", in_qualified_field=1,
             in_declared_field=1, competed=1, made_final=1, scored=1),
        dict(area="tri-valley", qualifier_type="automatic", route="automatic", in_qualified_field=1,
             in_declared_field=1, competed=0, made_final=0, scored=0),
        dict(area="tri-valley", qualifier_type="next_best_mark", route=None, in_qualified_field=1, in_declared_field=0,
             competed=0, made_final=0, scored=0, declined="next_best_mark", competed_other_moc_event=1),
        dict(area="tri-valley", qualifier_type=None, route="automatic", in_qualified_field=0, in_declared_field=1,
             competed=1, made_final=0, scored=0),
        dict(area="tri-valley", qualifier_type="automatic", route=None, in_qualified_field=1, in_declared_field=0,
             competed=0, made_final=0, scored=0, declined="automatic"),
        dict(area="bay-shore", qualifier_type="at_large_standard", route="at_large_standard", in_qualified_field=1,
             in_declared_field=1, competed=1, made_final=1, scored=0),
    ]
    q = pd.DataFrame([{"competed_other_moc_event": None, **base, **r} for r in rows])
    q["at_large_combined"] = q["qualifier_type"].isin(analysis.AT_LARGE_TYPES).astype(int)
    q["no_show"] = ((q["in_declared_field"] == 1) & (q["competed"] == 0)).astype(int)
    return q


def test_spot_utilization_accounting():
    su = analysis.spot_utilization(q_rows()).set_index("area")
    tv, bs = su.loc["tri-valley"], su.loc["bay-shore"]
    # TV: 6 automatic spots + 0 next best mark; 2 entrants competed, 1 no-show, 3 not used
    assert (tv["guaranteed_spots"], tv["g_competed"], tv["g_no_show"], tv["g_not_used"]) == (6, 2, 1, 3)
    assert tv["g_competed"] + tv["g_no_show"] + tv["g_not_used"] == tv["guaranteed_spots"]
    assert (tv["passed_down"], tv["declined_nbm"], tv["entries"], tv["no_show"]) == (1, 1, 3, 1)
    assert (bs["guaranteed_spots"], bs["g_not_used"], bs["at_large_spots"], bs["al_competed"]) == (6, 6, 1, 1)
    assert su.loc["class-a", "guaranteed_spots"] == 3                    # every Area appears, even with no rows
    roll = analysis.spot_utilization_by_area(su.reset_index()).set_index("area")
    assert roll.loc["tri-valley", "guaranteed_used_rate"] == round(2 / 6, 4)
    assert roll.loc["tri-valley", "no_show_rate"] == round(1 / 3, 4)


def test_field_makeup_and_at_large_share():
    fm = analysis.field_makeup(q_rows())
    per_type = fm[~fm["rollup"]].groupby("field")["share_of_field"].sum().round(6)
    assert (per_type == 1).all()
    decl = fm[(fm["field"] == "declared") & ~fm["rollup"]].set_index(["area", "qualifier_type"])["count"]
    assert decl[("tri-valley", "automatic")] == 3                 # pass-down routes in the declared field
    qual = fm[(fm["field"] == "qualified") & ~fm["rollup"]].set_index(["area", "qualifier_type"])["count"]
    assert qual[("tri-valley", "automatic")] == 3 and qual[("tri-valley", "next_best_mark")] == 1
    share = analysis.at_large_share(q_rows())
    comb = share[(share["field"] == "qualified") & (share["spot_type"] == "at_large_combined")].set_index("area")
    assert comb.loc["tri-valley", "area_share"] == 0.5 and comb.loc["class-a", "count"] == 0
    decl = share[(share["field"] == "declared") & (share["spot_type"] == "at_large_combined")].set_index("area")
    assert decl.loc["tri-valley", "count"] == 0 and decl.loc["bay-shore", "area_share"] == 1.0
    perf = analysis.moc_performance(q_rows())
    auto = perf[(perf["area"] == "tri-valley") & (perf["qualifier_type"] == "automatic")]
    assert set(auto["event"]) == {"100", "group:sprints_hurdles", "all"} and set(auto["gender"]) == {"girls", "all"}
    assert (auto["competed"] == 2).all() and auto["made_final"].isna().all()      # 2 entries: suppressed


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
    q["moc_overall_place"] = [3.0, None, None, None, None, 5.0]
    q = q.drop(index=3)
    cc = analysis.core_comparison(q)
    tv = cc[(cc["season"] == "2026") & (cc["event_group"] == "sprints_hurdles") & (cc["area"] == "tri-valley")]
    low = tv[tv["comparison_group"] == "lowest_automatic"].iloc[0]
    other = tv[tv["comparison_group"] == "at_large_other_areas"].iloc[0]
    # One athlete per group: counts are published, MOC-place figures are suppressed (< MIN_CELL).
    assert low["competed"] == 1 and pd.isna(low["made_final"]) and pd.isna(low["median_moc_place"])
    assert other["competed"] == 1 and pd.isna(other["made_final"]) and pd.isna(other["median_moc_place"])
    big = pd.concat([q.assign(season=s) for s in range(2020, 2026)])       # 6 seasons -> pooled cell of 6
    pooled = analysis.core_comparison(big)
    row = pooled[pooled["season"].str.contains("pooled") & (pooled["event_group"] == "sprints_hurdles")
                 & (pooled["area"] == "tri-valley") & (pooled["comparison_group"] == "lowest_automatic")].iloc[0]
    assert (row["competed"], row["made_final"], row["median_moc_place"]) == (6, 6, 3.0)
    assert set(cc["season"]) == {"2026", "2026-2026 pooled"}
    assert set(pooled["season"]) >= {"2020-2025 pooled"}


def _core_q():
    rows = []
    for season in (2025, 2026):
        for ev in ("100", "200"):
            for area, place, qtype, top in (("tri-valley", 5, "automatic", 1), ("tri-valley", 6, "automatic", 1),
                                            ("bay-shore", 5, "automatic", 0), ("bay-shore", 6, "automatic", 0),
                                            ("tri-valley", 8, "next_best_mark", 1), ("redwood-empire", 7, "at_large_standard", 0),
                                            ("class-a", 3, "automatic", 0), ("class-a", 5, "next_best_mark", 1)):
                rows.append(dict(season=season, gender="girls", event_code=ev, area=area, area_place=place,
                                 qualifier_type=qtype, route=qtype, made_final=top, in_declared_field=1, competed=1,
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
    assert {"entries", "made_final_count", "median_moc_place"} <= set(c.columns)
    small = c[(c["entries"] > 0) & (c["entries"] < analysis.MIN_CELL)]
    assert small["made_final_count"].isna().all() and small["median_moc_place"].isna().all()
    big = c[(c["season"].str.contains("pooled")) & (c["gender"] == "all") & (c["event_group"] == "all")
            & (c["area"] == "tri-valley") & (c["area_place"] == "5-6")].iloc[0]
    assert big["entries"] == 8 and big["made_final_count"] == 8          # TV 5th/6th, 2 events x 2 seasons x 2 places
    assert set(c["area_place"]) == {str(p) for p in range(1, 13)} | {"5-6", "7-8", analysis.NOT_AUTO_BAND}
    na = c[(c["season"].str.contains("pooled")) & (c["gender"] == "all") & (c["event_group"] == "all")
           & (c["area"] == "tri-valley") & (c["area_place"] == analysis.NOT_AUTO_BAND)].iloc[0]
    assert na["entries"] == 4 and pd.isna(na["made_final_count"])      # TV 8th next best mark: 4 entries


def test_moc_performance_publishes_counts_from_five_entries():
    q = pd.concat([q_rows().iloc[[0]]] * 5, ignore_index=True)
    perf = analysis.moc_performance(q)
    row = perf[(perf["event"] == "all") & (perf["gender"] == "all") & (perf["season"] == "2026")].iloc[0]
    assert (row["competed"], row["made_final"], row["made_final_rate"]) == (5, 5, 1.0)
    assert set(perf["season"]) == {"2026", "2026-2026 pooled"}


def test_left_out_counts_beaten_automatics_from_other_areas():
    routes = pd.DataFrame([
        # 1600 m: Bay Shore automatics at 5:20 and 5:31; a Redwood Empire 10th at 5:17 who wasn't entered
        dict(gender="girls", event_code="1600", meet_area="bay-shore", place=5, mark_value=320.0, mark_raw="5:20",
             athlete_name="Ana Vell", school_name="S1", is_relay=False, route="auto", left_out=False),
        dict(gender="girls", event_code="1600", meet_area="bay-shore", place=10, mark_value=331.0, mark_raw="5:31",
             athlete_name="Bea Ord", school_name="S2", is_relay=False, route="auto", left_out=False),
        dict(gender="girls", event_code="1600", meet_area="redwood-empire", place=6, mark_value=316.0, mark_raw="5:16",
             athlete_name="Cy Rao", school_name="S3", is_relay=False, route="auto", left_out=False),
        dict(gender="girls", event_code="1600", meet_area="redwood-empire", place=10, mark_value=317.0, mark_raw="5:17",
             athlete_name="Di Sato", school_name="S4", is_relay=False, route=None, left_out=True),
        dict(gender="girls", event_code="1600", meet_area="redwood-empire", place=11, mark_value=326.0, mark_raw="5:26",
             athlete_name="Eve Tam", school_name="S5", is_relay=False, route=None, left_out=True),
    ])
    q = pd.DataFrame([dict(season=2025, gender="girls", event_code="1600", area="bay-shore", area_place=p, route="automatic",
                           in_declared_field=1, competed=1, made_final=m, moc_overall_place=o, qualifier_type="automatic")
                      for p, m, o in ((5, 1, 6.0), (10, 0, 20.0))])
    lo, pairs = analysis.left_out(2025, routes, q)
    got = lo.set_index("athlete_name")["beaten_other_area_autos"].to_dict()
    assert got == {"Di Sato": 2, "Eve Tam": 1}            # own Area's 5:16 automatic doesn't count
    assert set(pairs["beaten_area"]) == {"bay-shore"} and pairs["beaten_made_final"].sum() == 1
    counts, beaten = analysis.left_out_summary(lo, pairs)
    row = counts[(counts["area"] == "redwood-empire") & (counts["beaten_area"] == "bay-shore")].iloc[0]
    assert (row["beat_any"], row["beaten_autos"]) == (2, 2)
    tot = counts[(counts["area"] == "redwood-empire") & (counts["beaten_area"] == "any")].iloc[0]
    assert (tot["left_out"], tot["beat_any"]) == (2, 2)
    b = beaten[(beaten["season"] == "2025") & (beaten["area"] == "all") & (beaten["beaten_area"] == "all")].iloc[0]
    assert b["beaten_autos"] == 2 and pd.isna(b["made_final"])           # 2 entries: MOC figures suppressed
