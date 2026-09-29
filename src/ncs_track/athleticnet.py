"""Athletic.net CSV ingest: raw extraction -> performances + relay_legs.

Spec: docs/ingest_spec_athleticnet.md. The column layout is the one agreed for the
browser-extension extraction; value formats are not yet confirmed against a real
file, so every field is parsed strictly and anything unexpected becomes an Issue
instead of a guess.

Rows are never dropped here. Out-of-scope rows (adaptive divisions, exhibition
blocks, 4x800) are kept with in_scope=False so counts can be reconciled.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from . import paths
from .events import parse_event, parse_gender, parse_round
from .issues import Issue
from .marks import MarkParseError, parse_mark, parse_status
from .names import grad_year, name_key
from .schema import ATHLETICNET_COLUMNS, PERFORMANCES, RELAY_LEGS, conform

FILENAME = re.compile(r"^athleticnet_(\d{4})_(\d+)\.csv$")
LEG_SEPARATORS = ("|", ";")


class IngestError(ValueError):
    pass


def parse_filename(path: Path) -> tuple[int, str]:
    m = FILENAME.match(path.name)
    if not m:
        raise IngestError(f"{path.name}: expected athleticnet_{{season}}_{{meet_id}}.csv")
    return int(m.group(1)), m.group(2)


def load_meets(path: Path = paths.MEETS) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def lookup_meet(meets: pd.DataFrame, season: int, meet_id: str) -> pd.Series:
    hit = meets[(meets["athleticnet_meet_id"] == meet_id)]
    if len(hit) != 1:
        raise IngestError(f"meet_id {meet_id} matches {len(hit)} rows in meets.csv (need exactly 1)")
    row = hit.iloc[0]
    if int(row["season"]) != season:
        raise IngestError(f"meet_id {meet_id}: filename season {season} != meets.csv season {row['season']}")
    return row


def read_raw(path: Path) -> tuple[pd.DataFrame, list[Issue]]:
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    missing = [c for c in ATHLETICNET_COLUMNS if c not in df.columns]
    if missing:
        raise IngestError(f"{path.name}: missing columns {missing}")
    issues = []
    extra = [c for c in df.columns if c not in ATHLETICNET_COLUMNS]
    if extra:
        issues.append(Issue("V01", "warning", "", f"{path.name}: unexpected columns ignored: {extra}"))
    return df[list(ATHLETICNET_COLUMNS)].apply(lambda s: s.str.strip()), issues


def _int_or_none(raw: str) -> int | None:
    return int(raw) if re.fullmatch(r"\d+", raw or "") else None


def _float_or_none(raw: str) -> float | None:
    if not raw:
        return None
    return float(raw.replace("+", ""))


def _split_legs(raw: str) -> list[str]:
    if not raw:
        return []
    sep = next((s for s in LEG_SEPARATORS if s in raw), None)
    parts = raw.split(sep) if sep else [raw]
    return [p.strip() for p in parts]


def normalize(raw: pd.DataFrame, meet: pd.Series, source_file: str, rules: dict) -> tuple[pd.DataFrame, pd.DataFrame, list[Issue]]:
    """Normalise one meet's raw rows. Returns (performances, relay_legs, issues)."""
    meet_key = meet["meet_key"]
    season = int(meet["season"])
    in_scope_codes = {(g, c) for g, codes in rules["events"]["main_simulation"].items() for c in codes}
    wind_max = rules["wind"]["legal_max_mps"]
    issues: list[Issue] = []
    perf_rows, leg_rows = [], []

    def issue(check, severity, msg, pid):
        issues.append(Issue(check, severity, meet_key, msg, pid))

    for i, r in enumerate(raw.to_dict("records"), start=1):
        pid = f"{meet_key}#{i}"
        gender = parse_gender(r["gender"])
        if gender is None:
            issue("V03", "error", f"unrecognised gender {r['gender']!r}", pid)
        ev = parse_event(r["event_raw"], r["division"])
        if ev.code is None:
            issue("V03", "error", f"unrecognised event {r['event_raw']!r}", pid)
        rnd = parse_round(r["round_raw"])
        if rnd == "unknown":
            issue("V03", "error", f"unrecognised round {r['round_raw']!r}", pid)

        # Mark and status. The status column wins if set; otherwise status comes from the mark.
        status_col = parse_status(r["status"]) if r["status"] else None
        if r["status"] and status_col is None and r["status"].upper() != "OK":
            issue("V04", "error", f"unrecognised status {r['status']!r}", pid)
        mark = None
        if r["mark_raw"] and ev.measure:
            try:
                mark = parse_mark(r["mark_raw"], ev.measure)
            except MarkParseError as e:
                issue("V04", "error", f"mark {r['mark_raw']!r}: {e}", pid)
        status = status_col or (mark.status if mark else None)
        if status is None:
            status = "OK" if mark else "NM"
            if not mark:
                issue("V04", "error", "no mark and no status", pid)
        if status_col and mark and mark.ok:
            issue("V04", "error", f"status {status_col} but numeric mark {r['mark_raw']!r}", pid)
        if status_col and mark and not mark.ok and mark.status != status_col:
            issue("V04", "warning", f"status column {status_col} != mark {mark.status}", pid)
        value = mark.value if (mark and mark.ok and status == "OK") else None

        place = _int_or_none(r["place"])
        if r["place"] and place is None and r["place"] not in ("--", "-"):
            issue("V06", "error", f"unparseable place {r['place']!r}", pid)
        if status != "OK" and place is not None:
            issue("V06", "error", f"place {place} on a {status} row", pid)

        try:
            wind = _float_or_none(r["wind"])
        except ValueError:
            wind = None
            issue("V13", "error", f"unparseable wind {r['wind']!r}", pid)
        wind_aided = bool(ev.wind_event and wind is not None and wind > wind_max)

        grade = _int_or_none(r["grade"])
        if r["grade"] and (grade is None or not 9 <= grade <= 12):
            issue("V11", "error", f"grade {r['grade']!r} not in 9-12", pid)
            grade = None

        in_scope = bool(
            gender and ev.code and (gender, ev.code) in in_scope_codes
            and not ev.is_adaptive and ev.modifier is None
        )
        perf_rows.append({
            "performance_id": pid, "meet_key": meet_key, "season": season, "level": meet["level"],
            "meet_area": meet["area"] or None, "source": "athleticnet", "source_file": source_file,
            "source_row": i,
            "gender": gender, "event_raw": r["event_raw"], "division_raw": r["division"],
            "event_code": ev.code, "event_modifier": ev.modifier, "measure": ev.measure,
            "is_relay": ev.is_relay, "is_adaptive": ev.is_adaptive, "in_scope": in_scope,
            "round_raw": r["round_raw"], "round": rnd, "heat": _int_or_none(r["heat"]),
            "place_raw": r["place"], "place": place,
            "status_raw": r["status"], "status": status,
            "mark_raw": r["mark_raw"], "mark_value": value,
            "mark_unit": mark.unit if (mark and value is not None) else None,
            "mark_flags": " ".join(mark.flags) if mark else "",
            "wind_raw": r["wind"], "wind": wind, "wind_aided": wind_aided,
            "athlete_id": (r["athlete_id"] or None) if not ev.is_relay else None,
            "athlete_name_raw": r["athlete_name"],
            "athlete_name_key": name_key(r["athlete_name"]) if r["athlete_name"] and not ev.is_relay else None,
            "grade": grade, "grad_year": grad_year(season, grade),
            "school_id": r["school_id"] or None, "school_name_raw": r["school_name"],
            "relay_team_label": r["relay_team_label"] or None, "source_url": r["source_url"],
        })

        if ev.is_relay:
            if r["athlete_id"]:
                issue("V09", "warning", "relay row has athlete_id set", pid)
            names = _split_legs(r["relay_leg_names"])
            ids = _split_legs(r["relay_leg_ids"])
            if ids and len(ids) != len(names):
                issue("V09", "error", f"{len(names)} leg names but {len(ids)} leg ids", pid)
            for n, leg in enumerate(names, start=1):
                leg_rows.append({
                    "performance_id": pid, "meet_key": meet_key, "leg_order": n,
                    "athlete_id": (ids[n - 1] or None) if n <= len(ids) else None,
                    "athlete_name_raw": leg, "athlete_name_key": name_key(leg),
                })

    perf = conform(pd.DataFrame(perf_rows, columns=list(PERFORMANCES)), PERFORMANCES)
    legs = conform(pd.DataFrame(leg_rows, columns=list(RELAY_LEGS)), RELAY_LEGS)
    return perf, legs, issues


def ingest_file(path: Path, meets: pd.DataFrame, rules: dict) -> tuple[pd.DataFrame, pd.DataFrame, list[Issue]]:
    season, meet_id = parse_filename(path)
    meet = lookup_meet(meets, season, meet_id)
    raw, issues = read_raw(path)
    ids_in_file = set(raw["meet_id"]) - {""}
    if ids_in_file != {meet_id}:
        issues.append(Issue("V02", "error", meet["meet_key"],
                            f"meet_id column {sorted(ids_in_file)} != filename {meet_id}"))
    perf, legs, more = normalize(raw, meet, path.name, rules)
    return perf, legs, issues + more
