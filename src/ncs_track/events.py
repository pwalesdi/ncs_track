"""Map raw event, gender and round labels to canonical codes.

Unknown labels return None / "unknown" rather than a guess; validation turns
those into errors so a new label is added here deliberately.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# code -> (measure, family, wind_event)
EVENTS: dict[str, tuple[str, str, bool]] = {
    "100": ("time", "sprint", True),
    "200": ("time", "sprint", True),
    "400": ("time", "sprint", False),
    "800": ("time", "distance_run", False),
    "1600": ("time", "distance_run", False),
    "3200": ("time", "distance_run", False),
    "100H": ("time", "hurdles", True),
    "110H": ("time", "hurdles", True),
    "300H": ("time", "hurdles", False),
    "4x100": ("time", "relay", False),
    "4x400": ("time", "relay", False),
    "4x800": ("time", "relay", False),
    "HJ": ("distance", "vertical", False),
    "PV": ("distance", "vertical", False),
    "LJ": ("distance", "horizontal", True),
    "TJ": ("distance", "horizontal", True),
    "SP": ("distance", "throw", False),
    "DT": ("distance", "throw", False),
}

ADAPTIVE_WORDS = ("unified", "ambulatory", "wheelchair", "seated")

# Event-block modifiers seen in Hy-Tek: extra blocks for the same event.
MODIFIERS = {
    "exhibition": re.compile(r"\bexhibition\b"),
    "rerun": re.compile(r"\bre-?run\b"),
    "jump_off": re.compile(r"\bjump[- ]?off\b"),
    # Athletic.net lists relay legs as "400 Meters (Relay Split)"; not an individual race.
    "relay_split": re.compile(r"\brelay split\b"),
}

# Ordered: hurdles and relays before flat distances so "100 Meter Hurdles" != "100".
_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b4\s*x\s*100\b"), "4x100"),
    (re.compile(r"\b4\s*x\s*400\b"), "4x400"),
    (re.compile(r"\b4\s*x\s*800\b"), "4x800"),
    (re.compile(r"\b100\s*(m|meters?)?\s*(h|hurdles?)\b"), "100H"),
    (re.compile(r"\b110\s*(m|meters?)?\s*(h|hurdles?)\b"), "110H"),
    (re.compile(r"\b300\s*(m|meters?)?\s*(h|hurdles?)\b"), "300H"),
    (re.compile(r"\bhigh\s*jump\b"), "HJ"),
    (re.compile(r"\bpole\s*vault\b"), "PV"),
    (re.compile(r"\blong\s*jump\b"), "LJ"),
    (re.compile(r"\btriple\s*jump\b"), "TJ"),
    (re.compile(r"\bshot\s*put\b"), "SP"),
    (re.compile(r"\bdiscus\b"), "DT"),
    (re.compile(r"\b3200\s*(m|meters?|run)?\b"), "3200"),
    (re.compile(r"\b1600\s*(m|meters?|run)?\b"), "1600"),
    (re.compile(r"\b800\s*(m|meters?|run)?\b"), "800"),
    (re.compile(r"\b400\s*(m|meters?|dash)?\b"), "400"),
    (re.compile(r"\b200\s*(m|meters?|dash)?\b"), "200"),
    (re.compile(r"\b100\s*(m|meters?|dash)?\b"), "100"),
]


@dataclass(frozen=True)
class EventInfo:
    code: str | None        # None = unrecognised
    measure: str | None     # "time" | "distance"
    family: str | None
    is_relay: bool
    wind_event: bool
    is_adaptive: bool
    modifier: str | None    # exhibition | rerun | jump_off | None


def _clean(raw: str) -> str:
    s = raw.lower().replace("×", "x")
    s = re.sub(r"\b(girls|boys|women|men|varsity|jv|frosh[- ]?soph)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_event(event_raw: str, division_raw: str = "") -> EventInfo:
    text = _clean(f"{event_raw} {division_raw}")
    adaptive = any(w in text for w in ADAPTIVE_WORDS)
    modifier = next((name for name, pat in MODIFIERS.items() if pat.search(text)), None)
    code = next((c for pat, c in _PATTERNS if pat.search(text)), None)
    if code is None:
        return EventInfo(None, None, None, False, False, adaptive, modifier)
    measure, family, wind = EVENTS[code]
    return EventInfo(code, measure, family, family == "relay", wind, adaptive, modifier)


_GENDERS = {
    "girls": "girls", "girl": "girls", "women": "girls", "womens": "girls", "female": "girls", "f": "girls", "w": "girls",
    "boys": "boys", "boy": "boys", "men": "boys", "mens": "boys", "male": "boys", "m": "boys",
}


def parse_gender(raw: str) -> str | None:
    return _GENDERS.get(re.sub(r"[^a-z]", "", (raw or "").lower()))


ROUNDS = ("final", "prelim", "semi", "unknown")

_ROUNDS = {
    "final": "final", "finals": "final", "f": "final", "timedfinal": "final", "timedfinals": "final",
    "finalstimed": "final",
    "prelim": "prelim", "prelims": "prelim", "preliminaries": "prelim", "preliminary": "prelim",
    "trials": "prelim", "trial": "prelim", "p": "prelim", "heats": "prelim",
    "semi": "semi", "semis": "semi", "semifinal": "semi", "semifinals": "semi", "s": "semi",
}


def parse_round(raw: str) -> str:
    """Canonical round. Blank or unrecognised -> "unknown" (validation error)."""
    return _ROUNDS.get(re.sub(r"[^a-z]", "", (raw or "").lower()), "unknown")
