"""Normalised table schemas. Single source of truth for column names and dtypes.

docs/ingest_spec_athleticnet.md documents these columns; a test keeps the two in sync.
"""

from __future__ import annotations

import pandas as pd

from .events import ROUNDS
from .marks import STATUSES

# Raw Athletic.net extraction columns, in the order the extension writes them.
ATHLETICNET_COLUMNS: tuple[str, ...] = (
    "meet_id", "meet_name", "meet_date", "gender", "division", "event_raw", "round_raw",
    "heat", "place", "athlete_name", "athlete_id", "grade", "school_name", "school_id",
    "mark_raw", "wind", "status", "relay_team_label", "relay_leg_names", "relay_leg_ids",
    "source_url",
)

# performances: one row per athlete (or relay team) per round per event per meet.
PERFORMANCES: dict[str, str] = {
    # identity / provenance
    "performance_id": "string",     # "{meet_key}#{source_row}"; stable because raw files are immutable
    "meet_key": "string",
    "season": "Int64",
    "level": "string",              # moc | area | league
    "meet_area": "string",          # area slug of the meet (blank for moc)
    "source": "string",             # athleticnet | hytek
    "source_file": "string",
    "source_row": "Int64",          # 1-based data row in the raw file
    # event
    "gender": "string",             # girls | boys
    "event_raw": "string",
    "division_raw": "string",
    "event_code": "string",         # see events.EVENTS; <NA> if unrecognised
    "event_modifier": "string",     # exhibition | rerun | jump_off | <NA>
    "measure": "string",            # time | distance
    "is_relay": "boolean",
    "is_adaptive": "boolean",       # Unified / Ambulatory -> excluded from analysis
    "in_scope": "boolean",          # main-simulation event, not adaptive, no modifier
    # round
    "round_raw": "string",
    "round": "string",              # final | prelim | semi | unknown
    "heat": "Int64",
    # result
    "place_raw": "string",
    "place": "Int64",               # <NA> when not placed (status != OK, or '--')
    "status_raw": "string",
    "status": "string",             # OK DNS DNF DQ FS SCR NH NM FOUL NT
    "mark_raw": "string",           # untouched source string
    "mark_value": "Float64",        # seconds (time) or meters (distance); <NA> unless status OK
    "mark_unit": "string",          # s | m
    "mark_flags": "string",         # space-separated: J Q q R NCS CIF h ...
    "wind_raw": "string",
    "wind": "Float64",              # m/s
    "wind_aided": "boolean",        # wind event and wind > rules.wind.legal_max_mps
    # who
    "athlete_id": "string",         # Athletic.net ID; <NA> for relays and unmatched Hy-Tek rows
    "athlete_name_raw": "string",
    "athlete_name_key": "string",   # names.name_key(); matching aid only
    "grade": "Int64",
    "grad_year": "Int64",
    "school_id": "string",          # Athletic.net school ID
    "school_name_raw": "string",
    "relay_team_label": "string",   # e.g. "A"
    "source_url": "string",
}

# relay_legs: one row per leg of a relay performance.
RELAY_LEGS: dict[str, str] = {
    "performance_id": "string",
    "meet_key": "string",
    "leg_order": "Int64",           # 1-4 in listed order (not necessarily running order)
    "athlete_id": "string",
    "athlete_name_raw": "string",
    "athlete_name_key": "string",
}

GENDERS = ("girls", "boys")
# ROUNDS and STATUSES are re-exported from events / marks.
_REEXPORTS = (ROUNDS, STATUSES)


def empty(schema: dict[str, str]) -> pd.DataFrame:
    return pd.DataFrame({c: pd.Series(dtype=t) for c, t in schema.items()})


def conform(df: pd.DataFrame, schema: dict[str, str]) -> pd.DataFrame:
    """Order columns per schema and cast dtypes. Missing/extra columns are errors."""
    missing = [c for c in schema if c not in df.columns]
    extra = [c for c in df.columns if c not in schema]
    if missing or extra:
        raise ValueError(f"schema mismatch: missing={missing} extra={extra}")
    return df[list(schema)].astype(schema)
