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
             competed=0, top_finish=0, scored=0, choice_tag="chose_other_events", vacancy_refilled_by_area="tri-valley"),
        dict(area="tri-valley", qualifier_type="replacement", in_qualified_field=0, in_declared_field=1, competed=1,
             top_finish=0, scored=0, choice_tag=None, vacancy_refilled_by_area=None),
        dict(area="bay-shore", qualifier_type="at_large_standard", in_qualified_field=1, in_declared_field=1,
             competed=1, top_finish=1, scored=0, choice_tag=None, vacancy_refilled_by_area=None),
    ]
    q = pd.DataFrame([{**base, **r} for r in rows])
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
    assert list(flags["area"]) == ["tri-valley"] and flags.iloc[0]["seasons_with_unused"] == 3
    assert analysis.spot_utilization_flags(su[su["season"] != 2024]).empty
