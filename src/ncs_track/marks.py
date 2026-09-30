"""Parse track & field marks into numbers without losing the raw string.

Times become seconds and field marks become meters. Parsing is strict: anything
unrecognised raises MarkParseError instead of guessing, so bad input surfaces in
validation rather than as a silently wrong number.

Formats handled (all seen in Hy-Tek results or expected from Athletic.net):
  times      11.60   4:57.94   1:02:03.4   12.004 (thousandths)
  feet-inch  5-04.00   31-2.75   142-05   5-0   5' 4"   17' 6.5"
  metric     12.34m
  prefixes   J  (tied height/time placed by judges or misses: J5-01.00, J15.02)
  suffixes   Q q R NCS CIF h a and combinations glued on: 47.20QCIF, 11.60RNCS, 11.6h,
             10.55a (Athletic.net: a = fully automatic timing, h = hand timed)
  statuses   DNS DNF DQ FS SCR NH NM ND FOUL NT
"""

from __future__ import annotations

import re
from dataclasses import dataclass

FOOT_M = 0.3048
INCH_M = 0.0254

STATUSES = ("OK", "DNS", "DNF", "DQ", "FS", "SCR", "NH", "NM", "FOUL", "NT")
_STATUS_ALIASES = {"ND": "NM", "SCRATCH": "SCR", "FALSE START": "FS"}

# Longest first so "CIF" wins over "C"-anything and "NCS" is taken whole.
_FLAG_TOKENS = ("CIF", "NCS", "Q", "q", "R", "h", "a", "*", "#", "@")

_TIME = re.compile(r"^(?:(?:(\d+):)?(\d{1,2}):)?(\d{1,2}(?:\.\d{1,3})?)$")
_FEET_INCH = re.compile(r"^(\d{1,3})-(\d{1,2}(?:\.\d{1,2})?)$")
_FEET_INCH_QUOTES = re.compile(r"^(\d{1,3})'\s*(\d{1,2}(?:\.\d{1,2})?)\"?$")
_METRIC = re.compile(r"^(\d{1,3}\.\d{1,2})m$")


class MarkParseError(ValueError):
    pass


@dataclass(frozen=True)
class Mark:
    raw: str
    status: str                 # one of STATUSES
    value: float | None         # seconds or meters; None unless status == "OK"
    unit: str | None            # "s" | "m"
    flags: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.status == "OK"


def _split_flags(rest: str) -> tuple[str, ...]:
    flags = []
    while rest:
        for tok in _FLAG_TOKENS:
            if rest.startswith(tok):
                flags.append(tok)
                rest = rest[len(tok):]
                break
        else:
            raise MarkParseError(f"unrecognised mark suffix {rest!r}")
    return tuple(flags)


def parse_status(raw: str) -> str | None:
    """Return the status code if `raw` is a status word, else None."""
    s = raw.strip().upper()
    s = _STATUS_ALIASES.get(s, s)
    return s if s in STATUSES and s != "OK" else None


def parse_time(core: str) -> float:
    m = _TIME.match(core)
    if not m:
        raise MarkParseError(f"not a time: {core!r}")
    hours, minutes, seconds = m.groups()
    if minutes is not None and float(seconds) >= 60:
        raise MarkParseError(f"seconds >= 60 in {core!r}")
    total = float(seconds) + 60 * int(minutes or 0) + 3600 * int(hours or 0)
    return round(total, 3)


def parse_distance(core: str) -> float:
    for pattern in (_FEET_INCH, _FEET_INCH_QUOTES):
        m = pattern.match(core)
        if m:
            feet, inches = int(m.group(1)), float(m.group(2))
            if inches >= 12:
                raise MarkParseError(f"inches >= 12 in {core!r}")
            return round(feet * FOOT_M + inches * INCH_M, 4)
    m = _METRIC.match(core)
    if m:
        return round(float(m.group(1)), 4)
    raise MarkParseError(f"not a distance/height: {core!r}")


_NUMERIC_CORE = {
    "time": re.compile(r"^[\d:.]+"),
    "distance": re.compile(r"^(?:\d{1,3}-\d{1,2}(?:\.\d{1,2})?|\d{1,3}'\s*\d{1,2}(?:\.\d{1,2})?\"?|\d{1,3}\.\d{1,2}m)"),
}


def parse_mark(raw: str, measure: str) -> Mark:
    """Parse one mark. `measure` is "time" or "distance" (heights are distances)."""
    if measure not in _NUMERIC_CORE:
        raise ValueError(f"measure must be 'time' or 'distance', got {measure!r}")
    text = (raw or "").strip()
    if not text:
        raise MarkParseError("empty mark")

    status = parse_status(text)
    if status:
        return Mark(raw=raw, status=status, value=None, unit=None)

    flags: list[str] = []
    if text[0] in "Jj" and len(text) > 1 and (text[1].isdigit()):
        flags.append("J")
        text = text[1:]

    m = _NUMERIC_CORE[measure].match(text)
    if not m:
        raise MarkParseError(f"no {measure} found in {raw!r}")
    core, rest = m.group(0), text[m.end():].strip()
    flags.extend(_split_flags(rest.replace(" ", "")))

    if measure == "time":
        return Mark(raw=raw, status="OK", value=parse_time(core), unit="s", flags=tuple(flags))
    return Mark(raw=raw, status="OK", value=parse_distance(core), unit="m", flags=tuple(flags))


def is_better(a: float, b: float, measure: str) -> bool:
    """True if mark value `a` beats `b` (lower time, longer/higher distance)."""
    return a < b if measure == "time" else a > b


def sort_key(value: float, measure: str) -> float:
    """Ascending sort key where smaller is always better."""
    return value if measure == "time" else -value
