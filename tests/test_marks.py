import pytest

from ncs_track.marks import MarkParseError, is_better, parse_mark


@pytest.mark.parametrize("raw, value, flags", [
    ("11.60", 11.60, ()),
    ("47.20QCIF", 47.20, ("Q", "CIF")),
    ("11.84q", 11.84, ("q",)),
    ("11.60RNCS", 11.60, ("R", "NCS")),
    ("47.49 CIF", 47.49, ("CIF",)),
    ("4:57.94", 297.94, ()),
    ("8:56.42 CIF", 536.42, ("CIF",)),
    ("12.004", 12.004, ()),
    ("1:02:03.4", 3723.4, ()),
    ("11.6h", 11.6, ("h",)),
    ("J15.02", 15.02, ("J",)),
])
def test_times(raw, value, flags):
    m = parse_mark(raw, "time")
    assert m.status == "OK" and m.unit == "s"
    assert m.value == pytest.approx(value)
    assert m.flags == flags
    assert m.raw == raw


@pytest.mark.parametrize("raw, meters, flags", [
    ("5-04.00", 5 * 0.3048 + 4 * 0.0254, ()),
    ("J5-01.00", 5 * 0.3048 + 1 * 0.0254, ("J",)),
    ("J11-08.00", 11 * 0.3048 + 8 * 0.0254, ("J",)),
    ("31-2.75", 31 * 0.3048 + 2.75 * 0.0254, ()),
    ("142-05", 142 * 0.3048 + 5 * 0.0254, ()),
    ("5-0", 5 * 0.3048, ()),
    ("45-02.50 CIF", 45 * 0.3048 + 2.5 * 0.0254, ("CIF",)),
    ("18-01.75 NCS", 18 * 0.3048 + 1.75 * 0.0254, ("NCS",)),
    ("18' 1.75\"", 18 * 0.3048 + 1.75 * 0.0254, ()),
    ("5'4\"", 5 * 0.3048 + 4 * 0.0254, ()),
    ("12.34m", 12.34, ()),
])
def test_distances(raw, meters, flags):
    m = parse_mark(raw, "distance")
    assert m.status == "OK" and m.unit == "m"
    assert m.value == pytest.approx(meters, abs=1e-4)
    assert m.flags == flags


@pytest.mark.parametrize("raw, status", [
    ("DNS", "DNS"), ("DNF", "DNF"), ("DQ", "DQ"), ("FS", "FS"), ("SCR", "SCR"),
    ("NH", "NH"), ("NM", "NM"), ("ND", "NM"), ("FOUL", "FOUL"), ("dq", "DQ"),
])
def test_statuses(raw, status):
    for measure in ("time", "distance"):
        m = parse_mark(raw, measure)
        assert m.status == status and m.value is None and not m.ok


@pytest.mark.parametrize("raw, measure", [
    ("", "time"),
    ("12.3xyz", "time"),        # unknown suffix
    ("1:75.00", "time"),        # seconds >= 60
    ("5-12.00", "distance"),    # inches >= 12
    ("abc", "distance"),
    ("11.60", "distance"),      # a time is not a distance
])
def test_rejects(raw, measure):
    with pytest.raises(MarkParseError):
        parse_mark(raw, measure)


def test_is_better():
    assert is_better(11.5, 11.6, "time")
    assert is_better(5.2, 5.1, "distance")
    assert not is_better(11.6, 11.6, "time")
